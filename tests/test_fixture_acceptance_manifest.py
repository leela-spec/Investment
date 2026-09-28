from hashlib import sha256
from pathlib import Path

import yaml


MANIFEST = Path("configs/fixture_acceptance.yaml")


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_fixtures() -> tuple[dict, list[dict]]:
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    fixtures = (
        data["transcripts"]
        + data["research_documents"]
        + data["portfolios"]
        + [data["macro_snapshot"]]
    )
    return data, fixtures


def test_fixture_manifest_resolves_and_hashes_match():
    data, fixtures = load_fixtures()

    assert data["mode"] == "offline_read_only"
    for fixture in fixtures:
        path = Path(fixture["evidence_file"])
        assert path.is_file(), fixture["id"]
        assert digest(path) == fixture["sha256"], fixture["id"]


def test_fixture_manifest_cannot_direct_outputs_into_source_fixtures():
    _, fixtures = load_fixtures()

    for fixture in fixtures:
        assert "output_path" not in fixture, fixture["id"]

    allowed_runtime_root = Path("implementation-runs/fixture-acceptance")
    assert allowed_runtime_root.parts == (
        "implementation-runs",
        "fixture-acceptance",
    )
