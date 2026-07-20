"""Populate the database from a JSON file of NVRs and cameras.

Records go through the same validation and storage rules as API requests.
A record that fails (e.g. the malformed serial numbers in the shipped
sample data) is skipped with a warning rather than aborting the seed.
"""

import json
import logging
from pathlib import Path

from pydantic import ValidationError

from .exceptions import DomainError
from .models import Camera, Nvr
from .storage import Storage

logger = logging.getLogger(__name__)


def seed_from_file(storage: Storage, seed_path: Path | str) -> None:
    data = json.loads(Path(seed_path).read_text())
    records = [(Nvr, storage.add_nvr, r) for r in data.get("nvrs", [])]
    records += [(Camera, storage.add_camera, r) for r in data.get("cameras", [])]

    loaded = skipped = 0
    for model, add, record in records:
        serial = record.get("serial_number", "<no serial>")
        try:
            add(model(**record))
            loaded += 1
        except (ValidationError, DomainError) as err:
            skipped += 1
            logger.warning("Skipping %s %s: %s", model.__name__, serial, err)
    logger.info("Seeded %d records from %s (%d skipped)", loaded, seed_path, skipped)
