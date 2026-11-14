"""Validate/assemble local final files. Never uploads or submits anything."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from zipfile import ZIP_DEFLATED, ZipFile


def youtube_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port:
        raise ValueError("Use an HTTPS YouTube URL without credentials or a custom port")
    host = parsed.hostname
    path = parsed.path.strip("/").split("/")
    if host in {"youtu.be", "www.youtu.be"} and len(path) == 1:
        identity = path[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if path == ["watch"]:
            values = parse_qs(parsed.query).get("v", [])
            identity = values[0] if len(values) == 1 else ""
        elif len(path) == 2 and path[0] in {"shorts", "live", "embed"}:
            identity = path[1]
        else:
            identity = ""
    else:
        identity = ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", identity):
        raise ValueError("A real YouTube video ID is required, not a channel/playlist/placeholder")
    return identity


def validate_text(links: str, pdf_text: str, pages: int) -> list[str]:
    errors = []
    if not 1 <= pages <= 5:
        errors.append("Expected a 1–5 page body-only report; inspect appendix boundaries manually if adding one")
    required = ["Group 21", "https://github.com/ThomasLin070217/AILT9019-Group21", "https://thomaslin070217.github.io/AILT9019-Group21/"]
    if any(value not in links for value in required):
        errors.append("Team ID, repository or public webpage URL is missing from the links file")
    video_ids = []
    flat_pdf = re.sub(r"\s+", "", pdf_text)
    for label in ["Presentation YouTube link", "Demo YouTube link"]:
        rows = [line.split(":", 1)[1].strip() for line in links.splitlines() if line.startswith(label + ":")]
        if len(rows) != 1:
            errors.append(f"Supply exactly one {label}")
            continue
        try:
            video_ids.append(youtube_id(rows[0]))
            if re.sub(r"\s+", "", rows[0]) not in flat_pdf:
                errors.append(f"{label} must also appear in the report")
        except ValueError as error:
            errors.append(f"{label}: {error}")
    if len(video_ids) == 2 and video_ids[0] == video_ids[1]:
        errors.append("Presentation and demo must be different videos, not two URL forms of the same video")
    if "recording/upload pending" in pdf_text.lower():
        errors.append("The report identification block still says recording/upload pending")
    if re.search(r"(?:sk-sp-[A-Za-z0-9._-]{15,}|AIza[A-Za-z0-9_-]{25,}|Bearer\s+[A-Za-z0-9._-]{20,})", links + "\n" + pdf_text):
        errors.append("Possible credential in submission text; inspect and remove it before packaging")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Directory containing report.pdf and submission_links.txt")
    parser.add_argument("--output", type=Path, help="Create a new ZIP after checks; omit to check only")
    args = parser.parse_args(argv)
    try:
        from pypdf import PdfReader
    except ImportError:
        parser.error("Install requirements-submission.txt before reading the PDF")
    folder = args.folder.resolve()
    try:
        reader = PdfReader(folder / "report.pdf")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        errors = validate_text((folder / "submission_links.txt").read_text(encoding="utf-8"), text, len(reader.pages))
    except Exception as error:
        print(f"Cannot check submission: {type(error).__name__}: {error}")
        return 1
    if errors:
        print("NOT READY:\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    if args.output:
        with ZipFile(args.output, "x", ZIP_DEFLATED) as archive:
            for name in ["report.pdf", "submission_links.txt"]:
                archive.write(folder / name, name)
        if args.output.stat().st_size > 100_000_000:
            args.output.unlink()
            print("ZIP exceeds 100 MB; new archive removed")
            return 1
        print(f"Created local archive: {args.output.resolve()}")
    print("Structural checks passed. Still verify signed-out playback, Zoom duration, all speakers/names, readable captions and actual team review. Nothing uploaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
