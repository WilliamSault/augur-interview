"""Application factory for the NVR/camera metadata service."""

import os
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .exceptions import DomainError
from .routes import router
from .seed import seed_from_file
from .storage import Storage, connect, init_db


def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def create_app(db_path: Path | str, seed_path: Path | str | None = None) -> FastAPI:
    """Build the FastAPI app backed by the SQLite database at db_path.

    When seed_path is given and the database is empty, it is populated
    from that file first. A database with existing data is never seeded.
    """
    init_db(db_path)
    if seed_path is not None:
        with closing(connect(db_path)) as conn:
            storage = Storage(conn)
            if not storage.list_nvrs() and not storage.list_cameras():
                seed_from_file(storage, seed_path)
    app = FastAPI(title="NVR Camera Metadata Service")
    app.state.db_path = db_path
    app.include_router(router)
    app.add_exception_handler(DomainError, domain_error_handler)
    return app


def app() -> FastAPI:
    """Entrypoint for `uvicorn --factory app.main:app`."""
    seed_path = os.environ.get("NVR_SEED_PATH", "sample_nvr_camera_data.json")
    return create_app(
        os.environ.get("NVR_DB_PATH", "nvr_metadata.db"),
        seed_path=seed_path or None,
    )
