"""Modelos ORM del esquema de la sección 3 del readme (design D1-D4 de db-01-esquema).

Importes, precios y cantidades en NUMERIC(18, 6) leídos como Decimal; nunca coma flotante.
Cada restricción tiene un nombre estable (convención de MetaData + nombre corto del CHECK).
"""

import datetime
import uuid
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

CONVENCION_DE_NOMBRES = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

PATRON_TICKER = "^[A-Z.-]{1,10}$"
FUENTES_DE_PRECIOS = ("yfinance", "ficheros")


def _importe() -> Numeric[Decimal]:
    return Numeric(18, 6, asdecimal=True)


def _instante() -> DateTime:
    return DateTime(timezone=True)


def _ticker_valido(columna: str = "ticker") -> CheckConstraint:
    return CheckConstraint(f"{columna} ~ '{PATRON_TICKER}'", name="ticker")


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENCION_DE_NOMBRES)


class Importacion(Base):
    """Cada carga válida del XLSX."""

    __tablename__ = "importacion"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    fichero_sha256: Mapped[str] = mapped_column(CHAR(64), index=True)
    importada_en: Mapped[datetime.datetime] = mapped_column(_instante(), server_default=func.now())

    posiciones: Mapped[list["Posicion"]] = relationship(
        back_populates="importacion", passive_deletes=True
    )


class CarteraVigente(Base):
    """Tabla de una sola fila que apunta a la importación vigente."""

    __tablename__ = "cartera_vigente"
    __table_args__ = (CheckConstraint("id", name="una_fila"),)

    id: Mapped[bool] = mapped_column(Boolean, primary_key=True, server_default=true())
    importacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("importacion.id", ondelete="RESTRICT"), unique=True
    )
    actualizada_en: Mapped[datetime.datetime] = mapped_column(
        _instante(), server_default=func.now()
    )


class Posicion(Base):
    """Una fila del fichero: abierta (sin venta) o cerrada (con fecha y precio de venta)."""

    __tablename__ = "posicion"
    __table_args__ = (
        UniqueConstraint("importacion_id", "fila"),
        Index(None, "importacion_id", "ticker"),
        CheckConstraint("fila >= 2", name="fila"),
        _ticker_valido(),
        CheckConstraint("cantidad > 0", name="cantidad"),
        CheckConstraint("precio_compra > 0", name="precio_compra"),
        CheckConstraint("precio_venta > 0", name="precio_venta"),
        CheckConstraint("(fecha_venta IS NULL) = (precio_venta IS NULL)", name="venta_completa"),
        CheckConstraint("fecha_venta >= fecha_compra", name="venta_posterior"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    importacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("importacion.id", ondelete="CASCADE")
    )
    fila: Mapped[int] = mapped_column(Integer)
    ticker: Mapped[str] = mapped_column(String(10))
    fecha_compra: Mapped[datetime.date] = mapped_column(Date)
    cantidad: Mapped[Decimal] = mapped_column(_importe())
    precio_compra: Mapped[Decimal] = mapped_column(_importe())
    fecha_venta: Mapped[datetime.date | None] = mapped_column(Date)
    precio_venta: Mapped[Decimal | None] = mapped_column(_importe())

    importacion: Mapped[Importacion] = relationship(back_populates="posiciones")


class PrecioDiario(Base):
    """Caché OHLC diaria: serie ajustada por splits y cierre sin ajustar."""

    __tablename__ = "precio_diario"
    __table_args__ = (
        _ticker_valido(),
        CheckConstraint("apertura > 0", name="apertura"),
        CheckConstraint("maximo > 0", name="maximo"),
        CheckConstraint("minimo > 0", name="minimo"),
        CheckConstraint("cierre > 0", name="cierre"),
        CheckConstraint("cierre_sin_ajustar > 0", name="cierre_sin_ajustar"),
        CheckConstraint("maximo >= minimo", name="maximo_minimo"),
        CheckConstraint(
            "fuente IN (" + ", ".join(f"'{f}'" for f in FUENTES_DE_PRECIOS) + ")",
            name="fuente",
        ),
    )

    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    fecha: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    apertura: Mapped[Decimal] = mapped_column(_importe())
    maximo: Mapped[Decimal] = mapped_column(_importe())
    minimo: Mapped[Decimal] = mapped_column(_importe())
    cierre: Mapped[Decimal] = mapped_column(_importe())
    cierre_sin_ajustar: Mapped[Decimal] = mapped_column(_importe())
    fuente: Mapped[str] = mapped_column(String)
    obtenido_en: Mapped[datetime.datetime] = mapped_column(_instante(), server_default=func.now())


class CoberturaPrecio(Base):
    """Rango de fechas ya pedido al proveedor por ticker y último split conocido."""

    __tablename__ = "cobertura_precio"
    __table_args__ = (
        _ticker_valido(),
        CheckConstraint("hasta >= desde", name="rango"),
    )

    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    desde: Mapped[datetime.date] = mapped_column(Date)
    hasta: Mapped[datetime.date] = mapped_column(Date)
    actualizado_en: Mapped[datetime.datetime] = mapped_column(
        _instante(), server_default=func.now()
    )
    ultimo_split: Mapped[datetime.date | None] = mapped_column(Date)
