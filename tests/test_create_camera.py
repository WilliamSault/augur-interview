import uuid

import pytest

from factories import camera_payload, nvr_payload

# Taken verbatim from sample_nvr_camera_data.json: "h" is not a hex
# character, so despite its shape this is not a valid UUID.
NOT_A_UUID = "h5e9a2c4-6f1b-4d8e-9c3a-7b4d8e2f5a6c"


def test_creates_camera_with_valid_payload(client, existing_nvr):
    payload = camera_payload(nvr_uuid=existing_nvr["serial_number"])

    response = client.post("/cameras", json=payload)

    assert response.status_code == 201
    assert response.json() == payload


@pytest.mark.parametrize("kind", ["electro-optical", "thermal", "infrared"])
def test_accepts_each_camera_kind(client, existing_nvr, kind):
    payload = camera_payload(nvr_uuid=existing_nvr["serial_number"], kind=kind)

    response = client.post("/cameras", json=payload)

    assert response.status_code == 201


def test_rejects_unknown_kind(client, existing_nvr):
    payload = camera_payload(nvr_uuid=existing_nvr["serial_number"], kind="ultraviolet")

    response = client.post("/cameras", json=payload)

    assert response.status_code == 422


def test_rejects_camera_when_nvr_does_not_exist(client):
    payload = camera_payload(nvr_uuid=str(uuid.uuid4()))

    response = client.post("/cameras", json=payload)

    assert response.status_code == 404
    # Distinguish a deliberate "NVR not found" from a missing route's 404.
    assert "NVR" in response.json()["detail"]


def test_rejects_duplicate_serial_number(client, existing_nvr):
    payload = camera_payload(nvr_uuid=existing_nvr["serial_number"])
    client.post("/cameras", json=payload)

    duplicate = camera_payload(
        nvr_uuid=existing_nvr["serial_number"],
        serial_number=payload["serial_number"],
    )
    response = client.post("/cameras", json=duplicate)

    assert response.status_code == 409


def test_rejects_serial_number_that_is_not_a_uuid(client, existing_nvr):
    payload = camera_payload(
        nvr_uuid=existing_nvr["serial_number"], serial_number=NOT_A_UUID
    )

    response = client.post("/cameras", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field", ["make", "model", "kind", "serial_number", "location", "nvr_uuid"]
)
def test_rejects_missing_required_field(client, existing_nvr, field):
    payload = camera_payload(nvr_uuid=existing_nvr["serial_number"])
    del payload[field]

    response = client.post("/cameras", json=payload)

    assert response.status_code == 422


def test_rejects_camera_when_nvr_is_at_capacity(client):
    nvr = nvr_payload(maximum_input_channels=1)
    client.post("/nvrs", json=nvr)

    first = client.post("/cameras", json=camera_payload(nvr_uuid=nvr["serial_number"]))
    second = client.post("/cameras", json=camera_payload(nvr_uuid=nvr["serial_number"]))

    assert first.status_code == 201
    assert second.status_code == 409
