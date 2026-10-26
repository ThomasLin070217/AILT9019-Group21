# AILT9019 — Group 21

## Project status

We are building **Travel Memory Map**: a local travel album where saving a trip lights the city area on the map, repeat visits create separate cards and brighter visit tiers, and user-triggered AI can draft a memory from the current trip’s photos and notes.

Thomas reported on 30 September 2026 that the proposal was submitted. The [proposal baseline](proposal/Travel_Memory_Map_Proposal.docx) is preserved for the 10 October revision; the Moodle receipt has not been independently checked here. Thomas’s city-map module is runnable with fictional demo data. Owen’s local backend provides SQLite trip storage, sanitised photo uploads and the AI proxy route, and the API-mode album now has browser controls for creating, uploading, editing, requesting an AI draft and deleting. A real cloud provider adapter is still planned.

**Start with the [four-person work allocation](docs/WORK_ALLOCATION.md)** for owners, deliverables, review partners and deadlines. Thomas owns map/integration, Angel owns the interface, Owen owns backend/storage, and Qingyang owns AI/evaluation.

## Run the city map

```bash
python3 serve.py
```

Open **http://127.0.0.1:8019/app/**. Python 3.10+ is sufficient; no API key or npm installation is needed. The default map uses OpenFreeMap online tiles, a locally bundled MapLibre renderer, and the repository's 19 OpenStreetMap city boundaries. All supported city outlines remain visible; a saved visit fills its city area and repeat visits increase its colour tier. Use **View area** to inspect a city's shape. `?map=local` uses the bundled coast-and-city map without any online tiles. Google Maps remains an opt-in alternative with `?map=google` and a configured key; see [Google setup](docs/GOOGLE_MAPS_SETUP.md).

Switch between **Map** and **Album** to explore a place or see its photo cards side by side. Select a city, search by English/Chinese name, and open **Try visit counting** to add/edit fictional demo visits. The first two Osaka cards show credited example photos; click a cover to view it. Unsaved sample drafts survive city changes and reloads within the tab. Browser demo storage is not the planned real backend. Map tile requests contain the current viewed area, while our app does not send trip photos or notes to the map provider. If the online map is unavailable, the bundled map remains usable.

Run `npm test` with Node.js 20+ for the map logic/storage checks. See [Thomas handoff](docs/THOMAS_HANDOFF.md) for browser checks and [API contract](docs/API_CONTRACT.md) for teammate integration. API mode (`/app/?mode=api`) requires Owen’s backend and never substitutes demo data when it fails.

## Run the local backend

The real backend serves the app and API from one origin and stores trips and photographs locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python3 -m backend
```

Open **http://127.0.0.1:8019/app/?mode=api**. Trips, edits and sanitised photos persist in `var/travel.db` and `var/media/`; `var/` is Git-ignored, so back it up to keep the album. The API-mode album includes an **Add a memory** form plus per-card **Add photo**, **Edit memory**, **Write with AI** and **Delete trip** controls. Unsaved composer and editor text stays in the tab. `python3 serve.py` remains the zero-install demo-only server; do not run both on port 8019 at once. See the [backend guide](docs/BACKEND.md) for configuration, endpoints, limits, the AI adapter contract and backup steps.

Run `.venv/bin/python -m pytest` for the 54 backend and configuration tests, and `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` for the legacy config check.

### Mid-term check: reproduce the working backend path

1. Start `python3 -m backend` after installing `requirements-dev.txt`; open **http://127.0.0.1:8019/app/?mode=api&map=local**.
2. Select Tokyo and save a fictional trip with a short note. The map lights up and a new trip card appears. Add `data/fixtures/T04/blur_sample.png` to that card; the backend validates and re-encodes the image before storing it with the trip in SQLite.
3. Edit and save the card, then reload the page. The card, photo and text remain. Save a second Tokyo trip to check that the city shows two independent visits.

This is the current input → local processing → output path. Use only the synthetic fixture and fictional text when recording the screen. AI writing is **not** part of this verified path: without a live provider adapter its route returns `503` and does not change the saved card. The [20 October test record](tests/evidence/2026-10-20-midterm/RESULTS.md) documents the older demo-only path; see the [26 October integration review](docs/INTEGRATION_REVIEW_2026-10-26.md) for the combined build.

## Team 21

| Name | Contact email | GitHub |
| --- | --- | --- |
| Yunian Lin (Thomas) | u3660124@connect.hku.hk | [ThomasLin070217](https://github.com/ThomasLin070217) |
| Xinyue Li (Angel) | 06.xinyue@gmail.com | [Tiramuffin](https://github.com/Tiramuffin) |
| Qingyang Lin | u3659001@connect.hku.hk | — |
| Ho Yeung Seto (Owen) | hiowenseto@gmail.com | [Owen-Seto](https://github.com/Owen-Seto) |

This directory is for private repository coordination only. Do not copy these details into the anonymous Moodle proposal or peer-review forms.

## Start here

- [Course plan](docs/COURSE_PLAN.md): dates, deliverables, grading, and non-negotiable rules.
- [Work allocation](docs/WORK_ALLOCATION.md): concrete responsibilities, handoffs and milestones.
- [Backend guide](docs/BACKEND.md): local setup, schema, routes, limits, AI adapter contract and backup.
- [Team guide](docs/TEAM_GUIDE.md): current scope and collaboration workflow.
- [Proposal baseline and revision notes](proposal/README.md): the submitted draft and next revision.
- [Evaluation plan](tests/EVALUATION_PLAN.md): how we will define a real pass, failure, and safe refusal.
- [AI-use log](docs/AI_USE_LOG.md): record prompts, changes, and verification as we work.
- [Friday standup](docs/FRIDAY_STANDUP.md): the required three-line weekly update format.

## Repository structure

```text
proposal/     Proposal drafts, diagrams, and peer-review notes
app/          Application source code
backend/      Local FastAPI + SQLite service (Owen)
data/         Public, synthetic, or self-curated project data only
tests/        Test cases and evaluation evidence
docs/         Project webpage and supporting documentation
var/          Git-ignored runtime database, uploads, and temp files
```

## Working agreement

- Create a branch for substantial work and open a pull request before merging.
- Keep commits small and describe what changed.
- Never upload personal, confidential, or API-key data.
- Add setup and run instructions as soon as the application has a first working version.

## Key dates

| Date | Milestone |
| --- | --- |
| 30 Sep 2026 | Proposal draft |
| 10 Oct 2026 | Revised proposal |
| 26 Oct 2026 | Mid-term check |
| 20 Nov 2026 | Final deliverables |

## Next integration step

The album controls already work in `?mode=api`. The next step is a live provider adapter behind `backend/ai/base.py`, followed by real AI runs and independent human reviews. Before enabling uploads to that provider, decide whether the current trip's date and title are included alongside its city, notes and photos, and make the pre-send notice match the actual payload. Demo-only map controls remain prototype material.
