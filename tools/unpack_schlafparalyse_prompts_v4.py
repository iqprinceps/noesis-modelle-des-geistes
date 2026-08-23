#!/usr/bin/env python3
"""Compatibility check for the old Schlafparalyse prompt-unpack command.

Prompts are now canonical Markdown files committed directly in EP06, EP07 and
EP08, matching the EP05 Jung-Pauli layout. Nothing is unpacked anymore.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODES = [
    ROOT / "03_EPISODEN/TYPE_B/EP06_SCHLAFPARALYSE_01",
    ROOT / "03_EPISODEN/TYPE_B/EP07_SCHLAFPARALYSE_02",
    ROOT / "03_EPISODEN/TYPE_B/EP08_SCHLAFPARALYSE_03",
]


def main() -> int:
    missing: list[str] = []
    for ep in EPISODES:
        if not list(ep.glob("NANOBANANA_GUIDE_V*.md")):
            missing.append(f"{ep.relative_to(ROOT)}: guide")
        if len(list(ep.glob("NANOBANANA_PROMPTS_V*_S*.md"))) < 4:
            missing.append(f"{ep.relative_to(ROOT)}: prompt batches")
    if missing:
        print("ERROR: canonical direct prompt files are incomplete:", file=sys.stderr)
        for item in missing:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("Schlafparalyse prompts are already committed directly in EP06-EP08.")
    print("No ZIP extraction is required. This command remains only for compatibility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
