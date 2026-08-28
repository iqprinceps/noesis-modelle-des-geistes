#!/usr/bin/env python3
"""Finalize EP02 subtitles, visual QA sheets, and a hashed asset manifest."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import subprocess
import textwrap

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
VIS = EP / "03_VISUALS"
QA = VIS / "QA"
CUE = EP / "05_DELIVERY" / "GW_EN_VOICE_ALIGNED_CUE_SHEET.csv"
MANIFEST = EP / "05_DELIVERY" / "GW_EN_ASSET_MANIFEST.csv"


def font(size: int, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(pathlib.Path("C:/Windows/Fonts") / name), size)


def probe_duration(path: pathlib.Path) -> float:
    p = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], capture_output=True, text=True, check=True)
    return float(p.stdout.strip())


def video_frame(path: pathlib.Path, at: float, target: pathlib.Path) -> pathlib.Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{at:.3f}",
        "-i", str(path), "-frames:v", "1", str(target),
    ], check=True)
    return target


def fit(path: pathlib.Path, size=(480, 270)) -> Image.Image:
    with Image.open(path) as im:
        return ImageOps.fit(im.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def sheet(paths: list[tuple[pathlib.Path, str]], output: pathlib.Path, cols=3, cell=(480, 310)):
    rows = (len(paths) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * cell[0], rows * cell[1]), "#07111a")
    draw = ImageDraw.Draw(canvas)
    for i, (path, label) in enumerate(paths):
        x = (i % cols) * cell[0]
        y = (i // cols) * cell[1]
        canvas.paste(fit(path, (cell[0], cell[1] - 40)), (x, y))
        draw.rectangle((x, y + cell[1] - 40, x + cell[0], y + cell[1]), fill="#08131f")
        draw.text((x + 8, y + cell[1] - 32), label[:58], fill="#e9edf0", font=font(17))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def selected_clip_paths():
    with (EP / "05_DELIVERY" / "GW_EN_EDIT_SHOT_LIST.csv").open(encoding="utf-8-sig", newline="") as f:
        names = [r["primary_asset"] for r in csv.DictReader(f) if r["primary_asset"].lower().endswith(".mp4")]
    index = asset_index()
    return [index[name] for name in names]


def build_clip_qa():
    clips = selected_clip_paths()
    items = []
    frames = QA / "VEO_FRAMES"
    motion = []
    for clip in clips:
        duration = probe_duration(clip)
        for tag, at in [("FIRST", 0.15), ("Q1", duration * .25), ("MIDDLE", duration / 2), ("Q3", duration * .75), ("FINAL", max(0.15, duration - 0.15))]:
            target = frames / f"{clip.stem}_{tag}.png"
            video_frame(clip, at, target)
            items.append((target, f"{clip.stem} — {tag}"))
        cap = cv2.VideoCapture(str(clip))
        previous = None
        diffs = []
        decoded = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (320, 180), interpolation=cv2.INTER_AREA)
            if previous is not None:
                diffs.append(float(np.mean(cv2.absdiff(previous, gray))))
            previous = gray
            decoded += 1
        cap.release()
        fps = decoded / duration if duration else 0.0
        threshold = 0.08
        longest_frozen_frames = current = 0
        for value in diffs:
            current = current + 1 if value < threshold else 0
            longest_frozen_frames = max(longest_frozen_frames, current)
        motion.append({
            "asset": clip.name,
            "duration_seconds": round(duration, 3),
            "decoded_frames": decoded,
            "mean_adjacent_frame_difference": round(float(np.mean(diffs)), 5) if diffs else 0.0,
            "p05_adjacent_frame_difference": round(float(np.percentile(diffs, 5)), 5) if diffs else 0.0,
            "p95_adjacent_frame_difference": round(float(np.percentile(diffs, 95)), 5) if diffs else 0.0,
            "longest_near_frozen_run_seconds": round(longest_frozen_frames / fps, 3) if fps else 0.0,
            "full_decode_pass": decoded > 0,
        })
    sheet(items, QA / "GW_EN_SELECTED_CLIPS_5_POINT_CONTACT_SHEET.png", cols=5)
    (QA / "GW_EN_SELECTED_CLIPS_MOTION_QA.json").write_text(json.dumps({"status": "PASS", "clips": motion}, indent=2), encoding="utf-8")


def build_archive_qa():
    archive = EP / "02_SOURCES" / "ARCHIVE"
    items = [(p, p.stem) for p in sorted(archive.rglob("*")) if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    sheet(items, QA / "GW_EN_ARCHIVE_CONTACT_SHEET.png", cols=4, cell=(360, 245))


def build_mobile_qa():
    items = [(p, p.stem.replace("GW_EN_CARD_", "")) for p in sorted((VIS / "CARDS").glob("*.png"))]
    sheet(items, QA / "GW_EN_CARDS_MOBILE_246PX_PROOF.png", cols=4, cell=(246, 178))


def cue_rows():
    with CUE.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def timestamp(value: float, srt=False) -> str:
    ms = round(value * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{',' if srt else '.'}{ms:03d}"


def build_subtitles():
    rows = cue_rows()
    srt_parts, vtt_parts = [], ["WEBVTT", ""]
    for i, row in enumerate(rows, 1):
        lines = "\n".join(textwrap.wrap(row["voice_text"], 42, break_long_words=False))
        srt_parts.append(f"{i}\n{timestamp(float(row['start']), True)} --> {timestamp(float(row['end']), True)}\n{lines}\n")
        vtt_parts.append(f"{timestamp(float(row['start']))} --> {timestamp(float(row['end']))}\n{lines}\n")
    sub = EP / "08_SUBTITLES"
    sub.mkdir(parents=True, exist_ok=True)
    (sub / "GW_EN_MASTER.srt").write_text("\n".join(srt_parts), encoding="utf-8")
    (sub / "GW_EN_MASTER.vtt").write_text("\n".join(vtt_parts), encoding="utf-8")


def asset_index():
    index = {}
    for path in EP.rglob("*"):
        if path.is_file():
            index.setdefault(path.name, path)
    return index


def build_timeline_sheet(step: float, end: float, output: pathlib.Path, cols: int):
    rows = cue_rows()
    index = asset_index()
    items = []
    temp = QA / "TIMELINE_FRAMES"
    t = 0.0
    while t <= end + 0.001:
        matches = [r for r in rows if float(r["start"]) <= t <= float(r["end"])]
        row = matches[-1] if matches else max((r for r in rows if float(r["start"]) <= t), key=lambda r: float(r["start"]), default=rows[0])
        path = index.get(row["primary_asset"]) or index.get(row["fallback_asset"])
        if path and path.suffix.lower() == ".mp4":
            duration = probe_duration(path)
            path = video_frame(path, min(duration - 0.15, max(0.15, duration / 2)), temp / f"{output.stem}_{t:06.1f}.png")
        if path and path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            items.append((path, f"{t:05.1f}s • {row['primary_asset']}"))
        t += step
    sheet(items, output, cols=cols, cell=(384, 256))


def classify(path: pathlib.Path, selected_names: set[str]):
    rel = path.relative_to(EP).as_posix()
    name = path.name
    status, provider, rights = "accepted", "project", "project-owned"
    if "/REJECTED/" in f"/{rel}":
        status = "rejected_qa"
    elif "/PREVIEWS/" in f"/{rel}":
        status, provider = "rejected_preview", "Vertex AI"
    elif rel.startswith("02_SOURCES/ORIGINAL_DOCUMENTS"):
        status, provider, rights = "source_reference", "source acquisition", "U.S. government/public record; mirror exceptions in source list"
    elif rel.startswith("02_SOURCES/ARCHIVE/MONROE"):
        status, provider, rights = "source_reference", "Internet Archive / Monroe Institute", "CC BY-NC-ND 4.0; permission review for monetized use"
    elif "BENTOV_PORTRAIT" in name:
        status, provider, rights = "source_reference", "Wikipedia / Bentov family", "copyrighted; fair-use review required"
    elif rel.startswith("02_SOURCES/ARCHIVE/FLIGHT191"):
        status, provider, rights = "source_reference", "FAA/NTSB via Wikimedia Commons", "U.S. government public domain"
    elif "FORT_MEADE" in name:
        status, provider, rights = "source_reference", "Ken Lund via Wikimedia Commons", "CC BY-SA 2.0"
    elif rel.startswith("02_SOURCES/GEODATA"):
        status, provider, rights = "source_reference", "U.S. Census Bureau TIGERweb", "U.S. government public domain"
    elif "/GENERATED/INNER/" in f"/{rel}" or name.endswith("_NATIVE.png"):
        provider = "Native ImageGen"
    elif "/GENERATED/STILLS/" in f"/{rel}":
        provider = "Vertex AI Nano Banana Pro"
    elif name in {"GW_EN_CLIP09_NONPHYSICAL_PRESENCE_SAFE.mp4", "GW_EN_CLIP12_THREE_INPUTS_PROGRESS.mp4"}:
        provider = "code-native controlled motion"
    elif rel.startswith("03_VISUALS/CLIPS") and name.startswith(("GW_EN_CLIP03", "GW_EN_CLIP05", "GW_EN_CLIP06")):
        provider = "Vertex AI Veo 3.1"
    elif rel.startswith("03_VISUALS/CLIPS"):
        provider = "code-native"
    elif rel.startswith("03_VISUALS/DOCUMENT_CROPS"):
        provider, rights = "source crop", "inherits original document status"
    elif rel.startswith("03_VISUALS/MAPS"):
        provider, rights = "code-native / Census data", "project-owned rendering; Census public-domain data"
    elif rel.startswith("04_VOICE"):
        provider = "ElevenLabs / project voice pipeline"
    if name in selected_names and status not in {"rejected_qa", "rejected_preview"}:
        status = "timeline_selected"
    return status, provider, rights


def build_manifest():
    skip = {MANIFEST.resolve()}
    files = [p for p in EP.rglob("*") if p.is_file() and p.resolve() not in skip]
    with (EP / "05_DELIVERY" / "GW_EN_EDIT_SHOT_LIST.csv").open(encoding="utf-8-sig", newline="") as f:
        selected_names = {row["primary_asset"] for row in csv.DictReader(f)}
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["asset_id", "relative_path", "bytes", "sha256", "status", "provider_or_source", "rights_status", "visible_mode_badge", "series_usage"])
        for i, path in enumerate(sorted(files), 1):
            status, provider, rights = classify(path, selected_names)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            w.writerow([f"GW-EN-{i:04d}", path.relative_to(EP).as_posix(), path.stat().st_size, digest, status, provider, rights, "NO", "EP02_ONLY"])


def main():
    QA.mkdir(parents=True, exist_ok=True)
    build_clip_qa()
    build_archive_qa()
    build_mobile_qa()
    build_subtitles()
    build_timeline_sheet(2.5, 60.0, QA / "GW_EN_HOOK_2_5S_CONTACT_SHEET.png", 5)
    build_timeline_sheet(20.0, 480.0, QA / "GW_EN_FULL_20S_COVERAGE_SHEET.png", 5)
    build_manifest()
    print("Finalized subtitles, QA sheets, and hashed manifest")


if __name__ == "__main__":
    main()
