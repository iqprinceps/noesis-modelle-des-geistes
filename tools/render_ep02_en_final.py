#!/usr/bin/env python3
"""Build the restartable EP02_EN picture lock, original score/SFX, and review master."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pathlib
import subprocess
import wave

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
EDL = EP / "05_DELIVERY" / "GW_EN_EDIT_SHOT_LIST.csv"
VOICE = EP / "04_VOICE" / "MASTER" / "GW_EN_VO_MASTER.wav"
SRT = EP / "08_SUBTITLES" / "GW_EN_MASTER.srt"
RENDER = EP / "06_RENDER"
SEGMENTS = RENDER / "CACHE" / "SEGMENTS"
AUDIO = EP / "04_AUDIO"
PICTURE = RENDER / "GW_EN_PICTURE_LOCK_1080P.mp4"
SCORE = AUDIO / "GW_EN_ORIGINAL_SCORE.wav"
SFX = AUDIO / "GW_EN_ORIGINAL_SFX.wav"
MIX = AUDIO / "GW_EN_FINAL_MIX.wav"
VOICE_STEM = AUDIO / "GW_EN_PROCESSED_VOICE_STEM.wav"
BED_STEM = AUDIO / "GW_EN_DUCKED_BED_STEM.wav"
REVIEW = RENDER / "EP02_GATEWAY_EN_REVIEW_MASTER_1080P.mp4"
FPS = 30
W, H = 1920, 1080
MASTER_END = 481.037


def run(command: list[str]) -> None:
    print("RUN", command[0], pathlib.Path(command[-1]).name)
    subprocess.run(command, check=True)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rows() -> list[dict[str, str]]:
    with EDL.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def asset_index() -> dict[str, pathlib.Path]:
    index = {}
    for path in EP.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".mp4", ".mov", ".webm"}:
            index.setdefault(path.name, path)
    return index


def probe_duration(path: pathlib.Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def segment_key(row: dict[str, str], asset: pathlib.Path) -> str:
    payload = json.dumps({
        "asset_sha256": sha256(asset), "duration": row["duration"],
        "shot": row["edit_shot_id"], "fps": FPS, "size": [W, H],
        "render_version": 5,
    }, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def render_segments(force: bool = False) -> list[pathlib.Path]:
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    index = asset_index()
    outputs = []
    for number, row in enumerate(rows(), 1):
        asset = index.get(row["primary_asset"])
        if not asset:
            raise FileNotFoundError(row["primary_asset"])
        duration = float(row["duration"])
        frames = max(1, round(duration * FPS))
        output = SEGMENTS / f"{number:03d}_{segment_key(row, asset)}.mp4"
        outputs.append(output)
        if output.is_file() and output.stat().st_size > 50_000 and not force:
            print("CACHE", output.name)
            continue
        common = [
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
            "-r", str(FPS), "-g", str(FPS * 2), "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(output),
        ]
        if asset.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            reading_asset = (
                asset.name.startswith("GW_EN_DOC")
                or "_CARD_" in asset.name
                or "_MAP_" in asset.name
            )
            if reading_asset:
                # Documents, maps and reading cards retain their complete safe
                # frame.  Camera drift on evidence both harms legibility and can
                # cut the exact words the narration is citing.
                vf = (
                    f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
                    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x080f12,"
                    f"fps={FPS},trim=duration={duration:.6f},setpts=PTS-STARTPTS,format=yuv420p"
                )
            else:
                # zoompan quantises x/y to source pixels.  Pre-scaling to 8K
                # makes those steps quarter-pixel at delivery resolution; the
                # cosine curve also removes abrupt starts and stops.
                progress = f"(0.5-0.5*cos(PI*on/{max(1, frames-1)}))"
                direction = -1 if number % 2 else 1
                if direction > 0:
                    x_expr = f"(iw-iw/zoom)*{progress}"
                else:
                    x_expr = f"(iw-iw/zoom)*(1-{progress})"
                vf = (
                    "scale=7680:4320:force_original_aspect_ratio=increase:flags=lanczos,"
                    "crop=7680:4320,"
                    f"zoompan=z='1.0+0.026*{progress}':x='{x_expr}':"
                    f"y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
                    f"trim=duration={duration:.6f},setpts=PTS-STARTPTS,format=yuv420p"
                )
            command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-i", str(asset), "-vf", vf, "-t", f"{duration:.6f}"] + common
        else:
            source_duration = probe_duration(asset)
            ratio = duration / source_duration
            source_fps = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=avg_frame_rate",
                "-of", "default=noprint_wrappers=1:nokey=1", str(asset),
            ], capture_output=True, text=True, check=True).stdout.strip()
            cadence = (
                "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
                if source_fps in {"24/1", "24000/1001"} else f"fps={FPS},"
            )
            vf = (
                f"setpts={ratio:.9f}*PTS,scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={W}:{H},{cadence}trim=duration={duration:.6f},setpts=PTS-STARTPTS,format=yuv420p"
            )
            command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(asset), "-vf", vf, "-t", f"{duration:.6f}"] + common
        run(command)
    return outputs


def concat_picture(segments: list[pathlib.Path], force: bool = False) -> None:
    if PICTURE.is_file() and PICTURE.stat().st_size > 1_000_000 and not force:
        print("CACHE", PICTURE.name)
        return
    concat = RENDER / "CACHE" / "GW_EN_CONCAT.txt"
    concat.parent.mkdir(parents=True, exist_ok=True)
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in segments) + "\n", encoding="utf-8")
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(PICTURE),
    ])


def write_stereo_wav(path: pathlib.Path, generator) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 48_000
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(sample_rate)
        cursor = 0
        total = round(MASTER_END * sample_rate)
        while cursor < total:
            count = min(sample_rate, total - cursor)
            t = (cursor + np.arange(count, dtype=np.float64)) / sample_rate
            stereo = np.clip(generator(t), -0.98, 0.98)
            out.writeframes((stereo * 32767.0).astype("<i2").tobytes())
            cursor += count


def score_generator(t: np.ndarray) -> np.ndarray:
    centers = np.array([0, 62, 118, 183, 239, 287, 336, 387, 435, 467, MASTER_END], dtype=float)
    roots = np.array([46.25, 55.00, 49.00, 61.74, 51.91, 43.65, 58.27, 55.00, 46.25, 65.41, 55.00])
    # Interpolate only modulation weights.  Fixed oscillators preserve phase
    # continuity across the full episode and avoid loop seams.
    root = np.interp(t, centers, roots)
    breath = 0.72 + 0.28 * np.sin(2 * np.pi * 0.031 * t + 0.4)
    left = (
        0.038 * np.sin(2 * np.pi * 46.25 * t + 0.3)
        + 0.030 * np.sin(2 * np.pi * 55.00 * t + 1.2)
        + 0.022 * np.sin(2 * np.pi * 65.41 * t + 2.1)
        + 0.010 * np.sin(2 * np.pi * (root * 2.0) * t + 0.8)
        + 0.005 * np.sin(2 * np.pi * 733.0 * t + 0.9 * np.sin(2 * np.pi * 0.017 * t))
    ) * breath
    right = (
        0.036 * np.sin(2 * np.pi * 46.25 * t + 0.8)
        + 0.031 * np.sin(2 * np.pi * 55.00 * t + 1.7)
        + 0.021 * np.sin(2 * np.pi * 65.41 * t + 2.6)
        + 0.010 * np.sin(2 * np.pi * (root * 2.0) * t + 1.1)
        + 0.005 * np.sin(2 * np.pi * 827.0 * t + 0.8 * np.sin(2 * np.pi * 0.019 * t))
    ) * breath
    # A very quiet literal 400/410 pair supports, but never masks, the
    # binaural explanation from 141–156 seconds.
    gate = np.clip((t - 140.0) / 2.0, 0, 1) * np.clip((158.0 - t) / 2.0, 0, 1)
    left += gate * 0.006 * np.sin(2 * np.pi * 400.0 * t)
    right += gate * 0.006 * np.sin(2 * np.pi * 410.0 * t)
    return np.column_stack([left, right])


SFX_EVENTS = [10.7, 39.5, 62.6, 99.5, 118.9, 149.1, 183.3, 239.0, 287.0, 303.9, 336.5, 355.8, 386.9, 434.8, 467.4]


def sfx_generator(t: np.ndarray) -> np.ndarray:
    mono = np.zeros_like(t)
    for idx, event in enumerate(SFX_EVENTS):
        dt = t - event
        hit = (dt >= 0) & (dt < 2.2)
        mono[hit] += 0.11 * np.sin(2 * np.pi * (43 + idx % 4 * 7) * dt[hit]) * np.exp(-2.5 * dt[hit])
        pre = (dt >= -0.8) & (dt < 0)
        phase = dt[pre] + 0.8
        mono[pre] += 0.018 * np.sin(2 * np.pi * (520 + idx * 17) * t[pre]) * (phase / 0.8) ** 2
    left = mono + 0.004 * np.sin(2 * np.pi * 121.0 * t) * np.clip((t - 183) / 1.5, 0, 1) * np.clip((205 - t) / 1.5, 0, 1)
    right = mono + 0.004 * np.sin(2 * np.pi * 129.0 * t) * np.clip((t - 183) / 1.5, 0, 1) * np.clip((205 - t) / 1.5, 0, 1)
    return np.column_stack([left, right])


def build_audio(force: bool = False) -> None:
    if force or not SCORE.is_file():
        print("BUILD", SCORE.name)
        write_stereo_wav(SCORE, score_generator)
    if force or not SFX.is_file():
        print("BUILD", SFX.name)
        write_stereo_wav(SFX, sfx_generator)
    if MIX.is_file() and VOICE_STEM.is_file() and BED_STEM.is_file() and MIX.stat().st_size > 1_000_000 and not force:
        print("CACHE", MIX.name)
        return
    # Keep explicit stems so narration-to-bed level can be measured directly.
    # This also avoids the invalid inference that a filtered/loudness-normalized
    # sum can be regressed against the unfiltered voice master sample-for-sample.
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(VOICE),
        "-af", "highpass=f=70,lowpass=f=13000,pan=stereo|c0=c0|c1=c0",
        "-ar", "48000", "-c:a", "pcm_s24le", str(VOICE_STEM),
    ])
    bed_graph = (
        "[0:a]pan=stereo|c0=c0|c1=c0,asplit=2[scm][scs];"
        "[1:a]volume=1.6[bed];[bed][scm]sidechaincompress=threshold=0.030:ratio=3:attack=10:release=520[duckm];"
        "[2:a]volume=0.40[fx];[fx][scs]sidechaincompress=threshold=0.030:ratio=3:attack=8:release=300[ducks];"
        "[duckm][ducks]amix=inputs=2:normalize=0,alimiter=limit=0.80[a]"
    )
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(VOICE), "-i", str(SCORE), "-i", str(SFX),
        "-filter_complex", bed_graph, "-map", "[a]", "-ar", "48000", "-c:a", "pcm_s24le", str(BED_STEM),
    ])
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(VOICE_STEM), "-i", str(BED_STEM),
        "-filter_complex", "[0:a][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.92,loudnorm=I=-16:TP=-1.2:LRA=7[a]",
        "-map", "[a]", "-ar", "48000", "-c:a", "pcm_s24le", str(MIX),
    ])


def build_review(force: bool = False) -> None:
    if REVIEW.is_file() and REVIEW.stat().st_size > 1_000_000 and not force:
        print("CACHE", REVIEW.name)
        return
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(PICTURE), "-i", str(MIX), "-i", str(SRT),
        "-map", "0:v:0", "-map", "1:a:0", "-map", "2:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
        "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-metadata", "title=The Gateway Process",
        "-t", f"{MASTER_END:.3f}", "-movflags", "+faststart", str(REVIEW),
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--force-picture", action="store_true")
    parser.add_argument("--force-mix", action="store_true")
    parser.add_argument("--force-review", action="store_true")
    parser.add_argument("--audio-only", action="store_true")
    args = parser.parse_args()
    RENDER.mkdir(parents=True, exist_ok=True)
    picture_force = args.force or args.force_picture
    if not args.audio_only:
        segments = render_segments(picture_force)
        concat_picture(segments, picture_force)
    build_audio(args.force or args.force_mix)
    if not args.audio_only:
        build_review(args.force or args.force_review or picture_force)
    print(REVIEW)


if __name__ == "__main__":
    main()
