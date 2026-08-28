#!/usr/bin/env python3
"""Build labelled QA sheets for the 42 native-portrait Short assets."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
JOBS = (
    "SP06A_ATEM", "SP06B_RUECKENLAGE", "SP07A_ALBTRAUMWORT",
    "SP07B_SALEM_ZEUGE", "SP08A_HAT_MAN_HUT", "SP08B_UNSICHTBARE_PERSON",
)
FONT = ImageFont.truetype(r"C:\Windows\Fonts\seguisb.ttf", 34)


for job in JOBS:
    folder = PROD / job / "assets_vertical_v2"
    sheet = Image.new("RGB", (1400, 900), (18, 20, 24))
    draw = ImageDraw.Draw(sheet)
    for index in range(1, 8):
        source = folder / f"SHOT{index:02d}.png"
        with Image.open(source).convert("RGB") as image:
            thumb = ImageOps.fit(image, (190, 760), Image.Resampling.LANCZOS)
        x = 20 + (index - 1) * 197
        sheet.paste(thumb, (x, 70))
        label = f"SHOT {index:02d}"
        draw.text((x + 95, 28), label, font=FONT, fill=(242, 239, 230), anchor="mm")
    output = folder / "CONTACT_SHEET_V2.jpg"
    sheet.save(output, quality=93, optimize=True)
    print(output)
