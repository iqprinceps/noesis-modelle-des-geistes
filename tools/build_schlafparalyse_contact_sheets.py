#!/usr/bin/env python3
"""Build final labeled contact sheets for EP06-EP08 still QA."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EPISODES = {
    "EP06": ROOT / "06_PRODUCTION" / "EP06_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT" / "NanoBanana_2K_Series",
    "EP07": ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT" / "NanoBanana_Pro_2K_Series",
    "EP08": ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT",
}
FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)


def main() -> int:
    for episode, output in EPISODES.items():
        files = sorted(
            [
                path
                for path in output.glob("*.png")
                if path.stem.startswith("IMG") or path.stem.startswith("SHOT")
            ],
            key=lambda path: path.name,
        )
        if len(files) not in {24, 40}:
            raise SystemExit(f"{episode}: expected 24 or 40 stills, got {len(files)}")
        qa_dir = output / "QA_CONTACT_SHEETS_FINAL"
        qa_dir.mkdir(parents=True, exist_ok=True)
        per_sheet = 8
        for sheet_index in range(math.ceil(len(files) / per_sheet)):
            batch = files[sheet_index * per_sheet : (sheet_index + 1) * per_sheet]
            sheet = Image.new("RGB", (1920, 4 * 584), (19, 24, 33))
            draw = ImageDraw.Draw(sheet)
            for index, path in enumerate(batch):
                with Image.open(path) as source:
                    tile = source.convert("RGB").resize((960, 540), Image.Resampling.LANCZOS)
                x = (index % 2) * 960
                y = (index // 2) * 584
                sheet.paste(tile, (x, y))
                draw.rectangle((x, y + 540, x + 960, y + 584), fill=(19, 24, 33))
                draw.text((x + 12, y + 550), path.name, font=FONT, fill=(242, 239, 227))
            destination = qa_dir / f"{episode}_FINAL_CONTACT_{sheet_index + 1:02d}.jpg"
            sheet.save(destination, quality=90, optimize=True)
            print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
