"""Punto de arranque: crea la aplicación FastAPI y conecta puertos y adaptadores."""

from fastapi import FastAPI

from app.infrastructure.config import Ajustes, obtener_ajustes


def crear_app(ajustes: Ajustes | None = None) -> FastAPI:
    """Crea la aplicación; valida los ajustes al arrancar para fallar pronto."""
    ajustes = ajustes or obtener_ajustes()
    app = FastAPI(
        title="trAIde API",
        version="0.1.0",
        description=(
            "API educativa sobre una cartera simulada. "
            "Las señales son orientativas y no constituyen asesoramiento financiero."
        ),
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )
    app.state.ajustes = ajustes
    return app


app = crear_app()
