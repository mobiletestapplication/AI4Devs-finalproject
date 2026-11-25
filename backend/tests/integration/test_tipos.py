"""Tipos exactos del esquema (tarea 3.4 de db-01-esquema; design D3)."""

import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.modelos import Posicion
from tests.integration.test_restricciones import con_importacion, posicion


def _guardar_y_leer(sesion: Session, cantidad: Decimal) -> Posicion:
    padre = con_importacion(sesion)
    sesion.add(posicion(padre.id, cantidad=cantidad))
    sesion.flush()
    sesion.expire_all()
    return sesion.scalars(select(Posicion).where(Posicion.importacion_id == padre.id)).one()


def test_un_decimo_se_lee_como_decimal_exacto(sesion: Session) -> None:
    leida = _guardar_y_leer(sesion, Decimal("0.1"))

    assert isinstance(leida.cantidad, Decimal)
    assert str(leida.cantidad) == "0.100000"


def test_la_bd_redondea_en_silencio_a_seis_decimales(sesion: Session) -> None:
    """Documenta por qué el rechazo de más de 6 decimales es de la aplicación (BE-01b)."""
    leida = _guardar_y_leer(sesion, Decimal("0.1234567"))

    assert str(leida.cantidad) == "0.123457"


def test_las_fechas_se_leen_como_date(sesion: Session) -> None:
    leida = _guardar_y_leer(sesion, Decimal("1"))

    assert type(leida.fecha_compra) is datetime.date
