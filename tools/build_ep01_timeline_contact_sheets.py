#!/usr/bin/env python3
"""Render every distinct resolved EP01 timeline visual for final manual QA."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
TIMELINE = ROOT / "06_PRODUCTION" / "EP01_KOZYREV" / "timeline" / "EP01_KOZYREV_timeline.json"
OUT = ROOT / "06_PRODUCTION" / "EP01_KOZYREV" / "qa" / "timeline_contact_sheets"
VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def load_preview(path: Path, temp: Path) -> Image.Image:
    if path.suffix.casefold() not in VIDEO_SUFFIXES:
        return Image.open(path).convert("RGB")
    frame = temp / f"{path.stem}.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", "2",
        "-i", str(path), "-frames:v", "1", str(frame),
    ], check=True)
    return Image.open(frame).convert("RGB")


def main() -> None:
    rows = json.loads(TIMELINE.read_text(encoding="utf-8"))
    first_cue: dict[str, str] = {}
    for row in rows:
        first_cue.setdefault(row["visual"], row["cue_id"])
    visuals = [(Path(path), cue) for path, cue in first_cue.items()]
    OUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("arial.ttf", 24)
    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        for page_index in range(0, len(visuals), 20):
            page = visuals[page_index:page_index + 20]
            sheet = Image.new("RGB", (2000, 1200), (18, 21, 23))
            draw = ImageDraw.Draw(sheet)
            for slot, (path, cue) in enumerate(page):
                image = load_preview(path, temp)
                thumb = ImageOps.fit(image, (380, 214), method=Image.Resampling.LANCZOS)
                x = 20 + (slot % 5) * 396
                y = 20 + (slot // 5) * 290
                sheet.paste(thumb, (x, y + 48))
                label = f"{cue}  {path.stem}"
                draw.text((x, y), label[:39], font=font, fill=(235, 222, 181))
            first = page_index + 1
            last = page_index + len(page)
            sheet.save(OUT / f"sheet_{first:02d}_{last:02d}.jpg", quality=92)
    print(f"Created {((len(visuals) - 1) // 20) + 1} sheets for {len(visuals)} distinct visuals in {OUT}")


if __name__ == "__main__":
    main()

