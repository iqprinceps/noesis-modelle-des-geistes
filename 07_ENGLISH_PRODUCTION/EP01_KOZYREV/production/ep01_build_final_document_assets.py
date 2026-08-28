#!/usr/bin/env python3
"""Build EP01 assets authorized by the final 31-shot decision matrix.

All document pixels come from archived originals. AI stills are accepted cached
outputs and are not generated here. The three clips are deterministic local builds.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from dataclasses import asdict
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


EP = Path(__file__).resolve().parents[1]
ORIG = EP / "04_SOURCES" / "ORIGINALS"
RENDERS = EP / "04_SOURCES" / "RENDERS" / "PATENT"
OUT_LOCAL = EP / "04_ASSETS" / "GENERATED" / "FINAL_DOCUMENT_TIMELINE"
OUT_DOC = EP / "04_ASSETS" / "GENERATED" / "DOCUMENT_EVIDENCE"
OUT_CLIP = EP / "04_ASSETS" / "CLIPS" / "LOCAL_PROGRESSIVE"
META = EP / "04_ASSETS" / "METADATA" / "FINAL_DOCUMENT_TIMELINE"
AI = EP / "04_ASSETS" / "GENERATED" / "NATIVE_IMAGEGEN" / "FINAL_DOCUMENT_REPAIR"
W, H, FPS = 1920, 1080, 25
BG = (8, 15, 18)
PAPER = (236, 232, 218)
WHITE = (235, 239, 240)
MUTED = (154, 169, 174)
CYAN = (87, 203, 217)
AMBER = (224, 174, 71)


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/bahnschrift.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F24, F30, F42, F54 = (font(n) for n in (24, 30, 42, 54))
FB34, FB56, FB88 = (font(n, True) for n in (34, 56, 88))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ImageOps.fit(image.convert("RGB"), (W, H), Image.Resampling.LANCZOS).save(path, compress_level=3)


def source_footer(draw: ImageDraw.ImageDraw, text: str) -> None:
    draw.text((72, 1020), text, font=F24, fill=MUTED)


def build_data_anchor() -> Path:
    path = OUT_LOCAL / "KZ_DATA_PATENT_FILING_ANCHOR.png"
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)
    # A source-faithful data anchor, not a reconstructed document.
    draw.arc((1010, 130, 1810, 930), 40, 325, fill=(55, 86, 94), width=18)
    draw.arc((1150, 270, 1680, 800), 35, 315, fill=CYAN, width=6)
    draw.ellipse((85, 80, 105, 100), fill=CYAN)
    draw.line((105, 90, 1830, 90), fill=(40, 65, 72), width=2)
    draw.text((110, 175), "2 JULY 1996", font=FB88, fill=WHITE)
    draw.text((116, 330), "KAZNACHEEV  +  TROFIMOV", font=FB56, fill=(214, 221, 221))
    draw.text((116, 450), "CURVED ALUMINUM PANEL CHAMBER", font=F42, fill=AMBER)
    draw.line((116, 545, 905, 545), fill=(69, 96, 101), width=3)
    draw.text((116, 585), "Verified filing data and construction abstract", font=F30, fill=MUTED)
    source_footer(draw, "Source: RU 2 122 446 C1 • application data and abstract")
    save(im, path)
    return path


def technical_figure(page_name: str, title: str, output_name: str) -> Path:
    source = Image.open(RENDERS / page_name).convert("RGB")
    path = OUT_LOCAL / output_name
    im = Image.new("RGB", (W, H), BG)
    context = ImageOps.contain(source, (430, 850), Image.Resampling.LANCZOS)
    figure = ImageOps.contain(source, (1250, 880), Image.Resampling.LANCZOS)
    im.paste(Image.new("RGB", (500, 900), PAPER), (60, 70))
    im.paste(Image.new("RGB", (1290, 900), PAPER), (570, 70))
    im.paste(context, (95 + (430-context.width)//2, 95 + (850-context.height)//2))
    im.paste(figure, (590 + (1250-figure.width)//2, 90 + (880-figure.height)//2))
    draw = ImageDraw.Draw(im)
    draw.rectangle((568, 68, 1862, 972), outline=(111, 117, 114), width=2)
    draw.text((72, 20), title, font=F30, fill=WHITE)
    source_footer(draw, "Original technical figure • RU 2 122 446 C1")
    save(im, path)
    return path


def sentence_evidence_from_accepted(
    accepted_name: str, output_name: str, heading: str, source_note: str, accent: str,
) -> Path:
    """Recompose an already verified exact highlight as a mobile-readable evidence state.

    The crop is derived from the amber highlight in the accepted renderer output,
    keeping the complete text line above and below. It never invents or retypes text.
    """
    source = Image.open(OUT_DOC / accepted_name).convert("RGB")
    pixels = source.load()
    amber = []
    for y in range(100, source.height - 60, 2):
        for x in range(620, source.width - 30, 2):
            r, g, b = pixels[x, y]
            if r > 175 and 105 < g < 215 and b < 135 and r > g + 20:
                amber.append((x, y))
    if not amber:
        raise ValueError(f"No verified amber phrase found in {accepted_name}")
    xs, ys = zip(*amber)
    y0, y1 = max(100, min(ys) - 105), min(source.height - 60, max(ys) + 110)
    excerpt = source.crop((635, y0, 1890, y1))
    page = Image.open(RENDERS / "RU2122446C1-2.png").convert("RGB")
    page.thumbnail((360, 760), Image.Resampling.LANCZOS)
    excerpt.thumbnail((1325, 610), Image.Resampling.LANCZOS)

    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)
    draw.text((72, 30), heading, font=F30, fill=WHITE)
    im.paste(Image.new("RGB", (430, 820), PAPER), (65, 105))
    im.paste(page, (100 + (360 - page.width)//2, 135 + (760 - page.height)//2))
    im.paste(Image.new("RGB", (1320, 690), PAPER), (540, 150))
    im.paste(excerpt, (555 + (1290 - excerpt.width)//2, 190 + (610 - excerpt.height)//2))
    draw.rectangle((538, 148, 1862, 842), outline=(111, 117, 114), width=2)
    if accent == "focus":
        draw.line((660, 900, 1540, 900), fill=CYAN, width=6)
        draw.line((660, 875, 660, 925), fill=CYAN, width=6)
        draw.line((1540, 875, 1540, 925), fill=CYAN, width=6)
        draw.text((1015, 925), "50 cm", font=FB34, fill=WHITE, anchor="mm")
    else:
        draw.line((680, 900, 1500, 900), fill=AMBER, width=5)
        for x, label in ((680, "1.2 m"), (1500, "2.8 m")):
            draw.line((x, 878, x, 922), fill=AMBER, width=5)
            draw.text((x, 946), label, font=F24, fill=WHITE, anchor="mm")
    source_footer(draw, source_note)
    path = OUT_DOC / output_name
    save(im, path)
    (META / f"{Path(output_name).stem}.json").write_text(json.dumps({
        "status": "PASS", "source_id": "KZ-SRC-001", "page": 2,
        "derived_from_verified_evidence": accepted_name,
        "highlight_bbox_in_verified_frame": [min(xs), min(ys), max(xs), max(ys)],
        "full_context_margin_pixels": [105, 110], "motion_policy": "STATIC_NO_PAN_ZOOM",
        "output": str(path),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def english_abstract_sentence_panels() -> Path:
    """Create one large exact-sentence panel from the original English abstract.

    The sentence wraps across three source lines, beginning at the end of one line.
    We retain the original raster glyphs and re-stack those source line fragments;
    no OCR text is retyped into the evidence area.
    """
    pdf_path = ORIG / "Kaznacheev_Trofimov_2006_Kozirev_space.pdf"
    doc = pymupdf.open(pdf_path)
    page = doc[8]
    start = page.search_for("Under the experiments")
    phrase = page.search_for("unusual optical effects")
    end = page.search_for("temporary transparentness")
    if len(start) != 2 or not phrase or not end:
        raise ValueError("Exact final optical-effects sentence could not be located on p.9")
    scale = 7.0
    # Original sentence pixels split only at word boundaries for mobile legibility.
    # The order remains verbatim; no glyph is synthesized.
    line_rects = [
        pymupdf.Rect(start[0].x0 - 1, start[0].y0, start[0].x1 + 1, start[0].y1),
        pymupdf.Rect(56.64, start[1].y0, 216.0, start[1].y1),
        pymupdf.Rect(221.5, start[1].y0, 511.0, start[1].y1),
        pymupdf.Rect(56.64, end[0].y0, 220.0, end[0].y1),
        pymupdf.Rect(221.5, end[0].y0, end[0].x1 + 6, end[0].y1),
    ]
    strips = []
    for rect in line_rects:
        pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=rect, alpha=False)
        strips.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))

    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)
    draw.text((72, 35), "AUTHORS' ENGLISH ABSTRACT", font=F30, fill=WHITE)
    draw.text((72, 100), "Exact sentence from the original page", font=F24, fill=MUTED)
    panel_box = (70, 170, 1850, 925)
    im.paste(Image.new("RGB", (1780, 755), PAPER), panel_box[:2])
    y = 255
    pasted = []
    for strip in strips:
        fit = ImageOps.contain(strip, (1580, 112), Image.Resampling.LANCZOS)
        x = 170
        im.paste(fit, (x, y))
        pasted.append((x, y, fit.width, fit.height))
        y += 125
    # Highlight the real phrase on the third original-raster fragment.
    line2 = line_rects[2]
    phrase_rect = phrase[0]
    x, y, fw, fh = pasted[2]
    source_w = (line2.x1 - line2.x0) * scale
    ratio = fw / source_w
    hx0 = x + (phrase_rect.x0-line2.x0) * scale * ratio - 7
    hx1 = x + (phrase_rect.x1-line2.x0) * scale * ratio + 7
    hy0, hy1 = y + 5, y + fh - 5
    draw.rounded_rectangle((hx0, hy0, hx1, hy1), radius=7, outline=AMBER, width=5)
    draw.rectangle(panel_box, outline=(111, 117, 114), width=2)
    source_footer(draw, "KZ-SRC-006 • original p. 9 • complete optical-effects sentence")
    path = OUT_DOC / "KZ_DOC_029.png"
    save(im, path)
    (META / "KZ_DOC_029.json").write_text(json.dumps({
        "status": "PASS", "source_id": "KZ-SRC-006", "page": 9,
        "phrases": ["Under the experiments", "unusual optical effects", "temporary transparentness"],
        "source_line_rects": [list(r) for r in line_rects],
        "original_raster_glyphs_only": True, "complete_relevant_sentence": True,
        "motion_policy": "STATIC_NO_PAN_ZOOM",
        "output": str(path),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def distant_interaction_sentence_panel() -> Path:
    """Mobile-readable verbatim first sentence from the 2008 English abstract."""
    pdf_path = ORIG / "Kaznacheev_Trofimov_2008_Distant_Interaction.pdf"
    page = pymupdf.open(pdf_path)[5]
    chunks = [
        "There are described the experiments",
        "on studying of distant field interactions",
        "between alive cages, peo-",
        "ple, plants.",
    ]
    rects = []
    for chunk in chunks:
        found = page.search_for(chunk)
        if not found:
            raise ValueError(f"Exact phrase not found on p.6: {chunk!r}")
        rects.append(found[0])
    scale = 7.0
    strips = []
    for rect in rects:
        clip = pymupdf.Rect(rect.x0 - 1, rect.y0, rect.x1 + 1, rect.y1)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip, alpha=False)
        strips.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)
    draw.text((72, 35), "DISTANT-INFORMATION INTERACTION", font=F30, fill=WHITE)
    draw.text((72, 100), "Authors' English abstract — exact opening sentence", font=F24, fill=MUTED)
    panel_box = (70, 170, 1850, 925)
    im.paste(Image.new("RGB", (1780, 755), PAPER), panel_box[:2])
    y = 260
    pasted = []
    for strip in strips:
        fit = ImageOps.contain(strip, (1580, 125), Image.Resampling.LANCZOS)
        x = 170
        im.paste(fit, (x, y))
        pasted.append((x, y, fit.width, fit.height))
        y += 145
    phrase = page.search_for("distant field interactions")[0]
    source_rect = rects[1]
    x, y, fw, fh = pasted[1]
    ratio = fw / ((source_rect.x1-source_rect.x0) * scale)
    hx0 = x + (phrase.x0-source_rect.x0) * scale * ratio - 7
    hx1 = x + (phrase.x1-source_rect.x0) * scale * ratio + 7
    draw.rounded_rectangle((hx0, y+4, hx1, y+fh-4), radius=7, outline=AMBER, width=5)
    draw.rectangle(panel_box, outline=(111, 117, 114), width=2)
    source_footer(draw, "KZ-SRC-007 • original p. 6 • complete first sentence")
    path = OUT_DOC / "KZ_DOC_028.png"
    save(im, path)
    (META / "KZ_DOC_028.json").write_text(json.dumps({
        "status": "PASS", "source_id": "KZ-SRC-007", "page": 6,
        "verbatim_chunks": chunks, "source_rects": [list(r) for r in rects],
        "original_raster_glyphs_only": True, "complete_relevant_sentence": True,
        "motion_policy": "STATIC_NO_PAN_ZOOM", "output": str(path),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def clockwise_model() -> Path:
    path = OUT_LOCAL / "KZ_MODEL_CLOCKWISE_SPIRAL.png"
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)
    draw.ellipse((88, 62, 108, 82), fill=CYAN)
    draw.line((108, 72, 1830, 72), fill=(40, 65, 72), width=2)
    draw.text((110, 135), "CLOCKWISE SPIRAL", font=FB56, fill=WHITE)
    cx, cy = 1030, 590
    points = []
    for i in range(330):
        t = i / 329 * math.pi * 4.6
        radius = 24 + 28 * t
        points.append((cx + radius * math.cos(t), cy + radius * math.sin(t)))
    draw.line(points, fill=AMBER, width=15, joint="curve")
    x1, y1 = points[-1]
    x0, y0 = points[-9]
    angle = math.atan2(y1-y0, x1-x0)
    for delta in (2.55, -2.55):
        draw.line((x1, y1, x1+54*math.cos(angle+delta), y1+54*math.sin(angle+delta)), fill=AMBER, width=14)
    draw.text((112, 940), "Direction is an explanatory translation of the patent's left/right spiral configurations.", font=F24, fill=MUTED)
    save(im, path)
    return path


def render_multi_document(pdf_name: str, page_number: int, phrases: list[str], output_name: str, source_id: str) -> Path:
    pdf_path = ORIG / pdf_name
    doc = pymupdf.open(pdf_path)
    page = doc[page_number-1]
    matches = []
    for phrase in phrases:
        found = page.search_for(phrase)
        if not found:
            raise ValueError(f"Exact phrase not found on page {page_number}: {phrase!r}")
        matches.extend(found)
    union = pymupdf.Rect(matches[0])
    for rect in matches[1:]:
        union |= rect
    clip = pymupdf.Rect(page.rect.x0, max(page.rect.y0, union.y0-48), page.rect.x1, min(page.rect.y1, union.y1+55))

    def raster(matrix: float, region=None):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(matrix, matrix), clip=region, alpha=False)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    full = raster(1.6)
    crop = raster(4.0, clip).convert("RGBA")
    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for rect in matches:
        coords = ((rect.x0-clip.x0)*4-6, (rect.y0-clip.y0)*4-5, (rect.x1-clip.x0)*4+6, (rect.y1-clip.y0)*4+5)
        od.rounded_rectangle(coords, radius=7, fill=(*AMBER, 54), outline=(*AMBER, 240), width=4)
    crop = Image.alpha_composite(crop, overlay).convert("RGB")
    full.thumbnail((470, 880), Image.Resampling.LANCZOS)
    crop.thumbnail((1250, 790), Image.Resampling.LANCZOS)
    im = Image.new("RGB", (W, H), BG)
    im.paste(Image.new("RGB", (520, 910), PAPER), (60, 70))
    im.paste(Image.new("RGB", (1280, 880), PAPER), (590, 100))
    im.paste(full, (85+(470-full.width)//2, 85+(880-full.height)//2))
    im.paste(crop, (605+(1250-crop.width)//2, 130+(790-crop.height)//2))
    draw = ImageDraw.Draw(im)
    draw.rectangle((588, 98, 1872, 982), outline=(111, 117, 114), width=2)
    source_footer(draw, f"{source_id} • original p. {page_number} • static, exact phrases highlighted")
    path = OUT_DOC / output_name
    save(im, path)
    record = {
        "status": "PASS", "source_id": source_id, "pdf": str(pdf_path), "page": page_number,
        "phrases": phrases, "match_count": len(matches), "crop_rect": list(clip),
        "highlight_rects": [list(r) for r in matches], "full_line_width_preserved": True,
        "motion_policy": "STATIC_NO_PAN_ZOOM", "output": str(path),
    }
    (META / f"{Path(output_name).stem}.json").parent.mkdir(parents=True, exist_ok=True)
    (META / f"{Path(output_name).stem}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return path


def metadata_composite() -> Path:
    inputs = [OUT_DOC / name for name in ("KZ_DOC_019B.png", "KZ_DOC_019C.png", "KZ_DOC_019D.png")]
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("Accepted patent metadata components are missing")
    path = OUT_DOC / "KZ_DOC_030.png"
    im = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(im)
    draw.text((72, 26), "PATENT METADATA", font=F30, fill=WHITE)
    boxes = [(70, 88, 1850, 354), (70, 378, 1850, 674), (70, 698, 1850, 994)]
    for source_path, box in zip(inputs, boxes):
        source = Image.open(source_path).convert("RGB").crop((620, 105, 1890, 1007))
        panel = ImageOps.fit(source, (box[2]-box[0], box[3]-box[1]), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        im.paste(panel, box[:2])
        draw.rectangle(box, outline=(111, 117, 114), width=2)
    source_footer(draw, "KZ-SRC-001 • original p. 2 • number, full date lines and full inventor lines")
    save(im, path)
    (META / "KZ_DOC_030.json").write_text(json.dumps({
        "status": "PASS", "source_id": "KZ-SRC-001", "page": 2,
        "components": [p.name for p in inputs], "motion_policy": "STATIC_NO_PAN_ZOOM",
        "full_relevant_lines_preserved": True, "output": str(path),
    }, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return path


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t*t*(3-2*t)


def fit_frame(image: Image.Image) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), (W, H), Image.Resampling.LANCZOS)


def zoom_frame(image: Image.Image, t: float, amount: float = 0.035, x_bias: float = 0.5, y_bias: float = 0.5) -> Image.Image:
    base = fit_frame(image)
    scale = 1 + amount * ease(t)
    nw, nh = round(W*scale), round(H*scale)
    enlarged = base.resize((nw, nh), Image.Resampling.LANCZOS)
    left = round((nw-W)*x_bias)
    top = round((nh-H)*y_bias)
    return enlarged.crop((left, top, left+W, top+H))


def encode(path: Path, duration: float, frame_fn) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = round(duration * FPS)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for index in range(frames):
            frame = frame_fn(index/(frames-1 if frames > 1 else 1))
            process.stdin.write(frame.convert("RGB").tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {path}")


def field_clip() -> Path:
    source = Image.open(EP / "04_ASSETS/GENERATED/DETERMINISTIC/KZ_MODEL_FIELD_CONCENTRATION.png").convert("RGB")
    path = OUT_CLIP / "KZ_CLIP_FIELD_CONCENTRATION_PROPOSAL.mp4"
    def frame(t):
        im = zoom_frame(source, t, .018, .53, .5)
        draw = ImageDraw.Draw(im, "RGBA")
        p = ease(t)
        centre = (1140, 585)
        for i in range(9):
            y = 365 + i*52
            visible = max(0.0, min(1.0, p*1.45-i*.055))
            if visible <= 0: continue
            x_end = 700 + int(730*visible)
            bend = int(70*math.sin(visible*math.pi))
            draw.line([(620, y), (880, y), (1040, y+bend), (x_end, y)], fill=(*CYAN, int(115+90*visible)), width=4)
        radius = 18 + 48*(0.5+0.5*math.sin(t*math.pi*8))*p
        draw.ellipse((centre[0]-radius, centre[1]-radius, centre[0]+radius, centre[1]+radius), outline=(*AMBER, 210), width=5)
        return im
    encode(path, 9.24, frame)
    return path


def value_limits_clip() -> Path:
    images = [
        Image.open(EP / "04_ASSETS/GENERATED/DETERMINISTIC/KZ_CARD_PATENT_CAN_SHOW.png"),
        Image.open(EP / "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_PATENT_PROVENANCE_DESK.png"),
        Image.open(EP / "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_EMPTY_RESULT_TRAY.png"),
    ]
    path = OUT_CLIP / "KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS.mp4"
    def state(index, local):
        return zoom_frame(images[index], local, .028 if index else .008, .46+.08*index, .5)
    def frame(t):
        seconds = t*14.0
        cuts = [0.0, 4.55, 9.2, 14.0]
        index = 0 if seconds < cuts[1] else 1 if seconds < cuts[2] else 2
        local = (seconds-cuts[index])/(cuts[index+1]-cuts[index])
        base = state(index, local)
        fade = .45
        if index < 2 and cuts[index+1]-fade <= seconds < cuts[index+1]:
            alpha = ease((seconds-(cuts[index+1]-fade))/fade)
            nxt = state(index+1, 0.0)
            base = Image.blend(base, nxt, alpha)
        return base
    encode(path, 14.0, frame)
    return path


def features_clip() -> Path:
    source = Image.open(AI / "KZ_PATENT_FEATURES_RECAP_START.png").convert("RGB")
    path = OUT_CLIP / "KZ_CLIP_PATENT_FEATURES_RECAP.mp4"
    def frame(t):
        im = zoom_frame(source, t, .012, .53, .54)
        draw = ImageDraw.Draw(im, "RGBA")
        seconds = t*3.2
        # Phase 1: physical focal-distance measuring jig.
        p1 = ease(min(1, seconds/.85))
        x0, x1, y = 120, int(120+560*p1), 710
        draw.line((x0, y, x1, y), fill=(*CYAN, 225), width=7)
        if p1 > .7:
            draw.line((x0, y-28, x0, y+28), fill=(*CYAN, 225), width=6)
            draw.line((x1, y-28, x1, y+28), fill=(*CYAN, 225), width=6)
            draw.text((280, 650), "50 cm", font=FB34, fill=(*WHITE, int(255*(p1-.7)/.3)))
        # Phase 2: direction arc appears over the open spiral.
        if seconds >= .9:
            p2 = ease(min(1, (seconds-.9)/.9))
            draw.arc((720, 110, 1500, 850), 205, 205+270*p2, fill=(*AMBER, 230), width=9)
        # Phase 3: drive housing rotation indicator.
        if seconds >= 1.9:
            p3 = ease(min(1, (seconds-1.9)/.8))
            draw.arc((830, 690, 1130, 990), 220, 220+295*p3, fill=(230, 118, 91, 235), width=10)
        return im
    encode(path, 3.2, frame)
    return path


def main() -> int:
    for folder in (OUT_LOCAL, OUT_DOC, OUT_CLIP, META):
        folder.mkdir(parents=True, exist_ok=True)
    built = [
        build_data_anchor(),
        technical_figure("RU2122446C1-6.png", "PATENT FIGURE 2", "KZ_FIG_PATENT_CYLINDER.png"),
        technical_figure("RU2122446C1-8.png", "PATENT FIGURE 4", "KZ_FIG_PATENT_MOTORIZED_PLATFORM.png"),
        clockwise_model(),
        technical_figure("RU2122446C1-7.png", "PATENT FIGURE 3", "KZ_FIG_PATENT_DRAWING_FIG3.png"),
        distant_interaction_sentence_panel(),
        english_abstract_sentence_panels(),
        metadata_composite(),
        sentence_evidence_from_accepted(
            "KZ_DOC_009.png", "KZ_DOC_032.png", "FOCUS DISTANCE",
            "KZ-SRC-001 • original p. 2 • complete focus-distance sentence", "focus",
        ),
        sentence_evidence_from_accepted(
            "KZ_DOC_021.png", "KZ_DOC_031.png", "CHAMBER DIMENSIONS",
            "KZ-SRC-001 • original p. 2 • complete dimensions/material sentence", "dimensions",
        ),
        field_clip(), value_limits_clip(), features_clip(),
    ]
    report = {
        "status": "PASS", "build_version": 1, "asset_count": len(built),
        "assets": [{"path": p.relative_to(EP).as_posix(), "sha256": sha256(p)} for p in built],
        "paid_generation_jobs": 0, "document_motion": "STATIC_NO_PAN_ZOOM",
        "clip_fps": FPS, "note": "All local builds are deterministic and resumable by stable output path.",
    }
    (META / "FINAL_DOCUMENT_ASSET_BUILD.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
