#!/usr/bin/env python3
"""Build a resumable full EP01 review render with restrained original score and SFX."""

from __future__ import annotations

import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np


EP = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "tools"))
from smooth_still_motion import ENGINE_VERSION, eased_zoompan_filter  # noqa: E402

EDL = EP / "06_TIMELINE/EP01_EN_FINAL_EDL.csv"
VOICE = EP / "02_VOICE/master/EP01_EN_KOZYREV_VO_MASTER.wav"
SUBTITLES = EP / "06_TIMELINE/EP01_EN_KOZYREV.srt"
REVIEW = EP / "07_REVIEW"
CACHE = REVIEW / "cache/segments"
AUDIO = REVIEW / "audio"
PICTURE = REVIEW / "cache/EP01_EN_KOZYREV_PICTURE_LOCK.mp4"
BED = AUDIO / "EP01_EN_KOZYREV_ORIGINAL_SCORE_SFX_BED.wav"
BED_MARKER = AUDIO / "EP01_EN_KOZYREV_ORIGINAL_SCORE_SFX_BED_V2.ok"
MIX = AUDIO / "EP01_EN_KOZYREV_FINAL_MIX.wav"
FINAL = REVIEW / "EP01_EN_KOZYREV_INTERNAL_REVIEW_1080p.mp4"
REPORT = REVIEW / "EP01_EN_KOZYREV_REVIEW_RENDER_REPORT.json"
SEGMENT_CACHE = REVIEW / "cache/segment_cache.json"
FPS = 25
DURATION = 434.632
W, H = 1920, 1080
MOTION_MODES = {
    "PHYSICAL_CHAMBER", "SUBJECTIVE_MYSTICAL", "PERSON_HISTORY",
    "EVIDENCE_PROCESS", "PHYSICAL_EVIDENCE",
}


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, text=True, capture_output=True)


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_bed() -> None:
    if BED.exists() and BED_MARKER.exists() and abs(BED.stat().st_size - int(DURATION * 48000 * 4 + 44)) < 1000:
        return
    AUDIO.mkdir(parents=True, exist_ok=True)
    rate = 48000
    chunk = rate * 5
    total = round(DURATION * rate)
    rng = np.random.default_rng(9401)
    swells = [0, 18, 55, 78, 117, 150, 198, 235, 251, 300, 339, 366, 399, 412, 422, 434.5]
    metal_hits = [0.46, 3.12, 20.9, 55.7, 89.8, 117.9, 137.5, 198.6, 235.7, 250.9, 259.0, 299.9, 338.7, 347.6, 362.0, 396.3, 412.4, 421.6, 427.4]
    with wave.open(str(BED), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(rate)
        for start in range(0, total, chunk):
            count = min(chunk, total - start)
            t = (start + np.arange(count)) / rate
            # Slow tension envelope; no stock music and no melodic claim-signalling.
            phase = np.interp(t, swells, np.linspace(0.25, 1.0, len(swells)))
            breathe = 0.74 + 0.26 * np.sin(2 * np.pi * t / 19.0) ** 2
            drone_l = (np.sin(2 * np.pi * 46.2 * t) + 0.52 * np.sin(2 * np.pi * 69.3 * t + 0.7)) * 0.0065
            drone_r = (np.sin(2 * np.pi * 46.2 * t + 0.16) + 0.50 * np.sin(2 * np.pi * 70.1 * t + 0.9)) * 0.0065
            air = rng.normal(0.0, 0.00055, (2, count))
            left = drone_l * breathe * (0.75 + 0.25 * phase) + air[0]
            right = drone_r * breathe * (0.75 + 0.25 * phase) + air[1]
            for hit in metal_hits:
                local = t - hit
                mask = (local >= 0) & (local < 1.8)
                if not np.any(mask):
                    continue
                x = local[mask]
                env = np.exp(-3.6 * x)
                tone = (np.sin(2 * np.pi * 612 * x) + 0.45 * np.sin(2 * np.pi * 947 * x)) * env * 0.008
                pulse = np.sin(2 * np.pi * 58 * x) * np.exp(-5.0 * x) * 0.008
                left[mask] += tone + pulse
                right[mask] += tone * 0.83 + pulse
            # A three-second harmonic tail gives the cliffhanger a deliberate landing.
            closing = t - 431.58
            mask = (closing >= 0) & (closing <= 3.0)
            if np.any(mask):
                x = closing[mask]
                env = np.sin(np.pi * x / 3.0) ** 1.35
                tail_l = (np.sin(2 * np.pi * 92.4 * x) + 0.32 * np.sin(2 * np.pi * 184.8 * x)) * env * 0.010
                tail_r = (np.sin(2 * np.pi * 92.4 * x + 0.18) + 0.30 * np.sin(2 * np.pi * 185.6 * x)) * env * 0.010
                left[mask] += tail_l
                right[mask] += tail_r
            stereo = np.column_stack((left, right))
            pcm = np.clip(stereo * 32767, -32768, 32767).astype("<i2")
            out.writeframes(pcm.tobytes())
    BED_MARKER.write_text("viewer-mix-v2 closing tail\n", encoding="utf-8")


def segment_signature(row: dict[str, str], source: Path) -> str:
    moving_still = source.suffix.casefold() != ".mp4" and row.get("semantic_mode") in MOTION_MODES
    payload = {
        "state": row["visual_state_id"],
        "path": row["selected_file_path"],
        "duration": row["duration_seconds"],
        "mtime_ns": source.stat().st_mtime_ns,
        "size": source.stat().st_size,
        "fps": FPS,
        "size_out": [W, H],
        "version": 3,
    }
    if moving_still:
        payload["smooth_motion_engine"] = ENGINE_VERSION
    return digest_text(json.dumps(payload, sort_keys=True))


def render_segment(index: int, row: dict[str, str], source: Path, target: Path) -> Path:
    duration = float(row["duration_seconds"])
    base = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black"
    vf = f"{base},fps={FPS},format=yuv420p"
    if source.suffix.casefold() == ".mp4":
        source_duration = float(json.loads(run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(source)
        ]).stdout)["format"]["duration"])
        pad = max(0.0, duration - source_duration)
        if pad:
            vf += f",tpad=stop_mode=clone:stop_duration={pad:.6f}"
        vf += f",trim=duration={duration:.6f},setpts=PTS-STARTPTS"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-an", "-vf", vf]
    else:
        # Documents, diagrams, maps and choice cards remain perfectly static.
        # Filmic, historical and experiential stills use the shared project-wide
        # 8K + four-subframe motion engine. Direct delivery-size zoompan is
        # prohibited because its integer crop positions visibly judder.
        if row.get("semantic_mode") in MOTION_MODES:
            phase = int(hashlib.sha256(row["visual_state_id"].encode()).hexdigest()[:2], 16) / 255
            x_bias = 0.42 + 0.16 * phase
            y_bias = 0.46 + 0.08 * (1 - phase)
            vf = eased_zoompan_filter(
                duration=duration,
                fps=FPS,
                width=W,
                height=H,
                x_bias=x_bias,
                y_bias=y_bias,
                zoom_amount=0.025,
                background="black",
            )
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-t", f"{duration:.6f}", "-i", str(source), "-an", "-vf", vf]
    cmd += ["-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(target)]
    run(cmd)
    return target


def build_segments(rows: list[dict[str, str]]) -> list[Path]:
    CACHE.mkdir(parents=True, exist_ok=True)
    prior = json.loads(SEGMENT_CACHE.read_text(encoding="utf-8")) if SEGMENT_CACHE.exists() else {}
    updated: dict[str, str] = {}
    outputs: list[Path] = []
    pending: list[tuple[int, dict[str, str], Path, Path]] = []
    for index, row in enumerate(rows, 1):
        source = EP / row["selected_file_path"]
        target = CACHE / f"{index:03d}_{row['visual_state_id']}.mp4"
        signature = segment_signature(row, source)
        key = target.name
        updated[key] = signature
        outputs.append(target)
        if target.exists() and prior.get(key) == signature:
            continue
        pending.append((index, row, source, target))

    if pending:
        workers = min(4, max(1, (os.cpu_count() or 2) // 2 + 1), len(pending))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(render_segment, index, row, source, target): target
                for index, row, source, target in pending
            }
            for future in as_completed(futures):
                rendered = future.result()
                print(f"RENDERED {rendered.name}", flush=True)

    SEGMENT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    SEGMENT_CACHE.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    return outputs


def concat_picture(segments: list[Path]) -> None:
    concat = REVIEW / "cache/concat.txt"
    concat.write_text("\n".join(f"file '{path.as_posix()}'" for path in segments) + "\n", encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(PICTURE)])


def mix_audio() -> None:
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(VOICE), "-i", str(BED),
        "-filter_complex",
        f"[0:a]adeclick=w=55:o=75:a=2:t=2:b=2,agate=threshold=0.0158:ratio=3:range=0.25:attack=8:release=120,deesser=i=0.35:m=0.55:f=0.55[voice];[1:a]volume=0.62,highpass=f=35,lowpass=f=5200[bed];[voice][bed]amix=inputs=2:duration=first:normalize=0,afade=t=in:st=0:d=0.12,alimiter=limit=0.88,loudnorm=I=-14:TP=-1:LRA=7,atrim=duration={DURATION}[mix]",
        "-map", "[mix]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(MIX),
    ])


def mux_final() -> None:
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(PICTURE), "-i", str(MIX), "-i", str(SUBTITLES),
        "-map", "0:v:0", "-map", "1:a:0", "-map", "2:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
        "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-movflags", "+faststart", "-t", f"{DURATION}", str(FINAL),
    ])


def report(selected_segment_count: int) -> None:
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(FINAL)]).stdout)
    loud = subprocess.run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(FINAL), "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"
    ], text=True, capture_output=True, check=False).stderr
    summary = loud[loud.rfind("Summary:"):] if "Summary:" in loud else loud[-2500:]
    data = {
        "file": FINAL.relative_to(EP).as_posix(),
        "duration_target_seconds": DURATION,
        "ffprobe": probe,
        "loudness_summary": summary,
        "score_and_sfx": {
            "origin": "Original procedural project bed; no stock or third-party music",
            "bed_file": BED.relative_to(EP).as_posix(),
            "mix_file": MIX.relative_to(EP).as_posix(),
            "voice_priority": "Narration dominant; restrained low drone and sparse metal transitions",
        },
        "subtitle_stream": SUBTITLES.relative_to(EP).as_posix(),
        "segment_count": selected_segment_count,
        "stale_cache_files_ignored": max(0, len(list(CACHE.glob("*.mp4"))) - selected_segment_count),
        "resumable_cache": SEGMENT_CACHE.relative_to(EP).as_posix(),
    }
    REPORT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    REVIEW.mkdir(parents=True, exist_ok=True)
    with EDL.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    build_bed()
    segments = build_segments(rows)
    concat_picture(segments)
    mix_audio()
    mux_final()
    report(len(segments))
    print(json.dumps({"render": str(FINAL), "events": len(rows), "cache": str(SEGMENT_CACHE)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
