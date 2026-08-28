#!/usr/bin/env python3
"""Project-wide visual QA for source-faithful document evidence frames."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("episode", type=Path)
    parser.add_argument("--pattern", default="*_DOC*.png")
    parser.add_argument("--per-sheet", type=int, default=9)
    args = parser.parse_args()

    episode = args.episode.resolve()
    crops = episode / "03_VISUALS" / "DOCUMENT_CROPS"
    metadata = episode / "03_VISUALS" / "METADATA" / "DOCUMENT_EVIDENCE"
    qa_dir = episode / "03_VISUALS" / "QA" / "DOCUMENT_EVIDENCE"
    qa_dir.mkdir(parents=True, exist_ok=True)

    assets = sorted(crops.glob(args.pattern))
    failures: list[str] = []
    records: list[dict] = []
    for asset in assets:
        meta_path = metadata / f"{asset.stem}.json"
        if not meta_path.exists():
            failures.append(f"missing metadata: {asset.name}")
            continue
        record = json.loads(meta_path.read_text(encoding="utf-8"))
        status = str(record.get("status", ""))
        if not status.startswith("PASS"):
            failures.append(f"{asset.name}: {status}")
        whole_page_scan = status == "PASS_WHOLE_PAGE_NO_TEXT_LAYER"
        if not whole_page_scan and not record.get("full_line_width_preserved"):
            failures.append(f"line width not preserved: {asset.name}")
        if not whole_page_scan and not record.get("crop_edges_clear_text_lines"):
            failures.append(f"text line at crop edge: {asset.name}")
        records.append({"asset": asset, "metadata": record})

    cell_w, cell_h = 1280, 720
    columns, rows = 3, 3
    title_h = 76
    thumb_box = (cell_w - 28, cell_h - title_h - 22)
    font = _font(24)
    small = _font(18)
    sheets: list[str] = []
    per_sheet = min(args.per_sheet, columns * rows)
    for sheet_no, offset in enumerate(range(0, len(records), per_sheet), 1):
        page = Image.new("RGB", (columns * cell_w, rows * cell_h), (12, 18, 21))
        draw = ImageDraw.Draw(page)
        for slot, item in enumerate(records[offset:offset + per_sheet]):
            row, column = divmod(slot, columns)
            x, y = column * cell_w, row * cell_h
            asset: Path = item["asset"]
            meta = item["metadata"]
            image = Image.open(asset).convert("RGB")
            image.thumbnail(thumb_box, Image.Resampling.LANCZOS)
            ix = x + (cell_w - image.width) // 2
            iy = y + title_h + (cell_h - title_h - image.height) // 2
            page.paste(image, (ix, iy))
            draw.text((x + 18, y + 12), asset.name, font=font, fill=(236, 235, 226))
            phrase = str(meta.get("phrase", ""))
            if len(phrase) > 105:
                phrase = phrase[:102] + "..."
            draw.text((x + 18, y + 44), f"p.{meta.get('page')} | {phrase}", font=small, fill=(224, 174, 71))
            draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(63, 74, 78), width=2)
        out = qa_dir / f"DOCUMENT_EVIDENCE_CONTACT_{sheet_no:02d}.jpg"
        page.save(out, quality=91)
        sheets.append(str(out))

    report = {
        "status": "PASS" if not failures and len(records) == len(assets) else "FAIL",
        "episode": str(episode),
        "asset_count": len(assets),
        "metadata_count": len(records),
        "failures": failures,
        "contact_sheets": sheets,
    }
    report_path = qa_dir / "DOCUMENT_EVIDENCE_QA.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
