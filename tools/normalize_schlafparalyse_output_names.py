#!/usr/bin/env python3
"""Normalize only generated-output names inside the local EP06-EP08 kits.

This deliberately does not copy or regenerate prompts.  It updates the queue and
prompt documentation in place so their requested output names match the flat
IMGxxx/SHOTxx files already used by production.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPISODES = ("EP06", "EP07", "EP08")


def normalized(text: str) -> str:
    for episode in EPISODES:
        text = re.sub(rf"\b{episode}_IMG(\d{{3}})_", r"IMG\1_", text)
        text = re.sub(rf"\b{episode}_RSV(\d{{2}})_", r"SHOT\1_", text)
        text = re.sub(rf"\b{episode}_SHOT(\d{{2}})_", r"SHOT\1_", text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write changes; without this flag the script only reports them",
    )
    args = parser.parse_args()

    changed: list[Path] = []
    for episode in EPISODES:
        kit = ROOT / "06_PRODUCTION" / f"{episode}_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT"
        candidates = [kit / "GENERATION_QUEUE.csv"]
        candidates.extend(sorted((kit / "01_PROMPTS").glob("*.md")))
        for path in candidates:
            if not path.is_file():
                continue
            before = path.read_text(encoding="utf-8-sig")
            after = normalized(before)
            if before == after:
                continue
            changed.append(path)
            if args.apply:
                path.write_text(after, encoding="utf-8", newline="")

    mode = "updated" if args.apply else "would update"
    print(f"{mode}: {len(changed)} file(s)")
    for path in changed:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
