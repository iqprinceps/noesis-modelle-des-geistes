#!/usr/bin/env python3
"""Narration for the EP13 teaser shorts, English and German.

One tool for all four, because they are the same job four times: read a short
script, synthesise it with the channel voice, normalise it, and get a forced
alignment so the cue sheet can be bound to words rather than to guesses.

The scripts are short enough for a single take each, so there is no assembly
step and no stem seams to worry about.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHARED_CLI = ROOT.parent / "NOESIS Channel" / "tools" / "elevenlabs_cli.py"
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
SETTINGS = {"stability": 0.61, "similarity_boost": 0.82, "style": 0.06,
            "speed": 1.0, "use_speaker_boost": True}
SEED = 260827

SHORTS = {
    "en1": (ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01_SHORTS" / "S01_BULLET_IN_CROWN",
            "VOICE_SCRIPT_EN.txt", "EP13_S01_EN", "en"),
    "en2": (ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01_SHORTS" / "S02_THE_SILENCE",
            "VOICE_SCRIPT_EN.txt", "EP13_S02_EN", "en"),
    "de1": (ROOT / "08_GERMAN_PRODUCTION" / "EP13_VATIKAN_01_SHORTS" / "S01_KUGEL_IN_KRONE",
            "VOICE_SCRIPT_DE.txt", "EP13_S01_DE", "de"),
    "de2": (ROOT / "08_GERMAN_PRODUCTION" / "EP13_VATIKAN_01_SHORTS" / "S02_DAS_SCHWEIGEN",
            "VOICE_SCRIPT_DE.txt", "EP13_S02_DE", "de"),
}


def run(args, capture=False, timeout=None):
    p = subprocess.run(args, text=True, capture_output=capture, timeout=timeout)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-3000:])
    return (p.stdout or "") + (p.stderr or "")


def paths(key):
    root, script, stem, lang = SHORTS[key]
    return {"root": root, "script": root / "01_SCRIPT" / script, "stem": stem, "lang": lang,
            "voice": root / "02_VOICE", "raw": root / "02_VOICE" / "raw",
            "master": root / "02_VOICE" / f"{stem}_VO_MASTER.wav",
            "align": root / "02_VOICE" / f"{stem}_ALIGNMENT.json"}


def prepare(key):
    p = paths(key)
    p["raw"].mkdir(parents=True, exist_ok=True)
    text = "\n\n".join(b.strip() for b in re.split(r"\n\s*\n", p["script"].read_text(encoding="utf-8")) if b.strip())
    src = p["voice"] / f"{p['stem']}_TAKE_01.txt"
    src.write_text(text + "\n", encoding="utf-8")
    batch = {"episode": p["stem"], "voice": VOICE_ID, "voice_name": "George",
             "model": "eleven_multilingual_v2", "settings": SETTINGS, "seed": SEED,
             "output_format": "mp3_44100_128", "output_dir": str(p["raw"].resolve()),
             "stems": [{"id": f"{p['stem']}_TAKE_01", "text_file": str(src.resolve())}]}
    (p["voice"] / "voice_batch.json").write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
    print(f"{key}: {len(text)} chars, {len(text.split())} words -> {p['voice'] / 'voice_batch.json'}")


def master(key):
    """Normalise the take to the channel's VO working level."""
    p = paths(key)
    mp3 = p["raw"] / f"{p['stem']}_TAKE_01.mp3"
    if not mp3.is_file():
        raise FileNotFoundError(mp3)
    p["master"].parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3),
         "-af", "highpass=f=70,loudnorm=I=-18:TP=-2:LRA=7,aresample=48000",
         "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(p["master"])], True, 600)
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(p["master"])], True).strip())
    print(f"{key}: {dur:.1f}s -> {p['master'].name}")


def load_key():
    spec = importlib.util.spec_from_file_location("noesis_elevenlabs_cli", SHARED_CLI)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    profile = os.environ.get("NOESIS_ELEVEN_PROFILE", "").strip()
    if profile:
        module._PROFIL = profile
    return str(module._load_key())


def align(key):
    p = paths(key)
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=load_key())
    text = p["script"].read_text(encoding="utf-8")
    with p["master"].open("rb") as fh:
        resp = client.forced_alignment.create(file=fh, text=text)
    data = resp.dict() if hasattr(resp, "dict") else json.loads(resp.json())
    data["episode"] = p["stem"]
    data["source_text"] = text
    p["align"].write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"{key}: alignment -> {p['align'].name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["prepare", "master", "align"])
    ap.add_argument("--which", default="en1,en2,de1,de2")
    a = ap.parse_args()
    for key in [k.strip() for k in a.which.split(",") if k.strip()]:
        {"prepare": prepare, "master": master, "align": align}[a.action](key)


if __name__ == "__main__":
    main()
