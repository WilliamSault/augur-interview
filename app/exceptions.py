"""Domain errors raised by the storage layer.

Each carries the HTTP status it maps to, so the API layer can translate
any DomainError with a single exception handler.
"""

from uuid import UUID


class DomainError(Exception):
    status_code: int

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NvrNotFound(DomainError):
    status_code = 404

    def __init__(self, serial_number: UUID):
        super().__init__(f"NVR {serial_number} not found")


class DuplicateSerial(DomainError):
    status_code = 409

    def __init__(self, entity: str, serial_number: UUID):
        super().__init__(f"{entity} with serial number {serial_number} already exists")


class NvrAtCapacity(DomainError):
    status_code = 409

    def __init__(self, serial_number: UUID):
        super().__init__(f"NVR {serial_number} has no free input channels")
