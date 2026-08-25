#!/usr/bin/env python3
"""Create EP08 QA contact sheets and optionally normalize approved stills to 2560x1440."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT"
QA_DIR = ROOT / "tmp" / "ep08_qa"
TARGET = (2560, 1440)


def stills() -> list[Path]:
    return sorted([*OUTPUT.glob("IMG*.png"), *OUTPUT.glob("SHOT*.png")], key=lambda path: path.name)


def normalized(image: Image.Image) -> Image.Image:
    target_ratio = TARGET[0] / TARGET[1]
    width, height = image.size
    ratio = width / height
    if ratio > target_ratio:
        new_width = round(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    elif ratio < target_ratio:
        new_height = round(width / target_ratio)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    return image.resize(TARGET, Image.Resampling.LANCZOS)


def metrics(path: Path) -> dict:
    with Image.open(path) as source:
        rgb = source.convert("RGB")
        gray = rgb.convert("L")
        stat = ImageStat.Stat(gray)
        histogram = gray.histogram()
        pixels = gray.width * gray.height
        return {
            "filename": path.name,
            "width": rgb.width,
            "height": rgb.height,
            "mean_luma": round(stat.mean[0], 1),
            "pixels_below_20_pct": round(sum(histogram[:51]) / pixels * 100, 1),
            "bytes": path.stat().st_size,
        }


def create_contact_sheet(paths: list[Path], index: int) -> Path:
    columns, rows = 2, 5
    tile_width, image_height, label_height = 960, 540, 44
    sheet = Image.new("RGB", (columns * tile_width, rows * (image_height + label_height)), "#202020")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=22)
    for position, path in enumerate(paths):
        with Image.open(path) as source:
            thumb = normalized(source.convert("RGB")).resize((tile_width, image_height), Image.Resampling.LANCZOS)
        x = (position % columns) * tile_width
        y = (position // columns) * (image_height + label_height)
        sheet.paste(thumb, (x, y))
        draw.rectangle((x, y + image_height, x + tile_width, y + image_height + label_height), fill="#202020")
        draw.text((x + 12, y + image_height + 10), path.name, fill="white", font=font)
    QA_DIR.mkdir(parents=True, exist_ok=True)
    destination = QA_DIR / f"EP08_CONTACT_SHEET_{index:02d}.jpg"
    sheet.save(destination, quality=88, optimize=True)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args()

    paths = stills()
    if args.normalize:
        for path in paths:
            with Image.open(path) as source:
                final = normalized(source.convert("RGB"))
            final.save(path, format="PNG", optimize=True)

    QA_DIR.mkdir(parents=True, exist_ok=True)
    data = [metrics(path) for path in paths]
    (QA_DIR / "EP08_IMAGE_METRICS.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    sheets = [create_contact_sheet(paths[start : start + 10], start // 10 + 1) for start in range(0, len(paths), 10)]
    print(json.dumps({"count": len(paths), "contact_sheets": [str(path) for path in sheets], "metrics": data}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
