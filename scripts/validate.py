from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from common import ROOT, load_json, load_yaml


def referenced_source_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "sourceRefs" and isinstance(child, list):
                found.update(str(item) for item in child)
            else:
                found.update(referenced_source_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(referenced_source_ids(child))
    return found


def validate_file(path: Path, schema_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        data = load_yaml(path)
        schema = load_json(schema_path)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{path.relative_to(ROOT)}:{location}: {error.message}")
        return data, errors
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
        return None, errors


def validate_country(path: Path) -> list[str]:
    data, errors = validate_file(path, ROOT / "schemas/country.schema.json")
    if data is None or errors:
        return errors

    iso2 = data["country"]["iso2"]
    if path.stem != iso2.lower():
        errors.append(f"{path.relative_to(ROOT)}: filename must match ISO-2 code {iso2.lower()}.yaml")

    source_ids = [source["id"] for source in data["sources"]]
    if len(source_ids) != len(set(source_ids)):
        errors.append(f"{path.relative_to(ROOT)}: duplicate source id")

    missing = referenced_source_ids(data.get("content", {})) - set(source_ids)
    if missing:
        errors.append(f"{path.relative_to(ROOT)}: unresolved sourceRefs: {sorted(missing)}")

    review = data["review"]
    reviewed = date.fromisoformat(review["reviewedAt"])
    next_review = date.fromisoformat(review["nextReviewAt"])
    if next_review < reviewed:
        errors.append(f"{path.relative_to(ROOT)}: nextReviewAt is before reviewedAt")

    if review["status"] == "approved" and data["country"]["coverage"] == "unavailable":
        errors.append(f"{path.relative_to(ROOT)}: approved country cannot be unavailable")
    if review["status"] == "approved" and not data["sources"]:
        errors.append(f"{path.relative_to(ROOT)}: approved country requires at least one source")
    if review["status"] == "approved" and data["country"]["coverage"] == "complete":
        required_modules = {"entry", "road", "money", "power", "emergency", "phrases"}
        missing_modules = required_modules - set(data["content"])
        if missing_modules:
            errors.append(
                f"{path.relative_to(ROOT)}: complete country misses modules: {sorted(missing_modules)}"
            )
    return errors


def validate_corridor(path: Path, known_countries: set[str]) -> list[str]:
    data, errors = validate_file(path, ROOT / "schemas/corridor.schema.json")
    if data is None or errors:
        return errors
    if path.stem != data["id"]:
        errors.append(f"{path.relative_to(ROOT)}: filename must match corridor id")
    for option in data["options"]:
        unknown = set(option["countries"]) - known_countries - {"DE"}
        if unknown:
            errors.append(f"{path.relative_to(ROOT)}: unknown corridor countries: {sorted(unknown)}")
    return errors


def main() -> int:
    errors: list[str] = []
    country_paths = sorted((ROOT / "countries").glob("*.yaml"))
    known_countries: set[str] = set()
    for path in country_paths:
        data = load_yaml(path)
        if isinstance(data, dict) and isinstance(data.get("country"), dict):
            known_countries.add(str(data["country"].get("iso2", "")))
        errors.extend(validate_country(path))

    for path in sorted((ROOT / "corridors").glob("*.yaml")):
        errors.extend(validate_corridor(path, known_countries))

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validation successful: {len(country_paths)} countries checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
