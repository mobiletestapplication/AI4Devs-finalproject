"""Modelos del dominio: dataclasses inmutables, sin I/O ni dependencias externas."""

import datetime
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BarraDiaria:
    """Barra OHLC diaria ya validada (design S7 de sec-01-seguridad-api).

    Precios en USD como ``Decimal`` con 6 decimales: OHLC ajustado por splits y cierre sin
    ajustar, como en ``PRECIO_DIARIO`` (sección 3 del readme).
    """

    ticker: str
    fecha: datetime.date
    apertura: Decimal
    maximo: Decimal
    minimo: Decimal
    cierre: Decimal
    cierre_sin_ajustar: Decimal
