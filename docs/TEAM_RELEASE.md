# Team review release — 21 October 2026

The integrated local album and course-model workflow are published for review in [draft PR #3](https://github.com/ThomasLin070217/AILT9019-Group21/pull/3), targeting main. The PR is not merged and is not a course submission. Teammates with accepted repository access can fetch the review branch now; their own installation/acceptance checks are still required.

- Review branch: `ThomasLin070217/thomaslin070217/explore-local-files`.
- Tested application source commit: `a144ad984100d5249b6ed656fa6a5f92129f5d5c`.
- The follow-up handoff commit adds review/status documents and LF line endings for CSV review templates. Raw provider outputs and application code are unchanged.
- Use the current head of the review branch for the complete documentation. Record `git rev-parse HEAD` in your own review.

## Get and run the same version

For an existing local clone with no uncommitted changes:

```bash
git fetch origin
git switch --track origin/ThomasLin070217/thomaslin070217/explore-local-files
git rev-parse HEAD
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 serve.py --port 8020
```

If you already have that local branch, switch to it and pull with `git pull --ff-only` instead of creating another tracking branch. Keep your own work before switching. A fresh clone can use:

```bash
git clone --branch ThomasLin070217/thomaslin070217/explore-local-files https://github.com/ThomasLin070217/AILT9019-Group21.git
cd AILT9019-Group21
```

Then follow the environment/startup commands above. Windows activation and further limits are in [README](../README.md). Open `http://127.0.0.1:8020/app/?mode=local&map=local` on your own computer. The localhost address on Thomas's computer is not a remotely hosted team demo.

The local album works without a model key. For live AI, configure the group's course credential privately in your own Git-ignored `.env.ai.local`, using the Bailian endpoint/model in `.env.example`. Obtain the credential through the group's existing private channel; it is not included in this branch, PR or screenshots. No credential was sent to teammates by this handoff.

## Verification

```bash
npm test
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/evaluate_ai.py
```

Observed assistant results: 15 JavaScript tests, 43 Python tests and 68 browser/integration groups passed (63 existing browser groups plus five recorded map checks). Playwright setup and optional browser commands: [handoff](THOMAS_HANDOFF.md). `evaluate_ai.py` without `--live` checks fixture hashes without spending quota. Review existing outputs before requesting any rerun.

## Review and demonstration materials

- [Balanced English team TODOs](TEAM_TODOS_2026-10-21.md).
- [Thomas verification and T02/T05 assistant assessments](reviews/thomas.md): human sign-off is still pending; T02 omits required greenery.
- [Portable test evidence and genuine map recording](../tests/evidence/2026-10-21-thomas/RESULTS.md).
- [Thomas's 243-word section and 100-word speaking script](midterm/THOMAS_SECTION.md).
- [Three-minute presentation outline and separate demo runbook](midterm/PRESENTATION_OUTLINE.md).
- [Issue register](midterm/ISSUE_REGISTER.md) and [course/access audit](midterm/COURSE_REQUIREMENTS_CHECK.md).
- [Friday standup draft](midterm/STANDUP_2026-10-23_DRAFT.md), prepared but not posted.

The map video uses real form/API/SQLite operations, licensed public photos and fictional trips. Its text-update step is manual and makes no AI call. The earlier real AI browser receipt is preserved separately; the mock regression suite is explicitly labelled. Do not present any assistant review as two humans' factual acceptance, or this silent map recording as someone's spoken contribution.

## Ready-to-forward team message

> The runnable review version is now available in draft PR #3. Please fetch the review branch above and record your commit ID. Start with the balanced English TODO list, complete your assigned tests and independent case reviews by 22 October at 22:00, and submit your section/segment by 23 October at 22:00 (proposed team deadlines, UTC+8). Model keys stay private. Report the actual result and any reproducible issue; no need to rerun the paid API unless investigating a specific problem. Thomas's technical verification, script and map recording are ready; independent human acceptance and current Moodle submission confirmation remain pending.

This message is a draft for Thomas to forward. No chat/email/Ed message, review request or assignment submission has been sent automatically.
