# NVR Camera Metadata Service

A small REST service for storing and retrieving metadata about Network Video
Recorders (NVRs) and the cameras connected to them.

**Stack:** Python / FastAPI / SQLite (stdlib `sqlite3`), managed with [uv](https://docs.astral.sh/uv/),
tested with pytest. SQLite keeps the service fully local: persistence is a
single database file, with no external database server to install or run.

## Getting started

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
uv sync          # install dependencies into .venv
uv run pytest    # run the test suite
```

## Running the service

```sh
uv run uvicorn --factory app.main:app
```

The API is then available at `http://localhost:8000`, with interactive
documentation at [http://localhost:8000/docs](http://localhost:8000/docs),
the easiest way to explore the endpoints from a browser.

Data is stored in `nvr_metadata.db` in the working directory; set
`NVR_DB_PATH` to use a different file. The database file is created on first
run and survives restarts.

### Sample data

On first run (an empty database), the service seeds itself from
`sample_nvr_camera_data.json`, so there is data to explore immediately.
A database that already contains data is never seeded. Set `NVR_SEED_PATH`
to seed from a different file, or to an empty string to disable seeding.

Two of the five sample cameras are skipped with a logged warning; their
serial numbers are not valid UUIDs (see assumption 1 below).

Example requests:

```sh
# create an NVR
curl -X POST localhost:8000/nvrs \
  -H 'Content-Type: application/json' \
  -d '{"make": "Hanwha Vision", "model": "QRN-1610S", "maximum_input_channels": 16, "serial_number": "a3f5e8d1-2c4b-4a9e-8f3d-1b5c7e9f2a4d"}'

# attach a camera to it
curl -X POST localhost:8000/cameras \
  -H 'Content-Type: application/json' \
  -d '{"make": "FLIR", "model": "A700-EST", "kind": "thermal", "serial_number": "f3c7e9a2-4d6b-4f8e-9c1a-7b5d3e8f2a4c", "location": "Building B", "nvr_uuid": "a3f5e8d1-2c4b-4a9e-8f3d-1b5c7e9f2a4d"}'
```

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/nvrs` | Create an NVR. `409` on duplicate serial. |
| `GET` | `/nvrs` | List all NVRs. |
| `DELETE` | `/nvrs/{serial_number}` | Delete an NVR. `409` while cameras are attached. |
| `POST` | `/cameras` | Create a camera. `404` unknown NVR, `409` duplicate serial or NVR at capacity. |
| `GET` | `/cameras` | List cameras. Optional filters `nvr_uuid`, `location`, `kind` (combine with AND). |
| `DELETE` | `/cameras/{serial_number}` | Delete a camera. |

The three read workflows from the task map onto `GET /cameras` filters:
`?nvr_uuid=<uuid>` (cameras on an NVR), `?location=Building%20A` (cameras in
a location), `?kind=thermal` (cameras of a kind).

Full request/response schemas are on the interactive docs page at `/docs`.


## Open questions & assumptions

The task description leaves a few behaviours unspecified. Rather than guess
silently, the decisions taken (and the reasoning) are recorded here; in a real
project these would be answered by gathering more information about the business requirements.

1. **Invalid UUIDs in the sample data.** The spec types serial numbers as
   UUIDs, but two cameras in `sample_nvr_camera_data.json` have serial numbers
   beginning `g4d8…` and `h5e9…`; `g` and `h` are not hexadecimal characters,
   so these are not valid UUIDs. **Decision:** serial numbers are strictly
   validated as UUIDs per the spec; the first-run seeder loads the three
   valid cameras and logs a warning for the two it rejects.

2. **Deleting an NVR that still has cameras.** Cascade-delete the cameras,
   orphan them, or refuse? **Decision:** refuse with `409 Conflict` the
   caller must delete (or re-home) the cameras first. Explicit beats
   destructive.

3. **Referential integrity on camera creation.** May a camera reference an
   NVR that hasn't been created? **Decision:** no, creating a camera with an
   unknown `nvr_uuid` returns `404`. NVRs must be created first; they are never
   created implicitly.

4. **Is `maximum_input_channels` a capacity limit?** The spec defines the
   field but never says to enforce it. **Assumption:** it is a capacity limit,
   and one camera consumes one input channel (real multi-sensor cameras can
   consume several). Creating a camera on a full NVR returns `409 Conflict`.

5. **No update workflow.** The spec asks for create, delete, and three read
   queries and no update. **Decision:** PUT/PATCH endpoints are intentionally
   omitted rather than forgotten; moving a camera between NVRs is
   delete-and-recreate. Easy to add if required.

6. **Location matching.** Camera location queries use exact, case-sensitive
   string matching (`Building A` ≠ `building a`). Fuzzy or case-insensitive
   matching would be a product decision for the customer.

7. **Filters that match nothing.** Querying cameras for an unknown NVR,
   location, or kind returns `200` with an empty array, not `404` so a filter
   with no matches is a valid question with an empty answer, not an error.
   *(Assumed, not specified.)*

8. **Listing endpoints.** Only the three camera queries are required, but a
   plain "list all NVRs / cameras" endpoint is included as a convenience as
   without it there is no way to discover what the service holds.

9. **Security & concurrency.** No authentication; the service assumes a
   single trusted client on a local machine, per the scope of the task.

10. **Serial numbers are client-supplied identifiers.** The spec never says
    who generates serials. **Assumption:** they come from the physical
    hardware, so the client supplies them and they act as primary keys,
    creating a second record with an existing serial returns `409 Conflict`
    rather than silently overwriting.

11. **First-run seeding.** The spec ships sample data but never says to load
    it. **Decision:** an empty database seeds itself from the sample file so
    the service is explorable immediately, and invalid records are skipped
    with a warning rather than aborting the whole seed. See "Sample data" above.
