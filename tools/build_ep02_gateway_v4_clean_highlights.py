#!/usr/bin/env python3
"""Rebuild Gateway evidence crops with clean, continuous highlights.

V4: Fixes the patchy multi-line highlight appearance by merging
adjacent line rectangles into single continuous highlight regions.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "06_PRODUCTION" / "EP02_GATEWAY" / "reference_package"
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V4" / "visuals" / "document_crops"
W, H = 1920, 1080
BG = (4, 17, 20)
GOLD = (224, 174, 71)
OFF = (238, 235, 222)
CYAN = (91, 210, 211)
ARIAL_B = Path("C:/Windows/Fonts/arialbd.ttf")
SERIF = Path("C:/Windows/Fonts/georgia.ttf")


def f(path: Path, size: int):
    return ImageFont.truetype(str(path), size)


def merge_rects(rects: list[tuple[int, int, int, int]], gap: int = 8) -> list[tuple[int, int, int, int]]:
    """Merge vertically adjacent rectangles into continuous blocks.

    Rectangles are merged if they overlap horizontally and the vertical
    gap between them is <= `gap` pixels. This creates clean, continuous
    highlight regions instead of separate per-line boxes.
    """
    if not rects:
        return []

    # Sort by y1 then x1
    sorted_rects = sorted(rects, key=lambda r: (r[1], r[0]))
    merged = [list(sorted_rects[0])]

    for x1, y1, x2, y2 in sorted_rects[1:]:
        prev = merged[-1]
        # Check if this rect is adjacent to the previous one
        # (overlaps horizontally and is close vertically)
        h_overlap = (x1 < prev[2] + 20) and (x2 > prev[0] - 20)
        v_close = y1 <= prev[3] + gap

        if h_overlap and v_close:
            # Merge: extend the previous rectangle
            prev[0] = min(prev[0], x1)
            prev[1] = min(prev[1], y1)
            prev[2] = max(prev[2], x2)
            prev[3] = max(prev[3], y2)
        else:
            merged.append([x1, y1, x2, y2])

    return [tuple(r) for r in merged]


def lines(x1: int, x2s: list[int], y1: int, step: int = 34, height: int = 29) -> list[tuple[int, int, int, int]]:
    """One rectangle per typewritten line, allowing the final x edge to vary."""
    return [(x1, y1 + i * step, x2, y1 + i * step + height) for i, x2 in enumerate(x2s)]


def highlight_block(x1: int, y1: int, x2: int, y2: int) -> list[tuple[int, int, int, int]]:
    """Single continuous highlight rectangle."""
    return [(x1, y1, x2, y2)]


def multi_block(*blocks: tuple[int, int, int, int]) -> list[tuple[int, int, int, int]]:
    """Multiple explicit highlight blocks."""
    return list(blocks)


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

    # Merge adjacent highlights for clean continuous appearance
    merged_marks = merge_rects(marks, gap=10)

    for x1, y1, x2, y2 in merged_marks:
        box = (
            ox + round((x1 - crop_box[0]) * scale),
            oy + round((y1 - crop_box[1]) * scale),
            ox + round((x2 - crop_box[0]) * scale),
            oy + round((y2 - crop_box[1]) * scale),
        )
        # Softer, more elegant highlight: semi-transparent fill + subtle border
        d.rounded_rectangle(box, radius=4, fill=(*GOLD, 45), outline=(*GOLD, 200), width=2)

    d.text((82, 48), title, font=f(SERIF, 46), fill=OFF)
    tw = d.textbbox((0, 0), label, font=f(ARIAL_B, 24))[2]
    d.rounded_rectangle((W - tw - 132, 48, W - 72, 92), radius=6, fill=(25, 43, 45, 235), outline=(*CYAN, 180), width=2)
    d.text((W - tw - 102, 57), label, font=f(ARIAL_B, 24), fill=OFF)
    d.text((82, 1025), "U.S. ARMY GATEWAY REPORT · 1983", font=f(ARIAL_B, 20), fill=(105, 160, 160))
    OUT.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(canvas.convert("RGBA"), ov).convert("RGB").save(OUT / name, quality=96)


def main():
    jobs = [
        # DOC01: Army header with date - single clean block
        ("GW_REPORT_PDF01_HEADER.png", (70, 45, 1450, 420),
         "V4_DOC01_ARMY_HEADER_DATE.png", "Army header, date and subject",
         highlight_block(300, 110, 1010, 240) +
         highlight_block(1110, 260, 1385, 320)),

        # DOC02: Task + Bentov - continuous blocks instead of line-by-line
        ("GW_REPORT_PDF01_HEADER.png", (90, 620, 1440, 1260),
         "V4_DOC02_TASK_BENTOV.png", "The assigned task — and Bentov enters",
         highlight_block(130, 680, 1370, 780) +
         highlight_block(400, 880, 1260, 945)),

        # DOC03: McDonnell signature - single block
        ("GW_REPORT_PDF02_SIGNATURE.png", (650, 720, 1400, 1040),
         "V4_DOC03_MCDONNELL_SIGNATURE.png", "The author on the page",
         highlight_block(760, 810, 1325, 995)),

        # DOC04: Focus 15 heading - clean single line
        ("GW_REPORT_PDF24_FOCUS15_21.png", (95, 125, 1440, 360),
         "V4_DOC04_FOCUS15_HEADING.png", "Focus 15: Travel into the Past",
         highlight_block(245, 198, 745, 235)),

        # DOC05: Less than 5% - merged continuous block
        ("GW_REPORT_PDF24_FOCUS15_21.png", (90, 505, 1430, 705),
         "V4_DOC05_LESS_THAN_FIVE_PERCENT.png", "The report's complete difficulty warning",
         highlight_block(112, 512, 1395, 651)),

        # DOC06: Focus 21 Future - clean single line
        ("GW_REPORT_PDF24_FOCUS15_21.png", (90, 785, 1430, 920),
         "V4_DOC06_FOCUS21_FUTURE.png", "Focus 21: The Future",
         highlight_block(250, 830, 605, 870)),

        # DOC07: OBE no guarantee - merged continuous blocks
        ("GW_REPORT_PDF24_FOCUS15_21.png", (85, 1080, 1440, 1360),
         "V4_DOC07_OBE_NO_GUARANTEE.png", "Out-of-body movement — no guarantee",
         highlight_block(195, 1102, 600, 1137) +
         highlight_block(875, 1150, 1390, 1328)),

        # DOC08: Information collection - clean blocks
        ("GW_REPORT_PDF25_INFO_COLLECTION.png", (80, 1360, 1450, 1940),
         "V4_DOC08_INFORMATION_COLLECTION.png", "Information collection — ten digits, never all ten",
         highlight_block(200, 1407, 720, 1442) +
         highlight_block(150, 1628, 1390, 1872)),

        # DOC09: Recommendation H - continuous block (was 8 separate lines!)
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (75, 205, 1450, 545),
         "V4_DOC09_RECOMMENDATION_H.png", "Recommendation H — the complete procedure",
         highlight_block(108, 248, 1375, 472)),

        # DOC10: Noncorporeal forms - merged block
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (90, 635, 1435, 750),
         "V4_DOC10_NONCORPOREAL_FORMS.png", "Recommendation J — the complete claim",
         highlight_block(108, 661, 1340, 731)),

        # DOC11: Holographic barrier - merged block
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (90, 742, 1435, 865),
         "V4_DOC11_HOLOGRAPHIC_BARRIER.png", "Recommendation K — the complete claim",
         highlight_block(108, 762, 1370, 859)),

        # DOC12: If experiments carried through - merged block
        ("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png", (90, 972, 1435, 1112),
         "V4_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png", "The report ends in the conditional",
         highlight_block(111, 1001, 1380, 1105)),
    ]
    for job in jobs:
        make(*job)
    print(f"Built {len(jobs)} clean-highlight document crops in {OUT}")


if __name__ == "__main__":
    main()
