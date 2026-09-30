# T01 initial fixture

Thomas's first normal-input fixture is ready as two original, non-personal **synthetic visual cards**, fictional Osaka notes and an explicit fact checklist in `case.json`. No API has been called and no result has been scored.

The first PNG contains blue/red squares, the second a green circle. They are deliberately graphics, not travel photos or proof of location. This small fixture tests whether a vision model preserves user-supplied facts and avoids turning unrelated visual content into invented travel events. It cannot validate realistic travel-photo understanding; before final evaluation, the team should either keep and declare this narrow scope or replace the images with licensed non-sensitive real photos, update the checklist, and freeze the revised case before testing.

The original geometric image assets are dedicated under CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/ . Rebuild with `scripts/build_t01_fixture.py` and Pillow if needed; committed PNGs are ready to use. Source hashes are in `case.json`.

Assigned reviewers: Angel and Qingyang. Save the model name/settings, prompt version, raw output, checks, edits required and verdict when the real AI adapter is available. Do not label an edited draft as the raw model answer.
