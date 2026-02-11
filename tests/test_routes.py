from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.api.routes import get_db
from app.database import Base


# Usa um SQLite em arquivo para compartilhar o mesmo banco
# entre a criação das tabelas e as sessões usadas nos testes.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


# Garante um banco limpo a cada rodada de testes
if os.path.exists("test.db"):
    os.remove("test.db")


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_shorten_url_creates_and_returns_short_url():
    payload = {"url": "https://example.com/shorten"}

    response = client.post("/shorten", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert data["short_url"].startswith("http://localhost:8000/")


def test_shorten_url_returns_same_short_url_for_same_original():
    payload = {"url": "https://example.com/idempotent"}

    first = client.post("/shorten", json=payload)
    second = client.post("/shorten", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["short_url"] == second.json()["short_url"]


def test_redirect_returns_307_and_location_header():
    payload = {"url": "https://example.com/redirect"}
    shorten_response = client.post("/shorten", json=payload)
    assert shorten_response.status_code == 200
    short_url = shorten_response.json()["short_url"]
    code = short_url.rsplit("/", 1)[-1]

    # Usa request com follow_redirects=False para inspecionar o redirecionamento
    response = client.request("GET", f"/{code}", follow_redirects=False)

    assert response.status_code in (301, 302, 303, 307, 308)
    assert response.headers.get("location") == payload["url"]


def test_redirect_invalid_code_returns_404():
    response = client.request("GET", "/invalid_code", follow_redirects=False)

    assert response.status_code == 404
    data = response.json()
    assert data.get("detail") == "URL not found"

