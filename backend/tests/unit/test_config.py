import pytest
from pydantic import ValidationError

from app.infrastructure.config import Ajustes

URL = "postgresql+psycopg://traide:secreta@localhost:5432/traide"


@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch: pytest.MonkeyPatch) -> None:
    for variable in (
        "HOSTS_ADMITIDOS",
        "ORIGENES_ADMITIDOS",
        "PROVEEDOR_PRECIOS",
        "BENCHMARK_TICKER",
        "LLM_API_KEY",
    ):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("DATABASE_URL", URL)


def test_valores_por_defecto() -> None:
    ajustes = Ajustes()

    assert ajustes.hosts_admitidos == ["localhost", "127.0.0.1"]
    assert ajustes.origenes_admitidos == ["http://localhost:8080", "http://127.0.0.1:8080"]
    assert ajustes.proveedor_precios == "yfinance"
    assert ajustes.benchmark_ticker == "SPY"
    assert ajustes.llm_api_key.get_secret_value() == ""


def test_listas_separadas_por_comas(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOSTS_ADMITIDOS", " localhost , 127.0.0.1,")
    monkeypatch.setenv("ORIGENES_ADMITIDOS", "http://localhost:8080,http://localhost:5173")

    ajustes = Ajustes()

    assert ajustes.hosts_admitidos == ["localhost", "127.0.0.1"]
    assert ajustes.origenes_admitidos == ["http://localhost:8080", "http://localhost:5173"]


@pytest.mark.parametrize("valor", ["", " , "])
def test_hosts_admitidos_vacia_es_error(monkeypatch: pytest.MonkeyPatch, valor: str) -> None:
    monkeypatch.setenv("HOSTS_ADMITIDOS", valor)

    with pytest.raises(ValidationError, match="HOSTS_ADMITIDOS"):
        Ajustes()


def test_proveedor_de_precios_desconocido_es_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROVEEDOR_PRECIOS", "alphavantage")

    with pytest.raises(ValidationError):
        Ajustes()


def test_proveedor_de_ficheros(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROVEEDOR_PRECIOS", "ficheros")

    assert Ajustes().proveedor_precios == "ficheros"


def test_sin_database_url_es_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL")

    with pytest.raises(ValidationError):
        Ajustes()


def test_secretos_no_se_muestran_como_texto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "clave-muy-secreta")

    ajustes = Ajustes()

    assert "clave-muy-secreta" not in str(ajustes)
    assert "clave-muy-secreta" not in repr(ajustes)
    assert "secreta@" not in str(ajustes)
    assert ajustes.llm_api_key.get_secret_value() == "clave-muy-secreta"
