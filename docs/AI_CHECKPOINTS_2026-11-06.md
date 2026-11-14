# AI integration and final check milestones

## Current update · 14 November 2026

The live-cloud gate is complete: school qwen3.8-flash, retained raw outputs,
request/privacy evidence, browser draft/review/save/restart and a safe missing-key
failure. See [live results](../tests/evidence/2026-11-14-live-ai/RESULTS.md).
The original T04 JSON failure was fixed and retained. Final automatic response
checks are 6/6; the original-case coverage is 4/5 and human scores are pending.
T03 has not been sent without separate cloud-transfer permission.

**Revised internal finish: Sunday 15 November, 23:00 HKT.**
- By 12:00: Owen supplies fresh-machine/restore evidence; Angel supplies usability evidence and the T03 permission decision.
- By 16:00: Qingyang coordinates the remaining permitted run and two independent reviews per case; all four provide their assigned verdicts.
- By 18:00: Thomas freezes tested code and prepares the report draft.
- By 21:00: Angel and Thomas finish the genuine three-minute recording.
- By 22:00: Thomas assembles the final package; all four review by 23:00.

These are internal targets. Moodle remains authoritative for submission. The
old 17/19 November internal targets below are retained as history, not current
instructions. No teammate completion is inferred from an elapsed deadline.

## Original planning context

The mid-term feedback says the demo already joins the travel map, trip records and photo uploads, and asks us to verify the integrated AI path and set short-term milestones. This page tracks that next stage; status was refreshed on **7 November** after Owen’s T02 review. Dates below are **proposed internal targets in Hong Kong time (UTC+8)**, not Moodle deadlines; the team should record any change to an owner or date. The course overview lists **20 November 2026** for final deliverables; verify the live Moodle instructions before packaging.

## Historical evidence at 7 November

The local app uses FastAPI, SQLite and an optional Chat Completions adapter (`AI_PROVIDER=responses`). On 6 November, the documented fixture runner's missing prompt-version import was fixed. A fake-provider browser run verified disclosure → explicit confirmation → current-trip request → editable unsaved draft → user save → reload. A fake-provider T01 fixture run also produced an unedited response with the prompt hash. [Exact evidence](../tests/evidence/2026-11-06-ai-mock/RESULTS.md). **At that checkpoint, no authorised live cloud call or human-rated five-case result existed.** The app works without AI, but this does not satisfy the remaining AI evaluation task.

## Original targets (superseded by weekend closeout)

| Internal target | Owner | Deliverable | Acceptance evidence / fallback |
| --- | --- | --- | --- |
| **9 Nov, 18:00** | Qingyang + Thomas | Choose a permitted vision provider and review request format, image limit, expected cost and retention. Owen signed off T02 on 6 Nov. | Provider/model and terms link in the project record; [T02 input review](../data/fixtures/T02/README.md) already recorded. If no key is available, record the access blocker and who is seeking it, rather than claiming a live test. |
| **11 Nov, 21:00** | Qingyang + Thomas | Run one permission-cleared case (start with synthetic T01) through the actual integrated route. Angel completes desktop/phone first-use and keyboard checks and records whether T03 can be sent to that provider. | HTTP status, model, prompt version/hash, unedited output, confirmation that saved trip stayed unchanged, and first-use observations. If T03 transfer is not permitted, replace it with a cleared fixture **before** freezing the five-case set. |
| **14 Nov, 20:00** | Qingyang coordinates; all four review | Run the frozen T01–T05 set and collect two independent verdicts for each case. Owen supplies fresh-computer, restart and backup/restore evidence. | Raw output per run; rubric marks for fact retention, unsupported claims and uncertainty; reviewer agreement/resolution; actual pass count and failures. Never score a mock response or an edited draft as the live model's output. |
| **16 Nov, 21:00** | Thomas | Assemble a draft report and three-minute presentation using only completed results. | Repository and webpage links, genuine system footage, actual evaluation table, contribution record, Ethics & AI-use disclosure and stated limits. |
| **17 Nov freeze; 19 Nov review** | All four | Freeze a tested version and review final files against Moodle. | Version/commit and test log; four-member check of claims, recording, report and submission format. |

## Acceptance rule for the AI path

A live integration result requires a permitted real model, the user's explicit per-trip confirmation, only that trip's sanitised images and fields in the provider request, a valid `draft`/`clarification`/`refusal` response, and no automatic change to the saved card. A draft is retained only after the user reviews and saves it. The five-case evaluation additionally requires raw outputs and two independent human verdicts per case; the proposal's **5/5** target is a target, not a measured score.

Use [the evaluation plan](../tests/EVALUATION_PLAN.md) for fixture rules and [the backend guide](BACKEND.md) for local configuration. Keep real keys and private outputs in ignored local files. If a target slips, update this table with the observed blocker, owner and next verifiable step.
