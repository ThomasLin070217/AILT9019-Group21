# Integrated product verification — 20 October 2026

Automated checks and assistant visual review only; independent human acceptance and live model factual-quality results are not claimed.

| Check | Observed outcome |
| --- | --- |
| JavaScript logic/date/storage |15 tests passed |
| Python store/HTTP/AI adapter/backup/photo changes |42 tests passed in a freshly installed virtual environment |
| Map browser |16 groups passed |
| Album browser |9 groups passed |
| View/responsive browser |3 groups passed |
| Real create/edit/delete browsers |9/8/9 groups passed |
| Integrated product browser |9 groups passed, simulated Responses provider only |
| Frozen model inputs |Five cases and image hashes verified |
| Live OpenAI |Subsequently configured Bailian course key; five final real responses collected, earlier failures preserved |
| Raw model output and two human reviewers |Raw outputs collected; two human verdicts pending; no human verdict fabricated |
| Whitespace |git diff --check passed |

Runtime: macOS, Python3.13.7, Node24.11.1, pinned Pillow12.3.0, Playwright1.62.1 and installed Google Chrome. Browser suite data is temporary public/synthetic test content; it is isolated from the user's `.local-album`. Python dependencies installed via requirements.txt into `/tmp/travel-fresh-venv` for the fresh setup check. No new npm runtime dependency.

Reproduction and commands: [README](../../../README.md), [browser setup](../../../docs/THOMAS_HANDOFF.md), [acceptance matrix](../../../docs/PRODUCT_ACCEPTANCE.md). Local detailed evidence is intentionally Git-ignored under `.context/final/`; the product contract receipt is copied alongside this record. Screenshots display public fixture photos/fictional text, not personal travel records. The image-export review caught and fixed cover overflow into the city label; final export was visually confirmed.

Follow-up live configuration and results: [Bailian run record](bailian/RESULTS.md). Python tests increased to43 after adding the course-adapter contract check; four real browser checks were added. The original63 browser groups remain the simulated/local regression baseline.
