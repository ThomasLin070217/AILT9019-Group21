# Public interactive demo — 17 November 2026

Supplemental URL: https://thomaslin070217.github.io/AILT9019-Group21/play/app/?mode=demo&map=local

The existing sample-data mode is published through the main-branch `/docs` Pages source. `scripts/build_public_demo.py` copies only public UI assets, sample covers, city catalogue and map data. No backend, personal fixture, API key or runtime storage is included. The copy check compares all 26 generated files byte for byte with their sources.

Assistant-operated browser verification against the Pages directory served locally:
- Loaded 19 cities, with 9 fictional seed trips across 5 visited cities.
- Selected unvisited Beijing and added a sample visit: area tier changed from 0 to 1; total became 10 trips / 6 cities.
- Edited its sample memory and saved; after reload the changed text remained.
- Added a second Beijing trip: separate card, 2 visits, area tier 2.
- Switched to Album; sample cards and photos rendered.

No live AI calls were made. This checks the public sample interaction, not hosted AI/upload functionality, independent human ratings or the final YouTube submission requirements. Two YouTube links remain pending in `docs/submission_links.txt`.
