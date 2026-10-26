# Travel Memory Map quick start

This guide covers the current integrated branch. Use fictional notes and a
permission-cleared photo for testing; the local album persists its records.

## Run the complete local album

From the repository root, with Python 3.10+:

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python3 -m backend
```

Open **http://127.0.0.1:8019/app/?mode=api**. The map uses online street tiles
by default; append `&map=local` for the bundled offline map. No AI or Google key
is needed for this core workflow.

1. Choose a supported city, then select **Add a memory**.
2. Enter a title or notes and save the trip. Add a JPG, PNG or WebP photo to its card.
3. Edit and save the memory. Reload the page: the card and photo remain in the
   local SQLite album, and the city's visit count remains one.
4. Add another trip in the same city. It becomes a separate card and the city's
   highlighted area changes visit tier.

The browser's **Write with AI** action displays exactly what will be sent and
requires a second click. With no provider configured it returns an honest error
and leaves the trip unchanged. To enable Thomas's OpenAI-compatible Responses
adapter, use the server-side settings in [the backend guide](BACKEND.md). A
generated draft must be reviewed and saved separately.

## Fictional no-install demo

Run `python3 serve.py` and open **http://127.0.0.1:8019/app/?map=local**.
This is a sample map with fictional Osaka visits, kept in browser storage. It
does not upload photos, create real trips or call AI. Stop one server before
starting the other on the same port.

Use **Reset sample album** in the demo footer when finished. To preserve real
API-mode trips, back up `var/travel.db` and `var/media/` together; see the
[backend guide](BACKEND.md).
