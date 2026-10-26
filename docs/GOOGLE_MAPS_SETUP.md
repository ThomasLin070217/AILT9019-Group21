# Google Maps local setup

Google Maps JavaScript API is an optional live base map. The default online map is OpenFreeMap/MapLibre, which needs no key; `?map=local` uses the bundled Natural Earth SVG, and `?map=google` opts into Google Maps. API and album query flags can be combined.

## Configure

Copy `.env.example` to `.env.maps.local`, enter a Maps JavaScript API browser key, run `python3 serve.py`, and open `/app/?map=google`. `.env.maps.local` is ignored by Git. Keep it local; don't put a key in source, a PR, screenshots or test logs. Environment variables `GOOGLE_MAPS_API_KEY` and `GOOGLE_MAPS_MAP_ID` override the file.

The development `DEMO_MAP_ID` enables advanced markers. It is not an API key. A production map can use its own JavaScript Map ID. A **Maps Demo Key** is a separate Google credential option for limited prototyping; a standard Maps key uses a billing-enabled project. This implementation does not assume which credential type the user supplied or manage its billing/quota.

Restrict the browser key in Google Cloud:

- Application restriction: **Websites**. For this preview, allow `http://127.0.0.1:8019/*` and, if used, `http://localhost:8019/*`.
- API restriction: **Maps JavaScript API**. This app does not need Places, Geocoding or Routes; city coordinates already exist locally.
- Add actual deployment origins before hosting. Review your account's usage limits separately.

The browser must receive the Maps key to load Google's SDK; it is not a server-only secret. The local `/api/map-config` endpoint exposes only the two browser settings, returns no-store, and rejects non-local Host/cross-origin Origin values. It does not expose other environment entries. Raw dotfiles are not served. These development-server checks do not replace Google's website/API restrictions, whose account settings have not been inspected.

## Behaviour

Google Maps loads only when opening Map view with `?map=google` and a configured key, not when opening directly in Album view. Google owns map tiles, attribution and its normal map requests. The app overlays the existing 19 city centres, trip counts/tiers and selected photo thumbnail. Our code does not upload the local photo files or travel notes to Google. Cloud memory generation remains unconnected.

Custom markers use AdvancedMarkerElement with `gmp-click`, keyboard support and the existing exact-city chooser for nearby pins. Filters update markers; selection connects to the same album/drafts. Zoom and fit use Google's geographic view. A timeout, rejected key or SDK load failure restores the local map with a visible explanation. Reload retries; `?map=local` intentionally avoids Google loading.

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
