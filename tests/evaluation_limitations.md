# System Evaluation & Known Limitations
Owner: Qingyang; 26 Oct integration status updated by Thomas
Mid‑term date: 26 Oct 2026

## Project mid‑term status
The integrated `main` build has the real local map‑album workflow, photo upload and SQLite persistence, alongside a separate fictional browser demo. Local backend and browser smoke checks passed; a fresh-machine check remains outstanding. Thomas's OpenAI-compatible Responses adapter is integrated and tested against simulated HTTP responses; a live provider call on this combined build remains outstanding. The earlier Qwen3‑VL‑Plus label is provisional; report the actual model used with each future run.
Fixture assets status：
- T01：complete
- T04, T05：added by Qingyang (data/fixtures/)
- T02：provisional synthetic-photo input prepared by Thomas; Owen review or replacement pending
- T03：Angel fixture added; AI output and independent review pending

> Real AI model outputs [PENDING‑TEAM‑AI‑RUN]. Evaluation statistics will be updated after team runs full test suite.

## Evaluation summary
Total planned test cases：T01,T02,T03,T04,T05 plus safety S01,S02
Pass / fail count：[PENDING‑TEAM‑AI‑RUN]

Representative raw AI output examples：
