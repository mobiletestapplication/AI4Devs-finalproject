"""Ajustes de la aplicación leídos del entorno (design O3 de ops-01-esqueleto)."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ListaSeparadaPorComas = Annotated[list[str], NoDecode]


class Ajustes(BaseSettings):
    """Configuración por entorno. Falla al arrancar si algún valor no es válido."""

    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    database_url: SecretStr
    hosts_admitidos: ListaSeparadaPorComas = Field(
        default_factory=lambda: ["localhost", "127.0.0.1"]
    )
    origenes_admitidos: ListaSeparadaPorComas = Field(
        default_factory=lambda: ["http://localhost:8080", "http://127.0.0.1:8080"]
    )
    proveedor_precios: Literal["yfinance", "ficheros"] = "yfinance"
    benchmark_ticker: str = Field(default="SPY", min_length=1)
    llm_api_key: SecretStr = SecretStr("")

    @field_validator("hosts_admitidos", "origenes_admitidos", mode="before")
    @classmethod
    def _separar_por_comas(cls, valor: object) -> object:
        if isinstance(valor, str):
            return [parte.strip() for parte in valor.split(",") if parte.strip()]
        return valor

    @field_validator("hosts_admitidos")
    @classmethod
    def _hosts_no_vacios(cls, valor: list[str]) -> list[str]:
        if not valor:
            raise ValueError("HOSTS_ADMITIDOS no puede estar vacía")
        return valor


@lru_cache
def obtener_ajustes() -> Ajustes:
    """Ajustes únicos del proceso; se validan la primera vez que se piden."""
    return Ajustes()
