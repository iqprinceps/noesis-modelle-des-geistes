from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PLAN = Path(__file__).resolve().parent / "EP08_VOICE_VISUAL_SYNC_PLAN.csv"
GENERATED = ROOT / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT"
OUT = ROOT / "SEMANTIC_CUTS"
QA = OUT / "QA_CONTACT_SHEETS"
SIZE = (2560, 1440)


def centering_for(name: str) -> tuple[float, float]:
    if "LEFT" in name or "SIDE" in name:
        return (0.33, 0.5)
    if "RIGHT" in name or "SOURCE_OBJECT" in name or "EXPECTATION_PANEL" in name:
        return (0.67, 0.5)
    if "BRIM" in name:
        return (0.5, 0.38)
    if "BODY" in name:
        return (0.5, 0.58)
    return (0.5, 0.5)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    specs: dict[str, str] = {}
    with PLAN.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["visual_asset"].startswith("CUT"):
                specs[row["visual_asset"]] = row["base_asset_or_build"]

    manifest = []
    created: list[Path] = []
    desired_files = set(specs)
    for visual, base in sorted(specs.items()):
        source_path = GENERATED / base
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        with Image.open(source_path) as source:
            source = source.convert("RGB")
            # Pre-render an 8% semantic reframe. The final edit holds this frame; it never zooms further.
            crop_w = round(source.width * 0.92)
            crop_h = round(source.height * 0.92)
            cx, cy = centering_for(visual)
            center_x, center_y = source.width * cx, source.height * cy
            left = max(0, min(source.width - crop_w, round(center_x - crop_w / 2)))
            top = max(0, min(source.height - crop_h, round(center_y - crop_h / 2)))
            staged = source.crop((left, top, left + crop_w, top + crop_h))
            result = staged.resize(SIZE, Image.Resampling.LANCZOS)
        output_path = OUT / visual
        result.save(output_path, compress_level=6)
        created.append(output_path)
        manifest.append({
            "filename": visual,
            "base_asset": base,
            "resolution": "2560x1440",
            "editor_rule": "PRE_RENDERED_SEMANTIC_REFRAME; NO_LIVE_ZOOM",
        })

    for stale in OUT.glob("CUT*.png"):
        if stale.name not in desired_files:
            stale.unlink()

    with (OUT / "SEMANTIC_CUTS_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest[0].keys())
        writer.writeheader()
        writer.writerows(manifest)

    QA.mkdir(parents=True, exist_ok=True)
    thumb = (480, 270)
    label_h = 50
    font = ImageFont.load_default(size=21)
    for page, start in enumerate(range(0, len(created), 12), 1):
        batch = created[start:start + 12]
        sheet = Image.new("RGB", (1920, 3 * (270 + label_h)), (11, 17, 29))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(batch):
            with Image.open(path) as image:
                frame = image.convert("RGB").resize(thumb, Image.Resampling.LANCZOS)
            x, y = (i % 4) * 480, (i // 4) * (270 + label_h)
            sheet.paste(frame, (x, y))
            label = path.stem[:39]
            draw.text((x + 8, y + 278), label, fill=(236, 231, 215), font=font)
        sheet.save(QA / f"EP08_SEMANTIC_CUTS_{page:02d}.jpg", quality=91)
    print(f"created={len(created)}")


if __name__ == "__main__":
    main()
