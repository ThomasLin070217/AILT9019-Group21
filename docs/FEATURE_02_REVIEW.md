# Feature 2 — edit a saved real trip

Status: implemented, assistant-checked and user-approved. The user authorized Feature 3 after reviewing Feature 2.

## Scope and review

Open `http://127.0.0.1:8020/app/?mode=local&map=local`, choose a city with a saved trip and click **Edit trip** below its card. If the album is empty, create a trip using the already approved **Add a trip** workflow first.

1. Change the title, trip date and notes. **Save changes** updates the same trip; card ordering follows the edited date.
2. Check that the ID, city, photos and total visits are unchanged. The map tier must not change merely because text was edited.
3. Reload or restart the server: the edited saved record should remain.
4. Type a draft, switch city or Map/Album view, then return: the draft remains. It also survives a reload in the same tab when session storage is available.
5. Cancel a modified editor: confirm discarding the draft. The saved trip remains unchanged. A save failure keeps the draft available to retry.
6. With the same trip open in two tabs, save in one then try saving different edits in the other. The second save reports a conflict and keeps that tab's draft. **Reload saved version** asks before discarding changes and loads the latest saved trip.

Title and notes may be cleared; an empty title uses `A visit to <city>`. The date may be cleared to “Date not recorded”. Existing photos and the saved city are intentionally fixed in this edit feature. There is no cloud or AI request.

## Implementation and checks

- `PATCH /api/trips/{id}` accepts `title`, `trip_date`, `notes` and required `expected_revision`. SQLite performs a serialized revision check and update in one transaction.
- Old Feature 1 records without a revision are treated as revision 0, so existing local albums require no manual migration.
- Successful edits retain the original identity and all photo references/bytes. Replaying the last successful edit is idempotent; stale conflicting content returns 409.
- Per-tab edit drafts use `travel-memory-map.local-edits.v1`, separate from demo drafts. Failed draft persistence keeps in-memory edits and displays a warning; it does not affect the saved SQLite album. This is draft recovery, not a backup tool.
- Verification commands: `npm test`, `python3 -m unittest discover -s tests -p 'test_*.py'`, and Playwright `tests/trip-edit.e2e.mjs`. Creation and existing demo/browser suites are also rerun before handoff.
- Screenshots and the new browser result record are in `.context/feature-02/`. Browser tests use a temporary album and the repository's credited example photo, never the user's album.
- 20 October 2026: 13 JavaScript tests and 20 Python tests passed. All 45 browser check groups passed: editing 8, creation 9, demo map 16, demo album 9, views 3. Desktop/mobile screenshots were inspected by the assistant.

## Still pending

Photo replacement/removal on existing trips, backup tooling, all AI functionality and its five-case evaluation, and the optional export/filter/animation features. Real trip deletion is now implemented and awaiting its own review in [Feature 3](FEATURE_03_REVIEW.md).
