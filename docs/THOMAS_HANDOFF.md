# Thomas map module handoff

## Delivered on 30 September 2026

- Runnable city map and equivalent searchable list, with 19 stable city IDs and pinned public-domain source data.
- City selection opens separate chronological sample cards; counts derive from independent trip IDs; brightness tiers are 1 / 2–3 / 4+.
- Demo add/edit/remove operations and browser persistence exercise the map rules. They are clearly labelled fictional and are not the planned SQLite/photo-upload implementation.
- Zoom, bounded pan, fit, native-name search, group filtering, visited filtering, empty states, visible failures, keyboard selection and responsive layout.
- Proposed [API contract](API_CONTRACT.md), replaceable data adapter, and explicit backend mode. HTTP contract tests use mocked endpoints, not Owen's actual backend.
- Initial T01 synthetic visual fixture with source/permission record and fact checklist. No AI generation or evaluation verdict is claimed.
- Project information page at `/app/about.html`, screenshots and a genuine recording of the working map demo.

## Run and check

From the repository root:

```bash
python3 serve.py
# Open http://127.0.0.1:8019/app/
```

Requires Python 3.10+; no Python packages, npm install, model key or external map service are needed for the app preview. The server binds only to 127.0.0.1 and serves `app/` and `data/`, not the entire repository. Do not use this development server on a public network.

```bash
npm test
# Node.js 20+; no npm dependencies needed for these logic tests.
```

For optional browser tests, install Playwright in a separate temporary directory to avoid changing application dependencies, and start the local preview first:

```bash
mkdir -p /tmp/travel-map-browser-tools
npm install --prefix /tmp/travel-map-browser-tools playwright@1.62.1
/tmp/travel-map-browser-tools/node_modules/.bin/playwright install chromium
PLAYWRIGHT_MODULE=/tmp/travel-map-browser-tools/node_modules/playwright/index.mjs node tests/browser.e2e.mjs
```

`CHROMIUM_EXECUTABLE`, `BASE_URL` and `EVIDENCE_DIR` may override the executable, server address and evidence output directory. The default evidence destination is `/tmp/travel-map-evidence`. The recorded check used Playwright 1.62.1 with an already installed Chromium headless binary; it did not require buying or configuring an AI service.

## Three-minute map walkthrough

1. Start in Osaka: two independent fictional trip cards and a count of two.
2. Select an unvisited city by marker or search; observe its empty state.
3. Return to Osaka, open Try visit counting, and add two sample visits. The count reaches four and the marker changes tier.
4. Edit a sample card and save. The count remains four. Reload and confirm persistence.
5. Remove a sample visit; count and tier recalculate. Reset the sample album to return to the original records.
6. Explain the boundary: uploads, SQLite and actual cloud AI are not connected. Show API mode failing honestly while the static server has no backend routes.

The short browser-test recording is functional evidence of this map module, not the final course presentation or a live AI demo. Re-record the actual integrated application for the mid-term.

## Handoffs to teammates

- **Angel:** reuse the selected city event and city IDs. Replace the simple sample-card view with the upload/album interface and dispatch `travel-map:trips-changed` after a successful real save. Do not use demo operations for real user data.
- **Owen:** serve the static assets and implement the two read arrays specified in the contract. Review ID/date/field limits and create-versus-update semantics before implementing writes. Switch the app to `?mode=api` for integration.
- **Qingyang:** add the actual generation adapter with Owen/Angel. Use `data/fixtures/T01/case.json` as a narrow initial smoke case; prepare the other cases and evaluate real outputs separately. Realistic photo quality remains untested.
- **Thomas:** collect teammate review, run the same checks against the genuine backend once ready, integrate uploads and AI, and record actual end-to-end evidence. No teammate acceptance or real API integration has been claimed.

## Follow-up verification

The [1 October test round and UI reference report](UI_REVIEW_2026-10-01.md) records passing regression tests and additional open issues: unsaved drafts, mobile card visibility, long titles and small touch targets. The follow-up UI pass resolves draft persistence, long-title wrapping, mobile selection visibility and control sizing; see `tests/evidence/2026-10-01-followup/RESULTS.md` for fresh evidence.

## Remaining limitations

The map is city-centre level and uses regional 1:50m coastline geometry. Close markers in the Pearl River Delta and Kansai can overlap at the broadest view; the city list and zoom provide exact selection. No geographic visit verification or route guidance is offered. Demo data is stored per browser/origin; changing port changes its storage, and clearing browser storage removes demo edits.

A fictional sample album is the initial view, clearly labelled. API mode deliberately does not fall back to samples. AI, real image handling, data-folder backups and SQLite failure behaviour are not covered by the current map tests.

## Earlier UI follow-up — 1 October (superseded layout)

The city catalogue now sits above a map/photo-card split view. The first two Osaka demo cards include credited local example photographs; all other demo records remain text-only. Covers open in an accessible native dialog. API mode supports the proposed same-origin media preview objects in contract v0.2, tested only with mocked routes. Real upload and AI generation remain pending. `tests/album.e2e.mjs` adds regressions for these interactions; use the same environment variables as the existing browser suite.


## Frontend redesign — 1 October

The current layout replaces the earlier top catalogue with a left city index, central map and a larger selected-city album. Map / Album switches expand the same city’s separate trip cards without changing counts or drafts. The view choice is stored in the URL (`?view=album`, compatible with `mode=api`). The city catalogue lists visited cities first, alphabetically within each group. Selected cities can show a photo thumbnail above their map marker; unavailable images leave the visit marker usable. Repeat-trip counts are printed on visited markers, alongside brightness.

Map data now uses pinned Natural Earth 1:50m geometry, filtered to the region. Headings use a bundled OFL-licensed Fraunces font. No external tiles, fonts or new service keys are needed. Google Maps remains an optional future integration requiring the user’s Cloud setup/key; it has not been connected.

Run `tests/views.e2e.mjs` with the same browser environment variables to verify view switching, reload/draft continuity and 320–1440px layouts. Latest evidence: `tests/evidence/2026-10-01-redesign/`. Source reference notes: [frontend research](FRONTEND_REFERENCES.md). Angel can build on this view structure for the actual upload/gallery module; the sample controls remain prototype-only.
