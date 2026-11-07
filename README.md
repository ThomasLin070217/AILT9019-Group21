# Travel Memory Map · AILT9019 Group 21

Travel Memory Map is a local travel album. A person selects one of 19 supported cities, saves a trip and optional photos/notes, and sees that city light up on the map. A return visit creates a separate card; the city highlight has distinct tiers for 1, 2–3 and 4+ saved trips. The map is a visual record of user-entered trips, not proof of travel.

The integrated product is on `main`. It uses FastAPI, SQLite and a browser interface. Photos are re-encoded before local storage to remove location/camera metadata. **Write with AI** is optional and user-triggered: the interface shows the selected trip fields before requesting a draft, and the draft must be reviewed and saved separately. The provider setting is named `AI_PROVIDER=responses` for compatibility, but the current adapter uses an OpenAI-compatible **Chat Completions** endpoint. No live provider result or five-case score on this integrated build is claimed yet.

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
- [6 November AI integration check](tests/evidence/2026-11-06-ai-mock/RESULTS.md): browser and fixture path against a local fake model, including consent, selected-trip privacy, editable draft and save. This is not a live-model quality result.
- [Evaluation plan](tests/EVALUATION_PLAN.md): T01–T05 and the human-review rules. The five live outputs and independent scores are still pending.
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
