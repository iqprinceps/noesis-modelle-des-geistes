from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

EP = Path(__file__).resolve().parents[1]
SRC = EP / "04_ASSETS" / "GENERATED" / "DETERMINISTIC"
OUT = EP / "05_QA" / "CONTACT_SHEETS"
OUT.mkdir(parents=True, exist_ok=True)
font_path = "C:/Windows/Fonts/arial.ttf"
font = ImageFont.truetype(font_path, 18)
files = sorted(SRC.glob("*.png"))
cols, rows = 4, 4
tw, th, lh = 480, 270, 34
for page, start in enumerate(range(0, len(files), cols * rows), 1):
    canvas = Image.new("RGB", (cols * tw, rows * (th + lh)), (5, 7, 8))
    draw = ImageDraw.Draw(canvas)
    for i, path in enumerate(files[start:start + cols * rows]):
        r, c = divmod(i, cols)
        x, y = c * tw, r * (th + lh)
        with Image.open(path) as im:
            thumb = ImageOps.fit(im.convert("RGB"), (tw, th), Image.Resampling.LANCZOS)
        canvas.paste(thumb, (x, y))
        label = path.stem.replace("KZ_", "")
        if len(label) > 47:
            label = label[:46] + "…"
        draw.rectangle((x, y + th, x + tw, y + th + lh), fill=(10, 14, 16))
        draw.text((x + 8, y + th + 7), label, font=font, fill=(215, 222, 224))
    canvas.save(OUT / f"deterministic_contact_{page:02d}.jpg", quality=91, subsampling=0)
print(f"sheets={(len(files) + cols * rows - 1) // (cols * rows)} assets={len(files)}")

triplets = EP / "05_QA" / "CLIP_TRIPLETS"
clip_files = sorted(triplets.glob("*.jpg"))
if clip_files:
    ctw, cth, clh = 640, 360, 34
    clip_sheet = Image.new("RGB", (3 * ctw, 5 * (cth + clh)), (5, 7, 8))
    cd = ImageDraw.Draw(clip_sheet)
    for i, path in enumerate(clip_files):
        r, c = divmod(i, 3)
        with Image.open(path) as im:
            thumb = ImageOps.fit(im.convert("RGB"), (ctw, cth), Image.Resampling.LANCZOS)
        x, y = c * ctw, r * (cth + clh)
        clip_sheet.paste(thumb, (x, y))
        cd.rectangle((x, y + cth, x + ctw, y + cth + clh), fill=(10, 14, 16))
        cd.text((x + 8, y + cth + 7), path.stem, font=font, fill=(215, 222, 224))
    clip_sheet.save(OUT / "clip_start_mid_end_contact.jpg", quality=92, subsampling=0)
    print(f"clip_triplets={len(clip_files)}")
