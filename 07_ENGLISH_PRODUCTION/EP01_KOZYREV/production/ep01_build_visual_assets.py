from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


EP = Path(__file__).resolve().parents[1]
CUE = EP / "06_TIMELINE" / "EP01_EN_VISUAL_CUE_SHEET.csv"
OUT = EP / "04_ASSETS" / "GENERATED" / "DETERMINISTIC"
SRC = EP / "04_SOURCES"
W, H = 1920, 1080


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = [
        "C:/Windows/Fonts/bahnschrift.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size=size)
    return ImageFont.load_default()


F18, F22, F28, F34, F46, F58, F78 = (font(n) for n in (18, 22, 28, 34, 46, 58, 78))
FB22, FB32, FB46, FB64, FB86 = (font(n, True) for n in (22, 32, 46, 64, 86))
WHITE = (235, 239, 240)
MUTED = (155, 169, 174)
INK = (13, 17, 19)
CYAN = (87, 203, 217)
AMBER = (224, 164, 72)
RED = (213, 80, 67)


def hval(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


def bg(state: str, warm: bool = False) -> Image.Image:
    seed = hval(state)
    top = (28, 25, 22) if warm else (8, 15, 19)
    bot = (7, 8, 10)
    sw, sh = 240, 135
    im = Image.new("RGB", (sw, sh), bot)
    p = im.load()
    cx = (620 + seed % 700) / W * sw
    cy = 470 / H * sh
    for y in range(sh):
        t = y / (sh - 1)
        for x in range(sw):
            radial = max(0.0, 1.0 - math.hypot(x - cx, y - cy) / 156)
            p[x, y] = tuple(int(bot[i] * t + top[i] * (1 - t) + radial * (9 if i == 2 else 5)) for i in range(3))
    return im.resize((W, H), Image.Resampling.BICUBIC)


def fit_inside(im: Image.Image, box: tuple[int, int, int, int], contain: bool = True) -> Image.Image:
    x0, y0, x1, y1 = box
    target = (x1 - x0, y1 - y0)
    if contain:
        c = ImageOps.contain(im.convert("RGB"), target, Image.Resampling.LANCZOS)
    else:
        c = ImageOps.fit(im.convert("RGB"), target, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    out = Image.new("RGB", target, (236, 234, 225))
    out.paste(c, ((target[0] - c.width) // 2, (target[1] - c.height) // 2))
    return out


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textbbox((0, 0), trial, font=f)[2] <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text_block(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, f: ImageFont.FreeTypeFont,
               fill=WHITE, width: int = 700, spacing: int = 12) -> int:
    x, y = xy
    for line in wrap(draw, text, f, width):
        draw.text((x, y), line, font=f, fill=fill)
        y += draw.textbbox((x, y), line, font=f)[3] - draw.textbbox((x, y), line, font=f)[1] + spacing
    return y


def grain(im: Image.Image, state: str) -> Image.Image:
    seed = hval(state)
    noise = Image.effect_noise((480, 270), 14 + seed % 8).convert("L").resize((W, H), Image.Resampling.BILINEAR)
    noise = ImageEnhance.Contrast(noise).enhance(.35)
    layer = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(im, layer, .045)


def save(im: Image.Image, state: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{state}.png"
    grain(im, state).save(path, compress_level=3)
    return path


def chrome(draw: ImageDraw.ImageDraw, state: str, kicker: str = "") -> None:
    draw.line((88, 82, 1832, 82), fill=(47, 71, 78), width=2)
    draw.ellipse((88, 61, 108, 81), fill=CYAN)


CARD_TITLES = {
    "KZ_CARD_MEDICAL_TO_TIME_MACHINE": "MEDICAL APPARATUS  TO  TIME MACHINE?",
    "KZ_CARD_1983_1996_CONTRADICTION": "DIED 1983  /  FILED 1996",
    "KZ_CARD_THREE_THEORIES_OPEN": "THREE EXPLANATIONS. NONE PROVEN.",
    "KZ_CARD_THEORY_ISOLATION": "1  ISOLATION",
    "KZ_CARD_THEORY_PHYSICAL": "2  PHYSICAL CHANGE",
    "KZ_CARD_THEORY_INFORMATION": "3  INFORMATION?",
    "KZ_CARD_STREAM_KOZYREV_TIME": "KOZYREV'S IDEA OF TIME",
    "KZ_CARD_STREAM_RESEARCHERS": "LATER RESEARCHERS",
    "KZ_CARD_STREAM_PATENT": "THE 1996 PATENT",
    "KZ_CARD_THREE_STREAMS_COLLAPSE": "THREE STORIES BECAME ONE",
    "KZ_CARD_THREE_STREAMS_SEPARATED": "SEPARATE THE THREADS",
    "KZ_CARD_TIME_AS_ACTIVE_IDEA": "TIME AS AN ACTIVE PROCESS",
    "KZ_CARD_WHY_DIRECTION": "WHY SHOULD DIRECTION MATTER?",
    "KZ_CARD_WHY_MOON": "WHY SHOULD THE MOON MATTER?",
    "KZ_CARD_CLAIM_NOT_PROOF": "A CLAIM IS NOT A RESULT",
    "KZ_CARD_PATENT_RECORDS_CLAIM": "A PATENT RECORDS A CLAIM",
    "KZ_CARD_THEORY_FORK_RETURN": "NOW TEST THE THREE EXPLANATIONS",
    "KZ_CARD_THEORY_ISOLATION_ACTIVE": "ISOLATION",
    "KZ_CARD_EXPERIENCE_NOT_INFORMATION": "EXPERIENCE IS NOT INFORMATION",
    "KZ_CARD_THEORY_PHYSICAL_ACTIVE": "PHYSICAL CHANGE",
    "KZ_CARD_PHYSICAL_VARIABLES": "TEMPERATURE  •  SOUND  •  MAGNETISM",
    "KZ_CARD_MEASURABLE_NOT_TIME_TRAVEL": "MEASURABLE IS NOT TIME TRAVEL",
    "KZ_CARD_THEORY_INFORMATION_ACTIVE": "INFORMATION FROM ELSEWHERE?",
    "KZ_CARD_EXTRAORDINARY_POSSIBILITY": "THE EXTRAORDINARY POSSIBILITY",
    "KZ_CARD_CLEAN_TEST": "A CLEAN TEST",
    "KZ_CARD_FEELING_NOT_TEST": "A FEELING IS NOT A TEST",
    "KZ_CARD_UNKNOWN_INFORMATION": "UNKNOWN INFORMATION — BEFORE REVEAL",
    "KZ_CARD_ONE_MATCH_CHANCE": "ONE MATCH CAN HAPPEN BY CHANCE",
    "KZ_CARD_POSTHOC_INTERPRETATION": "INTERPRETATION AFTER THE FACT",
    "KZ_CARD_THEORIES_FORCED_APART": "FORCE THE EXPLANATIONS APART",
    "KZ_CARD_PSYCHOLOGY_PREDICTION": "PREDICTION: REPORTS CHANGE",
    "KZ_CARD_PHYSICAL_PREDICTION": "PREDICTION: SENSORS CHANGE",
    "KZ_CARD_RANDOM_TARGET_BOUNDARY": "PREDICTION: HIDDEN TARGETS MATCH",
    "KZ_CARD_MISSING_EXPERIMENT": "THE DECISIVE EXPERIMENT IS MISSING",
    "KZ_CARD_APPARATUS_NOT_EVIDENCE": "AN APPARATUS IS NOT EVIDENCE",
    "KZ_CARD_INDEPENDENT_RESULT": "WHERE IS THE INDEPENDENT RESULT?",
    "KZ_CARD_LANGUAGE_OF_AUTHORITY": "THE LANGUAGE OF AUTHORITY",
    "KZ_CARD_PATENTED_MEANS_PROVEN": "PATENTED = PROVEN?",
    "KZ_CARD_IT_DOES_NOT": "IT DOES NOT.",
    "KZ_CARD_PATENT_CAN_SHOW": "A PATENT CAN SHOW WHO CLAIMED WHAT",
    "KZ_CARD_PATENT_NOT_CERTIFY": "IT CANNOT CERTIFY THE EFFECT",
    "KZ_CARD_DECISIVE_INFORMATION_QUESTION": "CAN IT DELIVER HIDDEN INFORMATION?",
    "KZ_CARD_RESULT_STILL_MISSING": "THE RESULT IS STILL MISSING",
    "KZ_CARD_THREE_OBSERVERS_THREE_TIMES": "THREE OBSERVERS. THREE TIMES.",
}


def build_card(state: str, voice: str) -> Image.Image:
    im = bg(state)
    d = ImageDraw.Draw(im)
    chrome(d, state, "question / boundary")
    title = CARD_TITLES.get(state, state.replace("KZ_CARD_", "").replace("_", " "))
    mode = hval(state) % 5
    accent = (CYAN, AMBER, RED)[hval(state) % 3]
    if mode == 0:
        d.rectangle((90, 210, 120, 860), fill=accent)
        text_block(d, (180, 255), title, FB86, width=1500, spacing=18)
        d.line((180, 700, 1650, 700), fill=(49, 67, 73), width=2)
    elif mode == 1:
        d.ellipse((1250, 170, 1760, 680), outline=accent, width=8)
        d.ellipse((1350, 270, 1660, 580), outline=(60, 85, 91), width=3)
        text_block(d, (120, 280), title, FB64, width=1040)
    elif mode == 2:
        for i in range(3):
            x = 150 + i * 540
            d.rounded_rectangle((x, 620, x + 430, 830), radius=18, outline=(54, 76, 82), width=3)
            d.ellipse((x + 176, 674, x + 254, 752), fill=accent if i == hval(state) % 3 else (37, 50, 55))
        text_block(d, (150, 210), title, FB64, width=1500)
    elif mode == 3:
        d.polygon([(1400, 170), (1790, 540), (1400, 910), (1150, 540)], outline=accent, fill=(15, 25, 29))
        d.line((1460, 260, 1460, 820), fill=(70, 92, 98), width=5)
        text_block(d, (120, 260), title, FB64, width=1080)
    else:
        for i in range(9):
            x = 980 + (i % 3) * 230
            y = 210 + (i // 3) * 230
            d.rounded_rectangle((x, y, x + 170, y + 170), radius=16, fill=(18, 31, 36), outline=accent if i == 4 else (50, 67, 72), width=3)
        text_block(d, (120, 250), title, FB64, width=760)
    if voice:
        text_block(d, (120, 890), voice, F28, fill=MUTED, width=1560, spacing=8)
    return im


SOURCE_LABELS = {
    "KZ_SRC_PATENT_COVER_DATE": ("Official filing", "Filed 2 July 1996", "patent:1", "KZ-SRC-001"),
    "KZ_SRC_PATENT_TITLE_CROP": ("The clinical title", "Device for correction of psychosomatic diseases", "patent:2", "KZ-SRC-001"),
    "KZ_SRC_PATENT_FIG2_CYLINDER": ("Configuration 1", "Cylinder", "patent:6", "KZ-SRC-001"),
    "KZ_SRC_PATENT_FIG3_CW": ("Configuration 2", "Clockwise spiral", "fig3", "KZ-SRC-001"),
    "KZ_SRC_PATENT_FIG4_ROTATION": ("Motorized platform", "Rotation is part of the claim", "fig4", "KZ-SRC-001"),
    "KZ_SRC_PATENT_LUNAR_GEOMAGNETIC": ("Claimed operating conditions", "Moon phase and geomagnetic conditions", "patent:4", "KZ-SRC-001"),
    "KZ_SRC_PATENT_HEIGHT": ("Maximum panel height", "2.8 metres", "patent:3", "KZ-SRC-001"),
    "KZ_SRC_PATENT_POLISHED_SURFACE_TEXT": ("Inner surface", "Ground and polished aluminum", "patent:3", "KZ-SRC-001"),
    "KZ_SRC_PATENT_FOCUS": ("Proposed focus", "50 centimetres from the working surface", "patent:3", "KZ-SRC-001"),
    "KZ_SRC_PATENT_PANEL_COUNT": ("Construction", "Four to ten curved panels", "patent:3", "KZ-SRC-001"),
    "KZ_SRC_PATENT_GEOMAGNETIC": ("Claimed condition", "Magneto-ionospheric storms", "patent:4", "KZ-SRC-001"),
    "KZ_SRC_PATENT_INVENTOR_CLAIM": ("Inventors' claim", "A field-concentration effect", "patent:1", "KZ-SRC-001"),
    "KZ_SRC_PATENT_HELIOGEOPHYSICAL": ("Claimed schedule", "Heliogeophysical conditions", "patent:4", "KZ-SRC-001"),
    "KZ_SRC_INVENTOR_PAIR_CLAIMS": ("Named inventors", "Kaznacheev and Trofimov", "patent:2", "KZ-SRC-001"),
    "KZ_SRC_PATENT_AUTHORITY_TRAP": ("The document looks definitive", "But a filing is not a replication", "patent:1", "KZ-SRC-001"),
    "KZ_SRC_PATENT_AUTHORITY_FULL": ("Russian patent RU 2122446 C1", "Publication: 27 November 1998", "patent:2", "KZ-SRC-001"),
    "KZ_SRC_PATENT_NUMBER_CROP": ("Document number", "RU 2122446 C1", "patent:1", "KZ-SRC-001"),
    "KZ_SRC_PATENT_DATES_CROP": ("Dates", "Filed 1996 • Published 1998", "patent:2", "KZ-SRC-001"),
    "KZ_SRC_PATENT_INVENTORS_CROP": ("Inventors", "V. P. Kaznacheev • A. V. Trofimov", "patent:2", "KZ-SRC-001"),
    "KZ_SRC_PATENT_DRAWINGS": ("Four drawings", "Cylinder, spirals and rotating platform", "patent:8", "KZ-SRC-001"),
    "KZ_SRC_PATENT_FOCUS_TEXT_DETAIL": ("Claim detail", "Focus: 50 cm", "patent:3", "KZ-SRC-001"),
    "KZ_SRC_PATENT_DIRECTION_TEXT_DETAIL": ("Claim detail", "Left- or right-twisted spiral", "patent:3", "KZ-SRC-001"),
    "KZ_SRC_PATENT_ROTATION_TEXT_DETAIL": ("Claim detail", "Motorized rotation", "patent:3", "KZ-SRC-001"),
    "KZ_SRC_PATENT_DIMENSIONS": ("Claim detail", "1.5 mm • 2.8 m • 1.2 m", "patent:5", "KZ-SRC-001"),
    "KZ_SRC_PATENT_DOCUMENTED_CHAMBER": ("What the patent establishes", "A described aluminum apparatus", "patent:6", "KZ-SRC-001"),
    "KZ_SRC_EVIDENCE_PATENT": ("Evidence layer 1", "A real patent", "patent:2", "KZ-SRC-001"),
}


def source_path(token: str) -> Path:
    if token.startswith("patent:"):
        return SRC / "RENDERS" / "PATENT" / f"RU2122446C1-{token.split(':')[1]}.png"
    if token == "fig3":
        return SRC / "RENDERS" / "PATENT" / "RU2122446C1_FIG3_SPIRAL_UPRIGHT.png"
    if token == "fig4":
        return SRC / "RENDERS" / "PATENT" / "RU2122446C1_FIG4_ROTATING_SPIRAL_UPRIGHT.png"
    return SRC / token


def source_composite(state: str, voice: str) -> tuple[Image.Image, str]:
    # Identity and publication states use distinct files so no portrait/page returns.
    special: dict[str, tuple[str, str, str, str]] = {
        "KZ_SRC_KOZYREV_PORTRAIT_1983": ("Nikolai Kozyrev", "1908–1983", "ORIGINALS/Nikolai_Kozyrev_1959.png", "KZ-SRC-002"),
        "KZ_HISTORY_PULKOVO_OBSERVATORY": ("Pulkovo Observatory", "Kozyrev's astronomical world", "ORIGINALS/Pulkovo_Observatory_1855_Bernardsky_PD.jpg", "KZ-SRC-015"),
        "KZ_HISTORY_PULKOVO_REFRACTOR": ("Astronomical instrument", "Pulkovo Observatory refractor", "ORIGINALS/Pulkovo_refractor_Vladimir_Ivanov_PD.jpg", "KZ-SRC-017"),
        "KZ_HISTORY_KOZYREV_NOT_CHAMBER_BUILDER": ("Kozyrev's actual field", "astronomy ended in 1983 • chamber patent filed 1996", "ORIGINALS/Pulkovo_big_refractor_1884_plate_PD.jpg", "KZ-SRC-019"),
        "KZ_PATENT_NO_KOZYREV_INVENTOR_FIELD": ("Inventors listed", "Kaznacheev • Trofimov — not Kozyrev", "patent:2", "KZ-SRC-001"),
        "KZ_SRC_2006_MODELED_SPACE": ("Modeled ‘Kozyrev space’", "Kaznacheev & Trofimov, 2006", "RENDERS/PAPERS/Kaznacheev_Trofimov_2006-1.png", "KZ-SRC-006"),
        "KZ_SRC_2006_ALTERED_INTERNAL_TIME": ("Claimed optical effects", "Kaznacheev & Trofimov, 2006", "RENDERS/PAPERS/Kaznacheev_Trofimov_2006-2.png", "KZ-SRC-006"),
        "KZ_SRC_RESEARCHERS_LATER_WORK": ("Distant-information interactions", "Kaznacheev & Trofimov, 2008", "RENDERS/PAPERS/Kaznacheev_Trofimov_2008-1.png", "KZ-SRC-007"),
        "KZ_SRC_CLAIM_HISTORY_PUBLICATIONS": ("The claims continued", "conference collection, 2019", "RENDERS/COLLECTION_SELECTED/collection_page_142.png", "KZ-SRC-008"),
        "KZ_SRC_EVIDENCE_PUBLICATIONS": ("Evidence layer 2", "authors' publications", "RENDERS/COLLECTION_SELECTED/collection_page_115.png", "KZ-SRC-008"),
        "KZ_SRC_EVIDENCE_STACK": ("What remains", "patent • papers • apparatus", "RENDERS/COLLECTION_SELECTED/collection_page_138.png", "KZ-SRC-008"),
        "KZ_SRC_KAZNACHEEV_TROFIMOV_CLAIM_HISTORY": ("Later chamber work", "documented in the 2019 collection", "RENDERS/COLLECTION_SELECTED/collection_page_168.png", "KZ-SRC-008"),
        "KZ_SRC_RESEARCHERS_AND_PUBLICATIONS": ("Researchers and publications", "documented identities, separate claims", "RENDERS/COLLECTION_SELECTED/collection_page_161.png", "KZ-SRC-008"),
    }
    if state in special:
        title, fact, token, sid = special[state]
    elif state in SOURCE_LABELS:
        title, fact, token, sid = SOURCE_LABELS[state]
    else:
        title = state.replace("KZ_SRC_", "").replace("_", " ").title()
        fact, token, sid = voice, "patent:1", "KZ-SRC-001"
    path = source_path(token)
    src = Image.open(path).convert("RGB")
    im = bg(state, warm=True)
    d = ImageDraw.Draw(im)
    chrome(d, state, "source")
    seed = hval(state)
    # Distinct factual detail: a source page is cropped to a different vertical region, not cosmetically re-exported.
    patent_crops = {
        "KZ_SRC_PATENT_COVER_DATE": (.07, .03, .93, .43),
        "KZ_SRC_PATENT_TITLE_CROP": (.07, .34, .93, .68),
        "KZ_SRC_PATENT_NUMBER_CROP": (.24, .02, .92, .23),
        "KZ_SRC_PATENT_DATES_CROP": (.08, .18, .91, .38),
        "KZ_SRC_PATENT_INVENTORS_CROP": (.48, .20, .93, .43),
        "KZ_PATENT_NO_KOZYREV_INVENTOR_FIELD": (.47, .18, .95, .45),
        "KZ_SRC_PATENT_DIMENSIONS": (.05, .03, .95, .34),
        "KZ_SRC_PATENT_FOCUS_TEXT_DETAIL": (.52, .00, .92, .095),
        "KZ_SRC_PATENT_HEIGHT": (.48, .13, .95, .48),
        "KZ_SRC_PATENT_PANEL_COUNT": (.48, .15, .95, .56),
        "KZ_SRC_PATENT_POLISHED_SURFACE_TEXT": (.50, .265, .94, .355),
        "KZ_SRC_PATENT_DIRECTION_TEXT_DETAIL": (.47, .30, .95, .74),
        "KZ_SRC_PATENT_ROTATION_TEXT_DETAIL": (.47, .48, .95, .96),
        "KZ_SRC_PATENT_HELIOGEOPHYSICAL": (.04, .02, .48, .42),
        "KZ_SRC_PATENT_LUNAR_GEOMAGNETIC": (.04, .25, .48, .67),
        "KZ_SRC_PATENT_GEOMAGNETIC": (.47, .02, .95, .42),
        "KZ_SRC_PATENT_INVENTOR_CLAIM": (.04, .32, .56, .72),
    }
    if token.startswith("patent:") and state in patent_crops:
        x0, y0, x1, y1 = patent_crops[state]
        src = src.crop((int(src.width*x0), int(src.height*y0), int(src.width*x1), int(src.height*y1)))
    elif token.startswith("patent:") and state not in {"KZ_SRC_PATENT_AUTHORITY_FULL", "KZ_SRC_EVIDENCE_PATENT"}:
        crop_h = int(src.height * .55)
        y0 = int((src.height - crop_h) * ((seed % 41) / 40))
        src = src.crop((int(src.width * .04), y0, int(src.width * .96), min(src.height, y0 + crop_h)))
    panel = fit_inside(src, (90, 135, 1160, 960), contain=True)
    panel = panel.filter(ImageFilter.UnsharpMask(radius=1.4, percent=130, threshold=2))
    im.paste(panel, (90, 135))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1210, 190, 1810, 855), radius=22, fill=(14, 20, 23), outline=(77, 89, 88), width=2)
    d.rectangle((1210, 190, 1221, 855), fill=AMBER)
    text_block(d, (1270, 270), title, FB46, width=470, spacing=14)
    text_block(d, (1270, 550), fact, F34, fill=(218, 210, 193), width=470)
    if state in {"KZ_SRC_PATENT_COVER_DATE", "KZ_SRC_KOZYREV_PORTRAIT_1983"}:
        d.text((1270, 800), "Source recorded in episode manifest", font=F22, fill=MUTED)
    return im, sid


def build_focus_model(state: str) -> tuple[Image.Image, str]:
    """A new explanatory composition, not a recrop of an earlier patent page."""
    im = bg(state, warm=False)
    d = ImageDraw.Draw(im)
    chrome(d, state, "explanatory geometry")
    cx, cy = 610, 550
    wall_box = (215, 165, 1035, 935)
    d.arc(wall_box, start=292, end=68, fill=(198, 206, 207), width=30)
    d.arc((250, 200, 1000, 900), start=292, end=68, fill=(72, 98, 105), width=5)
    focus = (1120, cy)
    for y in (315, 430, 550, 670, 785):
        x = int(cx + ((wall_box[2] - wall_box[0]) / 2) * .78)
        d.line((x, y, focus[0], focus[1]), fill=CYAN, width=4)
    d.ellipse((focus[0] - 16, focus[1] - 16, focus[0] + 16, focus[1] + 16), fill=AMBER)
    d.line((900, 875, focus[0], 875), fill=WHITE, width=3)
    d.line((900, 858, 900, 892), fill=WHITE, width=3)
    d.line((focus[0], 858, focus[0], 892), fill=WHITE, width=3)
    d.text((935, 900), "50 cm", font=F34, fill=WHITE)
    d.rounded_rectangle((1240, 205, 1810, 835), radius=22, fill=(14, 20, 23), outline=(77, 89, 88), width=2)
    d.rectangle((1240, 205, 1251, 835), fill=AMBER)
    text_block(d, (1300, 285), "Proposed focus", FB46, width=440)
    text_block(d, (1300, 550), "Curvature directs the claimed focus in front of the working surface", F28, fill=(218, 210, 193), width=430)
    return im, "KZ-SRC-001"


def inventor_pair(state: str) -> tuple[Image.Image, str]:
    first_identity_beat = state == "KZ_SRC_INVENTOR_PAIR_1996"
    left = SRC / ("RENDERS/KAZNACHEEV/Kaznacheev_memorial-12.png" if first_identity_beat else "RENDERS/PAPERS/Kaznacheev_Trofimov_2006-1.png")
    right = SRC / ("RENDERS/TROFIMOV/Trofimov_keynote-6.png" if first_identity_beat else "RENDERS/PAPERS/Kaznacheev_Trofimov_2008-1.png")
    im = bg(state, warm=True)
    d = ImageDraw.Draw(im)
    chrome(d, state, "named researchers")
    role = "patent inventor" if first_identity_beat else "publication author"
    for x, p, name in [(100, left, "VLAIL KAZNACHEEV"), (1010, right, "ALEXANDER TROFIMOV")]:
        pic = fit_inside(Image.open(p), (x, 150, x + 810, 790), contain=False)
        im.paste(ImageEnhance.Contrast(pic).enhance(1.05), (x, 150))
        d = ImageDraw.Draw(im)
        d.rectangle((x, 790, x + 810, 930), fill=(10, 15, 17))
        d.text((x + 34, 815), name, font=FB32, fill=WHITE)
        d.text((x + 34, 868), role, font=F22, fill=MUTED)
    return im, "KZ-SRC-004+005" if first_identity_beat else "KZ-SRC-006+007"


def spiral(draw: ImageDraw.ImageDraw, center: tuple[int, int], scale: float, reverse=False, color=CYAN, width=9):
    pts = []
    cx, cy = center
    for i in range(170):
        t = i / 169 * math.pi * 3.3
        if reverse:
            t = -t
        r = 18 + scale * i / 169
        pts.append((cx + math.cos(t) * r, cy + math.sin(t) * r))
    draw.line(pts, fill=color, width=width, joint="curve")


def build_model(state: str, voice: str) -> Image.Image:
    im = bg(state)
    d = ImageDraw.Draw(im)
    chrome(d, state, "explanatory model")
    title = state.replace("KZ_MODEL_", "").replace("KZ_PROTOCOL_", "").replace("KZ_REPLICATION_", "").replace("KZ_TARGET_GRID_", "TARGET GRID ").replace("KZ_TARGET_MATCH_", "TARGET MATCH ").replace("_", " ").title()
    text_block(d, (110, 150), title.upper(), FB46, width=1650)
    if "DIRECTION_COMPARE" in state or "FIG3_CCW" in state:
        spiral(d, (620, 590), 280, False, CYAN, 12)
        spiral(d, (1320, 590), 280, True, AMBER, 12)
        d.text((430, 890), "CLOCKWISE", font=F28, fill=MUTED)
        d.text((1150, 890), "COUNTERCLOCKWISE", font=F28, fill=MUTED)
    elif "ROTATION" in state:
        spiral(d, (960, 600), 300, False, CYAN, 15)
        d.arc((570, 210, 1350, 990), 200, 510, fill=AMBER, width=12)
        d.polygon([(1280, 260), (1380, 290), (1305, 355)], fill=AMBER)
    elif "FIELD_CONCENTRATION" in state or "INFORMATION_ACROSS_DISTANCE" in state:
        for i in range(11):
            y = 300 + i * 55
            bend = int(100 * math.sin(i / 10 * math.pi))
            d.bezier if hasattr(d, "bezier") else None
            d.line((180, y, 790, y - bend, 1130, y + bend, 1740, y), fill=(45 + i * 3, 112 + i * 5, 123 + i * 5), width=3)
        d.ellipse((875, 510, 1045, 680), outline=AMBER, width=8)
        if "INFORMATION" in state:
            d.rectangle((145, 420, 355, 640), outline=WHITE, width=4)
            d.rectangle((1560, 420, 1770, 640), outline=WHITE, width=4)
    elif "ORDINARY_VARIABLES" in state:
        labels = ["TEMPERATURE", "SOUND", "MAGNETISM", "EXPECTATION"]
        for i, lab in enumerate(labels):
            x = 160 + i * 420
            d.rounded_rectangle((x, 390, x + 330, 690), radius=28, fill=(15, 30, 35), outline=(55, 85, 92), width=4)
            d.ellipse((x + 115, 465, x + 215, 565), outline=(CYAN, AMBER, RED, WHITE)[i], width=8)
            d.text((x + 32, 615), lab, font=F22, fill=MUTED)
    elif state.startswith("KZ_TARGET_GRID_"):
        for i in range(4):
            x = 160 + i * 420
            y = 405
            selected = state.endswith("CHOOSE") and i == 0
            held = state.endswith("HOLD") and i == 0
            c = AMBER if selected or held else (58, 82, 89)
            d.rounded_rectangle((x, y, x + 320, y + 240), radius=20, fill=(14, 25, 29), outline=c, width=6 if selected else 3)
            d.line((x+20,y+28,x+160,y+135,x+300,y+28), fill=c, width=3)
            if held and i != 0:
                d.rectangle((x, y, x+320, y+240), fill=(2,6,8,145))
    elif state == "KZ_TARGET_MATCH_LIGHTHOUSE":
        # New explanatory drawing, not a crop or reuse of the target photograph.
        d.rounded_rectangle((170, 310, 820, 780), radius=24, fill=(14,25,29), outline=(55,82,89), width=4)
        d.polygon([(430,700),(560,700),(530,390),(460,390)], outline=CYAN)
        d.rectangle((445,330,545,410), outline=CYAN, width=6)
        d.line((385,330,605,330), fill=CYAN, width=5)
        d.arc((315,285,675,645), 205, 335, fill=(89,122,130), width=4)
        d.rounded_rectangle((1090, 310, 1740, 780), radius=24, fill=(18,22,23), outline=(80,72,62), width=4)
        rng = random.Random(7021)
        pts = [(1140 + i*48, 610 + rng.randrange(-70,70)) for i in range(11)]
        d.line(pts, fill=(216,205,178), width=5)
        d.line((1340,690,1440,420,1510,690), fill=(216,205,178), width=7)
        d.ellipse((1390,370,1490,455), outline=(216,205,178), width=5)
    elif "PROTOCOL" in state or "REPLICATION" in state or "TARGET" in state:
        stages = ["RANDOMIZE", "SEAL", "SESSION", "JUDGE", "REPEAT"]
        active = hval(state) % len(stages)
        for i, lab in enumerate(stages):
            x = 95 + i * 360
            c = CYAN if i <= active else (43, 56, 61)
            d.rounded_rectangle((x, 430, x + 260, 660), radius=22, outline=c, width=5, fill=(12, 22, 26))
            d.text((x + 25, 535), lab, font=F22, fill=WHITE if i <= active else MUTED)
            if i < len(stages) - 1:
                d.line((x + 270, 545, x + 345, 545), fill=c, width=5)
        if "MISSING" in state:
            d.line((1535, 390, 1820, 710), fill=RED, width=12)
            d.line((1820, 390, 1535, 710), fill=RED, width=12)
    else:
        spiral(d, (960, 590), 310, hval(state) % 2 == 0, CYAN, 13)
    text_block(d, (110, 900), voice, F28, fill=MUTED, width=1650)
    return im


def build_map(state: str) -> Image.Image:
    im = bg(state)
    d = ImageDraw.Draw(im)
    chrome(d, state, "next file")
    geo = json.loads((SRC / "ORIGINALS/Natural_Earth_110m_countries.geojson").read_text(encoding="utf-8"))
    def xy(lon, lat):
        return int((lon + 180) / 360 * W), int((90 - lat) / 180 * H)
    for ft in geo["features"]:
        geom = ft["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            for ring in poly[:1]:
                pts = [xy(a, b) for a, b, *_ in ring]
                if len(pts) > 2:
                    d.polygon(pts, fill=(18, 31, 35), outline=(42, 60, 66))
    novos = xy(82.92, 55.03)
    fort = xy(-76.73, 39.10)
    if state.endswith("FORT_MEADE_ZOOM"):
        d.ellipse((fort[0] - 160, fort[1] - 160, fort[0] + 160, fort[1] + 160), outline=AMBER, width=9)
        d.text((fort[0] + 190, fort[1] - 35), "FORT MEADE", font=FB46, fill=WHITE)
    else:
        d.line((novos[0], novos[1], fort[0], fort[1]), fill=CYAN, width=6)
        d.ellipse((novos[0] - 15, novos[1] - 15, novos[0] + 15, novos[1] + 15), fill=CYAN)
        d.ellipse((fort[0] - 15, fort[1] - 15, fort[0] + 15, fort[1] + 15), fill=AMBER)
        d.text((novos[0] + 25, novos[1] - 55), "NOVOSIBIRSK", font=F28, fill=WHITE)
        d.text((fort[0] + 25, fort[1] - 55), "FORT MEADE", font=F28, fill=WHITE)
    return im


def build_reflection_state() -> Image.Image:
    source = EP / "04_ASSETS/GENERATED/NANO_BANANA_PRO/KZ_EN_HERO01.png"
    im = ImageOps.fit(Image.open(source).convert("RGB"), (W, H), Image.Resampling.LANCZOS)
    # This is a distinct, single late subjective state: a new mirrored composition, never a callback export.
    right = ImageOps.mirror(im.crop((W // 2, 0, W, H))).filter(ImageFilter.GaussianBlur(3))
    im.paste(right, (W // 2, 0))
    veil = Image.new("RGBA", (W, H), (0, 14, 19, 0))
    ImageDraw.Draw(veil).rectangle((W // 2, 0, W, H), fill=(0, 35, 44, 70))
    return Image.alpha_composite(im.convert("RGBA"), veil).convert("RGB")


def build() -> dict[str, dict[str, str]]:
    rows = list(csv.DictReader(CUE.open(encoding="utf-8-sig")))
    unique: dict[str, dict[str, str]] = {}
    for row in rows:
        unique.setdefault(row["visual_state_id"], row)
    out_map = EP / "04_ASSETS" / "METADATA" / "deterministic_asset_map.json"
    manifest: dict[str, dict[str, str]] = {}
    asset_manifest = EP / "04_ASSETS" / "ASSET_MANIFEST.csv"
    if asset_manifest.exists():
        for prior in csv.DictReader(asset_manifest.open(encoding="utf-8-sig")):
            if prior.get("provider") == "LOCAL_DETERMINISTIC_PIL":
                manifest[prior["asset_id"]] = {
                    "file_path": prior["file_path"],
                    "source_id": prior.get("source_id", ""),
                    "provider": "LOCAL_DETERMINISTIC_PIL",
                    "status": "BUILT_AWAITING_VISUAL_QA",
                }
    pair_states = {"KZ_SRC_INVENTOR_PAIR_1996", "KZ_SRC_KAZNACHEEV_TROFIMOV_PAIR"}
    source_states = {
        "KZ_HISTORY_PULKOVO_OBSERVATORY",
        "KZ_HISTORY_PULKOVO_REFRACTOR",
        "KZ_HISTORY_KOZYREV_NOT_CHAMBER_BUILDER",
        "KZ_PATENT_NO_KOZYREV_INVENTOR_FIELD",
    }
    forced_states = {value.strip() for value in os.getenv("EP01_REBUILD_STATES", "").split(",") if value.strip()}
    for state, row in unique.items():
        status = row["asset_status"]
        cached = OUT / f"{state}.png"
        if status not in {"NEEDS_DETERMINISTIC_BUILD", "NEEDS_SOURCE_COMPOSITE", "NEEDS_SOURCE_RESEARCH"} and state not in forced_states:
            if status != "SELECTED_READY" or not cached.exists():
                continue
        if state == "KZ_HERO01_REFLECTION_STATE":
            continue
        if cached.exists() and os.getenv("EP01_REBUILD_DETERMINISTIC") != "1" and state not in forced_states:
            try:
                with Image.open(cached) as check:
                    if check.size == (W, H):
                        prior_source_id = manifest.get(state, {}).get("source_id", "")
                        manifest[state] = {
                            "file_path": cached.relative_to(EP).as_posix(),
                            "source_id": prior_source_id,
                            "provider": "LOCAL_DETERMINISTIC_PIL",
                            "status": "BUILT_AWAITING_VISUAL_QA",
                        }
                        continue
            except OSError:
                pass
        voice = row["voice_text"]
        sid = ""
        if state == "KZ_SRC_PATENT_FOCUS":
            im, sid = build_focus_model(state)
        elif state in pair_states:
            im, sid = inventor_pair(state)
        elif state.startswith("KZ_SRC_") or state in source_states or status in {"NEEDS_SOURCE_COMPOSITE", "NEEDS_SOURCE_RESEARCH"}:
            im, sid = source_composite(state, voice)
        elif state.startswith("KZ_CARD_"):
            im = build_card(state, voice)
        elif state.startswith("KZ_MAP_"):
            im = build_map(state)
        elif state == "KZ_HERO01_REFLECTION_STATE":
            im = build_reflection_state()
        else:
            im = build_model(state, voice)
        path = save(im, state)
        manifest[state] = {
            "file_path": path.relative_to(EP).as_posix(),
            "source_id": sid,
            "provider": "LOCAL_DETERMINISTIC_PIL",
            "status": "BUILT_AWAITING_VISUAL_QA",
        }
    out_map.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"built={len(manifest)} output={OUT}")
    return manifest


if __name__ == "__main__":
    build()
