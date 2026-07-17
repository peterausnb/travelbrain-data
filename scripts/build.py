from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from common import ROOT, canonical_json_bytes, load_json, load_yaml


def write_json(path: Path, value: object) -> str:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def build_metadata() -> tuple[datetime, str]:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    now = datetime.fromtimestamp(int(epoch), timezone.utc) if epoch else datetime.now(timezone.utc)
    sequence = os.environ.get("BUILD_SEQUENCE", "1")
    if not sequence.isdigit() or int(sequence) < 1:
        raise ValueError("BUILD_SEQUENCE must be a positive integer")
    return now, f"{now:%Y.%m.%d}.{sequence}"


def main() -> int:
    dist = ROOT / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    (dist / "countries").mkdir(parents=True)

    now, version = build_metadata()
    countries: dict[str, object] = {}

    for path in sorted((ROOT / "countries").glob("*.yaml")):
        data = load_yaml(path)
        if data["review"]["status"] != "approved":
            continue
        iso2 = data["country"]["iso2"]
        relative_path = f"countries/{iso2.lower()}.json"
        sha256 = write_json(dist / relative_path, data)
        countries[iso2] = {
            "coverage": data["country"]["coverage"],
            "version": version,
            "sha256": sha256,
            "path": relative_path,
        }

    approved_corridors = [
        load_yaml(path)
        for path in sorted((ROOT / "corridors").glob("*.yaml"))
        if load_yaml(path)["status"] == "approved"
    ]
    corridors_sha256 = write_json(dist / "corridors.json", approved_corridors)

    manifest = {
        "schemaVersion": 1,
        "contentVersion": version,
        "generatedAt": now.isoformat().replace("+00:00", "Z"),
        "minimumAppSchemaVersion": 1,
        "countries": countries,
        "corridors": {
            "version": version,
            "sha256": corridors_sha256,
            "path": "corridors.json",
        },
    }
    manifest_schema = load_json(ROOT / "schemas/manifest.schema.json")
    Draft202012Validator(manifest_schema, format_checker=FormatChecker()).validate(manifest)
    write_json(dist / "manifest.json", manifest)
    (dist / ".nojekyll").write_text("", encoding="utf-8")
    (dist / "index.html").write_text(
        "<!doctype html><html lang=\"de\"><meta charset=\"utf-8\">"
        "<title>TravelBrain Data</title><h1>TravelBrain Data</h1>"
        "<p>Maschinenlesbare Reisedaten. Einstieg: "
        "<a href=\"manifest.json\">manifest.json</a></p>",
        encoding="utf-8",
    )
    print(f"Build successful: {len(countries)} approved countries emitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
