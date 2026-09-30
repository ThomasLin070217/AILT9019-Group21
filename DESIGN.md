# Travel Memory Map interface

The first surface is an operating map and album browser, not a marketing page. The map is dominant, with a compact city catalogue to its left and a selected city's chronological records to its right. Mobile order is map, searchable cities, then cards. This design is a provisional implementation for team review.

## Tokens

- Ink `#223d37`, secondary text `#52665e`, paper `#f8f6f0`, card surface `#fffefb`, rules `#d6ddd4`.
- Sea `#e8efec`, land `#faf9f3`, text accent `#974e32`, main action `#27684e`.
- Marker tiers: `#99aca0`, `#547857`, `#96b46a`, `#d2d888`. Exact counts and explicit legend accompany colour.
- Serif headings use Georgia; controls/body use the system sans family. Base body 15px; controls avoid text truncation.
- Controls have 6–7px corners. No remote fonts, icon libraries, photo placeholders or external map tiles.

## Behaviour

SVG coastline geometry uses Mercator coordinates. Buttons zoom within the supported extent and fit back to all cities. Pan is enabled only after zoom so a phone can scroll the page normally at the default view. Markers retain keyboard focus after selection; city list selection provides an equivalent path. Native colour-independent focus outlines and reduced-motion styles are present.

## States and scope

Loading, error/retry, malformed local storage recovery, empty cities, empty search and failed backend reads are explicit. Sample controls are labelled and hidden in API mode. Card text is inserted as text, never HTML. The small card-arrival reveal is disabled when reduced motion is requested. Real uploads and AI controls belong to later integration.
