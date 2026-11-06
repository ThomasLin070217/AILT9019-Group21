# T02 provisional photo-only fixture

This case tests whether the AI can describe **visible content with no user notes** without inventing a trip story. The city is set to Osaka by the user; the image itself does not identify Osaka.

`park-bench.png` was generated with OpenAI's built-in imagegen tool on 26 October 2026. Thomas prepared it so the five-case suite is structurally complete. Owen reviewed the fixture on 6 November 2026 and accepted it as the final T02 input: the SHA-256 matches `case.json`, the PNG carries no EXIF or metadata chunks, and the image shows no people, readable text, watermark or identifiable landmark. The case is frozen for evaluation; authorship of the image remains Thomas's, per `source.creator` in `case.json`.

Generation prompt: “Create one realistic candid travel photo of an ordinary park path in an unidentifiable East Asian city: a wooden bench beside a small pond, several green trees, stone paving, soft overcast daylight. No people, signs, text, recognizable landmark or watermark.”

The image contains no real people or personal travel data. It is a synthetic test image, not proof of an actual trip. The committed checksum is in `case.json`; no cloud AI output or human score has been recorded. OpenAI's terms state that, as between OpenAI and the user and to the extent permitted by law, the user owns generated output. This fixture is published for course-project review; it is not separately licensed for unrelated reuse. See https://openai.com/policies/row-terms-of-use/.
