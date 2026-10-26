# City map: data, modes and limits

The default Map view uses [OpenFreeMap's Positron style](https://openfreemap.org/quick_start/) rendered by locally bundled MapLibre GL JS 5.6.0 (`app/vendor/maplibre/`, with its BSD licence). It needs network access for map tiles but no API key. The restrained basemap gives the city footprints geographic context without making roads the product's focus. OpenFreeMap's map data comes from OpenStreetMap; the renderer's attribution control remains visible.

The 19 city footprints in `data/map/city-regions.geojson` are bundled snapshots from OpenStreetMap relations. They are not downloaded when the app runs. The same geometry supplies a thin outline for each supported city, a stronger outline for the selected city, and a filled 1 / 2–3 / 4+ visit tier. The city catalogue still determines which places are supported. These footprints are approximate display areas, not a claim that a person visited every point in a municipality. Because the online basemap and bundled boundaries may have different update dates, their outlines can differ slightly.

Map modes:

| URL | Result |
| --- | --- |
| `/app/` or `/app/?mode=api` | OpenFreeMap/MapLibre, with automatic local fallback if loading fails |
| `/app/?map=local` | Bundled coast and city geometry; no third-party map requests |
| `/app/?map=google` | Optional Google Maps JavaScript API; requires the local browser key described in `GOOGLE_MAPS_SETUP.md` |

All modes use geographic coordinates and consistent zooming within a mode. A city boundary is easiest to see after selecting a city and using **View area**. Saving a trip updates that city's count and fill; a second trip creates a separate card and changes the tier when the threshold is crossed. Map providers receive the viewport/tile requests needed to draw their basemap. Trip photos, notes, and AI drafts are not sent to a map provider.

The app keeps an online map optional because availability and map data vary by network and provider. `?map=local` is also the stable reproduction mode for tests and the mid-term recording. The local map uses [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/) public-domain land geometry and the same OpenStreetMap city footprints.
