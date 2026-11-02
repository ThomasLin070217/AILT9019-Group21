# Integrated workflow review · 2 November 2026

This is Thomas's release smoke check of the integrated local product, run on `feat/thomas-final-delivery` from public `main` at `d0dfb7c`. It uses an isolated temporary SQLite/media directory, fictional Nanjing text and the synthetic `data/fixtures/T02/park-bench.png`; it does not use a person's travel album or a cloud AI key. The automated run deletes its two created trips afterward. T02 is used here only as a synthetic UI image; Owen has not yet signed it off as a final evaluation case.

## How it was run

1. Install the repository dependencies, including `requirements-dev.txt`, and start an isolated backend with a temporary `TRAVEL_DB_PATH`, `TRAVEL_MEDIA_DIR` and `AI_PROVIDER` unset. The usual app URL is `http://127.0.0.1:8019/app/?mode=api&map=local`; this run used port `8042` to avoid disturbing an existing server.
2. Run `python -m pytest -q` and `npm test` from the repository root.
3. With Playwright and Chrome available, run `BASE_URL=http://127.0.0.1:8042 EVIDENCE_DIR=tests/evidence/2026-11-02-thomas node tests/final-workflow.e2e.mjs`. The script captures screenshots, a WebM recording and a JSON result. Set `PLAYWRIGHT_MODULE` and `CHROMIUM_EXECUTABLE` when those packages are not on the default path.

## Observed results

| Check | Result |
| --- | --- |
| Python backend tests | 63 passed |
| Node domain/API tests | 22 passed |
| Browser: first trip creates one card and a tier-1 lit area | Passed |
| Browser: synthetic photo stored and displayed | Passed |
| Browser: editing a card does not add a visit | Passed |
| Browser: second trip creates a separate card and tier-2 area | Passed |
| Browser: text, photo, two cards and tier survive reload | Passed |
| Browser: pre-send disclosure identifies the current city/title/notes/photo count; missing-provider request preserves the saved card | Passed |
| Browser: 390px app view has no horizontal overflow | Passed |

No uncaught browser page errors were recorded. The [desktop map](two-trips-desktop.png), [desktop album](album-desktop.png), [mobile map](two-trips-mobile.png), [mobile album](album-mobile.png), [recording](workflow.webm) and `results.json` are the retained output. The webpage uses copies of the main screenshots and recording in `docs/assets/`.

## What this does not establish

- No real cloud model was called. Its output quality, cost, provider retention and the five-case human pass rate remain unverified.
- This was one machine and one synthetic city/photo path. A fresh-computer setup, physical phone check, backup/restore and broader failure cases still need owners' evidence.
- City areas are approximate visual boundaries. A saved trip is user-entered and is not independently verified travel.
