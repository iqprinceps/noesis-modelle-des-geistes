#!/usr/bin/env python3
"""EP05 Jung & Pauli V4 — Voice master and forced alignment.

Run from the repository root.

1) Generate raw MP3 stems:
   elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/voice/voice_batch_v4.json --execute
2) Build normalized master + forced alignment:
   python tools/ep05_voice.py all
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
PROD = ROOT / "PRODUCTION_SUMMARY" / "EP05_JUNG_PAULI_V4"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN_V4.txt"
BATCH = PROD / "voice" / "voice_batch_v4.json"
RAW = PROD / "voice" / "raw_stems"
MDIR = PROD / "voice" / "master"
MASTER = MDIR / "EP05_JUNG_PAULI_V4_VO_MASTER.wav"
ALIGNMENT = PROD / "voice" / "alignment" / "EP05_JUNG_PAULI_V4_alignment.json"

PRE, GAP, TAIL = 0.35, 0.65, 2.2


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


def build_master() -> float:
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    sdir = MDIR / "stems"
    sdir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    report = []

    pre = MDIR / "pre.wav"
    silence(pre, PRE)
    lines.append(f"file '{pre.as_posix()}'")

    for i, stem in enumerate(batch["stems"]):
        source_text = resolve_repo_path(stem["text_file"])
        if not source_text.is_file():
            raise SystemExit(f"Text stem missing: {source_text}")
        src = RAW / f"{stem['id']}.mp3"
        if not src.is_file():
            raise SystemExit(
                f"Raw voice stem missing: {src}\n"
                f"Generate it first with elevenlabs_cli.py batch --batch-file {BATCH} --execute"
            )
        dst = sdir / f"{stem['id']}.wav"
        normalize(src, dst)
        d = duration(dst)
        lines.append(f"file '{dst.as_posix()}'")
        report.append({"id": stem["id"], "duration": round(d, 3)})
        print(f"  {stem['id']:<34} {d:7.2f}s")
        if i < len(batch["stems"]) - 1:
            gap = MDIR / f"gap_{i+1:02d}.wav"
            silence(gap, GAP)
            lines.append(f"file '{gap.as_posix()}'")

    tail = MDIR / "tail.wav"
    silence(tail, TAIL)
    lines.append(f"file '{tail.as_posix()}'")

    concat = MDIR / "concat.txt"
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
        "-safe", "0", "-i", str(concat), "-c:a", "pcm_s24le", str(MASTER)
    ])
    total = duration(MASTER)
    (MDIR / "stem_report.json").write_text(json.dumps({
        "duration": round(total, 3),
        "voice": batch["voice"],
        "voice_name": batch.get("voice_name"),
        "settings": batch["settings"],
        "stems": report,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nMaster: {total:.2f}s ({int(total//60)}:{total%60:04.1f})")
    return total


def multipart(audio: Path, text: str):
    boundary = "----EP05" + uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), boundary


def align():
    if not MASTER.is_file():
        raise SystemExit(f"Voice master missing: {MASTER}")
    sys.path.insert(0, str(ROOT / "tools"))
    from elevenlabs_cli import _load_key  # type: ignore

    text = CLEAN.read_text(encoding="utf-8").strip()
    body, boundary = multipart(MASTER, text)
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
        "source_text": text,
        "audio": str(MASTER.resolve()),
        "audio_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
    })
    ALIGNMENT.parent.mkdir(parents=True, exist_ok=True)
    ALIGNMENT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Alignment -> {ALIGNMENT}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("master", "all"):
        build_master()
    if cmd in ("align", "all"):
        align()
