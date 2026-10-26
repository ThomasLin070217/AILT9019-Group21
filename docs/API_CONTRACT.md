# Local album API contract

Version 1.0 — 20 October 2026. Implemented in `serve.py`, `album_store.py`, `album_backup.py` and `ai_memory.py`. Host/origin must match loopback server. JSON failures use `{error:message}`. No key is returned to the browser. Assets are limited to app/data; private album files have dedicated authenticated-by-local-origin media routes.

## Routes

| Route | Request / response |
| --- | --- |
| `GET /api/cities` | Array from `data/cities.json`, 19 stable IDs |
| `GET /api/trips` | All active saved snapshots, no demo fallback |
| `POST /api/trips` | JSON `{request_id,city_id,trip_date,title,notes,photos:[{data:base64}]}` → 201 saved snapshot |
| `PATCH /api/trips/{id}` | JSON `{expected_revision,title?,trip_date?,notes?,memory_text?}` → updated snapshot; at least one edited field |
| `DELETE /api/trips/{id}` | JSON `{expected_revision}` → `{id,deleted:true,cleanup_pending}` |
| `POST /api/trips/{id}/photos` | JSON `{expected_revision,request_id,photos:[{data:base64}]}` → same trip with replacement photos |
| `GET /media/{trip_id}/{photo_id}.jpg` | Active referenced local JPEG only; removed references return 404 |
| `GET /api/backup` | Download ZIP: album.json plus referenced JPEGs and SHA-256 hashes |
| `POST /api/backups/preview` | `application/zip` → `{total,new,unchanged,conflicts,conflict_titles}` |
| `POST /api/backups/restore` | `application/zip` → merge new records; conflicts return 409 |
| `POST /api/backups/restore?copies=1` | Explicitly import conflicting records as new IDs, skip identical records |
| `GET /api/ai-config` | `{configured,provider,endpoint,model,prompt_version,privacy_url}`; no key |
| `POST /api/trips/{id}/generate` | JSON `{expected_revision,consent:true}` → unsaved AI result |

Trip snapshot fields: `id`, `city_id`, nullable ISO `trip_date`, `title`, `notes`, `memory_text`, `photos:[{id,url,alt}]`, `source:'user'`, integer `revision`. Photo-update idempotency metadata may also be present. Each distinct active trip ID is one visit. Editing, generating and replacing photos retain that identity. Empty titles default to `A visit to <city>`.

Photo limits: 1–5 still JPEG/PNG/WebP, 5 MB each/20 MB total/25 MP, 28 MB JSON upload. Saved copies are oriented JPEGs at most 4096 px; EXIF/GPS stripped. Text limits: title 200; notes/memory 5,000. PATCH/DELETE bodies max64 KB. Generation body max16 KB; provider timeout60s. Backups max100 MB ZIP/200 MB expanded/500 trips; reject unexpected paths, duplicates, invalid files and hash mismatches.

New trip revision starts at1; legacy missing revision is0. Changed edits increment revision atomically. Stale edits return409 and preserve drafts. Immediate identical create/edit/photo retries are idempotent. Delete keeps minimal request/identity tombstones to prevent create replay resurrecting removed trips; content is cleared. Physical cleanup follows commit; reads retry cleanup and media access is denied regardless. Restore never overwrites existing records and rolls back newly added files on failure.

AI result: `{status:'draft'|'clarification',title,memory_text,warnings:[],questions:[],provider,model,prompt_version,expected_revision,usage}`. A clarification has empty title/memory. Save reviewed drafts through PATCH using the returned revision. Generate never writes trip data, checks revisions before and after the external request, sends only selected city/date/notes/current sanitized photos, uses `store:false`, strict JSON-schema output for OpenAI, or explicit task text plus JSON-object output and local schema validation for the course Bailian gateway, and never automatically retries. Provider errors are sanitized. 400 validation, 403 origin/host, 404 missing trip/media, 409 conflict, 415 content type (upload limits may use413), 429 rate/credit, 503 missing configuration/access, 504 timeout, 500/502 storage/provider failure.

## Frontend integration

`travel-map:city-selected` has `detail.city_id`; dispatch `travel-map:trips-changed` after a successful external component save to reload snapshots. Counts deduplicate IDs and derive from all saved records. `filterTripDates` only filters displayed cards; never map counts. Brightness: 0 unvisited;1 tier1;2–3 tier2;4+ tier3. User/model text renders through textContent. Demo drafts/records use separate browser keys and never enter real backups or AI requests.

Current course configuration: Bailian Token Plan, qwen3.8-flash, prompt travel-memory-v4. Its Responses route uses explicit system/user task delivery and reasoning.effort=none. Separate provider instructions/schema handling were unreliable in observed earlier calls; failed attempts are preserved. Real requests remain current-trip-only, with no automatic provider fallback or retry.
