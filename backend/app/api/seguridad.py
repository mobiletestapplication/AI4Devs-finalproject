"""Middlewares de seguridad de la API (design S1-S5 de sec-01-seguridad-api).

Orden, de fuera hacia dentro: cabeceras → Host → origen → límite de frecuencia →
aplicación. Los tres rechazos se resuelven sin enrutar ni leer el cuerpo.
"""

import math
import time
from collections.abc import Iterable, Mapping

from limits import RateLimitItem, parse
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import MovingWindowRateLimiter
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.errores import aplicar_cabeceras_seguridad, respuesta_problema

METODOS_QUE_MODIFICAN = frozenset({"POST", "PUT", "PATCH", "DELETE"})
SEC_FETCH_SITE_AJENOS = frozenset({"cross-site", "same-site"})

# Límites de las operaciones caras por método y ruta (spec seguridad-api; design S4).
LIMITES: Mapping[tuple[str, str], RateLimitItem] = {
    ("POST", "/api/cartera/importacion"): parse("5/minute"),
    ("POST", "/api/backtests"): parse("10/minute"),
}


def host_sin_puerto(host: str) -> str:
    """``localhost:8080`` → ``localhost``; ``[::1]:8000`` → ``[::1]``; en minúsculas."""
    host = host.strip().lower()
    if host.startswith("["):
        return host.split("]", 1)[0] + "]"
    return host.rsplit(":", 1)[0] if ":" in host else host


class MiddlewareCabeceras:
    """Añade las cabeceras de seguridad a todas las respuestas HTTP."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def enviar(mensaje: Message) -> None:
            if mensaje["type"] == "http.response.start":
                aplicar_cabeceras_seguridad(MutableHeaders(scope=mensaje))
            await send(mensaje)

        await self.app(scope, receive, enviar)


class MiddlewareHost:
    """Rechaza con 400 los ``Host`` no admitidos (DNS rebinding), sin repetir el valor."""

    def __init__(self, app: ASGIApp, hosts_admitidos: Iterable[str]) -> None:
        self.app = app
        self.hosts = frozenset(h.strip().lower() for h in hosts_admitidos)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            host = Headers(scope=scope).get("host", "")
            if host_sin_puerto(host) not in self.hosts:
                respuesta = respuesta_problema(
                    400,
                    "host-no-admitido",
                    titulo="Host no admitido",
                    detalle="La cabecera Host no corresponde a esta aplicación.",
                )
                await respuesta(scope, receive, send)
                return
        await self.app(scope, receive, send)


class MiddlewareOrigen:
    """Rechaza con 403 las peticiones que modifican estado desde otro origen (CSRF)."""

    def __init__(self, app: ASGIApp, origenes_admitidos: Iterable[str]) -> None:
        self.app = app
        self.origenes = frozenset(o.strip().lower().rstrip("/") for o in origenes_admitidos)

    def _admitido(self, cabeceras: Headers) -> bool:
        origen = cabeceras.get("origin")
        if origen is not None:
            return origen.strip().lower().rstrip("/") in self.origenes
        return cabeceras.get("sec-fetch-site", "").lower() not in SEC_FETCH_SITE_AJENOS

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] == "http"
            and scope["method"] in METODOS_QUE_MODIFICAN
            and not self._admitido(Headers(scope=scope))
        ):
            respuesta = respuesta_problema(
                403,
                "origen-no-permitido",
                detalle="La petición no procede de la propia aplicación.",
            )
            await respuesta(scope, receive, send)
            return
        await self.app(scope, receive, send)


class MiddlewareLimite:
    """Límite de frecuencia por método y ruta con ``limits``, antes de leer el cuerpo."""

    def __init__(
        self, app: ASGIApp, limites: Mapping[tuple[str, str], RateLimitItem] = LIMITES
    ) -> None:
        self.app = app
        self.limites = dict(limites)
        self.limitador = MovingWindowRateLimiter(MemoryStorage())

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            ruta = scope["path"].rstrip("/") or "/"
            limite = self.limites.get((scope["method"], ruta))
            if limite is not None:
                cliente = scope.get("client")
                clave = cliente[0] if cliente else "desconocido"
                if not await self.limitador.hit(limite, clave, scope["method"], ruta):
                    ventana = await self.limitador.get_window_stats(
                        limite, clave, scope["method"], ruta
                    )
                    segundos = max(1, math.ceil(ventana.reset_time - time.time()))
                    respuesta = respuesta_problema(
                        429,
                        "demasiadas-peticiones",
                        detalle=f"Has superado el límite. Vuelve a intentarlo en {segundos} s.",
                        cabeceras={"Retry-After": str(segundos)},
                        reintentar_en=segundos,
                    )
                    await respuesta(scope, receive, send)
                    return
        await self.app(scope, receive, send)
