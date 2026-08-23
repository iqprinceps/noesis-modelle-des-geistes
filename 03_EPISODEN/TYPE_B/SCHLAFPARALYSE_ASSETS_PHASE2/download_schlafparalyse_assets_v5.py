#!/usr/bin/env python3
"""Download Schlafparalyse V5 base assets plus verified V5 additions.

The historical Phase-2 manifest remains intact. This wrapper runs the proven
resilient downloader twice into the same local runtime root, so existing files
are skipped and V5 additions receive the same retry/rate-limit/type checks.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "asset_manifest.csv"
ADD = HERE / "asset_manifest_v5_additions.csv"
DOWNLOADER = HERE / "download_schlafparalyse_assets.py"
DEFAULT_ROOT = Path.cwd() / "SCHLAFPARALYSE_ASSETS_PHASE2"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download NOESIS Schlafparalyse V5 source assets.")
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    p.add_argument("--only", choices=["EP06", "EP07", "EP08"], action="append")
    p.add_argument("--green-only", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--timeout", type=int, default=90)
    p.add_argument("--retries", type=int, default=5)
    p.add_argument("--wikimedia-delay", type=float, default=2.0)
    p.add_argument("--no-wikimedia-thumbnails", action="store_true")
    return p


def run_manifest(manifest: Path, args: argparse.Namespace) -> int:
    cmd = [
        sys.executable, str(DOWNLOADER),
        "--manifest", str(manifest),
        "--root", str(args.root),
        "--timeout", str(args.timeout),
        "--retries", str(args.retries),
        "--wikimedia-delay", str(args.wikimedia_delay),
    ]
    for ep in args.only or []:
        cmd += ["--only", ep]
    if args.green_only:
        cmd.append("--green-only")
    if args.dry_run:
        cmd.append("--dry-run")
    if args.force:
        cmd.append("--force")
    if args.no_wikimedia_thumbnails:
        cmd.append("--no-wikimedia-thumbnails")
    return subprocess.run(cmd, cwd=HERE).returncode


def main() -> int:
    args = parser().parse_args()
    failures = []
    for label, manifest in (("base", BASE), ("v5 additions", ADD)):
        print(f"\n=== {label}: {manifest.name} ===")
        rc = run_manifest(manifest, args)
        if rc:
            failures.append(label)
    if failures:
        print("\nOne or more manifest passes reported failed assets: " + ", ".join(failures), file=sys.stderr)
        print("Successful files remain downloaded; rerunning will skip them.", file=sys.stderr)
        return 1
    print("\nSchlafparalyse V5 source asset passes completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
