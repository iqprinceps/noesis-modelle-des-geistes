#!/usr/bin/env python3
"""Create the final EP01 render, thumbnail and complete upload handoff."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


EP = Path(__file__).resolve().parents[1]
REVIEW = EP / "07_REVIEW/EP01_EN_KOZYREV_INTERNAL_REVIEW_1080p.mp4"
RENDER_DIR = EP / "06_RENDER"
UPLOAD = EP / "09_UPLOAD"
MASTER = RENDER_DIR / "EP01_EN_KOZYREV_MASTER_1080P.mp4"
UPLOAD_MASTER = UPLOAD / MASTER.name
THUMB = UPLOAD / "EP01_EN_KOZYREV_THUMBNAIL_1280x720.jpg"
SOURCE = EP / "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/FINAL_DOCUMENT_REPAIR/KZ_FILM_LUNAR_STORM_SESSION.png"
SOURCES = EP / "04_SOURCES/SOURCE_AND_LICENSE_MANIFEST.csv"


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/bahnschrift.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def thumbnail() -> None:
    base = ImageOps.fit(Image.open(SOURCE).convert("RGB"), (1280, 720), Image.Resampling.LANCZOS)
    base = ImageEnhance.Contrast(base).enhance(1.14)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    pixels = overlay.load()
    for x in range(760):
        alpha = int(225 * (1 - x / 820) ** 1.25)
        for y in range(720):
            pixels[x, y] = (3, 8, 11, alpha)
    image = Image.alpha_composite(base.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(image)
    draw.ellipse((58, 55, 77, 74), fill=(85, 211, 222, 255))
    draw.line((77, 65, 555, 65), fill=(63, 110, 118, 255), width=3)
    draw.text((62, 116), "CAN METAL", font=font(84, True), fill=(245, 245, 237, 255))
    draw.text((62, 214), "BEND TIME?", font=font(84, True), fill=(226, 176, 68, 255))
    draw.text((67, 335), "THE KOZYREV MIRRORS", font=font(35, True), fill=(192, 213, 216, 255))
    draw.line((65, 397, 548, 397), fill=(85, 211, 222, 230), width=4)
    image.convert("RGB").save(THUMB, quality=94, subsampling=0, optimize=True)


def source_credits() -> str:
    with SOURCES.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected = [row for row in rows if not row["rights_status"].startswith("EXCLUDED")]
    lines = ["EP01 — KOZYREV MIRRORS — SOURCES AND CREDITS", ""]
    for row in selected:
        lines.extend([
            f"{row['source_id']} — {row['creator_or_publisher']} ({row['date']})",
            f"Source: {row['source_url']}",
            f"Rights/status: {row['rights_or_license']} — {row['rights_status']}",
            f"Use: {row['intended_use']}", "",
        ])
    lines.extend([
        "Generated visuals: OpenAI Native ImageGen and Google Nano Banana Pro, selected and visually reviewed for this episode only.",
        "Maps: Natural Earth public-domain data with an original episode-specific design.",
        "Music and sound design: original procedural production bed created for EP01.",
        "No permanent production-mode labels appear in the viewer image.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    if not REVIEW.is_file():
        raise FileNotFoundError(REVIEW)
    for folder in (RENDER_DIR, UPLOAD):
        folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REVIEW, MASTER)
    shutil.copy2(MASTER, UPLOAD_MASTER)
    thumbnail()
    shutil.copy2(EP / "06_TIMELINE/EP01_EN_KOZYREV.srt", UPLOAD / "EP01_EN_KOZYREV.srt")
    shutil.copy2(EP / "06_TIMELINE/EP01_EN_KOZYREV.vtt", UPLOAD / "EP01_EN_KOZYREV.vtt")
    shutil.copy2(EP / "04_ASSETS/ASSET_MANIFEST.csv", UPLOAD / "EP01_EN_ASSET_MANIFEST.csv")
    shutil.copy2(SOURCES, UPLOAD / "EP01_EN_SOURCES_AND_LICENSES.csv")
    archive = UPLOAD / "PRODUCTION_ARCHIVE"
    archive.mkdir(parents=True, exist_ok=True)
    archive_files = {
        EP / "01_SCRIPT/VOICE_SCRIPT_EN.txt": "EP01_EN_VOICE_SCRIPT.txt",
        EP / "02_VOICE/master/EP01_EN_KOZYREV_VO_MASTER.wav": "EP01_EN_KOZYREV_VO_MASTER.wav",
        EP / "02_VOICE/alignment/EP01_EN_KOZYREV_alignment.json": "EP01_EN_KOZYREV_alignment.json",
        EP / "06_TIMELINE/EP01_EN_VISUAL_CUE_SHEET.csv": "EP01_EN_VISUAL_CUE_SHEET.csv",
        EP / "06_TIMELINE/EP01_EN_FINAL_EDL.csv": "EP01_EN_FINAL_EDL.csv",
        EP / "06_TIMELINE/EP01_EN_REQUIRED_ASSET_SET.json": "EP01_EN_REQUIRED_ASSET_SET.json",
        EP / "05_QA/VOICE_MASTER_AUDIT.md": "EP01_EN_VOICE_MASTER_AUDIT.md",
        EP / "05_QA/FINAL_VISUAL_QA_REPORT.md": "EP01_EN_FINAL_VISUAL_QA_REPORT.md",
        EP / "05_QA/FINAL_READINESS_MATRIX.md": "EP01_EN_FINAL_READINESS_MATRIX.md",
        EP / "05_QA/REVIEW_RENDER_QA.json": "EP01_EN_REVIEW_RENDER_QA.json",
        EP / "05_QA/EP01_EN_CAMERA_MOTION_SMOOTHNESS_QA.json": "EP01_EN_CAMERA_MOTION_SMOOTHNESS_QA.json",
        EP / "05_QA/FINAL_TIMELINE/EP01_FINAL_TIMELINE_PRE_RENDER_QA.json": "EP01_EN_PRE_RENDER_QA.json",
        EP / "05_QA/DOCUMENT_EVIDENCE/EP01_DOCUMENT_DECISION_MATRIX_FINAL.md": "EP01_EN_DOCUMENT_DECISION_MATRIX.md",
        EP / "05_QA/DOCUMENT_EVIDENCE/EP01_20_FAIL_RESOLUTION_FINAL.md": "EP01_EN_DOCUMENT_RESOLUTION_REPORT.md",
    }
    for source, name in archive_files.items():
        shutil.copy2(source, archive / name)
    (UPLOAD / "EP01_EN_CREDITS_AND_SOURCES.txt").write_text(source_credits(), encoding="utf-8")
    description = """Could curved aluminum mirrors alter what a person perceives — or even how time feels?

This episode follows the Kozyrev-mirror story from Nikolai Kozyrev's real biography to the later 1996 patent, the apparatus described by Vlail Kaznacheev and Alexander Trofimov, the extraordinary claims in their publications, and the replication chain that is still missing.

We separate what the sources document from what remains a hypothesis, then end with a blind-target test that could make the mystery measurable.

Sources and image credits are included in the accompanying credits file and video credits.

#KozyrevMirrors #Unexplained #Documentary #TimePerception #Mystery
"""
    (UPLOAD / "EP01_EN_UPLOAD_DESCRIPTION.txt").write_text(description, encoding="utf-8")
    upload_meta = {
        "title": "Kozyrev Mirrors: Can Metal Bend Time?",
        "alternate_titles": [
            "The Kozyrev Mirrors: A Real Patent, Extraordinary Claims",
            "Inside the Kozyrev Mirrors — What the Evidence Actually Shows",
        ],
        "language": "en",
        "category": "Science & Technology",
        "thumbnail": THUMB.name,
        "master": UPLOAD_MASTER.name,
        "series_usage": "EP01_ONLY",
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    (UPLOAD / "EP01_EN_UPLOAD_METADATA.json").write_text(json.dumps(upload_meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    deliverables = []
    for path in sorted(UPLOAD.rglob("*")):
        if path.is_file() and path.name not in {"EP01_EN_DELIVERABLE_MANIFEST.json", ".gitkeep"}:
            deliverables.append({"file": path.relative_to(UPLOAD).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "status": "READY",
        "episode": "EP01_KOZYREV",
        "series_usage": "EP01_ONLY",
        "files": deliverables,
    }
    (UPLOAD / "EP01_EN_DELIVERABLE_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "READY", "master": str(MASTER), "upload_files": len(deliverables)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
