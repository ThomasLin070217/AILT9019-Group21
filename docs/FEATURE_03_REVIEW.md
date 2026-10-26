# Feature 3 — delete a real trip

Status: implemented, awaiting user review. Creation and editing were approved before this work. No fourth feature has started.

## Review

Open `http://127.0.0.1:8020/app/?mode=local&map=local`, select a city with a saved real trip and choose **Delete trip** below its card. If the review album is empty, first add a disposable trip with **Add a trip**.

1. The confirmation names the saved trip and photo count. **Keep trip** cancels; nothing changes. Keyboard focus starts on that safe action.
2. **Delete permanently** removes that trip and the album's photo copies. Original files chosen from your computer are untouched. Any unsaved editor for that trip is discarded only after confirmed successful deletion.
3. Check the city count and marker. Deleting one of four visits changes 4→3 and its brightness tier; 2→1 changes tier again; removing the last visit returns the city to its unvisited empty state. Other trips/cities must remain.
4. Reload or restart the server: deleted trips must stay deleted. A repeated delete request must not remove another visit.
5. An edit saved from another tab makes a stale deletion fail with a conflict. Refresh, review the updated card and confirm again if still desired.

## Storage and failure handling

`DELETE /api/trips/{id}` takes JSON `{expected_revision}` and returns `{id, deleted:true, cleanup_pending:boolean}`. The revision check and removal from the active album are one SQLite transaction. Failed transactions leave the original snapshot and photo files intact. A pending request disables further actions on that card. Failed/uncertain responses preserve the displayed card and its draft; retrying the same deletion is safe, or refresh to reconcile what was actually saved.

After a committed deletion, the local photo directory is removed. If the OS temporarily prevents file cleanup, the response explicitly reports `cleanup_pending`, the interface says so, and refreshing retries cleanup. Deleted photo URLs return 404 even while files await cleanup. A minimal deleted identity/request marker prevents lost-response retries or old create requests from resurrecting a deleted visit; saved text/photo references are removed from the snapshot. There is no user-facing trash or undo in this feature.

Existing SQLite albums are migrated additively on first access. Legacy trips with no revision remain supported.

## Verification

Storage/HTTP tests cover target isolation, retries, invalid/stale requests, database failure, file-cleanup failure and retry, deleted media access, create-replay prevention, and original-schema migration. The new browser suite is `tests/trip-delete.e2e.mjs`; all fixtures use an isolated temporary album and credited repository example photos, never the user's review album.

20 October 2026 verification: all 13 JavaScript and 27 Python tests passed (40 total). All 54 browser check groups passed: deletion 9, editing 8, creation 9, demo map 16, demo album 9 and views 3. Desktop/mobile screenshots were visually inspected. Screenshots and browser results live under `.context/feature-03/`.

## Next review unit

Proposed next: local album backup and restore. Wait for user acceptance before starting. Cloud AI, the five-case AI evaluation, and optional export/date-filter/map-animation features remain pending.
