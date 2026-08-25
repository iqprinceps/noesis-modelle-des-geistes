#!/usr/bin/env python3
"""Render the real 1924 Serpent Power scan into 16:9 source assets for EP04A."""

from __future__ import annotations

from pathlib import Path

import pymupdf
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PDF = (
    ROOT
    / "06_PRODUCTION"
    / "JUNG_SERIES_V1"
    / "REFERENCES_EP04AB"
    / "00_SHARED"
    / "04_MANUAL_LARGE_SOURCE"
    / "SERPENT_POWER"
    / "SHARED_The_Serpent_Power_1924_PD.pdf"
)
OUT = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "RENDER_EP04A" / "assets"
SIZE = (2560, 1440)


def render_page(document: pymupdf.Document, page_number: int) -> Image.Image:
    page = document[page_number - 1]
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(3.0, 3.0), alpha=False)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def page_on_table(page: Image.Image) -> Image.Image:
    background = ImageOps.fit(page, SIZE, method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(42))
    background = ImageEnhance.Brightness(background).enhance(0.18)
    canvas = background.convert("RGBA")

    foreground = ImageOps.contain(page, (1500, 1340), method=Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", (foreground.width + 80, foreground.height + 80), (0, 0, 0, 0))
    shadow_box = Image.new("RGBA", foreground.size, (0, 0, 0, 185))
    shadow.paste(shadow_box, (40, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    x = (SIZE[0] - foreground.width) // 2
    y = (SIZE[1] - foreground.height) // 2
    canvas.alpha_composite(shadow, (x - 40, y - 40))
    canvas.alpha_composite(foreground.convert("RGBA"), (x, y))
    return canvas.convert("RGB")


def title_detail(page: Image.Image) -> Image.Image:
    width, height = page.size
    crop = page.crop((int(width * 0.08), int(height * 0.02), int(width * 0.92), int(height * 0.60)))
    background = Image.new("RGB", SIZE, "#0d0c0a")
    foreground = ImageOps.contain(crop, (2440, 1340), method=Image.Resampling.LANCZOS)
    x = (SIZE[0] - foreground.width) // 2
    y = (SIZE[1] - foreground.height) // 2
    background.paste(foreground, (x, y))
    return background


def main() -> int:
    if not PDF.is_file():
        raise SystemExit(f"Missing source scan: {PDF}")
    OUT.mkdir(parents=True, exist_ok=True)
    document = pymupdf.open(PDF)
    title = render_page(document, 2)
    plate = render_page(document, 1)
    contents = render_page(document, 14)
    outputs = {
        "SHARED_BOOK_001_TITLE_1924.png": page_on_table(title),
        "SHARED_BOOK_001_TITLE_DETAIL.png": title_detail(title),
        "SHARED_BOOK_001_PLATE_I.png": page_on_table(plate),
        "SHARED_BOOK_001_ILLUSTRATIONS.png": page_on_table(contents),
    }
    for name, image in outputs.items():
        path = OUT / name
        image.save(path, optimize=True)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
