"""Application factory for the NVR/camera metadata service."""

from pathlib import Path

from fastapi import FastAPI


def create_app(db_path: Path | str) -> FastAPI:
    """Build the FastAPI app backed by the SQLite database at db_path."""
    app = FastAPI(title="NVR Camera Metadata Service")
    return app
