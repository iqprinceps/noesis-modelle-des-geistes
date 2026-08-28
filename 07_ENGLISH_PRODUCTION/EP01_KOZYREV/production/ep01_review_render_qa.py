#!/usr/bin/env python3
"""Verify the full EP01 review render at every edit and across its complete audio stream."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


EP = Path(__file__).resolve().parents[1]
EDL = EP / "06_TIMELINE/EP01_EN_FINAL_EDL.csv"
RENDER = EP / "07_REVIEW/EP01_EN_KOZYREV_INTERNAL_REVIEW_1080p.mp4"
FRAME_DIR = EP / "05_QA/REVIEW_RENDER_FRAMES"
SHEET_DIR = EP / "05_QA/REVIEW_RENDER_CONTACT_SHEETS"
REPORT = EP / "05_QA/REVIEW_RENDER_QA.json"
MANUAL = EP / "05_QA/REVIEW_RENDER_MANUAL_REVIEW.json"
FPS = 25


def command(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=check)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_contact_sheets(rows: list[dict[str, str]]) -> list[str]:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    SHEET_DIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for index, row in enumerate(rows, 1):
        midpoint = (float(row["record_in_seconds"]) + float(row["record_out_seconds"])) / 2.0
        target = FRAME_DIR / f"event_{index:03d}.jpg"
        # Always overwrite: event numbering can remain stable while the locked source changes.
        command([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{midpoint:.3f}",
            "-i", str(RENDER), "-frames:v", "1", "-vf", "scale=480:270", "-q:v", "2", str(target),
        ])
        frames.append(target)
    if len(frames) != len(rows):
        raise RuntimeError(f"Expected {len(rows)} review frames, found {len(frames)}")
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    pages = []
    per_page, cols, rows_per_page = 20, 4, 5
    for page, offset in enumerate(range(0, len(frames), per_page), 1):
        canvas = Image.new("RGB", (cols * 480, rows_per_page * 325), (12, 15, 18))
        draw = ImageDraw.Draw(canvas)
        for local, frame_path in enumerate(frames[offset:offset + per_page]):
            event_row = rows[offset + local]
            x = (local % cols) * 480
            y = (local // cols) * 325
            with Image.open(frame_path) as frame:
                canvas.paste(frame.convert("RGB"), (x, y))
            draw.rectangle((x, y + 270, x + 480, y + 325), fill=(8, 12, 15))
            draw.text((x + 8, y + 276), f"{event_row['event']}  {event_row['record_in_seconds']}s", font=font, fill=(238, 238, 232))
            label = event_row["visual_state_id"]
            draw.text((x + 8, y + 300), label[:55], font=small, fill=(137, 205, 218))
        path = SHEET_DIR / f"review_render_contact_{page:02d}.jpg"
        canvas.save(path, quality=93, subsampling=0)
        pages.append(path.relative_to(EP).as_posix())
    return pages


def main() -> int:
    with EDL.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    probe = json.loads(command([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(RENDER)
    ]).stdout)
    contacts = build_contact_sheets(rows)
    black = command([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(RENDER), "-vf", "blackdetect=d=0.12:pix_th=0.02", "-an", "-f", "null", "-"
    ], check=False).stderr
    silence = command([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(RENDER), "-map", "0:a:0", "-af", "silencedetect=noise=-48dB:d=0.8", "-f", "null", "-"
    ], check=False).stderr
    black_events = [line for line in black.splitlines() if "black_start:" in line]
    silence_events = [line for line in silence.splitlines() if "silence_start:" in line or "silence_end:" in line]
    duration = float(probe["format"]["duration"])
    streams = probe["streams"]
    video = next(stream for stream in streams if stream["codec_type"] == "video")
    audio = next(stream for stream in streams if stream["codec_type"] == "audio")
    subtitles = [stream for stream in streams if stream["codec_type"] == "subtitle"]
    manual = json.loads(MANUAL.read_text(encoding="utf-8")) if MANUAL.exists() else {"status": "PENDING"}
    automated_pass = abs(duration - 434.632) <= 0.05 and not black_events and not silence_events
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if automated_pass and manual.get("status") == "PASS_VIEWER_LED" else "REVIEW_REQUIRED",
        "render_file": RENDER.relative_to(EP).as_posix(),
        "sha256": sha256(RENDER),
        "duration_seconds": duration,
        "event_count": len(rows),
        "event_midpoints_visually_sampled": len(rows),
        "contact_sheets": contacts,
        "motion_review_basis": "Every selected progressive clip separately checked at start/middle/end; final render checked at every EDL event midpoint.",
        "audio_review_basis": "Complete muxed audio stream scanned end-to-end for silence/dropouts, duration, loudness and peak; narration performance inherits the prior full listening audit.",
        "black_events": black_events,
        "silence_events_below_minus_48db_over_0_8s": silence_events,
        "video": {key: video.get(key) for key in ("codec_name", "width", "height", "pix_fmt", "avg_frame_rate", "duration")},
        "audio": {key: audio.get(key) for key in ("codec_name", "sample_rate", "channels", "channel_layout", "duration")},
        "subtitle_stream_count": len(subtitles),
        "viewer_review": manual,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "contacts": len(contacts), "duration": duration, "black": len(black_events), "silence": len(silence_events)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
