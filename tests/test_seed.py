"""First-run seeding: an empty database is populated from the sample file;
a database with existing data is never touched; records with invalid
serials are skipped with a warning.
"""

import logging
from pathlib import Path

from factories import nvr_payload
from fastapi.testclient import TestClient

from app.main import create_app

SAMPLE_FILE = Path(__file__).parent.parent / "sample_nvr_camera_data.json"

SAMPLE_NVR_SERIALS = {
    "a3f5e8d1-2c4b-4a9e-8f3d-1b5c7e9f2a4d",
    "b7d9f2a3-5e1c-4b8f-9d2e-3a6f8c1b4e7d",
    "c1e4b6f9-8a2d-4c5e-7b9f-2d4a6c8e1f3b",
}
SAMPLE_VALID_CAMERA_SERIALS = {
    "d5a8c2e1-3f7b-4d9e-8a1c-5b3f7e9d2a4c",
    "e2b9d4f6-7a3c-4e8f-9b2d-6a4c8e1f3b5d",
    "f3c7e9a2-4d6b-4f8e-9c1a-7b5d3e8f2a4c",
}
# Not valid UUIDs ("g" and "h" are not hex characters); must be skipped.
SAMPLE_INVALID_CAMERA_SERIALS = {
    "g4d8f1b3-5e9a-4c7d-8b2e-6a3c9e1f4b5d",
    "h5e9a2c4-6f1b-4d8e-9c3a-7b4d8e2f5a6c",
}


def seeded_client(db_path) -> TestClient:
    return TestClient(create_app(db_path, seed_path=SAMPLE_FILE))


def test_seeds_sample_nvrs_into_an_empty_database(tmp_path):
    with seeded_client(tmp_path / "service.db") as client:
        serials = {nvr["serial_number"] for nvr in client.get("/nvrs").json()}

    assert serials == SAMPLE_NVR_SERIALS


def test_seeds_only_cameras_with_valid_serials(tmp_path):
    with seeded_client(tmp_path / "service.db") as client:
        serials = {cam["serial_number"] for cam in client.get("/cameras").json()}

    assert serials == SAMPLE_VALID_CAMERA_SERIALS


def test_warns_about_each_skipped_record(tmp_path, caplog):
    with caplog.at_level(logging.WARNING):
        with seeded_client(tmp_path / "service.db"):
            pass

    for serial in SAMPLE_INVALID_CAMERA_SERIALS:
        assert serial in caplog.text


def test_does_not_seed_a_database_that_already_has_data(tmp_path):
    db_path = tmp_path / "service.db"
    nvr = nvr_payload()
    with TestClient(create_app(db_path)) as client:
        client.post("/nvrs", json=nvr)

    with seeded_client(db_path) as client:
        serials = {n["serial_number"] for n in client.get("/nvrs").json()}

    assert serials == {nvr["serial_number"]}


def test_seeding_twice_does_not_duplicate_records(tmp_path):
    db_path = tmp_path / "service.db"
    with seeded_client(db_path):
        pass

    with seeded_client(db_path) as client:
        assert len(client.get("/nvrs").json()) == len(SAMPLE_NVR_SERIALS)
        assert len(client.get("/cameras").json()) == len(SAMPLE_VALID_CAMERA_SERIALS)


def test_does_not_seed_without_a_seed_path(tmp_path):
    with TestClient(create_app(tmp_path / "service.db")) as client:
        assert client.get("/nvrs").json() == []
        assert client.get("/cameras").json() == []
