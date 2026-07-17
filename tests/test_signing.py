from __future__ import annotations

import base64
import hashlib
import sys
import unittest
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sign_manifest import ALGORITHM, create_signature_envelope  # noqa: E402


class ManifestSigningTest(unittest.TestCase):
    def setUp(self) -> None:
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.private_key_pem = self.private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        self.manifest = b'{"contentVersion":"2026.07.17.1"}'

    def test_signature_matches_exact_manifest_bytes(self) -> None:
        envelope = create_signature_envelope(
            self.manifest,
            self.private_key_pem,
            "travelbrain-data-2026-01",
        )

        self.assertEqual(envelope["schemaVersion"], 1)
        self.assertEqual(envelope["algorithm"], ALGORITHM)
        self.assertEqual(envelope["manifestSha256"], hashlib.sha256(self.manifest).hexdigest())
        self.private_key.public_key().verify(
            base64.b64decode(str(envelope["signature"]), validate=True),
            self.manifest,
            ec.ECDSA(hashes.SHA256()),
        )

    def test_modified_manifest_does_not_verify(self) -> None:
        envelope = create_signature_envelope(
            self.manifest,
            self.private_key_pem,
            "travelbrain-data-2026-01",
        )

        with self.assertRaises(InvalidSignature):
            self.private_key.public_key().verify(
                base64.b64decode(str(envelope["signature"]), validate=True),
                self.manifest + b"\n",
                ec.ECDSA(hashes.SHA256()),
            )

    def test_invalid_key_id_and_wrong_curve_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            create_signature_envelope(self.manifest, self.private_key_pem, "invalid key id")

        p384_key = ec.generate_private_key(ec.SECP384R1()).private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        with self.assertRaises(ValueError):
            create_signature_envelope(self.manifest, p384_key, "travelbrain-data-2026-01")


if __name__ == "__main__":
    unittest.main()
