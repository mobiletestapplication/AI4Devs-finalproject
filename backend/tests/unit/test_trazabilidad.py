"""Tests del script de trazabilidad (design T1-T6 de qa-01-trazabilidad).

Prueban una herramienta de desarrollo, no comportamiento de la aplicación, así que no
citan escenarios de las specs.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from tests.trazabilidad import (
    Pendiente,
    comprobar,
    extraer_citas_pytest,
    extraer_citas_vitest,
    formatear,
    leer_escenarios_de_deltas,
    leer_escenarios_vivos,
    leer_pendientes,
    leer_spec,
)

SPEC = """\
# cartera Specification

## Purpose
Algo.

## Requirements

### Requirement: Importar
El sistema SHALL importar.

#### Scenario: Fichero válido
- **WHEN** algo
- **THEN** algo

#### Scenario: Fichero vacío
- **WHEN** algo
- **THEN** algo

### Requirement: Consultar
El sistema SHALL consultar.

#### Scenario: Sin cartera
- **WHEN** algo
- **THEN** algo
"""

DELTA = """\
# Spec Delta

## ADDED Requirements

### Requirement: Exportar
#### Scenario: A CSV

## MODIFIED Requirements

### Requirement: Consultar
#### Scenario: Con filtro

## REMOVED Requirements

### Requirement: Importar
#### Scenario: Fichero vacío
"""

ESCENARIOS = [
    "cartera::Importar::Fichero válido",
    "cartera::Importar::Fichero vacío",
    "cartera::Consultar::Sin cartera",
]


def _escribir(ruta: Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


# --- Lectura de specs (tarea 1.1) -----------------------------------------------------


def test_spec_con_dos_requisitos_y_tres_escenarios() -> None:
    identificadores, errores = leer_spec(SPEC, "cartera")

    assert identificadores == ESCENARIOS
    assert errores == []


@pytest.mark.parametrize("nombre", ["Con :: dentro", "Con > dentro", "Con — dentro"])
def test_nombre_con_separador_es_un_error(nombre: str) -> None:
    _, errores = leer_spec(f"### Requirement: R\n#### Scenario: {nombre}\n", "cartera")

    assert len(errores) == 1


def test_escenario_fuera_de_requisito_es_un_error() -> None:
    identificadores, errores = leer_spec("## Requirements\n#### Scenario: Suelto\n", "cartera")

    assert identificadores == []
    assert "fuera de un requisito" in errores[0]


def test_identificador_repetido_en_specs_vivas(tmp_path: Path) -> None:
    _escribir(tmp_path / "cartera" / "spec.md", SPEC + "\n#### Scenario: Sin cartera\n")

    _, errores = leer_escenarios_vivos(tmp_path)

    assert errores == ["identificador repetido: cartera::Consultar::Sin cartera"]


def test_capability_es_la_ruta_relativa_a_specs(tmp_path: Path) -> None:
    _escribir(tmp_path / "identidad" / "acceso" / "spec.md", SPEC)

    identificadores, _ = leer_escenarios_vivos(tmp_path)

    assert identificadores[0] == "identidad/acceso::Importar::Fichero válido"


def test_deltas_leen_added_y_modified_y_no_removed(tmp_path: Path) -> None:
    _escribir(tmp_path / "mi-change" / "specs" / "cartera" / "spec.md", DELTA)
    _escribir(tmp_path / "archive" / "viejo" / "specs" / "cartera" / "spec.md", DELTA)

    identificadores, errores = leer_escenarios_de_deltas(tmp_path)

    assert identificadores == {"cartera::Exportar::A CSV", "cartera::Consultar::Con filtro"}
    assert errores == []


def test_sin_directorio_de_changes_no_hay_deltas(tmp_path: Path) -> None:
    assert leer_escenarios_de_deltas(tmp_path / "no-existe") == (set(), [])


# --- Lista de pendientes (tarea 1.2) --------------------------------------------------


def test_lista_de_pendientes_valida() -> None:
    texto = '[BE-01a]\nescenarios = ["cartera::*", "cartera::Importar::*"]\n'

    pendientes, errores = leer_pendientes(texto)

    assert errores == []
    assert pendientes == [
        Pendiente("BE-01a", "cartera::*"),
        Pendiente("BE-01a", "cartera::Importar::*"),
    ]


@pytest.mark.parametrize(
    ("texto", "fragmento"),
    [
        ('[be-01]\nescenarios = ["cartera::*"]\n', "no sigue el patrón"),
        ('[BE-01]\nescenarios = ["cartera::Importar"]\n', "no es capability"),
        ('[BE-01]\nescenarios = ["cartera::*::Fichero"]\n', "'*' solo puede"),
        ('[BE-01]\nescenarios = ["cartera::Imp*::X"]\n', "'*' solo puede"),
        ('[BE-01]\nescenarios = ["cartera::::X"]\n', "partes vacías"),
        ('[BE-01]\nescenarios = "cartera::*"\n', "lista de textos"),
        ('[BE-01]\notra = ["cartera::*"]\n', "lista de textos"),
        ("BE-01 = 3\n", "lista de textos"),
        ("[BE-01\n", "no es TOML"),
    ],
)
def test_lista_de_pendientes_mal_formada(texto: str, fragmento: str) -> None:
    _, errores = leer_pendientes(texto)

    assert len(errores) == 1
    assert fragmento in errores[0]


@pytest.mark.parametrize(
    ("patron", "esperados"),
    [
        ("cartera::*", ESCENARIOS),
        ("cartera::Importar::*", ESCENARIOS[:2]),
        ("cartera::Consultar::Sin cartera", ESCENARIOS[2:]),
        ("cart::*", []),
    ],
)
def test_cobertura_de_los_patrones(patron: str, esperados: list[str]) -> None:
    pendiente = Pendiente("BE-01", patron)

    assert [e for e in ESCENARIOS if pendiente.coincide(e)] == esperados


# --- Citas (tarea 1.3) ----------------------------------------------------------------


@dataclass
class _MarcaFalsa:
    args: tuple[Any, ...]


@dataclass
class _TestFalso:
    nodeid: str
    marcas: list[_MarcaFalsa]

    def iter_markers(self, name: str | None = None) -> Iterator[_MarcaFalsa]:
        assert name == "escenario"
        return iter(self.marcas)


def test_citas_de_pytest() -> None:
    items = [
        _TestFalso("t.py::a", [_MarcaFalsa(("cartera::Importar::Fichero válido",))]),
        _TestFalso("t.py::b", []),
        _TestFalso("t.py::c", [_MarcaFalsa(("cartera::Importar::Fichero válido", "x::y::z"))]),
    ]

    citas, errores = extraer_citas_pytest(items)

    assert citas == {
        "cartera::Importar::Fichero válido": ["t.py::a", "t.py::c"],
        "x::y::z": ["t.py::c"],
    }
    assert errores == []


@pytest.mark.parametrize("args", [(), ("",), (3,)])
def test_marca_sin_identificador_es_un_error(args: tuple[Any, ...]) -> None:
    _, errores = extraer_citas_pytest([_TestFalso("t.py::a", [_MarcaFalsa(args)])])

    assert errores == ["t.py::a: la marca 'escenario' necesita texto"]


def test_citas_de_vitest() -> None:
    datos = [
        {"name": "A > cap::Req::Esc — detalle", "file": "/x/src/A.test.tsx"},
        {"name": "A > sin cita", "file": "/x/src/A.test.tsx"},
        {"name": "B > cap::Req::Otro", "file": "/x/src/B.test.tsx"},
    ]

    citas, errores = extraer_citas_vitest(datos)

    assert citas == {
        "cap::Req::Esc": ["A.test.tsx > A > cap::Req::Esc — detalle"],
        "cap::Req::Otro": ["B.test.tsx > B > cap::Req::Otro"],
    }
    assert errores == []


@pytest.mark.parametrize(("datos", "errores"), [({"no": "lista"}, 1), ([{"file": "x"}], 1)])
def test_json_de_vitest_mal_formado(datos: Any, errores: int) -> None:
    assert len(extraer_citas_vitest(datos)[1]) == errores


# --- Reglas (tarea 1.4) ---------------------------------------------------------------


def test_todo_cubierto_es_correcto() -> None:
    resultado = comprobar(
        ESCENARIOS,
        set(),
        {"cartera::Importar::Fichero válido": ["t1"]},
        [
            Pendiente("BE-01", "cartera::Importar::Fichero vacío"),
            Pendiente("FE-01", "cartera::Consultar::*"),
        ],
    )

    assert resultado.informe.correcto
    assert (resultado.total, resultado.con_test) == (3, 1)
    assert resultado.pendientes_por_ticket == {"BE-01": 1, "FE-01": 1}
    assert formatear(resultado).endswith("Trazabilidad: OK")


def test_regla_1_escenario_sin_test_ni_pendiente() -> None:
    resultado = comprobar(ESCENARIOS, set(), {}, [Pendiente("BE-01", "cartera::Importar::*")])

    assert resultado.informe.errores == {1: ["cartera::Consultar::Sin cartera"]}
    assert "Trazabilidad: FALLA" in formatear(resultado)


def test_regla_2_cita_inexistente_con_sugerencia() -> None:
    resultado = comprobar(
        ESCENARIOS,
        set(),
        {"cartera::Importar::Fichero valido": ["t1"]},
        [Pendiente("BE-01", "cartera::*")],
    )

    (error,) = resultado.informe.errores[2]
    assert "¿quisiste decir 'cartera::Importar::Fichero válido'?" in error


def test_regla_2_cita_de_un_delta_activo_es_valida() -> None:
    resultado = comprobar(
        ESCENARIOS,
        {"cartera::Exportar::A CSV"},
        {"cartera::Exportar::A CSV": ["t1"]},
        [Pendiente("BE-01", "cartera::*")],
    )

    assert resultado.informe.correcto


def test_regla_3_pendiente_que_ya_tiene_test() -> None:
    resultado = comprobar(
        ESCENARIOS,
        set(),
        {"cartera::Consultar::Sin cartera": ["t1"]},
        [Pendiente("BE-01", "cartera::*")],
    )

    (error,) = resultado.informe.errores[3]
    assert "quítalo de [BE-01], ya lo prueba t1; sustituye 'cartera::*'" in error


def test_regla_4_pendiente_inexistente() -> None:
    pendientes = [Pendiente("BE-01", "cartera::*"), Pendiente("BE-02", "cartera::Importar::Otro")]

    resultado = comprobar(ESCENARIOS, set(), {}, pendientes)

    assert resultado.informe.errores == {4: ["[BE-02] cartera::Importar::Otro"]}


def test_regla_5_pendiente_en_dos_tickets() -> None:
    pendientes = [Pendiente("BE-01", "cartera::*"), Pendiente("FE-01", "cartera::Consultar::*")]

    resultado = comprobar(ESCENARIOS, set(), {}, pendientes)

    assert resultado.informe.errores == {5: ["cartera::Consultar::Sin cartera (en BE-01, FE-01)"]}


# --- Pendientes de deltas activos (sec-01-seguridad-api, design S8) --------------------

DELTA_ACTIVO = {"cartera::Exportar::A CSV"}
TODO_PENDIENTE = Pendiente("BE-01", "cartera::*")


def test_pendiente_de_un_delta_activo_es_valido() -> None:
    pendientes = [TODO_PENDIENTE, Pendiente("FE-01", "cartera::Exportar::A CSV")]

    resultado = comprobar(ESCENARIOS, DELTA_ACTIVO, {}, pendientes)

    assert resultado.informe.correcto
    assert resultado.pendientes_por_ticket == {"BE-01": 3, "FE-01": 1}


def test_pendiente_de_un_delta_activo_con_test_falla_por_la_regla_3() -> None:
    pendientes = [TODO_PENDIENTE, Pendiente("FE-01", "cartera::Exportar::A CSV")]
    citas = {"cartera::Exportar::A CSV": ["t1"]}

    resultado = comprobar(ESCENARIOS, DELTA_ACTIVO, citas, pendientes)

    assert list(resultado.informe.errores) == [3]


def test_escenario_de_un_delta_activo_sin_pendiente_no_se_exige() -> None:
    resultado = comprobar(ESCENARIOS, DELTA_ACTIVO, {}, [TODO_PENDIENTE])

    assert resultado.informe.correcto


def test_un_patron_no_cubre_escenarios_de_deltas_activos() -> None:
    citas = {"cartera::Exportar::A CSV": ["t1"]}

    resultado = comprobar(ESCENARIOS, DELTA_ACTIVO, citas, [TODO_PENDIENTE])

    assert resultado.informe.correcto
    assert resultado.pendientes_por_ticket == {"BE-01": 3}


def test_pendiente_fuera_de_specs_y_deltas_sigue_fallando() -> None:
    pendientes = [TODO_PENDIENTE, Pendiente("FE-01", "cartera::Exportar::A PDF")]

    resultado = comprobar(ESCENARIOS, DELTA_ACTIVO, {}, pendientes)

    assert resultado.informe.errores == {4: ["[FE-01] cartera::Exportar::A PDF"]}
