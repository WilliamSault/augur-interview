import uuid

from factories import camera_payload, nvr_payload


def test_returns_empty_list_when_no_cameras_exist(client):
    response = client.get("/cameras")

    assert response.status_code == 200
    assert response.json() == []


def test_lists_a_created_camera(client, existing_nvr):
    camera = camera_payload(nvr_uuid=existing_nvr["serial_number"])
    client.post("/cameras", json=camera)

    response = client.get("/cameras")

    assert response.status_code == 200
    assert response.json() == [camera]


def test_filters_by_nvr(client):
    nvr_a, nvr_b = nvr_payload(), nvr_payload()
    client.post("/nvrs", json=nvr_a)
    client.post("/nvrs", json=nvr_b)
    on_a = camera_payload(nvr_uuid=nvr_a["serial_number"])
    on_b = camera_payload(nvr_uuid=nvr_b["serial_number"])
    client.post("/cameras", json=on_a)
    client.post("/cameras", json=on_b)

    response = client.get("/cameras", params={"nvr_uuid": nvr_a["serial_number"]})

    assert response.json() == [on_a]


def test_filters_by_location(client, existing_nvr):
    serial = existing_nvr["serial_number"]
    in_a = camera_payload(nvr_uuid=serial, location="Building A")
    in_b = camera_payload(nvr_uuid=serial, location="Building B")
    client.post("/cameras", json=in_a)
    client.post("/cameras", json=in_b)

    response = client.get("/cameras", params={"location": "Building B"})

    assert response.json() == [in_b]


def test_location_match_is_exact_and_case_sensitive(client, existing_nvr):
    camera = camera_payload(
        nvr_uuid=existing_nvr["serial_number"], location="Building A"
    )
    client.post("/cameras", json=camera)

    response = client.get("/cameras", params={"location": "building a"})

    assert response.status_code == 200
    assert response.json() == []


def test_filters_by_kind(client, existing_nvr):
    serial = existing_nvr["serial_number"]
    thermal = camera_payload(nvr_uuid=serial, kind="thermal")
    electro_optical = camera_payload(nvr_uuid=serial, kind="electro-optical")
    client.post("/cameras", json=thermal)
    client.post("/cameras", json=electro_optical)

    response = client.get("/cameras", params={"kind": "thermal"})

    assert response.json() == [thermal]


def test_filters_combine(client, existing_nvr):
    serial = existing_nvr["serial_number"]
    match = camera_payload(nvr_uuid=serial, location="Building A", kind="thermal")
    wrong_kind = camera_payload(nvr_uuid=serial, location="Building A", kind="infrared")
    wrong_location = camera_payload(
        nvr_uuid=serial, location="Building B", kind="thermal"
    )
    for camera in (match, wrong_kind, wrong_location):
        client.post("/cameras", json=camera)

    response = client.get(
        "/cameras", params={"location": "Building A", "kind": "thermal"}
    )

    assert response.json() == [match]


def test_unknown_nvr_returns_empty_list(client):
    response = client.get("/cameras", params={"nvr_uuid": str(uuid.uuid4())})

    assert response.status_code == 200
    assert response.json() == []


def test_rejects_unknown_kind(client):
    response = client.get("/cameras", params={"kind": "ultraviolet"})

    assert response.status_code == 422


def test_rejects_unknown_kind_with_valid_location(client):
    response = client.get(
        "/cameras", params={"location": "Building A", "kind": "ultraviolet"}
    )
    assert response.status_code == 422


def test_rejects_nvr_uuid_that_is_not_a_uuid(client):
    response = client.get("/cameras", params={"nvr_uuid": "not-a-uuid"})

    assert response.status_code == 422
