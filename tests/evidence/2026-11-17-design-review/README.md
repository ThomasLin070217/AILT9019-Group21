# Travel Memory Map design review

The comparison uses the same Osaka sample album and bundled map on the baseline `8f85a87` and the local design branch. The desktop viewport is 1440×900 and the emulated phone viewport is 390×844. The 320×740 layout also passed a horizontal overflow check.

| Surface | Before | After |
|---|---|---|
| Desktop, first viewport | [Before](before-desktop.png) | [After](after-desktop.png) |
| Phone, first viewport | [Before](before-mobile.png) | [After](after-mobile.png) |
| Phone, after selecting the memory link | | [After](after-mobile-memories.png) |

| Area | Observed issue and impact | Change |
|---|---|---|
| City index | Two section labels, two taglines and a bordered checkbox competed with search and drove the first rows down. | One heading, one visit summary, native filter controls and a conditional result count. |
| Selected city | Location, count and a repeated explanation consumed several lines before the first action. The mode disclaimer was below the workspace. | Put region and visit count on one line, label sample/local mode in the header and show sorting only when it can change the order. |
| Trip entries | The tall photo and credit appeared before the date and title. Box borders and inner padding reduced the text width and kept the second entry below the fold. | Date, fictional label and title lead. Rule-separated entries share the paper surface. 16:10 covers align with the prose. The second title is visible at 1440×900. |
| Phone | The selected city was clipped in the scroll strip and the first screen ended before the selected city’s memories. | Keep the selected row visible. Shorten the map area and offer an explicit jump link that focuses the selected city’s heading. |
| Local album | The AI action had a coloured fill on every trip. The form also restated the selected city. | Keep the create action prominent and make AI a secondary text action. The form label still names its city for assistive technology. |

Tested in Ego Browser with the built-in SVG map. The sample flow covered Map and Album, search by local name, empty results, sorting, adding and removing a sample, and closing PhotoSwipe with focus return. The local flow covered creating a trip, uploading a bundled park photo, editing Chinese and English text, reloading the saved result, and the missing-provider failure following explicit AI confirmation. The About page was also opened. See [recorded checks](browser-checks.json). An immediate close request during the gallery opening animation did not register. The settled viewer closed normally.

Commands passed: `npm test` (25), `python -m pytest -q` (94), `python3 scripts/build_public_demo.py --check` (31 public assets), `git diff --check`. Impeccable’s layout scan returned an empty result. The manual browser observations above are the primary design evidence. Live AI, optional online maps, Safari and physical phones were outside this round of verification.

The project uses native HTML/CSS/ES modules, locally bundled Fraunces, MapLibre and PhotoSwipe. Impeccable’s layout guidance and detector supported the review. The shadcn/ui Skill and 21st.dev examples were assessed for fit. The implementation uses the existing components and introduces zero dependencies. Style rules are in [DESIGN.md](../../../DESIGN.md).
