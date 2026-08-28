#!/usr/bin/env python3
"""Build two upload-ready NOESIS English Shorts with unique 9:16 assets.

The edit is driven by ElevenLabs forced alignment. Every editorial beat gets a
new visual; no still is reused within a Short. Still motion is rendered at 90
fps and temporally blended down to 30 fps to avoid the small pan/zoom judder
that was visible in earlier exports.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import fitz
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
W, H, FPS, SUB = 1080, 1920, 30, 3
BG = (7, 12, 17)
INK = (239, 235, 224)
MUTED = (163, 172, 178)
AMBER = (224, 164, 63)
CYAN = (92, 190, 202)

KZ = ROOT / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV" / "10_SHORTS" / "S01_NEVER_BUILT"
GW = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY" / "10_SHORTS" / "S01_THREE_TIMES"


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-6000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


FB = lambda n: font("arialbd.ttf", n)
FR = lambda n: font("arial.ttf", n)


def base() -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    px = im.load()
    for y in range(H):
        t = y / H
        c = (int(7 + 7*t), int(12 + 8*t), int(17 + 10*t))
        for x in range(W):
            px[x, y] = c
    return im


def glow(im: Image.Image, xy: tuple[int, int], color: tuple[int, int, int], radius=360):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = xy
    d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(*color, 78))
    layer = layer.filter(ImageFilter.GaussianBlur(radius // 2))
    im.paste(layer, (0, 0), layer)


def cover(src: Path, size: tuple[int, int], focus=(0.5, 0.5)) -> Image.Image:
    im = Image.open(src).convert("RGB")
    sw, sh = im.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    im = im.resize((round(sw*scale), round(sh*scale)), Image.Resampling.LANCZOS)
    x = max(0, min(im.width-tw, round((im.width-tw)*focus[0])))
    y = max(0, min(im.height-th, round((im.height-th)*focus[1])))
    return im.crop((x, y, x+tw, y+th))


def contain(src: Path, size: tuple[int, int], bg=(242, 238, 224)) -> Image.Image:
    im = Image.open(src).convert("RGB")
    im.thumbnail(size, Image.Resampling.LANCZOS)
    out = Image.new("RGB", size, bg)
    out.paste(im, ((size[0]-im.width)//2, (size[1]-im.height)//2))
    return out


def rounded_paste(dst: Image.Image, src: Image.Image, xy: tuple[int, int], radius=30,
                  outline=(55, 66, 73), width=2):
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, src.width-1, src.height-1), radius, fill=255)
    dst.paste(src, xy, mask)
    d = ImageDraw.Draw(dst)
    d.rounded_rectangle((xy[0], xy[1], xy[0]+src.width, xy[1]+src.height), radius,
                        outline=outline, width=width)


def label(d: ImageDraw.ImageDraw, text: str, y: int, color=AMBER, size=30):
    d.text((72, y), text.upper(), font=FB(size), fill=color)
    d.line((72, y+size+20, 350, y+size+20), fill=color, width=4)


def centered(d: ImageDraw.ImageDraw, text: str, y: int, f: ImageFont.FreeTypeFont, fill=INK):
    box = d.textbbox((0, 0), text, font=f)
    d.text(((W-(box[2]-box[0]))/2, y), text, font=f, fill=fill)


def wrap(d: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        probe = f"{cur} {word}".strip()
        if cur and d.textlength(probe, font=f) > width:
            lines.append(cur); cur = word
        else:
            cur = probe
    if cur: lines.append(cur)
    return lines


def save(im: Image.Image, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, quality=96)


def kz_assets() -> dict[str, Path]:
    out = KZ / "03_ASSETS" / "SHORT_SPECIFIC"
    src = ROOT / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV" / "04_SOURCES"
    portrait = src / "ORIGINALS" / "Nikolai_Kozyrev_1959.png"
    patent = src / "RENDERS" / "PATENT" / "RU2122446C1-1.png"
    fig3 = src / "RENDERS" / "PATENT" / "RU2122446C1_FIG3_SPIRAL_UPRIGHT.png"
    fig4 = src / "RENDERS" / "PATENT" / "RU2122446C1_FIG4_ROTATING_SPIRAL_UPRIGHT.png"
    result: dict[str, Path] = {}

    im = base(); glow(im, (250, 620), CYAN); d = ImageDraw.Draw(im)
    p = cover(portrait, (936, 1160), (0.5, 0.43)); p = ImageEnhance.Contrast(p).enhance(1.08)
    rounded_paste(im, p, (72, 180), 34)
    label(d, "The man behind the name", 80, CYAN)
    d.rectangle((72, 1050, 1008, 1415), fill=(7, 12, 17))
    d.text((96, 1090), "NIKOLAI\nKOZYREV", font=FB(88), fill=INK, spacing=4)
    d.text((98, 1315), "ASTRONOMER  •  DIED 1983", font=FB(35), fill=AMBER)
    result["kz_portrait"] = out / "KZ_S01_D01_KOZYREV_PORTRAIT.png"; save(im, result["kz_portrait"])

    im = base(); glow(im, (820, 940), AMBER); d = ImageDraw.Draw(im)
    label(d, "The thirteen-year gap", 95)
    p1 = cover(portrait, (360, 520), (0.5, 0.4)); rounded_paste(im, p1, (80, 330), 28)
    p2 = contain(patent, (440, 620)); rounded_paste(im, p2, (560, 290), 28)
    d.text((90, 920), "1983", font=FB(116), fill=INK)
    d.text((88, 1050), "KOZYREV DIES", font=FB(34), fill=MUTED)
    d.line((448, 1000, 620, 1000), fill=AMBER, width=8)
    d.polygon([(620, 1000), (584, 979), (584, 1021)], fill=AMBER)
    d.text((642, 920), "1996", font=FB(116), fill=INK)
    d.text((642, 1050), "PATENT FILED", font=FB(34), fill=AMBER)
    centered(d, "THE NAME CAME FIRST.", 1070, FB(58))
    centered(d, "THE MACHINE CAME LATER.", 1155, FB(58))
    result["kz_timeline"] = out / "KZ_S01_D02_1983_1996_TIMELINE.png"; save(im, result["kz_timeline"])

    im = base(); glow(im, (500, 850), AMBER); d = ImageDraw.Draw(im)
    label(d, "Russian patent RU 2122446 C1", 85)
    pg = contain(patent, (620, 940)); rounded_paste(im, pg, (230, 250), 28)
    d.rounded_rectangle((96, 1120, 984, 1340), 30, fill=(18, 27, 33), outline=AMBER, width=3)
    d.text((140, 1150), "FILED  •  2 JULY 1996", font=FB(45), fill=INK)
    d.text((140, 1230), "INVENTORS", font=FB(26), fill=MUTED)
    d.text((140, 1270), "KAZNACHEEV  •  TROFIMOV", font=FB(40), fill=AMBER)
    result["kz_patent"] = out / "KZ_S01_D03_PATENT_IDENTITY.png"; save(im, result["kz_patent"])

    im = base(); glow(im, (540, 820), CYAN); d = ImageDraw.Draw(im)
    label(d, "What the drawings describe", 85, CYAN)
    a = contain(fig3, (820, 440), (245, 242, 232)); rounded_paste(im, a, (130, 245), 30)
    b = contain(fig4, (820, 440), (245, 242, 232)); rounded_paste(im, b, (130, 820), 30)
    d.text((154, 710), "CURVED PANELS", font=FB(37), fill=INK)
    d.text((154, 1285), "ROTATING PLATFORM", font=FB(37), fill=INK)
    d.arc((785, 1270, 950, 1435), 45, 310, fill=AMBER, width=12)
    d.polygon([(927, 1282), (955, 1262), (949, 1298)], fill=AMBER)
    result["kz_drawings"] = out / "KZ_S01_D04_PATENT_DRAWINGS.png"; save(im, result["kz_drawings"])

    im = base(); glow(im, (540, 720), AMBER); d = ImageDraw.Draw(im)
    label(d, "Evidence boundary", 110)
    centered(d, "THE DESIGN", 490, FB(108))
    centered(d, "IS DOCUMENTED", 660, FB(72), MUTED)
    centered(d, "THE EFFECT?", 790, FB(118), AMBER)
    centered(d, "STILL OPEN", 925, FB(82), INK)
    d.line((215, 1035, 865, 1035), fill=(55, 68, 76), width=4)
    for y, txt in [(1090, "OFFICIAL PATENT"), (1185, "SPECIFIC APPARATUS"), (1280, "OUTCOME UNRESOLVED")]:
        d.ellipse((170, y+10, 202, y+42), outline=CYAN, width=5)
        d.text((235, y), txt, font=FB(43), fill=INK if "UNRESOLVED" not in txt else AMBER)
    result["kz_boundary"] = out / "KZ_S01_D05_DOCUMENTED_OPEN.png"; save(im, result["kz_boundary"])

    im = base(); glow(im, (540, 780), (174, 116, 220)); d = ImageDraw.Draw(im)
    label(d, "The question the patent leaves open", 105, (174, 116, 220))
    centered(d, "WHAT HAPPENED", 480, FB(82))
    centered(d, "INSIDE?", 615, FB(142), (174, 116, 220))
    d.line((205, 850, 875, 850), fill=(70, 61, 84), width=4)
    centered(d, "ALTERED PERCEPTION", 990, FB(48), CYAN)
    centered(d, "OR", 1085, FB(34), MUTED)
    centered(d, "INFORMATION ACROSS TIME", 1170, FB(43), AMBER)
    centered(d, "THE FILE REMAINS OPEN", 1300, FB(34), MUTED)
    result["kz_open"] = out / "KZ_S01_D08_OPEN_QUESTION.png"; save(im, result["kz_open"])

    kaz = src / "RENDERS" / "KAZNACHEEV" / "Kaznacheev_memorial-12.png"
    tro = src / "RENDERS" / "TROFIMOV" / "Trofimov_keynote-6.png"
    im = base(); glow(im, (540, 760), AMBER); d = ImageDraw.Draw(im)
    label(d, "The names on the later research", 90)
    left = cover(kaz, (430, 760), (0.5, 0.35)); right = cover(tro, (430, 760), (0.5, 0.30))
    rounded_paste(im, left, (80, 285), 28); rounded_paste(im, right, (570, 285), 28)
    d.text((85, 1090), "VLAIL\nKAZNACHEEV", font=FB(47), fill=INK, spacing=4)
    d.text((575, 1090), "ALEXANDER\nTROFIMOV", font=FB(47), fill=INK, spacing=4)
    centered(d, "TWO OTHER RESEARCHERS", 1305, FB(43), AMBER)
    result["kz_pair"] = out / "KZ_S01_D09_RESEARCHER_PAIR.png"; save(im, result["kz_pair"])

    for key, head, sub, accent in [
        ("kz_episode", "THE KOZYREV\nEVIDENCE TRAIL", "FULL EPISODE  •  NOESIS", AMBER),
        ("kz_follow", "ONE FILE ENDS.\nANOTHER OPENS.", "FOLLOW NOESIS", CYAN),
    ]:
        im = base(); glow(im, (540, 830), accent); d = ImageDraw.Draw(im)
        d.ellipse((190, 370, 890, 1070), outline=accent, width=5)
        d.ellipse((260, 440, 820, 1000), outline=(58, 74, 82), width=3)
        d.text((100, 1050), head, font=FB(78), fill=INK, spacing=10)
        d.text((105, 1200), sub, font=FB(38), fill=accent)
        d.text((105, 1275), "↓  WATCH THE FULL INVESTIGATION", font=FB(30), fill=MUTED)
        result[key] = out / f"KZ_S01_{'D06_FULL_EPISODE' if key=='kz_episode' else 'D07_FOLLOW'}.png"; save(im, result[key])

    cover_path = KZ / "05_OUTPUT" / "SHORT_COVER_9x16.png"
    im = cover(KZ / "03_ASSETS" / "GENERATED" / "KZ_S01_G01_ROTATING_CHAMBER.png", (W, H))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
    sd.rectangle((0, 0, W, 400), fill=(4, 8, 12, 120)); sd.rectangle((0, 1080, W, H), fill=(4, 8, 12, 205))
    im.paste(shade, (0, 0), shade); d = ImageDraw.Draw(im)
    d.text((70, 90), "NOESIS  •  MODELS OF MIND", font=FB(30), fill=AMBER)
    d.text((70, 1200), "KOZYREV", font=FB(112), fill=INK)
    d.text((70, 1335), "NEVER BUILT IT", font=FB(76), fill=AMBER)
    d.text((72, 1460), "THE NAME CAME FIRST", font=FB(39), fill=INK)
    save(im, cover_path)
    return result


def render_gateway_recommendation() -> Image.Image:
    pdf = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY" / "02_SOURCES" / "ORIGINAL_DOCUMENTS" / "CIA-RDP96-00788R001700210016-5_TEXT_LAYER.pdf"
    doc = fitz.open(pdf)
    page = doc[27]
    pix = page.get_pixmap(matrix=fitz.Matrix(3.5, 3.5), alpha=False)
    full = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    # Metadata-verified crop: full Recommendation H paragraph with clear line edges.
    scale = 3.5
    box = tuple(round(v*scale) for v in (0, 75, 612, 215.5))
    return full.crop(box)


def gw_assets() -> dict[str, Path]:
    out = GW / "03_ASSETS" / "SHORT_SPECIFIC"
    src = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
    header = src / "03_VISUALS" / "DOCUMENT_CROPS" / "GW_EN_DOC01_ARMY_HEADER.png"
    result: dict[str, Path] = {}

    im = base(); glow(im, (540, 750), CYAN); d = ImageDraw.Draw(im)
    label(d, "The file behind the myth", 90, CYAN)
    h = cover(header, (936, 760), (0.42, 0.5)); rounded_paste(im, h, (72, 260), 34)
    d.text((88, 1130), "GATEWAY", font=FB(122), fill=INK)
    d.text((92, 1280), "1983  •  ARMY ANALYSIS", font=FB(43), fill=AMBER)
    result["gw_file"] = out / "GW_S01_D01_GATEWAY_FILE.png"; save(im, result["gw_file"])

    im = base(); glow(im, (540, 860), CYAN); d = ImageDraw.Draw(im)
    label(d, "Compare only after the session", 90, CYAN)
    for i, (x, title, col) in enumerate([(70, "NOW", CYAN), (390, "PAST", AMBER), (710, "FUTURE", (174, 116, 220))]):
        d.rounded_rectangle((x, 390, x+300, 1190), 28, fill=(18, 27, 34), outline=col, width=4)
        d.ellipse((x+88, 500, x+212, 624), outline=col, width=8)
        d.line((x+150, 625, x+150, 900), fill=col, width=8)
        d.text((x+26, 1010), title, font=FB(49), fill=col)
        d.text((x+70, 1110), "SEALED", font=FB(26), fill=MUTED)
    centered(d, "THREE REPORTS.  ONE TARGET.", 1345, FB(48))
    centered(d, "NO CROSS-TALK.", 1435, FB(48), AMBER)
    result["gw_compare"] = out / "GW_S01_D02_COMPARE_AFTER.png"; save(im, result["gw_compare"])

    im = base(); glow(im, (540, 720), (174, 116, 220)); d = ImageDraw.Draw(im)
    label(d, "It reads like fiction", 100, (174, 116, 220))
    d.rounded_rectangle((105, 330, 975, 1340), 36, fill=(13, 18, 25), outline=(78, 67, 93), width=4)
    centered(d, "ONE TARGET", 470, FB(77))
    centered(d, "THREE TIMES", 610, FB(105), (174, 116, 220))
    d.line((245, 820, 835, 820), fill=(78, 67, 93), width=4)
    centered(d, "PRESENT  /  PAST  /  FUTURE", 930, FB(35), MUTED)
    centered(d, "THIS WAS A TEST PLAN.", 1130, FB(42), AMBER)
    result["gw_fiction"] = out / "GW_S01_D03_SCIENCE_FICTION.png"; save(im, result["gw_fiction"])

    im = base(); glow(im, (540, 900), AMBER); d = ImageDraw.Draw(im)
    label(d, "Original page • Recommendation H", 80)
    rec = render_gateway_recommendation()
    rec.thumbnail((936, 700), Image.Resampling.LANCZOS)
    paper = Image.new("RGB", (936, rec.height+100), (239, 235, 219))
    paper.paste(rec, ((936-rec.width)//2, 50))
    rounded_paste(im, paper, (72, 280), 28, outline=AMBER, width=4)
    y = 280 + paper.height + 90
    centered(d, "THREE INDIVIDUALS", y, FB(58))
    centered(d, "PRESENT  •  PAST  •  FUTURE", y+100, FB(45), AMBER)
    centered(d, "DEBRIEF — THEN COMPARE", y+195, FB(39), MUTED)
    result["gw_recommendation"] = out / "GW_S01_D04_RECOMMENDATION_H_FULL.png"; save(im, result["gw_recommendation"])

    im = base(); glow(im, (540, 800), CYAN); d = ImageDraw.Draw(im)
    label(d, "The document trail", 95, CYAN)
    h = cover(header, (890, 610), (0.50, 0.50)); rounded_paste(im, h, (95, 260), 30)
    centered(d, "PREPARED FOR", 980, FB(34), MUTED)
    centered(d, "THE UNITED STATES ARMY", 1040, FB(55), INK)
    d.line((230, 1170, 850, 1170), fill=CYAN, width=5)
    centered(d, "LATER RELEASED THROUGH", 1225, FB(31), MUTED)
    centered(d, "THE CIA ARCHIVE", 1280, FB(58), CYAN)
    result["gw_archive"] = out / "GW_S01_D10_ARMY_TO_CIA_ARCHIVE.png"; save(im, result["gw_archive"])

    cards = [
        ("gw_plan", "THE FILE STAYS OPEN", "A THREE-OBSERVER TEST", "OUTCOME UNRESOLVED", AMBER),
        ("gw_choice", "YOUR DECISION", "AUTHORIZE", "OR STOP?", CYAN),
        ("gw_comment", "ONE WORD", "AUTHORIZE", "OR  STOP", AMBER),
        ("gw_episode", "THE FULL GATEWAY FILE", "WATCH THE LONGFORM", "LINKED BELOW", CYAN),
        ("gw_follow", "THE NEXT FILE", "FOLLOW NOESIS", "DON'T MISS IT", AMBER),
    ]
    for idx, (key, small, main, sub, accent) in enumerate(cards, 5):
        im = base(); glow(im, (540, 760), accent); d = ImageDraw.Draw(im)
        label(d, small, 125, accent)
        d.rounded_rectangle((90, 390, 990, 1350), 44, fill=(13, 20, 27), outline=accent, width=4)
        lines = main.split("\n")
        yy = 560
        for ln in lines:
            size = 92
            while d.textlength(ln, font=FB(size)) > 790: size -= 3
            centered(d, ln, yy, FB(size), INK); yy += 125
        centered(d, sub, 1030 if len(lines)==1 else 1110, FB(58), accent)
        if key == "gw_choice":
            d.line((230, 1260, 850, 1260), fill=(63, 77, 85), width=4)
        d.text((110, 1240), "NOESIS  /  MODELS OF MIND", font=FB(30), fill=MUTED)
        result[key] = out / f"GW_S01_D{idx:02d}_{key.upper()}.png"; save(im, result[key])

    cover_path = GW / "05_OUTPUT" / "SHORT_COVER_9x16.png"
    im = cover(GW / "03_ASSETS" / "GENERATED" / "GW_S01_G01_THREE_OBSERVERS.png", (W, H))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
    sd.rectangle((0, 0, W, 420), fill=(4, 8, 12, 130)); sd.rectangle((0, 1050, W, H), fill=(4, 8, 12, 210))
    im.paste(shade, (0, 0), shade); d = ImageDraw.Draw(im)
    d.text((70, 90), "THE GATEWAY FILE", font=FB(34), fill=CYAN)
    d.text((70, 1190), "ONE TARGET", font=FB(92), fill=INK)
    d.text((70, 1315), "THREE TIMES", font=FB(100), fill=CYAN)
    d.text((72, 1460), "WOULD YOU AUTHORIZE IT?", font=FB(38), fill=INK)
    save(im, cover_path)
    return result


def shared_key() -> str:
    cli = Path.home() / "Documents" / "Codex" / "NOESIS Channel" / "tools" / "elevenlabs_cli.py"
    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", cli)
    if spec is None or spec.loader is None: raise RuntimeError(f"Cannot load {cli}")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module._load_key()


def multipart(audio: Path, text: str):
    boundary = "----NOESISSHORT" + uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\n".encode(), b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
        f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        b"Content-Type: audio/mpeg\r\n\r\n", audio.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), boundary


def align(short_root: Path, stem: str):
    audio = short_root / "02_VOICE" / "raw" / f"{stem}.mp3"
    text = (short_root / "01_SCRIPT" / "VOICE_SCRIPT_EN.txt").read_text(encoding="utf-8").strip()
    body, boundary = multipart(audio, text)
    req = Request("https://api.elevenlabs.io/v1/forced-alignment", data=body,
                  headers={"xi-api-key": shared_key(), "Content-Type": f"multipart/form-data; boundary={boundary}",
                           "Accept": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=600) as res: data = json.loads(res.read().decode())
    except HTTPError as exc:
        raise RuntimeError(f"Alignment HTTP {exc.code}: {exc.read().decode(errors='replace')[:1000]}")
    data.update({"source_text": text, "audio": str(audio.resolve()),
                 "audio_sha256": hashlib.sha256(audio.read_bytes()).hexdigest()})
    path = short_root / "02_VOICE" / "alignment" / f"{stem}_alignment.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Alignment -> {path}")


def alignment_arrays(data: dict):
    for x in (data, data.get("alignment", {}), data.get("normalized_alignment", {})):
        chars = x.get("characters")
        starts = x.get("character_start_times_seconds")
        ends = x.get("character_end_times_seconds")
        if chars and starts and ends: return "".join(chars), starts, ends
        if chars and isinstance(chars[0], dict) and {"text", "start", "end"} <= set(chars[0]):
            return ("".join(c["text"] for c in chars),
                    [float(c["start"]) for c in chars],
                    [float(c["end"]) for c in chars])
    raise RuntimeError("Unsupported ElevenLabs alignment schema")


def anchor_time(text: str, starts: list[float], anchor: str) -> float:
    pos = text.lower().find(anchor.lower())
    if pos < 0: raise RuntimeError(f"Anchor not found: {anchor}")
    return float(starts[pos])


def ass_time(t: float) -> str:
    cs = round(t*100); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def caption_chunks(text: str, starts: list[float], ends: list[float]) -> list[tuple[float,float,str]]:
    words = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    chunks, i = [], 0
    while i < len(words):
        j = i
        # End immediately at punctuation; otherwise keep compact four-word beats.
        while j < len(words) and j-i < 4:
            j += 1
            if re.search(r"[.!?—]$", words[j-1][0]):
                break
        phrase = " ".join(w[0] for w in words[i:j])
        a = max(0.0, float(starts[words[i][1]])-0.04)
        b = float(ends[words[j-1][2]-1])+0.08
        chunks.append((a, b, phrase))
        i = j
    return chunks


def write_subtitles(short_root: Path, stem: str, text: str, starts: list[float], ends: list[float]):
    out = short_root / "05_OUTPUT"
    out.mkdir(parents=True, exist_ok=True)
    chunks = caption_chunks(text, starts, ends)
    srt = []
    def tc(t):
        ms=round(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    for i,(a,b,phrase) in enumerate(chunks,1):
        srt += [str(i), f"{tc(a)} --> {tc(b)}", phrase, ""]
    (out / f"{stem}.srt").write_text("\n".join(srt), encoding="utf-8")
    ass = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Arial,64,&H00F5F2EA,&H000000FF,&H0010151A,&HC510151A,-1,0,0,0,100,100,0,0,3,4,0,2,125,125,385,1", "",
        "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for a,b,phrase in chunks:
        safe = phrase.replace("{", "(").replace("}", ")")
        ass.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Default,,0,0,0,,{safe}")
    path = out / f"{stem}.ass"; path.write_text("\n".join(ass)+"\n", encoding="utf-8-sig")
    return path


def camera(i: int, seconds: float) -> str:
    frames = max(1, int(round(seconds*FPS))*SUB)
    lin = f"(on/{frames})"; ease = f"({lin}*{lin}*(3-2*{lin}))"
    patterns = [
        (1.025, 1.068, f"(iw-iw/zoom)*(0.42+0.12*{ease})", "ih/2-(ih/zoom/2)"),
        (1.070, 1.030, f"(iw-iw/zoom)*(0.55-0.10*{ease})", "ih/2-(ih/zoom/2)"),
        (1.030, 1.060, "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(0.44+0.10*{ease})"),
        (1.060, 1.028, "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(0.56-0.10*{ease})"),
    ]
    z0,z1,x,y=patterns[i%len(patterns)]
    return (f"zoompan=z='{z0}+({z1-z0})*{ease}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS*SUB},"
            f"tmix=frames={SUB}:weights='1 1 1',fps={FPS},format=yuv420p")


def make_bed(seconds: float, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg","-y","-hide_banner","-loglevel","error",
         "-f","lavfi","-i",f"sine=frequency=48:duration={seconds}",
         "-f","lavfi","-i",f"sine=frequency=73:duration={seconds}",
         "-f","lavfi","-i",f"anoisesrc=d={seconds}:c=brown:a=.035",
         "-filter_complex",f"[0:a]volume=.13[a];[1:a]volume=.055[b];[2:a]lowpass=f=430,volume=.35[c];"
         f"[a][b][c]amix=inputs=3:normalize=0,afade=t=in:st=0:d=0.7,afade=t=out:st={max(0,seconds-1.2)}:d=1.2[out]",
         "-map","[out]","-ar","48000","-ac","2","-c:a","pcm_s16le",str(path)])


def render(short_root: Path, stem: str, anchors: list[str], visuals: list[Path], title: str, link: str):
    alignment = short_root / "02_VOICE" / "alignment" / f"{stem}_alignment.json"
    data = json.loads(alignment.read_text(encoding="utf-8"))
    text, starts, ends = alignment_arrays(data)
    voice = short_root / "02_VOICE" / "raw" / f"{stem}.mp3"
    total = duration(voice)
    times = [anchor_time(text, starts, a) for a in anchors] + [total]
    if len(visuals) != len(anchors): raise RuntimeError("Visual/anchor count mismatch")
    if len(set(map(str, visuals))) != len(visuals): raise RuntimeError("Repeated visual in Short")
    segdir = short_root / "04_EDIT" / "segments"; segdir.mkdir(parents=True, exist_ok=True)
    visual_fingerprints = [(str(p), hashlib.sha256(p.read_bytes()).hexdigest()) for p in visuals]
    signature = hashlib.sha256(
        voice.read_bytes() + json.dumps({"anchors": anchors, "visuals": visual_fingerprints}, sort_keys=True).encode()
    ).hexdigest()
    signature_path = segdir / ".render_signature"
    force = not signature_path.is_file() or signature_path.read_text(encoding="utf-8").strip() != signature
    files=[]; shots=[]
    for i,(img,a,b) in enumerate(zip(visuals,times,times[1:])):
        sec=max(0.10,b-a)
        dst=segdir/f"{i:02d}.mp4"
        if force or not dst.is_file() or abs(duration(dst)-sec) > 0.12:
            if "SHORT_SPECIFIC" in str(img):
                vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p"
            else:
                vf = f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},fps={FPS*SUB},{camera(i,sec)}"
            run(["ffmpeg","-y","-hide_banner","-loglevel","error","-loop","1","-t",f"{sec:.4f}","-i",str(img),
                 "-vf",vf, "-an","-c:v","libx264","-preset","veryfast","-crf","17","-r",str(FPS),str(dst)])
        files.append(dst); shots.append({"index":i+1,"start":round(a,3),"end":round(b,3),"duration":round(sec,3),"anchor":anchors[i],"visual":str(img)})
    signature_path.write_text(signature+"\n", encoding="utf-8")
    concat=segdir/"concat.txt"; concat.write_text("\n".join(f"file '{x.as_posix()}'" for x in files)+"\n",encoding="utf-8")
    silent=short_root/"04_EDIT"/"video_only.mp4"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),
         "-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-r",str(FPS),"-an",str(silent)])
    ass=write_subtitles(short_root,stem,text,starts,ends)
    bed=short_root/"04_EDIT"/"audio_bed.wav"; make_bed(total,bed)
    outdir=short_root/"05_OUTPUT"; final=outdir/f"{stem}_FINAL_9x16.mp4"
    ass_filter=str(ass).replace("\\","/").replace(":","\\:").replace("'","\\'")
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(silent),"-i",str(voice),"-i",str(bed),
         "-filter_complex",f"[0:v]subtitles='{ass_filter}'[v];[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[vo][key];"
         f"[2:a][key]sidechaincompress=threshold=.018:ratio=7:attack=12:release=280[duck];[vo][duck]amix=2:normalize=0:duration=first,"
         f"atrim=0:{total:.4f},aresample=192000,alimiter=limit=.89,aresample=48000,loudnorm=I=-14:TP=-1.2:LRA=9[a]",
         "-map","[v]","-map","[a]","-c:v","libx264","-preset","medium","-crf","17","-profile:v","high","-level","4.1",
         "-pix_fmt","yuv420p","-r",str(FPS),"-c:a","aac","-b:a","256k","-ar","48000","-ac","2","-t",f"{total:.4f}","-movflags","+faststart",str(final)])
    report={"title":title,"full_episode":link,"file":str(final.resolve()),"duration":round(duration(final),3),"shots":len(shots),
            "unique_visuals":len(set(map(str,visuals))),"max_shot":max(x["duration"] for x in shots),"shots_detail":shots}
    (outdir/"EDIT_REPORT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return final


def write_metadata(short_root: Path, title: str, description: str, tags: list[str], pinned: str):
    text = f"# Upload package\n\nTITLE\n{title}\n\nDESCRIPTION\n{description}\n\nTAGS\n{', '.join(tags)}\n\nPINNED COMMENT\n{pinned}\n\n"
    (short_root/"05_OUTPUT"/"YOUTUBE_METADATA.md").write_text(text,encoding="utf-8")


def qa_short(short_root: Path, stem: str):
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from qa_smooth_still_motion import analyse
    final = short_root / "05_OUTPUT" / f"{stem}_FINAL_9x16.mp4"
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels",
                            "-of", "json", str(final)], True))
    run(["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"])
    loud = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final),
                "-filter_complex", "ebur128=peak=true", "-f", "null", "-"], True)
    integrated = [float(x) for x in re.findall(r"I:\s*(-?\d+(?:\.\d+)?)\s+LUFS", loud)][-1]
    true_peak = [float(x) for x in re.findall(r"Peak:\s*(-?\d+(?:\.\d+)?)\s+dBFS", loud, re.I)]
    if not true_peak:
        true_peak = [float(x) for x in re.findall(r"TPK:\s*(-?\d+(?:\.\d+)?)", loud)]
    edit = json.loads((short_root/"05_OUTPUT"/"EDIT_REPORT.json").read_text(encoding="utf-8"))
    motion = []
    for p in sorted((short_root/"04_EDIT"/"segments").glob("[0-9][0-9].mp4")):
        result = analyse(p)
        shot_index = int(p.stem)
        expected_static = "SHORT_SPECIFIC" in edit["shots_detail"][shot_index]["visual"]
        if expected_static and result.get("central_low_motion_ratio", 0) >= 0.98:
            result["status"] = "PASS"
            result["mode"] = "intentional_static_reading_card"
        else:
            result["mode"] = "eased_moving_still"
        motion.append({"segment": p.name, **result})
    streams = probe["streams"]
    video = next(x for x in streams if x.get("width"))
    audio = next(x for x in streams if x.get("sample_rate"))
    checks = {
        "full_decode": "PASS",
        "vertical_1080x1920": "PASS" if (video["width"], video["height"]) == (1080,1920) else "FAIL",
        "frame_rate_30": "PASS" if video["r_frame_rate"] == "30/1" else "FAIL",
        "audio_48k_stereo": "PASS" if (audio["sample_rate"], audio["channels"]) == ("48000",2) else "FAIL",
        "unique_visuals": "PASS" if edit["shots"] == edit["unique_visuals"] else "FAIL",
        "shot_duration": "PASS" if edit["max_shot"] < 8.0 else "REVIEW",
        "integrated_loudness": "PASS" if -15.0 <= integrated <= -13.0 else "REVIEW",
        "motion_cadence": "PASS" if all(x["status"] == "PASS" for x in motion) else "REVIEW",
    }
    report = {"status": "PASS" if all(v == "PASS" for v in checks.values()) else "REVIEW",
              "checks": checks, "integrated_lufs": integrated,
              "true_peak_dbtp": true_peak[-1] if true_peak else None,
              "duration": float(probe["format"]["duration"]), "edit": edit, "motion": motion}
    (short_root/"05_OUTPUT"/"FINAL_QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(stem, report["status"], checks, "LUFS", integrated, "TP", report["true_peak_dbtp"])


def build_all():
    ka=kz_assets(); ga=gw_assets()
    kg=KZ/"03_ASSETS"/"GENERATED"; gg=GW/"03_ASSETS"/"GENERATED"
    kz_visuals=[kg/"KZ_S01_G01_ROTATING_CHAMBER.png",kg/"KZ_S01_G02_EMPTY_CHAIR.png",ka["kz_portrait"],ka["kz_timeline"],ka["kz_pair"],ka["kz_patent"],ka["kz_drawings"],kg/"KZ_S01_G04_MOTORIZED_PLATFORM.png",kg/"KZ_S01_G05_MOON_STORM.png",ka["kz_boundary"],ka["kz_open"],kg/"KZ_S01_G03_RESEARCHERS.png",kg/"KZ_S01_G06_PERCEPTION_OR_TIME.png",ka["kz_episode"],ka["kz_follow"]]
    kz_anchors=["Everyone calls","But Kozyrev never","Nikolai Kozyrev died","The patent for this","by two other researchers","It describes curved","A clockwise or counterclockwise","Even a motorized","And it links","The design is documented","What happened inside","And that makes the legend","So what would you test","The full evidence trail","Follow NOESIS"]
    gw_visuals=[ga["gw_file"],gg/"GW_S01_G01_THREE_OBSERVERS.png",gg/"GW_S01_G02_HIDDEN_TARGET.png",gg/"GW_S01_G03_PRESENT.png",gg/"GW_S01_G04_PAST.png",gg/"GW_S01_G05_FUTURE.png",ga["gw_compare"],ga["gw_fiction"],ga["gw_recommendation"],ga["gw_archive"],gg/"GW_S01_G06_ARMY_ANALYST.png",ga["gw_plan"],gg/"GW_S01_G07_NO_RESULT.png",ga["gw_choice"],ga["gw_comment"],ga["gw_episode"],ga["gw_follow"]]
    gw_anchors=["The famous","Three observers","One hidden target","One sees it now","One searches the immediate past","One searches the immediate future","Their descriptions","It sounds like science fiction","It is Recommendation H","prepared for the United States Army","But here is the part","The document lays out","The outcome remains","Would you authorize","Comment AUTHORIZE","The full Gateway investigation","Follow NOESIS"]
    kf=render(KZ,"EP01_EN_SHORT_S01",kz_anchors,kz_visuals,"Kozyrev Never Built the 'Kozyrev Mirror'","https://youtu.be/sNaGasLTP2U")
    gf=render(GW,"EP02_EN_SHORT_S01",gw_anchors,gw_visuals,"The CIA Gateway Report's Strangest Experiment","https://youtu.be/TRArTIGfva4")
    write_metadata(KZ,"Kozyrev Never Built the ‘Kozyrev Mirror’","Everyone calls it a Kozyrev Mirror. The original patent tells a stranger story.\n\nWatch the full evidence trail: https://youtu.be/sNaGasLTP2U\n\nWhat would you test inside it — altered perception or information from another time?\n\n#KozyrevMirror #Mystery #NOESIS #Shorts",["Kozyrev mirror","Nikolai Kozyrev","Russian patent","time travel mystery","NOESIS"],"Kozyrev died 13 years before the patent was filed. What would you test inside the chamber — PERCEPTION or TIME? Full episode: https://youtu.be/sNaGasLTP2U")
    write_metadata(GW,"The CIA Gateway Report’s Strangest Experiment","Three observers. One hidden target. Present, past, and future. The famous Gateway file lays out the test — and leaves its outcome open.\n\nWatch the full investigation: https://youtu.be/TRArTIGfva4\n\nWould you AUTHORIZE it or STOP the program?\n\n#GatewayProcess #CIAFiles #Mystery #NOESIS #Shorts",["Gateway Process","CIA Gateway Report","Recommendation H","remote viewing","NOESIS"],"One target. Three observers. Three different times. Would you AUTHORIZE the test or STOP the program? Full episode: https://youtu.be/TRArTIGfva4")
    print(kf); print(gf)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("stage",choices=["assets","align","render","qa","all"]); args=ap.parse_args()
    if args.stage in ("assets","all"): kz_assets(); gw_assets(); print("Short-specific assets built")
    if args.stage in ("align","all"):
        align(KZ,"EP01_EN_SHORT_S01"); align(GW,"EP02_EN_SHORT_S01")
    if args.stage in ("render","all"): build_all()
    if args.stage in ("qa","all"):
        qa_short(KZ,"EP01_EN_SHORT_S01"); qa_short(GW,"EP02_EN_SHORT_S01")


if __name__ == "__main__": main()
