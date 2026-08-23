#!/usr/bin/env python3
"""Compare V3 and V4 document crops side by side."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
V3_DIR = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V3_SYNC" / "visuals" / "document_crops"
V4_DIR = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V4" / "visuals" / "document_crops"
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V4" / "comparison"
ARIAL_B = Path("C:/Windows/Fonts/arialbd.ttf")
SERIF = Path("C:/Windows/Fonts/georgia.ttf")

W, H = 1920, 1080
BG = (4, 17, 20)
OFF = (238, 235, 222)
CYAN = (91, 210, 211)


def f(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


def make_comparison(v3_name: str, v4_name: str, out_name: str):
    v3_path = V3_DIR / v3_name
    v4_path = V4_DIR / v4_name

    if not v3_path.exists() or not v4_path.exists():
        print(f"  Skipping {out_name}: source missing")
        return

    v3 = Image.open(v3_path).convert("RGB")
    v4 = Image.open(v4_path).convert("RGB")

    # Create side-by-side comparison
    canvas = Image.new("RGB", (W * 2 + 40, H), BG)
    canvas.paste(v3, (0, 0))
    canvas.paste(v4, (W + 40, 0))

    d = ImageDraw.Draw(canvas)
    d.text((W // 2 - 60, 15), "V3", font=f(ARIAL_B, 36), fill=CYAN)
    d.text((W + 40 + W // 2 - 60, 15), "V4", font=f(ARIAL_B, 36), fill=CYAN)

    OUT.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT / out_name, quality=95)


def main():
    docs = [
        ("V3_DOC01_ARMY_HEADER_DATE.png", "V4_DOC01_ARMY_HEADER_DATE.png", "CMP_DOC01.png"),
        ("V3_DOC02_TASK_BENTOV.png", "V4_DOC02_TASK_BENTOV.png", "CMP_DOC02.png"),
        ("V3_DOC03_MCDONNELL_SIGNATURE.png", "V4_DOC03_MCDONNELL_SIGNATURE.png", "CMP_DOC03.png"),
        ("V3_DOC04_FOCUS15_HEADING.png", "V4_DOC04_FOCUS15_HEADING.png", "CMP_DOC04.png"),
        ("V3_DOC05_LESS_THAN_FIVE_PERCENT.png", "V4_DOC05_LESS_THAN_FIVE_PERCENT.png", "CMP_DOC05.png"),
        ("V3_DOC06_FOCUS21_FUTURE.png", "V4_DOC06_FOCUS21_FUTURE.png", "CMP_DOC06.png"),
        ("V3_DOC07_OBE_NO_GUARANTEE.png", "V4_DOC07_OBE_NO_GUARANTEE.png", "CMP_DOC07.png"),
        ("V3_DOC08_INFORMATION_COLLECTION.png", "V4_DOC08_INFORMATION_COLLECTION.png", "CMP_DOC08.png"),
        ("V3_DOC09_RECOMMENDATION_H.png", "V4_DOC09_RECOMMENDATION_H.png", "CMP_DOC09.png"),
        ("V3_DOC10_NONCORPOREAL_FORMS.png", "V4_DOC10_NONCORPOREAL_FORMS.png", "CMP_DOC10.png"),
        ("V3_DOC11_HOLOGRAPHIC_BARRIER.png", "V4_DOC11_HOLOGRAPHIC_BARRIER.png", "CMP_DOC11.png"),
        ("V3_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png", "V4_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png", "CMP_DOC12.png"),
    ]
    for v3, v4, out in docs:
        make_comparison(v3, v4, out)
    print(f"Created {len(docs)} comparison images in {OUT}")


if __name__ == "__main__":
    main()
