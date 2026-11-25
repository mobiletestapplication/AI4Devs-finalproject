"""Restricciones del esquema (tarea 3.3 de db-01-esquema; casos de arquitectura de la
sección 2.6 del readme, que no salen de ningún escenario de las specs).

Cada caso comprueba el nombre de la restricción que salta, no solo que falle.
"""

import datetime
import uuid
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.db.modelos import (
    Base,
    CarteraVigente,
    CoberturaPrecio,
    Importacion,
    Posicion,
    PrecioDiario,
)

HOY = datetime.date(2025, 3, 7)
HUELLA = "0" * 64


def importacion() -> Importacion:
    return Importacion(id=uuid.uuid4(), fichero_sha256=HUELLA)


def posicion(importacion_id: uuid.UUID, **cambios: Any) -> Posicion:
    valores: dict[str, Any] = {
        "importacion_id": importacion_id,
        "fila": 2,
        "ticker": "AAPL",
        "fecha_compra": datetime.date(2024, 3, 15),
        "cantidad": Decimal("10"),
        "precio_compra": Decimal("172.5"),
    }
    return Posicion(**(valores | cambios))


def precio(**cambios: Any) -> PrecioDiario:
    valores: dict[str, Any] = {
        "ticker": "AAPL",
        "fecha": HOY,
        "apertura": Decimal("170"),
        "maximo": Decimal("175"),
        "minimo": Decimal("169"),
        "cierre": Decimal("172"),
        "cierre_sin_ajustar": Decimal("172"),
        "fuente": "ficheros",
    }
    return PrecioDiario(**(valores | cambios))


def cobertura(**cambios: Any) -> CoberturaPrecio:
    valores: dict[str, Any] = {
        "ticker": "AAPL",
        "desde": datetime.date(2024, 1, 2),
        "hasta": HOY,
    }
    return CoberturaPrecio(**(valores | cambios))


def con_importacion(sesion: Session) -> Importacion:
    nueva = importacion()
    sesion.add(nueva)
    sesion.flush()
    return nueva


def nombre_de_restriccion(error: IntegrityError) -> str | None:
    """Nombre de la restricción que informa PostgreSQL (psycopg ``Diagnostic``)."""
    diagnostico = getattr(error.orig, "diag", None)
    return getattr(diagnostico, "constraint_name", None)


def restriccion_violada(sesion: Session, *objetos: Base) -> str | None:
    """Inserta en un savepoint y devuelve el nombre de la restricción que lo impide."""
    with pytest.raises(IntegrityError) as error, sesion.begin_nested():
        sesion.add_all(objetos)
        sesion.flush()
    return nombre_de_restriccion(error.value)


@pytest.mark.parametrize(
    ("cambios", "restriccion"),
    [
        ({"cantidad": Decimal("0")}, "ck_posicion_cantidad"),
        ({"precio_compra": Decimal("-1")}, "ck_posicion_precio_compra"),
        ({"fecha_venta": datetime.date(2024, 12, 20)}, "ck_posicion_venta_completa"),
        ({"precio_venta": Decimal("435")}, "ck_posicion_venta_completa"),
        (
            {"fecha_venta": datetime.date(2024, 3, 14), "precio_venta": Decimal("180")},
            "ck_posicion_venta_posterior",
        ),
        (
            {"fecha_venta": datetime.date(2024, 12, 20), "precio_venta": Decimal("-10")},
            "ck_posicion_precio_venta",
        ),
        ({"fila": 1}, "ck_posicion_fila"),
        ({"ticker": "aapl$"}, "ck_posicion_ticker"),
    ],
)
def test_posicion_rechaza_valores_no_validos(
    sesion: Session, cambios: dict[str, Any], restriccion: str
) -> None:
    padre = con_importacion(sesion)

    assert restriccion_violada(sesion, posicion(padre.id, **cambios)) == restriccion


def test_posicion_rechaza_fila_repetida_en_la_misma_importacion(sesion: Session) -> None:
    padre = con_importacion(sesion)
    sesion.add(posicion(padre.id))
    sesion.flush()

    otra = posicion(padre.id, ticker="MSFT")
    assert restriccion_violada(sesion, otra) == "uq_posicion_importacion_id_fila"


@pytest.mark.parametrize(
    ("cambios", "restriccion"),
    [
        ({"ticker": "aapl$"}, "ck_precio_diario_ticker"),
        ({"maximo": Decimal("168")}, "ck_precio_diario_maximo_minimo"),
        ({"fuente": "bloomberg"}, "ck_precio_diario_fuente"),
        ({"cierre_sin_ajustar": Decimal("0")}, "ck_precio_diario_cierre_sin_ajustar"),
    ],
)
def test_precio_diario_rechaza_valores_no_validos(
    sesion: Session, cambios: dict[str, Any], restriccion: str
) -> None:
    assert restriccion_violada(sesion, precio(**cambios)) == restriccion


def test_cobertura_rechaza_rango_invertido(sesion: Session) -> None:
    hasta_anterior = cobertura(hasta=datetime.date(2023, 12, 31))

    assert restriccion_violada(sesion, hasta_anterior) == "ck_cobertura_precio_rango"


@pytest.mark.parametrize(
    ("id_segunda", "restriccion"),
    [(True, "pk_cartera_vigente"), (False, "ck_cartera_vigente_una_fila")],
)
def test_solo_puede_haber_una_cartera_vigente(
    sesion: Session, id_segunda: bool, restriccion: str
) -> None:
    primera, segunda = con_importacion(sesion), con_importacion(sesion)
    sesion.add(CarteraVigente(importacion_id=primera.id))
    sesion.flush()

    otra = CarteraVigente(id=id_segunda, importacion_id=segunda.id)
    assert restriccion_violada(sesion, otra) == restriccion


def test_no_se_puede_borrar_la_importacion_vigente(sesion: Session) -> None:
    vigente = con_importacion(sesion)
    sesion.add(CarteraVigente(importacion_id=vigente.id))
    sesion.flush()

    with pytest.raises(IntegrityError) as error, sesion.begin_nested():
        sesion.execute(delete(Importacion).where(Importacion.id == vigente.id))
    assert nombre_de_restriccion(error.value) == "fk_cartera_vigente_importacion_id_importacion"


def test_borrar_una_importacion_no_vigente_borra_sus_posiciones(sesion: Session) -> None:
    anterior = con_importacion(sesion)
    sesion.add_all([posicion(anterior.id), posicion(anterior.id, fila=3, ticker="MSFT")])
    sesion.flush()

    sesion.execute(delete(Importacion).where(Importacion.id == anterior.id))

    restantes = sesion.scalar(select(func.count()).select_from(Posicion))
    assert restantes == 0


def test_una_fila_valida_de_cada_tabla_se_inserta(sesion: Session) -> None:
    padre = con_importacion(sesion)
    cerrada = posicion(
        padre.id,
        fila=3,
        ticker="BRK.B",
        fecha_venta=datetime.date(2024, 3, 15),
        precio_venta=Decimal("180"),
    )
    sesion.add_all(
        [
            CarteraVigente(importacion_id=padre.id),
            posicion(padre.id),
            cerrada,
            precio(),
            cobertura(ultimo_split=datetime.date(2024, 6, 10)),
        ]
    )
    sesion.flush()

    vigente = sesion.scalars(select(CarteraVigente)).one()
    assert vigente.id is True
    assert vigente.actualizada_en is not None
