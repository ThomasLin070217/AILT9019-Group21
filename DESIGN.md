# Travel Memory Map interface

The first surface is an operating map and album browser, not a marketing page. The map is dominant beside a selected city's chronological photo cards. A compact search/filter row and horizontally scrollable city strip sit above both. Mobile order is compact city controls, map, then cards; selecting a city brings its memories into view, with a Back to map action. This design is a provisional implementation for team review.

## Tokens

- Ink `#223d37`, secondary text `#52665e`, paper `#f8f6f0`, card surface `#fffefb`, rules `#d6ddd4`.
- Sea `#e8efec`, land `#faf9f3`, text accent `#974e32`, main action `#27684e`.
- Marker tiers: `#99aca0`, `#547857`, `#96b46a`, `#d2d888`. Exact counts and explicit legend accompany colour.
- Serif headings use Georgia; controls/body use the system sans family. Base body 15px; controls avoid text truncation.
- Controls have 6–7px corners. No remote fonts, icon libraries or external map tiles. Two locally bundled, credited Unsplash example covers demonstrate photo cards in demo mode; other cards stay text-only until photos exist.

## Behaviour

SVG coastline geometry uses Mercator coordinates. Buttons zoom within the supported extent and fit back to all cities. Pan is enabled only after zoom so a phone can scroll the page normally at the default view. Markers retain keyboard focus after selection; city list selection provides an equivalent path. Map hit areas and main buttons are at least 44px; close marker groups open explicit city choices. Card headings wrap long words. Selected-city scrolling happens only on pointer selection on small screens, not during typing or keyboard selection. Native colour-independent focus outlines and reduced-motion styles are present.

## States and scope

Loading, error/retry, malformed local storage recovery, empty cities, empty search and failed backend reads are explicit. Sample controls are labelled and hidden in API mode. Card text is inserted as text, never HTML. Pin fill transitions respect reduced motion; typing and city changes preserve per-tab drafts. Real uploads and AI controls belong to later integration.

## Photo browsing

Trip covers use a 3:2 crop above date/title/text; the native dialog displays the complete downloaded photograph. Desktop memory content scrolls within a bounded panel next to the map. Mobile cards flow naturally in the page. Failed media loads display a text fallback. Draft storage errors are visible; no edit is counted as another visit.
