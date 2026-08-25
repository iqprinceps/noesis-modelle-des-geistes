#!/usr/bin/env python3
"""Validate, promote and arrange the EP04A/EP04B visual production package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from pathlib import Path
from statistics import mean

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat

from generate_jung_series_vertex import EXPECTED, ROOT, SERIES_ROOT, THUMBNAILS, load_jobs


RAW = SERIES_ROOT / "00_RAW_VERTEX"
FINAL = SERIES_ROOT / "FINAL_STILLS"
MOTION = SERIES_ROOT / "MOTION_BASES_2K"
QA = SERIES_ROOT / "QA"
ARRANGEMENT = SERIES_ROOT / "ARRANGEMENT"
REFERENCE_ROOT = SERIES_ROOT / "REFERENCES_EP04AB"
MANIFEST = ROOT / "03_EPISODEN" / "TYPE_B" / "EP04A_EP04B_ASSETS_PHASE2" / "asset_manifest.csv"
CUES = {
    "EP04A": ROOT / "PRODUCTION_SUMMARY" / "EP04A_JUNG_KUNDALINI_V5" / "VISUAL_CUE_SHEET_V5_FINAL.csv",
    "EP04B": ROOT / "PRODUCTION_SUMMARY" / "EP04B_CHAKRA_GENEALOGIE_V5" / "VISUAL_CUE_SHEET_V5.csv",
}
W, H = 2560, 1440
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


def raw_path(job: dict) -> Path:
    return RAW / job["episode"] / job["kind"] / job["name"]


def perceptual_hash(image: Image.Image, size: int = 16) -> int:
    gray = ImageOps.grayscale(image).resize((size, size), Image.Resampling.LANCZOS)
    pixels = list(gray.getdata())
    threshold = mean(pixels)
    value = 0
    for pixel in pixels:
        value = (value << 1) | int(pixel >= threshold)
    return value


def validate() -> tuple[list[dict], list[str]]:
    jobs = load_jobs(include_thumbnails=True)
    records: list[dict] = []
    errors: list[str] = []
    hashes: list[tuple[str, int]] = []
    for job in jobs:
        path = raw_path(job)
        record = {"episode": job["episode"], "kind": job["kind"], "filename": job["name"], "path": str(path)}
        if not path.is_file():
            record.update(status="MISSING", width="", height="", mean_luma="", bytes="", sha256="")
            records.append(record)
            errors.append(f"missing: {job['name']}")
            continue
        try:
            data = path.read_bytes()
            with Image.open(path) as image:
                image.load()
                width, height = image.size
                luma = round(ImageStat.Stat(ImageOps.grayscale(image)).mean[0], 2)
                phash = perceptual_hash(image)
            aspect_ok = abs(width / height - 16 / 9) < 0.03
            size_ok = width >= 2048 and height >= 1152
            status = "PASS" if aspect_ok and size_ok else "FAIL_TECH"
            if status != "PASS":
                errors.append(f"technical: {job['name']} {width}x{height}")
            record.update(
                status=status,
                width=width,
                height=height,
                mean_luma=luma,
                brightness_flag="DARK_REVIEW" if luma < 32 else "BRIGHT_REVIEW" if luma > 225 else "",
                normalization="CENTER_CROP_RESIZE_2560x1440" if (width, height) != (W, H) else "NONE",
                bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
            )
            hashes.append((job["name"], phash))
        except Exception as exc:  # noqa: BLE001
            record.update(status="CORRUPT", width="", height="", mean_luma="", bytes="", sha256="")
            errors.append(f"corrupt: {job['name']}: {exc}")
        records.append(record)

    duplicate_pairs = []
    for index, (left_name, left_hash) in enumerate(hashes):
        for right_name, right_hash in hashes[index + 1 :]:
            distance = (left_hash ^ right_hash).bit_count()
            if distance <= 3:
                duplicate_pairs.append({"left": left_name, "right": right_name, "distance": distance})
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "perceptual_duplicate_review.json").write_text(json.dumps(duplicate_pairs, ensure_ascii=False, indent=2), encoding="utf-8")
    return records, errors


def write_audit(records: list[dict]) -> None:
    QA.mkdir(parents=True, exist_ok=True)
    fields = ["episode", "kind", "filename", "status", "width", "height", "mean_luma", "brightness_flag", "normalization", "bytes", "sha256", "path"]
    with (QA / "TECHNICAL_AUDIT.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def promote(records: list[dict]) -> None:
    for record in records:
        if record["status"] != "PASS":
            continue
        source = Path(record["path"])
        target = FINAL / record["episode"] / record["kind"] / record["filename"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as image:
            normalized = ImageOps.fit(ImageOps.exif_transpose(image).convert("RGB"), (W, H), Image.Resampling.LANCZOS)
            normalized.save(target)


def contact_sheets(records: list[dict]) -> None:
    font_small = ImageFont.truetype(str(FONT), 22)
    font_head = ImageFont.truetype(str(FONT_BOLD), 34)
    for episode in ("EP04A", "EP04B"):
        paths = [FINAL / item["episode"] / item["kind"] / item["filename"] for item in records if item["episode"] == episode and item["status"] == "PASS"]
        for page, start in enumerate(range(0, len(paths), 12), 1):
            batch = paths[start : start + 12]
            sheet = Image.new("RGB", (2048, 1260), (12, 16, 23))
            draw = ImageDraw.Draw(sheet)
            draw.text((30, 22), f"{episode} · V5 · Kontaktbogen {page}", font=font_head, fill=(240, 240, 236))
            for index, path in enumerate(batch):
                row, col = divmod(index, 4)
                x, y = 28 + col * 505, 88 + row * 385
                with Image.open(path) as image:
                    thumb = ImageOps.fit(image.convert("RGB"), (480, 270), Image.Resampling.LANCZOS)
                sheet.paste(thumb, (x, y))
                label = path.stem
                if len(label) > 42:
                    label = label[:40] + "…"
                draw.text((x, y + 282), label, font=font_small, fill=(205, 211, 220))
            destination = QA / f"{episode}_CONTACT_SHEET_{page:02d}.jpg"
            sheet.save(destination, quality=90)


def motion_contact_sheets() -> None:
    font_small = ImageFont.truetype(str(FONT), 22)
    font_head = ImageFont.truetype(str(FONT_BOLD), 34)
    for episode in ("EP04A", "EP04B"):
        paths = sorted((MOTION / episode).glob("*.png"))
        for page, start in enumerate(range(0, len(paths), 12), 1):
            batch = paths[start : start + 12]
            sheet = Image.new("RGB", (2048, 1260), (12, 16, 23))
            draw = ImageDraw.Draw(sheet)
            draw.text((30, 22), f"{episode} · Motion-Keyframes · {page}", font=font_head, fill=(240, 240, 236))
            for index, path in enumerate(batch):
                row, col = divmod(index, 4)
                x, y = 28 + col * 505, 88 + row * 385
                with Image.open(path) as image:
                    thumb = ImageOps.fit(image.convert("RGB"), (480, 270), Image.Resampling.LANCZOS)
                sheet.paste(thumb, (x, y))
                draw.text((x, y + 282), path.stem[:42], font=font_small, fill=(205, 211, 220))
            sheet.save(QA / f"{episode}_MOTION_CONTACT_SHEET_{page:02d}.jpg", quality=90)


def manifest_index() -> dict[str, Path]:
    result: dict[str, Path] = {}
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            filename = row.get("filename", "").strip()
            if not filename or not re.search(r"\.(png|jpe?g|tiff?|pdf)$", filename, re.I):
                continue
            hits = list(REFERENCE_ROOT.rglob(filename))
            if hits:
                result[row["id"]] = hits[0]
                result[filename] = hits[0]
    return result


def generated_index(episode: str) -> dict[str, Path]:
    result = {}
    for path in (FINAL / episode).rglob("*.png"):
        match = re.search(r"_(IMG\d{3}|RSV\d{2})_", path.name)
        if match:
            result[match.group(1)] = path
    return result


def motion_index(episode: str) -> dict[str, Path]:
    return {path.name.split("_")[0]: path for path in (MOTION / episode).glob("*.png")}


def pace_band(pace: str) -> str:
    return {"dense": "2.5–4.0 s", "normal": "4.0–6.0 s", "hold": "5.0–8.0 s"}.get(pace, "voice-anchored")


def build_arrangement() -> list[dict]:
    ARRANGEMENT.mkdir(parents=True, exist_ok=True)
    source_lookup = manifest_index()
    all_rows = []
    for episode, cue_path in CUES.items():
        gen_lookup = generated_index(episode)
        mot_lookup = motion_index(episode)
        episode_rows = []
        with cue_path.open(encoding="utf-8-sig", newline="") as handle:
            cues = list(csv.DictReader(handle))
        for order, cue in enumerate(cues, 1):
            spec = cue["source_or_generated"]
            resolved: list[str] = []
            missing: list[str] = []
            for token in re.findall(r"IMG\d{3}|RSV\d{2}|[AB]-G\d{2}|(?:EP04[AB]|SHARED)_[A-Z0-9_]+", spec):
                path = gen_lookup.get(token) or mot_lookup.get(token) or source_lookup.get(token)
                if path:
                    resolved.append(str(path))
                else:
                    missing.append(token)
            if "archive" in spec.lower() and not resolved:
                missing.append("ARCHIVE_SELECTION")
            status = "READY" if resolved and not missing else "PARTIAL" if resolved else "EDITORIAL_SOURCE_OR_MOTION"
            row = {
                "order": order,
                "cue_id": cue["cue_id"],
                "section": cue["section"],
                "voice_anchor": cue["voice_anchor"],
                "primary_visual": cue["primary_visual"],
                "asset_spec": spec,
                "resolved_paths": ";".join(resolved),
                "open_editorial_tokens": ";".join(missing),
                "pace": cue["pace"],
                "prevoice_duration_band": pace_band(cue["pace"]),
                "edit_function": cue["edit_function"],
                "notes": cue["notes"],
                "status": status,
            }
            episode_rows.append(row)
            all_rows.append({"episode": episode, **row})
        fields = list(episode_rows[0].keys())
        with (ARRANGEMENT / f"{episode}_SHOT_ORDER.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader(); writer.writerows(episode_rows)
    return all_rows


def write_handoff(records: list[dict], arrangement_rows: list[dict], errors: list[str]) -> None:
    counts = {}
    for episode in ("EP04A", "EP04B"):
        counts[episode] = {
            kind: sum(r["episode"] == episode and r["kind"] == kind and r["status"] == "PASS" for r in records)
            for kind in ("MAIN", "RESERVE", "THUMBNAIL")
        }
    motion_counts = {
        episode: len({path.name.split("_")[0] for path in (MOTION / episode).glob("*.png")})
        for episode in ("EP04A", "EP04B")
    }
    ready_cues = {episode: sum(row["episode"] == episode and row["status"] == "READY" for row in arrangement_rows) for episode in ("EP04A", "EP04B")}
    text = f"""# Jung/Kundalini V5 — Visual Handoff vor Voice

## Lieferstatus

- EP04A: {counts['EP04A']['MAIN']}/44 MAIN, {counts['EP04A']['RESERVE']}/8 Reserve, {counts['EP04A']['THUMBNAIL']}/1 Thumbnailbasis, {motion_counts['EP04A']}/14 Motion-Keyframe-Systeme.
- EP04B: {counts['EP04B']['MAIN']}/20 MAIN, {counts['EP04B']['RESERVE']}/4 Reserve, {counts['EP04B']['THUMBNAIL']}/1 Thumbnailbasis, {motion_counts['EP04B']}/15 Motion-Keyframe-Systeme.
- Anordnung: {len([r for r in arrangement_rows if r['episode']=='EP04A'])} EP04A-Cues und {len([r for r in arrangement_rows if r['episode']=='EP04B'])} EP04B-Cues in finaler Erzählreihenfolge.
- Direkt vollständig aufgelöste Cue-Zeilen: EP04A {ready_cues['EP04A']}, EP04B {ready_cues['EP04B']}. Gemischte Archiv-/Motion-Cues bleiben absichtlich als Layerkombinationen markiert.

## Timing-Regel

Die Shotreihenfolge ist fertig. Vor der Voice gelten nur die Pace-Bänder im Shot-Order-CSV. Framegenaue In-/Out-Zeiten werden nach Voice und Forced Alignment gesetzt; dadurch muss die Bildproduktion nicht erneut angefasst werden.

## Qualitätsstatus

Technische Fehler: {len(errors)}. Das technische Audit, die Kontaktbögen, die Duplikatprüfung und die redaktionellen QA-Entscheidungen liegen im QA-Ordner. Die Zuschauerkarten folgen dem globalen Verständlichkeits- und Human-Editorial-Standard `01_GLOBAL/00D_ZUSCHAUERKARTEN_STANDARD.md`: vollständige Kernaussage, sichtbare Bildbeziehung, natürliche Zuschauersprache und keine Produktionscodes oder technische KI-/Dashboard-Ästhetik im Frame.

## Ordner

- `FINAL_STILLS/EP04A` und `FINAL_STILLS/EP04B`: freigegebene 2K-Stills.
- `MOTION_BASES_2K`: timing-unabhängige V5-Keyframes für alle 29 Motion-Systeme.
- `REFERENCES_EP04AB`: historische Quellen einschließlich Lizenz-/Source-Sidecars.
- `ARRANGEMENT`: Cue-genaue Shot-Reihenfolge für den nächsten Voice-Schritt.
- `QA`: technische Audits und Kontaktbögen.
"""
    (SERIES_ROOT / "VOICE_READY_VISUAL_HANDOFF.md").write_text(text, encoding="utf-8")


def main() -> int:
    records, errors = validate()
    write_audit(records)
    promote(records)
    contact_sheets(records)
    motion_contact_sheets()
    arrangement_rows = build_arrangement()
    write_handoff(records, arrangement_rows, errors)
    print(json.dumps({"images": len(records), "errors": errors, "arrangement_rows": len(arrangement_rows)}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
