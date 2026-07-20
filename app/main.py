"""Application factory for the NVR/camera metadata service."""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .exceptions import DomainError
from .routes import router
from .storage import init_db


def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def create_app(db_path: Path | str) -> FastAPI:
    """Build the FastAPI app backed by the SQLite database at db_path."""
    init_db(db_path)
    app = FastAPI(title="NVR Camera Metadata Service")
    app.state.db_path = db_path
    app.include_router(router)
    app.add_exception_handler(DomainError, domain_error_handler)
    return app


def app() -> FastAPI:
    """Entrypoint for `uvicorn --factory app.main:app`."""
    return create_app(os.environ.get("NVR_DB_PATH", "nvr_metadata.db"))
