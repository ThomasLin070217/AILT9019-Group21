# API-mode interface results — 22 October 2026

Working tree on `main` (`265253c` plus uncommitted changes). Backend started from
the working tree on `127.0.0.1:8021` with a temporary SQLite database and media
folder. Browser: headless Google Chrome driven by `playwright-core` 1.62.1.

## Checks

| Check | Result |
| --- | --- |
| Create a trip from the API composer | Pass |
| Upload a photo from the card | Pass |
| Edit the memory text and save | Pass |
| Unconfigured AI fails visibly without changing the trip | Pass (`503`, clear message) |
| Delete the trip and its photos | Pass |
| No horizontal overflow at 390px | Pass |

`api-ui-results.json` records the machine-readable result; `api-ui.png` is the
desktop capture taken after the AI failure and before deletion.

## What the flow proves

- The browser can create a real backend trip without typing a terminal command.
- The uploaded photo is served back from `/media/` and appears as a card cover
  and thumbnail.
- Editing title, notes and memory text uses `PATCH` and leaves the visit count
  unchanged.
- The AI button shows the pre-send notice; with no provider configured the route
  returns `503` and the interface reports it instead of inventing text.
- Deleting the trip removes the card, photo row and stored file.
- The stacked 390px layout has no horizontal document overflow.
- In a separate check, composer text survived a city change and an unsaved
  editor draft reopened on return, then cleared after saving.

## Regression checks

| Suite | Result |
| --- | --- |
| `tests/views.e2e.mjs` | 3/3 checks passed |
| `tests/album.e2e.mjs` | 9/9 checks passed |
| `tests/browser.e2e.mjs` | Not run: the environment lacks Playwright's ffmpeg binary required for its video recording |

## Not verified

- The full existing Playwright suites (`browser`, `google-map`) were not rerun
  for this change.
- A real AI provider, Safari/Firefox, physical devices, a fresh machine and
  concurrent tabs remain untested.
- The test album used synthetic photographs and fictional notes only.

## Reproduce

```bash
python3 -m backend

PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs \
CHROMIUM_EXECUTABLE="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
BASE_URL=http://127.0.0.1:8019 \
node tests/api-ui.e2e.mjs
```
