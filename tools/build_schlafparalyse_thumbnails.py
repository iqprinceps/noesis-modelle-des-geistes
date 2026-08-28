#!/usr/bin/env python3
"""Thumbnails fuer EP06-EP08 aus der erzeugten Vorlage aufbereiten.

Die Vorlage ist 2752x1536 und traegt keinen Text. YouTube will 1280x720 und
hoechstens 2 MB; auf Handygroesse ist das Motiv allein zu leise, deshalb kommt
eine sehr kurze Titelzeile dazu.

Erzeugt je Episode drei Varianten (ohne Text, Text unten, Text oben) und eine
Lesbarkeitsprobe bei 246 px Breite - das ist die Groesse, in der YouTube
Thumbnails in der Randspalte zeigt. Was dort nicht mehr lesbar ist, ist im
Feed wertlos.

Aufbau und Grenzwerte folgen `tools/build_ep04a_thumbnail.py`; die Farben
kommen aus der Kartenpalette der Schlafparalyse-Serie, damit Thumbnail und
Karten im Video zusammenpassen.

    python tools/build_schlafparalyse_thumbnails.py EP06 EP08
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 1280, 720
PROOF_W = 246

# Kartenpalette der Serie (tools/build_schlafparalyse_cards.py).
CREAM = (248, 246, 239)
CYAN = (91, 204, 207)
GOLD = (224, 168, 83)

EPISODES = {
    "EP06": dict(
        dir="EP06_SCHLAFPARALYSE_V4",
        eyebrow="SCHLAFPARALYSE  I",
        lines=["DU BIST WACH.", "DEIN KÖRPER NICHT."],
        # Person liegt links, Praesenz steht rechts in der Tuer.
        # Text unten links ueber die Decke, damit die Tuer frei bleibt.
        side="left",
    ),
    "EP07": dict(
        dir="EP07_SCHLAFPARALYSE_V4",
        eyebrow="SCHLAFPARALYSE  II",
        lines=["WER SITZT AUF", "DEINER BRUST?"],
        side="left",
    ),
    "EP08": dict(
        dir="EP08_SCHLAFPARALYSE_V4",
        eyebrow="SCHLAFPARALYSE  III",
        lines=["DER MANN", "MIT DEM HUT"],
        # Silhouette steht mittig-links, rechts ist der dunkle Nebenraum.
        side="right",
    ),
}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


def base_crop(src_path: Path) -> Image.Image:
    """Mittig auf 16:9 beschneiden und auf Zielgroesse rechnen."""
    src = Image.open(src_path).convert("RGB")
    target_h = int(src.width / (16 / 9))
    if target_h <= src.height:
        top = (src.height - target_h) // 2
        crop = src.crop((0, top, src.width, top + target_h))
    else:
        target_w = int(src.height * 16 / 9)
        left = (src.width - target_w) // 2
        crop = src.crop((left, 0, left + target_w, src.height))
    return crop.resize((W, H), Image.Resampling.LANCZOS)


def scrim(img: Image.Image, box: tuple[int, int, int, int], strength: int = 200) -> None:
    """Weicher dunkler Verlauf, damit Schrift auf jedem Untergrund steht."""
    layer = Image.new("L", (W, H), 0)
    ImageDraw.Draw(layer).rectangle(box, fill=strength)
    layer = layer.filter(ImageFilter.GaussianBlur(70))
    img.paste(Image.new("RGB", (W, H), (6, 8, 12)), (0, 0), layer)


def fit_size(draw: ImageDraw.ImageDraw, lines: list[str], max_width: int,
             start: int = 96) -> int:
    """Groesste Schriftgroesse, bei der beide Zeilen in die Breite passen."""
    size = start
    while size > 40:
        f = font("ariblk.ttf", size)
        if max(draw.textlength(l, font=f) for l in lines) <= max_width:
            return size
        size -= 2
    return size


def compose(base: Image.Image, cfg: dict, position: str) -> Image.Image:
    img = base.copy()
    draw = ImageDraw.Draw(img)
    margin = 54
    max_width = int(W * 0.60)
    size = fit_size(draw, cfg["lines"], max_width)
    line_h = int(size * 1.02)
    block_h = line_h * len(cfg["lines"]) + 74

    x = margin if cfg["side"] == "left" else W - margin - max_width
    if position == "bottom":
        y = H - margin - block_h
        scrim(img, (x - 90, y - 120, x + max_width + 90, H + 80), 208)
    else:
        y = margin + 46
        scrim(img, (x - 90, -80, x + max_width + 90, y + block_h + 90), 205)

    draw = ImageDraw.Draw(img)
    draw.rectangle((x, y - 34, x + 132, y - 28), fill=GOLD)
    draw.text((x, y - 18), cfg["eyebrow"], font=font("seguisb.ttf", 27), fill=CYAN)
    ty = y + 34
    for line in cfg["lines"]:
        draw.text((x, ty), line, font=font("ariblk.ttf", size), fill=CREAM)
        ty += line_h
    return img


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    for quality in (92, 88, 84, 78, 72):
        img.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
        if path.stat().st_size <= 2 * 1024 * 1024:
            break
    print(f"  {path.name:38s} {img.width}x{img.height}  "
          f"{path.stat().st_size / 1024:6.0f} KB  q={quality}")


def build(ep: str) -> bool:
    cfg = EPISODES[ep]
    out = ROOT / "06_PRODUCTION" / cfg["dir"] / "thumbnail"
    src = out / f"{ep}_THUMB_BASE.png"
    if not src.is_file():
        print(f"{ep}: keine Vorlage ({src.name}) - erst "
              f"tools/generate_schlafparalyse_thumbnails.py laufen lassen")
        return False

    print(f"{ep}:")
    base = base_crop(src)
    save(base, out / f"{ep}_THUMB_A_ohne_text.jpg")
    bottom = compose(base, cfg, "bottom")
    save(bottom, out / f"{ep}_THUMB_B_unten.jpg")
    save(compose(base, cfg, "top"), out / f"{ep}_THUMB_C_oben.jpg")

    # Lesbarkeitsprobe: so klein zeigt YouTube das Thumbnail in der Randspalte.
    proof = bottom.resize((PROOF_W, int(PROOF_W * H / W)), Image.Resampling.LANCZOS)
    proof.save(out / "_lesbarkeitsprobe_246px.png")
    print(f"  {'_lesbarkeitsprobe_246px.png':38s} {proof.width}x{proof.height}")

    # Uploadfertige Fassung ist die untere Variante.
    upload = ROOT / "06_PRODUCTION" / cfg["dir"] / "upload"
    upload.mkdir(parents=True, exist_ok=True)
    save(bottom, upload / f"{ep}_THUMBNAIL_1280x720.jpg")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("episodes", nargs="*")
    args = parser.parse_args()
    for ep in args.episodes or list(EPISODES):
        if ep not in EPISODES:
            raise SystemExit(f"Unbekannte Episode: {ep}")
        build(ep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
