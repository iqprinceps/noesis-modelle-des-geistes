#!/usr/bin/env python3
"""Unpack the verified Schlafparalyse V4 prompt package into the repo tree.

Usage from repository root:
    python3 tools/unpack_schlafparalyse_prompts_v4.py

The script verifies the committed ZIP by SHA-256, blocks path traversal,
and refuses to overwrite different existing files unless --force is used.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

ZIP_REL = Path("03_EPISODEN/TYPE_B/SCHLAFPARALYSE_PROMPTS_V4_REPO_READY.zip")
EXPECTED_SHA256 = "5f414def0f6e9eda90dc35dc111fd152d414e1708c77f486df60d80976fe37d5"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def safe_target(root: Path, member: str) -> Path:
    target = (root / member).resolve()
    root_resolved = root.resolve()
    try:
        target.relative_to(root_resolved)
    except ValueError as exc:
        raise RuntimeError(f"Unsafe ZIP path: {member}") from exc
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing files even if their content differs",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="only verify ZIP checksum and contents; do not extract",
    )
    args = parser.parse_args()

    root = repo_root()
    archive = root / ZIP_REL
    if not archive.is_file():
        print(f"ERROR: package not found: {archive}", file=sys.stderr)
        return 2

    actual_sha = sha256_file(archive)
    if actual_sha != EXPECTED_SHA256:
        print("ERROR: ZIP checksum mismatch", file=sys.stderr)
        print(f"expected: {EXPECTED_SHA256}", file=sys.stderr)
        print(f"actual:   {actual_sha}", file=sys.stderr)
        return 3

    with zipfile.ZipFile(archive) as zf:
        members = [m for m in zf.infolist() if not m.is_dir()]
        for info in members:
            safe_target(root, info.filename)

        print(f"Verified package: {archive.relative_to(root)}")
        print(f"SHA-256: {actual_sha}")
        print(f"Files: {len(members)}")

        if args.check_only:
            return 0

        written = 0
        skipped = 0
        for info in members:
            target = safe_target(root, info.filename)
            data = zf.read(info)

            if target.exists() and not args.force:
                existing = target.read_bytes()
                if existing == data:
                    skipped += 1
                    continue
                print(
                    f"ERROR: refusing to overwrite different file: {target.relative_to(root)}\n"
                    "Re-run with --force only if you intentionally want to replace it.",
                    file=sys.stderr,
                )
                return 4

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            written += 1

    print(f"Extracted/updated: {written}")
    print(f"Already identical: {skipped}")
    print("Schlafparalyse V4 prompt files are ready in EP06, EP07 and EP08.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
