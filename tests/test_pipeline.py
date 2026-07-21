from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PipelineTest(unittest.TestCase):
    @staticmethod
    def build_env() -> dict[str, str]:
        return os.environ | {
            "SOURCE_DATE_EPOCH": "1767225600",
            "BUILD_SEQUENCE": "42",
        }

    def test_validation_succeeds(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=self.build_env(),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_only_approved_countries_are_published(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=self.build_env(),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((ROOT / "dist/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["contentVersion"], "2026.01.01.42")
        self.assertEqual(
            set(manifest["countries"]),
            {
                "AT", "BE", "CH", "CZ", "DK", "ES", "FR", "GB", "GR", "HR",
                "HU", "IT", "LU", "NL", "NO", "PL", "PT", "SE", "SI", "SK",
            },
        )
        for country in manifest["countries"].values():
            self.assertIn(country["coverage"], {"complete", "partial"})
            self.assertRegex(country["sha256"], r"^[a-f0-9]{64}$")
        self.assertRegex(manifest["corridors"]["sha256"], r"^[a-f0-9]{64}$")

    def test_build_is_reproducible_with_fixed_metadata(self) -> None:
        command = [sys.executable, str(ROOT / "scripts/build.py")]
        first = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, env=self.build_env())
        self.assertEqual(first.returncode, 0, first.stderr.decode())
        expected = (ROOT / "dist/manifest.json").read_bytes()
        second = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, env=self.build_env())
        self.assertEqual(second.returncode, 0, second.stderr.decode())
        self.assertEqual((ROOT / "dist/manifest.json").read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
