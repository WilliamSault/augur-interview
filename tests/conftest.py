import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from factories import nvr_payload


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path / "test.db")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def existing_nvr(client) -> dict:
    """An NVR created via the API, for tests that attach cameras to it."""
    payload = nvr_payload()
    client.post("/nvrs", json=payload)
    return payload
