#!/usr/bin/env python3
"""Build three materially different 1280×720 thumbnail directions and mobile QA."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


EP = Path(__file__).resolve().parents[1]
AS = EP / "03_VISUALS" / "ASSETS"
OUT = EP / "09_UPLOAD" / "THUMBNAILS"
W, H = 1280, 720
BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(BOLD), size)


def fit(path: Path, focus: tuple[float, float] = (.5, .5)) -> Image.Image:
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, (W, H), Image.Resampling.LANCZOS, centering=focus)


def grade(img: Image.Image, color: tuple[int, int, int], alpha: int) -> Image.Image:
    img = ImageEnhance.Contrast(img).enhance(1.18)
    img = ImageEnhance.Color(img).enhance(.88)
    layer = Image.new("RGBA", (W, H), color + (alpha,))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def gradient(img: Image.Image, left: bool = False) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = layer.load()
    for x in range(W):
        t = (1 - x / (W - 1)) if left else x / (W - 1)
        a = int(max(0, min(220, (t ** 1.7) * 245)))
        for y in range(H): px[x, y] = (3, 7, 12, a)
    return Image.alpha_composite(img, layer)


def label(d: ImageDraw.ImageDraw, xy: tuple[int, int], lines: list[str], size: int, fill=(247, 240, 221), spacing=0) -> None:
    x, y = xy
    for line in lines:
        d.text((x + 4, y + 5), line, font=font(size), fill=(0, 0, 0, 205), stroke_width=4, stroke_fill=(0, 0, 0, 230))
        d.text((x, y), line, font=font(size), fill=fill, stroke_width=2, stroke_fill=(12, 18, 22, 235))
        y += size + spacing


def save(img: Image.Image, name: str, concept: str, manifest: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    img.convert("RGB").save(path, quality=95, subsampling=0)
    mobile = img.convert("RGB").resize((246, 138), Image.Resampling.LANCZOS)
    mobile.save(OUT / f"MOBILE_{name}", quality=95)
    manifest.append({"file": name, "concept": concept, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "mobile": f"MOBILE_{name}"})


def thumb_a(manifest: list[dict]) -> None:
    img = fit(AS / "GENERATED" / "IMG001_SALEM_BEDROOM_COMAN_RECON.png", (.32, .48))
    img = gradient(grade(img, (20, 43, 57), 65), left=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((760, 72, 1216, 128), 12, fill=(188, 129, 62, 235))
    d.text((988, 100), "SALEM · 1692", font=font(29), fill=(15, 18, 20), anchor="mm")
    label(d, (690, 190), ["THE NIGHT", "BECAME", "EVIDENCE"], 82, fill=(250, 234, 199), spacing=-2)
    save(img, "THUMB_A_NIGHT_BECAME_EVIDENCE.jpg", "human Salem hook: private terror becomes evidence", manifest)


def thumb_b(manifest: list[dict]) -> None:
    img = fit(AS / "ORIGINAL" / "SRC_EP07_Fuseli_The_Nightmare_1781_full_painting.png", (.48, .48))
    img = gradient(grade(img, (52, 28, 17), 55), left=True)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((62, 72, 505, 128), 12, fill=(70, 191, 206, 235))
    d.text((283, 100), "THE NIGHTMARE · 1781", font=font(25), fill=(10, 16, 19), anchor="mm")
    label(d, (55, 180), ["WHY THE", "SAME VISITOR", "RETURNS"], 70, fill=(246, 238, 219), spacing=3)
    save(img, "THUMB_B_SAME_VISITOR_RETURNS.jpg", "iconic historical art and recurring visitor question", manifest)


def thumb_c(manifest: list[dict]) -> None:
    img = fit(AS / "GENERATED" / "IMG034_TWO_EXPECTATIONS_THRESHOLD.png", (.5, .5))
    img = grade(img, (7, 28, 37), 50)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(layer)
    d2.rectangle((0, 0, W, 215), fill=(3, 9, 15, 215))
    d2.rectangle((0, 605, W, 720), fill=(3, 9, 15, 185))
    img = Image.alpha_composite(img, layer)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 78), "CAN A STORY", font=font(78), fill=(248, 235, 205), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((W // 2, 158), "CHANGE THE BODY?", font=font(68), fill=(196, 232, 237), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((W // 2, 660), "TWO PEOPLE · THE SAME PARALYSIS", font=font(28), fill=(219, 224, 221), anchor="mm")
    save(img, "THUMB_C_STORY_CHANGES_BODY.jpg", "clean conceptual split: same body, different expectation", manifest)


def main() -> None:
    manifest: list[dict] = []
    thumb_a(manifest); thumb_b(manifest); thumb_c(manifest)
    thumbs = [Image.open(OUT / x["file"]).resize((640, 360), Image.Resampling.LANCZOS) for x in manifest]
    sheet = Image.new("RGB", (1280, 720), (8, 12, 17))
    sheet.paste(thumbs[0], (0, 0)); sheet.paste(thumbs[1], (640, 0)); sheet.paste(thumbs[2], (320, 360))
    sheet.save(OUT / "THUMBNAIL_CONTACT_SHEET.jpg", quality=94)
    mobiles = [Image.open(OUT / x["mobile"]) for x in manifest]
    mobile_sheet = Image.new("RGB", (738, 138), (8, 12, 17))
    for i, img in enumerate(mobiles): mobile_sheet.paste(img, (i * 246, 0))
    mobile_sheet.save(OUT / "THUMBNAIL_MOBILE_QA_246PX.jpg", quality=96)
    (OUT / "THUMBNAIL_MANIFEST.json").write_text(json.dumps({"canvas": "1280x720", "mobile_qa": "246x138", "variants": manifest, "selected_default": "THUMB_B_SAME_VISITOR_RETURNS.jpg"}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"variants": len(manifest), "selected": manifest[0]["file"]}, indent=2))


if __name__ == "__main__":
    main()
