"""Punto de arranque: crea la aplicación FastAPI y conecta puertos y adaptadores."""

from collections.abc import Mapping

from fastapi import FastAPI
from limits import RateLimitItem

from app.api.errores import registrar_manejadores
from app.api.seguridad import (
    LIMITES,
    MiddlewareCabeceras,
    MiddlewareHost,
    MiddlewareLimite,
    MiddlewareOrigen,
)
from app.infrastructure.config import Ajustes, obtener_ajustes
from app.infrastructure.registro import configurar_registro


def crear_app(
    ajustes: Ajustes | None = None,
    limites: Mapping[tuple[str, str], RateLimitItem] = LIMITES,
) -> FastAPI:
    """Crea la aplicación; valida los ajustes al arrancar para fallar pronto.

    ``limites`` solo se sustituye en los tests, para probar el límite sin las rutas reales.
    """
    ajustes = ajustes or obtener_ajustes()
    configurar_registro(ajustes)
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
    registrar_manejadores(app)
    # El último añadido es el más externo (design S1 de sec-01-seguridad-api):
    # cabeceras → Host → origen → límite → aplicación.
    app.add_middleware(MiddlewareLimite, limites=limites)
    app.add_middleware(MiddlewareOrigen, origenes_admitidos=ajustes.origenes_admitidos)
    app.add_middleware(MiddlewareHost, hosts_admitidos=ajustes.hosts_admitidos)
    app.add_middleware(MiddlewareCabeceras)
    return app


app = crear_app()
