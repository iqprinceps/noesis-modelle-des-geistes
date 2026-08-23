#!/usr/bin/env python3
"""Apply canonical Schlafparalyse V5 visual coverage after the existing V4 prep.

Run from repo root:
    python3 tools/prepare_schlafparalyse_visuals_v5.py

This does not delete the V4 prompt pool. It adds episode-specific shot/mix targets
and writes VISUAL_CUE_SHEET_V5.csv files for EP06-EP08 so production no longer
interprets the trilogy as three identical 56+8 AI-image packages.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "PRODUCTION_SUMMARY"

TARGETS = {
    "EP06": {
        "dir": "EP06_SCHLAFPARALYSE_V4",
        "acts": [
            (20,2,16,2,"subjective bedroom / paralysis / presence"),
            (18,7,9,2,"Newfoundland / Old Hag / cultural anchor"),
            (19,13,3,3,"REM atonia / PSG / sleep science"),
            (19,6,9,4,"Intruder / Incubus / vestibular families"),
            (19,14,2,3,"sleep lab / Takeuchi process"),
            (18,6,9,3,"body vs visitor / threat attribution"),
            (22,5,13,4,"presence mystery peak"),
            (14,5,2,7,"residue / final model / handoff"),
        ],
        "repeat": "no identical frame; same presence silhouette max 3x episode; bed/shadow max 2 shots in a row; science anchor every 20-30s of subjective recon",
    },
    "EP07": {
        "dir": "EP07_SCHLAFPARALYSE_V4",
        "acts": [
            (19,13,4,2,"Salem primary documents first"),
            (18,11,4,3,"Fuseli / Abildgaard / nightmare iconography"),
            (19,10,3,6,"many names / culture map / source-safe context"),
            (19,11,4,4,"culture shapes interpretation"),
            (18,11,2,5,"Hufford inversion / research"),
            (19,10,4,5,"experience vs culture loop"),
            (20,14,2,4,"Egypt vs Denmark / study comparison"),
            (14,8,4,2,"story propagation / EP08 handoff"),
        ],
        "repeat": "no identical frame; Fuseli max 4 semantic crops; document reuse only full/name-date/passage/detail; archive anchor about every 25s",
    },
    "EP08": {
        "dir": "EP08_SCHLAFPARALYSE_V4",
        "acts": [
            (20,10,3,7,"Art Bell / radio / fax / response counter"),
            (19,4,12,3,"Shadow People subjective world"),
            (18,7,7,4,"abduction overlap / UFO culture context"),
            (17,10,2,5,"Harvard / memory research"),
            (22,3,15,4,"Hat Man mystery peak"),
            (19,6,7,6,"pattern vs meme / expectation"),
            (20,10,6,4,"early web / CRT / feedback"),
            (15,8,5,2,"brain-experience-story-expectation loop"),
        ],
        "repeat": "no identical frame; full Hat Man only from S5; same silhouette max 4x episode; change visual mode every 20-25s; max 3 similar mystery recons in a row",
    },
}


def run_v4_prep() -> None:
    p = ROOT / "tools" / "prepare_schlafparalyse_production_inputs.py"
    if p.is_file():
        subprocess.run([sys.executable, str(p)], cwd=ROOT, check=True)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    run_v4_prep()
    for ep, cfg in TARGETS.items():
        prod = SUMMARY / cfg["dir"]
        src = prod / "VISUAL_CUE_SHEET.csv"
        if not src.is_file():
            raise SystemExit(f"Missing V4 cue sheet: {src}")
        rows = read_rows(src)
        if len(rows) != 8:
            raise SystemExit(f"Expected 8 cue rows for {ep}, found {len(rows)}")

        out = prod / "VISUAL_CUE_SHEET_V5.csv"
        fields = list(rows[0].keys()) + [
            "planned_shots", "original_target", "recon_target", "motion_target",
            "visual_priority_v5", "repeat_lock_v5",
        ]
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for row, target in zip(rows, cfg["acts"]):
                shots, orig, recon, motion, priority = target
                row = dict(row)
                row.update({
                    "planned_shots": str(shots),
                    "original_target": str(orig),
                    "recon_target": str(recon),
                    "motion_target": str(motion),
                    "visual_priority_v5": priority,
                    "repeat_lock_v5": cfg["repeat"],
                })
                w.writerow(row)
        total = sum(x[0] for x in cfg["acts"])
        print(f"{ep}: wrote {out.relative_to(ROOT)} ({total} target shots)")

    print("Schlafparalyse V5 visual coverage applied. V4 prompt pool preserved as reserve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
