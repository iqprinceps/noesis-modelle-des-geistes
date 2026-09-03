#!/usr/bin/env python3
"""Prepare, assemble, align and independently QA the EP13_EN voice.

Adapted from tools/produce_ep05_en_voice.py, which produced the published EP05
master. Same narrator, same delivery profile, same four stages: stems, assembly
with loudness normalisation, forced alignment, and an independent Scribe pass
that compares what the model actually said against the canonical script.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import uuid
from difflib import SequenceMatcher
from pathlib import Path
from urllib.request import Request, urlopen

from elevenlabs.client import ElevenLabs


ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01"
SCRIPT = EP / "01_SCRIPT" / "VOICE_SCRIPT_EN.txt"
VOICE = EP / "02_VOICE"
SOURCE = VOICE / "SOURCE"
MASTER = VOICE / "MASTER"
RAW = MASTER / "raw_stems"
NORM = MASTER / "normalized_stems"
ALIGN = VOICE / "ALIGNMENT" / "EP13_EN_VO_ALIGNMENT.json"
SHARED_CLI = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools\elevenlabs_cli.py")
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
SETTINGS = {"stability": 0.61, "similarity_boost": 0.82, "style": 0.06, "speed": 1.0, "use_speaker_boost": True}
SEED = 260827


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, capture_output=capture, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-5000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], True).strip())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paragraphs() -> list[str]:
    return [p.strip() for p in re.split(r"\r?\n\s*\r?\n", SCRIPT.read_text(encoding="utf-8")) if p.strip()]


def chunks(max_chars: int = 1120) -> list[str]:
    result, current, size = [], [], 0
    for p in paragraphs():
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
    RAW.mkdir(parents=True, exist_ok=True)
    stems = []
    for i, text in enumerate(chunks(), 1):
        stem_id = f"EP13_EN_TAKE_{i:02d}"
        path = SOURCE / f"{stem_id}.txt"
        path.write_text(text + "\n", encoding="utf-8")
        stems.append({"id": stem_id, "text_file": str(path.resolve())})
    reconstructed = "\n\n".join((SOURCE / f"EP13_EN_TAKE_{i:02d}.txt").read_text(encoding="utf-8").strip() for i in range(1, len(stems) + 1))
    expected = "\n\n".join(paragraphs())
    if reconstructed != expected:
        raise RuntimeError("stems do not reconstruct canonical script")
    batch = {
        "episode": "EP13_EN", "profile": "EP05_EN candidate A, reused", "voice": VOICE_ID, "voice_name": "George",
        "model": "eleven_multilingual_v2", "settings": SETTINGS, "seed": SEED,
        "output_format": "mp3_44100_128", "output_dir": str(RAW.resolve()), "stems": stems,
    }
    (VOICE / "voice_batch_master.json").write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
    print(f"prepared {len(stems)} stems, {len(expected)} chars, {len(expected.split())} words")


def loudness(path: Path) -> dict:
    text = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "loudnorm=I=-18:TP=-2:LRA=7:print_format=json", "-f", "null", "-"], True)
    blocks = re.findall(r'\{\s*"input_i".*?\}', text, re.S)
    return json.loads(blocks[-1]) if blocks else {}


def assemble() -> Path:
    batch = json.loads((VOICE / "voice_batch_master.json").read_text(encoding="utf-8"))
    NORM.mkdir(parents=True, exist_ok=True)
    concat, report, cursor = [], [], 0.0
    for i, stem in enumerate(batch["stems"], 1):
        src = RAW / f"{stem['id']}.mp3"
        if not src.is_file():
            raise FileNotFoundError(src)
        dst = NORM / f"{stem['id']}.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-af", "loudnorm=I=-18:TP=-2:LRA=7", "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(dst)])
        sec = duration(dst)
        concat.append(f"file '{dst.as_posix()}'")
        report.append({"id": stem["id"], "start": round(cursor, 3), "end": round(cursor + sec, 3), "duration": round(sec, 3), "sha256": sha(dst)})
        cursor += sec
        if i < len(batch["stems"]):
            gap_sec = 0.34
            gap = MASTER / f"gap_{i:02d}.wav"
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono:d={gap_sec}", "-c:a", "pcm_s24le", str(gap)])
            concat.append(f"file '{gap.as_posix()}'")
            cursor += gap_sec
    concat_path = MASTER / "concat.txt"
    concat_path.write_text("\n".join(concat) + "\n", encoding="utf-8")
    out = MASTER / "EP13_EN_VO_MASTER.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_path), "-c:a", "pcm_s24le", str(out)])
    data = {"profile": "EP05_A", "voice": "George", "model": batch["model"], "settings": batch["settings"], "duration": round(duration(out), 3), "loudness": loudness(out), "sha256": sha(out), "stems": report}
    (MASTER / "stem_report.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(out)
    return out


def load_key() -> str:
    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", SHARED_CLI)
    if spec is None or spec.loader is None:
        raise RuntimeError("shared ElevenLabs CLI unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module._load_key())


def multipart(audio: Path, text: str) -> tuple[bytes, str]:
    boundary = "----EP13EN" + uuid.uuid4().hex
    parts = [f"--{boundary}\r\n".encode(), b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n", f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(), b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode()]
    return b"".join(parts), boundary


def align() -> Path:
    audio = MASTER / "EP13_EN_VO_MASTER.wav"
    text = "\n\n".join(paragraphs())
    body, boundary = multipart(audio, text)
    req = Request("https://api.elevenlabs.io/v1/forced-alignment", data=body, headers={"xi-api-key": load_key(), "Content-Type": f"multipart/form-data; boundary={boundary}", "Accept": "application/json"}, method="POST")
    with urlopen(req, timeout=900) as response:
        data = json.loads(response.read().decode())
    data.update({"episode": "EP13_EN", "profile": "EP05_A", "source_text": text, "audio": str(audio.resolve()), "audio_sha256": sha(audio)})
    ALIGN.parent.mkdir(parents=True, exist_ok=True)
    ALIGN.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(ALIGN)
    return ALIGN


def tokens(text: str) -> list[str]:
    return re.findall(r"[0-9a-z]+", text.casefold())


def qa() -> None:
    audio = MASTER / "EP13_EN_VO_MASTER.wav"
    client = ElevenLabs(api_key=load_key())
    with audio.open("rb") as stream:
        response = client.speech_to_text.convert(model_id="scribe_v2", file=stream, language_code="en", tag_audio_events=False, diarize=False, timestamps_granularity="word", seed=260827, keyterms=["Fatima", "Lucia dos Santos", "Agca", "Sodano", "John Paul", "Holy Office", "Saint Peter's Square", "Napoleon"])
    raw = response.model_dump(mode="json") if hasattr(response, "model_dump") else json.loads(response.json())
    expected = tokens(SCRIPT.read_text(encoding="utf-8"))
    heard = tokens(str(raw.get("text", "")))
    matcher = SequenceMatcher(None, expected, heard, autojunk=False)
    issues = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            issues.append({"type": tag, "expected": expected[i1:i2], "heard": heard[j1:j2]})
    report = {"model": "scribe_v2", "expected_words": len(expected), "heard_words": len(heard), "sequence_similarity": round(matcher.ratio(), 6), "issues": issues, "transcription": raw, "status": "PASS" if matcher.ratio() >= 0.992 and len(issues) <= 4 else "REVIEW"}
    out = VOICE / "QA" / "EP13_EN_SCRIBE_CONTENT_QA.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("sequence_similarity", "issues", "status")}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["prepare", "assemble", "align", "qa"])
    args = ap.parse_args()
    {"prepare": prepare, "assemble": assemble, "align": align, "qa": qa}[args.action]()


if __name__ == "__main__":
    main()
