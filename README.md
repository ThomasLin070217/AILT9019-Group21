# Travel Memory Map · AILT9019 Group 21

Travel Memory Map is a local travel album. A person selects one of 19 supported cities, saves a trip and optional photos/notes, and sees that city light up on the map. A return visit creates a separate card; the city highlight has distinct tiers for 1, 2–3 and 4+ saved trips. The map is a visual record of user-entered trips, not proof of travel.

The integrated product is on `main`. It uses FastAPI, SQLite and a browser interface. Photos are re-encoded before local storage to remove location/camera metadata. **Write with AI** is optional and user-triggered: the interface shows the selected trip fields before requesting a draft, and the draft must be reviewed and saved separately. The provider setting is named `AI_PROVIDER=responses` for compatibility, but the current adapter uses an OpenAI-compatible **Chat Completions** endpoint. [Real Qwen integration was verified on 14 November](tests/evidence/2026-11-14-live-ai/RESULTS.md), including editable drafts, explicit save and restart persistence. T01/T02/T04/T05 and two safety cases have live outputs; T03 cloud-transfer permission and independent human scores remain pending.

## Try the public interactive demo

[Open the browser demo](https://thomaslin070217.github.io/AILT9019-Group21/play/app/?mode=demo&map=local): explore cities, open sample photo cards, edit fictional memories, add repeat visits and reload browser-local changes. No installation or API key is required. Photo uploads and cloud AI require the local backend below; they are not hosted on GitHub Pages.

The Pages site uses `docs/`. After changing the UI or public sample assets, run `python3 scripts/build_public_demo.py`, then `python3 scripts/build_public_demo.py --check`. The allowlist excludes personal fixtures, backend state and credentials.

## Run the working local product

Python 3.10+ is required. From a clone of this repository:

```bash
python3 -m venv .venv
source .venv/bin/activate                 # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python3 -m backend
```

Open **http://127.0.0.1:8019/app/?mode=api&map=local**. The bundled map needs no tile or AI key. The default `/app/?mode=api` view uses online OpenFreeMap tiles with an automatic local fallback. Google Maps is an optional third view with a separately configured key.

1. Choose a city and select **Add a memory**. Save a fictional title/notes.
2. Use **Add photo** on the saved card. For a non-personal sample, use `data/fixtures/T02/park-bench.png`.
3. Use **Edit memory**, save, then reload. The card, photo and text persist in local SQLite storage.
4. Save another trip in the same city. There are now two cards and a brighter map tier.
5. **Write with AI** shows the fields that would be sent. With no configured provider, it reports an error without changing the saved card.

Runtime data lives in Git-ignored `var/travel.db` and `var/media/`; back up both together. For configuration and limits see the [backend guide](docs/BACKEND.md). For a shorter walkthrough see [Quick start](docs/QUICK_START.md).

## Project webpage and evidence

- [Live project webpage](https://thomaslin070217.github.io/AILT9019-Group21/) ([source](docs/index.html)): problem, workflow, recorded local demonstration, setup, evidence and limits. The application itself still runs locally.
- [2 November integrated smoke check](tests/evidence/2026-11-02-thomas/RESULTS.md): browser workflow against an isolated backend and synthetic photo.
- [14 November live Qwen evidence](tests/evidence/2026-11-14-live-ai/RESULTS.md): real cloud requests, a JSON-formatting fix, retained failures/reruns, browser save/restart checks, 68 Python and 22 Node tests. Six expected response types are not a human quality score.
- [6 November AI integration check](tests/evidence/2026-11-06-ai-mock/RESULTS.md): browser and fixture path against a local fake model, including consent, selected-trip privacy, editable draft and save. This is not a live-model quality result.
- [Evaluation plan](tests/EVALUATION_PLAN.md): T01–T05 and the human-review rules. Four of the five original cases have live outputs; T03 and independent human scores remain pending.
- [Team and agent handoff](HANDOFF.md), [dated AI milestones](docs/AI_CHECKPOINTS_2026-11-06.md) and [release checklist](docs/RELEASE_CHECKLIST.md): current owner tasks, acceptance evidence and remaining gates.

Developers can run `npm test` and, after `pip install -r requirements-dev.txt`, `.venv/bin/python -m pytest -q`. The browser smoke script is `tests/final-workflow.e2e.mjs`; it requires Playwright and a running isolated backend. Test counts and limitations are recorded in the linked evidence, not inferred from this README.

## Data, privacy and limitations

The city footprints derive from OpenStreetMap, the bundled coastline from Natural Earth, and the default online tiles from OpenFreeMap. See [data sources](data/README.md) and [map basemap](docs/MAP_BASEMAP.md). The app is for one local user; it has no account system or cloud album sync. The 19 city areas are approximate display footprints. A cloud AI call sends only the selected trip's city, date, title, notes and sanitised photos after the user's confirmation. Photos stay local unless that optional call is made; provider retention and permission must be checked before using personal material. A failed AI call leaves the saved trip unchanged.

## Team and course

| Member | Role | Contact |
| --- | --- | --- |
| Yunian Lin (Thomas) | Map, integration and delivery | u3660124@connect.hku.hk |
| Xinyue Li (Angel) | Interface and first-use testing | 06.xinyue@gmail.com |
| Ho Yeung Seto (Owen) | Backend and local storage | hiowenseto@gmail.com |
| Qingyang Lin | AI evaluation | u3659001@connect.hku.hk |

All four members agreed to publish these contacts in the repository. The official final-deliverables date in the course overview is **20 November 2026**; Moodle controls the final submission instructions. Contributions and AI assistance must be reported accurately. [Course plan](docs/COURSE_PLAN.md) · [AI-use log](docs/AI_USE_LOG.md).

## Final verification and team handoff

- [Current tasks and acceptance criteria](docs/FINAL_HUMAN_TODO.md).
- [14 November retry/release evidence](tests/evidence/2026-11-14-release-readiness/RESULTS.md).
- After installing `requirements-dev.txt`, run `python -m scripts.verify_local_workflow --output var/reproduction/my-check` (choose a new output directory). It starts an isolated local server with AI disabled, checks 16 real HTTP/storage/restart/restore scenarios, and leaves your existing album alone. Keep `result.json` and `server.txt`; record who actually ran it.
- To check local final files: install `requirements-submission.txt`, then run `python -m scripts.check_submission /path/to/final-files`. Add `--output /path/to/AILT9019_Group21.zip` only after the checks pass. It does not upload anything or verify YouTube playback/team participation.

- [16 November final closeout status](docs/FINAL_CLOSEOUT_STATUS.md): completed preparation, exact missing inputs and the 17 November deadline.
