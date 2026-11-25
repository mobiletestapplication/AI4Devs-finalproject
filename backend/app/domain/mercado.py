"""Datos de mercado (design S7 de sec-01-seguridad-api).

``validar_barras`` es la única frontera de confianza para los datos del proveedor de
mercado: todo lo que llega de yfinance o del proveedor de ficheros pasa por aquí antes de
guardarse en la caché o usarse en un cálculo. Función pura: no registra ni lanza; devuelve
las barras válidas, los descartes con su motivo y los avisos.
"""

import datetime
import math
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from app.domain.modelos import BarraDiaria

PRECIOS = ("apertura", "maximo", "minimo", "cierre", "cierre_sin_ajustar")
SEIS_DECIMALES = Decimal("0.000001")
# NUMERIC(18, 6) del esquema: como mucho 12 cifras enteras.
PRECIO_MAXIMO = Decimal(10) ** 12

FECHA_NO_VALIDA = "fecha no válida"
FECHA_REPETIDA = "fecha repetida"
FECHA_FUTURA = "fecha futura"
OTRO_TICKER = "otro ticker"
PRECIO_NO_NUMERICO = "precio no numérico"
PRECIO_NO_POSITIVO = "precio no positivo"
PRECIO_FUERA_DE_RANGO = "precio fuera de rango"
MAXIMO_MENOR_QUE_MINIMO = "máximo menor que el mínimo"
FUERA_DEL_RANGO_DEL_DIA = "apertura o cierre fuera del rango máximo-mínimo"


@dataclass(frozen=True)
class Descarte:
    """Barra rechazada: fecha (si se pudo leer) y motivo, nunca los valores recibidos."""

    fecha: datetime.date | None
    motivo: str


@dataclass(frozen=True)
class ResultadoValidacion:
    validas: list[BarraDiaria] = field(default_factory=list)
    descartes: list[Descarte] = field(default_factory=list)
    avisos: list[Descarte] = field(default_factory=list)


def a_decimal(valor: object) -> Decimal | None:
    """Convierte un precio recibido a ``Decimal`` con 6 decimales, o ``None`` si no es un número.

    Los ``float`` se convierten con ``Decimal(repr(round(x, 6)))`` (sección 3 del readme)
    para no arrastrar el error binario; ``bool`` y textos no se aceptan como números.
    """
    if isinstance(valor, bool):
        return None
    if isinstance(valor, float):
        if not math.isfinite(valor):
            return None
        decimal = Decimal(repr(round(valor, 6)))
    elif isinstance(valor, int):
        decimal = Decimal(valor)
    elif isinstance(valor, Decimal):
        if not valor.is_finite():
            return None
        decimal = valor
    else:
        return None
    return decimal.quantize(SEIS_DECIMALES, rounding=ROUND_HALF_UP)


def _fecha(valor: object) -> datetime.date | None:
    if isinstance(valor, datetime.datetime):
        return valor.date()
    if isinstance(valor, datetime.date):
        return valor
    return None


def _motivo_de_precios(precios: Mapping[str, Decimal | None]) -> str | None:
    if any(p is None for p in precios.values()):
        return PRECIO_NO_NUMERICO
    valores = {nombre: p for nombre, p in precios.items() if p is not None}
    if any(p <= 0 for p in valores.values()):
        return PRECIO_NO_POSITIVO
    if any(p >= PRECIO_MAXIMO for p in valores.values()):
        return PRECIO_FUERA_DE_RANGO
    if valores["maximo"] < valores["minimo"]:
        return MAXIMO_MENOR_QUE_MINIMO
    return None


def validar_barras(
    ticker_pedido: str, filas: Iterable[Mapping[str, object]], hoy: datetime.date
) -> ResultadoValidacion:
    """Valida las barras recibidas del proveedor para ``ticker_pedido``.

    Se descartan las barras con fecha no válida, repetida (todas las de esa fecha) o
    posterior a ``hoy``; de otro ticker; o con algún precio no numérico, no finito, no
    positivo, fuera del rango de ``NUMERIC(18, 6)`` o con el máximo menor que el mínimo.
    Las que tienen la apertura o el cierre fuera de [mínimo, máximo] se aceptan con aviso,
    porque los datos ajustados del proveedor a veces se salen ligeramente de ese rango.
    """
    ticker = ticker_pedido.strip().upper()
    lista = list(filas)
    repeticiones = Counter(f for f in (_fecha(fila.get("fecha")) for fila in lista) if f)
    resultado = ResultadoValidacion()

    for fila in lista:
        fecha = _fecha(fila.get("fecha"))
        ticker_recibido = fila.get("ticker")
        precios = {nombre: a_decimal(fila.get(nombre)) for nombre in PRECIOS}
        if fecha is None:
            resultado.descartes.append(Descarte(None, FECHA_NO_VALIDA))
            continue
        if repeticiones[fecha] > 1:
            motivo: str | None = FECHA_REPETIDA
        elif fecha > hoy:
            motivo = FECHA_FUTURA
        elif ticker_recibido is not None and str(ticker_recibido).strip().upper() != ticker:
            motivo = OTRO_TICKER
        else:
            motivo = _motivo_de_precios(precios)
        if motivo is not None:
            resultado.descartes.append(Descarte(fecha, motivo))
            continue

        barra = BarraDiaria(ticker=ticker, fecha=fecha, **_sin_nulos(precios))
        if not (barra.minimo <= barra.apertura <= barra.maximo) or not (
            barra.minimo <= barra.cierre <= barra.maximo
        ):
            resultado.avisos.append(Descarte(fecha, FUERA_DEL_RANGO_DEL_DIA))
        resultado.validas.append(barra)

    resultado.validas.sort(key=lambda b: b.fecha)
    return resultado


def _sin_nulos(precios: Mapping[str, Decimal | None]) -> dict[str, Decimal]:
    return {nombre: p for nombre, p in precios.items() if p is not None}
