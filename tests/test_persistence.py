"""The spec requires data to persist through restarts.

A restart is simulated by building a second, completely fresh app instance
on the same database file: the new instance shares no memory with the first,
so anything it can read back must have come from disk.
"""

from factories import camera_payload, nvr_payload
from fastapi.testclient import TestClient

from app.main import create_app


def test_data_survives_restart(tmp_path):
    db_path = tmp_path / "service.db"
    nvr = nvr_payload()
    camera = camera_payload(nvr_uuid=nvr["serial_number"])

    with TestClient(create_app(db_path)) as original:
        original.post("/nvrs", json=nvr)
        original.post("/cameras", json=camera)

    with TestClient(create_app(db_path)) as restarted:
        assert restarted.get("/nvrs").json() == [nvr]
        assert restarted.get("/cameras").json() == [camera]
