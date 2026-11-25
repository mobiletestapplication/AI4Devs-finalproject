"""Registro estructurado y sin secretos (tarea 2.2 de sec-01-seguridad-api; design S6).

Prueban infraestructura de seguridad, no escenarios de las specs.
"""

import datetime
import json
import logging
import sys
from dataclasses import dataclass

import pytest
from pydantic import SecretStr

from app.infrastructure.config import Ajustes
from app.infrastructure.registro import (
    NOMBRE_MANEJADOR,
    FiltroSecretos,
    FormateadorJson,
    configurar_registro,
    registrar_descartes,
    secretos_de,
)

CONTRASENA = "s3cr3t0-de-la-bd"
CLAVE_LLM = "sk-clave-del-llm"


def _ajustes() -> Ajustes:
    return Ajustes(
        database_url=SecretStr(f"postgresql+psycopg://traide:{CONTRASENA}@db:5432/traide"),
        llm_api_key=SecretStr(CLAVE_LLM),
    )


def _registro(mensaje: str, *args: object, **extra: object) -> logging.LogRecord:
    record = logging.LogRecord("app.prueba", logging.ERROR, __file__, 1, mensaje, args, None)
    for clave, valor in extra.items():
        setattr(record, clave, valor)
    return record


def test_cada_registro_es_una_linea_json_con_campos_fijos() -> None:
    linea = FormateadorJson().format(_registro("fallo en %s", "twr", incidencia="abc123"))

    datos = json.loads(linea)
    assert datos["nivel"] == "ERROR"
    assert datos["mensaje"] == "fallo en twr"
    assert datos["incidencia"] == "abc123"
    assert datos["logger"] == "app.prueba"
    assert "\n" not in linea


def test_los_secretos_se_ocultan_en_el_mensaje() -> None:
    filtro = FiltroSecretos(secretos_de(_ajustes()))
    record = _registro("conectando con %s y clave %s", f"traide:{CONTRASENA}@db", CLAVE_LLM)

    filtro.filter(record)

    mensaje = record.getMessage()
    assert CONTRASENA not in mensaje
    assert CLAVE_LLM not in mensaje
    assert mensaje == "conectando con traide:***@db y clave ***"


def test_los_secretos_se_ocultan_en_la_traza() -> None:
    filtro = FiltroSecretos([CONTRASENA])
    try:
        raise RuntimeError(f"no se pudo conectar con {CONTRASENA}")
    except RuntimeError:
        record = logging.LogRecord("app", logging.ERROR, __file__, 1, "error", None, sys.exc_info())

    filtro.filter(record)
    linea = FormateadorJson().format(record)

    assert CONTRASENA not in linea
    assert "no se pudo conectar con ***" in json.loads(linea)["excepcion"]


def test_sin_secretos_no_se_toca_el_registro() -> None:
    record = _registro("valor %s", 1)

    FiltroSecretos(["", ""]).filter(record)

    assert record.args == (1,)


def test_secretos_de_ajustes_sin_clave_ni_contrasena() -> None:
    ajustes = Ajustes(database_url=SecretStr("postgresql+psycopg://traide@db/traide"))

    assert secretos_de(ajustes) == []


def test_configurar_registro_no_duplica_el_manejador() -> None:
    configurar_registro(_ajustes())
    configurar_registro(_ajustes())

    manejadores = [h for h in logging.getLogger("app").handlers if h.get_name() == NOMBRE_MANEJADOR]
    assert len(manejadores) == 1


@dataclass(frozen=True)
class _Descarte:
    fecha: datetime.date | None
    motivo: str


def test_descartes_del_proveedor_sin_valores(caplog: pytest.LogCaptureFixture) -> None:
    descartes = [
        _Descarte(datetime.date(2025, 3, 7), "precio no positivo"),
        _Descarte(None, "fecha no válida"),
    ]

    with caplog.at_level(logging.WARNING, logger="app.mercado"):
        registrar_descartes("MSFT", descartes)

    assert [(r.ticker, r.fecha, r.motivo) for r in caplog.records] == [  # type: ignore[attr-defined]
        ("MSFT", "2025-03-07", "precio no positivo"),
        ("MSFT", None, "fecha no válida"),
    ]
    assert all(r.getMessage() == "barra del proveedor descartada" for r in caplog.records)
