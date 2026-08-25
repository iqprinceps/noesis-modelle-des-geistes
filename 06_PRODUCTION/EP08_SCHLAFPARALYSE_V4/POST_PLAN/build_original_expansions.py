from __future__ import annotations

import csv
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PLAN = Path(__file__).resolve().parent / "EP08_VOICE_VISUAL_SYNC_PLAN.csv"
ASSETS = ROOT / "IMAGE_GENERATION_KIT" / "02_ASSETS"
OUT = ROOT / "ORIGINAL_EXPANSIONS"
QA = OUT / "QA_CONTACT_SHEETS"
SIZE = (2560, 1440)


def load_source(path: Path) -> Image.Image:
    if path.suffix.lower() == ".pdf":
        doc = fitz.open(path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        doc.close()
        return image
    with Image.open(path) as src:
        return src.convert("RGB")


def full_frame(src: Image.Image) -> Image.Image:
    bg = ImageOps.fit(src, SIZE, method=Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(52))
    bg = ImageEnhance.Color(bg).enhance(0.28)
    bg = ImageEnhance.Brightness(bg).enhance(0.34)
    navy = Image.new("RGB", SIZE, (8, 18, 38))
    bg = Image.blend(bg, navy, 0.44)

    max_w, max_h = 2240, 1260
    scale = min(max_w / src.width, max_h / src.height)
    fg = src.resize((max(1, round(src.width * scale)), max(1, round(src.height * scale))), Image.Resampling.LANCZOS)
    framed = Image.new("RGB", (fg.width + 12, fg.height + 12), (46, 36, 24))
    framed.paste(fg, (6, 6))
    x = (SIZE[0] - framed.width) // 2
    y = (SIZE[1] - framed.height) // 2
    bg.paste(framed, (x, y))
    return bg


def detail_frame(src: Image.Image) -> Image.Image:
    # A semantic detail is pre-rendered as its own still. The editor never zooms this frame later.
    return ImageOps.fit(src, SIZE, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def make_contact_sheets(files: list[Path]) -> None:
    QA.mkdir(parents=True, exist_ok=True)
    thumb = (480, 270)
    label_h = 54
    cols, rows = 4, 3
    font = ImageFont.load_default(size=22)
    for page, start in enumerate(range(0, len(files), cols * rows), 1):
        batch = files[start:start + cols * rows]
        sheet = Image.new("RGB", (cols * thumb[0], rows * (thumb[1] + label_h)), (12, 18, 30))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(batch):
            with Image.open(path) as image:
                frame = image.convert("RGB").resize(thumb, Image.Resampling.LANCZOS)
            x = (i % cols) * thumb[0]
            y = (i // cols) * (thumb[1] + label_h)
            sheet.paste(frame, (x, y))
            label = path.stem
            if len(label) > 38:
                label = label[:37] + "…"
            draw.text((x + 8, y + thumb[1] + 9), label, fill=(236, 231, 215), font=font)
        sheet.save(QA / f"EP08_ORIGINAL_EXPANSIONS_{page:02d}.jpg", quality=91)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    specs: dict[str, str] = {}
    with PLAN.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            visual = row["visual_asset"]
            base = row["base_asset_or_build"]
            if visual.startswith("SRC") and visual[3:6].isdigit() and (ASSETS / base).exists():
                specs[visual] = base

    created: list[Path] = []
    manifest: list[dict[str, str]] = []
    for visual, base in sorted(specs.items()):
        source_path = ASSETS / base
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        source = load_source(source_path)
        is_detail = any(token in visual for token in ("DETAIL", "MACRO"))
        result = detail_frame(source) if is_detail else full_frame(source)
        output_path = OUT / visual
        result.save(output_path, compress_level=6)
        created.append(output_path)
        manifest.append(
            {
                "filename": visual,
                "base_asset": base,
                "view": "DETAIL_STATIC" if is_detail else "FULL_CONTAIN_STATIC",
                "resolution": "2560x1440",
                "camera_rule": "NO_PAN_NO_ZOOM",
            }
        )

    with (OUT / "ORIGINAL_EXPANSIONS_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest[0].keys())
        writer.writeheader()
        writer.writerows(manifest)
    make_contact_sheets(created)
    print(f"created={len(created)}")


if __name__ == "__main__":
    main()
