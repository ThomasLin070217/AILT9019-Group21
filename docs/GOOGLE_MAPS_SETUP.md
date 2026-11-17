# Google Maps setup

The hosted sample album uses Google Maps when the Pages build supplies a browser key. The normal local startup uses OpenFreeMap. Use `?map=streets` for OpenFreeMap, `?map=local` for the bundled map, or `?map=google` to request Google Maps explicitly. API and album query flags can be combined.

## Hosted sample album

To activate this workflow, set Pages → Build and deployment → Source to GitHub Actions
and the repository variable `AILT_PAGES_ACTIONS` to `true`.
The Pages workflow copies `docs/` into its deployment artifact and writes the repository secret
`GOOGLE_MAPS_BROWSER_KEY` to the sample app's runtime configuration. The checked-in config is empty.
Google receives the key from the browser. Set the key’s Website restriction to
`https://thomaslin070217.github.io/*` and its API restriction to Maps JavaScript API.
The hosted album tries Google first, then OpenFreeMap, then the bundled map. The Maps Demo project is
subject to Google’s demo limits.

The app loads its 19 OpenStreetMap display footprints into Google's geographic Data layer as
GeoJSON longitude/latitude pairs. It uses Google's projection and viewport controls to keep each
footprint aligned with the basemap at any zoom. Visit counts set three green fill levels.
Clicking a footprint selects the same city as its marker. Footprints are approximate and can
differ from administrative lines drawn by Google.

## Configure locally

Copy `.env.example` to `.env.maps.local`, enter a Maps JavaScript API browser key, run `python3 serve.py`, and open `/app/?map=google`. `.env.maps.local` is ignored by Git. Keep it local; don't put a key in source, a PR, screenshots or test logs. Environment variables `GOOGLE_MAPS_API_KEY` and `GOOGLE_MAPS_MAP_ID` override the file.

The development `DEMO_MAP_ID` enables advanced markers. It is not an API key. A production map can use its own JavaScript Map ID. A **Maps Demo Key** is a separate Google credential option for limited prototyping; a standard Maps key uses a billing-enabled project. This implementation does not assume which credential type the user supplied or manage its billing/quota.

Restrict the browser key in Google Cloud:

- Application restriction: **Websites**. For this preview, allow `http://127.0.0.1:8019/*` and, if used, `http://localhost:8019/*`.
- API restriction: **Maps JavaScript API**. This app does not need Places, Geocoding or Routes; city coordinates already exist locally.
- Add actual deployment origins before hosting. Review your account's usage limits separately.

The browser must receive the Maps key to load Google's SDK; it is not a server-only secret. The local `/api/map-config` endpoint exposes only the two browser settings, returns no-store, and rejects non-local Host/cross-origin Origin values. It does not expose other environment entries. Raw dotfiles are not served. These development-server checks do not replace Google's website/API restrictions, whose account settings have not been inspected.

## Behaviour

Google Maps loads in Map view when the hosted config is present, or when Google is explicitly requested with a configured local key. Opening directly in Album defers map loading. Google owns map tiles, attribution and its normal map requests. The app overlays the existing 19 city centres, trip counts/tiers and selected photo thumbnail. Our code does not upload the local photo files or travel notes to Google. AI memory generation uses the separate local backend.

Custom markers use AdvancedMarkerElement with `gmp-click`, keyboard support and the existing exact-city chooser for nearby pins. Filters update markers; selection connects to the same album/drafts. Zoom and fit use Google's geographic view. A timeout, rejected key or SDK load failure tries OpenFreeMap and shows the provider change. If both online options fail, the bundled map remains available. Reload retries; `?map=local` intentionally avoids Google loading.

Google's logo/attribution remain visible and unmodified. Advanced markers currently use Google's default development Map ID styling; cloud custom styling is not configured. CSP permits Google's documented map/script/image/font/connect domains and the SDK's eval/blob requirements; local map mode makes no third-party requests. For the default OpenFreeMap source, see [map data and modes](MAP_BASEMAP.md).

## Verification

- `npm test`: domain/storage tests.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: isolated local config parsing tests, using fake values.
- Existing `tests/browser.e2e.mjs`, `tests/album.e2e.mjs`, `tests/views.e2e.mjs` force `map=local` so routine tests do not consume map quota.
- `tests/google-map.e2e.mjs` is an **opt-in live test**, requiring a configured key and using Google map loads. It records only redacted console errors, never request URLs or config values.

Use `PLAYWRIGHT_MODULE`, `CHROMIUM_EXECUTABLE`, `BASE_URL` and `EVIDENCE_DIR` as in the Thomas handoff. Real Chrome desktop/mobile emulation passed on 1 October 2026; Safari, physical devices, production origins, billing limits and Cloud restriction settings remain unverified.

## Official references

- [Load the Maps JavaScript API](https://developers.google.com/maps/documentation/javascript/load-maps-js-api)
- [Advanced markers setup / Map ID](https://developers.google.com/maps/documentation/javascript/advanced-markers/start)
- [Accessible marker events](https://developers.google.com/maps/documentation/javascript/advanced-markers/accessible-markers)
- [CSP requirements](https://developers.google.com/maps/documentation/javascript/content-security-policy)
- [API key restrictions](https://developers.google.com/maps/api-security-best-practices)
- [Maps Demo Key](https://developers.google.com/maps/documentation/javascript/demo-key)
