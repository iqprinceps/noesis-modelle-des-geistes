#!/usr/bin/env python3
"""Build labelled review sheets for the EP07 assets added after the old QA sheet."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SOURCE = Path(r"C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes\06_PRODUCTION\EP07_SCHLAFPARALYSE_V4\IMAGE_GENERATION_KIT\03_GENERATED_OUTPUT\NanoBanana_Pro_2K_Series")
OUT = Path(__file__).resolve().parents[1] / "00_AUDIT" / "REVIEW_SHEETS"
FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)


def main() -> None:
    files = [p for p in sorted(SOURCE.glob("*.png")) if p.stem.startswith("IMG") and int(p.stem[3:6]) >= 24]
    OUT.mkdir(parents=True, exist_ok=True)
    for page, start in enumerate(range(0, len(files), 8), 1):
        canvas = Image.new("RGB", (1920, 2336), (18, 22, 30))
        draw = ImageDraw.Draw(canvas)
        for i, path in enumerate(files[start:start + 8]):
            with Image.open(path) as src:
                tile = src.convert("RGB").resize((960, 540), Image.Resampling.LANCZOS)
            x, y = (i % 2) * 960, (i // 2) * 584
            canvas.paste(tile, (x, y))
            draw.rectangle((x, y + 540, x + 960, y + 584), fill=(18, 22, 30))
            draw.text((x + 10, y + 548), path.name, font=FONT, fill=(242, 239, 227))
        canvas.save(OUT / f"EP07_REUSE_REVIEW_{page:02d}.jpg", quality=91, optimize=True)


if __name__ == "__main__":
    main()
