# NVR Camera Metadata Service

A small REST service for storing and retrieving metadata about Network Video
Recorders (NVRs) and the cameras connected to them.

**Stack:** Python / FastAPI / SQLite (stdlib `sqlite3`), managed with [uv](https://docs.astral.sh/uv/),
tested with pytest. SQLite keeps the service fully local — persistence is a
single database file, with no external database server to install or run.

## Getting started

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
uv sync          # install dependencies into .venv
uv run pytest    # run the test suite
```

<!-- TODO before submission: server run command, seed script usage, API reference -->

## Open questions & assumptions

The task description leaves a few behaviours unspecified. Rather than guess
silently, the decisions taken (and the reasoning) are recorded here — in a real
project these would be answered by gathering more information about the business requirements.

1. **Invalid UUIDs in the sample data.** The spec types serial numbers as
   UUIDs, but two cameras in `sample_nvr_camera_data.json` have serial numbers
   beginning `g4d8…` and `h5e9…` — `g` and `h` are not hexadecimal characters,
   so these are not valid UUIDs. **Decision:** serial numbers are strictly
   validated as UUIDs per the spec; the seed script loads the three valid
   cameras and reports the two it rejects.

2. **Deleting an NVR that still has cameras.** Cascade-delete the cameras,
   orphan them, or refuse? **Decision:** refuse with `409 Conflict` — the
   caller must delete (or re-home) the cameras first. Explicit beats
   destructive.

3. **Referential integrity on camera creation.** May a camera reference an
   NVR that hasn't been created? **Decision:** no — creating a camera with an
   unknown `nvr_uuid` returns `404`. NVRs must be created first; they are never
   created implicitly.

4. **Is `maximum_input_channels` a capacity limit?** The spec defines the
   field but never says to enforce it. **Assumption:** it is a capacity limit,
   and one camera consumes one input channel (real multi-sensor cameras can
   consume several). Creating a camera on a full NVR returns `409 Conflict`.

5. **No update workflow.** The spec asks for create, delete, and three read
   queries — no update. **Decision:** PUT/PATCH endpoints are intentionally
   omitted rather than forgotten; moving a camera between NVRs is
   delete-and-recreate. Easy to add if required.

6. **Location matching.** Camera location queries use exact, case-sensitive
   string matching (`Building A` ≠ `building a`). Fuzzy or case-insensitive
   matching would be a product decision for the customer.

7. **Filters that match nothing.** Querying cameras for an unknown NVR,
   location, or kind returns `200` with an empty array, not `404` — a filter
   with no matches is a valid question with an empty answer, not an error.
   *(Assumed, not specified.)*

8. **Listing endpoints.** Only the three camera queries are required, but a
   plain "list all NVRs / cameras" endpoint is included as a convenience —
   without it there is no way to discover what the service holds.

9. **Security & concurrency.** No authentication; the service assumes a
   single trusted client on a local machine, per the scope of the task.
