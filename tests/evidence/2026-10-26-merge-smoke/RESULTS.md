# Merge smoke check — 26 October 2026

Branch head tested: `c6e7ac6` (`integration/owen-backend`), before the
documentation-only evidence update and PR #4 merge. Local FastAPI backend at
`http://127.0.0.1:8034/app/?mode=api`; browser defaulted to the OpenFreeMap
street basemap. Inputs were fictional text and the synthetic
`data/fixtures/T01/01-blue-red.png`, never a personal photo.

| Check | Observed result |
| --- | --- |
| Create an Osaka trip | API-mode card appeared; city count 0 → 1 and selected area was labelled lit. |
| Upload synthetic PNG | Card showed one photo; UI reported removal of location/camera metadata. |
| Edit and save memory | New text appeared; visit count stayed 1. |
| Reload page | Trip, edited text and photo remained; city count stayed 1. |
| Open AI notice and confirm without a provider | Notice listed city, date, title, notes and sanitised photos; request failed visibly with “No AI provider is configured”; saved trip remained. |
| Save a second Osaka trip | Two separate cards appeared; city count became 2 and UI reported a brighter area. |
| Cleanup | Both test trips were deleted through the local API; `GET /api/trips` returned an empty list. |

The browser check does not validate a real cloud response, provider retention,
physical-device accessibility, or a fresh installation. Backend tests:
`60 passed`; front-end tests: `22 passed`. No CI checks are configured on PR #4.
