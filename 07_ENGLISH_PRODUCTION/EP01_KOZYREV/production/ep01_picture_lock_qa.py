#!/usr/bin/env python3
"""Hard no-return and duplicate QA for final EP01 picture assets."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV"
CUE = EP / "06_TIMELINE" / "EP01_EN_VISUAL_CUE_SHEET.csv"
MANIFEST = EP / "04_ASSETS" / "ASSET_MANIFEST.csv"
SERIES = ROOT / "07_ENGLISH_PRODUCTION" / "00_GLOBAL" / "SERIES_ASSET_REGISTER.csv"
OUTPUT = EP / "05_QA" / "PICTURE_LOCK_QA.json"
NEAR_REVIEW = EP / "05_QA" / "NEAR_DUPLICATE_MANUAL_REVIEW.json"
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dhash64(path: Path) -> str:
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())
    value = 0
    for y in range(8):
        for x in range(8):
            value = (value << 1) | int(pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return f"{value:016x}"


def phash64(path: Path) -> str:
    """Frequency-domain perceptual hash; complements dHash on sparse dark layouts."""
    with Image.open(path) as image:
        sample = np.asarray(
            image.convert("L").resize((32, 32), Image.Resampling.LANCZOS),
            dtype=np.float64,
        )
    size = sample.shape[0]
    positions = np.arange(size)
    frequencies = positions[:, None]
    transform = np.cos((np.pi / size) * (positions + 0.5) * frequencies)
    transform[0] *= 1.0 / np.sqrt(2.0)
    dct = transform @ sample @ transform.T
    low = dct[:8, :8]
    median = np.median(low.flatten()[1:])
    bits = (low > median).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def hamming(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def video_hashes(path: Path) -> list[dict]:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    duration = float(probe.stdout.strip())
    times = [0.0, max(0.0, duration / 2.0), max(0.0, duration - 0.08)]
    results = []
    with tempfile.TemporaryDirectory(prefix="ep01_picture_qa_") as folder:
        for label, second in zip(("start", "middle", "end"), times):
            frame = Path(folder) / f"{label}.png"
            subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{second:.3f}", "-i", str(path), "-frames:v", "1", str(frame)],
                check=True,
            )
            results.append({
                "position": label,
                "seconds": round(second, 3),
                "dhash64": dhash64(frame),
                "phash64": phash64(frame),
            })
    return results


def no_return(rows: list[dict], field: str) -> list[dict]:
    seen_runs: set[str] = set()
    previous = None
    violations = []
    for row in rows:
        value = row[field]
        if value != previous:
            if value in seen_runs:
                violations.append({"cue_id": row["cue_id"], "asset_id": value, "field": field})
            seen_runs.add(value)
            previous = value
    return violations


def visual_runs(rows: list[dict]) -> list[dict]:
    runs: list[dict] = []
    current = None
    for row in rows:
        state = row["visual_state_id"]
        if current is None or current["visual_state_id"] != state:
            current = {
                "visual_state_id": state,
                "primary_asset_id": row["primary_asset_id"],
                "first_cue": row["cue_id"],
                "last_cue": row["cue_id"],
                "start_seconds": float(row["start_seconds"]),
                "end_seconds": float(row["end_seconds"]),
                "motion_class": row.get("motion_class", "STATIC_OR_NEAR_STATIC"),
                "reason": row.get("long_hold_reason", ""),
            }
            runs.append(current)
        else:
            current["last_cue"] = row["cue_id"]
            current["end_seconds"] = float(row["end_seconds"])
    for run in runs:
        run["duration_seconds"] = round(run["end_seconds"] - run["start_seconds"], 3)
        run["review_from_8s"] = run["duration_seconds"] >= 8.0
        run["unjustified_over_10s"] = run["duration_seconds"] > 10.0 and (
            run["motion_class"] != "PROGRESSIVE_MOTION" or not run["reason"].strip()
        )
    return runs


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else EP / path


def main() -> int:
    cues = list(csv.DictReader(CUE.open(encoding="utf-8-sig", newline="")))
    cue_returns = no_return(cues, "primary_asset_id") + no_return(cues, "visual_state_id")
    badge_violations = [row["cue_id"] for row in cues if row["visible_mode_badge"] != "NO"]
    runs = visual_runs(cues)
    holds_from_8s = [run for run in runs if run["review_from_8s"]]
    unjustified_over_10s = [run for run in runs if run["unjustified_over_10s"]]
    static_holds_from_8s = [
        run for run in holds_from_8s if run["motion_class"] != "PROGRESSIVE_MOTION"
    ]
    static_runs = [run for run in runs if run["motion_class"] != "PROGRESSIVE_MOTION"]
    longest_static_hold = max(static_runs, key=lambda item: item["duration_seconds"], default=None)

    manifest_rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8-sig", newline="")))
    selected = [row for row in manifest_rows if row.get("status") == "SELECTED"]
    missing_files = []
    usage_violations = []
    records = []
    for row in selected:
        path = resolve_path(row["file_path"])
        if not path.is_file():
            missing_files.append({"asset_id": row["asset_id"], "file_path": str(path)})
            continue
        if row.get("series_usage") != "EP01_ONLY":
            usage_violations.append({"asset_id": row["asset_id"], "series_usage": row.get("series_usage")})
        record = {
            "asset_id": row["asset_id"],
            "family_id": row["family_id"],
            "path": str(path),
            "sha256": sha256(path),
            "perceptual": video_hashes(path) if path.suffix.casefold() in VIDEO_EXTENSIONS else [{
                "position": "still",
                "dhash64": dhash64(path),
                "phash64": phash64(path),
            }],
        }
        records.append(record)

    exact_duplicates = []
    by_sha: dict[str, list[dict]] = {}
    for record in records:
        by_sha.setdefault(record["sha256"], []).append(record)
    for digest, group in by_sha.items():
        if len(group) > 1:
            exact_duplicates.append({"sha256": digest, "asset_ids": [item["asset_id"] for item in group]})

    near_duplicates = []
    stillish = []
    for record in records:
        for frame in record["perceptual"]:
            stillish.append((record, frame))
    for index, (left, left_frame) in enumerate(stillish):
        for right, right_frame in stillish[index + 1 :]:
            if left["asset_id"] == right["asset_id"]:
                continue
            dhash_distance = hamming(left_frame["dhash64"], right_frame["dhash64"])
            phash_distance = hamming(left_frame["phash64"], right_frame["phash64"])
            if dhash_distance <= 5 and phash_distance <= 6:
                near_duplicates.append(
                    {
                        "left_asset": left["asset_id"],
                        "left_position": left_frame["position"],
                        "right_asset": right["asset_id"],
                        "right_position": right_frame["position"],
                        "dhash_hamming": dhash_distance,
                        "phash_hamming": phash_distance,
                        "manual_review": "REQUIRED",
                    }
                )

    series_collisions = []
    if SERIES.exists():
        series_rows = list(csv.DictReader(SERIES.open(encoding="utf-8-sig", newline="")))
        for record in records:
            for prior in series_rows:
                if prior.get("content_sha256") == record["sha256"] and prior.get("episode_id") not in {"", "EP01_KOZYREV"}:
                    series_collisions.append(
                        {
                            "asset_id": record["asset_id"],
                            "sha256": record["sha256"],
                            "other_episode": prior.get("episode_id"),
                            "other_asset": prior.get("asset_id"),
                        }
                    )

    review_rows = []
    if NEAR_REVIEW.exists():
        review_rows = json.loads(NEAR_REVIEW.read_text(encoding="utf-8")).get("reviews", [])
    review_index = {
        (
            row.get("left_asset"), row.get("right_asset"),
            row.get("left_sha256"), row.get("right_sha256"),
        ): row for row in review_rows if row.get("verdict") == "PASS_DISTINCT"
    }
    record_index = {record["asset_id"]: record for record in records}
    unreviewed_near_duplicates = []
    for candidate in near_duplicates:
        left = record_index[candidate["left_asset"]]
        right = record_index[candidate["right_asset"]]
        review = review_index.get((
            candidate["left_asset"], candidate["right_asset"],
            left["sha256"], right["sha256"],
        ))
        if review:
            candidate["manual_review"] = "PASS_DISTINCT"
            candidate["review_reason"] = review.get("reason", "")
        else:
            unreviewed_near_duplicates.append(candidate)

    if not selected:
        status = "PARTIAL_NO_SELECTED_ASSETS"
    elif cue_returns or badge_violations or missing_files or usage_violations or exact_duplicates or series_collisions or unjustified_over_10s:
        status = "FAIL"
    elif unreviewed_near_duplicates or static_holds_from_8s:
        status = "REVIEW_REQUIRED"
    else:
        status = "PASS"
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "cue_count": len(cues),
        "selected_asset_count": len(selected),
        "cue_return_violations": cue_returns,
        "visible_badge_violations": badge_violations,
        "longest_static_hold": longest_static_hold,
        "holds_from_8_seconds": holds_from_8s,
        "static_holds_from_8_seconds": static_holds_from_8s,
        "unjustified_holds_over_10_seconds": unjustified_over_10s,
        "missing_files": missing_files,
        "series_usage_violations": usage_violations,
        "exact_duplicates": exact_duplicates,
        "near_duplicate_candidates": near_duplicates,
        "unreviewed_near_duplicate_candidates": unreviewed_near_duplicates,
        "near_duplicate_review_file": str(NEAR_REVIEW),
        "series_hash_collisions": series_collisions,
        "asset_hashes": records,
        "note": "Near perceptual matches and static holds from 8 seconds require manual review; exact duplicates, asset returns and unjustified holds over 10 seconds are hard failures.",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "cue_count", "selected_asset_count", "cue_return_violations", "exact_duplicates", "series_hash_collisions")}, indent=2))
    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
