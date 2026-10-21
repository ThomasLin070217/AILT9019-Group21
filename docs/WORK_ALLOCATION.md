# Travel Memory Map work allocation

**21 October update:** implementation and real course-model calls are now complete enough for independent acceptance. Use [current balanced English TODOs](TEAM_TODOS_2026-10-21.md) for immediate actions, review assignments and proposed internal deadlines. The September development plan below is historical and its pending-implementation statements are superseded by [current acceptance status](PRODUCT_ACCEPTANCE.md).

Development plan dated 30 September 2026 for four members. Thomas reports that the proposal has been submitted; its scope is our baseline. Assignments below reflect members' stated backgrounds, not a claim that everyone has already accepted their role. Raise availability or workload conflicts before 2 October. Update: Thomas’s map module and integration scaffolding are implemented with labelled fictional data; see [handoff and evidence](THOMAS_HANDOFF.md). Real backend/AI integration and the other modules remain planned.

Dates use Hong Kong / Shanghai time (UTC+8), 2026. Internal dates are team targets; Moodle controls course deadlines.

## Four owners

| Member | Stated background | Main responsibility | Concrete result |
| --- | --- | --- | --- |
| Thomas Yunian Lin | AI and Data Science plus AI and Humanities; basic Python/C++; AI-assisted coding | City map, integration and delivery coordination | Selectable map, correct brightness/counts, integrated workflow and release checklist |
| Angel Xinyue Li | AI and Data Science; basic Python/C++/JavaScript; simple mini-program experience | Upload and memory-card interface | Upload form, trip/card views, AI preview/edit/save controls and error states |
| Owen Ho Yeung Seto | Computer Science; Python/C++ | Local backend, photo storage and SQLite | Trip APIs, durable records, file handling, configuration and startup |
| Qingyang Lin | AI and Data Science; basic Python/C++ | AI generation and evaluation coordination | Cloud model adapter, travel prompt, structured results and five-case evidence report |

Use the proposal's local browser app, Python backend and SQLite as the starting architecture. Thomas and Angel choose a simple interface stack; Owen and Qingyang agree one backend framework by 2 October. No C++, model training or 3D component is needed. Every member builds a bounded module and can explain their own AI-assisted changes.

## Thomas owns the map and integration

- **2 Oct:** Agree the first city list/IDs with Owen, check map/city data permissions, and agree the map-to-card layout with Angel. Co-author the shared interface notes.
- **5 Oct:** Deliver a selectable 2D map and equivalent city list with sample data. Display exact saved-trip counts and brightness tiers of 1, 2–3 and 4+ visits. Selecting a city opens its separate trip cards.
- **8 Oct:** Integrate the frontend, backend and AI adapter. Run a real end-to-end walkthrough and coordinate fixes with module owners.
- Coordinate the **10 Oct** revised proposal, **26 Oct** mid-term and **20 Nov** final package. Own the project webpage outline and release checklist; each member still supplies their own code, report and demo work.

**Deliverables:** map component in `app/`, city/source manifest in `data/`, integration notes and a genuine end-to-end recording. **Acceptance:** another saved trip increases the same city's count; editing/retrying AI does not; reopening preserves trip history. Owen supplies counts from stored trip IDs.

**Reviewer/support:** Angel checks map/card interaction; Owen checks counts and persistence. Thomas prepares T01 and the problem/approach presentation segment.

## Angel owns the album interface

- **2 Oct:** Sketch city → photos → optional notes → saved card; agree field names with Owen and AI loading/error/clarification states with Qingyang.
- **5 Oct:** Build photo selection/preview, optional date/notes, trip cards and a city's trip list using sample responses. Keep repeated visits separate.
- **8 Oct:** Connect real storage and add Generate AI Memory, the pre-send notice, editable draft and explicit save action. Preserve typed notes and the saved trip when AI fails.
- Before the mid-term, maintain first-use screenshots/instructions and run a walkthrough with someone unfamiliar with the interface; record help needed.

**Deliverables:** form/card components in `app/`, first-use instructions and screenshots in `docs/`. **Acceptance:** save/reopen photos, edit AI title/text, and retry after failure without data loss or an extra visit. Provide labelled controls and text counts, not brightness alone.

**Reviewer/support:** Thomas checks the flow; Owen helps with API integration. Angel prepares T03 and contributes the accessibility report section and user-flow demo.

## Owen owns the backend and local data

- **2 Oct:** Draft schema and API request/response examples with Thomas and Qingyang. Define photo limits, validation and errors before frontend integration.
- **5 Oct:** Implement trip create/list/read/update, local photo files and SQLite persistence. Separate creating a trip from editing a card. Provide a minimal start command and sample configuration.
- **8 Oct:** Connect Qingyang's generator. Keep keys server-side, enforce current-trip-only payloads, strip metadata from outgoing image copies and preserve local records on API errors.
- Before **26 Oct**, verify a fresh setup on another member's computer, restart persistence, invalid-file handling and data-folder backup instructions.

**Deliverables:** backend/storage in `app/`, meaningful persistence/failure tests, credential-free `.env.example`, setup instructions. **Acceptance:** records survive restart; repeat trips stay separate; updates cannot increment visits; missing keys/timeouts do not lose data; outgoing requests contain no other trip.

**Reviewer/support:** Qingyang checks AI payloads; Thomas tests fresh setup. Owen prepares T02 and contributes architecture/reproducibility documentation and the technical demo segment.

## Qingyang owns AI generation and evaluation

- **2 Oct:** Compare a small number of cloud vision-language options for image support, access, privacy terms and cost. Try one non-sensitive sample if a team key is available; record access blockers honestly. Agree output fields with Owen and Angel.
- **5 Oct:** Build a standalone adapter and travel prompt for one trip's photos/city/notes. Return a title, short text and warning/clarification status. User facts take priority; photos add visible details; do not invent companions, landmarks or events.
- **8 Oct:** Integrate with Owen; handle malformed responses/timeouts and agree draft/clarification presentation with Angel. AI generation must be genuine, while basic album use remains independent of it.
- Before **26 Oct**, coordinate fixed fixtures, permission records, fact checklists and the complete five-case evaluation. Preserve raw outputs, failures, model settings and reruns, rather than replacing failures with human-edited successes.

**Deliverables:** adapter/prompt in `app/`, model decision note in `docs/`, safe fixtures/source manifest in `data/`, evidence index in `tests/`. **Acceptance:** response handling works; unsupported details are avoided or flagged; each case has a reproducible verdict. The submitted 5/5 target is a target, not an achieved score or a general accuracy claim.

**Reviewer/support:** Owen helps with Python/API integration; Thomas helps resolve scope/provider blockers. Qingyang prepares T04, coordinates shared T05, and contributes evaluation/limitations, AI risks and the failure-case demo.

## Shared interfaces by 2 October

Thomas has drafted [API_CONTRACT.md](API_CONTRACT.md) and implemented its map-side read adapter. Owen, Angel and Qingyang still need to review it; the actual backend routes are not implemented.

| Handoff | Owner → reviewers | Agreement required |
| --- | --- | --- |
| City catalogue → map/form/storage | Thomas → Angel, Owen | Stable city ID, label and coordinates; supported-city selection |
| Trip form → storage | Owen → Angel | Trip ID, city ID, optional date/notes, photo references; create versus update semantics |
| Trip → AI adapter | Owen → Qingyang | Current trip only; validated image copies, city and notes; no key in browser responses |
| AI → editor | Qingyang → Angel | Title/text, draft or clarification status, error shape; no automatic overwrite |
| Stored trips → map | Owen → Thomas | Count independent saved trip IDs; edits and AI retries never add visits |

Until integration, use matching checked-in non-personal sample JSON. Label mocks as mocks; they are not evidence of live AI. Interface changes require updating the examples and notifying the dependent owner.

## Five evaluation cases

| Case | Preparation owner | Condition | Two reviewers |
| --- | --- | --- | --- |
| T01 | Thomas | Clear photos and full notes | Angel, Qingyang |
| T02 | Owen | Photos/city with no notes | Thomas, Qingyang |
| T03 | Angel | Photos with brief notes | Owen, Thomas |
| T04 | Qingyang | Unclear/uninformative photos | Angel, Owen |
| T05 | All four; Qingyang coordinates | Clear conflict between photos and notes | Thomas, Owen |

Each fixture needs permitted photos, fictional non-personal notes, expected facts and forbidden inferences. Reviewers score unedited output independently and record disagreement/resolution. This is an internal feasibility evaluation, not an independent benchmark. See [Evaluation plan](../tests/EVALUATION_PLAN.md) for checks and evidence requirements.

## Milestones

| Date | Evidence due | Owner |
| --- | --- | --- |
| 2 Oct | Interface notes, city scope, model access/cost check and initial case specifications | Owen coordinates interfaces; all owners contribute |
| 5 Oct | Four small module demonstrations with matching sample inputs | Each module owner |
| 8 Oct | Real trip → AI draft → edited saved card workflow | Thomas coordinates; all owners fix defects |
| 9 Oct | Peer/consultation feedback and revised scope/evaluation | Qingyang consolidates; all review |
| 10 Oct | Revised anonymous proposal and submission receipt | Thomas coordinates submission |
| 23 Oct | Five-case results, fresh-setup check and mid-term evidence | Qingyang coordinates tests; Owen coordinates setup |
| 26 Oct | Mid-term package including genuine success/failure evidence | Thomas assembles; all verify |
| 13 Nov | Feature freeze, reruns, report sections and demo clips | Each module owner |
| 20 Nov | Webpage, code/setup, three-minute presentation plus demo, report and disclosures | Thomas coordinates; all review and explain their contributions |

Thomas coordinates the required consultation and Friday standup posting; each member supplies progress and blockers. This plan does not claim that any consultation is booked or update posted.

## Working rules and first actions

1. Use small feature branches and PRs stating the result, checks and remaining limitations. Have the named reviewer check the change before merge.
2. After a day blocked, record the specific blocker and ask the named support person. Rebalance if availability differs.
3. Every member supplies concrete product work, test evidence and a report/demo contribution. Log substantive AI assistance and actual human checks.
4. Never commit API keys, private photos/notes or chat screenshots. Only permission-cleared, non-sensitive demo fixtures belong in `data/`.
5. Preserve the submitted proposal; record subsequent design changes for the revised submission.

Start now: Thomas drafts city/map scope; Angel sketches the upload/card screen; Owen drafts the schema/API examples; Qingyang checks model access and drafts the five-case checklist. Thomas’s map checks are complete for the demo adapter; integration and actual AI testing remain to be done.
