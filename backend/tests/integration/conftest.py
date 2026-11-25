"""PostgreSQL real con Testcontainers (design D5 de db-01-esquema).

- ``postgres``: un contenedor ``postgres:16.16`` (la imagen de compose) por sesión de pytest.
- ``motor``: la BD del contenedor migrada con ``alembic upgrade head``.
- ``sesion`` y ``fabrica``: una transacción por test que se revierte al terminar.

El contenedor solo arranca si algún test pide estas fixtures.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic.config import Config
from pydantic import SecretStr
from sqlalchemy import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.community.postgres import PostgresContainer

from alembic import command
from app.infrastructure.config import Ajustes, obtener_ajustes
from app.infrastructure.db.session import crear_fabrica_sesiones, crear_motor

IMAGEN_POSTGRES = "postgres:16.16"
ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def url_de(contenedor: PostgresContainer, base_de_datos: str | None = None) -> str:
    url = contenedor.get_connection_url()
    if base_de_datos is None:
        return url
    return url.rsplit("/", 1)[0] + "/" + base_de_datos


def ajustes_para(url: str) -> Ajustes:
    return Ajustes(database_url=SecretStr(url))


def ejecutar_alembic(url: str, orden: str, revision: str = "head") -> None:
    """Ejecuta ``alembic <orden>`` contra ``url`` leyendo la URL por Ajustes, como en compose."""
    configuracion = Config(str(ALEMBIC_INI))
    anterior = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = url
    obtener_ajustes.cache_clear()
    try:
        if orden == "check":
            command.check(configuracion)
        else:
            getattr(command, orden)(configuracion, revision)
    finally:
        if anterior is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = anterior
        obtener_ajustes.cache_clear()


@pytest.fixture(scope="session")
def postgres() -> Iterator[PostgresContainer]:
    with PostgresContainer(IMAGEN_POSTGRES, driver="psycopg") as contenedor:
        yield contenedor


@pytest.fixture(scope="session")
def motor(postgres: PostgresContainer) -> Iterator[Engine]:
    url = url_de(postgres)
    ejecutar_alembic(url, "upgrade")
    motor = crear_motor(ajustes_para(url))
    yield motor
    motor.dispose()


@pytest.fixture
def conexion(motor: Engine) -> Iterator[Connection]:
    with motor.connect() as conexion:
        transaccion = conexion.begin()
        try:
            yield conexion
        finally:
            transaccion.rollback()


@pytest.fixture
def sesion(conexion: Connection) -> Iterator[Session]:
    with Session(bind=conexion, join_transaction_mode="create_savepoint") as sesion:
        yield sesion


@pytest.fixture
def fabrica(conexion: Connection) -> sessionmaker[Session]:
    """Fábrica como la de producción, pero dentro de la transacción del test."""
    fabrica = crear_fabrica_sesiones(conexion.engine)
    fabrica.configure(bind=conexion, join_transaction_mode="create_savepoint")
    return fabrica
