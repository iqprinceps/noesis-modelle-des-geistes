#!/usr/bin/env python3
"""Build normalized VO masters + ElevenLabs forced alignment for EP06-EP08.

Usage from repository root:
    python3 tools/schlafparalyse_voice.py EP06 master
    python3 tools/schlafparalyse_voice.py EP06 align
    python3 tools/schlafparalyse_voice.py EP06 all

Prerequisites:
1) python3 tools/prepare_schlafparalyse_production_inputs.py
2) elevenlabs_cli.py batch --batch-file <episode>/voice/voice_batch_v4.json --execute
3) ffmpeg + ffprobe on PATH
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
EP_MAP = {
    "EP06": ROOT / "PRODUCTION_SUMMARY" / "EP06_SCHLAFPARALYSE_V4",
    "EP07": ROOT / "PRODUCTION_SUMMARY" / "EP07_SCHLAFPARALYSE_V4",
    "EP08": ROOT / "PRODUCTION_SUMMARY" / "EP08_SCHLAFPARALYSE_V4",
}
PRE, GAP, TAIL = 0.35, 0.65, 2.2


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-6000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], True).strip())


def loudness(path: Path, integrated: float = -18.0, true_peak: float = -2.0) -> dict:
    out = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", f"loudnorm=I={integrated}:TP={true_peak}:LRA=7:print_format=json",
        "-f", "null", "-",
    ], True)
    matches = re.findall(r'\{\s*"input_i".*?\}', out, re.S)
    if not matches:
        raise RuntimeError("ffmpeg loudnorm analysis did not return JSON")
    return json.loads(matches[-1])


def normalize(src: Path, dst: Path, integrated: float = -18.0, true_peak: float = -2.0) -> None:
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
        "-af", filt, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(dst),
    ])


def silence(path: Path, seconds: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
        "-i", f"anullsrc=r=48000:cl=mono:d={seconds}", "-c:a", "pcm_s24le", str(path),
    ])


def resolve_repo_path(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def paths(ep: str):
    prod = EP_MAP[ep]
    clean = prod / "07_VOICE_SCRIPT_CLEAN_V4.txt"
    batch = prod / "voice" / "voice_batch_v4.json"
    raw = prod / "voice" / "raw_stems"
    mdir = prod / "voice" / "master"
    master = mdir / f"{ep}_SCHLAFPARALYSE_V4_VO_MASTER.wav"
    alignment = prod / "voice" / "alignment" / f"{ep}_SCHLAFPARALYSE_V4_alignment.json"
    return prod, clean, batch, raw, mdir, master, alignment


def build_master(ep: str) -> float:
    prod, clean, batch_path, raw, mdir, master, _ = paths(ep)
    if not batch_path.is_file() or not clean.is_file():
        raise SystemExit("Production inputs missing. Run: python3 tools/prepare_schlafparalyse_production_inputs.py")
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    sdir = mdir / "stems"
    sdir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    report = []

    pre = mdir / "pre.wav"
    silence(pre, PRE)
    lines.append(f"file '{pre.as_posix()}'")

    for i, stem in enumerate(batch["stems"]):
        source_text = resolve_repo_path(stem["text_file"])
        if not source_text.is_file():
            raise SystemExit(f"Text stem missing: {source_text}")
        src = raw / f"{stem['id']}.mp3"
        if not src.is_file():
            raise SystemExit(
                f"Raw voice stem missing: {src}\n"
                f"Generate it with: elevenlabs_cli.py batch --batch-file {batch_path.relative_to(ROOT)} --execute"
            )
        dst = sdir / f"{stem['id']}.wav"
        normalize(src, dst)
        d = duration(dst)
        lines.append(f"file '{dst.as_posix()}'")
        report.append({"id": stem["id"], "duration": round(d, 3)})
        print(f"  {stem['id']:<36} {d:7.2f}s")
        if i < len(batch["stems"]) - 1:
            gap = mdir / f"gap_{i+1:02d}.wav"
            silence(gap, GAP)
            lines.append(f"file '{gap.as_posix()}'")

    tail = mdir / "tail.wav"
    silence(tail, TAIL)
    lines.append(f"file '{tail.as_posix()}'")
    concat = mdir / "concat.txt"
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
        "-safe", "0", "-i", str(concat), "-c:a", "pcm_s24le", str(master),
    ])
    total = duration(master)
    (mdir / "stem_report.json").write_text(json.dumps({
        "episode": ep,
        "duration": round(total, 3),
        "voice": batch["voice"],
        "voice_name": batch.get("voice_name"),
        "settings": batch["settings"],
        "stems": report,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Master: {master.relative_to(ROOT)} — {total:.2f}s")
    return total


def multipart(audio: Path, text: str):
    boundary = "----SPV4" + uuid.uuid4().hex
    parts = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts), boundary


def align(ep: str) -> None:
    _, clean, _, _, _, master, alignment = paths(ep)
    if not master.is_file():
        raise SystemExit(f"Voice master missing: {master}. Run '{ep} master' first.")
    sys.path.insert(0, str(ROOT / "tools"))
    from elevenlabs_cli import _load_key  # type: ignore

    text = clean.read_text(encoding="utf-8").strip()
    body, boundary = multipart(master, text)
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
        "episode": ep,
        "source_text": text,
        "audio": str(master.resolve()),
        "audio_sha256": hashlib.sha256(master.read_bytes()).hexdigest(),
    })
    alignment.parent.mkdir(parents=True, exist_ok=True)
    alignment.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Alignment -> {alignment.relative_to(ROOT)}")


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1].upper() not in EP_MAP:
        print("Usage: python3 tools/schlafparalyse_voice.py EP06|EP07|EP08 [master|align|all]", file=sys.stderr)
        return 2
    ep = sys.argv[1].upper()
    cmd = sys.argv[2].lower() if len(sys.argv) > 2 else "all"
    if cmd not in {"master", "align", "all"}:
        raise SystemExit("command must be master, align or all")
    if cmd in {"master", "all"}:
        build_master(ep)
    if cmd in {"align", "all"}:
        align(ep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
