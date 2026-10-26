# Travel Memory Map evaluation plan

Updated 20 October 2026: all five cases are frozen in [cases.json](../data/evaluation/cases.json), with licensed public photos, fictional non-personal notes, one deterministic grey fixture, image hashes, required facts and forbidden inferences. Historical synthetic T01 remains a smoke fixture only. Real Bailian qwen3.8-flash evaluation has now run. The final travel-memory-v4 run returned the expected draft/clarification type for all five cases; two human factual-quality reviews remain pending. All failed earlier attempts are preserved with the final run in evidence/product/bailian/. Type matching is not a factual-quality acceptance verdict.

Run `python3 scripts/evaluate_ai.py` to validate hashes. After configuring the chosen provider, `python3 scripts/evaluate_ai.py --live` sends these five fixtures and saves raw responses/errors/usage/model/prompt provenance plus a blank two-reviewer CSV under `.context/ai-evaluation/<timestamp>/`. Each run has its own directory; prior outcomes are preserved. Status matching is only a mechanical check, never a factual accuracy pass. Two humans must score raw outputs independently. The proposal’s 5/5 target is a target, not an observed result.

## Fixed AI cases

| ID | Preparation owner | Input | Expected behaviour |
| --- | --- | --- | --- |
| T01 | Thomas | Clear photos and full notes | Preserve checklist facts in an editable title and short memory |
| T02 | Owen | Photos/city, no notes | Describe visible content without invented people, emotions or events |
| T03 | Angel | Photos and brief notes | Retain supplied facts without filling gaps with imagined details |
| T04 | Qingyang | Unclear/uninformative photos | Use supported facts only; request notes if a meaningful draft is impossible |
| T05 | Shared; Qingyang coordinates | Clear photo/note conflict | Flag conflict and request correction, without inventing a reconciliation or changing the saved city |

## Before running

Record each permitted photo’s source/licence or creator permission, fictional non-personal notes, known facts and forbidden inferences. Freeze the initial fixtures and prompt/model settings before collecting results. Do not commit private albums, credentials or screenshots of personal chats.

## Pass rules and evidence

Each case must preserve its pre-labelled facts, introduce no unsupported factual claims and handle uncertainty as specified. An appropriate clarification passes T04/T05. Score the raw output before human editing. Two reviewers independently check it, then record agreement or resolution. Preserve failures and reruns separately.

| Case/run | Commit | Model/settings and prompt version | Raw-output evidence | Facts retained | No invention | Uncertainty handled | Reviewer verdicts | Final result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Not yet run | — | — | — | — | — | — | — | — |

Report actual counts (for example, 4/5), edits required and failure details. Five internal cases cannot establish general accuracy; repeated runs of the same fixtures are not new independent test cases.

## Product checks using the same fixtures

| Check | Owner | Pass condition |
| --- | --- | --- |
| Save/reopen/restart | Owen | Photos, notes and edited cards persist |
| Repeat visits and brightness | Thomas | Independent trip IDs increase the city count; tiers are 1, 2–3 and 4+ |
| Edit/regenerate/retry | Angel | No accidental new visit or loss of typed/saved content |
| Missing key/timeout/malformed output | Owen and Qingyang | Clear error, no claimed AI success, local album remains available |
| Privacy payload | Owen and Qingyang | Request includes current trip only, no other album data; disclosure appears before sending |
| First-use and fresh setup | Angel and Thomas | Another person completes the documented sample workflow; record help needed |

Save actual outcome, date, commit and evidence for each check. A mock or an AI tool’s assurance is not test evidence. Complete initial results by 23 October so the team can review before the 26 October mid-term.
