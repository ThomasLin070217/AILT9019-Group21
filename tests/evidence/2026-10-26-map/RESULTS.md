# City map visual check — 26 October 2026

The default OpenFreeMap/MapLibre map loaded in the in-app browser at both the demo preview (`http://127.0.0.1:8032/app/`) and an isolated local API preview (`http://127.0.0.1:8033/app/?mode=api`). The API preview used a temporary SQLite database under `/private/tmp`, not the team's saved album.

Manual checks:

- 19 supported city markers appeared on a geographically aligned East Asia basemap. The muted Positron style kept labels and context visible.
- **View area** fitted Osaka's boundary. Its two demo visits filled the area with the 2–3 tier, while the marker showed 2 and the photo thumbnail remained attached. See `desktop-preview.png`.
- Tokyo's unvisited boundary remained outlined. Adding one fictional demo visit filled the region and changed the marker/count to 1; removing that test visit returned it to unlit and the demo count to its original 5 cities / 9 trips.
- In an isolated API database, saving one Osaka trip changed the map to 1 city / 1 trip and filled Osaka. Deleting that temporary trip restored 0 cities / 0 trips after reload. No real user records were changed.
- The local map still loads with `?map=local`. Without a configured key, explicit `?map=google` displays a clear notice and falls back to the local map. A live Google-key run was not performed for this change.

Automated checks: `npm test` passed 22 tests; `python -m pytest -q` passed 55; JavaScript syntax checks and `git diff --check` passed.

Limits: city geometries are bundled OpenStreetMap snapshots and may differ slightly from live basemap boundaries. External tiles require network access; the local map is the fallback. This visual check used the desktop preview plus a narrow in-app browser view, not a physical phone.
