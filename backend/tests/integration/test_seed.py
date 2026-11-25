"""Seed mínimo (tarea 3.5 de db-01-esquema; design D6)."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.modelos import CarteraVigente, Importacion, Posicion
from app.scripts.seed import huella_del_seed, sembrar


def _contar(sesion: Session, modelo: type[object]) -> int:
    return sesion.scalar(select(func.count()).select_from(modelo)) or 0


def test_el_seed_crea_la_cartera_vigente(fabrica: sessionmaker[Session]) -> None:
    assert sembrar(fabrica) is True

    with fabrica() as sesion:
        importacion = sesion.scalars(select(Importacion)).one()
        vigente = sesion.scalars(select(CarteraVigente)).one()
        posiciones = sesion.scalars(select(Posicion).order_by(Posicion.fila)).all()

    assert vigente.importacion_id == importacion.id
    assert importacion.fichero_sha256 == huella_del_seed()
    assert [p.ticker for p in posiciones] == ["AAPL", "MSFT", "NVDA"]
    assert [p.fecha_venta is None for p in posiciones] == [True, False, True]


def test_el_seed_no_sustituye_una_cartera_existente(fabrica: sessionmaker[Session]) -> None:
    sembrar(fabrica)

    assert sembrar(fabrica) is False

    with fabrica() as sesion:
        assert _contar(sesion, Importacion) == 1
        assert _contar(sesion, Posicion) == 3
