# Live Bailian course API verification — 20 October 2026

Provider: Alibaba Cloud Bailian Token Plan, course Group21. Model: qwen3.8-flash. Protocol: OpenAI-compatible Responses. The user authorized configuring the supplied course API for this application. Actual credentials are stored only in Git-ignored .env.ai.local (mode600); no key appears here. Inputs are licensed public images, a generated grey fixture and fictional notes. Calls were sequential and limited to integration/evaluation; no personal album was sent.

## Attempts preserved

| Run | Prompt | Observed result |
| --- | --- | --- |
|20261020T084808435358Z|v1|T01/T02/T04 returned results; T03/T05 exhausted the reasoning/output limit; some clarification text incorrectly planned future travel |
|20261020T084958751804Z|v2|Five responses collected after explicit system delivery and reasoning.effort=none; T02 still requested planning details, T03 embellished feelings and T04 asked future-itinerary questions |
|20261020T085102381892Z|v3|Explicit task text beside sources improved T02/T04/T05; T01/T03 returned an invalid empty-array result, rejected locally |
|20261020T085144191977Z|v4, T01 only|JSON-object mode plus local schema validation returned a valid short factual draft |
|20261020T085202128355Z|v4, all five|All five parsed successfully and matched expected draft/clarification types |

Failures and reruns are separate evidence, not hidden or counted as additional independent cases. The final adapter keeps metadata-free current-trip inputs, store:false, no tools/history and no automatic retry. OpenAI still uses strict schema; the course gateway uses explicit task text and JSON-object output with the same local validator. The short drafting task disables Qwen reasoning because the default reasoning consumed the limited output budget in the first run. Provider retention is not inferred from store:false.

## Final-run assistant factual triage

| Case | Expected/actual | Assistant observation | Human reviewers |
| --- | --- | --- | --- |
|T01|draft/draft|Retains Osaka/date/walk/photo/rest facts; added building/reflection details are visible in the fixture | Pending two independent reviews |
|T02|draft/draft|Impersonal description of building/roofs/walls/water/lantern; no invented companion/activity | Pending two independent reviews |
|T03|draft/draft|Retains Osaka/walk/photograph and describes visible building details, without invented feelings/date | Pending two independent reviews |
|T04|clarification/clarification|Recognizes the grey placeholder and requests clearer photo or factual completed-trip notes | Pending two independent reviews |
|T05|clarification/clarification|Flags snowy-mountain versus building conflict and asks for input correction | Pending two independent reviews |

**5/5 expected response types is a mechanical result, not a human factual-quality score.** Assistant triage above is a single assistant review. The blank review.csv remains blank/pending for two real reviewers. Five internal fixtures do not demonstrate general accuracy. Raw provider Responses, parsed results/errors, token usage and prompt/model/source provenance are preserved in each run directory.

## Real browser check

browser-results.json records four additional checks using the real configured API: provider/model disclosure before explicit send; uploaded public photo produces an editable draft; the draft does not modify SQLite; editing then explicitly saving retains the same trip ID and one visit. The test uses a temporary album removed afterward. Screenshot: local .context/bailian-live/ai-live-draft.png. It is a genuine provider response, unlike the separate simulated regression suite.

Official references: [Model catalogue/service information](https://help.aliyun.com/zh/model-studio/token-plan-team-overview), [Responses parameters and reasoning](https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-responses). Course-use authorization, shared-credit restrictions and expiry come from the user-supplied teaching-team notice; no private notice/key is copied into this repository.
