"""Run one approved fixture through the integrated API and save its unedited reply.

Run only with an authorised provider configuration. Results stay under Git-ignored
var/evaluation/ until the team checks permissions and decides what to publish.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from backend.ai import build_generator, generator_configured
from backend.ai.responses import PROMPT_VERSION
from backend.app import create_app
from backend.config import REPO_ROOT, Settings


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one T01–T05 case on the integrated AI route.")
    parser.add_argument("case", choices=[f"T{number:02d}" for number in range(1, 6)])
    parser.add_argument("--confirm-send", action="store_true", help="Acknowledge that the fixture image and notes go to the configured cloud provider.")
    parser.add_argument("--allow-angel-photo", action="store_true", help="For T03 only: confirm Angel's permission and provider terms have been checked.")
    args = parser.parse_args()

    fixture = REPO_ROOT / "data" / "fixtures" / args.case
    case = json.loads((fixture / "case.json").read_text(encoding="utf-8"))
    if args.case == "T03" and not args.allow_angel_photo:
        parser.error("T03 uses Angel's photograph; check permission/provider terms, then pass --allow-angel-photo.")
    if not args.confirm_send:
        parser.error("This sends the fixture to a third-party provider. Pass --confirm-send after reviewing the case.")

    source_settings = Settings.from_env()
    generator = build_generator(source_settings)
    if not generator_configured(generator):
        parser.error("No AI provider is configured. Set the ignored .env.ai.local first; do not put a key in Git.")

    with tempfile.TemporaryDirectory(prefix="travel-memory-eval-") as temporary:
        root = Path(temporary)
        settings = replace(source_settings, db_path=root / "travel.db", media_dir=root / "media", tmp_dir=root / "tmp")
        with TestClient(create_app(settings=settings, generator=generator)) as client:
            payload = {"city_id": case["input"]["city_id"], "notes": case["input"]["notes"]}
            created = client.post("/api/trips", json=payload)
            created.raise_for_status()
            trip_id = created.json()["id"]
            for filename in case["input"]["photos"]:
                photo = fixture / filename
                mime = "image/png" if photo.suffix.lower() == ".png" else "image/jpeg"
                with photo.open("rb") as stream:
                    uploaded = client.post(f"/api/trips/{trip_id}/photos", files={"file": (filename, stream, mime)})
                uploaded.raise_for_status()
            before = client.get(f"/api/trips/{trip_id}").json()
            reply = client.post(f"/api/trips/{trip_id}/memory", json={"confirmed": True})
            after = client.get(f"/api/trips/{trip_id}").json()
            if after != before:
                raise RuntimeError("AI route changed the saved trip; result not recorded as a valid run.")

    record = {
        "case_id": args.case,
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": source_settings.ai_model,
        "prompt_version": PROMPT_VERSION,
        "ai_timeout_seconds": source_settings.ai_timeout_seconds,
        "http_status": reply.status_code,
        "unedited_app_response": reply.json(),
        "saved_trip_unchanged": True,
        "human_reviews": [],
        "note": "The integrated API response is unedited. Human factual scoring and provider usage/cost are not supplied by this script.",
    }
    folder = REPO_ROOT / "var" / "evaluation"
    folder.mkdir(parents=True, exist_ok=True)
    try:
        folder.chmod(0o700)
    except OSError:
        pass
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = folder / f"{stamp}-{args.case}.json"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        json.dump(record, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(f"Saved unedited {args.case} response to {path} (HTTP {reply.status_code}).")
    return 0 if reply.status_code == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
