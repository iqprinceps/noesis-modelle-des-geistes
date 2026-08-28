#!/usr/bin/env python3
"""Render EP06 EN picture, adapted project-owned audio and upload master."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
ROOT = EP.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from smooth_still_motion import ENGINE_VERSION, eased_zoompan_filter  # noqa: E402


EDL = EP / "04_EDIT" / "VISUAL_EDL.json"
SEG = EP / "06_RENDER" / "segments"
PICTURE = EP / "06_RENDER" / "EP06_EN_PICTURE_1080P30.mp4"
VOICE = EP / "02_VOICE" / "MASTER" / "EP06_EN_VO_MASTER.wav"
AUDIO = EP / "05_AUDIO"
MIX = AUDIO / "EP06_EN_MIX_MASTER.wav"
MASTER_DIR = EP / "08_MASTER"
MASTER = MASTER_DIR / "EP06_SLEEP_PARALYSIS_02_EN_MASTER_1080P30.mp4"
DE_AUDIO = Path(r"C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes\06_PRODUCTION\EP07_SCHLAFPARALYSE_V4\audio\stems")
FPS = 30
W, H = 1920, 1080


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, capture_output=capture, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], True).strip())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frame_count(path: Path) -> int:
    raw = run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(path)], True)
    match = re.search(r"\d+", raw)
    if not match:
        raise RuntimeError(f"no frame count for {path}: {raw!r}")
    return int(match.group())


def segment_spec() -> list[dict]:
    edl = json.loads(EDL.read_text(encoding="utf-8"))
    shots = edl["shots"]
    expected_total = round(float(edl["voice_duration"]) * FPS)
    result = []
    previous = 0
    for i, shot in enumerate(shots):
        start_frame = previous
        end_frame = round(float(shot["end"]) * FPS) if i < len(shots) - 1 else expected_total
        if end_frame <= start_frame:
            raise RuntimeError(f"zero frame segment {shot['shot_id']}")
        previous = end_frame
        item = dict(shot)
        item.update({"start_frame": start_frame, "end_frame": end_frame, "frames": end_frame - start_frame, "render_duration": (end_frame - start_frame) / FPS})
        result.append(item)
    if previous != expected_total:
        raise RuntimeError(f"unexpected picture frames {previous}")
    return result


def render_one(shot: dict) -> dict:
    SEG.mkdir(parents=True, exist_ok=True)
    out = SEG / f"{shot['shot_id']}.mp4"
    expected_frames = int(shot["frames"])
    if not shot.get("_force") and out.exists() and out.stat().st_size > 10000:
        count = frame_count(out)
        if count == expected_frames:
            return {"shot_id": shot["shot_id"], "status": "reused", "frames": count, "sha256": sha256(out)}
    src = Path(shot["asset_abs"])
    dur = float(shot["render_duration"])
    common = ["-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), "-frames:v", str(expected_frames), "-movflags", "+faststart", str(out)]
    if src.suffix.lower() == ".mp4":
        src_dur = duration(src)
        # Overshoot by one delivery frame before trim so interpolation always
        # supplies the requested final frame without an end-frame freeze.
        factor = (dur + 2 / FPS) / src_dur
        vf = (
            f"setpts={factor:.9f}*PTS,"
            "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
            f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"trim=duration={dur:.9f},setpts=PTS-STARTPTS,format=yuv420p"
        )
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", vf] + common)
    elif shot["treatment"] == "shared 8K supersampled eased motion":
        vf = eased_zoompan_filter(duration=dur, fps=FPS, width=W, height=H, x_bias=float(shot["x_bias"]), y_bias=float(shot["y_bias"]), zoom_amount=float(shot["zoom"]), background="black")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-i", str(src), "-vf", vf] + common)
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS},trim=duration={dur:.9f},setpts=PTS-STARTPTS,format=yuv420p"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-i", str(src), "-vf", vf] + common)
    count = frame_count(out)
    if count != expected_frames:
        raise RuntimeError(f"frame mismatch {shot['shot_id']}: {count} != {expected_frames}")
    return {"shot_id": shot["shot_id"], "status": "rendered", "frames": count, "sha256": sha256(out)}


def render_segments() -> None:
    specs = segment_spec()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(render_one, shot): shot["shot_id"] for shot in specs}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"{result['shot_id']} {result['status']} {result['frames']}f", flush=True)
    results.sort(key=lambda x: x["shot_id"])
    (EP / "06_RENDER" / "SEGMENT_RENDER_MANIFEST.json").write_text(json.dumps({"engine": "shared smooth still motion", "engine_version": ENGINE_VERSION, "fps": FPS, "results": results}, indent=2) + "\n", encoding="utf-8")


def render_clips() -> None:
    specs = [s for s in segment_spec() if s["asset"].lower().endswith(".mp4")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(render_one, specs))
    for result in results:
        print(f"{result['shot_id']} {result['status']} {result['frames']}f")
    (EP / "06_RENDER" / "CLIP_CONVERSION_QA.json").write_text(json.dumps({"method": "motion-compensated 24 fps to 30 fps; two-frame interpolation headroom; no freeze padding", "clips": results}, indent=2) + "\n", encoding="utf-8")


def render_semantic_corrections() -> None:
    changed = {13, *range(16, 40), 41, 53, 81}
    specs = []
    for shot in segment_spec():
        number = int(shot["shot_id"].split("_")[-1])
        if number in changed:
            item = dict(shot); item["_force"] = True; specs.append(item)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(render_one, specs))
    for result in results: print(f"{result['shot_id']} corrected {result['frames']}f")
    (EP / "06_RENDER" / "SEMANTIC_CORRECTION_RENDER.json").write_text(json.dumps({"reason": "final semantic QA: align Fuseli progression, identify named scholars bibliographically, strengthen final media-state callback", "recoverability": "all overwritten files are deterministic derivatives and can be rerendered from the EDL", "results": results}, indent=2) + "\n", encoding="utf-8")


def concat_picture() -> None:
    specs = segment_spec()
    concat = EP / "06_RENDER" / "concat.txt"
    concat.parent.mkdir(parents=True, exist_ok=True)
    concat.write_text("\n".join(f"file '{(SEG / (s['shot_id'] + '.mp4')).as_posix()}'" for s in specs) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(PICTURE)])
    frames = frame_count(PICTURE)
    expected = round(float(json.loads(EDL.read_text(encoding="utf-8"))["voice_duration"]) * FPS)
    if frames != expected:
        raise RuntimeError(f"picture frame count {frames}")
    print(json.dumps({"picture": str(PICTURE), "frames": frames, "duration": duration(PICTURE), "sha256": sha256(PICTURE)}, indent=2))


def mix_audio() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    music = DE_AUDIO / "EP07_MX_MASTER.wav"
    sfx_names = ["EP07_SFX_SALEM_ROOMTONE.wav", "EP07_SFX_PAPER_INK.wav", "EP07_SFX_COURT_MURMUR.wav", "EP07_SFX_MAP_MOTION.wav", "EP07_SFX_MEDIA_HANDOFF.wav"]
    inputs = [VOICE, music] + [DE_AUDIO / x for x in sfx_names]
    target = duration(VOICE)
    delivery = round(float(json.loads(EDL.read_text(encoding="utf-8"))["voice_duration"]) * FPS) / FPS
    ratio = duration(music) / target
    args = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for item in inputs:
        args += ["-i", str(item)]
    filters = [f"[0:a]pan=stereo|c0=c0|c1=c0,atrim=0:{target:.9f},asetpts=PTS-STARTPTS[vo]", f"[1:a]atempo={ratio:.9f},atrim=0:{target:.9f},asetpts=PTS-STARTPTS,volume=2.8[mx]"]
    bed_labels = ["[mx]"]
    for i in range(2, len(inputs)):
        filters.append(f"[{i}:a]atempo={ratio:.9f},atrim=0:{target:.9f},asetpts=PTS-STARTPTS,volume=1.45[s{i}]")
        bed_labels.append(f"[s{i}]")
    filters.append("".join(bed_labels) + f"amix=inputs={len(bed_labels)}:duration=longest:normalize=0[bed]")
    filters.append("[bed][vo]sidechaincompress=threshold=0.020:ratio=6:attack=15:release=450:makeup=1[ducked]")
    filters.append(f"[vo][ducked]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-0.8:LRA=9:linear=true,volume=0.97dB,apad=whole_dur={delivery:.9f},atrim=0:{delivery:.9f}[mix]")
    args += ["-filter_complex", ";".join(filters), "-map", "[mix]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(MIX)]
    run(args)
    manifest = {"source": "project-owned deterministic EP07 music/SFX retimed proportionally to the George forced-aligned English arc", "ratio": ratio, "voice_authority": "George / ElevenLabs JBFqnCBsd6RMkjVDRZzb", "voice": str(VOICE.resolve()), "music": str(music), "sfx": sfx_names, "ducking": {"method": "voice-keyed sidechain compression", "threshold": 0.020, "ratio": 6, "attack_ms": 15, "release_ms": 450}, "delivery_trim_seconds": delivery, "final_calibration_db": 0.97, "duration": duration(MIX), "sha256": sha256(MIX)}
    (AUDIO / "AUDIO_MIX_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def mux_master() -> None:
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    delivery = round(float(json.loads(EDL.read_text(encoding="utf-8"))["voice_duration"]) * FPS) / FPS
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(PICTURE), "-i", str(MIX), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-t", f"{delivery:.9f}", "-movflags", "+faststart", str(MASTER)])
    manifest = {"master": str(MASTER.resolve()), "duration": duration(MASTER), "sha256": sha256(MASTER), "video": "H.264 1920x1080p30 yuv420p", "audio": "AAC 320 kb/s 48 kHz stereo", "voice_authority": "George / ElevenLabs JBFqnCBsd6RMkjVDRZzb / one canonical 6382-character request", "supersedes": ["SUPERSEDED_RYAN/EP06_SLEEP_PARALYSIS_02_EN_MASTER_1080P30_RYAN_SUPERSEDED.mp4", "../02_VOICE/SUPERSEDED_LEAN/EP06_EN_VO_MASTER_GEORGE_LEAN.wav"], "published": False}
    (MASTER_DIR / "MASTER_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "segments"
    if command == "segments": render_segments()
    elif command == "clips": render_clips()
    elif command == "semantic-corrections": render_semantic_corrections()
    elif command == "picture": concat_picture()
    elif command == "audio": mix_audio()
    elif command == "master": mux_master()
    else: raise SystemExit("Usage: render_episode.py [segments|clips|semantic-corrections|picture|audio|master]")


if __name__ == "__main__":
    main()
