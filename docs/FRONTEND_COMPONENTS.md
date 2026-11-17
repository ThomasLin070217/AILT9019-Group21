# Frontend component review — 17 November 2026

The app remains native JavaScript, HTML and CSS, shared by the local backend and GitHub Pages sample demo. No React migration or hosted AI service is introduced.

## Components considered

- [PhotoSwipe](https://photoswipe.com/getting-started/): selected for the image viewer. Official npm `latest` resolved to **5.4.4**, MIT licence, on this date; the documentation labels v6 as in development. Core and CSS are bundled locally with licence and verified npm integrity, not downloaded from a CDN at runtime. Core is imported only when someone opens a photograph.
- [Web Awesome Drawer](https://webawesome.com/docs/components/drawer/): reviewed as a framework-independent drawer reference. Not added: the current mobile task works as a flowing city/map/album layout without hiding navigation inside another overlay.
- [Base UI releases](https://base-ui.com/react/overview/releases): reviewed its current React controls and accessibility work. Not installed because this application does not use React.

## Shipped interaction changes

- PhotoSwipe gives photo zoom, previous/next controls, keyboard navigation and touch gestures. Sample galleries group credited photos from the selected city's fictional trips; backend galleries contain only the selected trip's uploaded photos. Captions name the trip and keep sample attribution explicit. Text is assigned with `textContent`.
- Viewer traps focus, makes the underlying app inert, restores focus on close, and respects reduced motion. The previous native dialog is retained if the new module cannot load. Image errors retain a way back to the album.
- An always-visible sample-visit action replaces the buried action in a collapsed panel. Demo limitations remain in the footer and an explanatory disclosure.
- Newest/oldest sorting and a clear-filters action make the collection easier to navigate. Sorting preserves draft text and saved visit counts.
- The backend's Add a memory form opens automatically for an empty city or an unsaved draft, and collapses after save to keep existing memories in view.
- Photo covers have a visible open affordance; AI and editing actions have distinct emphasis. Destructive actions still require confirmation.
- Phone Map/Album tabs retain visible labels; sticky navigation, readable attribution and flexible map height prevent the previous clipped footer. Zoom buttons remain at least 44 by 44 CSS pixels.

## Evidence and boundaries

See [the browser evidence](../tests/evidence/2026-11-17-frontend/RESULTS.md). Public deployment still serves fictional browser-local data; real uploads and AI require the local backend. No live AI request, private fixture publication, data migration or Moodle submission was performed in this UI pass.

The older PRODUCT.md/DESIGN.md include stale integration claims and design metadata; current README and runtime evidence describe the integrated build. Their broader context migration was not performed as a side effect of this refinement.
