# Local backend guide

Status: implemented by Owen on 22 October 2026 for the mid-term. The map module
and the demo preview remain unchanged. A cloud AI provider adapter is **not**
implemented; the proxy returns an honest `503` until Qingyang adds one.

## What it does

The backend serves the existing `app/` and `data/` files and a small JSON API
from the same origin, so the browser can use `?mode=api` without CORS changes.
It stores one row per saved trip and its sanitised photographs in a local SQLite
database. It never substitutes demo data for a failed request.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python3 -m backend
```

Open **http://127.0.0.1:8019/app/?mode=api**. Stop with Ctrl+C.

`python3 serve.py` is still the zero-install demo-only preview. The two servers
are alternatives; do not run them on the same port at the same time.

## Files and runtime state

```text
backend/
  app.py             application factory
  config.py          settings, env loading, runtime paths
  db.py              schema, PRAGMAs, request connections
  models.py          Pydantic request/response contract
  errors.py          error envelope and handlers
  cities.py          validated catalogue loader
  security.py        CSP, headers, dotfile blocking, request log
  static.py          /app and /data mounts
  routers/           system, cities, trips, photos, memory
  storage/           SQL helpers, image pipeline, file safety
  ai/                adapter protocol, null adapter, provider selection
var/                 Git-ignored runtime state (created on first start)
  travel.db          SQLite database (WAL)
  media/             sanitised stored photographs
  tmp/               upload and AI-copy scratch space
```

`var/` is never mounted as a static directory. `data/` remains public and must
only contain fictional or permission-cleared material.

## Configuration

Defaults are safe for a local single user. Copy `.env.example` to `.env` only if
you need to change them; `.env` is Git-ignored.

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Bind address. Keep it local. |
| `PORT` | `8019` | Port for app and API. |
| `TMM_DB_PATH` | `var/travel.db` | SQLite file. |
| `TMM_MEDIA_DIR` | `var/media` | Stored photographs. |
| `TMM_TMP_DIR` | `var/tmp` | Upload/AI scratch space. |
| `TMM_MAX_PHOTOS` | `8` | Per-trip photo limit. |
| `TMM_MAX_UPLOAD_BYTES` | `10485760` | 10 MiB per upload. |
| `TMM_STORED_MAX_EDGE` | `2400` | Longest stored edge. |
| `AI_PROVIDER` | empty | Adapter module name; empty means no AI. |
| `AI_API_KEY` | empty | Server-side only; never returned or logged. |
| `AI_MODEL` | empty | Provider model identifier. |
| `AI_BASE_URL` | empty | Optional provider endpoint. |
| `AI_TIMEOUT_SECONDS` | `20` | Server budget for one draft. |

`HOST`/`PORT` can also be overridden with `--host` and `--port`.

## Data model

```sql
trips(id TEXT PRIMARY KEY, city_id, trip_date, title, notes, memory_text,
      source, created_at, updated_at)
photos(id TEXT PRIMARY KEY, trip_id REFERENCES trips(id) ON DELETE CASCADE,
       filename UNIQUE, alt, mime, width, height, bytes, position, created_at)
```

- `trips.id` is a server-generated UUID and the only visit identity. One row is
  one visit; repeat visits are separate rows.
- Only `POST /api/trips` inserts. `PATCH` cannot change `id` or `city_id`, so an
  edit or AI retry can never add a visit.
- `trip_date` is a real `YYYY-MM-DD` or `NULL`; invalid dates such as
  `2026-02-31` fail validation.
- Limits mirror `app/domain.mjs`: title 200 characters, notes and memory text
  5,000 each.
- The city catalogue remains `data/cities.json`; there is no second city table.

## Routes

| Method and path | Result |
| --- | --- |
| `GET /api/health` | Storage and AI status; no paths, keys or content. |
| `GET /api/cities` | The 19 supported cities. |
| `GET /api/trips` | All saved snapshots, newest date first, null dates last. |
| `GET /api/trips/{id}` | One snapshot or `404`. |
| `POST /api/trips` | `201` with a server ID; rejects `id`, `photos`, `memory_text`, `source`. |
| `PATCH /api/trips/{id}` | Edits `title`, `notes`, `memory_text`, `trip_date` only. |
| `DELETE /api/trips/{id}` | `204`; cascades photo rows and unlinks files. |
| `POST /api/trips/{id}/photos` | Multipart `file` + optional `alt`; `201` photo object. |
| `DELETE /api/trips/{id}/photos/{photo_id}` | `204`; removes row and file. |
| `GET /media/{filename}` | Same-origin sanitised image only. |
| `POST /api/trips/{id}/memory` | `{"confirmed": true}` → draft or clarification. |
| `GET /api/map-config` | Local-origin-only Maps settings. |

Every non-2xx API response uses:

```json
{"error": {"code": "trip_not_found", "message": "This trip does not exist.", "details": []}}
```

Stable codes include `validation_error`, `unknown_city`, `trip_not_found`,
`photo_not_found`, `photo_limit_reached`, `file_too_large`, `unsupported_media`,
`invalid_image`, `confirmation_required`, `ai_not_configured`, `ai_timeout`,
`ai_provider_error`, `ai_malformed_response`, `storage_error`.

## Photo pipeline

1. Stream one file to `var/tmp`, aborting as soon as the byte limit is exceeded.
2. Verify with Pillow: JPEG, PNG or WebP only; no animation; minimum 64 px edge;
   maximum 40 megapixels.
3. Apply EXIF orientation, shrink to 2,400 px, then write to a brand-new image
   so EXIF, XMP, GPS, comments and other ancillary data are discarded. A small
   ICC profile is retained for colour accuracy.
4. Insert the row in a transaction, then rename the finished file into
   `var/media/`. A failed rename removes the row; a failed upload removes every
   temporary file.
5. AI copies are separate 1,280 px JPEGs in a temporary directory and are
   deleted immediately after the adapter returns.

Accepted uploads are always re-encoded. The original bytes, exotic colour
profiles and metadata are deliberately not preserved.

## AI adapter contract

`backend/ai/base.py` defines the boundary. Qingyang implements one module named
by `AI_PROVIDER` (for example `AI_PROVIDER=example` → `backend/ai/example.py`)
with a `create_generator(settings)` factory. The object must provide `name`,
`is_configured()` and `async generate(request) -> MemoryResult`.

```python
@dataclass(frozen=True)
class MemoryRequest:
    city_name: str
    trip_date: str | None
    title: str
    notes: str
    photo_paths: tuple[Path, ...]   # sanitised 1,280 px JPEG copies

class MemoryResult(BaseModel):
    status: Literal["draft", "clarification"]
    title: str = ""
    text: str = ""
    question: str | None = None
    warning: str | None = None
    model: str | None = None
```

Rules the route enforces:

- The request must include `{"confirmed": true}`; otherwise `400`.
- Only the selected trip's city, date, title, notes and sanitised photos are
  passed. No other trip is loaded into the payload.
- The route is read-only and never writes `memory_text`; the user must save a
  draft through `PATCH /api/trips/{id}`.
- Missing configuration → `503`; provider failure or unusable output → `502`;
  timeout → `504`. The saved trip is untouched in every case.
- Logs record trip ID, provider, duration and status only — never notes, prompts,
  image bytes or keys.

`NullGenerator` is the default. `AI_PROVIDER` pointing at a missing module logs a
warning and keeps the honest `503` rather than pretending to generate.

## Privacy and safety

- Bind to `127.0.0.1`; there is no account system or multi-user isolation.
- API keys stay in the server environment; the browser never receives them.
- Uploaded files and the database live in Git-ignored `var/`.
- `/media/` accepts only generated UUID filenames and checks the database; path
  traversal, dotfiles and unknown names return `404`.
- Security headers match the preview server, including the existing CSP so
  optional Google Maps keeps working.
- Error messages never echo notes, titles or request bodies.

## Tests

```bash
npm test                                             # domain + API client
.venv/bin/python -m pytest                           # backend, 51 cases
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'   # legacy config
```

Coverage includes restart persistence, ordering, visit invariants, validation,
photo limits, EXIF/GPS stripping, media traversal, cascade deletion, AI
confirmation, current-trip-only payloads, timeout, provider failure, malformed
output and error-envelope leakage.

An optional browser check exercises the API-mode interface against a running
backend (create, upload, edit, AI failure, delete, mobile overflow):

```bash
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs \
CHROMIUM_EXECUTABLE="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
BASE_URL=http://127.0.0.1:8019 \
node tests/api-ui.e2e.mjs
```

It writes a screenshot and JSON result to `/tmp/travel-map-api-ui` unless
`EVIDENCE_DIR` overrides it.

## Backup and restore

Stop the backend, then copy the whole `var/` folder. To restore, put `var/`
back and start the backend again. `var/travel.db` and `var/media/` must be kept
together; copying only one leaves rows without files or files without rows.

## Fresh-setup checklist

1. Clone the repository and create a virtual environment.
2. `pip install -r requirements-dev.txt`.
3. `python3 -m backend`; confirm the printed URL and `GET /api/health`.
4. Open `?mode=api`, use **Add a memory**, upload a JPEG with **Add photo**,
   then edit the title/notes/memory text with **Edit memory**.
5. Stop and restart; confirm the trip, photo and edit are still present.
6. Delete the trip; confirm the media URL now returns `404`.
7. Run all three test commands above.

## Known limitations

- Single local user only; no authentication, concurrency testing or deployment.
- No server-side idempotency key: the interface guards double submission with a
  busy state, but a scripted duplicate create would produce two visits.
- No automatic cleanup of a database row whose file was deleted outside the app;
  the startup sweep only removes unreferenced files older than one hour.
- No AI provider yet; the route's real generation path is unverified until
  Qingyang's adapter lands.
- The focused API-mode workflow was checked in headless Chrome on 22 October
  2026 (create, upload, edit, AI `503`, delete and 390px overflow). The full
  existing Playwright suites, Safari/Firefox, physical devices and a fresh
  machine remain unverified.
