# Owen backend + Qingyang fixture integration review

This records the initial Owen/Qingyang integration. Angel's T03 fixture and
Thomas's Responses adapter were added afterward; see
[the current team sync](TEAM_SYNC_2026-10-26.md) for the combined status.

This review branch starts from `main` at `835c124` and merges Owen's
`feat/backend-api-ui` at `7afde24`. It does not merge the separate PR #3 or the
uncommitted `feat/local-photo-trips` checkout.

## Working path

Start `python3 -m backend` after installing `requirements-dev.txt`, then open
`/app/?mode=api&map=local`. A user can save a city trip, add a photo, edit its
title/notes/memory, save another visit to the same city, reload the album and
delete either trip. SQLite and sanitised images are stored under Git-ignored
`var/`. The demo mode remains available via `python3 serve.py`.

The AI route requires explicit confirmation and protects the saved trip on
error. No live provider adapter is part of this branch: a confirmed AI request
returns `503` rather than a generated draft.

## Evaluation materials

Qingyang's T04 and T05 graphics are preserved. Their filenames and city IDs
now match `case.json`; SHA-256 values describe the committed PNG bytes. T01,
T04 and T05 are still **prepared, not run**. T02 and T03 have not been added to
`data/fixtures/`. No raw cloud output or independent human score is claimed.

## Verification on 26 October 2026

- `python -m pytest -q`: 55 passed, including fixture path/city/hash checks.
- `npm test`: 21 passed.
- Live local backend smoke check on an isolated temporary database: health,
  create, photo upload, edit, repeat visit, honest AI `503`, and delete passed.
- These checks do not establish real cloud AI quality, fresh-machine setup,
  accessibility on physical devices, or concurrent multi-tab behaviour.

## Review decisions before the next step

1. Review this backend/data integration and keep one canonical storage system.
2. Port the existing Bailian request logic from PR #3 into Owen's
   `MemoryGenerator` contract, without merging PR #3's second server/database.
3. Decide whether the current trip's date and title may be sent to the cloud;
   update the confirmation notice to match the actual request.
4. Add T02/T03, run all five frozen cases on the integrated build, and record
   raw outputs plus two independent reviews before reporting an AI pass count.
