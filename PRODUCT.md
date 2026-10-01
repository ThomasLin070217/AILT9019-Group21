# Travel Memory Map

## Platform

web

## Users and purpose

Students recording completed trips as city-based memories. The user chooses a city, supplies photos and optional notes, saves an independent trip, and can request an editable cloud AI draft. Repeated visits are distinct cards and brighten the city marker.

## Confirmed constraints

Local first version, cloud AI on explicit request only, no automatic classification, no 3D/navigation/social accounts, no invented experiences. Initial city coverage is a selected set in mainland China, Hong Kong, Macau, Taiwan and Japan. Five small evaluation cases are planned; no AI results have been collected.

## Current implementation boundary

Thomas's city-map module uses browser JavaScript and a Python standard-library preview server. It optionally loads Google Maps JavaScript API when a local key is configured; the bundled SVG remains available without a key or with map=local. This is a reversible implementation choice for straightforward team handoff, not a claim that the team approved a framework. The demo uses fictional browser-local records. Backend/SQLite, uploads and the cloud VLM remain separate teammates' modules.

## Evidence and accessibility

Pinned public-domain map data in data/SOURCES.json. Use text counts and a searchable keyboard-accessible city list alongside map brightness. Clearly label sample data and backend failures. Actual integration with teammate modules remains pending.
