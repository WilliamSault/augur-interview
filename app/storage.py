"""SQLite persistence for NVR and camera metadata."""

import sqlite3
from pathlib import Path

from .exceptions import DuplicateSerial, NvrAtCapacity, NvrNotFound
from .models import Camera, Nvr

SCHEMA = """
CREATE TABLE IF NOT EXISTS nvrs (
    serial_number TEXT PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    maximum_input_channels INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS cameras (
    serial_number TEXT PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    kind TEXT NOT NULL,
    location TEXT NOT NULL,
    nvr_uuid TEXT NOT NULL REFERENCES nvrs(serial_number)
);

CREATE INDEX IF NOT EXISTS idx_cameras_nvr_uuid ON cameras(nvr_uuid);
CREATE INDEX IF NOT EXISTS idx_cameras_location ON cameras(location);
CREATE INDEX IF NOT EXISTS idx_cameras_kind ON cameras(kind);
"""


def init_db(db_path: Path | str) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def connect(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class Storage:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def add_nvr(self, nvr: Nvr) -> None:
        try:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO nvrs (serial_number, make, model, maximum_input_channels)"
                    " VALUES (?, ?, ?, ?)",
                    (str(nvr.serial_number), nvr.make, nvr.model, nvr.maximum_input_channels),
                )
        except sqlite3.IntegrityError:
            raise DuplicateSerial("NVR", nvr.serial_number)

    def add_camera(self, camera: Camera) -> None:
        # Single transaction so the capacity check and insert are atomic.
        try:
            with self._conn:
                row = self._conn.execute(
                    "SELECT maximum_input_channels,"
                    " (SELECT COUNT(*) FROM cameras WHERE nvr_uuid = nvrs.serial_number)"
                    " AS cameras_connected"
                    " FROM nvrs WHERE serial_number = ?",
                    (str(camera.nvr_uuid),),
                ).fetchone()
                if row is None:
                    raise NvrNotFound(camera.nvr_uuid)
                if row["cameras_connected"] >= row["maximum_input_channels"]:
                    raise NvrAtCapacity(camera.nvr_uuid)
                self._conn.execute(
                    "INSERT INTO cameras"
                    " (serial_number, make, model, kind, location, nvr_uuid)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        str(camera.serial_number),
                        camera.make,
                        camera.model,
                        camera.kind.value,
                        camera.location,
                        str(camera.nvr_uuid),
                    ),
                )
        except sqlite3.IntegrityError:
            raise DuplicateSerial("Camera", camera.serial_number)
