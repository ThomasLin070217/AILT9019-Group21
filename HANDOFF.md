# AILT9019 Group 21 · Team and agent handoff

Updated **2 November 2026**. Start from the public [`main` branch](https://github.com/ThomasLin070217/AILT9019-Group21/tree/main), not a member's older feature branch. The reviewed baseline for this handoff is merge commit `fbd88d6`. Check for newer commits before starting. The [project webpage](https://thomaslin070217.github.io/AILT9019-Group21/) explains the product and shows a short recording; the **working album runs locally**, not on that webpage.

## What the product does now

A user chooses one of 19 supported cities, saves a trip with a title and optional notes, uploads photos, and gets a separate editable memory card for each visit. Saved trips persist in local SQLite and media storage. The map lights an approximate city area at one visit, brightens it at two to three visits, and brightens it again at four or more. Editing an existing card does not create another visit. The browser also has a fictional, no-backend demo mode; use **API mode** when testing the real integrated workflow.

The optional **Write with AI** action shows the selected trip's city, date, title, notes and sanitised photo count before confirmation. The backend adapter uses an OpenAI-compatible **Chat Completions** endpoint, although its configuration name is still `AI_PROVIDER=responses`. With no provider configured, it returns an honest error and leaves the saved card unchanged. **No live cloud result or five-case AI score has been verified on the integrated build.**

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
- **63 Python tests** and **22 Node tests** passed locally. These are software checks, not human ratings of AI writing.
- The published webpage loaded on desktop and a 390px mobile viewport; its HTML, CSS, images and recording were reachable. The page is a project presentation, not a hosted multi-user album.
- The five evaluation inputs T01–T05 exist, but **T02 is provisional** until Owen reviews it. Raw live-model outputs and independent verdicts are missing. Public consent for T03's photo does **not** establish permission to send it to a cloud model.
- The map areas are approximate display footprints, not exact administrative boundaries or proof that a trip occurred. Fresh-computer setup, physical-device usability and backup/restore have not yet been independently recorded.

## Who does what next

| Owner | Deliverable and internal target | Acceptance evidence |
| --- | --- | --- |
| **Owen Seto** · 9 Nov | Review/freeze T02; run installation on another computer, restart, backup/restore and one meaningful failure case. | Exact commands, machine/environment, observed results and any fixes in a PR or linked evidence file. A restored trip and photo must be visible. |
| **Xinyue (Angel) Li** · 11 Nov | First-use review of current `main` on desktop and phone; keyboard check and priority UI fixes; clarify separate cloud-transfer permission for T03 if needed. | Task notes, viewport/device, screenshots or recording, issue list and retest. Record permission decision explicitly; do not infer it from GitHub-publication consent. |
| **Qingyang Lin** · 14 Nov | Confirm a permitted vision model/provider, make one authorised live call through the integrated route, then run T01–T05 and arrange two independent verdicts per case. | Provider/model, prompt version, request settings, raw redacted outputs, rubric, reviewer verdicts and a calculated result. Mark unrun or disputed cases as pending. |
| **Yunian (Thomas) Lin** · 16 Nov | Assemble the webpage/repository links, actual evaluation findings, report draft and three-minute presentation plan; verify consultation and Ed standup records. | A final package draft with source links, contribution/AI-use disclosure and a claim-to-evidence check. The current short smoke recording is not the final presentation. |
| **All four** · 17 Nov freeze; 19 Nov review | Freeze tested code and review the final artifacts against Moodle. | All four approve accurate contribution and result statements; final recording and report are checked before submission. |

The course overview lists **20 November 2026** for final deliverables. Moodle's actual final submission page controls the required format and deadline. The [release checklist](docs/RELEASE_CHECKLIST.md) tracks remaining gates; the [final-delivery outline](docs/FINAL_DELIVERY_HANDOFF.md) contains a presentation timeline and report structure.

## Working rules for the next change

1. Pull the newest `main` and make a focused branch/PR. Note the baseline commit and do not overwrite someone else's unmerged work.
2. Keep test inputs fictional or permission-cleared. Keep keys in ignored local environment files; never put them in screenshots, recordings, issues or Git history.
3. Record what actually ran, the commands, exact result and a limitation. Do not turn a proposed check into a claimed pass.
4. Update [AI-use log](docs/AI_USE_LOG.md), [release checklist](docs/RELEASE_CHECKLIST.md) and this handoff when the evidence changes.

### Context to paste into another agent

> We are AILT9019 Group 21 building Travel Memory Map. Use the public `ThomasLin070217/AILT9019-Group21` repository and start from current `main` (this handoff was based on `fbd88d6`). The working app is local FastAPI + SQLite at `/app/?mode=api&map=local`; the GitHub Pages site is a presentation. One saved trip creates one city card and lights an approximate city area; repeat trips create separate cards and brighter tiers. Photos are sanitised and stored locally. The optional AI adapter uses Chat Completions under the legacy setting `AI_PROVIDER=responses`. No integrated live AI result or five-case human score is verified. Read `HANDOFF.md`, `docs/RELEASE_CHECKLIST.md`, `docs/BACKEND.md`, and `tests/EVALUATION_PLAN.md` before changing claims. Work on a focused branch, use fictional/cleared test material, keep keys private, and attach commands plus observed results to your PR. Ask the member which assigned deliverable they own, then work toward its acceptance evidence and internal date.
