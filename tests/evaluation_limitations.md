# System Evaluation & Known Limitations
Owner: Qingyang
Mid‑term date: 26 Oct 2026

## Project mid‑term status
Front‑end map‑album prototype is functional with browser‑side fictional demo trips.
Photo upload and SQLite persistence are implemented in Owen's integration branch and passed an isolated local API smoke check on the combined build. A fresh-machine and full browser check remain outstanding. Thomas's OpenAI-compatible Responses adapter has now been ported into this backend and tested against simulated HTTP responses; a live provider call on the combined build remains outstanding. The earlier Qwen3‑VL‑Plus label is provisional; report the actual model used with each future run.
Fixture assets status：
- T01：complete
- T04, T05：added by Qingyang (data/fixtures/)
- T02：pending Owen contribution
- T03：Angel fixture added; AI output and independent review pending

> Real AI model outputs [PENDING‑TEAM‑AI‑RUN]. Evaluation statistics will be updated after team runs full test suite.

## Evaluation summary
Total planned test cases：T01,T02,T03,T04,T05 plus safety S01,S02
Pass / fail count：[PENDING‑TEAM‑AI‑RUN]

Representative raw AI output examples：
