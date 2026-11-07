# Travel Memory Map release checklist

Status reviewed on 6 November 2026. Check an item only when evidence exists for the integrated `main` build. Internal targets below are not course deadlines; Moodle controls submission requirements.

## Product and integration

- [x] FastAPI/SQLite trip creation, read, edit, deletion and sanitised photo upload are integrated with the browser UI.
- [x] Nineteen city outlines, search/list selection, saved-area highlights and repeat-visit tiers are present.
- [x] User-triggered AI route, pre-send disclosure, draft review, clarification/refusal and unchanged-trip error handling are implemented with simulated provider tests.
- [x] Repository is public and anonymously readable; the expired private collaborator invitation is no longer needed for read access.
- [x] 2 November isolated-browser smoke check covers one and two visits, photo, edit, reload and missing-provider failure; see [evidence](../tests/evidence/2026-11-02-thomas/RESULTS.md).
- [x] 6 November fake-provider browser and T01 fixture runs verify the integrated transport/UI path and saved-trip boundary; see [evidence](../tests/evidence/2026-11-06-ai-mock/RESULTS.md). This is not a live model quality result.
- [ ] Record one authorised live model call through the integrated route; identify model, prompt version, raw output and provider terms. Owner: Qingyang, with Thomas for access.
- [x] Owen reviewed and froze the synthetic T02 input on 6 November; its source, permission and checksum are recorded in [T02](../data/fixtures/T02/README.md).
- [ ] Complete T01–T05 live runs and two independent human verdicts per case. Owner: Qingyang, with all four reviewing.
- [ ] Fresh installation, restart, backup/restore and failure checks on another member's computer. Owner: Owen.
- [ ] Current-build first-use, mobile and keyboard check with evidence. Owner: Angel.

## Final deliverables · official date 20 November

- [x] Public repository link and a static project webpage source with a genuine local workflow recording.
- [x] GitHub Pages serves `main:/docs` at https://thomaslin070217.github.io/AILT9019-Group21/; include this URL in the final package.
- [ ] Three-minute presentation plus genuine demo recording, showing success, one limitation/failure and what was learned. Owners: all; Thomas coordinates.
- [ ] Report within five pages plus appendix, including Ethics & AI-use disclosure and actual—not proposed—evaluation results. Owners: all; Thomas assembles.
- [ ] Confirm consultation and standup record from course systems. Owner: Thomas.
- [ ] All four review the final artifacts against Moodle's final instructions and retain submission receipt. Owner: all.

Internal target: follow the [dated AI milestones](AI_CHECKPOINTS_2026-11-06.md), freeze a tested version by 17 November and complete a team review by 19 November.
