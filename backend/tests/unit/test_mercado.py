"""Validador de los datos del proveedor de mercado (tarea 4.1 de sec-01-seguridad-api; S7).

Prueban la función pura del dominio. Los escenarios HTTP de "Datos del proveedor de
mercado como entrada no confiable" se prueban en BE-07, cuando exista
``GET /api/cartera/posiciones``.
"""

import datetime
from decimal import Decimal
from typing import Any

import pytest

from app.domain.mercado import (
    FECHA_FUTURA,
    FECHA_NO_VALIDA,
    FECHA_REPETIDA,
    FUERA_DEL_RANGO_DEL_DIA,
    MAXIMO_MENOR_QUE_MINIMO,
    OTRO_TICKER,
    PRECIO_FUERA_DE_RANGO,
    PRECIO_NO_NUMERICO,
    PRECIO_NO_POSITIVO,
    Descarte,
    a_decimal,
    validar_barras,
)

HOY = datetime.date(2025, 3, 7)
D06 = datetime.date(2025, 3, 6)
D07 = datetime.date(2025, 3, 7)


def fila(fecha: object = D06, **cambios: object) -> dict[str, object]:
    valores: dict[str, object] = {
        "fecha": fecha,
        "apertura": 408.0,
        "maximo": 412.0,
        "minimo": 405.5,
        "cierre": 410.25,
        "cierre_sin_ajustar": 410.25,
    }
    return valores | cambios


def _descartes(*filas: dict[str, object]) -> list[Descarte]:
    return validar_barras("MSFT", filas, HOY).descartes


def test_barras_validas_ordenadas_y_en_decimal() -> None:
    resultado = validar_barras("msft", [fila(D07, cierre=412), fila(D06)], HOY)

    assert [b.fecha for b in resultado.validas] == [D06, D07]
    primera = resultado.validas[0]
    assert primera.ticker == "MSFT"
    assert primera.cierre == Decimal("410.250000")
    assert resultado.descartes == []
    assert resultado.avisos == []


def test_cierre_no_positivo_se_descarta_y_el_resto_se_conserva() -> None:
    resultado = validar_barras("MSFT", [fila(D06), fila(D07, cierre=-5.0)], HOY)

    assert [b.cierre for b in resultado.validas] == [Decimal("410.250000")]
    assert resultado.descartes == [Descarte(D07, PRECIO_NO_POSITIVO)]


@pytest.mark.parametrize("valor", [float("nan"), float("inf"), "410.25", None, True])
def test_precio_no_numerico_o_no_finito(valor: Any) -> None:
    assert _descartes(fila(D07, cierre=valor)) == [Descarte(D07, PRECIO_NO_NUMERICO)]


def test_decimal_no_finito_tampoco_es_un_precio() -> None:
    assert a_decimal(Decimal("NaN")) is None
    assert a_decimal(Decimal("-Infinity")) is None


def test_precio_cero_en_otra_columna() -> None:
    assert _descartes(fila(D07, apertura=0)) == [Descarte(D07, PRECIO_NO_POSITIVO)]


def test_precio_fuera_del_rango_del_esquema() -> None:
    assert _descartes(fila(D07, maximo=Decimal("1e12"))) == [Descarte(D07, PRECIO_FUERA_DE_RANGO)]


def test_maximo_menor_que_el_minimo() -> None:
    assert _descartes(fila(D07, maximo=400, minimo=405)) == [Descarte(D07, MAXIMO_MENOR_QUE_MINIMO)]


def test_fecha_posterior_a_la_actual() -> None:
    futura = datetime.date(2025, 3, 10)

    resultado = validar_barras("MSFT", [fila(D07, cierre=412), fila(futura, cierre=999)], HOY)

    assert [b.cierre for b in resultado.validas] == [Decimal("412.000000")]
    assert resultado.descartes == [Descarte(futura, FECHA_FUTURA)]


def test_fecha_repetida_descarta_todas_las_barras_de_ese_dia() -> None:
    resultado = validar_barras("MSFT", [fila(D06), fila(D06, cierre=411), fila(D07)], HOY)

    assert [b.fecha for b in resultado.validas] == [D07]
    assert resultado.descartes == [Descarte(D06, FECHA_REPETIDA), Descarte(D06, FECHA_REPETIDA)]


@pytest.mark.parametrize("valor", ["2025-03-06", None, 20250306])
def test_fecha_no_valida(valor: object) -> None:
    assert _descartes(fila(valor)) == [Descarte(None, FECHA_NO_VALIDA)]


def test_fecha_con_hora_se_toma_como_dia() -> None:
    con_hora = datetime.datetime(2025, 3, 6, 16, 0, tzinfo=datetime.UTC)

    assert validar_barras("MSFT", [fila(con_hora)], HOY).validas[0].fecha == D06


def test_datos_de_otro_ticker() -> None:
    resultado = validar_barras("MSFT", [fila(D06, ticker="AAPL"), fila(D07, ticker="msft")], HOY)

    assert [b.fecha for b in resultado.validas] == [D07]
    assert resultado.descartes == [Descarte(D06, OTRO_TICKER)]


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (410.2500004, Decimal("410.250000")),
        (0.1, Decimal("0.100000")),
        (172.1234565, Decimal("172.123457")),
        (Decimal("172.1234565"), Decimal("172.123457")),
        (410, Decimal("410.000000")),
    ],
)
def test_conversion_a_decimal_de_seis_decimales(valor: object, esperado: Decimal) -> None:
    convertido = a_decimal(valor)

    assert convertido == esperado
    assert str(convertido) == str(esperado)


def test_apertura_fuera_del_rango_del_dia_se_acepta_con_aviso() -> None:
    resultado = validar_barras("MSFT", [fila(D06, apertura=412.5)], HOY)

    assert len(resultado.validas) == 1
    assert resultado.avisos == [Descarte(D06, FUERA_DEL_RANGO_DEL_DIA)]


def test_los_descartes_no_llevan_los_valores_recibidos() -> None:
    (descarte,) = _descartes(fila(D07, cierre="<script>alert(1)</script>"))

    assert "script" not in repr(descarte)
