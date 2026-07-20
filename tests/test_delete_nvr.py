import uuid

from factories import camera_payload


def test_deletes_nvr_without_cameras(client, existing_nvr):
    response = client.delete(f"/nvrs/{existing_nvr['serial_number']}")

    assert response.status_code == 204


def test_rejects_unknown_serial_number(client):
    serial = uuid.uuid4()

    response = client.delete(f"/nvrs/{serial}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"NVR {serial} not found"


def test_deleted_nvr_is_gone(client, existing_nvr):
    serial = existing_nvr["serial_number"]
    client.delete(f"/nvrs/{serial}")

    response = client.delete(f"/nvrs/{serial}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"NVR {serial} not found"


def test_rejects_nvr_that_still_has_cameras(client, existing_nvr):
    serial = existing_nvr["serial_number"]
    client.post("/cameras", json=camera_payload(nvr_uuid=serial))

    response = client.delete(f"/nvrs/{serial}")

    assert response.status_code == 409
    assert response.json()["detail"] == f"NVR {serial} still has cameras attached"


def test_deletes_nvr_once_its_cameras_are_deleted(client, existing_nvr):
    nvr_serial = existing_nvr["serial_number"]
    camera = camera_payload(nvr_uuid=nvr_serial)
    client.post("/cameras", json=camera)

    client.delete(f"/cameras/{camera['serial_number']}")
    response = client.delete(f"/nvrs/{nvr_serial}")

    assert response.status_code == 204


def test_rejects_serial_number_that_is_not_a_uuid(client):
    response = client.delete("/nvrs/not-a-uuid")

    assert response.status_code == 422
