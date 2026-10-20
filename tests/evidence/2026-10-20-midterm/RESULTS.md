# Mid-term reproducibility check — 20 October 2026

Tested commit: `c54cbc4` on `feat/thomas-city-map` before this documentation update. Use the README's **Mid-term check** steps with `?map=local`.

| Check | Expected | Actual |
| --- | --- | --- |
| Initial Osaka sample | Two distinct fictional trip cards and 2 visits | Pass: 2 cards, 2 visits |
| Add sample visit | New card and 3 visits | Pass: 3 cards, 3 visits |
| Edit text on new card | Updated text; count stays 3 | Pass |
| Reload | Card and count persist in the same browser profile | Pass |
| Domain unit tests | All pass | 13/13 passed on 20 October |
| Map configuration tests | All pass | 3/3 passed on 20 October |

The [output screenshot](workflow-output.png) comes from a fresh headless browser run of the same local server. The 16.52-second captioned MP4 in the team submission package records the live actions and reload check. Neither uses slides, personal data, notifications or API keys.

**Limits:** The new visit uses a test button and browser-local storage, not a user-uploaded photo or SQLite. The two bundled Osaka photos are credited examples; the generated test card has no photo. No cloud model is called, so this evidence makes no claim about AI response quality. Another team member has not yet reproduced the flow on a fresh computer. These items remain integration tasks.
