#!/usr/bin/env python3
"""Normalize legacy NOESIS asset CSV manifests before validation/acquisition.

The historical Pineal manifests contain a small class of malformed rows where a
literal comma inside a URL path (usually a Wikimedia/Wikisource filename) was
not quoted.  csv.reader therefore sees extra columns.  This tool repairs only
that mechanically identifiable case, then rewrites the complete file through
csv.writer so every field is RFC-4180-safe.

It deliberately refuses to guess when a row is still structurally ambiguous.
"""
from __future__ import annotations

import csv
import io
import pathlib
import re
import sys

# The problematic legacy URLs are file-like endpoints.  Matching to the file
# extension lets us distinguish commas *inside* the URL from the CSV delimiter
# immediately following the URL.
FILE_URL_RE = re.compile(
    r'https?://[^"\s]+?\.(?:jpg|jpeg|png|svg|pdf|djvu|tif|tiff|webp)(?=,|$)',
    re.IGNORECASE,
)


def encode_url_commas(line: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return match.group(0).replace(',', '%2C')
    return FILE_URL_RE.sub(repl, line)


def normalize_text(text: str, source: str = '<memory>') -> str:
    physical_lines = text.splitlines()
    if not physical_lines:
        raise ValueError(f'{source}: empty CSV')

    repaired = '\n'.join(encode_url_commas(line) for line in physical_lines) + '\n'
    rows = list(csv.reader(io.StringIO(repaired), strict=True))
    if not rows:
        raise ValueError(f'{source}: empty CSV after parsing')

    width = len(rows[0])
    bad = [(lineno, len(row)) for lineno, row in enumerate(rows[1:], 2) if len(row) != width]
    if bad:
        detail = ', '.join(f'line {n}: {w} fields' for n, w in bad)
        raise ValueError(
            f'{source}: normalization refused; expected {width} fields; {detail}. '
            'This is not a URL-comma case and requires an explicit human repair.'
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
