import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import re

BASE = Path(r"C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes")
neuer_ordner = BASE / "06_PRODUCTION" / "EP04_JUNG" / "visuals" / "Neuer Ordner"

# Parse V1/V2 pairs
pairs = {}
for f in sorted(neuer_ordner.iterdir()):
    if f.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        continue
    name = f.stem
    # Pattern: NN_IMGxx_VN_format
    m = re.match(r'(\d+_IMG\d+)_(V\d+)_(.+)', name)
    if m:
        base_id, version, fmt = m.groups()
        key = f"{base_id}_{fmt}"
        if key not in pairs:
            pairs[key] = {}
        pairs[key][version] = f

print(f"Found {len(pairs)} image pairs")

# Settings
THUMB_W, THUMB_H = 320, 200
PADDING = 6
LABEL_H = 24
COLS = 2  # V1 and V2 side by side
GROUP_PADDING = 20
BG_COLOR = (25, 25, 30)
TEXT_COLOR = (220, 220, 220)

# Group by scene number
scene_groups = {}
for key, versions in pairs.items():
    m = re.match(r'(\d+)_IMG(\d+)', key)
    if m:
        scene_num = int(m.group(1))
        img_num = int(m.group(2))
        if scene_num not in scene_groups:
            scene_groups[scene_num] = []
        scene_groups[scene_num].append((key, versions, img_num))

# Sort within each scene
for sn in scene_groups:
    scene_groups[sn].sort(key=lambda x: x[2])

# Calculate layout
cell_w = THUMB_W + PADDING
group_w = 2 * cell_w + GROUP_PADDING
groups_per_row = 3
total_groups = len(pairs)
rows_needed = -(-total_groups // groups_per_row)  # ceil div

sheet_w = groups_per_row * group_w + PADDING * 2
row_h = THUMB_H + LABEL_H + PADDING
sheet_h = rows_needed * row_h + PADDING * 2 + 40  # extra for header

sheet = Image.new("RGB", (sheet_w, sheet_h), BG_COLOR)
draw = ImageDraw.Draw(sheet)

try:
    font = ImageFont.truetype("arial.ttf", 11)
    font_title = ImageFont.truetype("arial.ttf", 14)
except:
    font = ImageFont.load_default()
    font_title = font

# Header
draw.text((PADDING, PADDING), "EP04 V1 vs V2 Vergleich — KI-generierte Bilder", fill=(255, 220, 100), font=font_title)

# Flatten and render
all_items = []
for sn in sorted(scene_groups.keys()):
    for key, versions, img_num in scene_groups[sn]:
        all_items.append((sn, key, versions, img_num))

y_start = 40
for idx, (sn, key, versions, img_num) in enumerate(all_items):
    group_col = idx % groups_per_row
    group_row = idx // groups_per_row

    gx = PADDING + group_col * group_w
    gy = y_start + group_row * row_h

    for vi, ver in enumerate(["V1", "V2"]):
        x = gx + vi * cell_w
        y = gy

        if ver in versions:
            path = versions[ver]
            try:
                img = Image.open(path).convert("RGB")
                img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
                ox = x + (THUMB_W - img.width) // 2
                oy = y + (THUMB_H - img.height) // 2
                sheet.paste(img, (ox, oy))
            except:
                draw.rectangle([x, y, x + THUMB_W, y + THUMB_H], fill=(80, 20, 20))

        # Version label
        color = (60, 140, 60) if ver == "V1" else (60, 80, 160)
        draw.rectangle([x, y + THUMB_H, x + THUMB_W, y + THUMB_H + LABEL_H], fill=color)
        label = f"{ver} — {path.stem}" if ver in versions else f"{ver} — fehlt"
        if len(label) > 38:
            label = label[:35] + "..."
        draw.text((x + 3, y + THUMB_H + 3), label, fill=(255, 255, 255), font=font)

out_path = BASE / "KONTAKTBOGEN_EP04_V1_vs_V2.png"
sheet.save(out_path, quality=90)
print(f"Saved: {out_path}")
print(f"Size: {sheet.width}x{sheet.height}")
