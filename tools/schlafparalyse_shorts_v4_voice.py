#!/usr/bin/env python3
"""Record the V4 Short narrations with George and force-align them.

The V4 texts are written for speech rather than for reading, so the delivery is
nudged a little more expressive than the V2 take (stability 0.58 -> 0.52) and a
little slower (speed 1.06 -> 1.02) to let the short sentences land. Everything
else matches the established channel profile so the Shorts still sound like the
long-form episodes.

Each Short stays one continuous ElevenLabs file. There are no internal stitches,
which is the invariant the whole Shorts pipeline was built around.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
SPECS = PROD / "V4_SCRIPTS.json"
CLI = Path.home() / "Documents" / "Codex" / "NOESIS Channel" / "tools" / "elevenlabs_cli.py"

VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
SETTINGS = {"stability": "0.52", "similarity": "0.80", "style": "0.10", "speed": "1.02"}
SEEDS = {
    "SP06A_ATEM": 2402, "SP06B_RUECKENLAGE": 2403, "SP07A_ALBTRAUMWORT": 2404,
    "SP07B_SALEM_ZEUGE": 2405, "SP08A_HAT_MAN_HUT": 2406, "SP08B_UNSICHTBARE_PERSON": 2407,
}


def load_key() -> str:
    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", CLI)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return str(module._load_key())


def record(job: str, data: dict) -> Path:
    folder = PROD / job / "voice_v4"
    folder.mkdir(parents=True, exist_ok=True)
    text = folder / ("%s_NARRATION_V4.txt" % job)
    text.write_text(data["narration"], encoding="utf-8")
    out = folder / ("%s_GEORGE_V4.mp3" % job)
    args = [
        sys.executable, str(CLI), "generate",
        "--voice", VOICE_ID, "--text-file", str(text), "--output", str(out),
        "--model", "eleven_multilingual_v2", "--output-format", "mp3_44100_128",
        "--speaker-boost", "--seed", str(SEEDS[job]), "--execute",
    ]
    for flag, value in SETTINGS.items():
        args += ["--" + flag.replace("_", "-"), value]
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode or not out.is_file():
        raise RuntimeError("%s: %s" % (job, (result.stderr or result.stdout)[-3000:]))
    return out


def multipart(audio: Path, text: str) -> tuple[bytes, str]:
    boundary = "----SPV4" + uuid.uuid4().hex
    parts = [
        ("--%s\r\n" % boundary).encode(),
        b'Content-Disposition: form-data; name="text"\r\n\r\n', text.encode(), b"\r\n",
        ("--%s\r\n" % boundary).encode(),
        ('Content-Disposition: form-data; name="file"; filename="%s"\r\n' % audio.name).encode(),
        b"Content-Type: audio/mpeg\r\n\r\n", audio.read_bytes(), b"\r\n",
        ("--%s--\r\n" % boundary).encode(),
    ]
    return b"".join(parts), boundary


def align(job: str, audio: Path, narration: str) -> dict:
    """Forced alignment gives the word timings the beat-cut editor runs on."""
    flat = " ".join(narration.split())
    body, boundary = multipart(audio, flat)
    request = Request(
        "https://api.elevenlabs.io/v1/forced-alignment", data=body,
        headers={
            "xi-api-key": load_key(),
            "Content-Type": "multipart/form-data; boundary=%s" % boundary,
            "Accept": "application/json",
        }, method="POST",
    )
    with urlopen(request, timeout=600) as response:
        data = json.loads(response.read().decode())
    words = [
        {"text": row.get("text", ""), "start": row.get("start"), "end": row.get("end"),
         "type": "word"}
        for row in data.get("words", [])
        if str(row.get("text", "")).strip()
    ]
    out = {
        "job": job,
        "purpose": "V4 forced alignment for beat-driven Shorts editing",
        "voice": "George", "voice_id": VOICE_ID,
        "expected_words": len(flat.split()),
        "heard_words": len(words),
        "transcription": {"words": words, "text": flat},
    }
    target = PROD / job / "voice_v4" / "ALIGNMENT_V4.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only")
    args = parser.parse_args()
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    summary = {}
    for job, data in specs.items():
        if job.startswith("_") or (args.only and job != args.only):
            continue
        audio = record(job, data)
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio)],
            capture_output=True, text=True,
        ).stdout.strip()
        report = align(job, audio, data["narration"])
        summary[job] = {
            "audio": str(audio),
            "seconds": round(float(probe), 3),
            "characters": len(data["narration"]),
            "expected_words": report["expected_words"],
            "heard_words": report["heard_words"],
        }
        print(json.dumps({job: summary[job]}, ensure_ascii=False), flush=True)
    (PROD / "V4_VOICE_REPORT.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
