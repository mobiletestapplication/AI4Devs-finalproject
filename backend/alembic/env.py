"""Entorno de Alembic: la URL de la BD sale de Ajustes (DATABASE_URL), nunca de alembic.ini."""

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app.infrastructure.config import obtener_ajustes

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# DB-01 sustituye este valor por los metadatos de los modelos ORM.
target_metadata = None


def _url() -> str:
    return obtener_ajustes().database_url.get_secret_value()


def run_migrations_offline() -> None:
    """Genera el SQL de las migraciones sin conectarse a la BD."""
    context.configure(
        url=_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones contra la BD de DATABASE_URL."""
    motor = create_engine(_url(), poolclass=pool.NullPool)
    with motor.connect() as conexion:
        context.configure(connection=conexion, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
