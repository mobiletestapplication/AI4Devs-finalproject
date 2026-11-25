"""Registro estructurado en JSON y sin secretos (design S6 de sec-01-seguridad-api).

Una línea JSON por evento con campos fijos. Los valores secretos (contraseña de la BD y
clave del LLM) se sustituyen por ``***`` antes de escribir nada, también en las trazas.
"""

import datetime
import json
import logging
from collections.abc import Iterable
from typing import Protocol

from sqlalchemy.engine import make_url

from app.infrastructure.config import Ajustes

LOGGER_APP = "app"
NOMBRE_MANEJADOR = "traide-json"
OCULTO = "***"
CAMPOS_EXTRA = ("incidencia", "metodo", "ruta", "estado", "ticker", "fecha", "motivo")

registro_mercado = logging.getLogger(f"{LOGGER_APP}.mercado")


class FormateadorJson(logging.Formatter):
    """Serializa cada registro como una línea JSON con campos fijos."""

    def format(self, record: logging.LogRecord) -> str:
        datos: dict[str, object] = {
            "ts": datetime.datetime.fromtimestamp(record.created, datetime.UTC).isoformat(),
            "nivel": record.levelname,
            "logger": record.name,
            "mensaje": record.getMessage(),
        }
        for campo in CAMPOS_EXTRA:
            if (valor := getattr(record, campo, None)) is not None:
                datos[campo] = valor
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            datos["excepcion"] = record.exc_text
        return json.dumps(datos, ensure_ascii=False, default=str)


class FiltroSecretos(logging.Filter):
    """Oculta los valores secretos en el mensaje y en la traza de cada registro."""

    def __init__(self, secretos: Iterable[str]) -> None:
        super().__init__()
        # Los más largos primero, por si uno contiene a otro.
        self._secretos = sorted({s for s in secretos if s}, key=len, reverse=True)

    def ocultar(self, texto: str) -> str:
        for secreto in self._secretos:
            texto = texto.replace(secreto, OCULTO)
        return texto

    def filter(self, record: logging.LogRecord) -> bool:
        if self._secretos:
            record.msg = self.ocultar(record.getMessage())
            record.args = None
            if record.exc_info:
                record.exc_text = self.ocultar(logging.Formatter().formatException(record.exc_info))
                record.exc_info = None
        return True


def secretos_de(ajustes: Ajustes) -> list[str]:
    """Valores que nunca deben aparecer en el log."""
    secretos = [ajustes.llm_api_key.get_secret_value()]
    contrasena = make_url(ajustes.database_url.get_secret_value()).password
    if contrasena:
        secretos.append(str(contrasena))
    return [s for s in secretos if s]


def configurar_registro(ajustes: Ajustes, nivel: int = logging.INFO) -> None:
    """Instala (una sola vez) el manejador JSON con el filtro de secretos en el logger ``app``."""
    logger = logging.getLogger(LOGGER_APP)
    logger.setLevel(nivel)
    for manejador in list(logger.handlers):
        if manejador.get_name() == NOMBRE_MANEJADOR:
            logger.removeHandler(manejador)
    manejador = logging.StreamHandler()
    manejador.set_name(NOMBRE_MANEJADOR)
    manejador.setFormatter(FormateadorJson())
    manejador.addFilter(FiltroSecretos(secretos_de(ajustes)))
    logger.addHandler(manejador)


class _Descarte(Protocol):
    @property
    def fecha(self) -> datetime.date | None: ...

    @property
    def motivo(self) -> str: ...


def registrar_descartes(ticker: str, descartes: Iterable[_Descarte]) -> None:
    """Una línea por barra descartada del proveedor: ticker, fecha y motivo, nunca los valores."""
    for descarte in descartes:
        registro_mercado.warning(
            "barra del proveedor descartada",
            extra={
                "ticker": ticker,
                "fecha": descarte.fecha.isoformat() if descarte.fecha else None,
                "motivo": descarte.motivo,
            },
        )
