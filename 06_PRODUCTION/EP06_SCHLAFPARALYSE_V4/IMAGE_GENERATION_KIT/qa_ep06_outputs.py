#!/usr/bin/env python3
"""Create deterministic EP06 image inventory and labeled QA contact sheets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from statistics import fmean

from PIL import Image, ImageDraw, ImageFont, ImageStat


KIT = Path(__file__).resolve().parent
QUEUE = KIT / "GENERATION_QUEUE.csv"
OUTPUT = KIT / "03_GENERATED_OUTPUT" / "NanoBanana_2K_Series"
SHEETS = OUTPUT / "QA_CONTACT_SHEETS"
REPORT = OUTPUT / "EP06_SHOT_QA.json"
SEQUENCE = OUTPUT / "EP06_SHOT_SEQUENCE.csv"


EXISTING_APPROVED = {
    "IMG001_1963_BEDROOM_DOOR.png",
    "IMG002_FOOTSTEPS_APPROACH.png",
    "IMG003_HAND_WILL_NOT_MOVE.png",
    "IMG005_CHEST_PRESSURE_CLOSE.png",
    "IMG007_FOGO_PLACE_ANCHOR_RECON.png",
    "SHOT01_EMPTY_HALLWAY.png",
}
REDESIGN_BUILTIN = {
    "IMG001_1963_BEDROOM_DOOR.png",
    "IMG002_FOOTSTEPS_APPROACH.png",
    "IMG003_HAND_WILL_NOT_MOVE.png",
    "IMG005_CHEST_PRESSURE_CLOSE.png",
    "IMG006_MALEVOLENT_PRESENCE_NEGATIVE_SPACE.png",
    "IMG009_REM_BODY_STILL.png",
    "IMG011_WAKE_BODY_LAG.png",
    "IMG013_INTRUDER_DOORWAY.png",
    "IMG015_VESTIBULAR_FLOAT.png",
    "IMG016_THREE_FAMILIES_TRIPTYCH_BASE.png",
    "IMG018_SLEEP_INTERRUPTION_CLOCK.png",
    "IMG019_RETURN_TO_BED_RECON.png",
    "IMG023_BODY_OR_VISITOR_SPLIT_BASE.png",
    "IMG024_EYE_CORNER_FORM.png",
    "IMG025_ALARM_WITHOUT_CAUSE.png",
    "IMG027_SHADOW_BECOMES_SHOULDER.png",
    "IMG028_PRESENCE_BEFORE_FORM.png",
    "IMG029_OBSERVING_INTELLIGENCE_AMBIGUOUS.png",
    "IMG031_NAMES_OVER_SAME_ROOM_BASE.png",
    "IMG032_BEDROOM_TO_COURT_HANDOFF.png",
    "SHOT04_EMPTY_BEDROOM_SHADOWS.png",
    "SHOT06_CTA_EMPTY_ROOM.png",
    "SHOT07_EMPTY_CORNER_AFTER_PRESENCE.png",
}
BED_OR_BEDROOM_FINALS = {
    "IMG004_MATTRESS_WEIGHT.png",
    "IMG008_OLD_HAG_BEDROOM_PATTERN.png",
    "IMG012_ARM_COMMAND_NO_RESPONSE.png",
    "IMG014_INCUBUS_PRESSURE.png",
    "IMG017_SLEEP_LAB_WIDE_RECON.png",
    "IMG020_EEG_AWAKE_BODY_STILL_BASE.png",
    "IMG021_LAB_HALLUCINATION_AMBIGUOUS.png",
    "IMG022_VIEWER_BEDROOM_TWO_STEPS.png",
    "IMG026_SOUND_BECOMES_STEP.png",
    "SHOT08_DAWN_AFTER_PARALYSIS.png",
}
SOURCE_LOCKED = {
    "IMG010_REM_RECORD_EDIT_BASE.png",
    "SHOT02_FOGO_MAP_TABLE.png",
    "SHOT03_REM_VS_SLOW_WAVE_SOURCE_TABLE.png",
}
VERTEX_PRO = {
    "IMG004_MATTRESS_WEIGHT.png",
    "IMG011_WAKE_BODY_LAG.png",
    "IMG012_ARM_COMMAND_NO_RESPONSE.png",
    "IMG014_INCUBUS_PRESSURE.png",
    "IMG017_SLEEP_LAB_WIDE_RECON.png",
    "IMG018_SLEEP_INTERRUPTION_CLOCK.png",
    "IMG020_EEG_AWAKE_BODY_STILL_BASE.png",
    "IMG022_VIEWER_BEDROOM_TWO_STEPS.png",
}


def queue_rows() -> list[dict[str, str]]:
    with QUEUE.open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        return [row for row in rows if row["kind"] != "STYLE_MASTER"]


def generation_method(name: str) -> str:
    if name in REDESIGN_BUILTIN:
        return "BUILTIN_IMAGEGEN_REDESIGN_LANCZOS_2K"
    if name in EXISTING_APPROVED:
        return "EXISTING_APPROVED_NANOBANANA"
    if name in SOURCE_LOCKED:
        return "DETERMINISTIC_SOURCE_LOCKED_COMPOSITE"
    if name in VERTEX_PRO:
        return "VERTEX_GEMINI_3_PRO_IMAGE_2K"
    return "BUILTIN_IMAGEGEN_UPSCALED_2K"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approve-after-visual-review", action="store_true")
    args = parser.parse_args()
    rows = queue_rows()
    names = [row["output_filename"] for row in rows]
    row_by_name = {row["output_filename"]: row for row in rows}
    SHEETS.mkdir(parents=True, exist_ok=True)
    inventory: list[dict[str, object]] = []
    thumbs: list[tuple[str, Image.Image]] = []
    missing: list[str] = []

    for name in names:
        path = OUTPUT / name
        if not path.is_file():
            missing.append(name)
            continue
        with Image.open(path) as source:
            rgb = source.convert("RGB")
            stat = ImageStat.Stat(rgb.resize((160, 90)))
            mean_rgb = [round(value, 2) for value in stat.mean]
            luminance = round(0.2126 * stat.mean[0] + 0.7152 * stat.mean[1] + 0.0722 * stat.mean[2], 2)
            inventory.append(
                {
                    "filename": name,
                    "order": int(row_by_name[name]["order"]),
                    "kind": row_by_name[name]["kind"],
                    "prompt_source": row_by_name[name]["prompt_source"],
                    "generation_method": generation_method(name),
                    "redesigned": name in REDESIGN_BUILTIN,
                    "bed_or_bedroom": name in BED_OR_BEDROOM_FINALS,
                    "width": source.width,
                    "height": source.height,
                    "aspect_ratio": round(source.width / source.height, 6),
                    "mode": source.mode,
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "mean_rgb": mean_rgb,
                    "mean_luminance": luminance,
                    "technical_status": "PASS"
                    if source.width == 2560 and source.height == 1440 and name.startswith(("IMG", "SHOT"))
                    else "REVIEW",
                    "visual_status": "PASS" if args.approve_after_visual_review else "PENDING_MANUAL_REVIEW",
                }
            )
            thumb = rgb.copy()
            thumb.thumbnail((640, 360), Image.Resampling.LANCZOS)
            thumbs.append((name, thumb))

    font = ImageFont.load_default(size=18)
    for sheet_index in range(0, len(thumbs), 4):
        group = thumbs[sheet_index : sheet_index + 4]
        canvas = Image.new("RGB", (1280, 780), (24, 24, 24))
        draw = ImageDraw.Draw(canvas)
        for local_index, (name, thumb) in enumerate(group):
            col = local_index % 2
            row = local_index // 2
            x = col * 640
            y = row * 390
            fitted = thumb
            image_y = y + 30
            canvas.paste(fitted, (x + (640 - fitted.width) // 2, image_y))
            draw.rectangle((x, y, x + 640, y + 30), fill=(12, 12, 12))
            draw.text((x + 8, y + 6), name, fill=(245, 245, 245), font=font)
        number = sheet_index // 4 + 1
        canvas.save(SHEETS / f"EP06_QA_SHEET_{number:02d}.jpg", quality=92, subsampling=0)

    report = {
        "episode": "EP06",
        "expected_images": len(names),
        "present_images": len(inventory),
        "missing_images": missing,
        "all_filenames_follow_IMG_or_SHOT": all(name.startswith(("IMG", "SHOT")) for name in names),
        "all_dimensions_2560x1440": all(
            item["width"] == 2560 and item["height"] == 1440 for item in inventory
        ),
        "average_luminance": round(fmean(item["mean_luminance"] for item in inventory), 2)
        if inventory
        else None,
        "minimum_luminance": min(item["mean_luminance"] for item in inventory) if inventory else None,
        "redesigned_images": len(REDESIGN_BUILTIN),
        "bed_or_bedroom_images": len(BED_OR_BEDROOM_FINALS),
        "bed_or_bedroom_limit": 10,
        "bed_or_bedroom_limit_pass": len(BED_OR_BEDROOM_FINALS) <= 10,
        "visual_review_completed": args.approve_after_visual_review,
        "visual_review_criteria": [
            "prompt adherence",
            "anatomy and room geometry",
            "no forbidden entity or silhouette",
            "no unwanted generated text or watermark",
            "readable shadows and mobile-safe midtones",
            "source-pixel preservation for map and polysomnography frames",
        ],
        "images": inventory,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with SEQUENCE.open("w", encoding="utf-8-sig", newline="") as handle:
        fields = [
            "order",
            "kind",
            "filename",
            "prompt_source",
            "generation_method",
            "redesigned",
            "bed_or_bedroom",
            "technical_status",
            "visual_status",
            "width",
            "height",
            "mean_luminance",
            "recommended_use",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in sorted(inventory, key=lambda value: int(value["order"])):
            writer.writerow(
                {
                    **{field: item.get(field, "") for field in fields},
                    "recommended_use": "MAIN_SEQUENCE_POOL"
                    if item["kind"] == "MAIN"
                    else "RESERVE_INSERT",
                }
            )
    print(json.dumps({key: report[key] for key in report if key != "images"}, indent=2, ensure_ascii=False))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
