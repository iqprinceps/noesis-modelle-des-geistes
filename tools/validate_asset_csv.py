#!/usr/bin/env python3
"""Validate NOESIS asset CSV manifests before automated acquisition."""
from __future__ import annotations
import csv
import pathlib
import sys

ALLOWED_STATUS_PREFIXES = (
    "VERIFIED", "CLEARED", "SOURCE", "REFERENCE", "HOLD", "PENDING",
    "REPLACED", "EXCLUDED", "RIGHTS", "OPEN", "PUBLIC", "CC", "PD",
)


def validate(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, strict=True))
    if not rows:
        return [f"{path}: empty CSV"]
    width = len(rows[0])
    if len(set(rows[0])) != width:
        errors.append(f"{path}: duplicate header names")
    for lineno, row in enumerate(rows[1:], 2):
        if len(row) != width:
            errors.append(f"{path}:{lineno}: expected {width} fields, got {len(row)}")
    # Status columns are intentionally discovered by name because episode schemas differ.
    status_cols = [i for i, h in enumerate(rows[0]) if "status" in h.lower() or "state" in h.lower()]
    for lineno, row in enumerate(rows[1:], 2):
        if len(row) != width:
            continue
        for i in status_cols:
            value = row[i].strip()
            if value and not value.upper().startswith(ALLOWED_STATUS_PREFIXES):
                errors.append(f"{path}:{lineno}: suspicious {rows[0][i]}={value!r}")
    return errors


def main() -> int:
    paths = [pathlib.Path(p) for p in sys.argv[1:]]
    if not paths:
        paths = list(pathlib.Path("07_ENGLISH_PRODUCTION").glob("EP*_PINEAL_*/**/*.csv"))
    failures: list[str] = []
    for path in paths:
        try:
            failures.extend(validate(path))
        except (OSError, csv.Error) as exc:
            failures.append(f"{path}: parser error: {exc}")
    if failures:
        print("CSV VALIDATION FAILED")
        print("\n".join(failures))
        return 1
    print(f"CSV VALIDATION OK: {len(paths)} file(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
