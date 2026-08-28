#!/usr/bin/env python3
"""Build EP02_EN thumbnail exports from the accepted Native ImageGen source."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
DIR = EP / "07_THUMBNAIL"
SOURCE = DIR / "GW_EN_THUMBNAIL_SOURCE_NATIVE.png"
PNG = DIR / "GW_EN_THUMBNAIL_FINAL_1280x720.png"
JPG = DIR / "GW_EN_THUMBNAIL_FINAL_1280x720.jpg"


def main() -> None:
    image = Image.open(SOURCE).convert("RGB")
    ratio = 1280 / 720
    target_w = int(image.height * ratio)
    left = max(0, (image.width - target_w) // 2)
    image = image.crop((left, 0, left + target_w, image.height)).resize((1280, 720), Image.Resampling.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(1.10)
    image = ImageEnhance.Color(image).enhance(1.08)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # Preserve the image's authored negative space while securing mobile legibility.
    for x in range(690):
        alpha = int(205 * (1 - x / 690) ** 1.7)
        draw.line((x, 0, x, 720), fill=(2, 8, 13, alpha))
    title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 82)
    kicker_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
    draw.text((62, 148), "THE ARMY'S", font=title_font, fill="#f0b746", stroke_width=2, stroke_fill="#0a1116")
    draw.text((62, 243), "GATEWAY", font=title_font, fill="#f4f6f2", stroke_width=2, stroke_fill="#0a1116")
    draw.text((62, 338), "TEST", font=title_font, fill="#f4f6f2", stroke_width=2, stroke_fill="#0a1116")
    draw.rounded_rectangle((62, 468, 552, 521), radius=8, fill=(7, 20, 28, 225), outline="#57cbd2", width=2)
    draw.text((84, 481), "THREE OBSERVERS. THREE TIMES.", font=kicker_font, fill="#70dde2")
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=3))
    image.save(PNG, optimize=True)
    image.save(JPG, quality=94, optimize=True, progressive=True)
    print(PNG)
    print(JPG)


if __name__ == "__main__":
    main()
