"""Formato común de errores (RFC 9457) y cabeceras de seguridad (design S5 de sec-01-seguridad-api).

Todos los errores salen en ``application/problem+json`` con textos generados por la
aplicación: nunca se repiten valores de la petición ni texto de terceros.
"""

import logging
import re
import uuid
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.exceptions import HTTPException as StarletteHTTPException

MEDIA_PROBLEMA = "application/problem+json"
PREFIJO_TIPO = "urn:traide:error:"

CABECERAS_SEGURIDAD = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Cache-Control": "no-store",
}
CSP_JSON = "default-src 'none'; frame-ancestors 'none'"

TITULOS = {
    400: "Petición no válida",
    403: "Origen no permitido",
    404: "Recurso no encontrado",
    405: "Método no permitido",
    413: "Contenido demasiado grande",
    415: "Tipo de contenido no admitido",
    422: "Contenido no válido",
    429: "Demasiadas peticiones",
    500: "Error interno",
    503: "Servicio no disponible",
}

UBICACIONES = {
    "path": "ruta",
    "query": "consulta",
    "header": "cabecera",
    "cookie": "cookie",
    "body": "cuerpo",
}

# Motivos por tipo de error de Pydantic: nunca se usa ``msg`` ni ``input`` (sin eco).
MOTIVOS = {
    "missing": "obligatorio",
    "extra_forbidden": "campo no admitido",
    "int_parsing": "debe ser un número entero",
    "int_type": "debe ser un número entero",
    "int_from_float": "debe ser un número entero",
    "float_parsing": "debe ser un número",
    "float_type": "debe ser un número",
    "decimal_parsing": "debe ser un número",
    "decimal_type": "debe ser un número",
    "bool_parsing": "debe ser verdadero o falso",
    "bool_type": "debe ser verdadero o falso",
    "date_parsing": "debe ser una fecha AAAA-MM-DD",
    "date_from_datetime_parsing": "debe ser una fecha AAAA-MM-DD",
    "date_type": "debe ser una fecha AAAA-MM-DD",
    "greater_than": "fuera de rango",
    "greater_than_equal": "fuera de rango",
    "less_than": "fuera de rango",
    "less_than_equal": "fuera de rango",
    "literal_error": "valor no admitido",
    "enum": "valor no admitido",
    "string_type": "debe ser un texto",
    "string_too_short": "demasiado corto",
    "string_too_long": "demasiado largo",
    "string_pattern_mismatch": "formato no válido",
    "json_invalid": "JSON no válido",
    "model_attributes_type": "debe ser un objeto JSON",
    "dict_type": "debe ser un objeto JSON",
    "list_type": "debe ser una lista",
}
MOTIVO_POR_DEFECTO = "valor no válido"

# Los nombres de campo pueden venir del cliente (campos extra): solo se repiten si son
# identificadores simples y cortos.
_NOMBRE_DE_CAMPO_SEGURO = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,39}")

registro = logging.getLogger("app.api.errores")


def aplicar_cabeceras_seguridad(cabeceras: MutableHeaders) -> None:
    """Cabeceras de todas las respuestas de la API; CSP estricta solo en las JSON."""
    for nombre, valor in CABECERAS_SEGURIDAD.items():
        cabeceras[nombre] = valor
    tipo = cabeceras.get("content-type", "")
    if tipo.startswith(("application/json", MEDIA_PROBLEMA)):
        cabeceras["Content-Security-Policy"] = CSP_JSON


def respuesta_problema(
    status: int,
    codigo: str,
    *,
    titulo: str | None = None,
    detalle: str | None = None,
    cabeceras: Mapping[str, str] | None = None,
    **extensiones: Any,
) -> JSONResponse:
    """Respuesta ``application/problem+json`` con las cabeceras de seguridad."""
    cuerpo: dict[str, Any] = {
        "type": PREFIJO_TIPO + codigo,
        "title": titulo or TITULOS.get(status, "Error"),
        "status": status,
    }
    if detalle:
        cuerpo["detail"] = detalle
    cuerpo.update(extensiones)
    respuesta = JSONResponse(
        cuerpo, status_code=status, media_type=MEDIA_PROBLEMA, headers=dict(cabeceras or {})
    )
    aplicar_cabeceras_seguridad(respuesta.headers)
    return respuesta


def _nombre_de_campo(partes: Sequence[int | str]) -> str:
    seguras = [
        str(parte)
        if isinstance(parte, int) or _NOMBRE_DE_CAMPO_SEGURO.fullmatch(parte)
        else "(no reconocido)"
        for parte in partes
    ]
    return ".".join(seguras)


def errores_de_validacion(errores: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Traduce los errores de Pydantic a ``{ubicacion, campo, motivo}`` sin valores recibidos."""
    resultado: list[dict[str, str]] = []
    for error in errores:
        loc = tuple(error.get("loc", ()))
        ubicacion = UBICACIONES.get(str(loc[0]), "petición") if loc else "petición"
        elemento = {
            "ubicacion": ubicacion,
            "campo": _nombre_de_campo(loc[1:]),
            "motivo": MOTIVOS.get(str(error.get("type")), MOTIVO_POR_DEFECTO),
        }
        if elemento not in resultado:
            resultado.append(elemento)
    return resultado


async def _validacion(_: Request, exc: Exception) -> JSONResponse:
    errores = errores_de_validacion(exc.errors() if isinstance(exc, RequestValidationError) else [])
    campos = ", ".join(sorted({e["campo"] for e in errores if e["campo"]}))
    detalle = f"Parámetros no válidos: {campos}" if campos else "La petición no es válida"
    return respuesta_problema(400, "peticion-no-valida", detalle=detalle, errores=errores)


async def _http(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        return respuesta_problema(500, "error-interno")
    status = exc.status_code
    codigo = "no-encontrado" if status == 404 else f"http-{status}"
    return respuesta_problema(status, codigo, cabeceras=exc.headers)


async def _inesperado(request: Request, exc: Exception) -> JSONResponse:
    incidencia = uuid.uuid4().hex
    registro.error(
        "error no previsto",
        exc_info=exc,
        extra={"incidencia": incidencia, "metodo": request.method, "ruta": request.url.path},
    )
    return respuesta_problema(
        500,
        "error-interno",
        detalle="Se ha producido un error no previsto. Indica la incidencia si lo comunicas.",
        incidencia=incidencia,
    )


def registrar_manejadores(app: FastAPI) -> None:
    """Instala los manejadores de error de S5 en la aplicación."""
    app.add_exception_handler(RequestValidationError, _validacion)
    app.add_exception_handler(StarletteHTTPException, _http)
    app.add_exception_handler(Exception, _inesperado)
