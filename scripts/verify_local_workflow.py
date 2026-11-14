"""Portable real-server check, with disposable storage and cloud AI disabled.

Install requirements.txt first. Run from a clone with:
    python -m scripts.verify_local_workflow --output var/reproduction/my-check
No developer-specific paths, credentials, personal album or cloud calls are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--python", default=sys.executable, help="Python with this clone's requirements installed")
    parser.add_argument("--port", type=int, default=0, help="Free local port; 0 selects one automatically")
    parser.add_argument("--output", type=Path, help="New evidence directory; existing directories are never overwritten")
    args = parser.parse_args(argv)
    root = args.repo.expanduser().resolve()
    if not (root / "backend/__main__.py").is_file():
        parser.error("--repo must point to a Travel Memory Map clone")
    if not 0 <= args.port <= 65535:
        parser.error("--port must be 0 through 65535")
    out = (args.output or root / "var/reproduction" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")).resolve()
    out.mkdir(parents=True, exist_ok=False)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", args.port))
        port = reservation.getsockname()[1]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("AI_", "TRAVEL_AI_", "TMM_"))}
    # Explicit empty entries also suppress keys that might exist in local dotenv files.
    env.update({k: "" for k in ("AI_PROVIDER", "AI_API_KEY", "AI_MODEL", "AI_BASE_URL", "TRAVEL_AI_API_KEY", "TRAVEL_AI_MODEL", "TRAVEL_AI_BASE_URL")})
    proc = None
    checks = []
    result = {"run_at_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
              "os": platform.platform(), "cloud_requests": 0, "checks": checks,
              "operator": "Not inferred; the person running this must add their name separately."}
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    result["commit"] = git.stdout.strip() if git.returncode == 0 else "not available"
    result["source_sha256"] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in
        ["backend/db.py", "backend/storage/trips.py", "backend/routers/trips.py", "app/repository.mjs", "scripts/verify_local_workflow.py"]}
    def stop():
        nonlocal proc
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)
            proc = None
    def check(condition, label):
        if not condition:
            raise AssertionError(label)
        checks.append({"check": label, "passed": True})
    with tempfile.TemporaryDirectory(prefix="tmm-verification-") as tmp, (out / "server.txt").open("w") as log, httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10, trust_env=False) as client:
        work = Path(tmp)
        def start(target):
            nonlocal proc
            env.update(TMM_DB_PATH=str(target / "travel.db"), TMM_MEDIA_DIR=str(target / "media"), TMM_TMP_DIR=str(target / "tmp"))
            proc = subprocess.Popen([args.python, "-m", "backend", "--host", "127.0.0.1", "--port", str(port)], cwd=root, env=env, stdout=log, stderr=log)
            for _ in range(150):
                if proc.poll() is not None:
                    raise RuntimeError("Backend exited; inspect server.txt")
                try:
                    if client.get("/api/health").status_code == 200:
                        return
                except httpx.TransportError:
                    pass
                time.sleep(.1)
            raise RuntimeError("Backend did not become ready")
        try:
            state = work / "album"
            start(state)
            check(client.get("/api/health").json()["ai_configured"] is False, "Cloud AI disabled for this check")
            check(client.get("/api/trips").json() == [], "Isolated album starts empty")
            check(client.get("/app/?mode=api&map=local").status_code == 200, "API-mode app is served")
            payload = {"city_id": "jp-osaka", "title": "Portable check", "notes": "Fictional test record"}
            headers = {"Idempotency-Key": "portable-test-first"}
            created = client.post("/api/trips", json=payload, headers=headers)
            check(created.status_code == 201, "Create trip")
            tid = created.json()["id"]
            replay = client.post("/api/trips", json=payload, headers=headers)
            check(replay.status_code == 201 and replay.json()["id"] == tid and len(client.get("/api/trips").json()) == 1, "Retry creates no extra visit")
            conflict = client.post("/api/trips", json={**payload, "notes": "Changed"}, headers=headers)
            check(conflict.status_code == 409, "Changed payload with reused key is rejected")
            with (root / "data/fixtures/T02/park-bench.png").open("rb") as image:
                response = client.post(f"/api/trips/{tid}/photos", files={"file": ("park.png", image, "image/png")})
            check(response.status_code == 201, "Upload synthetic photo")
            url = response.json()["url"]
            photo_hash = hashlib.sha256(client.get(url).content).hexdigest()
            response = client.patch(f"/api/trips/{tid}", json={"memory_text": "Edited synthetic memory"})
            check(response.status_code == 200, "Edit memory")
            snapshot = client.get("/api/trips").json()
            check(client.post(f"/api/trips/{tid}/memory", json={"confirmed": True}).status_code == 503 and client.get("/api/trips").json() == snapshot, "Missing AI configuration preserves album")
            invalid = client.post(f"/api/trips/{tid}/photos", files={"file": ("bad.png", b"not an image", "image/png")})
            check(invalid.status_code in (415, 422) and client.get("/api/trips").json() == snapshot, "Invalid image is rejected without changing album")
            stop(); start(state)
            check(client.get("/api/trips").json() == snapshot and hashlib.sha256(client.get(url).content).hexdigest() == photo_hash, "Restart preserves text and photo bytes")
            check(client.post("/api/trips", json=payload, headers=headers).json()["id"] == tid, "Retry key survives restart")
            stop()
            shutil.copytree(state, work / "backup")
            shutil.copytree(work / "backup", work / "restored")
            start(work / "restored")
            check(client.get("/api/trips").json() == snapshot and hashlib.sha256(client.get(url).content).hexdigest() == photo_hash, "Stopped-server DB and media backup restores correctly")
            second = client.post("/api/trips", json=payload, headers={"Idempotency-Key": "portable-test-second"})
            check(second.status_code == 201 and second.json()["id"] != tid and len(client.get("/api/trips").json()) == 2, "New key permits intentional same-city return visit")
            check(client.delete(f"/api/trips/{tid}").status_code == 204, "Delete trip")
            check(client.post("/api/trips", json=payload, headers=headers).status_code == 410 and len(client.get("/api/trips").json()) == 1, "Old retry cannot resurrect deleted trip")
            result.update(status="passed", photo_sha256=photo_hash)
        except Exception as error:
            result.update(status="failed", error=f"{type(error).__name__}: {error}")
        finally:
            stop()
            (out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {len(checks)} checks; evidence: {out}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
