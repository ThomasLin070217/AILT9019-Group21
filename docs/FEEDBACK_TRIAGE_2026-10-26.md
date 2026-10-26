# Group feedback triage — 26 October 2026

Original teammate records remain unchanged: [Angel's first-use test](ANGEL_USABILITY_TEST.md) and [Qingyang's consolidated reviews](../tests/consolidated_test_reviews.md). This note checks their observations against `main` after the integration merge.

| Feedback | Current assessment | Evidence / next step |
| --- | --- | --- |
| Angel: creating a memory was hard to discover in the fictional demo | Resolved in API mode. The visible **Add a memory** form opens the real local workflow. | Angel's 26 October desktop/mobile follow-up in her test record. |
| Qingyang: live AI output and human scoring are missing | Still open. The Responses adapter is integrated and has simulated HTTP tests, but no live model result on this combined build is recorded. | Run approved synthetic cases through `main`, retain raw output and two independent reviews; do not report a pass rate yet. |
| Qingyang: outbound cloud payload not yet verified live | Still open. Backend tests cover the selected-trip payload with a fake provider; this does not prove a live cloud request. | Verify provider configuration, permissions and the actual outbound payload before an approved live run. |
| Qingyang: possible demo `localStorage` loss on hard refresh | Unconfirmed. The existing browser regression explicitly reloads the fictional demo and checks its saved edits; no reproducible loss case is recorded. | Ask for browser/storage/reproduction steps if it recurs. |
| Qingyang: Google Maps needs a local key file | Expected optional setup, not a product defect. | The bundled local map and the default OpenFreeMap view work without a Google key. |
| Angel: map keyboard guidance | Improved on `main`: the map now visibly explains Tab, Enter and Space selection on desktop. | Check with a keyboard-only first-time user. |
| Frontend AI timeout versus backend budget | Fixed on `main`: the browser now waits 75 seconds against the backend's 60-second default budget, allowing the server's result or timeout response to arrive. | A live provider run is still needed to assess model latency and output. |

This triage does not convert pending evaluation work into a claimed pass. T02 remains missing; T01, T03, T04 and T05 inputs are present, but the five-case model run and human scores remain pending.
