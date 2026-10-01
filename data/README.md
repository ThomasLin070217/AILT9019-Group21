# Map and demonstration data

`cities.json` is the initial 19-city integration catalogue. `map/land.geojson` is Natural Earth 1:50m land geometry, retaining polygons intersecting the regional bounding box and removing unused properties. `SOURCES.json` pins source URLs, commit, hashes, transformations and the public-domain licence. Rebuild with `python3 scripts/build_map_data.py` (network only during rebuilding). Runtime rendering is local and uses no tile service.

Names/translations and filter groups were selected for the app. Coordinates are approximate city centres. The coarse coastline can omit small islands; it is not suitable for navigation or border interpretation. The catalogue is a small supported set, not full regional coverage.

`demo-trips.json` contains nine deliberately fictional text-only records in five cities. They are not the team's travel history or AI output. Browser demo storage is separate from future real trip storage. Never use these sample records to claim AI evaluation success.

`fixtures/T01/` contains original synthetic image cards and fictional notes for Thomas's initial test case. Its provenance and limitations are in that folder. Other cases and live AI results are still pending.

Only permission-cleared, non-sensitive fixtures belong here. Do not place private albums, chat screenshots, keys or real personal notes in this directory: it is served by the local preview.

`demo-covers/` contains two separately licensed Osaka example photographs used by the UI for demo cards only. See its source manifest for credits and hashes. They are not user uploads or AI evaluation inputs.
