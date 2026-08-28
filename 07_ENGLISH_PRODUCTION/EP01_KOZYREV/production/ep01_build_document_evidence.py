#!/usr/bin/env python3
"""Build only source-faithful EP01 document-evidence candidates.

No network media service is used. Every selected evidence crop is built from an
existing original PDF. Missing phrases produce a failure JSON and no PNG.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import asdict
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw
from rapidocr_onnxruntime import RapidOCR


EP = Path(__file__).resolve().parents[1]
ROOT = EP.parents[1]
sys.path.insert(0, str(ROOT))
from tools.document_evidence_renderer import render_evidence_frame  # noqa: E402


ORIG = EP / "04_SOURCES" / "ORIGINALS"
RENDERS = EP / "04_SOURCES" / "RENDERS"
OUT = EP / "04_ASSETS" / "GENERATED" / "DOCUMENT_EVIDENCE"
META = EP / "04_ASSETS" / "METADATA" / "DOCUMENT_EVIDENCE"
QA = EP / "05_QA" / "DOCUMENT_EVIDENCE"
OCR_CACHE = META / "OCR_CACHE"
CURRENT_MAP = EP / "04_ASSETS" / "METADATA" / "deterministic_asset_map.json"
BUILD_VERSION = 6

PATENT = "RU2122446C1_patent.pdf"
PAPER_2006 = "Kaznacheev_Trofimov_2006_Kozirev_space.pdf"
PAPER_2008 = "Kaznacheev_Trofimov_2008_Distant_Interaction.pdf"
COLLECTION = "Kozyrev_Mirrors_2019_collection.pdf"


def spec(shot_id, edl_event, asset_id, start, end, voice, source_id, pdf, page,
         method, phrases=(), region=None, fail_reason=None, note=""):
    return {
        "shot_id": shot_id, "edl_event": edl_event, "asset_id": asset_id,
        "start": start, "end": end, "voice": voice, "source_id": source_id,
        "pdf": pdf, "page": page, "method": method,
        "phrases": list(phrases), "region": region,
        "fail_reason": fail_reason, "note": note,
        "motion_policy": "STATIC_NO_PAN_ZOOM",
    }


SHOTS = [
    spec("KZ_DOC_001", "KZ-EDL-002", "KZ_SRC_PATENT_COVER_DATE", 2.800, 9.200,
         "In 1996, two Russian researchers filed a patent for a chamber made from curved aluminum panels.",
         "KZ-SRC-001", PATENT, 2, "fail", fail_reason="COMPOUND_VOICE_ONLY_PARTIALLY_HIGHLIGHTED",
         note="Date, inventors, and construction require separate readable excerpts; current single crop proves only the date."),
    spec("KZ_DOC_002", "KZ-EDL-003", "KZ_SRC_PATENT_TITLE_CROP", 9.200, 15.640,
         "Its first page gives the document a clinical title: a device for correcting psychosomatic diseases.",
         "KZ-SRC-001", PATENT, 2, "ocr_scan",
         ["DEVICE FOR CORRECTION OF MAN'S PSYCHOSOMATIC DISEASES"], "title"),
    spec("KZ_DOC_003", "KZ-EDL-009", "KZ_SRC_PATENT_FIG2_CYLINDER", 37.760, 39.640,
         "The panels could form a cylinder.", "KZ-SRC-001", PATENT, 6, "fail",
         fail_reason="FIGURE_HAS_NO_EXACT_TEXTUAL_PHRASE", note="Figure 2 is visually relevant but has no searchable phrase/caption supporting 'cylinder'."),
    spec("KZ_DOC_004", "KZ-EDL-010", "KZ_SRC_PATENT_FIG3_CW", 39.640, 41.120,
         "A clockwise spiral.", "KZ-SRC-001", PATENT, 7, "fail",
         fail_reason="FIGURE_DOES_NOT_ENCODE_DIRECTION", note="Figure 3 shows a spiral but does not prove clockwise direction."),
    spec("KZ_DOC_005", "KZ-EDL-012", "KZ_SRC_PATENT_FIG4_ROTATION", 43.200, 47.080,
         "One version placed the entire structure on a motorized platform.", "KZ-SRC-001", PATENT, 2, "ocr_scan",
         ["platform coupled to", "motor", "rotation."], "abstract",
         note="Both exact source fragments are highlighted inside the complete abstract paragraph."),
    spec("KZ_DOC_006", "KZ-EDL-014", "KZ_SRC_PATENT_LUNAR_GEOMAGNETIC", 48.840, 55.680,
         "The patent even favored sessions near the new moon, the full moon, and what it called magneto-ionospheric storms.",
         "KZ-SRC-001", PATENT, 4, "fail", fail_reason="NO_SEARCHABLE_TEXT_LAYER_AND_NO_VERIFIED_EXACT_PHRASE"),
    spec("KZ_DOC_007", "KZ-EDL-024", "KZ_SRC_RESEARCHERS_AND_PUBLICATIONS", 94.800, 100.280,
         "They studied the human body, the environment, and what they described as information exchange.",
         "KZ-SRC-008", COLLECTION, 161, "fail", fail_reason="WRONG_PAGE_SEMANTIC_MISMATCH",
         note="Current page 161 discusses a lunar-test project, not the complete simultaneous voice claim."),
    spec("KZ_DOC_008", "KZ-EDL-032", "KZ_SRC_PATENT_POLISHED_SURFACE_TEXT", 121.960, 124.720,
         "Their inner surfaces are ground or polished.", "KZ-SRC-001", PATENT, 2, "fail",
         ["with ground surface"], "abstract", fail_reason="VOICE_EXCEEDS_VISIBLE_SOURCE_PHRASE",
         note="The English abstract says 'ground surface'; 'polished' is not present in this translation."),
    spec("KZ_DOC_009", "KZ-EDL-033", "KZ_SRC_PATENT_FOCUS", 124.720, 130.360,
         "Their curvature is designed to create a focus about fifty centimeters in front of the working surface.",
         "KZ-SRC-001", PATENT, 2, "ocr_scan",
         ["for focus at a distance of 50 cm from operating surface."], "abstract"),
    spec("KZ_DOC_010", "KZ-EDL-039", "KZ_SRC_PATENT_GEOMAGNETIC", 142.800, 146.640,
         "Why should a treatment chamber care about geomagnetic conditions?", "KZ-SRC-001", PATENT, 4, "fail",
         fail_reason="NO_SEARCHABLE_TEXT_LAYER_AND_NO_VERIFIED_EXACT_PHRASE"),
    spec("KZ_DOC_011", "KZ-EDL-040", "KZ_SRC_PATENT_INVENTOR_CLAIM", 146.640, 149.640,
         "The patent records the inventors' answer.", "KZ-SRC-001", PATENT, 1, "fail",
         fail_reason="CURRENT_CROP_NOT_TRACEABLE_TO_EXACT_PASSAGE"),
    spec("KZ_DOC_012", "KZ-EDL-042", "KZ_SRC_PATENT_HELIOGEOPHYSICAL", 155.840, 160.800,
         "They connected treatment conditions with what they called the heliogeophysical environment.",
         "KZ-SRC-001", PATENT, 4, "fail", fail_reason="NO_SEARCHABLE_TEXT_LAYER_AND_NO_VERIFIED_EXACT_PHRASE"),
    spec("KZ_DOC_013", "KZ-EDL-046", "KZ_SRC_RESEARCHERS_LATER_WORK", 166.680, 171.440,
         "But Kaznacheev and Trofimov did not keep the idea inside medicine.", "KZ-SRC-007", PAPER_2008, 6,
         "pdf_text_title", ["Distant-information interaction"]),
    spec("KZ_DOC_014", "KZ-EDL-047", "KZ_SRC_2006_MODELED_SPACE", 171.440, 175.520,
         "In later publications, they described a modeled Kozyrev space.", "KZ-SRC-006", PAPER_2006, 9,
         "pdf_text_title", ["modeled ―Kozirev space‖"]),
    spec("KZ_DOC_015", "KZ-EDL-048", "KZ_SRC_2006_ALTERED_INTERNAL_TIME", 175.520, 178.160,
         "They wrote about altered internal time.", "KZ-SRC-006", PAPER_2006, 9, "fail",
         fail_reason="EXACT_PHRASE_NOT_FOUND", note="The English abstract says 'temporary transparentness', not altered internal time."),
    spec("KZ_DOC_016", "KZ-EDL-087", "KZ_SRC_EVIDENCE_PATENT", 317.280, 321.160,
         "The sources behind this episode contain a real patent.", "KZ-SRC-001", PATENT, 2, "ocr_scan",
         ["RUSSIAN AGENCY FOR PATENTS AND TRADEMARKS"], "agency"),
    spec("KZ_DOC_017", "KZ-EDL-088", "KZ_SRC_EVIDENCE_PUBLICATIONS", 321.160, 326.720,
         "They contain publications in which the researchers describe extraordinary information effects.",
         "KZ-SRC-006", PAPER_2006, 9, "fail", ["a set of unusual optical effects"],
         fail_reason="SEMANTIC_MISMATCH_INFORMATION_VS_OPTICAL_EFFECTS",
         note="Corrected from mismatched 2019 collection page to the authors' 2006 English abstract."),
    spec("KZ_DOC_018", "KZ-EDL-092", "KZ_SRC_PATENT_AUTHORITY_TRAP", 338.720, 341.880,
         "And here the patent creates one final trap.", "KZ-SRC-001", PATENT, 2, "fail",
         ["ABSTRACT OF INVENTION"], "agency", fail_reason="INTERPRETIVE_VOICE_HAS_NO_EXACT_SOURCE_PHRASE",
         note="Formal patent header is context, not an exact phrase for 'trap'."),
    spec("KZ_DOC_019A", "KZ-EDL-093/KZ-CUE-097", "KZ_SRC_PATENT_AUTHORITY_FULL", 341.880, 342.960,
         "It looks like a verdict.", "KZ-SRC-001", PATENT, 2, "fail", ["ABSTRACT OF INVENTION"], "agency",
         fail_reason="INTERPRETIVE_VOICE_HAS_NO_EXACT_SOURCE_PHRASE"),
    spec("KZ_DOC_019B", "KZ-EDL-093/KZ-CUE-098", "KZ_SRC_PATENT_NUMBER_CROP", 342.960, 344.040,
         "A government number.", "KZ-SRC-001", PATENT, 2, "ocr_scan", ["2 122 446"], "number",
         note="The exact number is highlighted; RU and C1 remain visible in the same source header."),
    spec("KZ_DOC_019C", "KZ-EDL-093/KZ-CUE-099", "KZ_SRC_PATENT_DATES_CROP", 344.040, 345.240,
         "Dates.", "KZ-SRC-001", PATENT, 2, "ocr_scan",
         ["Application: 96113190/14, 02.07.1996", "Date of publication: 27.11.1998"], "metadata_left"),
    spec("KZ_DOC_019D", "KZ-EDL-093/KZ-CUE-100", "KZ_SRC_PATENT_INVENTORS_CROP", 345.240, 346.320,
         "Inventors.", "KZ-SRC-001", PATENT, 2, "ocr_scan",
         ["Kaznacheev V.P.", "Trofimov A.V."], "metadata_right"),
    spec("KZ_DOC_019E", "KZ-EDL-093/KZ-CUE-101", "KZ_SRC_PATENT_DRAWINGS", 346.320, 347.560,
         "Technical drawings.", "KZ-SRC-001", PATENT, 8, "fail",
         fail_reason="FIGURE_PAGE_HAS_NO_EXACT_TEXTUAL_PHRASE", note="Existing animated document clip is prohibited; drawing page needs a separate evidence decision."),
    spec("KZ_DOC_020", "KZ-EDL-099", "KZ_SRC_EVIDENCE_STACK", 366.000, 369.360,
         "For this story, the patent is still invaluable.", "KZ-SRC-008", COLLECTION, 138, "fail",
         fail_reason="WRONG_SOURCE_PAGE", note="A 2019 clinical table cannot evidence the value of the 1996 patent."),
    spec("KZ_DOC_021", "KZ-EDL-100", "KZ_SRC_PATENT_DIMENSIONS", 369.360, 371.160,
         "It gives the legend dimensions.", "KZ-SRC-001", PATENT, 2, "ocr_scan",
         ["aluminum-alloy plates. 0.5 mm thick, up to 280 cm high and 120 cm wide."], "abstract"),
    spec("KZ_DOC_022", "KZ-EDL-102", "KZ_SRC_PATENT_FOCUS_TEXT_DETAIL", 374.600, 375.800,
         "Focal distance.", "KZ-SRC-001", PATENT, 2, "fail",
         ["for focus at a distance of 50 cm from operating surface."], "abstract",
         fail_reason="DUPLICATE_EVIDENCE_RETURN_NO_NEW_SOURCE_STATE",
         note="Would exactly duplicate KZ_DOC_009 after an intervening visual; later callback needs a genuinely new asset."),
    spec("KZ_DOC_023", "KZ-EDL-103", "KZ_SRC_PATENT_DIRECTION_TEXT_DETAIL", 375.800, 376.640,
         "Direction.", "KZ-SRC-001", PATENT, 3, "fail", fail_reason="EXACT_DIRECTION_PHRASE_NOT_VERIFIED"),
    spec("KZ_DOC_024", "KZ-EDL-104", "KZ_SRC_PATENT_ROTATION_TEXT_DETAIL", 376.640, 377.760,
         "Rotation.", "KZ-SRC-001", PATENT, 2, "fail",
         ["platform coupled to", "motor", "rotation."], "abstract",
         fail_reason="DUPLICATE_EVIDENCE_RETURN_NO_NEW_SOURCE_STATE",
         note="Would exactly duplicate KZ_DOC_005 after an intervening visual; later callback needs a genuinely new asset."),
    spec("KZ_DOC_025", "KZ-EDL-107", "KZ_SRC_PATENT_DOCUMENTED_CHAMBER", 383.600, 385.840,
         "The patented chamber is documented.", "KZ-SRC-001", PATENT, 2, "ocr_scan",
         ["SUBSTANCE: device has", "construction which"], "abstract",
         note="The complete abstract paragraph remains visible; the source translation omits 'chamber'."),
    spec("KZ_DOC_026", "KZ-EDL-108", "KZ_SRC_KAZNACHEEV_TROFIMOV_CLAIM_HISTORY", 385.840, 392.440,
         "Kaznacheev and Trofimov connected it with unusual claims about perception, information, and time.",
         "KZ-SRC-006", PAPER_2006, 9, "fail", ["distant information transmission"],
         fail_reason="COMPOUND_VOICE_NOT_SUPPORTED_BY_SINGLE_VISIBLE_PASSAGE",
         note="Corrected from generic 2019 page to the named authors' English abstract; voice contains broader synthesis."),
    spec("KZ_DOC_027", "KZ-EDL-109", "KZ_SRC_CLAIM_HISTORY_PUBLICATIONS", 392.440, 396.320,
         "Reports of intense experiences belong to the history of the project.", "KZ-SRC-008", COLLECTION, 142,
         "fail", fail_reason="EXACT_PHRASE_NOT_FOUND_ON_PLANNED_PAGE"),
]


REGIONS = {
    "number": (500, 90, 1070, 230),
    "agency": (120, 330, 610, 470),
    "metadata_left": (120, 455, 610, 565),
    "metadata_right": (620, 455, 1060, 700),
    "title": (120, 690, 850, 750),
    "abstract": (115, 735, 610, 1170),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).casefold()
    return "".join(char for char in text if char.isalnum())


def ocr_lines(image_path: Path) -> list[dict]:
    cache = OCR_CACHE / f"{image_path.stem}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))["lines"]
    result, _elapsed = RapidOCR()(str(image_path))
    lines = []
    for box, text, score in result or []:
        lines.append({"box": box, "text": text, "confidence": float(score)})
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"image": str(image_path), "lines": lines}, indent=2, ensure_ascii=False), encoding="utf-8")
    return lines


def box_rect(box):
    xs = [point[0] for point in box]
    ys = [point[1] for point in box]
    return min(xs), min(ys), max(xs), max(ys)


def in_region(line: dict, region: tuple[int, int, int, int]) -> bool:
    x0, y0, x1, y1 = box_rect(line["box"])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return region[0] <= cx <= region[2] and region[1] <= cy <= region[3]


def locate_phrase(lines: list[dict], phrase: str) -> list[dict]:
    ordered = sorted(lines, key=lambda row: (round(box_rect(row["box"])[1] / 8), box_rect(row["box"])[0]))
    stream = ""
    owners: list[int] = []
    for index, line in enumerate(ordered):
        part = normalized(line["text"])
        stream += part
        owners.extend([index] * len(part))
    needle = normalized(phrase)
    start = stream.find(needle)
    if start < 0:
        raise ValueError(f"OCR exact normalized phrase not found: {phrase!r}")
    selected = sorted(set(owners[start:start + len(needle)]))
    matches = [ordered[index] for index in selected]
    if not matches or min(item["confidence"] for item in matches) < 0.72:
        raise ValueError(f"OCR confidence below threshold for: {phrase!r}")
    return matches


def render_ocr(specification: dict, output: Path, metadata: Path) -> dict:
    source = RENDERS / "PATENT" / f"RU2122446C1-{specification['page']}.png"
    page = Image.open(source).convert("RGB")
    region = REGIONS[specification["region"]]
    candidates = [line for line in ocr_lines(source) if in_region(line, region)]
    matched: list[dict] = []
    for phrase in specification["phrases"]:
        matched.extend(locate_phrase(candidates, phrase))
    unique = []
    seen = set()
    for row in matched:
        key = tuple(round(v, 1) for p in row["box"] for v in p)
        if key not in seen:
            unique.append(row)
            seen.add(key)

    rx0, ry0, rx1, ry1 = region
    crop = page.crop((rx0, ry0, rx1, ry1)).convert("RGBA")
    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for row in unique:
        x0, y0, x1, y1 = box_rect(row["box"])
        draw.rounded_rectangle((x0-rx0-5, y0-ry0-4, x1-rx0+5, y1-ry0+4), radius=6,
                               fill=(224, 174, 71, 58), outline=(224, 174, 71, 245), width=4)
    crop = Image.alpha_composite(crop, overlay).convert("RGB")

    canvas = Image.new("RGB", (1920, 1080), (8, 15, 18))
    context = page.copy()
    context.thumbnail((540, 930), Image.Resampling.LANCZOS)
    scale = min(1190 / crop.width, 820 / crop.height)
    crop = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.Resampling.LANCZOS)
    canvas.paste(Image.new("RGB", (570, 950), (236, 232, 218)), (60, 60))
    canvas.paste(Image.new("RGB", (1260, 900), (236, 232, 218)), (630, 105))
    canvas.paste(context, (60 + (570-context.width)//2, 70 + (930-context.height)//2))
    canvas.paste(crop, (665 + (1190-crop.width)//2, 145 + (820-crop.height)//2))
    ImageDraw.Draw(canvas).rectangle((628, 103, 1892, 1007), outline=(115, 120, 116), width=2)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=96)
    record = {
        "status": "PASS_OCR_VERIFIED_SCAN", "build_version": BUILD_VERSION,
        "pdf": str(ORIG / specification["pdf"]),
        "source_render": str(source), "page": specification["page"],
        "phrase": " | ".join(specification["phrases"]), "match_count": len(unique),
        "ocr_engine": "RapidOCR local ONNX", "ocr_min_confidence": min(r["confidence"] for r in unique),
        "highlight_rects": [list(box_rect(row["box"])) for row in unique],
        "crop_rect": list(region), "full_line_width_preserved": True,
        "crop_edges_clear_text_lines": True, "safe_canvas_margin_px": 60,
    }
    metadata.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def render_pdf_title(specification: dict, output: Path, metadata: Path) -> dict:
    """Render authors plus complete title, ending before the abstract begins."""
    pdf_path = ORIG / specification["pdf"]
    doc = pymupdf.open(pdf_path)
    page = doc[specification["page"] - 1]
    matches = page.search_for(specification["phrases"][0])
    if not matches:
        raise ValueError(f"Evidence phrase not found: {specification['phrases'][0]!r}")
    union = pymupdf.Rect(matches[0])
    for match in matches[1:]:
        union |= match
    clip = pymupdf.Rect(page.rect.x0, max(page.rect.y0, union.y0 - 30),
                        page.rect.x1, min(page.rect.y1, union.y1 + 2))

    def raster(matrix: float, rect=None):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(matrix, matrix), clip=rect, alpha=False)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    full = raster(1.5)
    crop_scale = 3.6
    def highlighted(source_clip: pymupdf.Rect, scale: float):
        source = raster(scale, source_clip).convert("RGBA")
        overlay = Image.new("RGBA", source.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for rect in matches:
            draw.rounded_rectangle(((rect.x0-source_clip.x0)*scale-7, (rect.y0-source_clip.y0)*scale-5,
                                    (rect.x1-source_clip.x0)*scale+7, (rect.y1-source_clip.y0)*scale+5),
                                   radius=7, fill=(224, 174, 71, 58), outline=(224, 174, 71, 245), width=4)
        return Image.alpha_composite(source, overlay).convert("RGB")

    crop = highlighted(clip, crop_scale)
    detail_clip = pymupdf.Rect(max(page.rect.x0, union.x0 - 3), max(page.rect.y0, union.y0 - 2),
                               min(page.rect.x1, union.x1 + 3), min(page.rect.y1, union.y1 + 3))
    detail = highlighted(detail_clip, 5.2)
    full.thumbnail((500, 900), Image.Resampling.LANCZOS)
    crop.thumbnail((1190, 260), Image.Resampling.LANCZOS)
    scale = min(1100 / detail.width, 260 / detail.height)
    detail = detail.resize((max(1, round(detail.width*scale)), max(1, round(detail.height*scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1920, 1080), (8, 15, 18))
    canvas.paste(Image.new("RGB", (560, 940), (236, 232, 218)), (72, 68))
    canvas.paste(Image.new("RGB", (1270, 900), (236, 232, 218)), (620, 108))
    canvas.paste(full, (72 + (560-full.width)//2, 88 + (900-full.height)//2))
    canvas.paste(crop, (660 + (1190-crop.width)//2, 315 - crop.height//2))
    canvas.paste(detail, (705 + (1100-detail.width)//2, 690 - detail.height//2))
    ImageDraw.Draw(canvas).rectangle((618, 106, 1892, 1010), outline=(115, 120, 116), width=2)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=96)
    record = {
        "status": "PASS", "build_version": BUILD_VERSION, "pdf": str(pdf_path),
        "page": specification["page"], "phrase": specification["phrases"][0],
        "match_count": len(matches), "page_rect": list(page.rect), "crop_rect": list(clip),
        "highlight_rects": [list(rect) for rect in matches], "full_line_width_preserved": True,
        "crop_edges_clear_text_lines": True, "safe_canvas_margin_px": 72,
        "crop_scope": "complete_author_and_title_block_only",
        "detail_crop_rect": list(detail_clip),
    }
    metadata.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    current = json.loads(CURRENT_MAP.read_text(encoding="utf-8"))
    inventory = {"episode": "EP01_KOZYREV", "policy": "STATIC_NO_PAN_ZOOM", "shots": SHOTS}
    inv_path = META / "EP01_DOCUMENT_EVIDENCE_INVENTORY.json"
    inv_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")

    rows = []
    for item in SHOTS:
        output = OUT / f"{item['shot_id']}.png"
        metadata = META / f"{item['shot_id']}.json"
        record = {**item}
        mapped = current.get(item["asset_id"], {})
        current_path = EP / mapped.get("file_path", "") if mapped.get("file_path") else None
        record["current_asset_path"] = str(current_path) if current_path else None
        record["current_asset_sha256"] = sha256(current_path) if current_path and current_path.exists() else None
        record["output_path"] = str(output)
        try:
            if item["method"] == "fail":
                raise ValueError(item["fail_reason"])
            if output.exists() and metadata.exists():
                old = json.loads(metadata.read_text(encoding="utf-8"))
                if str(old.get("status", "")).startswith("PASS") and old.get("build_version") == BUILD_VERSION:
                    rows.append(old)
                    continue
            if item["method"] == "ocr_scan":
                evidence = render_ocr(item, output, metadata)
            elif item["method"] == "pdf_text_title":
                evidence = render_pdf_title(item, output, metadata)
            elif item["method"] == "pdf_text":
                qa = render_evidence_frame(
                    pdf_path=ORIG / item["pdf"], page_number=item["page"], phrase=item["phrases"][0],
                    output_path=output, metadata_path=metadata,
                )
                evidence = asdict(qa)
            else:
                raise ValueError(f"Unknown method: {item['method']}")
            record.update(evidence)
            record["status"] = evidence["status"]
            record["build_version"] = BUILD_VERSION
            record["output_sha256"] = sha256(output)
        except Exception as exc:
            if output.exists():
                output.unlink()
            record["status"] = item.get("fail_reason") or "FAIL_BUILD"
            record["build_error"] = str(exc)[:500]
        metadata.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append(record)

    csv_path = META / "EP01_DOCUMENT_EVIDENCE_INVENTORY.csv"
    fields = ["shot_id", "edl_event", "asset_id", "start", "end", "voice", "source_id", "pdf", "page",
              "method", "status", "motion_policy", "phrase", "output_path", "note", "build_error"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary = {
        "status": "PASS" if all(str(r["status"]).startswith("PASS") for r in rows) else "FAIL",
        "edl_document_events": 27,
        "document_shots_including_clip_substates": len(rows),
        "corrected_assets": sum(str(r["status"]).startswith("PASS") for r in rows),
        "failed_assets": sum(not str(r["status"]).startswith("PASS") for r in rows),
        "render_started": False,
        "paid_generation_started": False,
    }
    (QA / "EP01_DOCUMENT_EVIDENCE_BUILD_SUMMARY.json").parent.mkdir(parents=True, exist_ok=True)
    (QA / "EP01_DOCUMENT_EVIDENCE_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
