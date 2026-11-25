"""Seguridad de la API: errores, cabeceras, Host, origen y límite de frecuencia.

Tareas 3.1-3.6 de sec-01-seguridad-api. Los escenarios que no necesitan rutas de negocio
se citan con la marca ``escenario``; el resto de casos usa rutas de prueba registradas
solo aquí (``/prueba/...``).
"""

import logging
from typing import Any

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from limits import parse
from pydantic import BaseModel, ConfigDict, SecretStr

from app.api.errores import CSP_JSON, MEDIA_PROBLEMA
from app.api.seguridad import LIMITES
from app.infrastructure.config import Ajustes
from app.main import crear_app

AJUSTES = Ajustes(database_url=SecretStr("postgresql+psycopg://traide@localhost:5432/traide_tests"))
LIMITE_DE_PRUEBA = {("POST", "/prueba/limitada"): parse("5/minute")}
CABECERAS_ESPERADAS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "x-frame-options": "DENY",
    "cache-control": "no-store",
}
ORIGEN_AJENO = {"Origin": "https://atacante.example"}


class CuerpoEstricto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    periodo: int = 14


def _app_de_prueba() -> FastAPI:
    app = crear_app(AJUSTES, limites=LIMITE_DE_PRUEBA)
    app.state.llamadas = 0

    @app.get("/prueba/entero")
    def entero(periodo: int) -> dict[str, int]:
        return {"periodo": periodo}

    @app.post("/prueba/cuerpo")
    def cuerpo(datos: CuerpoEstricto) -> dict[str, int]:
        return {"periodo": datos.periodo}

    @app.get("/prueba/fallo")
    def fallo() -> None:
        raise RuntimeError("detalle interno /app/app/secreto.py SELECT * FROM posicion")

    @app.post("/prueba/limitada")
    async def limitada(request: Request) -> dict[str, int]:
        app.state.llamadas += 1
        return {"bytes": len(await request.body())}

    @app.api_route("/prueba/libre", methods=["GET", "POST"], include_in_schema=False)
    def libre() -> dict[str, bool]:
        app.state.llamadas += 1
        return {"ok": True}

    return app


@pytest.fixture
def app() -> FastAPI:
    return _app_de_prueba()


@pytest.fixture
def cliente(app: FastAPI) -> TestClient:
    return TestClient(app, base_url="http://localhost:8080", raise_server_exceptions=False)


def _es_problema(respuesta: Any, status: int) -> dict[str, Any]:
    assert respuesta.status_code == status
    assert respuesta.headers["content-type"].startswith(MEDIA_PROBLEMA)
    cuerpo: dict[str, Any] = respuesta.json()
    assert cuerpo["status"] == status
    assert cuerpo["type"].startswith("urn:traide:error:")
    assert cuerpo["title"]
    return cuerpo


# --- Formato común de los errores (tarea 3.1) ----------------------------------------


@pytest.mark.escenario("seguridad-api::Formato común de los errores::Ruta inexistente")
def test_ruta_inexistente(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/no-existe")

    _es_problema(respuesta, 404)
    assert "Traceback" not in respuesta.text


def test_parametro_no_valido_sin_eco_del_valor(cliente: TestClient) -> None:
    valor = "<script>alert(1)</script>"

    respuesta = cliente.get("/prueba/entero", params={"periodo": valor})

    cuerpo = _es_problema(respuesta, 400)
    assert cuerpo["errores"] == [
        {"ubicacion": "consulta", "campo": "periodo", "motivo": "debe ser un número entero"}
    ]
    assert "periodo" in cuerpo["detail"]
    assert "script" not in respuesta.text


def test_campo_no_admitido_en_el_cuerpo(cliente: TestClient) -> None:
    respuesta = cliente.post("/prueba/cuerpo", json={"periodo": 14, "comision": 1})

    cuerpo = _es_problema(respuesta, 400)
    assert cuerpo["errores"] == [
        {"ubicacion": "cuerpo", "campo": "comision", "motivo": "campo no admitido"}
    ]


def test_nombre_de_campo_con_marcado_no_se_repite(cliente: TestClient) -> None:
    respuesta = cliente.post("/prueba/cuerpo", json={"<img src=x>": 1})

    cuerpo = _es_problema(respuesta, 400)
    assert cuerpo["errores"][0]["campo"] == "(no reconocido)"
    assert "img" not in respuesta.text


def test_error_inesperado_con_incidencia_y_sin_detalles(
    cliente: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.ERROR, logger="app.api.errores"):
        respuesta = cliente.get("/prueba/fallo")

    cuerpo = _es_problema(respuesta, 500)
    incidencia = cuerpo["incidencia"]
    assert len(incidencia) == 32
    assert int(incidencia, 16) >= 0
    for fuga in ("Traceback", "secreto.py", "SELECT", "/app/"):
        assert fuga not in respuesta.text
    for cabecera, valor in CABECERAS_ESPERADAS.items():
        assert respuesta.headers[cabecera] == valor
    (registro,) = caplog.records
    assert registro.incidencia == incidencia  # type: ignore[attr-defined]
    assert registro.exc_info is not None


# --- Cabeceras de seguridad (tarea 3.2) ----------------------------------------------


@pytest.mark.escenario("seguridad-api::Cabeceras de seguridad de la API::Respuesta JSON de la API")
def test_cabeceras_en_respuesta_json(app: FastAPI) -> None:
    directo = TestClient(app, base_url="http://127.0.0.1:8000")

    respuesta = directo.get("/api/openapi.json")

    assert respuesta.status_code == 200
    for cabecera, valor in CABECERAS_ESPERADAS.items():
        assert respuesta.headers[cabecera] == valor
    assert respuesta.headers["content-security-policy"] == CSP_JSON


@pytest.mark.escenario("seguridad-api::Cabeceras de seguridad de la API::Respuesta de error")
def test_cabeceras_en_respuesta_de_error(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/no-existe")

    assert respuesta.status_code == 404
    for cabecera, valor in CABECERAS_ESPERADAS.items():
        assert respuesta.headers[cabecera] == valor
    assert respuesta.headers["content-security-policy"] == CSP_JSON


def test_documentacion_sin_csp_pero_con_el_resto(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/docs")

    assert respuesta.status_code == 200
    assert respuesta.headers["x-content-type-options"] == "nosniff"
    assert "content-security-policy" not in respuesta.headers


# --- Host admitido (tarea 3.3) -------------------------------------------------------


@pytest.mark.escenario("seguridad-api::Host admitido::DNS rebinding")
def test_dns_rebinding(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/cartera/posiciones", headers={"Host": "atacante.example:8080"})

    cuerpo = _es_problema(respuesta, 400)
    assert set(cuerpo) <= {"type", "title", "status", "detail"}


@pytest.mark.escenario(
    "seguridad-api::Formato común de los errores::Host rechazado con el formato común"
)
def test_host_rechazado_con_el_formato_comun(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/openapi.json", headers={"Host": "atacante.example"})

    _es_problema(respuesta, 400)
    assert "atacante.example" not in respuesta.text


@pytest.mark.parametrize("host", ["localhost:8080", "LOCALHOST", "127.0.0.1:8000", "localhost"])
def test_hosts_admitidos(cliente: TestClient, host: str) -> None:
    assert cliente.get("/api/openapi.json", headers={"Host": host}).status_code == 200


@pytest.mark.parametrize("host", ["", "localhost.atacante.example", "127.0.0.2", "[::1]:8000"])
def test_hosts_no_admitidos(cliente: TestClient, host: str) -> None:
    assert cliente.get("/api/openapi.json", headers={"Host": host}).status_code == 400


# --- Origen de las peticiones que modifican estado (tarea 3.4) -----------------------


@pytest.mark.escenario(
    "seguridad-api::Origen de las peticiones que envían datos::Importación desde otra web"
)
def test_importacion_desde_otra_web(app: FastAPI, cliente: TestClient) -> None:
    respuesta = cliente.post(
        "/api/cartera/importacion", headers=ORIGEN_AJENO, files={"fichero": b"PK\x03\x04"}
    )
    a_ruta_existente = cliente.post("/prueba/libre", headers=ORIGEN_AJENO)

    _es_problema(respuesta, 403)
    assert a_ruta_existente.status_code == 403
    assert app.state.llamadas == 0, "el rechazo llega antes de ejecutar ninguna ruta"


@pytest.mark.parametrize(
    ("cabeceras", "esperado"),
    [
        ({"Origin": "http://localhost:8080"}, 200),
        ({"Origin": "http://127.0.0.1:8080/"}, 200),
        ({"Sec-Fetch-Site": "same-site"}, 403),
        ({"Sec-Fetch-Site": "cross-site"}, 403),
        ({"Sec-Fetch-Site": "same-origin"}, 200),
        ({}, 200),
        ({"Origin": "null"}, 403),
    ],
)
def test_reglas_de_origen(cliente: TestClient, cabeceras: dict[str, str], esperado: int) -> None:
    assert cliente.post("/prueba/libre", headers=cabeceras).status_code == esperado


def test_get_con_origen_ajeno_se_acepta(cliente: TestClient) -> None:
    assert cliente.get("/prueba/libre", headers=ORIGEN_AJENO).status_code == 200


# --- Límite de frecuencia (tarea 3.5) ------------------------------------------------


def test_sexta_peticion_limitada_sin_ejecutar_la_ruta(app: FastAPI, cliente: TestClient) -> None:
    respuestas = [cliente.post("/prueba/limitada", content=b"x" * 1024) for _ in range(6)]

    assert [r.status_code for r in respuestas] == [200] * 5 + [429]
    cuerpo = _es_problema(respuestas[-1], 429)
    retry_after = int(respuestas[-1].headers["retry-after"])
    assert 0 < retry_after <= 60
    assert cuerpo["reintentar_en"] == retry_after
    assert app.state.llamadas == 5, "la sexta no llega a la ruta ni lee el cuerpo"


def test_ruta_sin_limite_admite_cien_peticiones(cliente: TestClient) -> None:
    codigos = {cliente.post("/prueba/libre").status_code for _ in range(100)}

    assert codigos == {200}


def test_tabla_real_de_limites() -> None:
    assert {clave: str(limite) for clave, limite in LIMITES.items()} == {
        ("POST", "/api/cartera/importacion"): "5 per 1 minute",
        ("POST", "/api/backtests"): "10 per 1 minute",
    }


# --- Orden de la cadena (tarea 3.6) --------------------------------------------------


def test_host_se_comprueba_antes_que_el_origen(cliente: TestClient) -> None:
    respuesta = cliente.post("/prueba/libre", headers={"Host": "atacante.example", **ORIGEN_AJENO})

    assert respuesta.status_code == 400
