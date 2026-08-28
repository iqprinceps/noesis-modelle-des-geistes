#!/usr/bin/env python3
"""Pre-render QA for EP01's final viewer-led EDL and document evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


EP = Path(__file__).resolve().parents[1]
EDL = EP / "06_TIMELINE" / "EP01_EN_FINAL_EDL.csv"
QA_DIR = EP / "05_QA" / "FINAL_TIMELINE"
REPORT = QA_DIR / "EP01_FINAL_TIMELINE_PRE_RENDER_QA.json"
DOC_CONTACT = QA_DIR / "EP01_FINAL_DOCUMENT_CONTACT_SHEET.jpg"
DOC_MOBILE = QA_DIR / "EP01_FINAL_DOCUMENT_MOBILE_PROOF.jpg"
NEW_CONTACT = QA_DIR / "EP01_FINAL_REPAIR_CONTACT_SHEET.jpg"
CLIP_CONTACT = QA_DIR / "EP01_FINAL_CLIP_START_MID_END.jpg"
SERIES = EP.parents[1] / "00_GLOBAL" / "SERIES_ASSET_REGISTER.csv"


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


F18, F26 = font(18), font(26, True)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe(path: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ], check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def video_frame(path: Path, seconds: float) -> Image.Image:
    with tempfile.TemporaryDirectory(prefix="ep01_qa_") as folder:
        output = Path(folder) / "frame.png"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{seconds:.4f}",
            "-i", str(path), "-frames:v", "1", str(output)
        ], check=True)
        return Image.open(output).convert("RGB").copy()


def representative(path: Path) -> Image.Image:
    if path.suffix.casefold() == ".mp4":
        duration = float(ffprobe(path)["format"]["duration"])
        return video_frame(path, max(0, duration/2))
    return Image.open(path).convert("RGB")


def dhash(image: Image.Image) -> str:
    gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = list(gray.getdata())
    value = 0
    for y in range(8):
        for x in range(8):
            value = (value << 1) | int(pixels[y*9+x] > pixels[y*9+x+1])
    return f"{value:016x}"


def distance(a: str, b: str) -> int:
    return (int(a, 16) ^ int(b, 16)).bit_count()


def contact(items: list[tuple[str, Image.Image]], output: Path, cell=(480, 310), columns=3) -> None:
    rows_count = (len(items)+columns-1)//columns
    canvas = Image.new("RGB", (cell[0]*columns, cell[1]*rows_count), (7, 12, 15))
    draw = ImageDraw.Draw(canvas)
    for index, (label, source) in enumerate(items):
        col, row = index % columns, index // columns
        thumb = ImageOps.fit(source.convert("RGB"), (cell[0], cell[1]-40), Image.Resampling.LANCZOS)
        x, y = col*cell[0], row*cell[1]
        canvas.paste(thumb, (x, y+40))
        draw.text((x+8, y+8), label, font=F18, fill=(231, 236, 238))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=92)


def main() -> int:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    edl = rows(EDL)
    issues = []
    paths = [EP / row["selected_file_path"] for row in edl]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        issues.append({"type": "MISSING_ASSET", "items": missing})

    states = [row["visual_state_id"] for row in edl]
    returns = [state for state, count in Counter(states).items() if count > 1]
    if returns:
        issues.append({"type": "ASSET_RETURN", "items": returns})

    badges = [row["event"] for row in edl if row.get("visible_mode_badge", "NO") not in ("", "NO")]
    if badges:
        issues.append({"type": "VISIBLE_MODE_BADGE", "items": badges})

    file_hashes, visual_hashes = {}, {}
    for row, path in zip(edl, paths):
        if not path.is_file():
            continue
        file_hashes[row["visual_state_id"]] = sha256(path)
        visual_hashes[row["visual_state_id"]] = dhash(representative(path))
    exact = []
    by_hash = {}
    for state, digest in file_hashes.items():
        if digest in by_hash:
            exact.append([by_hash[digest], state])
        by_hash[digest] = state
    if exact:
        issues.append({"type": "EXACT_CONTENT_DUPLICATE", "items": exact})
    near = []
    items = list(visual_hashes.items())
    for i, (a, ah) in enumerate(items):
        for b, bh in items[i+1:]:
            d = distance(ah, bh)
            if d <= 2:
                near.append({"a": a, "b": b, "distance": d})

    docs = [row for row in edl if row["visual_state_id"].startswith("KZ_DOC_")]
    doc_motion = [row["event"] for row in docs if row["motion_class"] != "STATIC_OR_NEAR_STATIC"]
    if doc_motion:
        issues.append({"type": "DOCUMENT_MOTION", "items": doc_motion})
    doc_items = [(row["visual_state_id"], Image.open(EP/row["selected_file_path"]).convert("RGB")) for row in docs]
    contact(doc_items, DOC_CONTACT, columns=3)
    contact([(label, image.resize((480, 270), Image.Resampling.LANCZOS)) for label, image in doc_items], DOC_MOBILE, cell=(480, 310), columns=3)

    new_states = {
        "KZ_DATA_PATENT_FILING_ANCHOR", "KZ_FIG_PATENT_CYLINDER", "KZ_MODEL_CLOCKWISE_SPIRAL",
        "KZ_FILM_LUNAR_STORM_SESSION", "KZ_DOC_028", "KZ_FILM_ALUMINUM_SURFACE_MACRO",
        "KZ_CLIP_FIELD_CONCENTRATION_PROPOSAL", "KZ_FILM_HELIOGEOPHYSICAL_CHAMBER", "KZ_DOC_029",
        "KZ_FILM_PATENT_AUTHORITY_LIGHTTABLE", "KZ_DOC_030", "KZ_FIG_PATENT_DRAWINGS_PAGE8",
        "KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS", "KZ_CLIP_PATENT_FEATURES_RECAP",
        "KZ_MYSTIC_CLAIMS_TRIAD", "KZ_MYSTIC_INTENSE_EXPERIENCE_HISTORY",
    }
    repair_items = [(row["visual_state_id"], representative(EP/row["selected_file_path"])) for row in edl if row["visual_state_id"] in new_states]
    contact(repair_items, NEW_CONTACT, columns=3)

    clip_rows = [row for row in edl if (EP/row["selected_file_path"]).suffix.casefold() == ".mp4"]
    clip_items, clip_qa = [], []
    for row in clip_rows:
        path = EP / row["selected_file_path"]
        probe = ffprobe(path)
        duration = float(probe["format"]["duration"])
        video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
        fps = video.get("avg_frame_rate", "")
        decode = subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-v", "error", "-i", str(path), "-f", "null", "-"
        ], capture_output=True, text=True)
        clip_qa.append({
            "state": row["visual_state_id"], "duration": duration, "edl_duration": float(row["duration_seconds"]),
            "fps": fps, "width": video.get("width"), "height": video.get("height"), "decode_exit": decode.returncode,
        })
        for label, second in (("start", .05), ("mid", duration/2), ("end", max(.05, duration-.08))):
            clip_items.append((f"{row['visual_state_id']} {label}", video_frame(path, second)))
        if duration + .08 < float(row["duration_seconds"]) or decode.returncode:
            issues.append({"type": "CLIP_DECODE_OR_DURATION", "state": row["visual_state_id"]})
    contact(clip_items, CLIP_CONTACT, columns=3)

    holds = []
    for row in edl:
        duration = float(row["duration_seconds"])
        if duration >= 8:
            item = {
                "event": row["event"], "state": row["visual_state_id"], "duration": duration,
                "motion": row["motion_class"], "reason": row["long_hold_reason"],
            }
            holds.append(item)
            if duration > 10 and (row["motion_class"] != "PROGRESSIVE_MOTION" or not row["long_hold_reason"].strip()):
                issues.append({"type": "UNJUSTIFIED_HOLD_OVER_10", "item": item})

    series_collisions = []
    if SERIES.is_file():
        other = {row["content_sha256"]: row for row in rows(SERIES) if row.get("episode_id") != "EP01_KOZYREV"}
        for state, digest in file_hashes.items():
            if digest in other:
                series_collisions.append({"state": state, "other": other[digest]})
    if series_collisions:
        issues.append({"type": "SERIES_CONTENT_COLLISION", "items": series_collisions})

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "status": "PASS" if not issues else "FAIL",
        "event_count": len(edl), "unique_state_count": len(set(states)), "missing_assets": missing,
        "asset_returns": returns, "exact_content_duplicates": exact, "near_duplicate_candidates_distance_le_2": near,
        "selected_document_count": len(docs), "document_motion_violations": doc_motion,
        "document_policy": "STATIC_NO_PAN_ZOOM", "clip_qa": clip_qa, "holds_at_or_above_8_seconds": holds,
        "series_content_collisions": series_collisions, "visible_mode_badges": badges,
        "contact_sheets": [str(p.relative_to(EP)) for p in (DOC_CONTACT, DOC_MOBILE, NEW_CONTACT, CLIP_CONTACT)],
        "issues": issues,
        "manual_review_required": [
            "Inspect every final document at full size and 480x270 mobile proof.",
            "Inspect every repair still and every clip at start/middle/end.",
            "Review near-duplicate candidates by content, not hash alone.",
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "events": len(edl), "documents": len(docs), "clips": len(clip_rows), "issues": issues, "near": len(near)}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
