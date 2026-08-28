#!/usr/bin/env python3
"""Replace one locked state in both EP01 cue and required-asset records."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
CUE = EP / "06_TIMELINE/EP01_EN_VISUAL_CUE_SHEET.csv"
REQUIRED = EP / "06_TIMELINE/EP01_EN_REQUIRED_ASSET_SET.json"


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: ep01_replace_locked_state.py OLD NEW SELECTED_PATH")
    old, new, selected_path = sys.argv[1:]
    with CUE.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    changed = 0
    for row in rows:
        if row["visual_state_id"] == old:
            row["visual_state_id"] = new
            row["selected_asset_id"] = new
            row["selected_file_path"] = selected_path
            row["visual_action"] = row["visual_action"].replace(old, new)
            changed += 1
    with CUE.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    required = json.loads(REQUIRED.read_text(encoding="utf-8"))
    required_changed = 0
    for family in required.values():
        for state in family.get("states", []):
            if state.get("state_id") == old:
                state["state_id"] = new
                state["selected_file_path"] = selected_path
                state["visual_action"] = state.get("visual_action", "").replace(old, new)
                state["content_sha256"] = "PENDING_FINALIZER"
                required_changed += 1
    REQUIRED.write_text(json.dumps(required, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if changed != 1 or required_changed != 1:
        raise RuntimeError(f"replacement count cue={changed} required={required_changed}")
    print(json.dumps({"old": old, "new": new, "cue": changed, "required": required_changed}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
