#!/usr/bin/env python3
"""Render representative locked frames at the 246 px mobile review width."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


EP = Path(__file__).resolve().parents[1]
MANIFEST = EP / "04_ASSETS" / "ASSET_MANIFEST.csv"
OUT = EP / "05_QA" / "MOBILE_READABILITY_PROOF_246PX.png"
ASSETS = [
    "KZ_SRC_PATENT_COVER_DATE",
    "KZ_SRC_KOZYREV_PORTRAIT_1983",
    "KZ_CARD_THREE_THEORIES_OPEN",
    "KZ_TARGET_GRID_SEALED",
    "KZ_REPLICATION_CHAIN_MISSING",
    "KZ_MAP_NOVOSIBIRSK_TO_FORT_MEADE",
]


def main() -> int:
    rows = {row["asset_id"]: row for row in csv.DictReader(MANIFEST.open(encoding="utf-8-sig"))}
    width, image_height, label_height = 246, 139, 34
    sheet = Image.new("RGB", (width * 3, (image_height + label_height) * 2), (12, 15, 17))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("arial.ttf", 12)
    for index, asset_id in enumerate(ASSETS):
        path = EP / rows[asset_id]["file_path"]
        image = Image.open(path).convert("RGB").resize((width, image_height), Image.Resampling.LANCZOS)
        x = (index % 3) * width
        y = (index // 3) * (image_height + label_height)
        sheet.paste(image, (x, y))
        draw.text((x + 7, y + image_height + 8), asset_id, fill=(210, 218, 221), font=font)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT, optimize=True)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
