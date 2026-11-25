"""Conexiones a PostgreSQL sin estado global (design D7 de db-01-esquema).

Quien necesita la BD construye su motor a partir de unos Ajustes concretos: el seed con
los del entorno y los tests con los del contenedor. Importar este módulo no conecta.
"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.config import Ajustes


def crear_motor(ajustes: Ajustes) -> Engine:
    """Motor con `pool_pre_ping` para recuperar conexiones cerradas por PostgreSQL."""
    return create_engine(ajustes.database_url.get_secret_value(), pool_pre_ping=True)


def crear_fabrica_sesiones(motor: Engine) -> sessionmaker[Session]:
    """Sesiones sin `expire_on_commit`, para leer los objetos tras confirmar."""
    return sessionmaker(motor, expire_on_commit=False)
