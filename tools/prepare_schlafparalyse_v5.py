#!/usr/bin/env python3
"""Prepare Schlafparalyse EP06-EP08 with individualized V5 visual coverage.

The proven V4 builder remains responsible for voice/audio/motion handoff files.
Prompts are already committed directly in each episode folder; the compatibility
unpack helper does not extract the legacy ZIP anymore. V5 then replaces the
generic visual cue language with episode-specific targets.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPE_B = ROOT / "03_EPISODEN" / "TYPE_B"
SUMMARY = ROOT / "PRODUCTION_SUMMARY"

CFG = {
    "EP06": dict(summary="EP06_SCHLAFPARALYSE_V4", episode="EP06_SCHLAFPARALYSE_01",
                 shots=149, pool="32 MAIN + 8 RESERVE", acts=[20,18,19,19,19,18,22,14],
                 mixes=["2O/16R/2M","7O/9R/2M","13O/3R/3M","6O/9R/4M","14O/2R/3M","6O/9R/3M","5O/13R/4M","5O/2R/7M"],
                 modes=["intimate reconstruction","Newfoundland archive + reconstruction","science archive + explanatory motion","reconstruction + classification motion","sleep-lab archive + procedural motion","body/presence reconstruction + motion","presence reconstruction + hypothesis motion","archive callback + final motion"]),
    "EP07": dict(summary="EP07_SCHLAFPARALYSE_V4", episode="EP07_SCHLAFPARALYSE_02",
                 shots=146, pool="20 MAIN + 4 RESERVE", acts=[19,18,19,19,18,19,20,14],
                 mixes=["13O/4R/2M","11O/4R/3M","10O/3R/6M","11O/4R/4M","11O/2R/5M","10O/4R/5M","14O/2R/4M","8O/4R/2M"],
                 modes=["Salem primary documents + restrained reconstruction","historical art + semantic detail crops","culture archive + map/typography","historical sources + interpretation motion","research/archive + thesis motion","archive + feedback motion","study/country context + comparison motion","historical callback + transition reconstruction"]),
    "EP08": dict(summary="EP08_SCHLAFPARALYSE_V4", episode="EP08_SCHLAFPARALYSE_03",
                 shots=150, pool="32 MAIN + 8 RESERVE", acts=[20,19,18,17,22,19,20,15],
                 mixes=["10O/3R/7M","4O/12R/3M","7O/7R/4M","10O/2R/5M","3O/15R/4M","6O/7R/6M","10O/6R/4M","8O/5R/2M"],
                 modes=["radio/media archive + counter motion","shadow reconstruction + mechanism anchor","UFO culture archive + restrained reconstruction","research archive + memory motion","Hat Man reconstruction + controlled reveal","media/reconstruction + meme motion","early-tech archive + feedback reconstruction","archive callbacks + final loop motion"]),
}


def run_base() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools" / "prepare_schlafparalyse_production_inputs.py")], cwd=ROOT, check=True)


def apply(ep: str, cfg: dict) -> None:
    out = SUMMARY / cfg["summary"]
    cue = out / "VISUAL_CUE_SHEET.csv"
    rows = []
    if cue.is_file():
        with cue.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    if len(rows) != 8:
        raise RuntimeError(f"{ep}: expected 8 cue rows, found {len(rows)}")

    fields = ["act","beat","anchor_text","visual_mode","audio","edit_rule","v5_shot_target","v5_mix_target","v5_repeat_lock"]
    with cue.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for i, row in enumerate(rows):
            row = dict(row)
            row["visual_mode"] = cfg["modes"][i]
            row["v5_shot_target"] = cfg["acts"][i]
            row["v5_mix_target"] = cfg["mixes"][i]
            row["v5_repeat_lock"] = "no identical frame; no consecutive same base asset; no still >9s"
            row["edit_rule"] = (row.get("edit_rule") or "") + "; V5 individualized coverage applies"
            w.writerow(row)

    coverage = TYPE_B / cfg["episode"] / "VISUAL_COVERAGE_V5.md"
    (out / "VISUAL_PRODUCTION_LOCK_V5.md").write_text(
        f"# {ep} — Visual Production Lock V5\n\n"
        f"Canonical coverage: `{coverage.relative_to(ROOT).as_posix()}`\n\n"
        f"- shot target: **{cfg['shots']}**\n"
        f"- direct AI pool: **{cfg['pool']}**\n"
        "- AI pool is not a shot quota; originals, semantic source crops and motion preserve cut density.\n"
        "- one AI/source base may provide at most two shots and only with genuinely different information.\n"
        "- fill render_manifest lists until the act targets in VISUAL_CUE_SHEET.csv are covered.\n"
        "- run `tools/check_schlafparalyse_visual_coverage_v5.py` before final render.\n",
        encoding="utf-8",
    )
    print(f"{ep}: V5 visual target {cfg['shots']} applied")


def main() -> int:
    run_base()
    for ep, cfg in CFG.items():
        apply(ep, cfg)
    print("Schlafparalyse V5 production inputs are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
