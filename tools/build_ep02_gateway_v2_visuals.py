#!/usr/bin/env python3
"""Build precise evidence crops and high-density explanatory cards for Gateway V2."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
V1 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY"
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2" / "visuals"
DOC = OUT / "document_crops"
CARD = OUT / "cards"
W, H = 1920, 1080
BG = (4, 17, 20)
CYAN = (91, 210, 211)
GOLD = (224, 174, 71)
OFF = (238, 235, 222)
RED = (213, 92, 78)
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_B = Path(r"C:\Windows\Fonts\arialbd.ttf")
SERIF = Path(r"C:\Windows\Fonts\georgia.ttf")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def frame_crop(source: Path, box: tuple[int, int, int, int], name: str, title: str,
               highlights: list[tuple[int, int, int, int]] | None = None,
               label: str = "IN THE REPORT") -> None:
    image = Image.open(source).convert("RGB")
    crop = image.crop(box)
    scale = min(1740 / crop.width, 850 / crop.height)
    crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (W, H), BG)
    x, y = (W - crop.width) // 2, 155 + (850 - crop.height) // 2
    canvas.paste(crop, (x, y))
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    for hbox in highlights or []:
        hx1 = x + round((hbox[0] - box[0]) * scale); hy1 = y + round((hbox[1] - box[1]) * scale)
        hx2 = x + round((hbox[2] - box[0]) * scale); hy2 = y + round((hbox[3] - box[1]) * scale)
        draw.rounded_rectangle((hx1, hy1, hx2, hy2), radius=8, fill=(*GOLD, 55), outline=(*GOLD, 235), width=4)
    draw.text((82, 48), title, font=font(SERIF, 46), fill=OFF)
    tw = draw.textbbox((0, 0), label, font=font(FONT_B, 24))[2]
    draw.rounded_rectangle((W - tw - 132, 48, W - 72, 92), radius=6, fill=(25, 43, 45, 235), outline=(*CYAN, 180), width=2)
    draw.text((W - tw - 102, 57), label, font=font(FONT_B, 24), fill=OFF)
    draw.text((82, 1025), "U.S. ARMY GATEWAY REPORT · 1983", font=font(FONT_B, 20), fill=(105, 160, 160))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    DOC.mkdir(parents=True, exist_ok=True); canvas.save(DOC / name, quality=95)


def card_base(kicker: str, title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    canvas = Image.new("RGB", (W, H), BG); draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((46, 40, W - 46, H - 40), radius=18, outline=(30, 78, 81), width=2)
    draw.text((86, 72), kicker, font=font(FONT_B, 22), fill=GOLD)
    draw.text((86, 116), title, font=font(SERIF, 52), fill=OFF)
    return canvas, draw


def save_card(image: Image.Image, name: str) -> None:
    CARD.mkdir(parents=True, exist_ok=True); image.save(CARD / name, quality=95)


def card_three_observers() -> None:
    im, d = card_base("RECOMMENDATION H", "Three observers. One target.")
    xs = [330, 960, 1590]; names = [("PAST", "FOCUS 15"), ("PRESENT", "NORMAL SPACE-TIME"), ("FUTURE", "FOCUS 21")]
    for x, (name, sub) in zip(xs, names):
        d.ellipse((x - 54, 285, x + 54, 393), outline=CYAN, width=5)
        d.line((x, 393, x, 560), fill=CYAN, width=5); d.line((x, 438, x - 70, 510), fill=CYAN, width=5); d.line((x, 438, x + 70, 510), fill=CYAN, width=5)
        d.text((x, 610), name, anchor="mm", font=font(FONT_B, 31), fill=OFF)
        d.text((x, 650), sub, anchor="mm", font=font(FONT, 21), fill=GOLD)
        d.line((x, 700, 960, 820), fill=(63, 137, 140), width=3)
    d.rounded_rectangle((715, 790, 1205, 900), radius=55, fill=GOLD)
    d.text((960, 845), "COMPARE REPORTS", anchor="mm", font=font(FONT_B, 28), fill=(8, 22, 24))
    d.text((960, 975), "PROPOSED PROCEDURE · NO RESULT REPORTED", anchor="mm", font=font(FONT_B, 21), fill=(112, 178, 178))
    save_card(im, "V2_CARD01_THREE_OBSERVERS.png")


def card_people_chain() -> None:
    im, d = card_base("WHO BUILT THE MODEL?", "Training, theory, assessment")
    entries = [("ROBERT MONROE", "TRAINING SYSTEM"), ("ITZHAK BENTOV", "ANALOGIES"), ("WAYNE McDONNELL", "ARMY ASSESSMENT")]
    for i, (name, role) in enumerate(entries):
        x1 = 100 + i * 610; x2 = x1 + 500
        d.rounded_rectangle((x1, 300, x2, 760), radius=18, fill=(10, 31, 35), outline=(50, 124, 127), width=3)
        d.ellipse((x1 + 180, 365, x1 + 320, 505), outline=GOLD, width=5)
        d.line((x1 + 250, 505, x1 + 250, 605), fill=GOLD, width=5)
        d.text(((x1 + x2) // 2, 650), name, anchor="mm", font=font(FONT_B, 27), fill=OFF)
        d.text(((x1 + x2) // 2, 700), role, anchor="mm", font=font(FONT_B, 19), fill=CYAN)
        if i < 2:
            d.line((x2 + 22, 530, x2 + 82, 530), fill=GOLD, width=5)
            d.polygon([(x2 + 82, 530), (x2 + 64, 518), (x2 + 64, 542)], fill=GOLD)
    d.text((960, 910), "THE REPORT CONNECTS ALL THREE", anchor="mm", font=font(FONT_B, 28), fill=(128, 188, 188))
    save_card(im, "V2_CARD02_PEOPLE_CHAIN.png")


def card_mechanism_ladder() -> None:
    im, d = card_base("THE LOGIC OF THE REPORT", "Where the evidentiary jump occurs")
    labels = [("TWO TONES", "PERCEPTION", CYAN), ("RELAXATION", "EXPERIENCE", CYAN),
              ("COHERENCE", "MODEL", GOLD), ("INFORMATION FIELD", "SPECULATION", RED),
              ("PAST / FUTURE", "EXTRAORDINARY CLAIM", RED)]
    for i, (main, sub, color) in enumerate(labels):
        x = 115 + i * 350; y = 350 + (i % 2) * 110
        d.rounded_rectangle((x, y, x + 300, y + 150), radius=18, fill=(11, 31, 35), outline=color, width=4)
        d.text((x + 150, y + 54), main, anchor="mm", font=font(FONT_B, 25), fill=OFF)
        d.text((x + 150, y + 105), sub, anchor="mm", font=font(FONT_B, 18), fill=color)
        if i < 4:
            d.line((x + 300, y + 75, x + 350, 425 + ((i + 1) % 2) * 110), fill=(100, 140, 140), width=4)
    d.line((1110, 260, 1110, 780), fill=RED, width=5)
    d.text((1140, 790), "CLAIM GAP", font=font(FONT_B, 26), fill=RED)
    save_card(im, "V2_CARD03_MECHANISM_LADDER.png")


def card_test_protocol() -> None:
    im, d = card_base("WHAT WOULD COUNT AS EVIDENCE?", "A state change is not yet information transfer")
    steps = [("1", "PRESELECT", "TARGET"), ("2", "BLIND", "OBSERVER"), ("3", "LOCK", "SCORING"), ("4", "REPEAT", "INDEPENDENTLY")]
    for i, (num, a, b) in enumerate(steps):
        x = 95 + i * 450
        d.ellipse((x, 330, x + 95, 425), fill=GOLD)
        d.text((x + 47, 377), num, anchor="mm", font=font(FONT_B, 38), fill=BG)
        d.rounded_rectangle((x, 485, x + 350, 700), radius=18, fill=(11, 31, 35), outline=CYAN, width=3)
        d.text((x + 175, 550), a, anchor="mm", font=font(FONT_B, 29), fill=OFF)
        d.text((x + 175, 615), b, anchor="mm", font=font(FONT_B, 24), fill=CYAN)
        if i < 3:
            d.line((x + 360, 592, x + 425, 592), fill=GOLD, width=5)
    d.text((960, 870), "THE REPORT DESCRIBES A PROPOSAL — NOT THIS COMPLETED CHAIN", anchor="mm", font=font(FONT_B, 24), fill=RED)
    save_card(im, "V2_CARD04_TEST_PROTOCOL.png")


def card_evidence_scale() -> None:
    im, d = card_base("SAME AUDIO. DIFFERENT CLAIMS.", "Do not confuse the size of the conclusion")
    d.line((270, 740, 1650, 740), fill=(97, 145, 145), width=8)
    points = [(360, "RELAXATION", "MEASURABLE"), (740, "ATTENTION", "PLAUSIBLE"), (1120, "REMOTE TARGET", "UNPROVEN"), (1550, "PAST / FUTURE", "UNPROVEN")]
    for x, name, state in points:
        color = CYAN if x < 1000 else RED
        d.ellipse((x - 32, 708, x + 32, 772), fill=color)
        d.text((x, 620), name, anchor="mm", font=font(FONT_B, 25), fill=OFF)
        d.text((x, 835), state, anchor="mm", font=font(FONT_B, 19), fill=color)
    d.line((930, 300, 930, 900), fill=GOLD, width=5)
    d.text((960, 260), "EVIDENCE GAP", anchor="mm", font=font(FONT_B, 27), fill=GOLD)
    save_card(im, "V2_CARD05_EVIDENCE_SCALE.png")


def main() -> int:
    rp = V1 / "reference_package"
    p1 = rp / "GW_REPORT_PDF01_HEADER.png"; p2 = rp / "GW_REPORT_PDF02_SIGNATURE.png"
    p24 = rp / "GW_REPORT_PDF24_FOCUS15_21.png"; p25 = rp / "GW_REPORT_PDF25_INFO_COLLECTION.png"
    p28 = rp / "GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"
    jobs = [
        (p1, (70, 45, 1450, 420), "V2_DOC01_ARMY_HEADER_DATE.png", "Army header, date and subject", [(1110, 260, 1385, 320), (300, 110, 1010, 240)]),
        (p1, (90, 620, 1440, 1260), "V2_DOC02_TASK_BENTOV.png", "The assigned task — and Bentov enters", [(130, 680, 1370, 770), (400, 880, 780, 950)]),
        (p2, (650, 720, 1400, 1040), "V2_DOC03_MCDONNELL_SIGNATURE.png", "The author on the page", [(760, 820, 1320, 990)]),
        (p24, (95, 125, 1440, 360), "V2_DOC04_FOCUS15_HEADING.png", "Focus 15: Travel into the Past", [(180, 160, 720, 220)]),
        (p24, (90, 440, 1430, 720), "V2_DOC05_LESS_THAN_FIVE_PERCENT.png", "The report's own difficulty warning", [(130, 530, 1360, 650)]),
        (p24, (90, 760, 1430, 1015), "V2_DOC06_FOCUS21_FUTURE.png", "Focus 21: The Future", [(170, 810, 600, 865)]),
        (p24, (85, 1000, 1440, 1370), "V2_DOC07_OBE_NO_GUARANTEE.png", "Out-of-body movement — no guarantee", [(110, 1110, 1390, 1265)]),
        (p25, (80, 1340, 1450, 1900), "V2_DOC08_INFORMATION_COLLECTION.png", "Information Collection Potential", [(120, 1410, 920, 1470), (120, 1740, 1380, 1870)]),
        (p28, (75, 175, 1450, 555), "V2_DOC09_RECOMMENDATION_H.png", "Recommendation H: three observers", [(105, 240, 1400, 520)]),
        (p28, (90, 610, 1435, 755), "V2_DOC10_NONCORPOREAL_FORMS.png", "Recommendation J", [(120, 655, 1390, 735)]),
        (p28, (90, 735, 1435, 875), "V2_DOC11_HOLOGRAPHIC_BARRIER.png", "Recommendation K", [(120, 760, 1390, 850)]),
        (p28, (90, 930, 1435, 1120), "V2_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png", "The report ends in the conditional", [(110, 990, 1390, 1090)]),
    ]
    for args in jobs: frame_crop(*args)
    card_three_observers(); card_people_chain(); card_mechanism_ladder(); card_test_protocol(); card_evidence_scale()
    print(f"Built {len(jobs)} evidence crops and 5 explanatory cards in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
