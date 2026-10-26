# Feature 1 — create a real trip

Status: implemented, assistant-checked and user-approved. The user requested one feature at a time, with verification and a user review before starting the next feature.

## Scope

Select a supported city → choose real photos → optionally enter a title/date/notes → save → see an independent trip card, all selected photos and updated map visits. SQLite and local image files are the necessary persistence foundation. Demo records stay separate.

## Review

1. Start `python3 serve.py --port 8020` and open `http://127.0.0.1:8020/app/?mode=local&map=local`.
2. Choose a city and click **Add a trip**. Choose 1–5 JPEG/PNG/WebP photos; remove a preview if needed. Enter a date and notes and save.
3. Confirm the card's title, date, notes and photos, and the city's visit count. Open each thumbnail to see the saved image.
4. Add another trip to that city: it should produce a separate card and exactly one additional visit.
5. Reload or stop/start the server with the same data directory. Saved photos and records should remain.
6. Cancel a filled form: discard requires confirmation and does not create a trip. Invalid photos or failed saves should report the problem and keep the form usable.

Browser verification uses the repository's credited example photos as upload fixtures in an isolated temporary album. They are test inputs, not the user's real travel history. No test uploads enter the review album.

## Automated verification

- Existing JavaScript domain/storage tests: 13.
- Python storage/HTTP/configuration tests: 13 (10 new plus 3 existing).
- New browser workflow: 9 check groups, including real uploads, failure preservation, retry deduplication, actual server restart, visit counts, photo viewer, mobile layout and cancellation.
- Existing demo browser regression suites: 28 check groups passed (map 16, album 9, views 3); 37 browser groups total including the new workflow.
- Desktop/mobile screenshots are stored locally under `.context/feature-01/` and visually inspected by the assistant. All checks passed on 20 October 2026; no cloud AI or live Google Maps checks were run for this feature.

## Boundaries

Photos are saved as JPEG copies, with orientation applied and embedded metadata removed. Up to 5 MB per file, 20 MB total, 25 megapixels per file; JPEG output's longest edge is at most 4096 px. HEIC and animated images are not supported. Original source photos are not changed. Unsaved form data and selected files remain in the open page; leaving/reloading prompts before discarding them, but drafts are not restored after closing the page.

Real card editing/deletion, backup/restore tooling, cloud AI generation, AI disclosure/draft review, uncertainty handling, five-case AI evaluation and optional export/filter/animation features remain pending. Server restart recovery is checked locally; independent setup on another person's computer is not claimed.

User approved Feature 1 and authorized Feature 2. See [Feature 2 review](FEATURE_02_REVIEW.md) for current real card editing and its separate review gate.
