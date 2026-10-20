# Album UI follow-up verification — 1 October 2026

This pass follows the user's approval to implement the [UI review](../../../docs/UI_REVIEW_2026-10-01.md). App source hashes are in [source-sha256.json](source-sha256.json).

## Results

- **13/13 unit tests passed**, including draft reconstruction, quota failure with in-tab retention, and same-origin media URL validation.
- **16/16 existing map browser check groups passed** on the final layout. The injection check now specifically rejects an injected image instead of assuming all cards must be image-free.
- **9/9 new album browser check groups passed**: credited local cover loading; photo viewer/Escape/focus; draft navigation/reload; saved-trip identity; explicit discard; long titles; mobile city selection; exact selection near overlapping pins; same-origin mocked API photos and broken-image fallback. The tests also assert mobile cards are not height-clipped and controls meet the 44px target.
- Diagnostics covered **320, 390, 540, 541, 768, 851, 1024 and 1440px** with no horizontal document overflow. Draft text survives city changes; long titles do not overflow the panel; Tokyo selection brings memories into view; synthesized touch panning changes the map view and clears drag state. The checkbox itself is 18px but its clickable label is at least 44px high.
- Desktop/mobile captures were visually inspected during the bounded implementation pass. A desktop height cap that initially leaked onto mobile was removed and covered by an explicit final browser assertion.
- `git diff --check` passed. Original proposal and travel fixture data were not edited.

[Desktop](desktop.png) · [Mobile](mobile.png) · [Album checks](album-results.json) · [Map checks](browser-results.json) · [Diagnostics](audit-results.json)

Tests used Playwright/Chromium in fresh isolated contexts, not the user's open album. Narrow-screen taps on overlapping pins intentionally open a city chooser. The new test uses a real touchscreen coordinate at the visible pin to exercise that routing; it does not force a click through the overlapping elements. All final checks passed.

## What changed

Top search/filter/city strip; wider photo-led cards beside the map; mobile selection scrolls to the album; exact nearby-city choices; larger map controls and hit areas; safe wrapping; per-tab draft persistence with explicit discard; credited demo covers and an image viewer. Two Unsplash photographs are bundled as local presentation examples with license/source hashes; they are never real trip evidence or AI inputs.

## Still pending

Real photo upload, multi-photo gallery/cover selection, SQLite persistence, live cloud AI and actual teammate backend integration. The optional `/media/` contract is proposed and tested with mocks. No claim of physical-device testing, Safari/Firefox testing, full accessibility certification or AI evaluation success. Per-tab drafts are not a backup and closing the tab may remove them.
