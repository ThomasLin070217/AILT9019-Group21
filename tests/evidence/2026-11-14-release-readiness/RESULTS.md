# Release readiness verification — 14 November 2026

Codex-operated on the development Mac; not independent human acceptance. No cloud calls in this batch.

- 89 Python tests and 25 Node tests pass, including keyed retries, simultaneous requests, database migration and local submission validation.
- Portable checker: 16 real HTTP/storage/restart/backup/restore checks pass; see `portable-workflow.json`. It starts an isolated server and disables cloud AI, without touching the user's album. Source hashes identify the working-tree implementation; the embedded Git commit is its base, not a claim of a clean tree.
- Real Ego browser: deliberately dropped a committed 201 create response, reloaded, then retried the preserved form. One trip remained, with “Saved trip recovered. Visit count unchanged.” A deliberate identical subsequent visit used a fresh key and produced two trips. See `browser-result.json`, snapshots and screenshot. UUID operation keys are not credentials.
- Server remembers keyed requests across restart; a changed payload returns 409 and deleted-trip replay returns 410. A new key creates a new visit. Schema v1 → v2 preserves trip/photo rows.
- `scripts/check_submission.py` checks PDF length, required links, distinct YouTube video IDs and matching PDF URLs; only then can it produce a local ZIP. It cannot verify playback, actual participation or human judgment.

## Limits

Single local user, no authentication/load-test claim. Session-storage denial limits retry persistence to memory. Request mappings have no expiry. Existing live-Qwen evidence remains separately dated; this test is not an additional AI quality evaluation. The historical absolute-path verifier remains archived unchanged; use the new portable module for future runs. Human output ratings, T03 permission/run, four-member Zoom presentation and real YouTube URLs are still outstanding.
