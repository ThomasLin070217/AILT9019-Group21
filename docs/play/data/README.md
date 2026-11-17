# Map and demonstration data

`cities.json` is the initial 19-city integration catalogue. `map/land.geojson` is Natural Earth 1:50m land geometry, retaining polygons intersecting the regional bounding box and removing unused properties. `SOURCES.json` pins source URLs, commit, hashes, transformations and the public-domain licence. Rebuild with `python3 scripts/build_map_data.py` (network only during rebuilding). The offline renderer uses this local geometry without a tile service. With a configured browser key, the optional Google Maps renderer loads its online basemap instead; see `docs/GOOGLE_MAPS_SETUP.md`.

`map/city-regions.geojson` provides a separate display footprint for each of the 19 cities. It is derived from OpenStreetMap administrative relations via Nominatim and offered under the [ODbL 1.0](https://www.openstreetmap.org/copyright). `map/city-regions-sources.json` records the relation ID and source link for every city, the selection and simplification steps, and limitations. The app always displays `© OpenStreetMap contributors` attribution alongside this layer. The geometry is packaged locally, so browsing the map does not send city or visit data to Nominatim. The Google mode uses the same packaged areas as an overlay.

Names/translations and filter groups were selected for the app. Coordinates are approximate city centres. The coarse coastline can omit small islands; it is not suitable for navigation or border interpretation. The area layer omits distant disconnected islands for Tokyo and Kaohsiung so that the selected footprint stays near the city centre. These areas are visual context, not authoritative administrative boundaries or proof that a user visited. The catalogue is a small supported set, not full regional coverage.

`demo-trips.json` contains nine deliberately fictional text-only records in five cities. They are not the team's travel history or AI output. Browser demo storage is separate from future real trip storage. Never use these sample records to claim AI evaluation success.

`fixtures/T01/` contains original synthetic image cards and fictional notes for Thomas's initial test case. Its provenance and limitations are in that folder. Other cases and live AI results are still pending.

Only permission-cleared, non-sensitive fixtures belong here. Do not place private albums, chat screenshots, keys or real personal notes in this directory: it is served by the local preview.

`demo-covers/` contains two separately licensed Osaka example photographs used by the UI for demo cards only. See its source manifest for credits and hashes. They are not user uploads or AI evaluation inputs.
