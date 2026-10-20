# Map module verification

Run date: 30 September 2026. This records Thomas's map module, **not** the five AI evaluation cases or the integrated application. Exact tested source hashes are in [source-sha256.json](source-sha256.json).

## Results

- `npm test`: **10/10 passed** with Node.js 24.11.1. Covers visit identity, brightness boundaries, create/edit/reload/remove, invalid inputs, storage failures, search/filtering, chronological cards, source points within the map, bounded zoom/pan and the read adapter.
- `tests/browser.e2e.mjs`: **16 check groups passed** using Playwright 1.62.1 and Chromium headless. Includes desktop (1440 × 1050) and mobile (390 × 844), keyboard focus, Chinese search, empty states, repeat visits, safe text rendering, reload, reset/recovery, API-error behaviour and preview-server file restrictions.
- No page JavaScript errors or horizontal document overflow were observed in the tested views. Demo runtime requests remained on the local origin.
- Screenshots were visually inspected; mobile label placement was adjusted and final interactions rerun. Local documentation links and `git diff --check` passed.

Machine-readable check descriptions: [browser-results.json](browser-results.json).

## Captures

[Desktop screenshot](desktop.png) · [Mobile screenshot](mobile.png) · [Map walkthrough recording](map-walkthrough.webm)

The recording is an automated walkthrough of real map controls over explicitly fictional data. It also exercises storage recovery. It is not a live AI demo or the final presentation.

## What these results do not show

- Backend mode was checked with mocked HTTP responses. Owen's genuine SQLite backend is not implemented/integrated here.
- No real photos, personal notes, cloud model API, token costs or VLM factual accuracy were tested.
- Browser-local persistence validates the demo adapter, not database reliability or cross-device sync.
- T01 has a narrow synthetic visual fixture; it and T02–T05 still need actual model outputs and human scoring.
- Teammate review/acceptance and a fresh setup on another member's computer remain pending.
