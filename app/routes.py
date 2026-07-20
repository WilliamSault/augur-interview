"""HTTP endpoints. Thin layer: validation via models, rules via Storage."""

from collections.abc import Iterator
from contextlib import closing
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from .models import Camera, Nvr
from .storage import Storage, connect

router = APIRouter()


def get_storage(request: Request) -> Iterator[Storage]:
    with closing(connect(request.app.state.db_path)) as conn:
        yield Storage(conn)


@router.post("/nvrs", status_code=201)
def create_nvr(nvr: Nvr, storage: Storage = Depends(get_storage)) -> Nvr:
    storage.add_nvr(nvr)
    return nvr


@router.post("/cameras", status_code=201)
def create_camera(camera: Camera, storage: Storage = Depends(get_storage)) -> Camera:
    storage.add_camera(camera)
    return camera


@router.delete("/nvrs/{serial_number}", status_code=204)
def delete_nvr(serial_number: UUID, storage: Storage = Depends(get_storage)) -> None:
    storage.delete_nvr(serial_number)


@router.delete("/cameras/{serial_number}", status_code=204)
def delete_camera(serial_number: UUID, storage: Storage = Depends(get_storage)) -> None:
    storage.delete_camera(serial_number)
