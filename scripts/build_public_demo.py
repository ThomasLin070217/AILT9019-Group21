"""Copy only public UI assets into the existing /docs GitHub Pages site.
Run after changing app/ or the public sample/map data. No backend, fixtures or
runtime files are published. --check detects stale/missing/extra outputs.
"""
from pathlib import Path
import argparse
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/play"

def assets():
    files = {}
    for folder in ("app", "data/map", "data/demo-covers"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and path.suffix in {".html", ".mjs", ".js", ".css", ".ttf", ".woff2", ".json", ".geojson", ".jpg", ".png", ".md", ".txt"}:
                files[path.relative_to(ROOT)] = path.read_bytes()
    for name in ("cities.json", "demo-trips.json", "README.md", "SOURCES.json"):
        path = ROOT / "data" / name
        files[path.relative_to(ROOT)] = path.read_bytes()
    return files

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = assets()
    if args.check:
        actual = {p.relative_to(DEST): p.read_bytes() for p in DEST.rglob("*") if p.is_file()}
        if actual != expected:
            raise SystemExit("Public demo is stale. Run python3 scripts/build_public_demo.py")
        print(f"Public demo matches {len(expected)} allowlisted source files.")
        return
    if DEST.exists():
        shutil.rmtree(DEST)
    for relative, content in expected.items():
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    print(f"Built {len(expected)} public files in docs/play.")

if __name__ == "__main__":
    main()
