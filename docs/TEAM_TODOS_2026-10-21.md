# Team TODOs — Mid-term Check on 26 October

Updated: 21 October 2026. This is a proposed allocation for team confirmation. All times are Hong Kong / Shanghai time (UTC+8). Internal deadlines below are suggested team targets; Moodle remains authoritative for course requirements.

The core application is implemented, including local photo storage, SQLite, trip editing/deletion, backup/restore, map counts and AI draft review/save. Real Bailian qwen3.8-flash outputs exist for all five evaluation cases. Our next step is independent verification, fixes and presentation evidence. Each member must personally run their checks, understand the relevant code and accurately record their contribution and AI assistance.

## Balanced allocation

Each member owns one verification package, independent AI reviews, a short written section and one presentation segment. Thomas and Owen have two AI reviews each because release coordination and installation/storage checks involve more work. Angel and Qingyang have three each. The ten reviews cover all five cases twice without assigning a case to the same person twice.

| Member | Main verification package | AI reviews | Written / presentation contribution |
| --- | --- | --- | --- |
| Thomas | Shared release, map behaviour and integration | T02, T05 | Problem, overall workflow and final material assembly |
| Angel | User flow, mobile usability and one first-time user trial | T01, T03, T04 | Quick-start / usability section and interface walkthrough |
| Owen | Fresh installation, persistence and backup/restore | T03, T04 | Architecture / reproduction section and storage demonstration |
| Qingyang | AI failure handling, privacy and evaluation consolidation | T01, T02, T05 | Evaluation / limitations section and AI clarification demonstration |

**Dependency:** the latest implementation is currently in Thomas's local working tree. Thomas must first share the runnable branch and commit ID. Everyone should test that same commit, rather than assume the current main branch contains the latest work. The existing raw evaluation files can be reviewed as soon as they are shared; they do not require additional paid API calls.

## Thomas — Release and integration

- [ ] **By 21 October: share the runnable version.** Prepare and push the review branch, excluding credentials, personal albums and chat attachments. Share the branch, commit ID and README startup instructions. Handle course-key configuration privately. Done when all three teammates can retrieve the same version.
- [ ] **By 22 October, 22:00: verify the map and review T02 / T05.** Check separate repeat-visit cards, exact counts, brightness at 1 / 2–3 / 4+ visits, unchanged counts after edits/AI saves, and reduced counts after deletion. Record steps, actual results and independent AI scores in `docs/reviews/thomas.md`.
- [ ] **By 23 October, 22:00: prepare the integration section.** Write approximately 200–300 words on the problem and overall workflow, plus a roughly 45-second presentation segment. Assemble the four members' existing sections/clips into the shared outline; assign each blocking defect to its module owner rather than fixing everything yourself. Check Moodle requirements, submission/access arrangements and outstanding course-administration items. Deliver the shared issue list and presentation outline.

## Angel — User flow and usability

- [ ] **By 22 October, 22:00: test the interface and review T01 / T03 / T04.** On your own device, select a city, upload two permitted non-sensitive photos, enter notes/date, save, view photos, generate a draft, edit it, explicitly save and refresh. Check a narrow/mobile layout, keyboard labels, cancellation and photo replacement. Confirm the displayed visit count remains correct. Record screenshots, reproducible issues and independent AI scores in `docs/reviews/angel.md`.
- [ ] **By 23 October, 22:00: run one brief first-time user trial.** Ask someone unfamiliar with the app to follow the README with permitted test data. Record where help was needed and the actual outcome. Produce a one-page quick-start guide with screenshots; keep the trial bounded to the core workflow.
- [ ] **By the same deadline: prepare the usability section.** Write approximately 200–300 words on interaction/accessibility and the observed trial, plus a roughly 45-second interface walkthrough. Fix interface defects from your package and ask the original reporter to retest.

## Owen — Installation and local data

- [ ] **By 22 October, 22:00: install from scratch and review T03 / T04.** Follow the README on your own computer; create the virtual environment, install requirements and run `npm test` plus `python3 -m unittest discover -s tests -p 'test_*.py'`. Record OS/Python/Node versions, commit ID, commands, outputs and independent AI scores in `docs/reviews/owen.md`. Done when the documented setup works without Thomas operating your computer.
- [ ] **By 23 October, 22:00: verify persistence and recovery.** Use a disposable test album. Check records/photos after restarting, ZIP backup restored into a separate empty data directory, identical imports skipped and conflicting imports kept separate. Check PNG export and date filtering against saved records. Record actual results; correct setup/storage defects and have the reporter retest. Do not use a personal album for destructive tests.
- [ ] **By the same deadline: prepare the technical section.** Write approximately 200–300 words explaining browser → Python → SQLite/local photos, backup/restore and the difference between creating and updating a trip. Prepare a roughly 45-second technical demonstration, and patch README steps where your installation exposed gaps.

## Qingyang — AI behaviour and evaluation

- [ ] **By 22 October, 22:00: verify AI failure handling and review T01 / T02 / T05.** Check the pre-send disclosure, current-trip-only payload, editable unsaved draft and explicit save. Use controlled missing-key/provider-failure checks with test data to confirm saved trips remain available and no extra visit appears. Confirm the key is absent from browser responses/logs. Record evidence and independent AI scores in `docs/reviews/qingyang.md`.
- [ ] **By 23 October, 22:00: consolidate the ten independent reviews.** For each case, retain both reviewers' original scores and reasons, then record disagreements and their resolution. Link inputs, raw outputs, expected facts, unsupported details and final verdicts. Preserve earlier failed runs and model/prompt settings. Report the actual accuracy result; matching the expected response type is not automatically a factual-quality pass. Chase missing reviews, but do not write another person's verdict.
- [ ] **By the same deadline: prepare the AI section.** Write approximately 200–300 words on evaluation, limitations, privacy and AI use, plus a roughly 45-second clarification/failure demonstration. Use existing real outputs where possible. Explain what changed across prompt versions and what remains uncertain. Rerun only a specific case when needed, sequentially, preserving every attempt and respecting the shared course quota.

## Independent AI review assignments

Frozen inputs and photo sources: [cases.json](../data/evaluation/cases.json). Final raw run: [travel-memory-v4](../tests/evidence/product/bailian/20261020T085202128355Z/).

| Case | Input condition | Two independent reviewers | Raw output |
| --- | --- | --- | --- |
| T01 | Clear photos and full notes | Angel, Qingyang | [T01.json](../tests/evidence/product/bailian/20261020T085202128355Z/T01.json) |
| T02 | Clear photo, no notes | Thomas, Qingyang | [T02.json](../tests/evidence/product/bailian/20261020T085202128355Z/T02.json) |
| T03 | Photo and brief notes | Angel, Owen | [T03.json](../tests/evidence/product/bailian/20261020T085202128355Z/T03.json) |
| T04 | Uninformative grey image | Angel, Owen | [T04.json](../tests/evidence/product/bailian/20261020T085202128355Z/T04.json) |
| T05 | Photo/notes conflict | Thomas, Qingyang | [T05.json](../tests/evidence/product/bailian/20261020T085202128355Z/T05.json) |

Read the original images, fact checklist and unedited raw output before scoring. Do not read the assistant's factual triage until your independent first draft is recorded. Put your scores in your own `docs/reviews/<name>.md`; Qingyang consolidates them afterward.

For each assigned case, record:

| Case | Required facts retained? | Unsupported details, with exact examples | Uncertainty/conflict handled correctly? | Pass/fail and reason | Reviewer/date |
| --- | --- | --- | --- | --- | --- |
| Assigned case | Pending | Pending | Pending | Pending | Pending |

A relevant clarification can pass T04/T05. The three normal-photo cases should produce grounded text. Evaluate the original model response, not a human-edited version. Five internal cases cannot establish general accuracy.

## Shared deadlines and completion criteria

- **22 October, 22:00:** each member submits an initial verification record, assigned independent AI reviews and reproducible issues. Report blockers when they occur, not only at the deadline.
- **23 October, 22:00:** each member submits their remaining verification evidence, 200–300-word section and roughly 45-second presentation segment. The four segments form the draft three-minute presentation; check any separate demo requirements against Moodle.
- **24 October, 22:00:** module owners fix blocking defects; original reporters retest and record the result. Keep follow-up work with the relevant owner.
- **25 October:** rehearse the full workflow together, check consistency across materials and stop nonessential feature additions.
- **26 October:** complete the mid-term check/submission according to Moodle's actual instructions.

Each person delivers a reviewable record/PR, personally performed verification and their written/presentation contribution. Label unfinished work as unfinished and failures as failures. Never fabricate trial participants, reviews, results or individual contributions. Raise workload or availability problems early so the team can rebalance.
