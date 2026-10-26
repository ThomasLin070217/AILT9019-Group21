# Backend module results — 22 October 2026

Working tree on `main` (`265253c`), not committed when these checks ran.
Environment: macOS, Python 3.14.4 in a local `.venv`, FastAPI 0.158.1, Pillow
13.0.0, pytest 9.1.1.

## Automated checks

| Check | Command | Result |
| --- | --- | --- |
| Node domain and API-client tests | `npm test` | 21/21 passed |
| Backend and configuration tests | `.venv/bin/python -m pytest` | 54/54 passed |
| Legacy preview config tests | `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | 3/3 passed |

The pytest total is 51 new backend cases plus the 3 existing `serve.py`
configuration cases. No test used real personal photographs, notes or API keys.

## What the tests prove

- A trip create, list and edit survive a new application instance using the same
  database.
- Two creates in one city are two visits; editing or retrying never changes the
  trip ID or city.
- Invalid cities, `2026-02-31`, over-long text, client-chosen IDs and identity
  edits fail without writing a row.
- Delete cascades photo rows and removes the stored file.
- A JPEG with camera, author, comment and GPS tags is re-encoded with no EXIF,
  and the private strings are absent from the served bytes.
- Oversized, non-image, tiny and over-limit uploads leave no row and no file.
- `/media/` rejects traversal, dotfiles and unknown names.
- The AI route refuses an unconfirmed request, sends only the selected trip's
  data and sanitised 1,280 px copies, times out with `504`, and returns `502` or
  `503` without modifying the saved trip.
- Error envelopes do not echo private notes, and security headers match the
  preview server.

## Not verified

- A live `uvicorn`/`python3 -m backend` launch was not performed in this
  session; the command was rejected in the tool environment. The app factory and
  every route were exercised through FastAPI's `TestClient`, including two
  separate app instances over one SQLite file.
- Playwright browser suites were not rerun in `?mode=api`; that is Thomas's
  integration check with Angel's UI.
- No cloud provider adapter exists, so real AI output quality and cost remain
  untested.
- Fresh setup on another member's computer, Safari/Firefox, physical devices and
  concurrent multi-tab writes remain outstanding.

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
.venv/bin/python -m pytest
npm test
```

Then start `python3 -m backend`, open `http://127.0.0.1:8019/app/?mode=api`, and
follow the fresh-setup checklist in `docs/BACKEND.md`.
