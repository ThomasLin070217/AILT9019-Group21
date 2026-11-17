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
  tier-1: "#16643b"
  tier-2: "#56e62e"
  tier-3: "#bdff24"
typography:
  display:
    fontFamily: "Fraunces,Georgia,serif"
    fontSize: "44px"
    fontWeight: 470
    lineHeight: 1.08
    letterSpacing: "-.035em"
  headline:
    fontFamily: "Fraunces,Georgia,serif"
    fontSize: "28px"
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
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.65
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
  trip-entry:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    padding: "16px 0 12px"
---

# Design System: Travel Memory Map

## Overview

**Creative North Star: "The Open City Album"**

A compact city index and a working map sit beside an open album. Warm paper, pale water, white controls and rust selection keep the place legible while photographs and personal text carry the memory. This is the implemented direction recorded for team review, not a claim of a separate user-approved brand system.

Fraunces gives city names and trip titles an album-like voice. System sans keeps navigation, dates and notes clear. Fine rules separate trips on a shared paper surface. Floating controls sit above the map.

**Key Characteristics:**
- A persistent city index coordinates map selection and the selected city’s memories.
- Locally bundled Fraunces headings with compact system sans controls.
- White controls, warm paper albums, pale blue water and rust selection.
- Credited example photos and explicit fictional-trip labels remain visible.

## Colors

The palette places rust selection against white controls, warm paper and pale blue water. Frontmatter contains the normative values, extracted from `app/styles.css`.

### Primary

- **Rust** (`accent`) marks selected map rings, dates, keyboard focus and the sample-visit action.
- **Warm selection paper** (`selected-city`) and **deep rust text** (`selected-city-ink`) identify the selected city row without turning the whole catalogue into an accent block.

### Secondary

- **Pale water** (`sea`) establishes the map field and missing-photo fallback.
- **Forest status** (`green`) is reserved for the small status message; it is not the dominant brand accent.
- **Visit tiers** (`tier-0` through `tier-3`) move from slate through green to more fluorescent lime for no visits, one visit, two–three visits and four or more. They are data colours, not alternative button themes.

### Neutral

- **Charcoal** (`ink`) carries primary text; **quiet grey** (`muted`) carries supporting text.
- **Warm paper** (`paper`) is the album background; **white** (`surface`) is the control surface.
- **Fine rule** (`line`) divides panels and card actions; **land paper** (`land`) separates coastline geometry from water.

**The Count Before Colour Rule.** Every visit tier has a written legend, and saved visit totals remain visible in the index and album; colour never carries the count alone.

## Typography

**Display Font:** locally bundled Fraunces, with Georgia and serif fallbacks. The bundled variable face exposes weights 100–900 and uses `font-display: swap`.

**Body Font:** the system sans stack in the frontmatter. There is no separate mono face.

The softly shaped display face makes cities and memories feel personal while compact sans labels keep the map usable.

### Hierarchy

- **Display:** selected-city heading; on narrow desktop it becomes 38px. At phone widths it scales from 30px to 38px.
- **Headline:** city index heading at 28px, reduced to 23px on phones.
- **Title:** trip heading at 25px on both desktop and phone.
- **Body:** general interface copy. Trip prose uses 14px type with 1.65 line height, up to 68 characters per line, and preserves user line breaks.
- **Label:** rust trip dates. Other metadata uses 10–13px sans text; visit counts use tabular numerals. There is no imposed scale ratio or uppercase-label system.
- **Brand:** Fraunces at 23px, weight 540, line height 1 and letter spacing −.035em; reduced to 21px and then 19px at smaller widths. The sample or local album label sits beneath it in 11px system sans.

**The Album Voice Rule.** Use Fraunces for the brand, city headings and memory titles; use system sans for controls, dates, counts and readable memory text.

## Layout

The default desktop workspace is a three-column grid: city index (264px), fluid map, album (408px). It sits below a 76px top bar and above a footer of at least 48px. Workspace height is `calc(100dvh - 124px)` with a 560px minimum; the index and album scroll within their columns. At widths of at least 1700px the index and album expand to 288px and 460px. Between 851px and 1200px they narrow to 220px and 330px.

At 850px and below, the workspace flows vertically: compact two-column search/filter controls, a horizontal city strip, a fixed-height map, then memories. City items scroll horizontally, and the selected city stays visible when its selection changes. The map canvas is 280px tall. On phones the map controls sit together along the bottom. The link below the map names the selected city and focuses the memory heading. Back to map returns focus to the fit control. Journal entries flow into two columns at tablet widths and one on phones.

Album view hides the map and retains the city index. Its desktop card grid uses `repeat(auto-fit,minmax(min(100%,300px),1fr))` with a 24px gap, so available cards occupy the width without an empty phantom column. Stacked breakpoints explicitly use two columns, then one. Switching views preserves selected records and drafts.

The desktop journal uses 28px panel padding and entries sit flush to the prose column. A rule and 16px of top padding separate each entry. Use 4px between date and title, 12px between title, cover and prose, and 8px before actions. Phone journal padding is 16px and Album view has up to 40px on each side.

## Elevation & Depth

Persistent panels and cards are flat, separated by tonal fields and thin rules. Small shadows distinguish controls or choices sitting above another surface. The photo viewer uses a dark translucent backdrop to isolate a complete image.

### Shadow Vocabulary

- **Map overlay:** `0 6px 24px #233c4220`, used by nearby-city choices through the shared shadow custom property.
- **Map control:** `0 2px 8px #233c4218`, used by zoom and fit buttons.
- **Selected view:** `0 2px 5px #26332a10`, used by the active Map/Album segment.
- **Viewer backdrop:** `rgba(27,34,33,.85)`; this is an overlay, not a card shadow.

**The Quiet Surface Rule.** Entries share the paper surface and use top rules. Persistent panels are separated by background tone. Reserve shadows for selected view controls, floating map controls and nearby-city choices.

## Shapes

Controls and city rows have gently rounded corners (`control`); the view-switch enclosure is slightly softer (`switch`). Nearby-city choices and the fallback photo dialog use the larger `surface` radius. The cover has a 4px radius. Visit badges and legend dots are circular. Panels meet along straight one-pixel rules rather than floating as a collection of cards.

Photo covers align with the title and use a 16:10 crop with the subject centred horizontally and positioned at 35% vertically. The image viewer contains the complete image. Map points remain round; a selected city with an available cover adds a small framed photo and stem. There are no decorative route lines.

## Components

### Buttons

Quiet white controls use a one-pixel grey border, a 44px minimum height and weight 550. The rust primary variant belongs to the clearly labelled sample-visit control, with a darker rust hover state. Text actions are small, underlined and transparent. Disabled controls use opacity .45 and a not-allowed cursor. Interactive controls use a three-pixel rust focus outline with three-pixel offset.

### Inputs / Fields

Search, select and textarea fields have one-pixel grey borders and rounded control corners. Search has a pale neutral fill and inset magnifier; the native select remains recognizable. The visited-only checkbox uses the rust accent. Editing sample text reveals a labelled, vertically resizable textarea, plus explicit save/discard controls and draft-storage guidance. Error feedback is shown in the shared error region rather than an invented field-error style.

### Navigation

The Map/Album segmented control sits on a pale neutral enclosure; its active segment becomes white with a small shadow. `aria-pressed` communicates the current view. At phone widths icons and labels are both visible. The city index pairs English and local names with a textual count, showing visited cities first. A warm selected row and filled rust count badge tie the index to the active map marker.

### Chips / Badges

The visit badge is a circular numerical count with a pale green neutral field; selection changes it to rust with white text. An unvisited row shows a dash. These are status indicators inside city buttons, not independent filter chips.

### Cards / Containers

Read each entry in order from date and sample provenance to title, optional cover and credit, then memory text and actions. Show sorting with two or more entries. In local mode the Add a memory disclosure uses the light rust treatment. Write with AI is a text action beside editing and photo controls. The text-only and missing-photo states retain the date, title and prose.

### Memory Map

The offline map uses local Natural Earth SVG geometry and Mercator coordinates. With a configured key, Google Maps supplies the live base map, attribution and native map gestures; custom advanced markers inherit the same count/selection palette and link to the same album. The application preserves Google attribution, exposes provider/loading/fallback status and retains the local map on SDK failure. Marker brightness is derived from saved trip IDs; labels and the written legend supply the meaning. Markers support keyboard activation, retain focus through selection and have large invisible hit areas. Close marker groups offer explicit city choices. Zoom and fit controls are fixed-size white buttons. Panning is enabled only after zoom so the default map permits normal mobile page scrolling.

On successful save a city marker pulses once for 440ms. The fill uses green at three intensities and remains visible after the pulse. Reduced-motion preference skips the pulse. Card-cover hover uses a small brightness change without added animation.

### Photo Viewer and Feedback

PhotoSwipe shows the full photograph and returns focus on close. The native dialog provides the fallback. Loading, no matching cities, empty memories, failed media, backend errors and damaged local records have explicit text states. Status uses a polite live region; errors use an alert. Demo controls and fictional content labels stay distinct from backend mode.

The sample album stores fictional edits in the browser. The local album uses FastAPI and SQLite for saved trips and photo uploads. Cloud AI drafts require provider configuration and explicit trip-level confirmation.

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
- Keep provider and storage labels accurate. Photos and optional AI belong to the local album. Google Maps requires a local browser key.
- Don't use decorative shadows on every card or add motion beyond the restrained marker state change.
