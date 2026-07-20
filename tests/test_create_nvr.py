import pytest
from factories import nvr_payload


def test_creates_nvr_with_valid_payload(client):
    payload = nvr_payload()

    response = client.post("/nvrs", json=payload)

    assert response.status_code == 201
    assert response.json() == payload


def test_rejects_duplicate_serial_number(client):
    payload = nvr_payload()
    client.post("/nvrs", json=payload)

    response = client.post(
        "/nvrs", json=nvr_payload(serial_number=payload["serial_number"])
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "field", ["make", "model", "maximum_input_channels", "serial_number"]
)
def test_rejects_missing_required_field(client, field):
    payload = nvr_payload()
    del payload[field]

    response = client.post("/nvrs", json=payload)

    assert response.status_code == 422


# Taken verbatim from sample_nvr_camera_data.json: "g" is not a hex
# character, so despite its shape this is not a valid UUID.
NOT_A_UUID = "g4d8f1b3-5e9a-4c7d-8b2e-6a3c9e1f4b5d"


def test_rejects_serial_number_that_is_not_a_uuid(client):
    response = client.post("/nvrs", json=nvr_payload(serial_number=NOT_A_UUID))

    assert response.status_code == 422


@pytest.mark.parametrize("channels", [0, -4, "sixteen"])
def test_rejects_invalid_maximum_input_channels(client, channels):
    response = client.post("/nvrs", json=nvr_payload(maximum_input_channels=channels))

    assert response.status_code == 422
