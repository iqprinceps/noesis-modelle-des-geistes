#!/usr/bin/env python3
"""Fail when production image prompts are hidden outside their episode folder."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPE_B = ROOT / "03_EPISODEN" / "TYPE_B"


def relevant_episode(d: Path) -> bool:
    return d.is_dir() and re.match(r"^EP\d{2}[A-Z]?_", d.name) is not None


def main() -> int:
    errors: list[str] = []
    checked = 0
    for ep in sorted(p for p in TYPE_B.iterdir() if relevant_episode(p)):
        has_prompt_signal = any(ep.glob("NANOBANANA*")) or any(
            (ROOT / "PRODUCTION_SUMMARY").glob(f"{ep.name.split('_')[0]}*/NANOBANANA_PROMPTS_V*_S*.md")
        )
        if not has_prompt_signal:
            continue
        checked += 1
        guides = list(ep.glob("NANOBANANA_GUIDE_V*.md"))
        batches = list(ep.glob("NANOBANANA_PROMPTS_V*_S*.md"))
        if not guides:
            errors.append(f"{ep.relative_to(ROOT)}: missing local NANOBANANA_GUIDE_V*.md")
        if not batches:
            errors.append(f"{ep.relative_to(ROOT)}: missing local NANOBANANA_PROMPTS_V*_S*.md")
        for batch in batches:
            text = batch.read_text(encoding="utf-8")
            if "Referenz:" not in text or "Prompt:" not in text:
                errors.append(f"{batch.relative_to(ROOT)}: entries are not full Dateiname/Referenz/Prompt format")
    if errors:
        print("IMAGE PROMPT LAYOUT: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"IMAGE PROMPT LAYOUT: OK ({checked} episode folders checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
