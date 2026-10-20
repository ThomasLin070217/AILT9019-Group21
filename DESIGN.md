---
name: "Travel Memory Map"
description: "An open city album with a compact index and a photographic memory map."
colors:
  ink: "#292e30"
  muted: "#626767"
  paper: "#f6f5f1"
  surface: "#fff"
  line: "#e2e3df"
  sea: "#e1ecee"
  land: "#f8f7f2"
  accent: "#ad4a29"
  green: "#345f51"
  selected-city: "#f5e8dd"
  selected-city-ink: "#8c3c20"
  tier-0: "#829b9b"
  tier-1: "#516442"
  tier-2: "#9f502f"
  tier-3: "#eea348"
typography:
  display:
    fontFamily: "Fraunces,Georgia,serif"
    fontSize: "44px"
    fontWeight: 470
    lineHeight: 1.08
    letterSpacing: "-.035em"
  headline:
    fontFamily: "Fraunces,Georgia,serif"
    fontSize: "32px"
    fontWeight: 480
    lineHeight: 1.12
    letterSpacing: "-.03em"
  title:
    fontFamily: "Fraunces,Georgia,serif"
    fontSize: "25px"
    fontWeight: 470
    lineHeight: 1.2
    letterSpacing: "-.025em"
  body:
    fontFamily: "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  memory-body:
    fontFamily: "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.75
  label:
    fontFamily: "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
    fontSize: "11px"
    fontWeight: 600
rounded:
  control: "8px"
  switch: "10px"
  surface: "12px"
  circle: "50%"
spacing:
  tight: "8px"
  small: "12px"
  medium: "16px"
  card: "20px"
  section: "24px"
  panel: "28px"
  wide-panel: "40px"
components:
  button-default:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 14px"
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "10px 14px"
    width: "100%"
  button-text:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    padding: "10px 0"
  search-field:
    backgroundColor: "#f8f9f6"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 12px 10px 37px"
    width: "100%"
  view-switch:
    backgroundColor: "#f1f2ee"
    rounded: "{rounded.switch}"
    padding: "4px"
  city-selected:
    backgroundColor: "{colors.selected-city}"
    textColor: "{colors.selected-city-ink}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
  visit-badge:
    backgroundColor: "#e9eee8"
    textColor: "#365847"
    rounded: "{rounded.circle}"
    width: "26px"
    height: "26px"
  trip-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.surface}"
    padding: "0 20px 12px"
---

# Design System: Travel Memory Map

## Overview

**Creative North Star: "The Open City Album"**

A compact city index and a working map sit beside an open album. Warm paper, pale water, white controls and rust selection keep the place legible while photographs and personal text carry the memory. This is the implemented direction recorded for team review, not a claim of a separate user-approved brand system.

Fraunces gives city names and trip titles an album-like voice; system sans keeps navigation and metadata clear. The interface stays practical and quietly tactile: fine rules separate persistent regions, rounded cards hold individual trips, and small lifted controls sit above the map. The older green-led, Georgia-led catalogue treatment has been replaced.

**Key Characteristics:**
- A persistent city index coordinates map selection and the selected city’s memories.
- Locally bundled Fraunces headings with compact system sans controls.
- White cards and controls, warm paper albums, pale blue water and rust selection.
- Credited example photos and explicit fictional-trip labels remain visible.

## Colors

The palette places rust selection against white controls, warm paper and pale blue water. Frontmatter contains the normative values, extracted from `app/styles.css`.

### Primary

- **Rust** (`accent`) marks selected map rings, dates, keyboard focus and the sample-visit action.
- **Warm selection paper** (`selected-city`) and **deep rust text** (`selected-city-ink`) identify the selected city row without turning the whole catalogue into an accent block.

### Secondary

- **Pale water** (`sea`) establishes the map field and missing-photo fallback.
- **Forest status** (`green`) is reserved for the small status message; it is not the dominant brand accent.
- **Visit tiers** (`tier-0` through `tier-3`) move from slate through olive and rust to amber for no visits, one visit, two–three visits and four or more. They are data colours, not alternative button themes.

### Neutral

- **Charcoal** (`ink`) carries primary text; **quiet grey** (`muted`) carries supporting text.
- **Warm paper** (`paper`) is the album background; **white** (`surface`) is the control and card surface.
- **Fine rule** (`line`) divides panels and card actions; **land paper** (`land`) separates coastline geometry from water.

**The Count Before Colour Rule.** Every visit tier has a written legend, and saved visit totals remain visible in the index and album; colour never carries the count alone.

## Typography

**Display Font:** locally bundled Fraunces, with Georgia and serif fallbacks. The bundled variable face exposes weights 100–900 and uses `font-display: swap`.

**Body Font:** the system sans stack in the frontmatter. There is no separate mono face.

The softly shaped display face makes cities and memories feel personal while compact sans labels keep the map usable.

### Hierarchy

- **Display:** selected-city heading; on narrow desktop it becomes 38px, and at phone widths it becomes 42px.
- **Headline:** catalogue heading; it becomes 27px below the stacked-layout breakpoint and 26px on phones.
- **Title:** trip heading; it becomes 28px on phones.
- **Body:** general interface copy. Trip prose uses the separate `memory-body` role and becomes 14px on phones.
- **Label:** rust trip dates. Other metadata uses 10–13px sans text; visit counts use tabular numerals. There is no imposed scale ratio or uppercase-label system.
- **Brand:** Fraunces at 23px, weight 540, line height 1 and letter spacing −.035em; reduced to 21px, then 20px at smaller widths.

**The Album Voice Rule.** Use Fraunces for the brand, city headings and memory titles; use system sans for controls, dates, counts and readable memory text.

## Layout

The default desktop workspace is a three-column grid: city index (264px), fluid map, album (408px). It sits below a 76px top bar and above a footer of at least 48px. Workspace height is `calc(100dvh - 124px)` with a 680px minimum; the index and album scroll within their columns. At widths of at least 1700px the index and album expand to 288px and 460px. Between 851px and 1200px they narrow to 220px and 330px.

At 850px and below, the workspace flows vertically: compact two-column search/filter controls, a horizontal city strip, a fixed-height map, then memories. City items are 138px wide with proximity scroll snapping. The map is 450px high, reducing to 405px at 540px and below. Memory cards form two columns until the 540px breakpoint, then one. Pointer city selection reveals the album on small screens; keyboard selection does not force page scrolling. A Back to map control appears in stacked Map view.

Album view hides the map and retains the city index. Its desktop card grid uses `repeat(auto-fit,minmax(280px,1fr))` with a 24px gap, so available cards occupy the width without an empty phantom column. Stacked breakpoints explicitly use two columns, then one. Switching views preserves selected records and drafts.

Spacing is compact in the index and generous around photographs: desktop album padding is 28px, card side padding is 20px, and card separation is 22px. Expanded Album view uses 36px vertical and 40px horizontal padding. These are observed dimensions rather than a universal arithmetic spacing scale.

## Elevation & Depth

Persistent panels and cards are flat, separated by tonal fields and thin rules. Small shadows distinguish controls or choices sitting above another surface. The photo viewer uses a dark translucent backdrop to isolate a complete image.

### Shadow Vocabulary

- **Map overlay:** `0 6px 24px #233c4220`, used by nearby-city choices through the shared shadow custom property.
- **Map control:** `0 2px 8px #233c4218`, used by zoom and fit buttons.
- **Selected view:** `0 2px 5px #26332a10`, used by the active Map/Album segment.
- **Viewer backdrop:** `rgba(27,34,33,.85)`; this is an overlay, not a card shadow.

**The Quiet Surface Rule.** Cards and persistent panels use borders and background tone. Reserve shadows for selected view controls, floating map controls and nearby-city choices.

## Shapes

Controls and city rows have gently rounded corners (`control`); the view-switch enclosure is slightly softer (`switch`). Trip cards, nearby-city choices and the photo dialog share the larger `surface` radius. Visit badges and legend dots are circular. Panels meet along straight one-pixel rules rather than floating as a collection of cards.

Photo covers bleed to the card edges, use a 4:3 crop and position the subject at centre/35% vertically. The image viewer contains the complete image. Map points remain round; a selected city with an available cover adds a small framed photo and stem. There are no decorative route lines.

## Components

### Buttons

Quiet white controls use a one-pixel grey border, a 44px minimum height and weight 550. The rust primary variant belongs to the clearly labelled sample-visit control, with a darker rust hover state. Text actions are small, underlined and transparent. Disabled controls use opacity .45 and a not-allowed cursor. Interactive controls use a three-pixel rust focus outline with three-pixel offset.

### Inputs / Fields

Search, select and textarea fields have one-pixel grey borders and rounded control corners. Search has a pale neutral fill and inset magnifier; the native select remains recognizable. The visited-only checkbox uses the rust accent. Editing sample text reveals a labelled, vertically resizable textarea, plus explicit save/discard controls and draft-storage guidance. Error feedback is shown in the shared error region rather than an invented field-error style.

### Navigation

The Map/Album segmented control sits on a pale neutral enclosure; its active segment becomes white with a small shadow. `aria-pressed` communicates the current view. At phone widths its visible labels give way to the existing map and album icons. The city index pairs English and local names with a textual count, showing visited cities first. A warm selected row and filled rust count badge tie the index to the active map marker.

### Chips / Badges

The visit badge is a circular numerical count with a pale green neutral field; selection changes it to rust with white text. An unvisited row shows a dash. These are status indicators inside city buttons, not independent filter chips.

### Cards / Containers

A trip card holds an optional cover, credit, date, wrapping title, memory text and provenance line. Demo cards expose edit/remove text actions below a fine divider. The preview snippets include the text-only variant, which is also valid when no photo exists. Missing media leaves the memory text and a plain fallback intact.

### Memory Map

The offline map uses local Natural Earth SVG geometry and Mercator coordinates. With a configured key, Google Maps supplies the live base map, attribution and native map gestures; custom advanced markers inherit the same count/selection palette and link to the same album. The application preserves Google attribution, exposes provider/loading/fallback status and retains the local map on SDK failure. Marker brightness is derived from saved trip IDs; labels and the written legend supply the meaning. Markers support keyboard activation, retain focus through selection and have large invisible hit areas. Close marker groups offer explicit city choices. Zoom and fit controls are fixed-size white buttons. Panning is enabled only after zoom so the default map permits normal mobile page scrolling.

The only animated state is marker fill (`180ms ease-out`); reduced-motion preference removes it. Card-cover hover uses a small brightness change without added animation.

### Photo Viewer and Feedback

The native dialog shows the full photograph with a Close photo action, caption and focus returned to the trigger. Loading, no matching cities, empty memories, failed media, backend errors and damaged local records have explicit text states. Status uses a polite live region; errors use an alert. Demo controls and fictional content labels stay distinct from backend mode.

This is a local demonstration. Real uploads, cloud AI and SQLite are not integrated; the existing API-facing mode does not establish those capabilities.

## Do's and Don'ts

### Do:
- Do preserve visible counts, keyboard selection, focus outlines and reduced-motion support.
- Do use the same selected city and drafts when switching Map and Album views.
- Do retain photo credits, fictional-story labels and useful memory text when media fails.
- Do let long city names and trip titles wrap without clipping.
- Do keep the complete photograph reachable from its cropped card cover.

### Don't:
- Don't reintroduce the replaced green-led catalogue styling or use Georgia as the primary display face.
- Don't imply that example photographs document fictional trips.
- Don't depict routes or imply real uploads, cloud AI or SQLite integration. Google Maps is optional and requires a local browser key.
- Don't use decorative shadows on every card or add motion beyond the restrained marker state change.
