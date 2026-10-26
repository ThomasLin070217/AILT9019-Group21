# Map and backend integration contract

Version 0.4, 22 October 2026. The trip, photo and AI-proxy routes are implemented
by Owen's local backend (`python3 -m backend`), and the API-mode album now uses
them for the create, upload, edit, AI-draft and delete controls. Demo mode is
unchanged. Angel, Qingyang and Thomas should still review and extend their
modules against this contract; implementation here is not a claim of joint
acceptance.

## Running modes

- `python3 serve.py` — zero-dependency **demo-only** preview. It serves `app/`
  and `data/` and implements only `/api/map-config`. It has no trip API.
- `python3 -m backend` — the real local service. It serves `app/`, `data/`, the
  JSON API and `/media/` from one origin, and stores state in `var/`.
- `/app/` — explicit fictional demo. `DemoRepository` in `app/repository.mjs`
  uses the browser-local key `travel-memory-map.demo.v1`.
- `/app/?mode=api` — reads and writes the real backend. Errors remain errors; no
  demo fallback. Demo write controls are absent.
- No account login, analytics or upload to a third-party service in this module.
  A real cloud AI call happens only through `POST /api/trips/{id}/memory` after
  an explicit confirmation, once a provider adapter is configured.

## City records

`GET /api/cities` returns a JSON array matching `data/cities.json`:

```json
[{"id":"jp-osaka","name":"Osaka","local_name":"大阪","region":"Japan","longitude":135.503754,"latitude":34.691095,"source_ne_id":1159151537}]
```

IDs are stable integration keys, not display names. `region` is a UI filter
group. The backend rejects duplicate IDs at startup and seeds no separate city
table. The initial catalogue has 19 cities; source coordinates and licence are
recorded in `data/SOURCES.json`.

## Trip snapshots

`GET /api/trips` returns all **saved** trip snapshots, not drafts or per-photo
rows. `GET /api/trips/{id}` returns one snapshot.

```json
[{
  "id":"trip-stable-id",
  "city_id":"jp-osaka",
  "trip_date":"2026-05-16",
  "title":"A rainy weekend",
  "notes":"My own notes",
  "memory_text":"Text reviewed and saved by the user",
  "photos":[{"id":"photo-id","url":"/media/photo-id.jpg","alt":"A view"}],
  "source":"user"
}]
```

- `id`: server-generated UUID. One distinct ID is one visit. Editing a note,
  photos or AI text retains this ID and city ID.
- `city_id`: an existing catalogue ID. `PATCH` cannot change it.
- `trip_date`: real ISO calendar date `YYYY-MM-DD`, or `null`. Newest first,
  unknown dates last, then most recently created.
- `title`: up to 200 characters. `notes` and `memory_text`: up to 5,000
  characters each; empty strings allowed. The map uses `textContent`, never HTML
  from user or model text.
- `photos`: preview objects with a same-origin `/media/` URL. The first photo is
  the cover. Metadata such as width and height is returned by the upload route
  but not repeated in the snapshot.
- `source`: provenance such as `demo` or `user`; never used to infer a visit.

Duplicate snapshots with the same ID are counted once by the frontend, with the
last occurrence winning. The backend returns exactly one snapshot per ID. The UI
never uses the number of photos or generation calls as a visit count.

## Write routes (implemented)

| Method and path | Body | Result |
| --- | --- | --- |
| `POST /api/trips` | `city_id`, optional `trip_date`, `title`, `notes` | `201` snapshot. Server sets `id`, `source`, timestamps. Unknown fields such as `photos`, `memory_text`, `source` or a client `id` return `422`. |
| `PATCH /api/trips/{id}` | any of `title`, `notes`, `memory_text`, `trip_date` | `200` snapshot. `id` and `city_id` return `422`. An empty patch returns `422`. |
| `DELETE /api/trips/{id}` | none | `204`; removes photo rows and their files. |

Editing must use `PATCH`; only `POST` creates a visit. The frontend must disable
its submit control while a create request is in flight, because a deliberate
second create is a legitimate second visit and the backend has no idempotency
key.

## Photo upload (implemented)

`POST /api/trips/{id}/photos` accepts `multipart/form-data` with one `file` and
an optional `alt` (up to 200 characters). Create the trip first, then upload each
photograph separately.

```json
{"id":"photo-id","url":"/media/uuid.jpg","alt":"A view","width":1600,"height":1200}
```

- Accepted: JPEG, PNG and WebP only; no animation; minimum 64 px edge; maximum
  40 megapixels; 10 MiB per upload; 8 photographs per trip.
- Every accepted upload is re-encoded into a new image. EXIF, XMP, GPS, author
  comments and other ancillary metadata are removed. A small ICC profile is
  retained. The original bytes are not preserved.
- Stored copies are limited to a 2,400 px longest edge. PNG with alpha stays
  PNG; everything else becomes JPEG.
- `GET /media/{filename}` serves only database-referenced files with generated
  UUID names. Traversal, dotfiles and unknown names return `404`.
- `DELETE /api/trips/{id}/photos/{photo_id}` removes the row and file.
- Failures: `413` too large, `415` unsupported, `422` invalid/too small/limit
  reached, `404` unknown trip. A failed upload leaves neither a row nor a file.

## AI memory route (implemented proxy and optional Responses provider)

`POST /api/trips/{id}/memory`

```json
{"confirmed": true}
```

The confirmation is mandatory and represents the pre-send notice. Without it the
route returns `400 confirmation_required` and makes no provider call.

Success returns either an editable draft or a clarification request:

```json
{"status":"draft","title":"A rainy weekend in Osaka","text":"...","question":null,"warning":null,"model":"..."}
```

```json
{"status":"clarification","title":"","text":"","question":"Which city is in the first photograph?","warning":"The notes and photos disagree."}
```

Rules enforced by the route:

- Only the selected trip's city, date, title, notes and sanitised 1,280 px JPEG
  copies are passed to the adapter. No other album data is included.
- The route is read-only. It never writes `memory_text`; the user must save the
  edited draft through `PATCH /api/trips/{id}`.
- Keys stay in the server environment and are never returned or logged.
- Missing configuration → `503 ai_not_configured`; provider failure or unusable
  output → `502 ai_provider_error` / `ai_malformed_response`; timeout → `504
  ai_timeout`. The saved trip is unchanged in every case.
- `AI_PROVIDER=responses` selects Thomas's OpenAI-compatible adapter against
  `backend/ai/base.py`. A real provider call on this combined branch remains
  to be verified; without configuration the route returns `503`.

## Error envelope

Every non-2xx API response uses:

```json
{"error":{"code":"trip_not_found","message":"This trip does not exist.","details":[]}}
```

Codes are stable strings. `details` is optional and never contains notes,
prompts, keys or request bodies. `GET /api/health` is a monitoring exception: a
degraded service returns `503` with health fields plus an `error` object.

## Visit calculation

`countVisits()` deduplicates trip IDs then groups by city. `visitTier()` maps 0
to unvisited, 1 to tier 1, 2–3 to tier 2 and 4+ to tier 3. Text always displays
the exact count. Counts derive from saved records rather than a separate counter.

## Component events

After a city is selected, the map dispatches:

```js
window.addEventListener('travel-map:city-selected', event => {
  const cityId = event.detail.city_id;
  // Angel can open the corresponding trip form/list.
});
```

After the backend confirms a trip create/update/delete, an integrated component
can request a fresh snapshot:

```js
window.dispatchEvent(new Event('travel-map:trips-changed'));
```

The map re-reads the active repository. This event must follow a successful
save, not an unsaved edit. API refresh failure is visible and does not fabricate
success.

## Failure contract and review checklist

Read requests time out after 10 seconds; photo upload after 60 seconds; AI
requests after 25 seconds so the 20-second server budget is usable. Return
non-2xx for failures and never return success with missing or corrupt arrays.
Invalid city IDs, dates and text shapes fail visibly. Demo writes report
quota/access errors instead of pretending to persist.

- **Owen:** backend, schema, sanitisation, media serving and proxy implemented;
  the API-mode composer/card controls are wired through `ApiRepository`.
  Fresh-setup verification on another machine remains.
- **Angel:** review the new API-mode composer, editor, photo strip and AI notice
  states, refine the visual/interaction details, and keep the demo-only controls
  separate. Dispatch `travel-map:trips-changed` only after a confirmed save.
- **Qingyang:** run the combined Responses adapter on approved fixtures and
  coordinate independent draft/clarification review; map counts must not depend
  on generation outcomes.
- **Thomas:** repeat the browser checks in `?mode=api` against the real backend.
  A focused workflow check is in `tests/api-ui.e2e.mjs`; mocked HTTP tests do not
  complete the full integration handoff.

## Draft and cover behaviour

Demo text drafts use a separate per-tab session-storage key
(`travel-memory-map.demo-drafts.v1`), survive city changes and reloads, and never
count as saved trips. Saving clears that draft only after the repository reports
success. Explicit discard/reset/delete clears the corresponding drafts. If draft
persistence fails, in-memory edits remain and the user is told to keep the tab
open. These demo controls are not enabled in API mode.

Clicking a cover opens the native image dialog; Escape/Close restores focus.
Demo covers retain their separate photographer/example label and are never used
as backend fallbacks or AI inputs.
