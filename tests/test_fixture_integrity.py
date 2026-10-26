"""Keep prepared AI cases loadable before any model run is reported."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_prepared_ai_fixtures_reference_real_cities_and_verified_images():
    city_ids = {city["id"] for city in json.loads((ROOT / "data/cities.json").read_text())}
    fixture_root = ROOT / "data/fixtures"
    cases = sorted(fixture_root.glob("T*/case.json"))
    assert {"T01", "T03", "T04", "T05"} <= {path.parent.name for path in cases}

    for case_path in cases:
        case = json.loads(case_path.read_text())
        assert case["id"] == case_path.parent.name
        assert case["input"]["city_id"] in city_ids
        assert case["status"] == "prepared_not_run"
        assert case["results"] == []
        assert case["input"]["photos"]
        for filename in case["input"]["photos"]:
            photo = case_path.parent / filename
            assert photo.is_file(), photo
            expected = case["source"]["sha256"][filename]
            assert hashlib.sha256(photo.read_bytes()).hexdigest() == expected
