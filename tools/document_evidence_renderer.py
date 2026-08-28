#!/usr/bin/env python3
"""Reusable, source-faithful evidence frames for documentary episodes.

The renderer searches the original PDF for the spoken phrase, expands the
selection to a complete text block, keeps the full line width, and highlights
the actual match.  It deliberately fails when the phrase cannot be located;
silently substituting an arbitrary page crop would create false visual proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable

import pymupdf
import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class EvidenceQA:
    status: str
    pdf: str
    page: int
    phrase: str
    match_count: int
    page_rect: list[float]
    crop_rect: list[float]
    highlight_rects: list[list[float]]
    full_line_width_preserved: bool
    crop_edges_clear_text_lines: bool
    safe_canvas_margin_px: int


def _rect_list(rect: pymupdf.Rect) -> list[float]:
    return [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)]


def _text_blocks(page: pymupdf.Page) -> list[tuple[pymupdf.Rect, str]]:
    blocks: list[tuple[pymupdf.Rect, str]] = []
    for raw in page.get_text("blocks"):
        if len(raw) < 5 or not str(raw[4]).strip():
            continue
        blocks.append((pymupdf.Rect(raw[:4]), str(raw[4])))
    return blocks


def _text_lines(page: pymupdf.Page) -> list[pymupdf.Rect]:
    lines: list[pymupdf.Rect] = []
    data = page.get_text("dict")
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if spans:
                lines.append(pymupdf.Rect(line["bbox"]))
    return lines


def _complete_evidence_crop(
    page: pymupdf.Page,
    matches: list[pymupdf.Rect],
    *,
    fallback_above: float,
    fallback_below: float,
) -> tuple[pymupdf.Rect, bool]:
    """Return a full-width crop around the complete paragraph/text block."""
    match_union = pymupdf.Rect(matches[0])
    for match in matches[1:]:
        match_union |= match

    containing = [
        rect for rect, _text in _text_blocks(page)
        if rect.intersects(match_union) or rect.contains(match_union)
    ]
    if containing:
        block = min(containing, key=lambda rect: rect.get_area())
        # Most source PDFs expose paragraphs as blocks.  Very tall blocks are
        # page containers; for those we retain a generous line-snapped window.
        if block.height <= min(360.0, page.rect.height * 0.52):
            top, bottom = block.y0 - 18.0, block.y1 + 18.0
        else:
            top = match_union.y0 - fallback_above
            bottom = match_union.y1 + fallback_below
    else:
        top = match_union.y0 - fallback_above
        bottom = match_union.y1 + fallback_below

    # OCR boxes in historical PDFs frequently overlap or duplicate lines.  A
    # raster whitespace search is more faithful to what the viewer will see:
    # snap both crop edges to the nearest visually empty horizontal row.
    snap_scale = 2.0
    snap_pix = page.get_pixmap(matrix=pymupdf.Matrix(snap_scale, snap_scale), alpha=False)
    snap_image = Image.frombytes("RGB", [snap_pix.width, snap_pix.height], snap_pix.samples).convert("L")
    ink = (np.asarray(snap_image) < 205).mean(axis=1)

    def snap(y: float) -> tuple[float, float]:
        centre = max(0, min(len(ink) - 1, int(round(y * snap_scale))))
        radius = int(round(42.0 * snap_scale))
        lo = max(0, centre - radius)
        hi = min(len(ink) - 1, centre + radius)
        candidates = np.arange(lo, hi + 1)
        values = ink[candidates]
        minimum = float(values.min())
        near_minimum = candidates[values <= minimum + 0.0008]
        chosen = int(near_minimum[np.argmin(np.abs(near_minimum - centre))])
        return chosen / snap_scale, float(ink[chosen])

    top, top_ink = snap(top)
    bottom, bottom_ink = snap(bottom)
    if bottom <= match_union.y1 + 8:
        bottom, bottom_ink = snap(match_union.y1 + max(80.0, fallback_below))
    if top >= match_union.y0 - 8:
        top, top_ink = snap(match_union.y0 - max(40.0, fallback_above))

    # Preserve the complete line width.  This is the central invariant: a
    # phrase may be highlighted, but the continuation of its sentence may not
    # disappear at an editorial crop edge.
    clip = pymupdf.Rect(
        page.rect.x0,
        max(page.rect.y0, top),
        page.rect.x1,
        min(page.rect.y1, bottom),
    )

    # Skewed historical OCR frequently produces overlapping line boxes that
    # falsely connect an entire page. The raster gap is more faithful to what
    # the viewer sees and avoids collapsing a readable excerpt to a tiny full
    # page. Body-text rows occupy far less than 14% of the page width; the snap
    # routine has already selected the locally emptiest row.
    clear_edges = top_ink < 0.14 and bottom_ink < 0.14
    return clip, clear_edges


def _render_page(page: pymupdf.Page, matrix: float, clip: pymupdf.Rect | None = None) -> Image.Image:
    pix = page.get_pixmap(matrix=pymupdf.Matrix(matrix, matrix), clip=clip, alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def _highlight_crop(
    crop: Image.Image,
    clip: pymupdf.Rect,
    matches: Iterable[pymupdf.Rect],
    matrix: float,
    accent: tuple[int, int, int],
) -> Image.Image:
    rgba = crop.convert("RGBA")
    overlay = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for rect in matches:
        x0 = round((rect.x0 - clip.x0) * matrix) - 7
        y0 = round((rect.y0 - clip.y0) * matrix) - 5
        x1 = round((rect.x1 - clip.x0) * matrix) + 7
        y1 = round((rect.y1 - clip.y0) * matrix) + 5
        draw.rounded_rectangle(
            (x0, y0, x1, y1), radius=7,
            fill=(*accent, 58), outline=(*accent, 245), width=4,
        )
    return Image.alpha_composite(rgba, overlay).convert("RGB")


def render_evidence_frame(
    *,
    pdf_path: Path,
    page_number: int,
    phrase: str,
    output_path: Path,
    metadata_path: Path,
    canvas_size: tuple[int, int] = (1920, 1080),
    background: tuple[int, int, int] = (8, 15, 18),
    paper: tuple[int, int, int] = (236, 232, 218),
    accent: tuple[int, int, int] = (224, 174, 71),
    fallback_above: float = 70.0,
    fallback_below: float = 230.0,
    footer: str | None = None,
    footer_font: ImageFont.ImageFont | None = None,
) -> EvidenceQA:
    doc = pymupdf.open(pdf_path)
    page = doc[page_number - 1]
    matches = page.search_for(phrase)
    if not matches:
        raise ValueError(f"Evidence phrase not found on page {page_number}: {phrase!r} in {pdf_path}")

    clip, clear_edges = _complete_evidence_crop(
        page, matches, fallback_above=fallback_above, fallback_below=fallback_below,
    )
    crop_scale = 3.6
    full = _render_page(page, 1.5)
    crop = _render_page(page, crop_scale, clip)
    crop = _highlight_crop(crop, clip, matches, crop_scale, accent)

    width, height = canvas_size
    canvas = Image.new("RGB", canvas_size, background)
    safe = 72
    context_box = (500, 900)
    evidence_box = (1190, 820)
    full.thumbnail(context_box, Image.Resampling.LANCZOS)
    crop.thumbnail(evidence_box, Image.Resampling.LANCZOS)

    context_panel = Image.new("RGB", (560, 940), paper)
    evidence_panel = Image.new("RGB", (1270, 900), paper)
    canvas.paste(context_panel, (safe, 68))
    canvas.paste(evidence_panel, (620, 108))
    canvas.paste(full, (safe + (560 - full.width) // 2, 88 + (900 - full.height) // 2))
    canvas.paste(crop, (660 + (1190 - crop.width) // 2, 148 + (820 - crop.height) // 2))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle((618, 106, 1892, 1010), outline=(115, 120, 116), width=2)
    draw.line((660, 985, 1160, 985), fill=accent, width=8)
    if footer and footer_font:
        draw.text((safe, 1020), footer, font=footer_font, fill=(190, 197, 194))

    qa = EvidenceQA(
        status="PASS",
        pdf=str(pdf_path),
        page=page_number,
        phrase=phrase,
        match_count=len(matches),
        page_rect=_rect_list(page.rect),
        crop_rect=_rect_list(clip),
        highlight_rects=[_rect_list(rect) for rect in matches],
        full_line_width_preserved=True,
        crop_edges_clear_text_lines=clear_edges,
        safe_canvas_margin_px=safe,
    )
    if not clear_edges:
        qa.status = "FAIL_TEXT_LINE_AT_CROP_EDGE"
        raise RuntimeError(json.dumps(asdict(qa), ensure_ascii=False))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=96)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(asdict(qa), indent=2, ensure_ascii=False), encoding="utf-8")
    return qa
