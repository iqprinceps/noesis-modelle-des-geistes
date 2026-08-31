#!/usr/bin/env python3
"""Project-wide cadence QA for eased motion rendered from still images."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np


DEFAULT_MOTION_MODES = {
    "PHYSICAL_CHAMBER", "SUBJECTIVE_MYSTICAL", "PERSON_HISTORY",
    "EVIDENCE_PROCESS", "PHYSICAL_EVIDENCE",
}


def load_edl(path: Path) -> tuple[list[dict], str]:
    """Load the legacy CSV cue sheet or a production JSON visual EDL."""
    if path.suffix.casefold() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        shots = payload.get("shots")
        if not isinstance(shots, list):
            raise ValueError(f"JSON EDL has no shots array: {path}")
        rows: list[dict] = []
        for index, shot in enumerate(shots, 1):
            motion_declared = any(
                key in shot for key in ("motion", "motion_mode", "motion_amplitude")
            )
            motion_value = shot.get("motion")
            motion_mode = str(shot.get("motion_mode", "")).casefold()
            motion_amplitude = float(shot.get("motion_amplitude", 0.0) or 0.0)
            moving = (
                motion_value is True
                or motion_amplitude > 0.0
                or any(
                    token in motion_mode
                    for token in ("push", "pan", "zoom", "move", "motion")
                )
            )
            rows.append({
                "selected_file_path": shot.get("asset_abs") or shot.get("asset") or "",
                "semantic_mode": shot.get("kind", ""),
                "visual_state_id": shot.get("shot_id", f"V{index:03d}"),
                "segment_name": f"{shot.get('shot_id', f'V{index:03d}')}.mp4",
                "shot_number": index,
                "motion_declared": motion_declared,
                "moving": moving,
            })
        return rows, "json"

    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for index, row in enumerate(rows, 1):
        row["segment_name"] = f"{index:03d}_{row['visual_state_id']}.mp4"
        row["shot_number"] = index
    return rows, "csv"


def frame_differences(path: Path) -> np.ndarray:
    capture = cv2.VideoCapture(str(path))
    values: list[float] = []
    previous = None
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        grey = cv2.cvtColor(
            cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA),
            cv2.COLOR_BGR2GRAY,
        )
        if previous is not None:
            values.append(float(cv2.absdiff(grey, previous).mean()))
        previous = grey
    capture.release()
    return np.asarray(values, dtype=np.float64)


def analyse(path: Path) -> dict[str, float | int | str]:
    diffs = frame_differences(path)
    if len(diffs) < 8:
        return {"status": "FAIL_TOO_SHORT", "frames_checked": int(len(diffs) + 1)}
    start = int(len(diffs) * 0.20)
    end = max(start + 4, int(len(diffs) * 0.80))
    central = diffs[start:end]
    median = float(np.median(central))
    jerk = float(np.median(np.abs(np.diff(central))) / max(median, 1e-6))
    p95_ratio = float(np.percentile(central, 95) / max(median, 1e-6))
    low_ratio = float(np.mean(central < 0.10))
    status = "PASS"
    # A high low-motion ratio can be intrinsic to a dark or textureless image;
    # it is retained as a diagnostic but is not evidence of camera judder.
    # Judder is identified by unstable velocity and quantised jump spikes.
    if jerk > 0.65 or p95_ratio > 2.50:
        status = "FAIL_CADENCE"
    return {
        "status": status,
        "frames_checked": int(len(diffs) + 1),
        "central_median_adjacent_difference": round(median, 6),
        "central_jerk_over_median": round(jerk, 4),
        "central_p95_over_median": round(p95_ratio, 4),
        "central_low_motion_ratio": round(low_ratio, 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edl", required=True, type=Path)
    parser.add_argument("--segments", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows, edl_format = load_edl(args.edl)

    findings: list[dict] = []
    failures: list[str] = []
    if edl_format == "json":
        undeclared = [
            row["visual_state_id"] for row in rows
            if Path(row["selected_file_path"]).suffix.casefold()
            not in {".mp4", ".mov", ".mkv", ".webm"}
            and not row.get("motion_declared", False)
        ]
        if undeclared:
            failures.append(
                "JSON EDL must declare motion, motion_mode, or motion_amplitude "
                f"for every still; missing on {len(undeclared)} shot(s): "
                + ", ".join(undeclared)
            )
    for index, row in enumerate(rows, 1):
        source = Path(row["selected_file_path"])
        mode = row.get("semantic_mode", "")
        if source.suffix.casefold() in {".mp4", ".mov", ".mkv", ".webm"}:
            continue
        if edl_format == "csv" and mode not in DEFAULT_MOTION_MODES:
            continue
        if edl_format == "json" and not row.get("moving", False):
            continue
        segment = args.segments / row["segment_name"]
        if not segment.is_file():
            failures.append(f"missing segment: {segment.name}")
            continue
        result = analyse(segment)
        result.update({
            "shot": row.get("shot_number", index),
            "state": row["visual_state_id"],
            "segment": segment.name,
        })
        findings.append(result)
        if result["status"] != "PASS":
            failures.append(
                f"{index:03d} {row['visual_state_id']}: "
                f"jerk={result.get('central_jerk_over_median')}, "
                f"p95/p50={result.get('central_p95_over_median')}, "
                f"low={result.get('central_low_motion_ratio')}"
            )

    report = {
        "status": "PASS" if not failures else "FAIL",
        "definition": (
            "Central-60%-cadence QA on rendered moving-still segments. "
            "Static documents/cards/maps and native clips are excluded."
        ),
        "thresholds": {
            "central_jerk_over_median_max": 0.65,
            "central_p95_over_median_max": 2.50,
            "central_low_motion_ratio": "diagnostic_only_for_dark_or_low_texture_images",
        },
        "shots_checked": len(findings),
        "failures": failures,
        "shots": findings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "shots_checked": len(findings),
        "failures": failures,
    }, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
