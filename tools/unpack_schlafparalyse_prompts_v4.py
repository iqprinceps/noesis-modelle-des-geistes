#!/usr/bin/env python3
"""Materialize the legacy Schlafparalyse V4 prompt package into episode folders.

The historical repository file named *.zip may be either a real ZIP or a
base64-text wrapper around that ZIP. Both forms are accepted, but the decoded
ZIP payload must match the locked SHA-256 before extraction.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import sys
import zipfile
from pathlib import Path

ZIP_REL = Path("03_EPISODEN/TYPE_B/SCHLAFPARALYSE_PROMPTS_V4_REPO_READY.zip")
EXPECTED_PAYLOAD_SHA256 = "b490ec50fea91644191fff71ee10f6ffbcff23160f2dc95d1dd7a52681da674e"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def safe_target(root: Path, member: str) -> Path:
    target = (root / member).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Unsafe ZIP path: {member}") from exc
    return target


def load_zip_payload(path: Path) -> tuple[bytes, str]:
    raw = path.read_bytes()
    if raw.startswith(b"PK\x03\x04"):
        return raw, "binary ZIP"

    compact = b"".join(raw.split())
    try:
        decoded = base64.b64decode(compact, validate=True)
    except Exception as exc:
        raise RuntimeError(
            f"Prompt package is neither ZIP nor valid base64-wrapped ZIP: {path}"
        ) from exc
    if not decoded.startswith(b"PK\x03\x04"):
        raise RuntimeError("Decoded prompt package does not contain a ZIP payload")
    return decoded, "legacy base64-wrapped ZIP"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite different existing files")
    parser.add_argument("--check-only", action="store_true", help="verify package and members only")
    args = parser.parse_args()

    root = repo_root()
    archive = root / ZIP_REL
    if not archive.is_file():
        print(f"ERROR: package not found: {archive}", file=sys.stderr)
        return 2

    try:
        payload, package_form = load_zip_payload(archive)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    actual_sha = sha256_bytes(payload)
    if actual_sha != EXPECTED_PAYLOAD_SHA256:
        print("ERROR: decoded ZIP payload checksum mismatch", file=sys.stderr)
        print(f"expected: {EXPECTED_PAYLOAD_SHA256}", file=sys.stderr)
        print(f"actual:   {actual_sha}", file=sys.stderr)
        return 4

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        members = [m for m in zf.infolist() if not m.is_dir()]
        for info in members:
            safe_target(root, info.filename)

        print(f"Verified package: {archive.relative_to(root)} ({package_form})")
        print(f"Decoded ZIP SHA-256: {actual_sha}")
        print(f"Files: {len(members)}")
        if args.check_only:
            return 0

        written = 0
        skipped = 0
        for info in members:
            target = safe_target(root, info.filename)
            data = zf.read(info)
            if target.exists() and not args.force:
                if target.read_bytes() == data:
                    skipped += 1
                    continue
                print(
                    f"ERROR: refusing to overwrite different file: {target.relative_to(root)}\n"
                    "Re-run with --force only if you intentionally want to replace it.",
                    file=sys.stderr,
                )
                return 5
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            written += 1

    print(f"Extracted/updated: {written}")
    print(f"Already identical: {skipped}")
    print("Schlafparalyse V4 prompt markdown is materialized in EP06, EP07 and EP08.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
