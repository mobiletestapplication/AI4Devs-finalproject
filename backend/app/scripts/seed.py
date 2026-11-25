"""Seed mínimo de la cartera (design D6 de db-01-esquema).

Uso: ``python -m app.scripts.seed`` (en compose: ``docker compose exec api python -m
app.scripts.seed``). Inserta 3 posiciones fijas si no hay cartera vigente; si ya la hay, no
hace nada, para no sustituir la cartera del usuario. Desde BE-08 cargará
``cartera-ejemplo.xlsx`` con el caso de uso de importación.
"""

import datetime
import hashlib
import json
import sys
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.config import obtener_ajustes
from app.infrastructure.db.modelos import CarteraVigente, Importacion, Posicion
from app.infrastructure.db.session import crear_fabrica_sesiones, crear_motor

FECHA = datetime.date.fromisoformat

# (fila, ticker, fecha de compra, cantidad, precio de compra, fecha de venta, precio de venta)
POSICIONES_SEED: tuple[
    tuple[int, str, datetime.date, Decimal, Decimal, datetime.date | None, Decimal | None], ...
] = (
    (2, "AAPL", FECHA("2024-03-15"), Decimal("10"), Decimal("172.50"), None, None),
    (
        3,
        "MSFT",
        FECHA("2024-01-10"),
        Decimal("5"),
        Decimal("380.00"),
        FECHA("2024-12-20"),
        Decimal("435.00"),
    ),
    (4, "NVDA", FECHA("2024-06-03"), Decimal("2.5"), Decimal("120.25"), None, None),
)


def huella_del_seed() -> str:
    """SHA-256 de la representación canónica del fixture (ocupa el lugar del fichero)."""
    canonico = json.dumps([[str(campo) for campo in fila] for fila in POSICIONES_SEED])
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def sembrar(fabrica: sessionmaker[Session]) -> bool:
    """Crea la cartera del seed si no hay ninguna vigente. Devuelve si la ha creado."""
    with fabrica.begin() as sesion:
        if sesion.scalar(select(CarteraVigente.id)) is not None:
            return False
        importacion = Importacion(fichero_sha256=huella_del_seed())
        importacion.posiciones = [
            Posicion(
                fila=fila,
                ticker=ticker,
                fecha_compra=compra,
                cantidad=cantidad,
                precio_compra=p_compra,
                fecha_venta=venta,
                precio_venta=p_venta,
            )
            for fila, ticker, compra, cantidad, p_compra, venta, p_venta in POSICIONES_SEED
        ]
        sesion.add(importacion)
        sesion.flush()
        sesion.add(CarteraVigente(importacion_id=importacion.id))
    return True


def main() -> int:
    motor = crear_motor(obtener_ajustes())
    try:
        creada = sembrar(crear_fabrica_sesiones(motor))
    finally:
        motor.dispose()
    if creada:
        print(f"Seed cargado: {len(POSICIONES_SEED)} posiciones.")
    else:
        print("Ya hay una cartera vigente: el seed no la sustituye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
