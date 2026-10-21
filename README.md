# AILT9019 — Group 21

The current runnable review branch is published in [draft PR #3](https://github.com/ThomasLin070217/AILT9019-Group21/pull/3). See [team release instructions](docs/TEAM_RELEASE.md) for the tested source, startup and remaining acceptance tasks.

Travel Memory Map saves completed trips as a local photo album. Each trip is one visit; repeated trips get separate cards and change the city marker brightness (1 / 2–3 / 4+ visits). The catalogue has 19 cities with English/Chinese search, Map/Album views and a bundled map. [Proposal](proposal/Travel_Memory_Map_Proposal.docx) · [Product acceptance record](docs/PRODUCT_ACCEPTANCE.md)

## Install and run

Requires Python 3.10+ and pip. Node.js 20+ is only needed for JavaScript tests. The Python dependency is pinned in `requirements.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 serve.py --port 8020
```

Open **http://127.0.0.1:8020/app/?mode=local&map=local**. The server binds to this computer only. If the port is in use, choose another port. On Windows activate with `.venv\Scripts\activate`. Mac users can also double-click `start.command` after installing Python.

1. Select a city, choose **Add a trip**, upload 1–5 photos, enter a date/title/notes and save.
2. Open each saved photo. Add another trip to the same city to increase visits.
3. **Edit trip** changes text/date/saved memory; **Edit photos** replaces the complete photo set. Neither adds a visit. The first photo is the cover.
4. **Delete trip** requires explicit confirmation. It removes this visit and its stored photo copies. Original source photos are untouched.
5. Restart the server: records and photos remain. Date filters affect displayed cards, while map counts continue to reflect all saved trips. Undated cards have an explicit toggle.
6. **Export PNG** downloads a local image of the saved card. Map marker changes animate briefly; reduced-motion preferences disable the animation.

Photos: still JPEG/PNG/WebP only, up to 5 MB each, 20 MB total, 25 megapixels each. HEIC/animated images are rejected. Stored copies are oriented JPEGs with metadata removed, at most 4096 px on the longer edge; originals remain unchanged. Titles allow 200 characters; notes and saved memories allow 5,000 each. Text drafts survive same-tab reloads; selected photo files must be reselected after closing/reloading the page.

## Storage and backup

Real records live in Git-ignored `.local-album/album.sqlite3`; photos live in `.local-album/media/`. Browser clearing does not delete them. Use `--data-dir /absolute/path/to/album` for another private directory, outside served `app/` and `data/`. This is a single-user local application, with revision checks against concurrent edits.

Open **Backup & restore album** in the local album. Download a ZIP, choose it to preview, then confirm import. Identical records are skipped. Conflicting IDs are never overwritten: explicitly choose to import conflicts as new trips (which adds visits), or cancel. Deleted records in an older backup also require the explicit copy option. Corrupt archives are rejected; failed imports roll back new records/files.

ZIP limits: 100 MB compressed, 200 MB expanded, 500 trips. For larger albums, stop the server and copy the **entire** data folder (database and media together) to another disk; restore that complete folder while the server is stopped. ZIPs contain your photos and notes: keep them private. API keys are excluded. A ZIP is not an automatic/offsite backup; losing the data folder and all backups loses the album. Deletion has no undo. If the OS temporarily blocks file cleanup, deleted/obsolete media is inaccessible; refreshing retries cleanup.

## Optional AI memory drafts

The current workspace uses the course-sponsored **Alibaba Cloud Bailian Token Plan**, model **qwen3.8-flash**, through its OpenAI-compatible Responses endpoint. Real generation, all five frozen cases and the browser draft/edit/save workflow have now run. Final-run response types match all five expectations; two independent human factual reviews are still pending. OpenAI remains an alternative provider.

Configure `.env.ai.local` at the repository root (Git-ignored). The course key has already been configured privately in this workspace; it is never included in source:

```dotenv
TRAVEL_AI_PROVIDER=Alibaba Cloud Bailian (course Group 21)
TRAVEL_AI_BASE_URL=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
TRAVEL_AI_MODEL=qwen3.8-flash
TRAVEL_AI_API_KEY=your-own-api-key
```

Use a model that supports image inputs and structured outputs. The app reads configuration for each request; no restart is needed. Never commit the file or reuse editor/Conductor credentials. Dedicated `TRAVEL_AI_*` environment variables override the file. [Bailian model catalogue](https://help.aliyun.com/zh/model-studio/token-plan-team-overview) · [Responses parameters](https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-responses). To use OpenAI instead, set provider=OpenAI, base URL=https://api.openai.com/v1 and a compatible model such as gpt-4.1-mini with your own OpenAI key. Keys and endpoints are provider-specific.

On a saved trip choose **Generate AI memory**. Review the provider/model, endpoint and exact trip text before **Send & generate**. Only this trip’s selected city, date, notes and all current photo copies (fresh metadata-free JPEGs up to 1024 px) are sent. No other trips, saved AI memories or original metadata are sent. The request uses `store:false`; this does not guarantee zero provider retention. The current course interface consumes the shared Group 21 credits. The supplied teaching-team notice authorizes course-app use and states this key expires on 19 November 2026; avoid high concurrency. Provider retention and account terms apply. [Bailian service information](https://help.aliyun.com/zh/model-studio/token-plan-team-overview). If using OpenAI, consult its separate [data policy](https://developers.openai.com/api/docs/guides/your-data).

AI output remains an **unsaved editable draft** until **Save reviewed memory**. Clarification results ask for better notes/photos or correction and cannot be saved as a generated story. Timeouts, missing keys, malformed results and provider failures leave saved records intact. Retry is manual. The model can still make factual mistakes: check every draft against the supplied evidence. Session drafts survive same-tab reloads; stale revisions require reconciling the saved trip before saving again.

## Demo and maps

`/app/` remains the clearly labelled fictional demo, separate from the real album. `/app/?mode=api` reads the backend without demo writes. Use `?mode=local&map=local` for the full real workflow without external map services. Google Maps is optional; [setup](docs/GOOGLE_MAPS_SETUP.md). The local path uses bundled map data/fonts and makes no cloud request until you explicitly send an AI request.

## Verify

```bash
npm test
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/evaluate_ai.py
# Only after configuring your key; sends five public fixtures, may incur API charges:
python3 scripts/evaluate_ai.py --live
```

The five frozen cases, source licences, hashes, facts and forbidden inferences are in `data/evaluation/cases.json`. The live runner records raw responses, parsed drafts, usage, model/prompt version and a two-reviewer CSV under `.context/ai-evaluation/`. No human verdicts are filled automatically. See [evaluation plan](tests/EVALUATION_PLAN.md) and [browser test setup](docs/THOMAS_HANDOFF.md). Mock API checks establish workflow behaviour, not real AI factual quality. Real course-model attempts, including failed earlier runs, are preserved in tests/evidence/product/bailian/. See [live run notes](tests/evidence/product/bailian/RESULTS.md). The course gateway uses explicit task text and JSON-object output with server-side schema validation; the OpenAI route retains strict JSON-schema output. qwen3.8-flash reasoning is disabled for this short drafting task to avoid spending the output budget on reasoning alone.

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
