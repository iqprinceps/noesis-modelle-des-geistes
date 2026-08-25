#!/usr/bin/env python3
"""Validate the improved EP06-EP08 edit and camera policy on a built timeline."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


STATIC_KINDS = {"CARD", "SOURCE_STATIC"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("timeline", type=Path)
    args = parser.parse_args()
    data = json.loads(args.timeline.read_text(encoding="utf-8"))
    shots = data.get("shots", [])
    if not shots:
        raise SystemExit("FAIL: timeline has no shots")

    failures: list[str] = []
    paths = [shot.get("visual", "") for shot in shots if shot.get("visual")]
    counts = Counter(paths)
    reused_slots = sum(count - 1 for count in counts.values() if count > 1)
    reuse_ratio = reused_slots / max(1, len(paths))

    if shots[0].get("duration", 99) > 2.5:
        failures.append(f"first visual change is too late ({shots[0]['duration']:.2f}s)")
    if reuse_ratio > 0.15:
        failures.append(f"repeated-slot ratio {reuse_ratio:.1%} exceeds 15%")
    overused = {path: count for path, count in counts.items() if count > 2}
    if overused:
        failures.append(f"{len(overused)} media path(s) are used more than twice")
    adjacent = [a for a, b in zip(paths, paths[1:]) if a == b]
    if adjacent:
        failures.append(f"{len(adjacent)} directly repeated identical visual(s)")

    movable_stills = 0
    moved_stills = 0
    for shot in shots:
        kind = shot.get("kind", "STILL")
        policy = shot.get("motion_policy", "")
        duration = float(shot.get("duration", 0))
        sid = str(shot.get("shot_id", ""))
        if kind in STATIC_KINDS and not policy.startswith("STATIC_"):
            failures.append(f"{sid}: {kind} must be static, got {policy}")
        if kind == "VIDEO" and policy != "NATIVE_CLIP_NO_EXTERNAL_CAMERA":
            failures.append(f"{sid}: clip has external camera policy {policy}")
        if kind == "CARD" and duration > 6.0 and "END" not in sid.upper():
            failures.append(f"{sid}: non-endcard duration {duration:.2f}s exceeds 6s")
        if kind != "VIDEO" and duration > 9.0 and not (kind == "CARD" and "END" in sid.upper()):
            failures.append(f"{sid}: still duration {duration:.2f}s exceeds 9s")
        if kind == "STILL":
            movable_stills += 1
            moved_stills += int(policy == "SUBTLE_STILL")

    moved_ratio = moved_stills / max(1, movable_stills)
    if moved_ratio > 0.60:
        failures.append(f"moving ordinary-still ratio {moved_ratio:.1%} exceeds 60%")

    print(f"Timeline: {args.timeline}")
    print(f"Shots: {len(shots)}; unique media: {len(counts)}; repeated slots: {reuse_ratio:.1%}")
    print(f"Ordinary stills moving: {moved_stills}/{movable_stills} ({moved_ratio:.1%})")
    policies = Counter(str(shot.get("motion_policy", "MISSING")) for shot in shots)
    for policy, count in sorted(policies.items()):
        print(f"  {policy}: {count}")

    if failures:
        print("\nEDIT POLICY: NOT READY")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nEDIT POLICY: READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
