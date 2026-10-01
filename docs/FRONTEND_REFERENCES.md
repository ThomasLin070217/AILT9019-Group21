# Frontend references — 1 October 2026

The user remembered a GitHub project called “旅行记忆” but did not know its URL. We searched Chinese and English names and reviewed likely candidates. **None is confirmed as the exact project the user meant.**

| Repository | Evidence read / inspected | Applied lesson |
| --- | --- | --- |
| [823889637/travel-memory](https://github.com/823889637/travel-memory) | README, MemoryMap.vue and tokens.css; committed journey-desktop.png | Keep selected place and memory context linked. Preserve zoom during selection. Its committed desktop screenshot shows an empty/error state; we do not claim a successful live demo. No license was established, so no source or assets were copied. |
| [0718lol/lumeng](https://github.com/0718lol/lumeng) — 旅梦 | README, Trips.jsx, screenshot-trips.png | Put photos before card metadata; separate a trip from its photo count. The screenshot is branded Tripbook (its declared upstream). MIT project; our implementation borrows the idea, not code/assets. |
| [seanmorley15/AdventureLog](https://github.com/seanmorley15/AdventureLog) | Official map and details screenshots from the earlier UI research | Map and details stay visible together, with compact controls. No source code reused. |

[carolinaaafy/travel-memory-sticker-card](https://github.com/carolinaaafy/travel-memory-sticker-card) was another name match (570 stars when checked). It generates travel sticker cards and is **not a map frontend**. Its license limits reuse to personal, non-commercial uses and prohibits redistribution without permission; none of its assets/code was incorporated.

## What changed in our own app

- Replace the large introductory heading and full-width controls with a compact city sidebar.
- Show the map and a city’s dated photo cards together; selected cities with a usable cover get a thumbnail marker.
- Add Map / Album switching for a wider view of the selected city’s cards.
- List visited cities first. Keep exact counts alongside color tiers and the equivalent keyboard city list.
- Replace coarse 1:110m land with a pinned regional 1:50m source; keep attribution.
- Use white control surfaces, warm paper behind the cards, pale blue water and rust selection. Self-host Fraunces under the bundled SIL OFL.
- Preserve mobile city selection, draft persistence, explicit demo labels, nearby-city chooser, safe image URLs and all proposed teammate interfaces.

This is a locally runnable frontend module, not evidence that uploads, Google Maps, SQLite or the cloud VLM have been integrated. The submitted proposal is unchanged. No collaborator message was sent.
