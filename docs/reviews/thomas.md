# Thomas verification package —21 October2026

Prepared by Codex with AI assistance at Thomas's request. The executable checks below were actually run by the assistant. The T02/T05 assessments are assistant drafts for Thomas, not Thomas's personal sign-off or an independent/blind human review. The assistant has seen earlier triage. Human-review CSV cells remain pending.

Application source commit: `a144ad984100d5249b6ed656fa6a5f92129f5d5c`. The subsequent handoff commit adds status/review documents and normalizes review-template CSV line endings; the scored model outputs are unchanged.

## Environment and actual checks

macOS; Python3.13.7; Node24.11.1; Pillow12.3.0; Playwright1.62.1; installed Google Chrome. Tests use isolated temporary albums and permitted public fixture photos with fictional notes. No personal album or new real model request was used in this verification round.

| Check | Command / evidence | Observed result |
| --- | --- | --- |
| Logic and date/storage invariants | `npm test` |15 passed |
| Python storage/HTTP/AI adapter/backup | `python3 -m unittest discover -s tests -p 'test_*.py'` |43 passed |
| Frozen fixture integrity | `python3 scripts/evaluate_ai.py` | All five fixtures and photo hashes verified; no live request |
| Map / album / view browser regressions | `tests/browser.e2e.mjs`, `album.e2e.mjs`, `views.e2e.mjs` |16+9+3 groups passed |
| Real trip create / edit / delete | Corresponding trip browser scripts |9+8+9 groups passed; stable identity and restart behaviour verified |
| Integrated product workflow | `tests/product.e2e.mjs` |9 groups passed; provider explicitly simulated |
| Recorded local map integration | `scripts/record_map_walkthrough.mjs` |5 groups passed against real local form/API/SQLite |
| Secret/path exclusion | Scan staged file bytes against configured AI/Maps keys and reject private-data paths | No configured keys, local albums or attachments included |

Portable receipts and video: [verification evidence](../../tests/evidence/2026-10-21-thomas/). Detailed screenshots and diagnostic logs stay in `.context/thomas-release/`. The first concurrent edit-suite attempt stalled and was interrupted without claiming a pass. Bounded waits/failure capture were added; a clean standalone confirmation completed all8 edit checks with exit0. The interrupted-attempt note is retained. Review-template CSV CRLFs were normalized to LF without changing cells so the complete branch passes Git whitespace checks.

Browser setup follows [THOMAS_HANDOFF.md](../THOMAS_HANDOFF.md); set PLAYWRIGHT_MODULE/CHROMIUM_EXECUTABLE as appropriate. Map/album/view scripts use a running local preview at BASE_URL; other scripts create their own temporary backend.

## Map/count walkthrough

1. Open a disposable local album; Osaka starts at0 visits/tier0.
2. Submit four separate trips through the actual photo form: counts0→1→2→3→4 and tiers0→1→2→2→3; four independent cards appear.
3. Edit an existing title: same four trip IDs, four cards and tier3.
4. Save manually reviewed memory text through the real PATCH route: same trip ID/count. This demonstrates the update invariant, not model generation. A separate earlier live AI browser receipt verifies generation/draft/edit/save.
5. Confirm four deletions: counts4→3→2→1→0 and tiers3→2→2→1→0, returning to the empty state.
6. The recorder observed no uncaught browser errors and cleaned up its temporary album.

The public fixture remains credited under data/demo-covers/SOURCES.json. Recording: [genuine map walkthrough](../../tests/evidence/2026-10-21-thomas/walkthrough.webm). It has no narration; Thomas's speaking script is prepared separately.

## T02 — assistant assessment for Thomas

Inputs: Osaka selected; no date/notes; one licensed photograph showing a multi-tiered building, green roofs, extensive greenery, pond/reflection and stone lantern. See frozen [case definition](../../data/evaluation/cases.json) and [unaltered raw output](../../tests/evidence/product/bailian/20261020T085202128355Z/T02.json).

Output title: `Osaka Castle View`.

Output memory: “A multi-tiered castle structure with white walls and green roofs is visible in the distance. The building is reflected in a calm pond, which features a stone lantern on its bank.”

| Criterion | Assistant finding |
| --- | --- |
| Expected response type | draft received; correct |
| Required facts | Partial. Multi-tiered building is retained. The explicit required detail `greenery` is absent; green roofs do not describe greenery |
| Unsupported factual claims | No clear unsupported personal event, companion, feeling, restaurant or date. Building/walls/roofs/reflection/lantern are visible. The title names the recognizable landmark but is not geographic visit verification |
| Uncertainty handling | No future-itinerary or missing-date questions; appropriate for a clear image |
| Provisional recommendation | **Fail completeness / needs review** under the frozen all-required-facts rule. This is a case-level omission, not an application crash or evidence of general inaccuracy |
| Thomas personal verdict / second reviewer | Pending Thomas and Qingyang. Do not count this assistant draft as either independent human review |

This is stricter than the earlier assistant summary, which described visible content but did not flag the omitted required greenery. Preserve that earlier record and this correction. Resolve any intended rubric interpretation explicitly; do not change frozen facts after seeing the answer to manufacture a pass.

## T05 — assistant assessment for Thomas

Inputs: Osaka selected; a building/pond/garden photo; notes assert only snow-covered mountains and no buildings. [Raw output](../../tests/evidence/product/bailian/20261020T085202128355Z/T05.json).

The output returns clarification, leaves title and memory empty, identifies the building-versus-snowy-mountain contradiction and asks whether the wrong photo was uploaded or the notes should be corrected. It introduces no reconciling travel story, silently accepted snow claim or saved-city change.

| Criterion | Assistant finding |
| --- | --- |
| Required facts | All three: flags contradiction, asks for correction, empty title/memory |
| Unsupported reconciliation | None observed |
| Uncertainty/conflict handling | Correct clarification rather than an invented draft |
| Provisional recommendation | Pass for this raw response, pending independent human confirmation |
| Thomas personal verdict / second reviewer | Pending Thomas and Qingyang |

No aggregate human pass rate is assigned. Five expected response types matched in the final run; factual completeness and two-human acceptance are separate.

## Integration and delivery handoff

- [Thomas section and speaking script](../midterm/THOMAS_SECTION.md):243 written words and100 spoken words, approximately45 seconds before rehearsal.
- [Three-minute group outline and separate demo runbook](../midterm/PRESENTATION_OUTLINE.md): four timed slots; missing teammates' actual clips are marked pending.
- [Issue register](../midterm/ISSUE_REGISTER.md): owners, evidence, targets and closure criteria; includes the T02 omission.
- [Course/access audit](../midterm/COURSE_REQUIREMENTS_CHECK.md): local official PDF checked; accepted teammate accounts verified; course invitation still pending; no authenticated current Moodle/Ed evidence.
- [Standup draft](../midterm/STANDUP_2026-10-23_DRAFT.md): three lines prepared, not posted.

Thomas still needs to personally confirm the independent review, rehearse/record his speech, verify current Moodle/Ed and consultation records, and obtain the course account holder's access acceptance. Other members' own-device checks, human verdicts and presentation contributions remain theirs.
