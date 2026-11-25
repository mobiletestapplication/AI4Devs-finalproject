import pytest
from fastapi.testclient import TestClient

from app.infrastructure.config import Ajustes
from app.main import crear_app


@pytest.fixture
def cliente() -> TestClient:
    ajustes = Ajustes(database_url="postgresql+psycopg://traide@localhost:5432/traide_tests")
    # Host admitido (seguridad-api): TestClient envía "testserver" por defecto.
    return TestClient(crear_app(ajustes), base_url="http://localhost")


def test_openapi_bajo_prefijo_api(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/openapi.json")

    assert respuesta.status_code == 200
    assert respuesta.json()["info"]["title"] == "trAIde API"


def test_documentacion_bajo_prefijo_api(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/docs")

    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]


def test_rutas_de_documentacion_fuera_de_api_no_existen(cliente: TestClient) -> None:
    assert cliente.get("/docs").status_code == 404
    assert cliente.get("/openapi.json").status_code == 404
    assert cliente.get("/redoc").status_code == 404


def test_crear_app_sin_ajustes_usa_los_del_entorno() -> None:
    app = crear_app()

    assert isinstance(app.state.ajustes, Ajustes)
