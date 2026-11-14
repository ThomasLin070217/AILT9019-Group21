# Fresh clone and restore verification — 14 November 2026

A new HTTPS clone of public main `0115b19fc67006825c795c4b32c6e1aaf21c9a56`, with a new virtual environment, passed the pinned-dependency install, **68 Python tests and 22 Node tests**. Environment: macOS 15.7.9 arm64, Python 3.13.7, Node v24.11.1. This is assistant-operated on the same development Mac, not independent teammate/device acceptance.

The real `python -m backend --port 8052` server was exercised over HTTP against isolated runtime folders:

- Served the app; created one `jp-osaka` trip; uploaded the synthetic T02 park image; edited the memory.
- Missing AI configuration returned 503 and left the trip unchanged. No cloud calls were made.
- Invalid image bytes were rejected and left the trip unchanged.
- Process restart preserved the complete trip snapshot and photo SHA-256.
- With the server stopped, copied the database and media into a backup, restored them into a different directory and restarted against that location. The snapshot and photo hash matched.

Evidence: `fresh-clone.json`, `pytest.txt`, `node-tests.txt`, `install.txt`, `server.txt`, `fresh_check.py`.
The first harness attempt used unsupported city ID `osaka`; the server correctly rejected it. The harness was corrected to the catalogue ID `jp-osaka`. This was a harness input error, not an application fix. The script's paths describe the isolated run and must be changed for another machine; ordinary reproduction instructions remain in README. All test servers were stopped after checking.

This closes Thomas's same-computer fresh-environment/restore check. Owen's independent computer acceptance, Angel's physical-device checks, human AI scoring and final video recording remain separate tasks.
