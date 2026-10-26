# Travel Memory Map evaluation plan

Status on 26 October 2026: the five AI cases remain unrun against a live cloud model on the integrated build. T01, T03, T04 and T05 inputs are prepared; T02 now has a provisional synthetic-photo fixture prepared by Thomas pending Owen’s review. Thomas’s separate map-module tests are recorded in [map evidence](evidence/MAP_RESULTS.md). Preserve the submitted proposal’s five-case set and proposed **5/5** acceptance target. Four members prepare one case each; the conflict case is shared. Ownership and reviewers are in [Work allocation](../docs/WORK_ALLOCATION.md).

## Fixed AI cases

| ID | Preparation owner | Input | Expected behaviour |
| --- | --- | --- | --- |
| T01 | Thomas | Clear photos and full notes | Preserve checklist facts in an editable title and short memory |
| T02 | Owen (Thomas prepared provisional asset) | Photos/city, no notes | Describe visible content without invented people, emotions or events |
| T03 | Angel | Photos and brief notes | Retain supplied facts without filling gaps with imagined details |
| T04 | Qingyang | Unclear/uninformative photos | Use supported facts only; request notes if a meaningful draft is impossible |
| T05 | Shared; Qingyang coordinates | Clear photo/note conflict | Flag conflict and request correction, without inventing a reconciliation or changing the saved city |

## Before running

Record each permitted photo’s source/licence or creator permission, fictional non-personal notes, known facts and forbidden inferences. Freeze the initial fixtures and prompt/model settings before collecting results. Do not commit private albums, credentials or screenshots of personal chats.

For a configured provider, run one approved case through the **integrated API** from the repository root:

```bash
.venv/bin/python -m scripts.run_ai_fixture T01 --confirm-send
```

This creates an isolated temporary album, uploads only that case's image(s), calls the current AI route once, checks that the saved trip did not change, and writes the unedited app response to Git-ignored `var/evaluation/`. Run T02/T04/T05 the same way after reviewing their synthetic inputs. T03 uses Angel's real photo and additionally requires `--allow-angel-photo` **only after** the team confirms her permission covers the chosen provider and reviews its retention terms. The script refuses to run without local provider configuration. It does not supply a human score or prove general model accuracy.

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
