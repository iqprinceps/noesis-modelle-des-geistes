#!/usr/bin/env python3
"""Thumbnail fuer EP04A aufbereiten.

Die Vorlage ist 2752x1536 (Seitenverhaeltnis 1.792) und 6,6 MB gross -- YouTube
will 1280x720 und hoechstens 2 MB.  Zusaetzlich traegt sie keinen Text; auf
Handygroesse ist das Motiv allein zu leise.  Erzeugt zwei Varianten zum
Vergleich und schreibt beide als JPEG.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "00_RAW_VERTEX" / "EP04A"
       / "THUMBNAIL" / "EP04A_THUMB_JUNG_SCHLANGE.png")
OUT = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "RENDER_EP04A" / "thumbnail"

W, H = 1280, 720
CREAM = (243, 239, 230)
TEAL = (141, 199, 205)
RED = (208, 90, 82)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(f"C:/Windows/Fonts/{path}", size)


def base_crop() -> Image.Image:
    """Auf 16:9 beschneiden, Motiv vergroessern, hellen Papierrand beruhigen."""
    src = Image.open(SRC).convert("RGB")
    # Der helle Papierrand rechts traegt bei Thumbnailgroesse nichts, die
    # Schlange soll aber weiter dahinter hervorkommen -- also nur teilweise weg.
    right = int(src.width * 0.885)
    target_h = int(right / (16 / 9))
    top = max(0, (src.height - target_h) // 2 - int(src.height * 0.03))
    crop = src.crop((0, top, right, min(src.height, top + target_h)))
    img = crop.resize((W, H), Image.Resampling.LANCZOS)

    # Das Papier rechts ist der hellste Fleck im Bild und zieht bei kleiner
    # Darstellung mehr Aufmerksamkeit als Jungs Gesicht.  Weich abdunkeln.
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rectangle((W - 190, -50, W + 50, H + 50), fill=150)
    mask = mask.filter(ImageFilter.GaussianBlur(90))
    img.paste(Image.new("RGB", (W, H), (10, 12, 16)), (0, 0), mask)
    return img


def scrim(img: Image.Image, box: tuple[int, int, int, int], strength: int = 190) -> None:
    """Weicher dunkler Verlauf, damit Schrift auf jedem Untergrund steht."""
    x0, y0, x1, y1 = box
    layer = Image.new("L", (W, H), 0)
    ImageDraw.Draw(layer).rectangle((x0, y0, x1, y1), fill=strength)
    layer = layer.filter(ImageFilter.GaussianBlur(70))
    img.paste(Image.new("RGB", (W, H), (6, 8, 12)), (0, 0), layer)


def variant_bottom(base: Image.Image) -> Image.Image:
    img = base.copy()
    scrim(img, (-80, 395, 780, 800), 210)
    d = ImageDraw.Draw(img)
    d.rectangle((54, 424, 196, 430), fill=RED)
    d.text((56, 450), "ZÜRICH 1932", font=font("seguisb.ttf", 33), fill=TEAL)
    d.text((52, 500), "WOVOR JUNG", font=font("ariblk.ttf", 94), fill=CREAM)
    d.text((52, 594), "WARNTE", font=font("ariblk.ttf", 94), fill=CREAM)
    return img


def variant_top(base: Image.Image) -> Image.Image:
    img = base.copy()
    scrim(img, (-80, -80, 640, 330), 205)
    d = ImageDraw.Draw(img)
    d.text((54, 60), "WOVOR", font=font("ariblk.ttf", 86), fill=CREAM)
    d.text((54, 146), "JUNG", font=font("ariblk.ttf", 86), fill=CREAM)
    d.text((54, 232), "WARNTE", font=font("ariblk.ttf", 86), fill=TEAL)
    d.text((58, 335), "ZÜRICH 1932", font=font("seguisb.ttf", 32), fill=(200, 195, 186))
    return img


def save(img: Image.Image, name: str) -> None:
    path = OUT / name
    for quality in (92, 88, 84, 78, 72):
        img.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
        if path.stat().st_size <= 2 * 1024 * 1024:
            break
    kb = path.stat().st_size / 1024
    print(f"{name:34s} {img.width}x{img.height}  {kb:7.0f} KB  q={quality}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    base = base_crop()
    save(base, "EP04A_THUMB_A_ohne_text.jpg")
    save(variant_bottom(base), "EP04A_THUMB_B_unten.jpg")
    save(variant_top(base), "EP04A_THUMB_C_oben.jpg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
