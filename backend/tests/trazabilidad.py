"""Trazabilidad escenario -> test (sección 2.6 del readme; design T1-T6 de qa-01-trazabilidad).

Comprueba que cada escenario de las specs vivas tiene al menos un test que lo cita o está
en la lista de pendientes con el ticket que lo cubrirá, y que ningún test ni pendiente cita
un escenario inexistente.

Uso, desde ``backend/``::

    uv run python tests/trazabilidad.py [--vitest FICHERO] [--pendientes FICHERO]

``--vitest`` es el JSON de ``npx vitest list --json=FICHERO``; el CI siempre lo pasa.
"""

from __future__ import annotations

import argparse
import contextlib
import difflib
import io
import json
import re
import sys
import tomllib
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import pytest

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIR_BACKEND = RAIZ_REPO / "backend"
DIR_SPECS = RAIZ_REPO / "openspec" / "specs"
DIR_CHANGES = RAIZ_REPO / "openspec" / "changes"
FICHERO_PENDIENTES = DIR_BACKEND / "tests" / "escenarios_pendientes.toml"

SEPARADOR = "::"
SEPARADOR_DESCRIBE = " > "
SEPARADOR_DETALLE = " — "  # raya: "cap::Req::Esc — detalle" en los títulos de Vitest
COMODIN = "*"
FRAGMENTOS_PROHIBIDOS = (SEPARADOR, SEPARADOR_DESCRIBE, SEPARADOR_DETALLE)
SECCIONES_CITABLES_DE_DELTA = ("ADDED", "MODIFIED")
PATRON_TICKET = re.compile(r"(OPS|DB|SEC|BE|FE|QA|REL)-\d{2}[a-z]?")

_RE_SECCION = re.compile(r"^##\s+(.+?)\s*$")
_RE_REQUISITO = re.compile(r"^###\s+Requirement:\s*(.+?)\s*$")
_RE_ESCENARIO = re.compile(r"^####\s+Scenario:\s*(.+?)\s*$")

REGLAS = {
    1: "Escenarios sin test ni ticket pendiente",
    2: "Tests que citan un escenario inexistente",
    3: "Escenarios pendientes que ya tienen test",
    4: "Pendientes que no coinciden con ningún escenario",
    5: "Escenarios pendientes en más de un ticket",
    6: "Identificadores o tickets mal formados",
    7: "Nombres ambiguos o repetidos en las specs",
}


@dataclass
class Informe:
    """Errores acumulados por regla (T4)."""

    errores: dict[int, list[str]] = field(default_factory=lambda: defaultdict(list))

    def anadir(self, regla: int, mensaje: str) -> None:
        self.errores[regla].append(mensaje)

    def anadir_todos(self, regla: int, mensajes: Iterable[str]) -> None:
        for mensaje in mensajes:
            self.anadir(regla, mensaje)

    @property
    def correcto(self) -> bool:
        return not any(self.errores.values())


@dataclass(frozen=True)
class Pendiente:
    """Entrada de la lista de pendientes: un identificador o un patrón con ``*``."""

    ticket: str
    patron: str

    def coincide(self, identificador: str) -> bool:
        if self.patron.endswith(SEPARADOR + COMODIN):
            return identificador.startswith(self.patron[: -len(COMODIN)])
        return identificador == self.patron

    @property
    def es_patron(self) -> bool:
        return self.patron.endswith(COMODIN)


# --- Specs ---------------------------------------------------------------------------


def leer_spec(
    texto: str, capability: str, secciones: tuple[str, ...] | None = None
) -> tuple[list[str], list[str]]:
    """Devuelve los identificadores de los escenarios de una spec y los errores de la regla 7.

    Con ``secciones``, solo cuenta los requisitos de las secciones ``## <SECCIÓN> ...``
    indicadas (deltas de changes activos); sin ellas, todos (specs vivas).
    """
    identificadores: list[str] = []
    errores: list[str] = []
    en_seccion_valida = secciones is None
    requisito: str | None = None
    for linea in texto.splitlines():
        if (seccion := _RE_SECCION.match(linea)) and not linea.startswith("###"):
            requisito = None
            if secciones is not None:
                en_seccion_valida = seccion.group(1).split()[0].upper() in secciones
            continue
        if not en_seccion_valida:
            continue
        if coincidencia := _RE_REQUISITO.match(linea):
            requisito = coincidencia.group(1)
            errores.extend(_nombre_ambiguo(capability, "requisito", requisito))
        elif coincidencia := _RE_ESCENARIO.match(linea):
            escenario = coincidencia.group(1)
            if requisito is None:
                errores.append(f"{capability}: escenario '{escenario}' fuera de un requisito")
                continue
            errores.extend(_nombre_ambiguo(capability, "escenario", escenario))
            identificadores.append(SEPARADOR.join((capability, requisito, escenario)))
    return identificadores, errores


def _nombre_ambiguo(capability: str, tipo: str, nombre: str) -> Iterator[str]:
    for fragmento in FRAGMENTOS_PROHIBIDOS:
        if fragmento in nombre:
            yield f"{capability}: el {tipo} '{nombre}' contiene '{fragmento.strip()}'"


def _specs_en(directorio: Path) -> Iterator[tuple[str, str]]:
    """(capability, texto) de cada ``spec.md`` bajo ``directorio``."""
    for ruta in sorted(directorio.rglob("spec.md")):
        yield ruta.parent.relative_to(directorio).as_posix(), ruta.read_text(encoding="utf-8")


def leer_escenarios_vivos(dir_specs: Path) -> tuple[list[str], list[str]]:
    """Escenarios exigidos: los de las specs vivas, con los errores de la regla 7."""
    identificadores: list[str] = []
    errores: list[str] = []
    for capability, texto in _specs_en(dir_specs):
        ids, errs = leer_spec(texto, capability)
        identificadores.extend(ids)
        errores.extend(errs)
    vistos: set[str] = set()
    for identificador in identificadores:
        if identificador in vistos:
            errores.append(f"identificador repetido: {identificador}")
        vistos.add(identificador)
    return identificadores, errores


def leer_escenarios_de_deltas(dir_changes: Path) -> tuple[set[str], list[str]]:
    """Escenarios citables pero no exigidos: ADDED y MODIFIED de los changes activos."""
    identificadores: set[str] = set()
    errores: list[str] = []
    if not dir_changes.is_dir():
        return identificadores, errores
    for change in sorted(p for p in dir_changes.iterdir() if p.is_dir() and p.name != "archive"):
        dir_deltas = change / "specs"
        if not dir_deltas.is_dir():
            continue
        for capability, texto in _specs_en(dir_deltas):
            ids, errs = leer_spec(texto, capability, SECCIONES_CITABLES_DE_DELTA)
            identificadores.update(ids)
            errores.extend(f"{change.name}/{error}" for error in errs)
    return identificadores, errores


# --- Pendientes ----------------------------------------------------------------------


def leer_pendientes(texto: str) -> tuple[list[Pendiente], list[str]]:
    """Lee la lista TOML de pendientes (T3) y devuelve los errores de la regla 6."""
    try:
        datos = tomllib.loads(texto)
    except tomllib.TOMLDecodeError as error:
        return [], [f"la lista de pendientes no es TOML válido: {error}"]
    pendientes: list[Pendiente] = []
    errores: list[str] = []
    for ticket, tabla in datos.items():
        if not PATRON_TICKET.fullmatch(ticket):
            errores.append(f"ticket '{ticket}' no sigue el patrón {PATRON_TICKET.pattern}")
            continue
        escenarios = tabla.get("escenarios") if isinstance(tabla, dict) else None
        if not isinstance(escenarios, list) or not all(isinstance(e, str) for e in escenarios):
            errores.append(f"[{ticket}] necesita 'escenarios' como lista de textos")
            continue
        for patron in escenarios:
            if problema := _error_de_patron(patron):
                errores.append(f"[{ticket}] {problema}")
            else:
                pendientes.append(Pendiente(ticket, patron))
    return pendientes, errores


def _error_de_patron(patron: str) -> str | None:
    partes = patron.split(SEPARADOR)
    if any(not parte.strip() for parte in partes):
        return f"'{patron}' tiene partes vacías"
    if COMODIN in partes[:-1] or any(COMODIN in p for p in partes if p != COMODIN):
        return f"'{patron}': '*' solo puede ser la última parte"
    if len(partes) == 3 or (len(partes) == 2 and partes[-1] == COMODIN):
        return None
    return (
        f"'{patron}' no es capability::Requirement::Scenario, "
        "capability::Requirement::* ni capability::*"
    )


# --- Citas de los tests --------------------------------------------------------------


class _Marca(Protocol):
    @property
    def args(self) -> tuple[Any, ...]: ...


class _Test(Protocol):
    @property
    def nodeid(self) -> str: ...

    def iter_markers(self, name: str | None = None) -> Iterator[_Marca]: ...


Citas = dict[str, list[str]]


def extraer_citas_pytest(items: Iterable[_Test]) -> tuple[Citas, list[str]]:
    """Citas de la marca ``escenario`` de los tests recogidos (T1)."""
    citas: Citas = defaultdict(list)
    errores: list[str] = []
    for item in items:
        for marca in item.iter_markers(name="escenario"):
            validos = [a for a in marca.args if isinstance(a, str) and a.strip()]
            if not marca.args or len(validos) != len(marca.args):
                errores.append(f"{item.nodeid}: la marca 'escenario' necesita texto")
            for identificador in validos:
                citas[identificador.strip()].append(item.nodeid)
    return citas, errores


class _Recolector:
    def __init__(self) -> None:
        self.items: list[pytest.Item] = []

    def pytest_collection_modifyitems(self, items: list[pytest.Item]) -> None:
        self.items.extend(items)


def recoger_citas_pytest() -> tuple[Citas, list[str]]:
    """Recoge los tests de ``backend/tests`` en este proceso, sin ejecutarlos."""
    recolector = _Recolector()
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        codigo = pytest.main(
            [
                "--collect-only",
                "-q",
                "-p",
                "no:cacheprovider",
                "-c",
                str(DIR_BACKEND / "pyproject.toml"),
                "--rootdir",
                str(DIR_BACKEND),
                str(DIR_BACKEND / "tests"),
            ],
            plugins=[recolector],
        )
    if codigo not in (pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED):
        raise SystemExit(
            f"{salida.getvalue()}\npytest no pudo recoger los tests (código {int(codigo)})"
        )
    return extraer_citas_pytest(recolector.items)


def extraer_citas_vitest(datos: Any) -> tuple[Citas, list[str]]:
    """Citas al principio del título de cada test de ``vitest list --json`` (T2)."""
    citas: Citas = defaultdict(list)
    if not isinstance(datos, list):
        return citas, ["el JSON de Vitest no es una lista de tests"]
    errores: list[str] = []
    for test in datos:
        nombre = test.get("name") if isinstance(test, dict) else None
        if not isinstance(nombre, str):
            errores.append(f"entrada de Vitest sin 'name': {test!r}")
            continue
        titulo = nombre.split(SEPARADOR_DESCRIBE)[-1]
        if SEPARADOR not in titulo:
            continue
        fichero = Path(str(test.get("file", ""))).name
        citas[titulo.split(SEPARADOR_DETALLE)[0].strip()].append(f"{fichero} > {nombre}")
    return citas, errores


def fusionar(*grupos: Citas) -> Citas:
    total: Citas = defaultdict(list)
    for grupo in grupos:
        for identificador, tests in grupo.items():
            total[identificador].extend(tests)
    return total


# --- Reglas --------------------------------------------------------------------------


@dataclass
class Resultado:
    informe: Informe
    total: int
    con_test: int
    pendientes_por_ticket: dict[str, int]


def comprobar(
    escenarios: list[str],
    citables: set[str],
    citas: Citas,
    pendientes: list[Pendiente],
) -> Resultado:
    """Aplica las reglas 1-5 (T4)."""
    informe = Informe()
    exigidos = set(escenarios)
    conocidos = sorted(citables | exigidos)

    for identificador, tests in sorted(citas.items()):
        if identificador not in citables and identificador not in exigidos:
            parecido = difflib.get_close_matches(identificador, conocidos, n=1, cutoff=0.6)
            pista = f"; ¿quisiste decir '{parecido[0]}'?" if parecido else ""
            informe.anadir(2, f"{identificador} (citado por {', '.join(tests)}){pista}")

    asignacion: dict[str, list[Pendiente]] = defaultdict(list)
    for pendiente in pendientes:
        coincidentes = [e for e in escenarios if pendiente.coincide(e)]
        if not coincidentes:
            informe.anadir(4, f"[{pendiente.ticket}] {pendiente.patron}")
        for identificador in coincidentes:
            asignacion[identificador].append(pendiente)

    for identificador in escenarios:
        asignados = asignacion.get(identificador, [])
        if len(asignados) > 1:
            tickets = ", ".join(p.ticket for p in asignados)
            informe.anadir(5, f"{identificador} (en {tickets})")
        if asignados and identificador in citas:
            pendiente = asignados[0]
            consejo = (
                f"; sustituye '{pendiente.patron}' por los escenarios que siguen pendientes"
                if pendiente.es_patron
                else ""
            )
            informe.anadir(
                3,
                f"{identificador}: quítalo de [{pendiente.ticket}], ya lo prueba "
                f"{', '.join(citas[identificador])}{consejo}",
            )
        if not asignados and identificador not in citas:
            informe.anadir(1, identificador)

    pendientes_por_ticket: dict[str, int] = defaultdict(int)
    for identificador, asignados in asignacion.items():
        if identificador not in citas:
            pendientes_por_ticket[asignados[0].ticket] += 1
    return Resultado(
        informe=informe,
        total=len(exigidos),
        con_test=len(exigidos & citas.keys()),
        pendientes_por_ticket=dict(sorted(pendientes_por_ticket.items())),
    )


def formatear(resultado: Resultado) -> str:
    lineas: list[str] = []
    for regla, titulo in REGLAS.items():
        errores = resultado.informe.errores.get(regla)
        if errores:
            lineas.append(f"\n[{regla}] {titulo} ({len(errores)}):")
            lineas.extend(f"  - {error}" for error in errores)
    pendientes = sum(resultado.pendientes_por_ticket.values())
    lineas.append(
        f"\nEscenarios: {resultado.total} · con test: {resultado.con_test}"
        f" · pendientes: {pendientes}"
    )
    if resultado.pendientes_por_ticket:
        lineas.append(
            "Pendientes por ticket: "
            + ", ".join(f"{t} {n}" for t, n in resultado.pendientes_por_ticket.items())
        )
    lineas.append("Trazabilidad: " + ("OK" if resultado.informe.correcto else "FALLA"))
    return "\n".join(lineas).lstrip("\n")


# --- Línea de órdenes ----------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--vitest", type=Path, help="JSON de 'npx vitest list --json=FICHERO'")
    parser.add_argument("--pendientes", type=Path, default=FICHERO_PENDIENTES)
    args = parser.parse_args(argv)

    escenarios, errores_specs = leer_escenarios_vivos(DIR_SPECS)
    de_deltas, errores_deltas = leer_escenarios_de_deltas(DIR_CHANGES)
    pendientes, errores_pendientes = leer_pendientes(args.pendientes.read_text(encoding="utf-8"))
    citas_pytest, errores_pytest = recoger_citas_pytest()
    citas_vitest: Citas = {}
    errores_vitest: list[str] = []
    if args.vitest is None:
        print(
            "Aviso: sin --vitest no se leen los tests del frontend; "
            "los escenarios que solo prueba Vitest saldrán como sin test.",
            file=sys.stderr,
        )
    else:
        datos = json.loads(args.vitest.read_text(encoding="utf-8"))
        citas_vitest, errores_vitest = extraer_citas_vitest(datos)

    resultado = comprobar(escenarios, de_deltas, fusionar(citas_pytest, citas_vitest), pendientes)
    resultado.informe.anadir_todos(6, errores_pendientes + errores_pytest + errores_vitest)
    resultado.informe.anadir_todos(7, errores_specs + errores_deltas)
    print(formatear(resultado))
    return 0 if resultado.informe.correcto else 1


if __name__ == "__main__":
    sys.exit(main())
