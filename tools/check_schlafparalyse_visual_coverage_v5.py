#!/usr/bin/env python3
"""QA the local render-manifest coverage for Schlafparalyse V5.

This checker does not judge artistic quality. It catches the production failure
mode that prompted V5: too few media paths causing long holds or obvious reuse.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = {
    "EP06": dict(out="EP06_SCHLAFPARALYSE_V4", total=149, acts=[20,18,19,19,19,18,22,14]),
    "EP07": dict(out="EP07_SCHLAFPARALYSE_V4", total=146, acts=[19,18,19,19,18,19,20,14]),
    "EP08": dict(out="EP08_SCHLAFPARALYSE_V4", total=150, acts=[20,19,18,17,22,19,20,15]),
}


def flatten(value):
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(x) for x in value if x]
    return []


def main() -> int:
    p = argparse.ArgumentParser(description="Check Schlafparalyse V5 visual coverage before render.")
    p.add_argument("episode", choices=CFG)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--allow-shortfall", type=int, default=5,
                   help="Allowed total media-path shortfall versus target (default: 5).")
    args = p.parse_args()
    cfg = CFG[args.episode]
    manifest = args.manifest or (ROOT / "06_PRODUCTION" / cfg["out"] / "render_manifest.json")
    if not manifest.is_file():
        print(f"FAIL: render manifest missing: {manifest}")
        return 2

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assets = data.get("assets", data)
    if not isinstance(assets, dict):
        print("FAIL: manifest must contain an object or an 'assets' object")
        return 2

    act_paths = []
    all_paths = []
    for i in range(1, 9):
        keys = [f"S{i}", f"S{i:02d}"]
        value = None
        for key in keys:
            if key in assets:
                value = assets[key]
                break
        paths = flatten(value)
        act_paths.append(paths)
        all_paths.extend(paths)

    # Some manifests use custom cue IDs rather than S1-S8. In that case count
    # everything, but act-level QA cannot be asserted safely.
    act_keyed = any(act_paths)
    if not act_keyed:
        all_paths = []
        for value in assets.values():
            all_paths.extend(flatten(value))

    counts = Counter(all_paths)
    duplicates = {k: v for k, v in counts.items() if v > 2}
    reused_slots = sum(count - 1 for count in counts.values() if count > 1)
    reuse_ratio = reused_slots / max(1, len(all_paths))
    adjacent = []
    for paths in act_paths:
        for a, b in zip(paths, paths[1:]):
            if a == b:
                adjacent.append(a)

    fail = False
    target = cfg["total"]
    total = len(all_paths)
    print(f"{args.episode} V5 coverage")
    print(f"Manifest: {manifest}")
    print(f"Media paths: {total} / target {target}")
    print(f"Unique paths: {len(counts)}; repeated slots: {reused_slots} ({reuse_ratio:.1%})")

    if total < target - args.allow_shortfall:
        print(f"FAIL: coverage shortfall {target-total} exceeds allowed {args.allow_shortfall}")
        fail = True
    else:
        print("OK: total coverage is within target tolerance")

    if act_keyed:
        for i, (paths, need) in enumerate(zip(act_paths, cfg["acts"]), 1):
            status = "OK" if len(paths) >= need - 1 else "LOW"
            print(f"  S{i}: {len(paths):>2} / {need}  {status}")
            if status == "LOW":
                fail = True
    else:
        print("NOTE: custom cue IDs detected; act-level counts skipped")

    if adjacent:
        print(f"FAIL: {len(adjacent)} consecutive identical path occurrence(s)")
        fail = True
    else:
        print("OK: no consecutive identical paths in S1-S8 lists")

    if duplicates:
        print("WARN: base paths used more than twice:")
        for path, count in sorted(duplicates.items(), key=lambda x: (-x[1], x[0]))[:20]:
            print(f"  {count}x {path}")
        # More than twice is a hard V5 repeat-rule violation unless the editor
        # deliberately replaces entries with semantic crops as separate files.
        fail = True
    else:
        print("OK: no path used more than twice")

    if reuse_ratio > 0.15:
        print(f"FAIL: repeated-slot ratio {reuse_ratio:.1%} exceeds the improved 15% ceiling")
        fail = True
    else:
        print("OK: repeated-slot ratio <= 15%")

    missing = [x for x in all_paths if not (Path(x) if Path(x).is_absolute() else ROOT / x).is_file()]
    if missing:
        print(f"FAIL: {len(missing)} referenced media path(s) are missing locally")
        for path in missing[:20]:
            print(f"  {path}")
        fail = True
    else:
        print("OK: all referenced media paths exist locally")

    if fail:
        print("\nV5 visual gate: NOT READY — add/replace concrete coverage before render.")
        return 1
    print("\nV5 visual gate: READY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
