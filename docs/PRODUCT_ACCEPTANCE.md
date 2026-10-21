# Product implementation and acceptance record

20 October 2026. User authorized continuing through all remaining proposal features without individual review pauses. This is assistant verification, not independent teammate/human acceptance. The submitted proposal is unchanged. Existing branch name is unchanged; changes remain local for user review.

| Proposal capability | Implemented | Verification / remaining boundary |
| --- | --- | --- |
| 19-city 2D map, native/English search, Map/Album views | Yes | Existing map/album/view browser regressions pass; optional Google Maps live tests were not repeated |
| Real visit counts and 1 / 2–3 / 4+ brightness; separate repeat visits | Yes | Counts derive from saved trip IDs; edits, photo replacement and AI never create a visit |
| Upload photos, date and notes; view saved photos | Yes | Real byte validation, SQLite and local media; browser workflow and store reconstruction/restarts tested |
| Edit card text/date/memory and photos | Yes | Revision conflicts preserve drafts; stable identity; complete photo-set replacement |
| Confirmed delete | Yes | Transaction safety, tombstones, denied old photo URLs, count recalculation, restart and cleanup retry tests |
| Persistent local album and backup | Yes | Portable ZIP preview/merge/copy restore; checksum/path validation and rollback; complete-folder backup for larger albums |
| User-triggered current-trip AI and disclosure | Yes, integration | Real course Bailian Responses calls + browser consent/edit/save verified; simulated provider, stale-revision and privacy checks remain separate |
| Editable title/memory draft and explicit save | Yes, integration | Mock provider → unsaved draft → user edit → PATCH same trip; reload and failure retention tested |
| Unclear/conflicting inputs | Prompt and flow implemented | Mock clarification blocks generated-memory save; Real grey/conflict cases returned relevant clarification; independent human factual review pending |
| Album usable without key/provider and no record loss | Yes | Missing key, malformed/refused output, rate limit, timeout, failed storage and stale revisions tested |
| Five fixed factual-quality cases | Fixtures and runner ready | Five hashed public/synthetic cases; Real outputs collected for all five cases; final response types match5/5; two human factual reviews pending; no human 5/5 accuracy claim |
| README installation/reproduction | Yes, automated | Fresh Python3.13 virtual environment, pinned Pillow12.3.0 install and42 Python tests passed; another person's first-use acceptance remains pending |
| PNG card export / inclusive date filter / marker animation | Yes | PNG bytes + visual inspection, date rules, unchanged counts, reduced-motion and mobile checks |

## Observed checks

- `npm test`: **15 passed**.
- Fresh environment: `python -m unittest discover -s tests -p 'test_*.py'`: **42 passed**.
- Browser: map16 + album9 + views3 + create9 + edit8 + delete9 + product9 = **63 groups passed**; desktop and320/390px mobile; no uncaught browser errors.
- All five evaluation image hashes verified. The initial no-key attempts are historical. The course key was subsequently configured privately; final live results and earlier failed calls are now preserved under tests/evidence/product/bailian/.
- Batched visual review covered desktop album, mobile editing/AI disclosure and exported PNG. Cover clipping was fixed, then export/remaining UI confirmed once.
- `git diff --check` passes. `.env.ai.local`, local albums and `.context` evidence are Git-ignored; actual credentials are not in source.

Portable test receipts: [evidence](../tests/evidence/product/RESULTS.md). Detailed browser logs/screenshots and fresh-install logs are in `.context/final/`, `.context/final-*.log`, `.context/fresh-install.log` and `.context/fresh-tests.log` in this workspace.

## Real course-model evaluation follow-through

Bailian qwen3.8-flash is configured in private .env.ai.local. Five cases ran sequentially. Prompt versions v1–v3 exposed missing instruction propagation, planning-style responses, reasoning token exhaustion and invalid schema output. Version v4 places the task explicitly beside source data, uses JSON-object output plus server schema validation and disables reasoning for this short task. The final five cases match expected response types. Four additional live browser checks verified disclosure, generation, unsaved draft and explicit edited save with unchanged trip ID/count. See tests/evidence/product/bailian/RESULTS.md. Team members must still independently review raw outputs against the frozen facts. Partial reruns are supported with --case T01; prior evidence is never overwritten.

## Scope and practical limits

Single-user loopback app,19 preset cities; no3D, routing, social sharing, auto-classification or cloud sync. Photo limits/format conversion and ZIP limits are documented in README. There is no automatic backup/undo. Session text drafts are tab-scoped; chosen photo files need reselecting after reload. Provider retention/charges apply after explicit send; `store:false` is not a promise of zero retention. Final outputs have assistant factual triage; two independent human factual reviews remain pending.

Course-provider follow-up: 43 Python tests and15 JavaScript tests passed; integrated mock product regression9 groups passed again; real browser flow4 checks passed. The prior42-test fresh-environment run remains historical evidence.
