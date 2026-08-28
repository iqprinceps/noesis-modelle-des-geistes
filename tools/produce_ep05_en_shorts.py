#!/usr/bin/env python3
"""Produce the two independent EP05 English 9:16 Shorts.

The script uses the selected ElevenLabs voice and forced alignment as timing
authority, builds source-faithful vertical cards, renders portrait stills with
the shared eased/sub-frame motion pipeline, synthesizes original music and SFX,
burns dynamic captions, and exports upload-ready masters without uploading.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import wave
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from produce_noesis_en_shorts import alignment_arrays, anchor_time
from smooth_still_motion import eased_zoompan_filter


ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "07_ENGLISH_PRODUCTION" / "EP05_SLEEP_PARALYSIS_01_SHORTS"
CANON = (
    Path.home() / ".codex" / "worktrees" / "1552" / "Youtube Modelle des Geistes"
    / "07_ENGLISH_PRODUCTION" / "EP05_SLEEP_PARALYSIS_01"
)
W, H, FPS, SR = 1080, 1920, 30, 48000
INK = (240, 236, 224)
MUTED = (165, 174, 177)
AMBER = (230, 169, 67)
CYAN = (96, 194, 211)
BG = (8, 13, 18)


def run(args: list[str], capture: bool = False) -> str:
    proc = subprocess.run(args, text=True, capture_output=capture)
    if proc.returncode:
        raise RuntimeError((proc.stderr or proc.stdout or "command failed")[-8000:])
    return (proc.stdout or "") + (proc.stderr or "")


def media_duration(path: Path) -> float:
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], True).strip())


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


def fb(size: int) -> ImageFont.FreeTypeFont:
    return font("arialbd.ttf", size)


def fr(size: int) -> ImageFont.FreeTypeFont:
    return font("arial.ttf", size)


def base(top=(7, 12, 18), bottom=(18, 23, 27)) -> Image.Image:
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / max(1, H - 1)
        arr[y, :, :] = [round(top[i] * (1-t) + bottom[i] * t) for i in range(3)]
    return Image.fromarray(arr, "RGB")


def cover(src: Path, size=(W, H), focus=(0.5, 0.5)) -> Image.Image:
    im = Image.open(src).convert("RGB")
    sw, sh = im.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    im = im.resize((round(sw*scale), round(sh*scale)), Image.Resampling.LANCZOS)
    x = max(0, min(im.width-tw, round((im.width-tw)*focus[0])))
    y = max(0, min(im.height-th, round((im.height-th)*focus[1])))
    return im.crop((x, y, x+tw, y+th))


def contain(src: Path, size: tuple[int, int], bgcolor=(236, 232, 219)) -> Image.Image:
    im = Image.open(src).convert("RGB")
    im.thumbnail(size, Image.Resampling.LANCZOS)
    out = Image.new("RGB", size, bgcolor)
    out.paste(im, ((size[0]-im.width)//2, (size[1]-im.height)//2))
    return out


def glow(im: Image.Image, xy: tuple[int, int], color: tuple[int, int, int], radius=320, alpha=65):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = xy
    d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(max(20, radius//2)))
    im.paste(layer, (0, 0), layer)


def rounded_paste(dst: Image.Image, src: Image.Image, xy: tuple[int, int], radius=30,
                  outline=(66, 74, 77), width=3):
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, src.width-1, src.height-1), radius, fill=255)
    dst.paste(src, xy, mask)
    ImageDraw.Draw(dst).rounded_rectangle(
        (xy[0], xy[1], xy[0]+src.width, xy[1]+src.height), radius,
        outline=outline, width=width,
    )


def centered(d: ImageDraw.ImageDraw, text: str, y: int, f: ImageFont.FreeTypeFont,
             fill=INK):
    box = d.textbbox((0, 0), text, font=f)
    d.text(((W-(box[2]-box[0]))/2, y), text, font=f, fill=fill)


def label(d: ImageDraw.ImageDraw, text: str, y=80, color=AMBER):
    d.text((72, y), text.upper(), font=fb(30), fill=color)
    d.line((72, y+50, 360, y+50), fill=color, width=4)


def shade(im: Image.Image, top=170, bottom=220):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle((0, 0, W, 330), fill=(4, 8, 12, top))
    d.rectangle((0, 1280, W, H), fill=(4, 8, 12, bottom))
    im.paste(lay, (0, 0), lay)


def save(im: Image.Image, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, compress_level=3)


def p(*parts: str) -> Path:
    return CANON.joinpath(*parts)


def build_a_assets() -> dict[str, Path]:
    root = PROD / "S01_HUFFORD_OLD_HAG" / "03_ASSETS"
    out = root / "VERTICAL"
    gen = root / "GENERATED"
    a: dict[str, Path] = {
        "A01": gen / "A01_DOOR_EYE.png",
        "A03": gen / "A03_FAILED_HAND.png",
        "A04": gen / "A04_MATTRESS.png",
        "A08": gen / "A08_NAME_BEFORE.png",
        "A11": gen / "A11_INTENTION.png",
    }

    src = p("03_VISUALS", "GENERATED_STILLS", "EP05_GEN_HOOK_FOOTSTEPS_FLOOR.png")
    im = cover(src, focus=(0.57, 0.78)); shade(im, 80, 80); d = ImageDraw.Draw(im)
    label(d, "Two steps cross the room", 90, CYAN)
    a["A02"] = out / "A02_FOOTSTEPS.png"; save(im, a["A02"])

    photo = p("02_SOURCES", "ORIGINALS", "EP05_ORIG_HUFFORD_OFFICIAL_PHOTO.jpg")
    im = base((13, 18, 20), (29, 27, 22)); glow(im, (270, 700), AMBER)
    pic = Image.open(photo).convert("RGB").resize((780, 780), Image.Resampling.LANCZOS)
    rounded_paste(im, pic, (150, 250), 34, AMBER, 4); d = ImageDraw.Draw(im)
    label(d, "The encounter came first", 90)
    d.rounded_rectangle((80, 1080, 1000, 1390), 32, fill=(12, 18, 21), outline=(79, 82, 75), width=3)
    d.text((118, 1135), "DAVID HUFFORD", font=fb(76), fill=INK)
    d.text((120, 1245), "FOLKLORIST", font=fb(35), fill=AMBER)
    d.text((120, 1320), "Hufford with Mary Ann Bucklin", font=fr(28), fill=MUTED)
    a["A05"] = out / "A05_HUFFORD_IDENTITY.png"; save(im, a["A05"])

    src = p("02_SOURCES", "ORIGINALS", "EP05_ORIG_FOGO_TILTING_HARBOUR.jpg")
    im = cover(src, focus=(0.47, 0.43)); im = ImageEnhance.Contrast(im).enhance(1.05); shade(im, 130, 200)
    d = ImageDraw.Draw(im); label(d, "Years later • Newfoundland", 90, AMBER)
    d.text((70, 1240), "FOGO ISLAND", font=fb(92), fill=INK)
    d.text((74, 1355), "A LIVING OLD HAG TRADITION", font=fb(34), fill=AMBER)
    a["A06"] = out / "A06_FOGO_COAST.png"; save(im, a["A06"])

    src = p("03_VISUALS", "REUSED_GERMAN_SERIES", "STILLS", "IMG061_FOGO_FIELDWORK_INTERVIEW_RECON.png")
    im = cover(src, focus=(0.52, 0.50)); shade(im, 130, 170); d = ImageDraw.Draw(im)
    label(d, "Strangers described the sequence", 88, CYAN)
    d.text((76, 1320), "DOOR  •  STEPS  •  BODY  •  WEIGHT", font=fb(34), fill=INK)
    a["A07"] = out / "A07_ORAL_HISTORY.png"; save(im, a["A07"])

    fus = p("02_SOURCES", "ORIGINALS", "EP05_ORIG_FUSELI_NIGHTMARE.jpg")
    abi = p("02_SOURCES", "ORIGINALS", "EP05_ORIG_NACHTMAHR_ABILDGAARD.jpg")
    im = base((23, 16, 11), (10, 14, 17)); glow(im, (540, 690), AMBER); d = ImageDraw.Draw(im)
    label(d, "The name: Old Hag", 80)
    left = cover(fus, (450, 720), (0.54, 0.45)); right = cover(abi, (450, 720), (0.52, 0.42))
    rounded_paste(im, left, (70, 300), 26, (109, 83, 47), 3)
    rounded_paste(im, right, (560, 300), 26, (109, 83, 47), 3)
    d.text((88, 1050), "FUSELI  •  1781", font=fb(28), fill=MUTED)
    d.text((576, 1050), "ABILDGAARD  •  c.1800", font=fb(28), fill=MUTED)
    centered(d, "HISTORICAL NIGHT-PRESSURE", 1190, fb(45), INK)
    centered(d, "ICONOGRAPHY", 1260, fb(58), AMBER)
    a["A09"] = out / "A09_OLD_HAG_REVEAL.png"; save(im, a["A09"])

    rem = p("02_SOURCES", "ORIGINALS", "EP05_ORIG_REM_PSG.png")
    eeg = p("02_SOURCES", "ORIGINALS", "EP05_ORIG_EEG_CAP.jpg")
    im = base((8, 19, 23), (16, 23, 25)); glow(im, (760, 740), CYAN); d = ImageDraw.Draw(im)
    label(d, "REM physiology", 80, CYAN)
    graph = contain(rem, (900, 560), (239, 237, 227)); rounded_paste(im, graph, (90, 260), 26, CYAN, 3)
    body = cover(eeg, (390, 620), (0.48, 0.45)); rounded_paste(im, body, (600, 900), 26, (82, 103, 106), 3)
    d.text((88, 940), "AWARENESS", font=fb(54), fill=INK)
    d.text((88, 1010), "RETURNS", font=fb(54), fill=CYAN)
    d.line((90, 1120, 520, 1120), fill=CYAN, width=5)
    d.text((88, 1170), "MUSCLES", font=fb(54), fill=INK)
    d.text((88, 1240), "STAY QUIET", font=fb(54), fill=AMBER)
    a["A10"] = out / "A10_REM_ATONIA.png"; save(im, a["A10"])

    src = p("03_VISUALS", "GENERATED_STILLS", "EP05_GEN_PRESENCE_DIRECTED_PROXIMITY.png")
    im = cover(src, focus=(0.58, 0.48)); shade(im, 105, 120); d = ImageDraw.Draw(im)
    label(d, "Why the footsteps?", 86, CYAN)
    a["A11B"] = out / "A11B_FOOTSTEPS_QUESTION.png"; save(im, a["A11B"])

    src = p("03_VISUALS", "GENERATED_STILLS", "EP05_GEN_CORR_FOGO_OLD_HAG.png")
    im = cover(src, focus=(0.50, 0.46)); shade(im, 115, 120); d = ImageDraw.Draw(im)
    label(d, "Why the weight?", 86, AMBER)
    a["A11C"] = out / "A11C_WEIGHT_QUESTION.png"; save(im, a["A11C"])

    src = p("03_VISUALS", "EDITED_COMPOSITES", "EP05_EDIT_HUFFORD_HOSTILE_INTENTION.png")
    im = cover(src, focus=(0.48, 0.47)); shade(im, 110, 135); d = ImageDraw.Draw(im)
    label(d, "Why the certainty of intention?", 86, AMBER)
    a["A11D"] = out / "A11D_INTENTION_QUESTION.png"; save(im, a["A11D"])

    src = p("03_VISUALS", "REUSED_GERMAN_SERIES", "STILLS", "IMG024_NIGHTMARE_PRINT_WORKSHOP.png")
    im = cover(src, focus=(0.56, 0.49)); shade(im, 120, 205); d = ImageDraw.Draw(im)
    label(d, "Does folklore shape the encounter?", 85, AMBER)
    d.text((72, 1180), "STORY", font=fb(94), fill=INK)
    d.text((72, 1295), "GIVES IT A FACE", font=fb(53), fill=AMBER)
    a["A12"] = out / "A12_FOLKLORE_MASK.png"; save(im, a["A12"])

    im = base((14, 19, 20), (33, 25, 18)); glow(im, (540, 850), AMBER); d = ImageDraw.Draw(im)
    label(d, "Or does experience shape folklore?", 86, CYAN)
    nodes = [(540, 420, "BODY"), (270, 820, "ENCOUNTER"), (540, 1220, "STORY"), (810, 820, "MEMORY")]
    for x, y, txt in nodes:
        d.ellipse((x-135, y-105, x+135, y+105), fill=(19, 28, 31), outline=CYAN if txt in ("BODY","ENCOUNTER") else AMBER, width=5)
        box=d.textbbox((0,0),txt,font=fb(27)); d.text((x-(box[2]-box[0])/2,y-17),txt,font=fb(27),fill=INK)
    for (x1,y1,_),(x2,y2,_) in zip(nodes, nodes[1:]+nodes[:1]):
        d.line((x1,y1,x2,y2), fill=(98, 104, 96), width=6)
    centered(d, "A RECURRING SHAPE", 205, fb(44), INK)
    centered(d, "CAN TRAVEL BOTH WAYS", 265, fb(38), AMBER)
    a["A13"] = out / "A13_ENCOUNTER_LOOP.png"; save(im, a["A13"])

    book = p("02_SOURCES", "ORIGINALS", "EP05_ORIG_HUFFORD_BOOK_COVER.jpg")
    im = base((15, 18, 17), (24, 21, 17)); glow(im, (360, 760), AMBER); d = ImageDraw.Draw(im)
    label(d, "The full evidence trail", 90)
    bk = Image.open(book).convert("RGB").resize((510, 770), Image.Resampling.LANCZOS)
    rounded_paste(im, bk, (285, 300), 22, AMBER, 4)
    centered(d, "SLEEP PARALYSIS", 1170, fb(64), INK)
    centered(d, "WHY YOU FEEL SOMEONE", 1260, fb(46), INK)
    centered(d, "IN THE ROOM", 1330, fb(58), AMBER)
    a["A14"] = out / "A14_LONGFORM_BRIDGE.png"; save(im, a["A14"])

    im = base((8, 16, 20), (30, 23, 17)); d = ImageDraw.Draw(im); glow(im, (270, 820), CYAN); glow(im, (810, 820), AMBER)
    label(d, "Which came first?", 92)
    d.rounded_rectangle((70, 350, 510, 1360), 34, fill=(13, 24, 29), outline=CYAN, width=5)
    d.rounded_rectangle((570, 350, 1010, 1360), 34, fill=(30, 23, 16), outline=AMBER, width=5)
    centered(d, "LEGEND", 520, fb(70), CYAN); centered(d, "OR", 770, fb(44), MUTED); centered(d, "ENCOUNTER", 1040, fb(61), AMBER)
    a["A15"] = out / "A15_LEGEND_OR_ENCOUNTER.png"; save(im, a["A15"])

    return a


def build_b_assets() -> dict[str, Path]:
    root = PROD / "S02_TAKEUCHI_LAB" / "03_ASSETS"
    out = root / "VERTICAL"
    gen = root / "GENERATED"
    b: dict[str, Path] = {
        "B01": gen / "B01_INTERRUPTION_ACTION.png",
        "B04": gen / "B04_SLEEP_SENSORS.png",
        "B05": gen / "B05_SELECTED_AWAKENING.png",
        "B09": gen / "B09_AWARE_IMMOBILE.png",
        "B10": gen / "B10_AV_DISTURBANCE.png",
        "B12": gen / "B12_MEASURABLE_THRESHOLD.png",
    }

    im = base((9, 22, 27), (19, 28, 30)); glow(im, (540, 760), CYAN); d = ImageDraw.Draw(im)
    label(d, "Healthy participants", 88, CYAN)
    for i in range(16):
        row, col = divmod(i, 4); x=165+col*250; y=330+row*270
        d.ellipse((x-42,y-70,x+42,y+14), fill=(197,218,219), outline=CYAN, width=3)
        d.rounded_rectangle((x-62,y+25,x+62,y+145), 28, fill=(44,72,77), outline=(117,171,178), width=3)
    centered(d, "16 PEOPLE", 1330, fb(86), INK)
    b["B02"] = out / "B02_SIXTEEN.png"; save(im, b["B02"])

    im = base((8, 21, 27), (17, 27, 30)); glow(im, (540, 820), CYAN); d = ImageDraw.Draw(im)
    label(d, "Six isolated episodes", 84, CYAN)
    for i in range(6):
        row, col = divmod(i, 2); x=310+col*460; y=430+row*380
        d.rounded_rectangle((x-170,y-125,x+170,y+125),34,fill=(15,29,34),outline=(60,81,86),width=3)
        d.text((x-31,y-53),str(i+1),font=fb(78),fill=MUTED)
    centered(d, "0 / 6", 1580, fb(66), MUTED)
    b["B03"] = out / "B03_SIX_EPISODES_BASE.png"; save(im, b["B03"])

    im = base((10, 23, 27), (21, 28, 29)); glow(im, (540, 760), CYAN); d=ImageDraw.Draw(im)
    label(d, "Awake interval", 90, CYAN)
    d.ellipse((190, 330, 890, 1030), fill=(235,232,219), outline=CYAN, width=8)
    d.ellipse((270, 410, 810, 950), outline=(71,91,95), width=5)
    d.line((540,680,540,445), fill=(21,29,31), width=24)
    d.line((540,680,760,680), fill=AMBER, width=24)
    d.ellipse((510,650,570,710), fill=(21,29,31))
    centered(d, "60 MINUTES", 1120, fb(86), INK)
    centered(d, "AWAKE", 1230, fb(86), AMBER)
    b["B06"] = out / "B06_SIXTY_MINUTES.png"; save(im, b["B06"])

    im = base((8, 20, 25), (18, 27, 29)); glow(im, (710, 760), CYAN); d = ImageDraw.Draw(im)
    label(d, "Return to bed", 90, CYAN)
    d.rounded_rectangle((90, 350, 840, 1080), 38, fill=(18, 31, 35), outline=(78, 135, 144), width=5)
    d.rounded_rectangle((145, 635, 785, 980), 30, fill=(226, 224, 211), outline=(121, 157, 160), width=4)
    d.ellipse((210, 675, 340, 805), fill=(190, 205, 204), outline=CYAN, width=4)
    d.rounded_rectangle((315, 710, 700, 920), 48, fill=(112, 145, 148), outline=(204, 220, 219), width=4)
    d.rounded_rectangle((865, 470, 1010, 930), 24, fill=(11, 25, 30), outline=CYAN, width=4)
    for row in range(5):
        y=535+row*70
        d.line((890,y,930,y-18,970,y+10,995,y-8), fill=CYAN if row<3 else AMBER, width=4)
    for offset in (0, 18, 36):
        d.line((330,740+offset,850,575+offset), fill=(110, 151, 156), width=3)
    d.text((96, 1190), "SLEEP AGAIN", font=fb(76), fill=INK)
    d.text((96, 1290), "PSG CONTINUES", font=fb(48), fill=CYAN)
    b["B07"] = out / "B07_RETURN_TO_BED.png"; save(im, b["B07"])

    im = base((8, 20, 25), (18, 27, 29)); glow(im, (540, 820), CYAN); d=ImageDraw.Draw(im)
    label(d, "Four experimental nights", 86, CYAN)
    for i in range(4):
        y=350+i*225
        d.rounded_rectangle((100,y,980,y+150), 28, fill=(17,31,36), outline=(72,126,136), width=3)
        d.text((135,y+43),f"NIGHT {i+1}",font=fb(36),fill=INK)
        d.line((410,y+75,875,y+75),fill=CYAN,width=5)
        for x in (500,640,780): d.ellipse((x-13,y+62,x+13,y+88),fill=AMBER)
    centered(d, "EPISODES APPEARED UNDER", 1180, fb(41), INK)
    centered(d, "THE INTERRUPTED-SLEEP PROTOCOL", 1250, fb(38), CYAN)
    centered(d, "NOT EVERY INTERRUPTION • NOT EVERY PERSON", 1350, fb(28), MUTED)
    b["B08"] = out / "B08_PROTOCOL_BOUNDARY.png"; save(im, b["B08"])

    card = p("02_SOURCES", "CAPTURES", "SRC_TAKEUCHI_PUBMED_1992_CARD.png")
    im = base((7,18,23),(18,27,29)); glow(im,(740,760),CYAN); d=ImageDraw.Draw(im)
    label(d,"The recorded contradiction",82,CYAN)
    src = Image.open(card).convert("RGB"); src.thumbnail((940,620),Image.Resampling.LANCZOS)
    rounded_paste(im,src,(70,230),24,CYAN,3)
    d.rounded_rectangle((75,930,1005,1390),30,fill=(14,26,31),outline=(79,115,120),width=3)
    d.text((120,995),"WAKING AWARENESS",font=fb(52),fill=INK)
    d.text((120,1085),"WHILE",font=fb(30),fill=MUTED)
    d.text((120,1150),"MUSCLE ATONIA",font=fb(60),fill=CYAN)
    d.text((120,1245),"PERSISTED",font=fb(60),fill=AMBER)
    d.text((120,1330),"Takeuchi et al. • Sleep • 1992",font=fr(28),fill=MUTED)
    b["B11"] = out / "B11_AWARENESS_ATONIA.png"; save(im, b["B11"])

    thumb = p("07_THUMBNAILS", "EP05_EN_THUMB_C_LAB_CONTRADICTION.jpg")
    im = base((8,19,24),(20,28,29)); glow(im,(540,700),CYAN); d=ImageDraw.Draw(im)
    label(d,"The full experiment",90,CYAN)
    src = cover(thumb,(940,720),(0.50,0.50))
    rounded_paste(im,src,(70,250),26,CYAN,3)
    centered(d,"SIX EPISODES",1080,fb(80),INK)
    centered(d,"ONE MEASURABLE CONTRADICTION",1190,fb(39),CYAN)
    b["B13"] = out / "B13_LONGFORM_BRIDGE.png"; save(im, b["B13"])

    im=base((7,18,23),(26,23,20)); glow(im,(250,820),CYAN); glow(im,(820,820),AMBER); d=ImageDraw.Draw(im)
    label(d,"What unsettles you most?",90,AMBER)
    opts=[("BODY",CYAN),("BRAIN",INK),("PRESENCE",AMBER)]
    for i,(txt,col) in enumerate(opts):
        y=390+i*330; d.rounded_rectangle((95,y,985,y+245),36,fill=(15,27,31),outline=col,width=5)
        centered(d,txt,y+65,fb(84),col)
    b["B14"] = out / "B14_VIEWER_CHOICE.png"; save(im,b["B14"])
    return b


def ass_time(t: float) -> str:
    cs=round(t*100); h,cs=divmod(cs,360000); m,cs=divmod(cs,6000); s,cs=divmod(cs,100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def tc(t: float) -> str:
    ms=round(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def caption_chunks(text: str, starts: list[float], ends: list[float], total: float):
    words=[(m.group(),m.start(),m.end()) for m in re.finditer(r"\S+",text)]
    chunks=[]; i=0
    while i<len(words):
        j=i
        while j<len(words) and j-i<4:
            j+=1
            phrase=" ".join(x[0] for x in words[i:j])
            if re.search(r"[.!?—:]$",words[j-1][0]) or len(phrase)>28: break
        phrase=" ".join(x[0] for x in words[i:j])
        a=max(0.0,float(starts[words[i][1]])-0.035)
        b=min(total,float(ends[words[j-1][2]-1])+0.07)
        chunks.append((a,b,phrase)); i=j
    # Padding must never create two simultaneous subtitle events. Keep the
    # word-level response, but close each cue just before the next begins.
    fixed=[]
    for index,(a,b,phrase) in enumerate(chunks):
        if index+1 < len(chunks):
            b=min(b,max(a+0.040,chunks[index+1][0]-0.001))
        fixed.append((a,b,phrase))
    return fixed


def write_captions(short_root: Path, stem: str, total: float) -> Path:
    data=json.loads((short_root/"02_VOICE"/"alignment"/f"{stem}_alignment.json").read_text(encoding="utf-8"))
    text,starts,ends=alignment_arrays(data); chunks=caption_chunks(text,starts,ends,total)
    out=short_root/"05_OUTPUT"; out.mkdir(parents=True,exist_ok=True)
    srt=[]
    for i,(a,b,phrase) in enumerate(chunks,1): srt += [str(i),f"{tc(a)} --> {tc(b)}",phrase,""]
    (out/f"{stem}.srt").write_text("\n".join(srt),encoding="utf-8")
    ass=[
        "[Script Info]","ScriptType: v4.00+",f"PlayResX: {W}",f"PlayResY: {H}","WrapStyle: 0","ScaledBorderAndShadow: yes","",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Arial,67,&H00F1EEE5,&H000000FF,&H000B1014,&HC40B1014,-1,0,0,0,100,100,0,0,3,4,0,2,135,135,410,1","",
        "[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for a,b,phrase in chunks:
        safe=phrase.replace("{","(").replace("}",")")
        ass.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Default,,0,0,0,,{safe}")
    path=out/f"{stem}.ass"; path.write_text("\n".join(ass)+"\n",encoding="utf-8-sig")
    return path


def synth_stems(short_root: Path, kind: str, total: float, count_times: list[float] | None=None):
    audio=short_root/"04_AUDIO"; audio.mkdir(parents=True,exist_ok=True)
    n=round(total*SR); t=np.arange(n,dtype=np.float64)/SR
    rng=np.random.default_rng(905 if kind=="A" else 906)
    if kind=="A":
        music=(0.10*np.sin(2*np.pi*46*t)+0.045*np.sin(2*np.pi*92*t+0.4)+0.018*np.sin(2*np.pi*232*t))
        music*=0.72+0.28*np.sin(2*np.pi*0.035*t)
    else:
        music=(0.07*np.sin(2*np.pi*55*t)+0.035*np.sin(2*np.pi*110*t)+0.014*np.sin(2*np.pi*440*t))
        music*=0.80+0.20*np.sin(2*np.pi*0.055*t)
    noise=rng.normal(0,1,n); noise=np.cumsum(noise); noise/=max(1e-9,np.max(np.abs(noise)))
    music += 0.018*noise
    music *= np.minimum(1,t/0.55)*np.minimum(1,(total-t)/0.9)
    sfx=np.zeros(n,dtype=np.float64)

    def pulse(at: float, freq: float, dur: float, amp: float, noisy=False):
        start=max(0,round(at*SR)); length=min(n-start,round(dur*SR))
        if length<=0:return
        x=np.arange(length)/SR; env=np.exp(-x*7.0)*np.minimum(1,x/0.008)
        sig=np.sin(2*np.pi*freq*x)*env
        if noisy: sig += rng.normal(0,0.45,length)*env
        sfx[start:start+length] += amp*sig

    if kind=="A":
        pulse(0.18,180,0.22,0.30,True); pulse(1.45,82,0.30,0.34,True); pulse(2.30,76,0.32,0.31,True)
        pulse(3.25,116,0.20,0.17); pulse(5.78,58,0.70,0.25,True); pulse(17.66,104,0.80,0.18)
        pulse(19.12,760,0.20,0.10); pulse(38.50,310,0.35,0.10,True)
    else:
        pulse(0.12,640,0.18,0.12); pulse(1.88,480,0.15,0.10)
        for i,at in enumerate(count_times or []): pulse(at,620+i*45,0.24,0.18)
        pulse(11.50,820,0.18,0.12); pulse(13.36,1260,0.10,0.08); pulse(14.64,92,0.35,0.15,True)
        pulse(33.42,720,0.35,0.12); pulse(38.64,155,0.85,0.11)

    def write(path: Path, mono: np.ndarray):
        stereo=np.column_stack((mono,mono)); pcm=np.clip(stereo,-0.98,0.98)
        with wave.open(str(path),"wb") as wv:
            wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
            wv.writeframes((pcm*32767).astype("<i2").tobytes())
    write(audio/"MUSIC_BED.wav",music); write(audio/"SFX.wav",sfx)


def render_six_signal_clip(dst: Path, duration: float, absolute_start: float, event_times: list[float]):
    dst.parent.mkdir(parents=True,exist_ok=True); tmp=dst.with_suffix(".mp4v.mp4")
    writer=cv2.VideoWriter(str(tmp),cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
    frames=max(2,round(duration*FPS))
    for fi in range(frames):
        now=absolute_start+fi/FPS
        im=base((8,21,27),(17,27,30)); glow(im,(540,820),CYAN); d=ImageDraw.Draw(im)
        label(d,"Six isolated episodes",84,CYAN)
        active=sum(now>=x for x in event_times)
        for i in range(6):
            row,col=divmod(i,2); x=310+col*460; y=430+row*380
            on=i<active
            colr=AMBER if on else (60,81,86)
            d.rounded_rectangle((x-170,y-125,x+170,y+125),34,fill=(15,29,34),outline=colr,width=7 if on else 3)
            d.text((x-31,y-53),str(i+1),font=fb(78),fill=INK if on else MUTED)
            if on:
                dt=max(0,now-event_times[i]); r=max(0,100-round(dt*220))
                if r>0:d.ellipse((x-r,y-r,x+r,y+r),outline=AMBER,width=8)
        centered(d,f"{active} / 6",1580,fb(66),AMBER if active else MUTED)
        frame=cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR); writer.write(frame)
    writer.release()
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(tmp),"-c:v","libx264","-preset","veryfast","-crf","16","-pix_fmt","yuv420p","-r",str(FPS),str(dst)])
    tmp.unlink(missing_ok=True)


def render_short(short_root: Path, stem: str, anchors: list[str], visuals: list[Path], static: set[int], kind: str):
    data=json.loads((short_root/"02_VOICE"/"alignment"/f"{stem}_alignment.json").read_text(encoding="utf-8"))
    text,starts,ends=alignment_arrays(data); voice=short_root/"02_VOICE"/"raw"/f"{stem}.mp3"
    total=media_duration(voice); times=[anchor_time(text,starts,a) for a in anchors]+[total]
    # The first spoken phoneme begins a few milliseconds after time zero. The
    # opening visual must nevertheless cover the complete master from frame 0.
    times[0]=0.0
    segdir=short_root/"04_EDIT"/"segments"; segdir.mkdir(parents=True,exist_ok=True)
    count_times=[]
    if kind=="B": count_times=[anchor_time(text,starts,x) for x in ("one,","two,","three,","four,","five,","six.")]
    files=[]; details=[]
    for i,(img,a,b) in enumerate(zip(visuals,times,times[1:])):
        sec=max(0.1,b-a); dst=segdir/f"{i:02d}.mp4"
        if kind=="B" and i==2:
            render_six_signal_clip(dst,sec,a,count_times)
        else:
            if i in static:
                vf=f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS},format=yuv420p"
            else:
                vf=eased_zoompan_filter(duration=sec,fps=FPS,width=W,height=H,zoom_amount=0.018,
                    supersample_width=4320,supersample_height=7680)
            run(["ffmpeg","-y","-hide_banner","-loglevel","error","-loop","1","-t",f"{sec:.6f}","-i",str(img),"-vf",vf,
                "-an","-c:v","libx264","-preset","veryfast","-crf","16","-pix_fmt","yuv420p","-r",str(FPS),str(dst)])
        files.append(dst); details.append({"index":i+1,"start":round(a,3),"end":round(b,3),"duration":round(sec,3),"anchor":anchors[i],"visual":str(img.resolve()),"static":i in static,"segment":str(dst.resolve())})
    concat=segdir/"concat.txt"; concat.write_text("\n".join(f"file '{x.as_posix()}'" for x in files)+"\n",encoding="utf-8")
    video=short_root/"04_EDIT"/"video_only.mp4"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p","-color_range","tv","-r",str(FPS),"-an",str(video)])
    synth_stems(short_root,kind,total,count_times)
    audio=short_root/"04_AUDIO"; mix=audio/f"{stem}_FINAL_MIX_48K_STEREO.wav"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(voice),"-i",str(audio/"MUSIC_BED.wav"),"-i",str(audio/"SFX.wav"),
        "-filter_complex","[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=72,lowpass=f=15000,acompressor=threshold=-18dB:ratio=2.2:attack=8:release=90[vo];[1:a]volume=.24[m];[2:a]volume=.58[s];[m][s]amix=inputs=2:normalize=0[bed];[bed][vo]sidechaincompress=threshold=.018:ratio=7:attack=9:release=220[duck];[vo][duck]amix=inputs=2:normalize=0:duration=first,atrim=0:%0.6f,aresample=192000,alimiter=limit=.90,aresample=48000,loudnorm=I=-14:TP=-1.0:LRA=7[out]"%total,
        "-map","[out]","-ar","48000","-ac","2","-c:a","pcm_s24le",str(mix)])
    ass=write_captions(short_root,stem,total); final=short_root/"05_OUTPUT"/f"{stem}_MASTER_1080x1920_30.mp4"
    assf=str(ass.resolve()).replace("\\","/").replace(":","\\:").replace("'","\\'")
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(video),"-i",str(mix),"-vf",f"subtitles='{assf}',scale=w=iw:h=ih:in_range=auto:out_range=tv,format=yuv420p",
        "-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","medium","-crf","16","-profile:v","high","-level","4.2","-pix_fmt","yuv420p","-color_range","tv","-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-r",str(FPS),
        "-c:a","aac","-b:a","256k","-ar","48000","-ac","2","-t",f"{total:.6f}","-movflags","+faststart",str(final)])
    report={"stem":stem,"duration":round(media_duration(final),6),"voice":str(voice.resolve()),"mix":str(mix.resolve()),"master":str(final.resolve()),"shots":details,"count_signal_times":count_times}
    (short_root/"05_OUTPUT"/"EDIT_REPORT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return final


def covers(a: dict[str,Path],b: dict[str,Path]):
    for src,out,title1,title2,accent in [
        (a["A08"],PROD/"S01_HUFFORD_OLD_HAG"/"05_OUTPUT"/"COVER_FRAME_9x16.png","THE OLD HAG","CAME LATER",AMBER),
        (b["B09"],PROD/"S02_TAKEUCHI_LAB"/"05_OUTPUT"/"COVER_FRAME_9x16.png","AWAKE.","STILL PARALYZED.",CYAN),
    ]:
        im=cover(src); shade(im,160,225); d=ImageDraw.Draw(im)
        d.text((70,95),"NOESIS  •  MODELS OF MIND",font=fb(28),fill=accent)
        d.text((70,1320),title1,font=fb(92),fill=INK)
        d.text((70,1440),title2,font=fb(72),fill=accent)
        d.text((73,1550),"SLEEP PARALYSIS",font=fb(35),fill=INK)
        save(im,out)


def build_all():
    a=build_a_assets(); b=build_b_assets(); covers(a,b)
    va=[a["A01"],a["A02"],a["A03"],a["A04"],a["A05"],a["A06"],a["A07"],a["A08"],a["A09"],a["A10"],a["A11"],a["A11B"],a["A11C"],a["A11D"],a["A12"],a["A13"],a["A14"],a["A15"]]
    aa=["The door opens","Footsteps cross","You try to move","Then the mattress sinks","This happened to David Hufford","Years later","strangers described","gave the visitor a name","the Old Hag","REM physiology","But Hufford's puzzle","why the footsteps","the weight","the certainty","Does folklore","Or do recurring encounters","The full investigation","Which came first"]
    vb=[b["B01"],b["B02"],b["B03"],b["B04"],b["B05"],b["B06"],b["B07"],b["B08"],b["B09"],b["B10"],b["B11"],b["B12"],b["B13"],b["B14"]]
    ab=["Researchers interrupted","sixteen healthy people","Six isolated","They slept","were awakened","stayed awake for an hour","then returned to bed","Across four nights","When they occurred","All but one","The recordings caught","The doorway was measurable","The full experiment","BODY, BRAIN"]
    fa=render_short(PROD/"S01_HUFFORD_OLD_HAG","EP05_EN_SHORT_S01",aa,va,{4,8,9,11,12,14,15,16,17},"A")
    fb_=render_short(PROD/"S02_TAKEUCHI_LAB","EP05_EN_SHORT_S02",ab,vb,{1,2,5,6,7,10,12,13},"B")
    print(fa); print(fb_)


def build_b_only():
    b=build_b_assets()
    vb=[b["B01"],b["B02"],b["B03"],b["B04"],b["B05"],b["B06"],b["B07"],b["B08"],b["B09"],b["B10"],b["B11"],b["B12"],b["B13"],b["B14"]]
    ab=["Researchers interrupted","sixteen healthy people","Six isolated","They slept","were awakened","stayed awake for an hour","then returned to bed","Across four nights","When they occurred","All but one","The recordings caught","The doorway was measurable","The full experiment","BODY, BRAIN"]
    final=render_short(PROD/"S02_TAKEUCHI_LAB","EP05_EN_SHORT_S02",ab,vb,{1,2,5,6,7,10,12,13},"B")
    print(final)


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("stage",choices=["assets","render","render_b","all"]); args=ap.parse_args()
    if args.stage=="assets":
        a=build_a_assets(); b=build_b_assets(); covers(a,b)
    elif args.stage=="render_b":
        build_b_only()
    else:
        build_all()
    return 0


if __name__=="__main__":
    raise SystemExit(main())
