#!/usr/bin/env python3
"""Create optimized patent and document crops for Gateway V5.

Key improvements:
- Patent crops show FULL important content (not just centered)
- Document crops properly frame the relevant text
- Better composition for visual clarity
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF for PDF rendering

ROOT = Path(__file__).resolve().parents[1]
PATENT_PDF_DIR = ROOT / "06_PRODUCTION" / "Gateway_Production" / "Assets_Research_Luna"
REPORT_PNG_DIR = ROOT / "06_PRODUCTION" / "EP02_GATEWAY" / "reference_package"
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V5" / "visuals" / "patents"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
BG = (4, 17, 20)
GOLD = (224, 174, 71)
OFF = (238, 235, 222)
CYAN = (91, 210, 211)
ARIAL_B = Path("C:/Windows/Fonts/arialbd.ttf")
SERIF = Path("C:/Windows/Fonts/georgia.ttf")


def f(path, size):
    return ImageFont.truetype(str(path), size)


def make_patent_crop(pdf_path, page_num, crop_box, name, title, label="U.S. PATENT"):
    """Render a PDF page and crop to show the important content."""
    doc = fitz.open(str(pdf_path))
    page = doc[page_num]
    # Render at high DPI for quality
    mat = fitz.Matrix(3, 3)  # 3x scale
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()

    # Crop to the important area
    crop = img.crop(crop_box)
    scale = min(1740 / crop.width, 850 / crop.height)
    crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.Resampling.LANCZOS)

    # Create canvas
    canvas = Image.new("RGB", (W, H), BG)
    ox, oy = (W - crop.width) // 2, 155 + (850 - crop.height) // 2
    canvas.paste(crop, (ox, oy))

    # Add title and label
    d = ImageDraw.Draw(canvas)
    d.text((82, 48), title, font=f(SERIF, 46), fill=OFF)
    tw = d.textbbox((0, 0), label, font=f(ARIAL_B, 24))[2]
    d.rounded_rectangle((W - tw - 132, 48, W - 72, 92), radius=6, fill=(25, 43, 45, 235), outline=(*CYAN, 180), width=2)
    d.text((W - tw - 102, 57), label, font=f(ARIAL_B, 24), fill=OFF)
    d.text((82, 1025), "U.S. PATENT OFFICE", font=f(ARIAL_B, 20), fill=(105, 160, 160))

    canvas.save(OUT / name, quality=96)
    print(f"Created: {name}")


def main():
    # Bentov 1971 Patent - Drawing showing the device
    bentov_1971 = PATENT_PDF_DIR / "GW_DOC_002_US3605725_Bentov_Controlled_Catheter_Patent.pdf"

    # Page 0 - Full patent drawing with device diagram
    make_patent_crop(
        bentov_1971, 0,
        (100, 200, 1400, 1100),  # Show the full drawing area
        "V5_PATENT_BENTOV_1971_DRAWING.png",
        "Bentov Patent — Controlled Motion Device (1971)",
        "U.S. PATENT 3,605,725"
    )

    # Page 1 - Claims section
    make_patent_crop(
        bentov_1971, 1,
        (80, 100, 1450, 900),  # Show claims text
        "V5_PATENT_BENTOV_1971_CLAIMS.png",
        "Bentov Patent — Claims Section",
        "PATENT CLAIMS"
    )

    # Bentov 1969 Patent - Electrode design
    bentov_1969 = PATENT_PDF_DIR / "GW_DOC_001_US5213562_Binaural_EEG_Patent.pdf"

    # Monroe Patent - Binaural beats
    make_patent_crop(
        bentov_1969, 0,
        (100, 150, 1400, 1050),  # Full diagram
        "V5_PATENT_MONROE_BINAURAL.png",
        "Monroe Patent — Binaural Beat Method",
        "U.S. PATENT 5,213,562"
    )

    # Page with EEG diagram
    make_patent_crop(
        bentov_1969, 1,
        (80, 100, 1450, 950),
        "V5_PATENT_MONROE_EEG.png",
        "Monroe Patent — EEG Pattern Reproduction",
        "EEG PATTERNS"
    )

    # Gateway Report pages - better crops
    report_pages = [
        ("GW_REPORT_PDF24_FOCUS15_21.png", (80, 120, 1440, 500), "V5_DOC_FOCUS15_FULL.png", "Focus 15 — Complete Section", "THE COMPLETE TEXT"),
        ("GW_REPORT_PDF24_FOCUS15_21.png", (80, 500, 1440, 920), "V5_DOC_FOCUS21_FULL.png", "Focus 21 — Complete Section", "THE COMPLETE TEXT"),
        ("GW_REPORT_PDF24_FOCUS15_21.png", (80, 920, 1440, 1360), "V5_DOC_OBE_FULL.png", "Out-of-Body Movement — Complete", "THE COMPLETE TEXT"),
        ("GW_REPORT_PDF25_INFO_COLLECTION.png", (80, 1360, 1450, 1700), "V5_DOC_INFO_COLLECTION_TOP.png", "Information Collection — Opening", "THE REPORT"),
        ("GW_REPORT_PDF25_INFO_COLLECTION.png", (80, 1700, 1450, 1940), "V5_DOC_TEN_DIGITS.png", "The Ten Digits Experiment", "DOCUMENTED RESULT"),
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (75, 205, 1450, 545), "V5_DOC_RECOMMENDATION_H_FULL.png", "Recommendation H — Complete", "THE FULL PROCEDURE"),
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (90, 635, 1435, 865), "V5_DOC_RECOMMENDATION_JK.png", "Recommendations J & K", "NON-CORPOREAL FORMS"),
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (90, 865, 1435, 1112), "V5_DOC_EXPERIMENTS_ENDING.png", "The Conditional Ending", "IF EXPERIMENTS CARRIED THROUGH"),
    ]

    for source, crop_box, name, title, label in report_pages:
        src_path = REPORT_PNG_DIR / source
        img = Image.open(src_path).convert("RGB")
        crop = img.crop(crop_box)
        scale = min(1740 / crop.width, 850 / crop.height)
        crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.Resampling.LANCZOS)

        canvas = Image.new("RGB", (W, H), BG)
        ox, oy = (W - crop.width) // 2, 155 + (850 - crop.height) // 2
        canvas.paste(crop, (ox, oy))

        d = ImageDraw.Draw(canvas)
        d.text((82, 48), title, font=f(SERIF, 46), fill=OFF)
        tw = d.textbbox((0, 0), label, font=f(ARIAL_B, 24))[2]
        d.rounded_rectangle((W - tw - 132, 48, W - 72, 92), radius=6, fill=(25, 43, 45, 235), outline=(*CYAN, 180), width=2)
        d.text((W - tw - 102, 57), label, font=f(ARIAL_B, 24), fill=OFF)
        d.text((82, 1025), "U.S. ARMY GATEWAY REPORT · 1983", font=f(ARIAL_B, 20), fill=(105, 160, 160))

        canvas.save(OUT / name, quality=96)
        print(f"Created: {name}")


if __name__ == "__main__":
    main()
