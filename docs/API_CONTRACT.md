# Map integration contract

Version 0.2, 1 October 2026. Implemented by Thomas for the map prototype; **proposed for review by Owen, Angel and Qingyang**, not a claim of joint approval or a finished backend. The static preview does not implement `/api` routes.

## Running modes

- `/app/`: explicit fictional demo. `DemoRepository` in `app/repository.mjs` uses a separate browser-local key `travel-memory-map.demo.v1`. It is replaceable and is not the proposed SQLite backend.
- `/app/?mode=api`: reads `GET /api/cities` and `GET /api/trips` from the same origin. Errors remain errors; no demo fallback. Demo write controls are absent. Owen's local Python server can serve the existing static files plus these routes.
- No cloud calls, map tile calls, account login, analytics or upload endpoint in this module. Two credited example covers are bundled locally for demo mode. Refresh the API view after another component saves a record.

## City records

`GET /api/cities` returns a JSON array matching `data/cities.json`:

```json
[{"id":"jp-osaka","name":"Osaka","local_name":"大阪","region":"Japan","longitude":135.503754,"latitude":34.691095,"source_ne_id":1159151537}]
```

IDs are stable integration keys, not display names. `region` is a UI filter group. Return unique IDs and numeric coordinates. The initial catalogue has 19 cities; source coordinates and licence are recorded in `data/SOURCES.json`. Owen should seed from this catalogue rather than invent another spelling/ID set. Changing the supported geography requires reviewing the initial map extent.

## Trip snapshots

`GET /api/trips` returns all **saved** trip snapshots, not draft or per-photo rows:

```json
[{
  "id":"trip-stable-id",
  "city_id":"jp-osaka",
  "trip_date":"2026-05-16",
  "title":"A rainy weekend",
  "notes":"My own notes",
  "memory_text":"Text reviewed and saved by the user",
  "photos":[],
  "source":"user"
}]
```

- `id`: non-empty stable string. One distinct ID is one visit. Changing a note, photos or AI text must retain this ID and city ID.
- `city_id`: an existing catalogue ID.
- `trip_date`: real ISO calendar date `YYYY-MM-DD`, or `null`; sorted newest first, unknown dates last.
- `title`: text, up to 200 characters. `notes` and `memory_text`: text, up to 5,000 characters each; empty strings allowed. The map uses `textContent`, never HTML from user/model text.
- `photos`: array. Optional preview objects may contain `{"id":"photo-id","url":"/media/photo-id.jpg","alt":"User-provided description"}`. The first object with a same-origin `/media/` URL supplies the cover; legacy ID-only objects remain valid and render as text-only cards. URLs outside this path are ignored. Failed image loads leave the memory text visible. This optional shape is proposed for Owen/Angel review; photo upload, cover choice and multi-photo gallery remain integration work. The static server does not implement `/media/`; browser checks mock it.
- `source`: provenance such as `demo` or `user`; not used to infer a visit.

Duplicate snapshots with the same ID are counted once, with the final array occurrence winning. The backend should return exactly one current snapshot per ID. The UI never uses the number of photos or generation calls as a visit count.

## Visit calculation

`countVisits()` deduplicates trip IDs then groups by city. `visitTier()` maps 0 to unvisited, 1 to tier 1, 2–3 to tier 2 and 4+ to tier 3. Text always displays the exact count. Removing the last trip returns a city to unvisited. Counts are derived from saved records instead of maintaining a separate counter that can drift.

## Component events

After a city is selected, the map dispatches:

```js
window.addEventListener('travel-map:city-selected', event => {
  const cityId = event.detail.city_id;
  // Angel can open the corresponding trip form/list.
});
```

After the backend confirms a trip create/update/delete, an integrated component can request a fresh snapshot:

```js
window.dispatchEvent(new Event('travel-map:trips-changed'));
```

The map re-reads the active repository. This event must follow a successful save, not an unsaved edit. API refresh failure is visible and does not fabricate success.

## Proposed writes for the backend team

Owen and Angel should review route names before implementing them: `POST /api/trips` creates an independent trip ID, `PATCH /api/trips/{id}` edits an existing card, and `DELETE /api/trips/{id}` removes that visit. Editing AI text must use update, never create. Photo upload and AI generation request/response limits remain Owen/Angel/Qingyang's review items.

Qingyang's draft result should distinguish a draft from a request for clarification. The map has **not** implemented or validated that AI endpoint. Keep API keys in the backend; send only the selected trip after the agreed notice. Do not expose them in these read responses.

## Failure contract and review checklist

Return non-2xx for failures and do not return success with missing/corrupt trip arrays. Frontend requests time out after 10 seconds. Invalid city IDs/dates/text shape fail visibly. Demo writes also report quota/access errors instead of pretending to persist.

- Owen: approve catalogue IDs, read-array shapes, persistence semantics and local hosting.
- Angel: confirm selection event, replace sample card UI with the real album component, and trigger refresh after successful writes.
- Qingyang: agree generation and clarification semantics with Owen/Angel; map counts must not depend on generation outcomes.
- Thomas: integrate actual modules once available and repeat the browser checks against the real backend. Mocked HTTP tests do not complete that handoff.

## Draft and cover behaviour

Demo text drafts use a separate per-tab session-storage key (`travel-memory-map.demo-drafts.v1`), survive city changes/reloads, and never count as saved trips. Saving clears that draft only after the repository reports success. Explicit discard/reset/delete clears the corresponding drafts. If draft persistence fails, in-memory edits remain and the user is told to keep the tab open. These controls are not enabled in API mode.

Clicking a cover opens the native image dialog; Escape/Close restores focus. Demo covers always retain their separate photographer/example label and are never used as backend fallbacks or AI inputs.
