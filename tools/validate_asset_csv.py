#!/usr/bin/env python3
"""Validate NOESIS asset CSV manifests before automated acquisition."""
from __future__ import annotations
import csv
import pathlib
import re
import sys

MACHINE_STATUS_HEADERS = {"status", "verification_state", "acquisition_state"}
MACHINE_STATUS_RE = re.compile(r"^[A-Z0-9]+(?:[_/-][A-Z0-9]+)*$")


def validate(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, strict=True))
    if not rows:
        return [f"{path}: empty CSV"]
    width = len(rows[0])
    if any(not name.strip() for name in rows[0]):
        errors.append(f"{path}: blank header name")
    if len(set(rows[0])) != width:
        errors.append(f"{path}: duplicate header names")
    for lineno, row in enumerate(rows[1:], 2):
        if len(row) != width:
            errors.append(f"{path}:{lineno}: expected {width} fields, got {len(row)}")
    id_cols = [i for i, h in enumerate(rows[0]) if h.lower() in {"asset_id", "source_id"}]
    for i in id_cols:
        seen: dict[str, int] = {}
        for lineno, row in enumerate(rows[1:], 2):
            if len(row) != width:
                continue
            value = row[i].strip()
            if not value:
                errors.append(f"{path}:{lineno}: blank {rows[0][i]}")
            elif value in seen:
                errors.append(
                    f"{path}:{lineno}: duplicate {rows[0][i]}={value!r}; "
                    f"first seen on line {seen[value]}"
                )
            else:
                seen[value] = lineno
    # Rights descriptions are intentionally free text. Only workflow-state
    # columns use machine-readable uppercase tokens.
    status_cols = [i for i, h in enumerate(rows[0]) if h.lower() in MACHINE_STATUS_HEADERS]
    for lineno, row in enumerate(rows[1:], 2):
        if len(row) != width:
            continue
        for i in status_cols:
            value = row[i].strip()
            if not value:
                errors.append(f"{path}:{lineno}: blank {rows[0][i]}")
            elif not MACHINE_STATUS_RE.fullmatch(value):
                errors.append(
                    f"{path}:{lineno}: invalid machine status "
                    f"{rows[0][i]}={value!r}"
                )
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
