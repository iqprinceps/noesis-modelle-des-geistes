import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

BASE = Path(r"C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes")

# Collect all image sources
sources = []

# 1) Generated images (Neuer Ordner) - V1 and V2
neuer_ordner = BASE / "06_PRODUCTION" / "EP04_JUNG" / "visuals" / "Neuer Ordner"
if neuer_ordner.exists():
    for f in sorted(neuer_ordner.iterdir()):
        if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.tif', '.tiff'):
            sources.append(("GENERATED", f))

# 2) Reference images
references = BASE / "06_PRODUCTION" / "EP04_JUNG" / "visuals" / "references"
if references.exists():
    for f in sorted(references.iterdir()):
        if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.svg'):
            sources.append(("REFERENCE", f))

# 3) Archive/Downloaded images in 05_GENERATED
generated_base = BASE / "05_GENERATED" / "EP04_JUNG_CHAKREN_V4"
subfolders = [
    "00_REFERENCES", "01_JUNG", "02_HAUER_NAZI", "03_WOODROFFE_SERPENT",
    "04_CHAKRA_TANTRA", "05_LEADBEATER_THEOSOPHICAL", "06_ZURICH_LOCATIONS",
    "07_ROTES_BUCH_PAULI"
]
for sub in subfolders:
    folder = generated_base / sub
    if folder.exists():
        for f in sorted(folder.iterdir()):
            if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.svg'):
                sources.append((sub, f))

print(f"Found {len(sources)} images total")

# Filter out SVG (can't open with PIL easily)
valid_sources = []
for label, path in sources:
    if path.suffix.lower() == '.svg':
        continue
    try:
        img = Image.open(path)
        img.verify()
        valid_sources.append((label, path))
    except Exception as e:
        print(f"Skipping {path.name}: {e}")

print(f"Valid images: {len(valid_sources)}")

# Contact sheet settings
THUMB_W, THUMB_H = 220, 140
PADDING = 8
LABEL_H = 28
COLS = 8
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (220, 220, 220)
LABEL_BG = (50, 50, 50)

rows = math.ceil(len(valid_sources) / COLS)
sheet_w = COLS * (THUMB_W + PADDING) + PADDING
sheet_h = rows * (THUMB_H + LABEL_H + PADDING) + PADDING

sheet = Image.new("RGB", (sheet_w, sheet_h), BG_COLOR)
draw = ImageDraw.Draw(sheet)

try:
    font = ImageFont.truetype("arial.ttf", 11)
except:
    font = ImageFont.load_default()

for idx, (label, path) in enumerate(valid_sources):
    col = idx % COLS
    row = idx // COLS
    x = PADDING + col * (THUMB_W + PADDING)
    y = PADDING + row * (THUMB_H + LABEL_H + PADDING)

    try:
        img = Image.open(path).convert("RGB")
        img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
        # Center the thumbnail
        ox = x + (THUMB_W - img.width) // 2
        oy = y + (THUMB_H - img.height) // 2
        sheet.paste(img, (ox, oy))
    except Exception as e:
        draw.rectangle([x, y, x + THUMB_W, y + THUMB_H], fill=(80, 20, 20))
        draw.text((x + 5, y + THUMB_H // 2), "ERR", fill=(255, 100, 100), font=font)

    # Label background
    draw.rectangle([x, y + THUMB_H, x + THUMB_W, y + THUMB_H + LABEL_H], fill=LABEL_BG)
    # Label text: short filename
    name = path.stem
    if len(name) > 26:
        name = name[:23] + "..."
    draw.text((x + 3, y + THUMB_H + 3), name, fill=TEXT_COLOR, font=font)
    # Category badge
    badge_color = {
        "GENERATED": (60, 140, 60),
        "REFERENCE": (60, 80, 160),
        "00_REFERENCES": (100, 100, 60),
        "01_JUNG": (140, 80, 60),
        "02_HAUER_NAZI": (140, 60, 60),
        "03_WOODROFFE_SERPENT": (60, 120, 120),
        "04_CHAKRA_TANTRA": (120, 60, 120),
        "05_LEADBEATER_THEOSOPHICAL": (120, 120, 60),
        "06_ZURICH_LOCATIONS": (60, 120, 80),
        "07_ROTES_BUCH_PAULI": (100, 80, 120),
    }.get(label, (80, 80, 80))
    draw.rectangle([x, y, x + 50, y + 14], fill=badge_color)
    short_label = label[:12] if len(label) > 12 else label
    draw.text((x + 2, y + 1), short_label, fill=(255, 255, 255), font=font)

out_path = BASE / "KONTAKTBOGEN_EP04_ALLE.png"
sheet.save(out_path, quality=90)
print(f"Saved to: {out_path}")
print(f"Size: {sheet.width}x{sheet.height}")
