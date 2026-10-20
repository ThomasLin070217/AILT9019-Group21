# AILT9019 — Group 21

## Project status

We are building **Travel Memory Map**: a local travel album with city markers, separate cards for repeat visits, and user-triggered AI memory writing from the current trip’s photos and notes.

Thomas reported on 30 September 2026 that the proposal was submitted. The [proposal baseline](proposal/Travel_Memory_Map_Proposal.docx) is preserved for the 10 October revision; the Moodle receipt has not been independently checked here. Thomas’s city-map module is now runnable with fictional demo data. Photo uploads, the SQLite backend and real cloud AI integration remain planned.

**Start with the [four-person work allocation](docs/WORK_ALLOCATION.md)** for owners, deliverables, review partners and deadlines. Thomas owns map/integration, Angel owns the interface, Owen owns backend/storage, and Qingyang owns AI/evaluation.

## Run the city map

```bash
python3 serve.py
```

Open **http://127.0.0.1:8019/app/**. Python 3.10+ is sufficient; no API key or npm installation is needed. Switch between **Map** and **Album** to explore a place or see its photo cards side by side. Select a city, search by English/Chinese name, and open **Try visit counting** to add/edit fictional demo visits. The first two Osaka cards show credited example photos; click a cover to view it. Unsaved sample drafts survive city changes and reloads within the tab. Browser demo storage is not the planned real backend. No photos or notes are sent to a cloud service by this prototype. Google Maps is optional: see [local key setup](docs/GOOGLE_MAPS_SETUP.md). With a configured key, Map view uses Google’s online tiles and custom city markers; `?map=local` uses the offline map.

Run `npm test` with Node.js 20+ for the map logic/storage checks. See [Thomas handoff](docs/THOMAS_HANDOFF.md) for browser checks and [API contract](docs/API_CONTRACT.md) for teammate integration. API mode (`/app/?mode=api`) requires Owen’s backend and never substitutes demo data when it fails.

### Mid-term check: reproduce the working path

1. Run `python3 serve.py` and open **http://127.0.0.1:8019/app/?map=local** in a fresh browser profile. No API key or package installation is needed.
2. Osaka starts with **2 fictional trips**. Expand **Try visit counting**, then choose **Add a sample visit**. The app saves a third independent trip in browser-local storage; Osaka now shows **3 visits** and a third card.
3. Choose **Edit sample text** on the new card, type a short fictional memory, and save. The text changes but the visit count remains **3**. Reload the page: both the card and count remain. **Reset sample album** restores the starting data.

This is a real running input → local processing → output path for the map and album prototype. It uses fictional test data. Photo upload, SQLite persistence and cloud AI generation are **not yet implemented**; the browser demo does not prove those proposed functions. The [20 October test record](tests/evidence/2026-10-20-midterm/RESULTS.md) gives the observed result and limits.

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
- [Team guide](docs/TEAM_GUIDE.md): current scope and collaboration workflow.
- [Proposal baseline and revision notes](proposal/README.md): the submitted draft and next revision.
- [Evaluation plan](tests/EVALUATION_PLAN.md): how we will define a real pass, failure, and safe refusal.
- [AI-use log](docs/AI_USE_LOG.md): record prompts, changes, and verification as we work.
- [Friday standup](docs/FRIDAY_STANDUP.md): the required three-line weekly update format.

## Repository structure

```text
proposal/     Proposal drafts, diagrams, and peer-review notes
app/          Application source code
data/         Public, synthetic, or self-curated project data only
tests/        Test cases and evaluation evidence
docs/         Project webpage and supporting documentation
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

Connect a real photo upload and saved trip to the city album, then add current-trip-only AI drafting with review and explicit save. The [shared API contract](docs/API_CONTRACT.md) describes the existing map handoff; teammates still need to approve and implement the backend and AI routes.
