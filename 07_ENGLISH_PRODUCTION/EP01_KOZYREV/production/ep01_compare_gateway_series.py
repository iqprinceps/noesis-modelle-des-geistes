#!/usr/bin/env python3
"""Compare final EP01 exports against the accessible Gateway V7 final timeline."""

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


EP = Path(__file__).resolve().parents[1]
MANIFEST = EP / "04_ASSETS/ASSET_MANIFEST.csv"
REPORT = EP / "05_QA/SERIES_GATEWAY_COMPARISON.json"
GATEWAY = Path(r"C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes\06_PRODUCTION\EP02_GATEWAY_V7")
GATEWAY_TIMELINE = GATEWAY / "timeline/EP02_GATEWAY_V7_timeline.json"
GATEWAY_QA = GATEWAY / "render/final/EP02_GATEWAY_V7_QA.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frame_image(path: Path) -> Image.Image:
    if path.suffix.casefold() in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}:
        return Image.open(path).convert("RGB")
    with tempfile.TemporaryDirectory(prefix="ep01_gateway_compare_") as folder:
        frame = Path(folder) / "frame.png"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path), "-frames:v", "1", str(frame)
        ], check=True)
        return Image.open(frame).convert("RGB")


def dhash(image: Image.Image) -> str:
    gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    arr = np.asarray(gray, dtype=np.int16)
    bits = (arr[:, :-1] > arr[:, 1:]).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def phash(image: Image.Image) -> str:
    gray = np.asarray(image.convert("L").resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float64)
    n = 32
    x = np.arange(n)
    k = x[:, None]
    basis = np.cos(np.pi * (2 * x + 1) * k / (2 * n))
    basis[0, :] *= 1 / np.sqrt(2)
    dct = basis @ gray @ basis.T
    low = dct[:8, :8].flatten()
    threshold = np.median(low[1:])
    value = 0
    for bit in low > threshold:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def hamming(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def fingerprints(path: Path) -> dict[str, str]:
    with frame_image(path) as image:
        return {"sha256": sha256(path), "dhash": dhash(image), "phash": phash(image)}


def main() -> int:
    if not GATEWAY_TIMELINE.exists():
        raise SystemExit(f"Gateway final timeline not accessible: {GATEWAY_TIMELINE}")
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        ep_rows = [row for row in csv.DictReader(handle) if row["status"] == "SELECTED"]
    ep_assets = []
    for row in ep_rows:
        path = EP / row["file_path"]
        fp = fingerprints(path)
        ep_assets.append({"asset_id": row["asset_id"], "path": row["file_path"], **fp})

    gateway_timeline = json.loads(GATEWAY_TIMELINE.read_text(encoding="utf-8"))
    gateway_unique: dict[str, dict] = {}
    missing = []
    for shot in gateway_timeline:
        raw = shot.get("visual", "")
        if not raw:
            continue
        path = Path(raw)
        if not path.exists():
            missing.append(raw)
            continue
        gateway_unique.setdefault(str(path.resolve()).casefold(), {"path": path, "shots": []})["shots"].append(shot.get("shot_id", ""))
    gateway_assets = []
    for item in gateway_unique.values():
        path = item["path"]
        fp = fingerprints(path)
        gateway_assets.append({"path": str(path), "shots": item["shots"], **fp})

    exact = []
    candidates = []
    gateway_sha = {item["sha256"]: item for item in gateway_assets}
    for left in ep_assets:
        if left["sha256"] in gateway_sha:
            exact.append({"ep01": left, "gateway": gateway_sha[left["sha256"]]})
        for right in gateway_assets:
            dd = hamming(left["dhash"], right["dhash"])
            pd = hamming(left["phash"], right["phash"])
            if dd <= 4 and pd <= 6:
                candidates.append({
                    "ep01_asset": left["asset_id"],
                    "ep01_path": left["path"],
                    "gateway_path": right["path"],
                    "gateway_shots": right["shots"],
                    "dhash_hamming": dd,
                    "phash_hamming": pd,
                })
    gateway_qa = json.loads(GATEWAY_QA.read_text(encoding="utf-8")) if GATEWAY_QA.exists() else {}
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if exact else ("REVIEW_REQUIRED" if candidates else "PASS"),
        "gateway_basis": {
            "timeline": str(GATEWAY_TIMELINE),
            "final_render": gateway_qa.get("file", ""),
            "final_render_sha256": gateway_qa.get("sha256", ""),
            "timeline_shots": len(gateway_timeline),
            "unique_accessible_final_visuals": len(gateway_assets),
            "missing_timeline_visual_paths": sorted(set(missing)),
        },
        "ep01_selected_assets": len(ep_assets),
        "exact_cross_episode_collisions": exact,
        "perceptual_cross_episode_candidates": candidates,
        "gateway_handoff_note": "EP01 uses its own Novosibirsk-to-Fort-Meade map exports and does not import or restart a Gateway shot.",
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "ep01": len(ep_assets), "gateway": len(gateway_assets), "exact": len(exact), "candidates": len(candidates), "missing_gateway_paths": len(set(missing))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
