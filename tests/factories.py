"""Builders for valid request payloads, with per-test overrides."""

import uuid


def nvr_payload(**overrides) -> dict:
    payload = {
        "make": "Hanwha Vision",
        "model": "QRN-1610S",
        "maximum_input_channels": 16,
        "serial_number": str(uuid.uuid4()),
    }
    payload.update(overrides)
    return payload


def camera_payload(nvr_uuid: str, **overrides) -> dict:
    payload = {
        "make": "Hikvision",
        "model": "DS-2CD2T83G2-4I",
        "kind": "electro-optical",
        "serial_number": str(uuid.uuid4()),
        "location": "Building A",
        "nvr_uuid": nvr_uuid,
    }
    payload.update(overrides)
    return payload
