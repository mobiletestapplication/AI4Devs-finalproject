"""Migraciones de Alembic (tareas 3.1 y 3.2 de db-01-esquema)."""

from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine, inspect, text
from testcontainers.community.postgres import PostgresContainer

from tests.integration.conftest import ejecutar_alembic, url_de

TABLAS = {"cartera_vigente", "importacion", "posicion", "precio_diario", "cobertura_precio"}


def test_upgrade_head_crea_las_cinco_tablas(motor: Engine) -> None:
    with motor.connect() as conexion:
        tablas = conexion.scalars(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        ).all()

    assert set(tablas) == TABLAS | {"alembic_version"}


def test_modelos_y_migracion_no_difieren(motor: Engine, postgres: PostgresContainer) -> None:
    ejecutar_alembic(url_de(postgres), "check")


@pytest.fixture
def base_de_datos_limpia(motor: Engine, postgres: PostgresContainer) -> Iterator[str]:
    nombre = "migracion_limpia"
    administrador = motor.execution_options(isolation_level="AUTOCOMMIT")
    with administrador.connect() as conexion:
        conexion.execute(text(f"DROP DATABASE IF EXISTS {nombre}"))
        conexion.execute(text(f"CREATE DATABASE {nombre}"))
    yield url_de(postgres, nombre)
    with administrador.connect() as conexion:
        conexion.execute(text(f"DROP DATABASE {nombre} WITH (FORCE)"))


def _tablas(url: str) -> set[str]:
    motor = create_engine(url)
    try:
        return set(inspect(motor).get_table_names()) - {"alembic_version"}
    finally:
        motor.dispose()


def test_upgrade_downgrade_y_upgrade_en_limpio(base_de_datos_limpia: str) -> None:
    ejecutar_alembic(base_de_datos_limpia, "upgrade")
    assert _tablas(base_de_datos_limpia) == TABLAS

    ejecutar_alembic(base_de_datos_limpia, "downgrade", "base")
    assert _tablas(base_de_datos_limpia) == set()

    ejecutar_alembic(base_de_datos_limpia, "upgrade")
    assert _tablas(base_de_datos_limpia) == TABLAS
