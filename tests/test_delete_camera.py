import uuid

from factories import camera_payload, nvr_payload


def test_deletes_existing_camera(client, existing_nvr):
    camera = camera_payload(nvr_uuid=existing_nvr["serial_number"])
    client.post("/cameras", json=camera)

    response = client.delete(f"/cameras/{camera['serial_number']}")

    assert response.status_code == 204


def test_rejects_unknown_serial_number(client):
    serial = uuid.uuid4()

    response = client.delete(f"/cameras/{serial}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Camera {serial} not found"


def test_deleted_camera_is_gone(client, existing_nvr):
    camera = camera_payload(nvr_uuid=existing_nvr["serial_number"])
    client.post("/cameras", json=camera)
    client.delete(f"/cameras/{camera['serial_number']}")

    response = client.delete(f"/cameras/{camera['serial_number']}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Camera {camera['serial_number']} not found"


def test_deleting_a_camera_frees_nvr_capacity(client):
    nvr = nvr_payload(maximum_input_channels=1)
    client.post("/nvrs", json=nvr)
    first = camera_payload(nvr_uuid=nvr["serial_number"])
    client.post("/cameras", json=first)

    second = camera_payload(nvr_uuid=nvr["serial_number"])
    blocked = client.post("/cameras", json=second)
    client.delete(f"/cameras/{first['serial_number']}")
    allowed = client.post("/cameras", json=second)

    assert blocked.status_code == 409
    assert allowed.status_code == 201


def test_rejects_serial_number_that_is_not_a_uuid(client):
    response = client.delete("/cameras/not-a-uuid")

    assert response.status_code == 422
