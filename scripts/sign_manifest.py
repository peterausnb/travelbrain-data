from __future__ import annotations

import argparse
import base64
import hashlib
import os
import re
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from jsonschema import Draft202012Validator

from common import ROOT, canonical_json_bytes, load_json

ALGORITHM = "ECDSA_P256_SHA256"
KEY_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def create_signature_envelope(
    manifest_bytes: bytes,
    private_key_pem: bytes,
    key_id: str,
) -> dict[str, object]:
    if not manifest_bytes or len(manifest_bytes) > 512 * 1024:
        raise ValueError("manifest must contain between 1 byte and 512 KiB")
    if not KEY_ID_PATTERN.fullmatch(key_id):
        raise ValueError("invalid signing key id")

    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    if not isinstance(private_key, ec.EllipticCurvePrivateKey) or not isinstance(
        private_key.curve,
        ec.SECP256R1,
    ):
        raise ValueError("signing key must use the P-256 curve")

    signature = private_key.sign(manifest_bytes, ec.ECDSA(hashes.SHA256()))
    private_key.public_key().verify(signature, manifest_bytes, ec.ECDSA(hashes.SHA256()))
    envelope: dict[str, object] = {
        "schemaVersion": 1,
        "algorithm": ALGORITHM,
        "keyId": key_id,
        "manifestSha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    schema = load_json(ROOT / "schemas/manifest-signature.schema.json")
    Draft202012Validator(schema).validate(envelope)
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign the exact TravelBrain manifest bytes")
    parser.add_argument("--manifest", type=Path, default=ROOT / "dist/manifest.json")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/manifest.sig.json")
    args = parser.parse_args()

    private_key = os.environ.get("TRAVELBRAIN_SIGNING_KEY_PEM")
    key_id = os.environ.get("TRAVELBRAIN_SIGNING_KEY_ID")
    if not private_key or not key_id:
        parser.error("TRAVELBRAIN_SIGNING_KEY_PEM and TRAVELBRAIN_SIGNING_KEY_ID are required")
    manifest_bytes = args.manifest.read_bytes()
    envelope = create_signature_envelope(manifest_bytes, private_key.encode("utf-8"), key_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_json_bytes(envelope))
    print(f"Manifest signed with key id {key_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
