#!/usr/bin/env python3
"""Build individualized EP04A / EP04B VO masters and forced alignment.

Raw ElevenLabs MP3 stems are generated separately from each episode's
voice_batch.json. This tool normalizes those stems, respects the episode-
specific per-stem pause map, builds a mono PCM24 master and aligns it against
the clean editorial transcript.

Usage:
    python tools/ep04ab_voice.py EP04A all
    python tools/ep04ab_voice.py EP04B all
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

PROFILES = {
    "EP04A": {
        "prod": ROOT / "PRODUCTION_SUMMARY" / "EP04A_JUNG_KUNDALINI_V5",
        "clean": "07_VOICE_SCRIPT_CLEAN_V5.txt",
        "master": "EP04A_JUNG_KUNDALINI_V5_VO_MASTER.wav",
        "alignment": "EP04A_JUNG_KUNDALINI_V5_alignment.json",
    },
    "EP04B": {
        "prod": ROOT / "PRODUCTION_SUMMARY" / "EP04B_CHAKRA_GENEALOGIE_V5",
        "clean": "07_VOICE_SCRIPT_CLEAN_V5.txt",
        "master": "EP04B_CHAKRA_GENEALOGIE_V5_VO_MASTER.wav",
        "alignment": "EP04B_CHAKRA_GENEALOGIE_V5_alignment.json",
    },
}


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-6000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path)
    ], True).strip())


def loudness(path: Path, integrated: float = -18.0, true_peak: float = -2.0) -> dict:
    out = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", f"loudnorm=I={integrated}:TP={true_peak}:LRA=7:print_format=json",
        "-f", "null", "-"
    ], True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', out, re.S)[-1])


def normalize(src: Path, dst: Path, integrated: float = -18.0, true_peak: float = -2.0):
    st = loudness(src, integrated, true_peak)
    dst.parent.mkdir(parents=True, exist_ok=True)
    filt = (
        f"loudnorm=I={integrated}:TP={true_peak}:LRA=7:"
        f"measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
        f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:"
        f"offset={st['target_offset']}:linear=true"
    )
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-af", filt, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(dst)
    ])


def silence(path: Path, seconds: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
        "-i", f"anullsrc=r=48000:cl=mono:d={seconds}", "-c:a", "pcm_s24le", str(path)
    ])


def resolve_repo_path(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def paths(profile: str):
    cfg = PROFILES[profile]
    prod = cfg["prod"]
    batch = prod / "voice" / "voice_batch.json"
    timing = prod / "voice" / "voice_timing.json"
    raw = prod / "voice" / "raw_stems"
    mdir = prod / "voice" / "master"
    clean = prod / cfg["clean"]
    master = mdir / cfg["master"]
    alignment = prod / "voice" / "alignment" / cfg["alignment"]
    return prod, batch, timing, raw, mdir, clean, master, alignment


def build_master(profile: str) -> float:
    prod, batch_path, timing_path, raw, mdir, clean, master, alignment = paths(profile)
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    gaps = timing.get("gaps_after", {})
    pre = float(timing.get("pre_roll_seconds", 0.3))
    tail_s = float(timing.get("tail_seconds", 2.0))

    sdir = mdir / "stems"
    sdir.mkdir(parents=True, exist_ok=True)
    concat_lines: list[str] = []
    report = []
    cursor = 0.0

    pre_file = mdir / "pre.wav"
    silence(pre_file, pre)
    concat_lines.append(f"file '{pre_file.as_posix()}'")
    cursor += pre

    for index, stem in enumerate(batch["stems"]):
        source_text = resolve_repo_path(stem["text_file"])
        if not source_text.is_file():
            raise SystemExit(f"Text stem missing: {source_text}")
        src = raw / f"{stem['id']}.mp3"
        if not src.is_file():
            raise SystemExit(
                f"Raw voice stem missing: {src}\n"
                f"Generate the episode batch first from {batch_path.relative_to(ROOT)}"
            )
        dst = sdir / f"{stem['id']}.wav"
        normalize(src, dst)
        d = duration(dst)
        start = cursor
        end = start + d
        concat_lines.append(f"file '{dst.as_posix()}'")
        row = {
            "id": stem["id"],
            "duration": round(d, 3),
            "start": round(start, 3),
            "end": round(end, 3),
        }
        cursor = end
        if index < len(batch["stems"]) - 1:
            gap_s = float(gaps.get(stem["id"], 0.55))
            row["gap_after"] = gap_s
            gap = mdir / f"gap_{index+1:02d}.wav"
            silence(gap, gap_s)
            concat_lines.append(f"file '{gap.as_posix()}'")
            cursor += gap_s
        report.append(row)
        print(f"  {stem['id']:<36} {d:7.2f}s")

    tail = mdir / "tail.wav"
    silence(tail, tail_s)
    concat_lines.append(f"file '{tail.as_posix()}'")
    cursor += tail_s

    concat = mdir / "concat.txt"
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
        "-safe", "0", "-i", str(concat), "-c:a", "pcm_s24le", str(master)
    ])
    total = duration(master)
    (mdir / "stem_report.json").write_text(json.dumps({
        "episode": profile,
        "duration": round(total, 3),
        "voice": batch["voice"],
        "voice_name": batch.get("voice_name"),
        "model": batch.get("model"),
        "settings": batch["settings"],
        "timing_note": timing.get("note"),
        "stems": report,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{profile} master: {total:.2f}s")
    return total


def multipart(audio: Path, text: str, prefix: str):
    boundary = "----" + prefix + uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), boundary


def align(profile: str):
    prod, batch, timing, raw, mdir, clean, master, alignment = paths(profile)
    if not master.is_file():
        raise SystemExit(f"Voice master missing: {master}")
    sys.path.insert(0, str(ROOT / "tools"))
    from elevenlabs_cli import _load_key  # type: ignore

    text = clean.read_text(encoding="utf-8").strip()
    body, boundary = multipart(master, text, profile)
    req = Request(
        "https://api.elevenlabs.io/v1/forced-alignment",
        data=body,
        headers={
            "xi-api-key": _load_key(),
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=600) as res:
            data = json.loads(res.read().decode())
    except HTTPError as exc:
        raise SystemExit(f"Alignment HTTP {exc.code}: {exc.read().decode(errors='replace')[:800]}")

    data.update({
        "episode": profile,
        "source_text": text,
        "audio": str(master.resolve()),
        "audio_sha256": hashlib.sha256(master.read_bytes()).hexdigest(),
    })
    alignment.parent.mkdir(parents=True, exist_ok=True)
    alignment.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Alignment -> {alignment}")


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1].upper() not in PROFILES:
        raise SystemExit("Usage: python tools/ep04ab_voice.py EP04A|EP04B [master|align|all]")
    profile = sys.argv[1].upper()
    cmd = sys.argv[2].lower() if len(sys.argv) > 2 else "all"
    if cmd in ("master", "all"):
        build_master(profile)
    if cmd in ("align", "all"):
        align(profile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
