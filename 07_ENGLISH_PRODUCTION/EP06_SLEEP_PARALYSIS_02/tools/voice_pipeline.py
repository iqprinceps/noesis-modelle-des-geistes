#!/usr/bin/env python3
"""Resume-safe George voice master, content QA and alignment for EP06 EN.

The only TTS authority is the already generated, manifest-locked ElevenLabs
George full-canonical stem. This tool never issues a TTS request; it only masters and
verifies that immutable source before forced alignment.
"""

from __future__ import annotations

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


EP = Path(__file__).resolve().parents[1]
SCRIPT = EP / "01_SCRIPT" / "VOICE_SCRIPT_EN.txt"
VOICE = EP / "02_VOICE"
MASTER_DIR = VOICE / "MASTER"
ALIGN_DIR = VOICE / "ALIGNMENT"
SUB_DIR = EP / "07_SUBTITLES"
SHARED_CLI = Path(r"C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel\tools\elevenlabs_cli.py")
RAW_GEORGE = MASTER_DIR / "raw_stems_george_full" / "EP06_EN_GEORGE_FULL.mp3"
RAW_MANIFEST = MASTER_DIR / "raw_stems_george_full" / "manifest.json"
SELECTED_VOICE = "JBFqnCBsd6RMkjVDRZzb"
SELECTED_VOICE_NAME = "George - Warm, Captivating Storyteller"
MODEL = "eleven_multilingual_v2"
SETTINGS = {
    "stability": 0.61,
    "similarity_boost": 0.82,
    "style": 0.06,
    "speed": 1.0,
    "use_speaker_boost": True,
}
SEED = 260827


def run(args: list[str], capture: bool = False) -> str:
    p = subprocess.run(args, capture_output=capture, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-6000:])
    return (p.stdout or "") + (p.stderr or "")


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], True).strip())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def as_dict(value) -> dict:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return json.loads(value.json())


def load_key() -> str:
    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", SHARED_CLI)
    if spec is None or spec.loader is None:
        raise RuntimeError("shared encrypted ElevenLabs CLI unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module._load_key())


def scribe_file(audio: Path, expected_text: str, seed: int) -> dict:
    client = ElevenLabs(api_key=load_key())
    with audio.open("rb") as stream:
        response = client.speech_to_text.convert(
            model_id="scribe_v2",
            file=stream,
            language_code="en",
            tag_audio_events=False,
            diarize=False,
            timestamps_granularity="word",
            seed=seed,
            keyterms=[
                "Richard Coman", "Bridget Bishop", "Henry Fuseli", "mara",
                "incubus", "kanashibari", "Newfoundland", "David Hufford",
                "Baland Jalal", "Devon Hinton", "jinn", "atonia",
            ],
        )
    raw = as_dict(response)
    expected = tokens(expected_text)
    heard = tokens(str(raw.get("text", "")))
    return {
        "audio": str(audio.resolve()),
        "duration_seconds": round(duration(audio), 3),
        "expected_words": len(expected),
        "heard_words": len(heard),
        "estimated_wpm": round(len(expected) / duration(audio) * 60, 1),
        "sequence_similarity": round(SequenceMatcher(None, expected, heard, autojunk=False).ratio(), 6),
        "transcript": str(raw.get("text", "")),
        "transcription": raw,
    }


def build_master() -> None:
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_GEORGE.exists() or not RAW_MANIFEST.exists():
        raise RuntimeError("manifest-locked George source missing; refusing any TTS fallback")
    raw_manifest = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
    if len(raw_manifest) != 1:
        raise RuntimeError("expected exactly one George source stem")
    item = raw_manifest[0]
    sent_text = SCRIPT.read_text(encoding="utf-8").strip()
    if item.get("voice_id") != SELECTED_VOICE or item.get("model_id") != MODEL:
        raise RuntimeError("George voice/model authority mismatch")
    if item.get("settings") != SETTINGS or int(item.get("seed", -1)) != SEED:
        raise RuntimeError("Part-1 continuity settings mismatch")
    if int(item.get("characters", -1)) != len(sent_text):
        raise RuntimeError("generated character count does not match canonical lean cut")
    if item.get("sha256") != sha256(RAW_GEORGE):
        raise RuntimeError("George raw source hash mismatch")
    master = MASTER_DIR / "EP06_EN_VO_MASTER.wav"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(RAW_GEORGE),
        "-af", "loudnorm=I=-18:TP=-2:LRA=7", "-ar", "48000", "-ac", "1",
        "-c:a", "pcm_s24le", str(master),
    ])
    report = {
        "tts_provider": "ElevenLabs",
        "voice": SELECTED_VOICE,
        "voice_name": SELECTED_VOICE_NAME,
        "model": MODEL,
        "settings": SETTINGS,
        "seed": SEED,
        "sent_characters": len(sent_text),
        "script_sha256": sha256(SCRIPT),
        "raw_sha256": sha256(RAW_GEORGE),
        "master_sha256": sha256(master),
        "duration_seconds": round(duration(master), 3),
        "word_count": len(tokens(SCRIPT.read_text(encoding="utf-8"))),
        "continuity_reference": "EP05_EN Part 1 voice_batch_master.json and stem_report.json",
        "generation_requests": 1,
        "pickup_requests": 0,
    }
    (MASTER_DIR / "VOICE_MASTER_MANIFEST.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


def multipart(audio: Path, text: str) -> tuple[bytes, str]:
    boundary = "----SP2EN" + uuid.uuid4().hex
    body = [
        f"--{boundary}\r\n".encode(), b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
        f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        b"Content-Type: audio/wav\r\n\r\n", audio.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(body), boundary


def align() -> None:
    audio = MASTER_DIR / "EP06_EN_VO_MASTER.wav"
    text = SCRIPT.read_text(encoding="utf-8").strip()
    body, boundary = multipart(audio, text)
    req = Request(
        "https://api.elevenlabs.io/v1/forced-alignment", data=body,
        headers={"xi-api-key": load_key(), "Content-Type": f"multipart/form-data; boundary={boundary}", "Accept": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=900) as response:
        data = json.loads(response.read().decode())
    data.update({"source_text": text, "audio": str(audio.resolve()), "audio_sha256": sha256(audio)})
    ALIGN_DIR.mkdir(parents=True, exist_ok=True)
    path = ALIGN_DIR / "EP06_EN_FORCED_ALIGNMENT.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)


def master_qa() -> None:
    audio = MASTER_DIR / "EP06_EN_VO_MASTER.wav"
    expected = SCRIPT.read_text(encoding="utf-8").strip()
    report = scribe_file(audio, expected, 82662)
    report["audio_sha256"] = sha256(audio)
    path = MASTER_DIR / "EP06_EN_VO_SCRIBE_QA.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("duration_seconds", "expected_words", "heard_words", "estimated_wpm", "sequence_similarity", "transcript")}, indent=2))


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "master-qa"
    if command == "master":
        build_master()
    elif command == "align":
        align()
    elif command == "master-qa":
        master_qa()
    else:
        raise SystemExit("Usage: voice_pipeline.py [master|align|master-qa]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
