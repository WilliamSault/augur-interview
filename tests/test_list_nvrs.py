from factories import nvr_payload


def test_returns_empty_list_when_no_nvrs_exist(client):
    response = client.get("/nvrs")

    assert response.status_code == 200
    assert response.json() == []


def test_lists_created_nvrs(client):
    first, second = nvr_payload(), nvr_payload()
    client.post("/nvrs", json=first)
    client.post("/nvrs", json=second)

    response = client.get("/nvrs")

    assert response.status_code == 200
    by_serial = sorted(response.json(), key=lambda nvr: nvr["serial_number"])
    assert by_serial == sorted([first, second], key=lambda nvr: nvr["serial_number"])
