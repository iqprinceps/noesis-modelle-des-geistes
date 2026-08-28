#!/usr/bin/env python3
"""Conform short selected EP01 clips to their exact EDL block without freeze frames."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
EDL = EP / "06_TIMELINE" / "EP01_EN_FINAL_EDL.csv"
CUE = EP / "06_TIMELINE" / "EP01_EN_VISUAL_CUE_SHEET.csv"
OUT = EP / "04_ASSETS" / "CLIPS" / "CONFORMED_25FPS"
META = EP / "04_ASSETS" / "METADATA" / "FINAL_DOCUMENT_TIMELINE" / "CLIP_CONFORM.json"


def load(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def probe(path: Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)
    ], check=True, text=True, capture_output=True)
    return float(json.loads(result.stdout)["format"]["duration"])


def main() -> int:
    edl = load(EDL)
    OUT.mkdir(parents=True, exist_ok=True)
    replacements = {}
    report = []
    for row in edl:
        source = EP / row["selected_file_path"]
        if source.suffix.casefold() != ".mp4":
            continue
        source_duration = probe(source)
        target_duration = float(row["duration_seconds"])
        if source_duration + .04 >= target_duration:
            continue
        target = OUT / f"{row['visual_state_id']}.mp4"
        ratio = target_duration / source_duration
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-an",
            "-vf", f"minterpolate=fps=50:mi_mode=mci:mc_mode=obmc:me_mode=bidir,setpts={ratio:.9f}*PTS,fps=25,trim=duration={target_duration:.6f},setpts=PTS-STARTPTS",
            "-r", "25", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(target),
        ], check=True)
        replacements[row["visual_state_id"]] = target.relative_to(EP).as_posix()
        report.append({
            "state": row["visual_state_id"], "source": source.relative_to(EP).as_posix(),
            "source_duration": source_duration, "target_duration": target_duration,
            "stretch_ratio": ratio, "output": target.relative_to(EP).as_posix(),
            "interpolation": "minterpolate 50fps MCI/OBMC then 25fps delivery",
        })

    cues = load(CUE)
    fields = list(cues[0])
    for row in cues:
        replacement = replacements.get(row["visual_state_id"])
        if replacement:
            row["selected_file_path"] = replacement
            row["motion_class"] = "PROGRESSIVE_MOTION"
            row["asset_status"] = "SELECTED_READY"
            row["selection_status"] = "FINAL_CONFORMED"
    with CUE.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        writer.writerows(cues)
    META.parent.mkdir(parents=True, exist_ok=True)
    META.write_text(json.dumps({"status": "PASS", "conformed_count": len(report), "clips": report}, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"conformed": len(report), "states": sorted(replacements)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
