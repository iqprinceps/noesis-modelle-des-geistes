#!/usr/bin/env python3
"""Prepare, assemble, and align the selected EP02_EN voice master.

Generation itself is executed by the shared encrypted-profile ElevenLabs CLI.
This file never reads or prints a secret.

The two candidates are short, identical-excerpt auditions only. After selection,
exactly one complete batch is prepared and rendered.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import uuid
from difflib import SequenceMatcher
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
SCRIPT = EP / "01_SCRIPT" / "VOICE_SCRIPT_EN.txt"
VOICE = EP / "04_VOICE"
SOURCE = VOICE / "SOURCE"
SHARED_CLI = Path.home() / "Documents" / "Codex" / "NOESIS Channel" / "tools" / "elevenlabs_cli.py"
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"

CANDIDATES = {
    "A": {"stability": 0.58, "similarity_boost": 0.80, "style": 0.08, "speed": 1.06, "seed": 260802},
    "B": {"stability": 0.66, "similarity_boost": 0.82, "style": 0.04, "speed": 1.03, "seed": 260822},
}


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, capture_output=capture, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-5000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], True).strip())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def script_paragraphs() -> list[str]:
    return [p.strip() for p in re.split(r"\r?\n\s*\r?\n", SCRIPT.read_text(encoding="utf-8")) if p.strip()]


def chunks(max_chars: int = 1200) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    size = 0
    for p in script_paragraphs():
        extra = len(p) + (2 if current else 0)
        if current and size + extra > max_chars:
            result.append("\n\n".join(current))
            current, size = [], 0
        current.append(p)
        size += extra
    if current:
        result.append("\n\n".join(current))
    return result


def prepare() -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    parts = chunks()
    stems = []
    for i, text in enumerate(parts, 1):
        stem_id = f"GW_EN_TAKE_{i:02d}"
        path = SOURCE / f"{stem_id}.txt"
        path.write_text(text + "\n", encoding="utf-8")
        stems.append({"id": stem_id, "text_file": str(path.resolve())})

    reconstructed = "\n\n".join(pathlib_text(Path(x["text_file"])) for x in stems)
    expected = "\n\n".join(script_paragraphs())
    if reconstructed != expected:
        raise RuntimeError("voice chunks no longer reconstruct canonical script")

    audition = {
        "rule": "two short auditions with identical excerpt; one full master only",
        "excerpt": str((VOICE / "pronunciation_test.txt").resolve()),
        "candidates": CANDIDATES,
    }
    (VOICE / "audition_manifest.json").write_text(json.dumps(audition, indent=2) + "\n", encoding="utf-8")
    print(f"prepared {len(parts)} stems, {len(expected.split())} words")


def prepare_master(name: str) -> None:
    settings = CANDIDATES[name]
    voice_settings = {k: v for k, v in settings.items() if k != "seed"}
    stems = [{"id": p.stem, "text_file": str(p.resolve())} for p in sorted(SOURCE.glob("GW_EN_TAKE_*.txt"))]
    if not stems:
        raise RuntimeError("run prepare first")
    out = VOICE / "MASTER" / "raw_stems"
    out.mkdir(parents=True, exist_ok=True)
    batch = {
        "episode": "EP02_EN",
        "selected_from_audition": name,
        "voice": VOICE_ID,
        "voice_name": "George",
        "model": "eleven_multilingual_v2",
        "settings": {**voice_settings, "use_speaker_boost": True},
        "seed": settings["seed"],
        "output_format": "mp3_44100_128",
        "output_dir": str(out.resolve()),
        "stems": stems,
    }
    (VOICE / "voice_batch_master.json").write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
    print(f"selected candidate {name}; prepared one complete master batch")


def pathlib_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def loudness(path: Path) -> dict:
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "loudnorm=I=-18:TP=-2:LRA=7:print_format=json", "-f", "null", "-"], True)
    match = re.findall(r'\{\s*"input_i".*?\}', out, re.S)
    return json.loads(match[-1]) if match else {}


def assemble() -> Path:
    batch = json.loads((VOICE / "voice_batch_master.json").read_text(encoding="utf-8"))
    name = batch["selected_from_audition"]
    cdir = VOICE / "MASTER"
    final = cdir / "normalized_stems"
    master_dir = cdir
    final.mkdir(parents=True, exist_ok=True)
    master_dir.mkdir(parents=True, exist_ok=True)
    concat: list[str] = []
    report: list[dict] = []
    cursor = 0.0
    for i, stem in enumerate(batch["stems"], 1):
        src = cdir / "raw_stems" / f"{stem['id']}.mp3"
        if not src.is_file():
            raise FileNotFoundError(src)
        dst = final / f"{stem['id']}.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-af", "loudnorm=I=-18:TP=-2:LRA=7", "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(dst)])
        sec = duration(dst)
        concat.append(f"file '{dst.as_posix()}'")
        report.append({"id": stem["id"], "start": round(cursor, 3), "end": round(cursor + sec, 3), "duration": round(sec, 3), "sha256": sha256(dst)})
        cursor += sec
        if i < len(batch["stems"]):
            gap_sec = 0.42
            gap = master_dir / f"gap_{i:02d}.wav"
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono:d={gap_sec}", "-c:a", "pcm_s24le", str(gap)])
            concat.append(f"file '{gap.as_posix()}'")
            cursor += gap_sec
    concat_path = master_dir / "concat.txt"
    concat_path.write_text("\n".join(concat) + "\n", encoding="utf-8")
    master = master_dir / "GW_EN_VO_MASTER.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_path), "-c:a", "pcm_s24le", str(master)])
    data = {"candidate": name, "voice": "George", "model": batch["model"], "settings": batch["settings"], "duration": round(duration(master), 3), "loudness": loudness(master), "sha256": sha256(master), "stems": report}
    (master_dir / "stem_report.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(master)
    return master


def load_key() -> str:
    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", SHARED_CLI)
    if spec is None or spec.loader is None:
        raise RuntimeError("shared ElevenLabs CLI unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module._load_key())


def multipart(audio: Path, text: str) -> tuple[bytes, str]:
    boundary = "----GWEN" + uuid.uuid4().hex
    parts = [f"--{boundary}\r\n".encode(), b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n", f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(), b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode()]
    return b"".join(parts), boundary


def align() -> Path:
    master = VOICE / "MASTER" / "GW_EN_VO_MASTER.wav"
    batch = json.loads((VOICE / "voice_batch_master.json").read_text(encoding="utf-8"))
    name = batch["selected_from_audition"]
    text = "\n\n".join(script_paragraphs())
    body, boundary = multipart(master, text)
    req = Request("https://api.elevenlabs.io/v1/forced-alignment", data=body, headers={"xi-api-key": load_key(), "Content-Type": f"multipart/form-data; boundary={boundary}", "Accept": "application/json"}, method="POST")
    with urlopen(req, timeout=900) as response:
        data = json.loads(response.read().decode())
    data.update({"episode": "EP02_EN", "candidate": name, "source_text": text, "audio": str(master.resolve()), "audio_sha256": sha256(master)})
    path = VOICE / "ALIGNMENT" / "GW_EN_VO_ALIGNMENT.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["prepare", "prepare-master", "assemble", "align"])
    ap.add_argument("--candidate", choices=["A", "B"])
    args = ap.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "prepare-master":
        if not args.candidate:
            raise SystemExit("--candidate is required")
        prepare_master(args.candidate)
    elif args.action == "assemble":
        assemble()
    elif args.action == "align":
        align()


if __name__ == "__main__":
    main()
