#!/usr/bin/env python3
"""Build one 4x4 contact sheet per Short from assets_v4, for visual sign-off.

The generator's own checks only catch hard failures (non-portrait, no image
data). The recurring soft failures in this project are a rotated room, a
rendered phone or frame around the scene, a cropped head and an accidental
double exposure. Those need a human look, so this makes looking cheap.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
TILE_W = 340
COLUMNS = 4


def sheet(job: str, out_dir: Path) -> Path | None:
    assets = sorted((PROD / job / "assets_v4").glob("SHOT*.png"))
    if not assets:
        return None
    tile_h = int(TILE_W * 2752 / 1536)
    rows = (len(assets) + COLUMNS - 1) // COLUMNS
    canvas = Image.new("RGB", (COLUMNS * TILE_W, rows * tile_h), (26, 26, 28))
    try:
        face = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", 30)
    except OSError:
        face = ImageFont.load_default()
    for index, path in enumerate(assets):
        with Image.open(path) as image:
            thumb = image.convert("RGB").resize((TILE_W, tile_h), Image.LANCZOS)
        column, row = index % COLUMNS, index // COLUMNS
        canvas.paste(thumb, (column * TILE_W, row * tile_h))
        draw = ImageDraw.Draw(canvas)
        label = path.stem.replace("SHOT", "")
        x, y = column * TILE_W + 12, row * tile_h + 10
        draw.rectangle((x - 6, y - 4, x + 52, y + 38), fill=(10, 10, 12))
        draw.text((x, y), label, font=face, fill=(240, 236, 226))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / ("%s_ASSETS_V4.jpg" % job)
    canvas.save(target, quality=88)
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(PROD / "QA_ASSETS_V4"))
    args = parser.parse_args()
    out_dir = Path(args.out)
    for job in sorted(path.name for path in PROD.iterdir()
                      if path.is_dir() and path.name.startswith("SP")):
        target = sheet(job, out_dir)
        if target:
            count = len(list((PROD / job / "assets_v4").glob("SHOT*.png")))
            print("%-28s %2d Motive -> %s" % (job, count, target), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
