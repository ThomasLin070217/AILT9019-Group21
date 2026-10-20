# Travel map redesign — 1 October 2026

Mode: Operate, with photographic recall as the primary content.

User asked to replace an ugly frontend, learn from GitHub travel-memory apps, and authorized us to identify the vaguely remembered reference. No exact repo identified. The competitor-like direction is user requested. Code-led implementation; no generated comp. The Impeccable launcher/context/seed are not executable on this machine (exit 126); source context and reference images were inspected directly. No seed result or user approval is claimed.

## Direction contract

A working map beside an open city album, with a compact persistent city index. The first viewport shows actual supported cities, counted visits, a selected marker, and a real credited example photo with the trip’s own text. Remove the old hero and horizontal desktop filter strip. A clear Map / Album control expands the same city's cards without changing records or drafts. Map selection is the signature interaction: select a place, see its photo marker and independent dated memories. Saved trip IDs own count and brightness. No artificial route lines or visit claims.

White controls, warm paper album, pale blue water, rust selection. Self-hosted Fraunces gives headings a personal album voice; system sans controls stay compact. Detailed 1:50m geometry replaces the old coarse coastline. Photo cards use large 4:3 crops, with the complete picture reachable by keyboard in the viewer. Single restrained marker-fill transition, disabled for reduced motion.

Desktop: three columns, city index / map / selected-city album. Narrow desktop: 220px index, fluid map, 330px album. Mobile: compact controls and city strip, map then flowing cards; selection reveals the city album. Album mode removes the map and gives photos the available width. No social feature or fake upload/AI button. Missing media leaves text intact; demo status, errors and recovery remain explicit.

## Quality bar / references inspected

- https://github.com/0718lol/lumeng — README, Trips.jsx and screenshot-trips.png: large images with date/place details, photo count separate from visit count. Screenshot still says Tripbook (upstream), not proof of its latest UI.
- https://github.com/823889637/travel-memory — README, MemoryMap.vue, tokens.css and journey-desktop.png: coordinated selection; preserve map gesture state and separate memory context. The committed screenshot contains a backend500/empty state, so it is not proof of a successful current demo. No code/assets copied; no license inferred.
- https://github.com/seanmorley15/AdventureLog — official map/details screenshots inspected in the prior research round: map/details co-presence and restrained controls.

Borrow information architecture, not branding, screenshots or data. Keep locally licensed Unsplash sample photos and explicit fictional-story labels. Distinct map provider and backend integration remain pending. Review desktop, mobile, narrow and album screenshots together.
