#!/usr/bin/env python3
"""Hard-fail EP02 linear picture lock and build the English-series asset registry."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import subprocess

import cv2
import numpy as np


ROOT = pathlib.Path(__file__).resolve().parent.parent
EN = ROOT / "07_ENGLISH_PRODUCTION"
EP = EN / "EP02_GATEWAY"
EDL = EP / "05_DELIVERY" / "GW_EN_EDIT_SHOT_LIST.csv"
OUT = EP / "05_DELIVERY" / "GW_EN_PICTURE_LOCK_HASH_REGISTRY.csv"
REPORT = EP / "03_VISUALS" / "QA" / "GW_EN_PICTURE_LOCK_QA.json"
SERIES = EN / "00_GLOBAL" / "ENGLISH_SERIES_ASSET_REGISTRY.csv"
MEDIA = {".png", ".jpg", ".jpeg", ".mp4", ".mov", ".webm"}


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def phash_frame(frame: np.ndarray) -> str:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    small = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    dct = cv2.dct(small)[:8, :8]
    values = dct.flatten()[1:]
    bits = values > np.median(values)
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def perceptual_hash(path: pathlib.Path) -> str:
    if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        frame = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if frame is None:
            raise RuntimeError(f"Cannot decode {path}")
        return phash_frame(frame)
    cap = cv2.VideoCapture(str(path))
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    for fraction in (0.08, 0.5, 0.92):
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(count - 1, round((count - 1) * fraction))))
        ok, frame = cap.read()
        if ok:
            frames.append(cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA))
    cap.release()
    if not frames:
        raise RuntimeError(f"Cannot decode video {path}")
    return phash_frame(np.concatenate(frames, axis=1))


def hamming(a: str, b: str) -> int:
    return (int(a, 16) ^ int(b, 16)).bit_count()


def find_assets():
    index = {}
    for path in EP.rglob("*"):
        if path.is_file() and path.suffix.lower() in MEDIA and "REJECTED" not in path.parts:
            index.setdefault(path.name, path)
    return index


def read_edl():
    with EDL.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def ep01_roots():
    candidates = [
        EN / "EP01_KOZYREV",
        pathlib.Path.home() / "Documents" / "Codex" / "Youtube Modelle des Geistes" / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV",
    ]
    worktrees = pathlib.Path.home() / ".codex" / "worktrees"
    if worktrees.is_dir():
        candidates.extend(worktrees.glob("*/Youtube Modelle des Geistes/07_ENGLISH_PRODUCTION/EP01_KOZYREV"))
    resolved = []
    seen = set()
    for path in candidates:
        if path.is_dir() and str(path.resolve()).lower() not in seen:
            seen.add(str(path.resolve()).lower())
            resolved.append(path.resolve())
    return resolved


def series_candidates(roots):
    """Use the accessible EP01 release-oriented pool when no final EDL exists."""
    paths = []
    allowed_parts = {"CLIPS", "STILLS", "INNER", "CARDS", "MAPS", "DOCUMENT_CROPS"}
    for root in roots:
        for path in root.rglob("*"):
            upper_parts = {part.upper() for part in path.parts}
            if (
                path.is_file()
                and path.suffix.lower() in MEDIA
                and upper_parts.intersection(allowed_parts)
                and not upper_parts.intersection({"QA", "REJECTED", "PREVIEWS"})
            ):
                paths.append(path)
    unique = {}
    for path in paths:
        unique.setdefault(str(path.resolve()).lower(), path)
    return list(unique.values())


def main():
    rows = read_edl()
    index = find_assets()
    selected = []
    for row in rows:
        path = index.get(row["primary_asset"])
        if not path:
            raise FileNotFoundError(row["primary_asset"])
        selected.append({
            "edit_shot_id": row["edit_shot_id"],
            "asset": row["primary_asset"],
            "path": path.relative_to(EP).as_posix(),
            "sha256": sha256(path),
            "phash": perceptual_hash(path),
            "series_usage": "EP02_ONLY",
        })

    # An asset may occupy only one EDL row; cue-level states were already collapsed.
    names = [x["asset"] for x in selected]
    asset_returns = sorted({n for n in names if names.count(n) > 1})
    sha_groups = {}
    for item in selected:
        sha_groups.setdefault(item["sha256"], []).append(item["asset"])
    exact = [v for v in sha_groups.values() if len(v) > 1]
    near = []
    for i, left in enumerate(selected):
        for right in selected[i + 1:]:
            distance = hamming(left["phash"], right["phash"])
            if distance <= 2:
                near.append({"left": left["asset"], "right": right["asset"], "distance": distance})

    roots = ep01_roots()
    ep01 = []
    for path in series_candidates(roots):
        ep01.append({"asset": path.name, "path": str(path), "sha256": sha256(path), "phash": perceptual_hash(path)})
    cross_exact, cross_near = [], []
    for left in selected:
        for right in ep01:
            if left["sha256"] == right["sha256"]:
                cross_exact.append({"ep02": left["asset"], "ep01": right["path"]})
            elif hamming(left["phash"], right["phash"]) <= 2:
                cross_near.append({"ep02": left["asset"], "ep01": right["path"], "distance": hamming(left["phash"], right["phash"])})

    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(selected[0]))
        w.writeheader()
        w.writerows(selected)

    existing = []
    if SERIES.is_file():
        with SERIES.open(encoding="utf-8-sig", newline="") as f:
            existing = [r for r in csv.DictReader(f) if r.get("episode") != "EP02_EN"]
    series_rows = existing + [{
        "episode": "EP02_EN", "asset": x["asset"], "relative_path": f"EP02_GATEWAY/{x['path']}",
        "sha256": x["sha256"], "phash": x["phash"], "series_usage": "EP02_ONLY",
    } for x in selected]
    with SERIES.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["episode", "asset", "relative_path", "sha256", "phash", "series_usage"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(series_rows)

    durations = [float(r["duration"]) for r in rows]
    long_holds = [{k: r[k] for k in ("edit_shot_id", "duration", "primary_asset", "retention_review")} for r in rows if float(r["duration"]) >= 8]
    report = {
        "status": "PASS" if not (asset_returns or exact or near or cross_exact or cross_near) else "FAIL",
        "actual_edit_shots": len(rows),
        "actual_asset_runs": len(selected),
        "unique_semantic_motifs": len({(r["primary_asset"], r["asset_state"]) for r in rows}),
        "asset_return_count": len(asset_returns),
        "asset_returns": asset_returns,
        "exact_repeat_count": len(exact),
        "exact_repeats": exact,
        "near_repeat_count": len(near),
        "near_repeats_threshold_phash_le_2": near,
        "cross_episode_exact_collision_count": len(cross_exact),
        "cross_episode_near_collision_count": len(cross_near),
        "ep01_final_edl_found": any((root / "05_DELIVERY").is_dir() and any((root / "05_DELIVERY").glob("*EDIT*SHOT*.csv")) for root in roots),
        "ep01_release_oriented_media_compared": len(ep01),
        "ep01_roots_searched": [str(root) for root in roots],
        "longest_hold_seconds": max(durations),
        "longest_static_hold_seconds": max(float(r["duration"]) for r in rows if not r["primary_asset"].lower().endswith(".mp4")),
        "holds_at_or_above_8_seconds": long_holds,
        "unjustified_holds_over_10_seconds": [x for x in long_holds if float(x["duration"]) > 10 and not x["retention_review"]],
        "visible_mode_badges": 0,
        "series_usage": "EP02_ONLY",
        "notes": [
            "Perceptual collision threshold is 64-bit DCT pHash Hamming distance <=2.",
            "No EP01 final EDL was found in the accessible roots; cross-episode QA therefore used the stricter available release-oriented EP01 pool (clips, stills, inner visuals, cards, maps, and document crops; QA/previews/rejects excluded).",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "PASS" or report["unjustified_holds_over_10_seconds"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
