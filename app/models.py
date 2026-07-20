"""API models. Field names and types follow the task specification."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class CameraKind(StrEnum):
    ELECTRO_OPTICAL = "electro-optical"
    THERMAL = "thermal"
    INFRARED = "infrared"


class Nvr(BaseModel):
    make: str
    model: str
    maximum_input_channels: int = Field(gt=0)
    serial_number: UUID


class Camera(BaseModel):
    make: str
    model: str
    kind: CameraKind
    serial_number: UUID
    location: str
    nvr_uuid: UUID
