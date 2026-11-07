# Integrated AI path review · 6 November 2026

Initial baseline: public `main` at `12ac90b`; the browser test was rerun successfully on 7 November after updating to `fab0e38` (Owen’s T02 review). This review used a local fake Chat Completions provider, an isolated temporary SQLite/media directory, fictional text and synthetic fixture images. **No cloud model, personal photo or real credential was used.** The fake response proves transport and UI behaviour, not writing quality or the five-case acceptance target.

## Defect found and fixed

The documented `python -m scripts.run_ai_fixture T01 --confirm-send` command previously failed before any request because `scripts/run_ai_fixture.py` imported a missing `PROMPT_VERSION` from `backend.ai.responses`. The adapter now defines `chat-completions-v1`; the runner stores both that label and a SHA-256 hash of the exact system prompt with each response. Its `--help` command and a complete fake-provider T01 run now work.

## What ran

- `python -m pytest -q`: **63 passed**.
- `npm test`: **22 passed**.
- `node tests/integrated-ai.e2e.mjs`, with Playwright, Chrome and the repository's Python dependencies available: **passed**. The self-contained script starts an isolated backend and a loopback fake provider, tests the browser, then stops both. In this macOS environment, `NO_PROXY=127.0.0.1,localhost` was needed for the backend's HTTP client to reach the loopback provider rather than the system proxy. The script sets it only for its spawned test backend.
- `python -m scripts.run_ai_fixture T01 --confirm-send` against a loopback fake provider: **HTTP 200**; exactly one `/v1/chat/completions` call containing the two T01 synthetic images; the saved trip was unchanged. The [unedited mock result](cli-T01-result.json) includes model, prompt version/hash and empty `human_reviews`.

## Browser assertions

The [repeatable browser script](../../integrated-ai.e2e.mjs) verified that the current-trip disclosure lists city, title, notes and photo count; Cancel causes zero provider calls; explicit Send causes one; the provider request contains the selected Osaka trip and one prepared JPEG, with no text from a separate Tokyo trip. The returned title and memory text appear in an editable form while the database still holds the original trip. Only **Save reviewed draft** persists the result, and it survives reload. No browser page error was recorded. See [machine result](results.json), [draft before save](draft-before-save.png) and [saved after reload](saved-after-reload.png).

## Still required for a course evaluation claim

1. Obtain an authorised vision-model key and review provider terms. No such key was present in either the clean review worktree or the existing local checkout on 6 November.
2. Confirm permissions for the five fixtures. Owen reviewed and froze T02 on 6 November after this mock run; T03's public-repository consent does not cover transfer to a cloud provider.
3. Run T01–T05 through the integrated route with the actual model, preserve raw outputs and record two independent human verdicts per case. Report the actual count, including failures and unrun cases.
4. Recheck a real provider's request format, image limits, cost and retention policy. The fake provider does not validate those external properties.
