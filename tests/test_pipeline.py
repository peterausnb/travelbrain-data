from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PipelineTest(unittest.TestCase):
    def test_validation_succeeds(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_only_approved_countries_are_published(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((ROOT / "dist/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["countries"]), {"AT", "CH", "IT"})
        for country in manifest["countries"].values():
            self.assertIn(country["coverage"], {"complete", "partial"})
            self.assertRegex(country["sha256"], r"^[a-f0-9]{64}$")


if __name__ == "__main__":
    unittest.main()
