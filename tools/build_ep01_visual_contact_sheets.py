#!/usr/bin/env python3
"""Build labelled contact sheets for manual EP01 visual QA."""

from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "05_GENERATED" / "EP01_KOZYREV" / "01_SELECTED"
DEFAULT_OUT = ROOT / "06_PRODUCTION" / "EP01_KOZYREV" / "qa" / "selected_contact_sheets"


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(source.glob("*.png"), key=lambda p: p.name.casefold())
    font = ImageFont.truetype("arial.ttf", 28)
    for page_index in range(0, len(files), 20):
        page_files = files[page_index:page_index + 20]
        sheet = Image.new("RGB", (2000, 1200), (18, 21, 23))
        draw = ImageDraw.Draw(sheet)
        for slot, path in enumerate(page_files):
            image = Image.open(path).convert("RGB")
            thumb = ImageOps.fit(image, (380, 214), method=Image.Resampling.LANCZOS)
            x = 20 + (slot % 5) * 396
            y = 20 + (slot // 5) * 290
            sheet.paste(thumb, (x, y + 38))
            draw.text((x, y), path.stem, font=font, fill=(235, 222, 181))
        sheet.save(out / f"sheet_{page_index + 1:02d}_{page_index + len(page_files):02d}.jpg", quality=92)
    print(f"Created {((len(files) - 1) // 20) + 1} contact sheets in {out}")


if __name__ == "__main__":
    main()
