#!/usr/bin/env python3
"""Rebuild Gateway evidence crops with line-accurate, complete highlights."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "06_PRODUCTION" / "EP02_GATEWAY" / "reference_package"
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V3_SYNC" / "visuals" / "document_crops"
W, H = 1920, 1080
BG = (4, 17, 20)
GOLD = (224, 174, 71)
OFF = (238, 235, 222)
CYAN = (91, 210, 211)
ARIAL_B = Path("C:/Windows/Fonts/arialbd.ttf")
SERIF = Path("C:/Windows/Fonts/georgia.ttf")


def f(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


def lines(x1: int, x2s: list[int], y1: int, step: int = 34, height: int = 29) -> list[tuple[int, int, int, int]]:
    """One rectangle per typewritten line, allowing the final x edge to vary."""
    return [(x1, y1 + i * step, x2, y1 + i * step + height) for i, x2 in enumerate(x2s)]


def make(source: str, crop_box, name: str, title: str, marks, label="IN THE REPORT"):
    page = Image.open(SRC / source).convert("RGB")
    crop = page.crop(crop_box)
    scale = min(1740 / crop.width, 850 / crop.height)
    crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (W, H), BG)
    ox, oy = (W - crop.width) // 2, 155 + (850 - crop.height) // 2
    canvas.paste(crop, (ox, oy))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x1, y1, x2, y2 in marks:
        box = (
            ox + round((x1 - crop_box[0]) * scale),
            oy + round((y1 - crop_box[1]) * scale),
            ox + round((x2 - crop_box[0]) * scale),
            oy + round((y2 - crop_box[1]) * scale),
        )
        d.rounded_rectangle(box, radius=5, fill=(*GOLD, 52), outline=(*GOLD, 242), width=3)
    d.text((82, 48), title, font=f(SERIF, 46), fill=OFF)
    tw = d.textbbox((0, 0), label, font=f(ARIAL_B, 24))[2]
    d.rounded_rectangle((W - tw - 132, 48, W - 72, 92), radius=6, fill=(25, 43, 45, 235), outline=(*CYAN, 180), width=2)
    d.text((W - tw - 102, 57), label, font=f(ARIAL_B, 24), fill=OFF)
    d.text((82, 1025), "U.S. ARMY GATEWAY REPORT · 1983", font=f(ARIAL_B, 20), fill=(105, 160, 160))
    OUT.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(canvas.convert("RGBA"), ov).convert("RGB").save(OUT / name, quality=96)


def main():
    jobs = [
        ("GW_REPORT_PDF01_HEADER.png", (70, 45, 1450, 420), "V3_DOC01_ARMY_HEADER_DATE.png", "Army header, date and subject",
         [(300, 110, 1010, 240), (1110, 260, 1385, 320)]),
        ("GW_REPORT_PDF01_HEADER.png", (90, 620, 1440, 1260), "V3_DOC02_TASK_BENTOV.png", "The assigned task — and Bentov enters",
         lines(130, [1370, 1360, 1010], 680, 38, 32) + lines(400, [1160, 1260], 880, 38, 32)),
        ("GW_REPORT_PDF02_SIGNATURE.png", (650, 720, 1400, 1040), "V3_DOC03_MCDONNELL_SIGNATURE.png", "The author on the page",
         [(760, 810, 1325, 995)]),
        ("GW_REPORT_PDF24_FOCUS15_21.png", (95, 125, 1440, 360), "V3_DOC04_FOCUS15_HEADING.png", "Focus 15: Travel into the Past",
         [(245, 198, 745, 235)]),
        ("GW_REPORT_PDF24_FOCUS15_21.png", (90, 505, 1430, 705), "V3_DOC05_LESS_THAN_FIVE_PERCENT.png", "The report's complete difficulty warning",
         [(1115, 512, 1395, 543), (112, 548, 1390, 579), (112, 584, 1390, 615), (112, 620, 1390, 651)]),
        ("GW_REPORT_PDF24_FOCUS15_21.png", (90, 785, 1430, 920), "V3_DOC06_FOCUS21_FUTURE.png", "Focus 21: The Future",
         [(250, 830, 605, 870)]),
        ("GW_REPORT_PDF24_FOCUS15_21.png", (85, 1080, 1440, 1360), "V3_DOC07_OBE_NO_GUARANTEE.png", "Out-of-body movement — no guarantee",
         [(195, 1102, 600, 1137), (875, 1150, 1390, 1192), (110, 1188, 1390, 1328)]),
        ("GW_REPORT_PDF25_INFO_COLLECTION.png", (80, 1360, 1450, 1940), "V3_DOC08_INFORMATION_COLLECTION.png", "Information collection — ten digits, never all ten",
         [(200, 1407, 720, 1442), (150, 1628, 1390, 1872)]),
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (75, 205, 1450, 545), "V3_DOC09_RECOMMENDATION_H.png", "Recommendation H — the complete procedure",
         lines(108, [1305, 1375, 1375, 1370, 1375, 1375, 1375, 1210], 248, 33, 27)),
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (90, 635, 1435, 750), "V3_DOC10_NONCORPOREAL_FORMS.png", "Recommendation J — the complete claim",
         [(185, 661, 1320, 692), (108, 699, 1340, 731)]),
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (90, 742, 1435, 865), "V3_DOC11_HOLOGRAPHIC_BARRIER.png", "Recommendation K — the complete claim",
         [(187, 762, 1340, 793), (108, 798, 1370, 829), (108, 832, 925, 859)]),
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (90, 972, 1435, 1112), "V3_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png", "The report ends in the conditional",
         [(111, 1001, 1380, 1033), (111, 1038, 1378, 1070), (111, 1074, 655, 1105)]),
    ]
    for job in jobs:
        make(*job)
    print(f"Built {len(jobs)} line-accurate document crops in {OUT}")


if __name__ == "__main__":
    main()
