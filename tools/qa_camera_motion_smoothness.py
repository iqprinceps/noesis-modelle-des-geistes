#!/usr/bin/env python3
"""Detect frame-cadence stutter in moving stills and converted source clips."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_ep02_en_final as render  # noqa: E402


def frame_differences(path: Path) -> np.ndarray:
    capture = cv2.VideoCapture(str(path))
    values: list[float] = []
    previous = None
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        grey = cv2.cvtColor(cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
        if previous is not None:
            values.append(float(cv2.absdiff(grey, previous).mean()))
        previous = grey
    capture.release()
    return np.asarray(values, dtype=np.float64)


def longest_run(mask: np.ndarray) -> int:
    longest = current = 0
    for value in mask:
        current = current + 1 if value else 0
        longest = max(longest, current)
    return longest


def main() -> None:
    index = render.asset_index()
    findings: list[dict] = []
    failures: list[str] = []
    for number, row in enumerate(render.rows(), 1):
        asset = index[row["primary_asset"]]
        is_image = asset.suffix.lower() in {".png", ".jpg", ".jpeg"}
        reading = asset.name.startswith("GW_EN_DOC") or "_CARD_" in asset.name or "_MAP_" in asset.name
        source_rate = None
        converted_24 = False
        if not is_image:
            source_rate = render.subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", str(asset)],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            converted_24 = source_rate in {"24/1", "24000/1001"}
        if reading or (not is_image and not converted_24):
            continue

        segment = render.SEGMENTS / f"{number:03d}_{render.segment_key(row, asset)}.mp4"
        diffs = frame_differences(segment)
        if len(diffs) < 8:
            continue
        edge = max(2, int(len(diffs) * 0.10))
        interior = diffs[edge:-edge] if len(diffs) > edge * 2 + 4 else diffs
        median = float(np.median(interior))
        # A decoded duplicate from simple 24→30 frame repetition is virtually
        # identical (<0.1 mean luma step at this probe size). Genuine slow
        # motion remains comfortably above that boundary; using a fraction of
        # the median would wrongly flag intentionally quiet passages.
        low_threshold = 0.10
        low = interior < low_threshold
        repeat_ratio = float(low.mean())
        max_low_run = longest_run(low)
        p95_over_median = float(np.percentile(interior, 95) / max(median, 1e-6))
        central_start = int(len(diffs) * 0.20)
        central_end = max(central_start + 4, int(len(diffs) * 0.80))
        central = diffs[central_start:central_end]
        central_median = float(np.median(central))
        central_jerk = float(np.median(np.abs(np.diff(central))) / max(central_median, 1e-6))
        central_p95_over_median = float(np.percentile(central, 95) / max(central_median, 1e-6))
        status = "PASS"
        # Converted clips fail on repeated/held frames. For eased still motion,
        # tiny steps at the curve ends are intentional; the central 60% must
        # instead show low velocity jerk and no quantised jump spikes.
        cadence_failed = (
            (converted_24 and (repeat_ratio > 0.02 or max_low_run > 1))
            or (is_image and (central_jerk > 0.95 or central_p95_over_median > 2.80))
        )
        if cadence_failed:
            status = "FAIL_CADENCE"
            failures.append(
                f"{number:03d} {asset.name}: repeat_ratio={repeat_ratio:.3f}, run={max_low_run}, "
                f"central_jerk={central_jerk:.3f}, central_p95/p50={central_p95_over_median:.3f}"
            )
        findings.append({
            "shot": number,
            "asset": asset.name,
            "segment": segment.name,
            "class": "moving_still" if is_image else "24_to_30_clip",
            "source_rate": source_rate,
            "frames_checked": int(len(diffs) + 1),
            "median_adjacent_difference": round(median, 6),
            "low_motion_threshold": round(low_threshold, 6),
            "low_motion_ratio_interior": round(repeat_ratio, 6),
            "longest_low_motion_run_frames": max_low_run,
            "p95_over_median": round(p95_over_median, 4),
            "central_60pct_jerk_over_median": round(central_jerk, 4),
            "central_60pct_p95_over_median": round(central_p95_over_median, 4),
            "status": status,
        })

    report = {
        "status": "PASS" if not failures else "FAIL",
        "definition": "Interior-frame cadence check for supersampled moving stills and 24-to-30 fps interpolated clips; static evidence/cards/maps are intentionally excluded.",
        "shots_checked": len(findings),
        "failures": failures,
        "shots": findings,
    }
    output = render.RENDER / "QA" / "GW_EN_CAMERA_MOTION_SMOOTHNESS_QA.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
