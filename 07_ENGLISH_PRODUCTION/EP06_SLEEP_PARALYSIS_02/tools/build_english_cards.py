#!/usr/bin/env python3
"""Build mobile-readable English evidence and interaction cards."""

from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


EP = Path(__file__).resolve().parents[1]
OUT = EP / "03_VISUALS" / "ASSETS" / "CARDS"
W, H = 1920, 1080
FONT_REG = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), size)


def base(seed: int, warm: bool = False) -> Image.Image:
    random.seed(seed)
    img = Image.new("RGB", (W, H))
    px = img.load()
    c0 = (11, 18, 27) if not warm else (25, 18, 15)
    c1 = (18, 38, 50) if not warm else (59, 38, 24)
    for y in range(H):
        t = y / (H - 1)
        for x in range(W):
            radial = max(0.0, 1.0 - math.hypot((x - W * 0.53) / W, (y - H * 0.48) / H) * 1.8)
            noise = random.randint(-3, 3)
            px[x, y] = tuple(max(0, min(255, int(c0[i] * (1 - radial * .6) + c1[i] * radial * .6 + noise))) for i in range(3))
    return img.filter(ImageFilter.GaussianBlur(0.35))


def line(draw: ImageDraw.ImageDraw, y: int, x0: int = 170, x1: int = 1750, color=(72, 196, 210)) -> None:
    draw.rounded_rectangle((x0, y, x1, y + 5), 3, fill=color)


def save(img: Image.Image, name: str, manifest: list[dict], text: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    img.save(path, quality=96)
    manifest.append({"file": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "visible_text": text})
    mobile = img.resize((246, 138), Image.Resampling.LANCZOS)
    mobile.save(OUT / f"MOBILE_{name}")


def study_scope(manifest: list[dict]) -> None:
    img = base(6201)
    d = ImageDraw.Draw(img)
    d.text((170, 130), "A CROSS-CULTURAL COMPARISON", font=font(35, True), fill=(100, 207, 219))
    d.text((170, 245), "EGYPT", font=font(112, True), fill=(245, 221, 179))
    d.text((795, 260), "and", font=font(55), fill=(190, 201, 208))
    d.text((995, 245), "DENMARK", font=font(112, True), fill=(220, 238, 241))
    line(d, 415)
    d.text((170, 500), "Specific samples.", font=font(72, True), fill=(245, 245, 241))
    d.text((170, 605), "Not portraits of entire countries.", font=font(65), fill=(205, 213, 218))
    d.text((170, 920), "Jalal & Hinton · Culture, Medicine, and Psychiatry · 2013", font=font(28), fill=(142, 158, 168))
    save(img, "CARD_STUDY_SCOPE.png", manifest, ["A CROSS-CULTURAL COMPARISON", "EGYPT and DENMARK", "Specific samples.", "Not portraits of entire countries."])


def study_results(manifest: list[dict]) -> None:
    img = base(6202)
    d = ImageDraw.Draw(img)
    d.text((170, 115), "STUDY I · LIFETIME SLEEP PARALYSIS", font=font(34, True), fill=(100, 207, 219))
    d.text((170, 240), "44%", font=font(150, True), fill=(245, 221, 179))
    d.text((520, 280), "Egyptian sample", font=font(52), fill=(239, 239, 234))
    d.text((520, 350), "207 of 470", font=font(34), fill=(163, 176, 184))
    d.text((1080, 240), "25%", font=font(150, True), fill=(220, 238, 241))
    d.text((1430, 280), "Danish", font=font(52), fill=(239, 239, 234))
    d.text((1430, 342), "sample", font=font(52), fill=(239, 239, 234))
    d.text((1430, 410), "56 of 223", font=font(34), fill=(163, 176, 184))
    line(d, 505)
    d.text((170, 585), "STUDY II · MEAN LIFETIME EPISODES AMONG EXPERIENCERS", font=font(31, True), fill=(100, 207, 219))
    d.text((170, 690), "19.4", font=font(105, True), fill=(245, 221, 179))
    d.text((520, 725), "Egyptian sample", font=font(44), fill=(225, 228, 227))
    d.text((1080, 690), "6.0", font=font(105, True), fill=(220, 238, 241))
    d.text((1355, 725), "Danish sample", font=font(44), fill=(225, 228, 227))
    d.text((170, 955), "Reported sample results · PMID 23884906", font=font(28), fill=(142, 158, 168))
    save(img, "CARD_STUDY_RESULTS.png", manifest, ["44% Egyptian sample 207 of 470", "25% Danish sample 56 of 223", "19.4 vs 6.0 mean lifetime episodes"])


def association(manifest: list[dict]) -> None:
    img = base(6203, warm=True)
    d = ImageDraw.Draw(img)
    d.text((170, 120), "WITHIN THE EGYPTIAN SAMPLE", font=font(37, True), fill=(238, 188, 118))
    d.text((170, 260), "SUPERNATURAL", font=font(105, True), fill=(245, 237, 220))
    d.text((170, 370), "ATTRIBUTION", font=font(105, True), fill=(245, 237, 220))
    d.text((858, 500), "↕", font=font(88, True), fill=(104, 201, 211))
    d.text((170, 625), "GREATER FEAR", font=font(75, True), fill=(237, 206, 167))
    d.text((1045, 625), "LONGER IMMOBILITY", font=font(62, True), fill=(237, 206, 167))
    line(d, 765, color=(104, 201, 211))
    d.text((170, 830), "ASSOCIATED IN THE DATA", font=font(46, True), fill=(230, 235, 233))
    d.text((170, 900), "Direction remains unresolved.", font=font(40), fill=(168, 181, 183))
    d.text((1435, 962), "PMID 23884906", font=font(26), fill=(132, 145, 148))
    save(img, "CARD_STUDY_ASSOCIATION.png", manifest, ["WITHIN THE EGYPTIAN SAMPLE", "SUPERNATURAL ATTRIBUTION", "GREATER FEAR", "LONGER IMMOBILITY", "ASSOCIATED IN THE DATA", "Direction remains unresolved."])


def interaction(manifest: list[dict]) -> None:
    img = base(6204)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 180), "WHAT CARRIES MORE POWER", font=font(40, True), fill=(155, 175, 184), anchor="ma")
    d.text((W // 2, 245), "INTO THE NEXT NIGHT?", font=font(40, True), fill=(155, 175, 184), anchor="ma")
    d.text((W // 2, 435), "EXPERIENCE", font=font(118, True), fill=(242, 221, 180), anchor="mm")
    d.text((W // 2, 560), "or", font=font(48), fill=(112, 204, 215), anchor="mm")
    d.text((W // 2, 695), "STORY", font=font(145, True), fill=(230, 240, 241), anchor="mm")
    d.text((W // 2, 900), "Leave one word below.", font=font(42), fill=(174, 187, 192), anchor="mm")
    save(img, "CARD_EXPERIENCE_OR_STORY.png", manifest, ["WHAT CARRIES MORE POWER INTO THE NEXT NIGHT?", "EXPERIENCE", "or", "STORY", "Leave one word below."])


def source_identity_cards(manifest: list[dict]) -> None:
    img = base(6205, warm=True); d = ImageDraw.Draw(img)
    d.text((170, 135), "DAVID J. HUFFORD", font=font(58, True), fill=(239, 188, 111))
    line(d, 235, color=(104, 201, 211))
    d.text((170, 330), "THE TERROR THAT", font=font(95, True), fill=(247, 239, 220))
    d.text((170, 435), "COMES IN THE NIGHT", font=font(95, True), fill=(247, 239, 220))
    d.text((170, 600), "An experience-centered study of", font=font(47), fill=(211, 219, 218))
    d.text((170, 665), "supernatural assault traditions", font=font(47), fill=(211, 219, 218))
    d.text((170, 905), "University of Pennsylvania Press · 1982", font=font(31), fill=(151, 165, 169))
    d.text((170, 955), "Bibliographic identification · not a simulated book cover", font=font(25), fill=(125, 138, 143))
    save(img, "CARD_DAVID_HUFFORD_WORK.png", manifest, ["DAVID J. HUFFORD", "THE TERROR THAT COMES IN THE NIGHT", "University of Pennsylvania Press · 1982"])

    img = base(6206); d = ImageDraw.Draw(img)
    d.text((170, 125), "BALAND JALAL", font=font(66, True), fill=(244, 220, 178))
    d.text((170, 210), "DEVON E. HINTON", font=font(66, True), fill=(221, 239, 241))
    line(d, 320)
    d.text((170, 395), "RATES AND CHARACTERISTICS", font=font(61, True), fill=(244, 244, 238))
    d.text((170, 475), "OF SLEEP PARALYSIS", font=font(61, True), fill=(244, 244, 238))
    d.text((170, 555), "IN DENMARK AND EGYPT", font=font(61, True), fill=(244, 244, 238))
    d.text((170, 720), "Culture, Medicine, and Psychiatry · 37 · 2013", font=font(35), fill=(179, 192, 197))
    d.text((170, 785), "DOI 10.1007/s11013-013-9327-x · PMID 23884906", font=font(31), fill=(139, 164, 172))
    d.text((170, 955), "Bibliographic source card · concise mobile view", font=font(25), fill=(123, 139, 145))
    save(img, "CARD_JALAL_HINTON_PAPER.png", manifest, ["BALAND JALAL", "DEVON E. HINTON", "RATES AND CHARACTERISTICS OF SLEEP PARALYSIS IN DENMARK AND EGYPT", "2013"])


def document_evidence(manifest: list[dict]) -> None:
    src = EP / "03_VISUALS" / "ASSETS" / "ORIGINAL"
    items = [
        (
            "SRC_EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692_p1_full.png",
            "EVIDENCE_COMAN_FULL_CONTEXT.png",
            "RICHARD COMAN TESTIMONY",
            "Salem · 2 June 1692 · full manuscript context",
            None,
        ),
        (
            "SRC_EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692_p1_pressure_passage.png",
            "EVIDENCE_COMAN_PRESSURE.png",
            '“lay upon my breast or body”',
            "Richard Coman testimony · 2 June 1692",
            (275, 405, 1700, 555),
        ),
        (
            "SRC_EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692_p1_cannot_speak_nor_stir.png",
            "EVIDENCE_COMAN_SPEAK_STIR.png",
            '“could not speak nor stir”',
            "Transcription of Richard Coman testimony · 2 June 1692",
            (70, 490, 1760, 690),
        ),
    ]
    for source, name, title, footer, highlight in items:
        raw = Image.open(src / source).convert("RGB")
        if "FULL_CONTEXT" in name:
            fitted = ImageOps.contain(raw, (W, H), Image.Resampling.LANCZOS)
            img = Image.new("RGB", (W, H), (13, 18, 24))
            img.paste(fitted, ((W - fitted.width) // 2, (H - fitted.height) // 2))
        else:
            img = ImageOps.fit(raw, (W, H), Image.Resampling.LANCZOS)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        if highlight:
            d.rounded_rectangle(highlight, 12, fill=(224, 171, 83, 34), outline=(247, 205, 126, 210), width=5)
        d.rectangle((0, 835, W, H), fill=(8, 12, 17, 220))
        d.text((110, 875), title, font=font(56, True), fill=(246, 237, 216, 255))
        d.text((110, 965), footer, font=font(29), fill=(159, 184, 194, 255))
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
        save(img, name, manifest, [title, footer])


def main() -> None:
    manifest: list[dict] = []
    study_scope(manifest)
    study_results(manifest)
    association(manifest)
    interaction(manifest)
    source_identity_cards(manifest)
    document_evidence(manifest)
    (OUT / "CARDS_MANIFEST.json").write_text(json.dumps({"episode": "EP06_EN", "canvas": "1920x1080", "mobile_qa": "246x138", "cards": manifest}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cards": len(manifest), "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
