#!/usr/bin/env python3
"""Materialize the legacy Schlafparalyse V4 prompt package into episode folders.

The historical repository file may be a real ZIP, a base64-text wrapper, or a
ZIP whose central directory was lost. In the last case we recover only complete
local file entries and verify their CRC before writing anything.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import io
import struct
import sys
import zipfile
import zlib
from pathlib import Path

ZIP_REL = Path("03_EPISODEN/TYPE_B/SCHLAFPARALYSE_PROMPTS_V4_REPO_READY.zip")
EXPECTED_PAYLOAD_SHA256 = "b490ec50fea91644191fff71ee10f6ffbcff23160f2dc95d1dd7a52681da674e"
LOCAL_SIG = b"PK\x03\x04"


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


def load_payload(path: Path) -> tuple[bytes, str]:
    raw = path.read_bytes()
    if raw.startswith(LOCAL_SIG):
        return raw, "binary ZIP payload"
    compact = b"".join(raw.split())
    try:
        decoded = base64.b64decode(compact, validate=True)
    except Exception as exc:
        raise RuntimeError("package is neither ZIP nor valid base64-wrapped ZIP") from exc
    if not decoded.startswith(LOCAL_SIG):
        raise RuntimeError("decoded package does not start with a ZIP local header")
    return decoded, "legacy base64-wrapped ZIP payload"


def normal_zip_entries(payload: bytes) -> list[tuple[str, bytes]]:
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        return [(i.filename, zf.read(i)) for i in zf.infolist() if not i.is_dir()]


def salvage_local_entries(payload: bytes) -> list[tuple[str, bytes]]:
    """Recover complete ZIP local entries when the central directory is missing."""
    entries: list[tuple[str, bytes]] = []
    pos = 0
    while pos + 30 <= len(payload) and payload[pos:pos + 4] == LOCAL_SIG:
        (
            _sig, _ver, flags, method, _mtime, _mdate, crc32_expected,
            compressed_size, uncompressed_size, name_len, extra_len,
        ) = struct.unpack_from("<IHHHHHIIIHH", payload, pos)
        if flags & 0x08:
            raise RuntimeError("cannot safely salvage ZIP entries using data descriptors")
        name_start = pos + 30
        name_end = name_start + name_len
        data_start = name_end + extra_len
        data_end = data_start + compressed_size
        if data_end > len(payload):
            raise RuntimeError("legacy ZIP ends inside a file entry; refusing partial extraction")
        name_bytes = payload[name_start:name_end]
        encoding = "utf-8" if (flags & 0x800) else "cp437"
        name = name_bytes.decode(encoding)
        compressed = payload[data_start:data_end]
        if method == 0:
            data = compressed
        elif method == 8:
            data = zlib.decompress(compressed, -15)
        else:
            raise RuntimeError(f"unsupported compression method {method} for {name}")
        if len(data) != uncompressed_size:
            raise RuntimeError(f"size mismatch while salvaging {name}")
        if (binascii.crc32(data) & 0xFFFFFFFF) != crc32_expected:
            raise RuntimeError(f"CRC mismatch while salvaging {name}")
        if not name.endswith("/"):
            entries.append((name, data))
        pos = data_end
    if not entries:
        raise RuntimeError("no complete local ZIP entries could be recovered")
    return entries


def read_entries(payload: bytes) -> tuple[list[tuple[str, bytes]], str]:
    try:
        return normal_zip_entries(payload), "normal ZIP"
    except zipfile.BadZipFile:
        return salvage_local_entries(payload), "salvaged local ZIP entries (CRC verified)"


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
        payload, package_form = load_payload(archive)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    actual_sha = sha256_bytes(payload)
    if actual_sha != EXPECTED_PAYLOAD_SHA256:
        print("ERROR: decoded payload checksum mismatch", file=sys.stderr)
        print(f"expected: {EXPECTED_PAYLOAD_SHA256}", file=sys.stderr)
        print(f"actual:   {actual_sha}", file=sys.stderr)
        return 4

    try:
        entries, read_mode = read_entries(payload)
        for name, _ in entries:
            safe_target(root, name)
    except (RuntimeError, zlib.error, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 5

    print(f"Verified package: {archive.relative_to(root)} ({package_form})")
    print(f"Payload SHA-256: {actual_sha}")
    print(f"Read mode: {read_mode}")
    print(f"Complete files: {len(entries)}")
    if args.check_only:
        return 0

    written = 0
    skipped = 0
    for name, data in entries:
        target = safe_target(root, name)
        if target.exists() and not args.force:
            if target.read_bytes() == data:
                skipped += 1
                continue
            print(
                f"ERROR: refusing to overwrite different file: {target.relative_to(root)}\n"
                "Re-run with --force only if you intentionally want to replace it.",
                file=sys.stderr,
            )
            return 6
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        written += 1

    print(f"Extracted/updated: {written}")
    print(f"Already identical: {skipped}")
    print("Schlafparalyse V4 prompt markdown is materialized in EP06, EP07 and EP08.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
