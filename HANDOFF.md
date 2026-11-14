# AILT9019 Group 21 · Team and agent handoff

Updated **14 November 2026**. Start from the public [`main` branch](https://github.com/ThomasLin070217/AILT9019-Group21/tree/main), not a member's older feature branch. Live-AI fixes were tested at code commit `a95a108`, based on main `fa673fc`. Check for newer commits before starting. The [project webpage](https://thomaslin070217.github.io/AILT9019-Group21/) explains the product and shows a short recording; the **working album runs locally**, not on that webpage.

## What the product does now

A user chooses one of 19 supported cities, saves a trip with a title and optional notes, uploads photos, and gets a separate editable memory card for each visit. Saved trips persist in local SQLite and media storage. The map lights an approximate city area at one visit, brightens it at two to three visits, and brightens it again at four or more. Editing an existing card does not create another visit. The browser also has a fictional, no-backend demo mode; use **API mode** when testing the real integrated workflow.

The optional **Write with AI** action shows the selected trip's city, date, title, notes and sanitised photo count before confirmation. The backend adapter uses an OpenAI-compatible **Chat Completions** endpoint, although its configuration name is still `AI_PROVIDER=responses`. With no provider configured, it returns an honest error and leaves the saved card unchanged. **Real Qwen generation, review/save and restart persistence were verified on 14 November.** T01/T02/T04/T05 and S01/S02 have live outputs. T03 cloud permission/run and all independent human scores remain pending. See [live evidence](tests/evidence/2026-11-14-live-ai/RESULTS.md). A 6 November local fake-provider browser and T01 fixture run verified the full transport/UI path; see [evidence](tests/evidence/2026-11-06-ai-mock/RESULTS.md) and [dated milestones](docs/AI_CHECKPOINTS_2026-11-06.md).

## Reproduce the current local workflow

From the repository root, with Python 3.10+:

```bash
python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python3 -m backend
```

Open `http://127.0.0.1:8019/app/?mode=api&map=local`. Use fictional notes and the synthetic `data/fixtures/T02/park-bench.png`; do not use someone's personal photos for a routine smoke test. Create a trip, upload the image, edit, reload, and add a second trip to the same city. Back up `var/travel.db` and `var/media/` together. More setup and AI configuration details are in [Quick start](docs/QUICK_START.md) and the [backend guide](docs/BACKEND.md). Never commit credentials or runtime albums.

## Verified evidence and its limits

- On 2 November, Thomas's isolated API-mode run passed **7 browser checks** covering first and second visits, photo upload, editing, reload persistence, AI disclosure/no-provider behaviour and 390px overflow. [Script](tests/final-workflow.e2e.mjs) · [commands, captures and limitations](tests/evidence/2026-11-02-thomas/RESULTS.md).
- **68 Python tests** and **22 Node tests** passed on the 14 November code. These are software checks, not human ratings of AI writing.
- The published webpage loaded on desktop and a 390px mobile viewport; its HTML, CSS, images and recording were reachable. The page is a project presentation, not a hosted multi-user album.
- The five evaluation inputs T01–T05 exist; **Owen reviewed and froze T02 on 6 November**. Live outputs now exist for four original cases and two safety cases; independent verdicts remain missing. Public consent for T03's photo does **not** establish permission to send it to a cloud model.
- The map areas are approximate display footprints, not exact administrative boundaries or proof that a trip occurred. Fresh-computer setup, physical-device usability and backup/restore have not yet been independently recorded.

## Who does what next

The weekend completion target is **15 November, 23:00 HKT** (internal, not a
Moodle deadline). Do not add new features while closing these evidence gaps.

| Owner | Deliverable | Internal deadline / acceptance |
| --- | --- | --- |
| Qingyang | Review retained live outputs, arrange two independent verdicts per case, coordinate T03 permission/run with Angel | 15 Nov 16:00: rubric and actual result table; no assistant-only verdict presented as human scoring |
| Owen | Fresh-machine install, restart, backup/restore and meaningful failure check; review assigned AI cases | 15 Nov 12:00: commands, environment and restored trip/photo evidence; AI reviews by 16:00 |
| Angel | Desktop/phone/keyboard checks and blocking fixes; explicit T03 cloud-transfer decision; final recording | Tests/permission by 15 Nov 12:00; AI reviews by 16:00; recording by 21:00 |
| Thomas | Integrate verified fixes and evidence, check final Moodle requirements, assemble report/page/recording script | Code freeze and report draft by 15 Nov 18:00; complete package by 22:00 |
| All four | Review actual contributions, results, report and recording | 15 Nov 23:00: final internal sign-off |

The course overview lists **20 November 2026** for final deliverables; Moodle
controls the actual format/time. This work did not submit anything to Moodle.
School-key expiry in the supplied email is 19 November. Keep it private.

## Working rules for the next change

1. Pull the newest `main` and make a focused branch/PR. Note the baseline commit and do not overwrite someone else's unmerged work.
2. Keep test inputs fictional or permission-cleared. Keep keys in ignored local environment files; never put them in screenshots, recordings, issues or Git history.
3. Record what actually ran, the commands, exact result and a limitation. Do not turn a proposed check into a claimed pass.
4. Update [AI-use log](docs/AI_USE_LOG.md), [release checklist](docs/RELEASE_CHECKLIST.md) and this handoff when the evidence changes.

### Context to paste into another agent

> We are AILT9019 Group 21 building Travel Memory Map. Use the public `ThomasLin070217/AILT9019-Group21` repository and start from current `main` (live verification code commit `a95a108`). The working app is local FastAPI + SQLite at `/app/?mode=api&map=local`; the GitHub Pages site is a presentation. One saved trip creates one city card and lights an approximate city area; repeat trips create separate cards and brighter tiers. Photos are sanitised and stored locally. The optional AI adapter uses Chat Completions under the legacy setting `AI_PROVIDER=responses`. Real Qwen live outputs and browser review/save/restart were verified on 14 November; T03 permission/run and independent human scores remain pending. Read tests/evidence/2026-11-14-live-ai/RESULTS.md, including the retained original T04 failure and all reruns. Do not report 6/6 response-type checks as 5/5 human accuracy. Read `HANDOFF.md`, `docs/RELEASE_CHECKLIST.md`, `docs/BACKEND.md`, and `tests/EVALUATION_PLAN.md` before changing claims. Work on a focused branch, use fictional/cleared test material, keep keys private, and attach commands plus observed results to your PR. Ask the member which assigned deliverable they own, then work toward its acceptance evidence and internal date.
