#!/usr/bin/env python3
"""Normalize NOESIS asset CSV manifests before validation/acquisition.

All fields must already be valid RFC-4180 CSV.  The normalizer deliberately
does not guess whether an unquoted comma belongs to a URL or separates fields:
that distinction is ambiguous when a row contains several URLs.  Known legacy
rows are repaired explicitly in their manifests; this tool then performs a
lossless parse-and-write canonicalization and refuses malformed input.
"""
from __future__ import annotations

import csv
import io
import pathlib
import sys


def normalize_text(text: str, source: str = '<memory>') -> str:
    if not text:
        raise ValueError(f'{source}: empty CSV')

    rows = list(csv.reader(io.StringIO(text), strict=True))
    if not rows:
        raise ValueError(f'{source}: empty CSV after parsing')

    width = len(rows[0])
    bad = [(lineno, len(row)) for lineno, row in enumerate(rows[1:], 2) if len(row) != width]
    if bad:
        detail = ', '.join(f'line {n}: {w} fields' for n, w in bad)
        raise ValueError(
            f'{source}: normalization refused; expected {width} fields; {detail}. '
            'Repair the ambiguous row explicitly before acquisition.'
        )

    out = io.StringIO(newline='')
    writer = csv.writer(out, lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    return out.getvalue()


def normalize_file(path: pathlib.Path, check_only: bool) -> bool:
    original = path.read_text(encoding='utf-8-sig')
    normalized = normalize_text(original, str(path))
    changed = normalized != original
    if changed and not check_only:
        path.write_text(normalized, encoding='utf-8', newline='')
    return changed


def main() -> int:
    args = sys.argv[1:]
    check_only = False
    if '--check' in args:
        check_only = True
        args.remove('--check')

    paths = [pathlib.Path(p) for p in args]
    if not paths:
        paths = sorted(pathlib.Path('07_ENGLISH_PRODUCTION').glob('EP*_PINEAL_*/**/*.csv'))

    failures: list[str] = []
    changed: list[str] = []
    for path in paths:
        try:
            if normalize_file(path, check_only=check_only):
                changed.append(str(path))
        except (OSError, csv.Error, ValueError) as exc:
            failures.append(str(exc))

    if failures:
        print('CSV NORMALIZATION FAILED')
        print('\n'.join(failures))
        return 1

    if check_only and changed:
        print('CSV NORMALIZATION REQUIRED')
        print('\n'.join(changed))
        return 2

    action = 'would normalize' if check_only else 'normalized'
    print(f'CSV NORMALIZATION OK: {len(paths)} file(s); {action} {len(changed)} file(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
