#!/usr/bin/env python3
"""Build EP06 evidence frames while preserving source-image pixels exactly.

Only uniform resampling and, for the historical chart, a 90-degree rotation are
applied to the real source layers. No generative model redraws evidence content.
"""

from __future__ import annotations

from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter


Image.MAX_IMAGE_PIXELS = None
KIT = Path(__file__).resolve().parent
ASSETS = KIT / "02_ASSETS"
OUTPUT = KIT / "03_GENERATED_OUTPUT" / "NanoBanana_2K_Series"
SIZE = (2560, 1440)


def wood_background(seed: int, dark: bool = False) -> Image.Image:
    random.seed(seed)
    base = Image.new("RGB", SIZE, (36, 31, 28) if dark else (105, 77, 55))
    draw = ImageDraw.Draw(base)
    plank = 210
    for x in range(0, SIZE[0], plank):
        tone = random.randint(-8, 8)
        color = (
            max(0, min(255, (38 if dark else 112) + tone)),
            max(0, min(255, (33 if dark else 82) + tone)),
            max(0, min(255, (30 if dark else 58) + tone)),
        )
        draw.rectangle((x, 0, min(x + plank - 3, SIZE[0]), SIZE[1]), fill=color)
        draw.line((x, 0, x, SIZE[1]), fill=(18, 16, 15) if dark else (68, 48, 36), width=3)
        for y in range(45, SIZE[1], 95):
            wobble = random.randint(-10, 10)
            draw.line((x + 15, y + wobble, min(x + plank - 18, SIZE[0]), y), fill=(58, 48, 42) if dark else (126, 91, 64), width=1)
    return base.filter(ImageFilter.GaussianBlur(radius=0.35))


def fit(image: Image.Image, box: tuple[int, int]) -> Image.Image:
    copy = image.convert("RGB")
    copy.thumbnail(box, Image.Resampling.LANCZOS)
    return copy


def paste_with_shadow(canvas: Image.Image, layer: Image.Image, xy: tuple[int, int], border: int = 8) -> None:
    x, y = xy
    shadow = Image.new("RGBA", (layer.width + 50, layer.height + 50), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle((22, 22, layer.width + 22, layer.height + 22), fill=(0, 0, 0, 145))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=16))
    canvas.paste(shadow, (x - 20, y - 20), shadow)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((x - border, y - border, x + layer.width + border, y + layer.height + border), fill=(220, 214, 202))
    canvas.paste(layer, (x, y))


def chart_table() -> None:
    canvas = wood_background(1873)
    chart = Image.open(ASSETS / "EP06_Fogo_Island_to_Cape_Bonavista_Admiralty_Chart_1873.jpg")
    chart = chart.rotate(-90, expand=True)
    chart = fit(chart, (2135, 1380))
    x = 30 + (2135 - chart.width) // 2
    y = (1440 - chart.height) // 2
    paste_with_shadow(canvas, chart, (x, y), border=5)

    draw = ImageDraw.Draw(canvas)
    # Completely blank closed notebook, outside the chart.
    draw.rounded_rectangle((2225, 425, 2490, 890), radius=16, fill=(229, 226, 215), outline=(188, 181, 165), width=4)
    draw.line((2250, 438, 2250, 878), fill=(200, 194, 180), width=2)
    # Plain pencil, no branding.
    draw.rounded_rectangle((2510, 475, 2526, 850), radius=6, fill=(178, 132, 73))
    draw.polygon(((2510, 475), (2526, 475), (2518, 447)), fill=(206, 180, 142))
    draw.polygon(((2515, 459), (2521, 459), (2518, 447)), fill=(45, 38, 34))
    canvas.save(OUTPUT / "SHOT02_FOGO_MAP_TABLE.png", compress_level=6)


def rem_record_base() -> None:
    canvas = wood_background(30, dark=True)
    # Soft neutral laboratory wall/desk split, deliberately free of generated displays.
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 2560, 270), fill=(49, 54, 57))
    draw.rectangle((1760, 320, 2410, 1120), fill=(31, 36, 39))
    draw.rounded_rectangle((1885, 455, 2220, 785), radius=12, fill=(56, 61, 63), outline=(88, 94, 96), width=5)
    source = fit(Image.open(ASSETS / "EP06_REM_Polysomnography_30sec.png"), (1450, 1060))
    paste_with_shadow(canvas, source, (150, (1440 - source.height) // 2), border=12)
    canvas.save(OUTPUT / "IMG010_REM_RECORD_EDIT_BASE.png", compress_level=6)


def comparison_table() -> None:
    canvas = wood_background(306, dark=True)
    rem = fit(Image.open(ASSETS / "EP06_REM_Polysomnography_30sec.png"), (1120, 850))
    slow = fit(Image.open(ASSETS / "EP06_Slow_Wave_Sleep_PSG.jpg"), (1120, 850))
    y1 = (1440 - rem.height) // 2
    y2 = (1440 - slow.height) // 2
    paste_with_shadow(canvas, rem, (100, y1), border=10)
    paste_with_shadow(canvas, slow, (1340, y2), border=10)
    canvas.save(OUTPUT / "SHOT03_REM_VS_SLOW_WAVE_SOURCE_TABLE.png", compress_level=6)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    chart_table()
    rem_record_base()
    comparison_table()
    print("BUILT=SHOT02_FOGO_MAP_TABLE.png,IMG010_REM_RECORD_EDIT_BASE.png,SHOT03_REM_VS_SLOW_WAVE_SOURCE_TABLE.png")


if __name__ == "__main__":
    main()
