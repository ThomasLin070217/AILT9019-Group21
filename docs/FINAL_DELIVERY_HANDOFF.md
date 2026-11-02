# Final delivery working outline · 2 November 2026

This is a coordination draft for the four-person team, not a claim that final artifacts are already complete. The course overview lists **20 November 2026** for final deliverables; verify the Moodle submission page before packaging. Internal freeze: **17 November**; four-person review: **19 November**.

## Thomas's prepared material

- Public-repository README, quick start, backend, release and current handoff documentation have been aligned to the integrated build.
- The project webpage source is `docs/index.html`. It presents the problem, actual app screenshots, a recorded synthetic local workflow, setup, evidence and explicit limits. Hosting/accessible URL still needs a final check.
- The browser smoke script and retained evidence are in `tests/final-workflow.e2e.mjs` and `tests/evidence/2026-11-02-thomas/RESULTS.md`. The integrated run passed seven browser checks; 63 Python and 22 Node checks also passed locally.

## Three-minute presentation structure

| Time | Content | Evidence to show |
| --- | --- | --- |
| 0:00–0:25 | User problem and single task | One city visit becomes a retrievable trip memory; no claim of verified travel |
| 0:25–1:35 | Genuine system workflow | Select city → save card → add synthetic photo → edit → second card and brighter area → reload |
| 1:35–2:10 | Optional AI and boundary | Show explicit current-trip disclosure and editable result **only if a permitted live call is evidenced**; otherwise show the honest no-provider state |
| 2:10–2:40 | Evaluation | Present actual T01–T05 outcomes only after raw outputs and independent verdicts exist; otherwise state tested local workflow and outstanding AI evaluation |
| 2:40–3:00 | Limits and next step | Approximate city areas, local storage, provider/data permission and an evidence-backed next step |

Record an actual application window and keep private data, notifications and credentials out of frame. A final three-minute recording still needs to be made; the webpage's 13-second smoke recording is source footage, not the final presentation.

## Report structure (five pages maximum before appendix)

1. Background: named user, one task, pain point and a modest value hypothesis.
2. Pipeline: input, local trip/photo storage, map rendering, current-trip AI confirmation, Chat Completions adapter, editable draft and failure path.
3. Evaluation: method, T01–T05 raw model results and two independent reviews per case when available; distinguish software checks from AI quality judgments.
4. Distribution/accessibility: public repository and webpage URL, fresh setup on another computer, keyboard/mobile findings and known limitations.
5. Ethics and AI-use disclosure: photo permission and metadata stripping, cloud transfer/retention, hallucinated memories, injection handling, and the actual team use of coding assistants.

## Inputs needed before Thomas can assemble final artifacts

- **Owen, by 9 Nov:** review T02 and provide fresh-machine, restart and backup/restore records with exact commands/results.
- **Angel, by 11 Nov:** current-build desktop/mobile first-use and keyboard evidence; separate permission if the T03 photo is ever sent to a cloud model.
- **Qingyang, by 14 Nov:** permitted model/provider details, one authorised live integrated call, raw T01–T05 outputs and two independent verdicts for each case. Report any cases not run as pending.
- **All four, by 19 Nov:** review the report and presentation against Moodle, verify contributions, and approve exact claims. Thomas packages the repository/page links and final files after that review.
