#!/usr/bin/env python3
"""EP03 PEAR V2 — Forced Alignment für Timeline-Sync.

Sendet den Voice-Master und den Text an die ElevenLabs Forced Alignment API,
um genaue Zeitstempel für jedes Wort zu erhalten. Diese werden dann für die
Timeline-Buildung verwendet, damit gesprochene Texte und angezeigte Bilder
perfekt synchron sind.

Nutzung:
    python tools/pear_align_v2.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

# V2 Pfade
MASTER = PROD / "voice" / "master" / "EP03_V2_VO_MASTER.wav"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN_V2.txt"
ALIGNMENT = PROD / "voice" / "alignment" / "EP03_V2_alignment.json"


def multipart(audio: Path, text: str):
    """Erstellt multipart/form-data für die Alignment-API."""
    b = "----SPG" + uuid.uuid4().hex
    parts = [
        f"--{b}\r\n".encode(),
        b'Content-Disposition: form-data; name="text"\r\n\r\n',
        text.encode(),
        b"\r\n",
        f"--{b}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'.encode(),
        b"Content-Type: audio/wav\r\n\r\n",
        audio.read_bytes(),
        b"\r\n",
        f"--{b}--\r\n".encode()
    ]
    return b"".join(parts), b


def align():
    """Führt Forced Alignment durch."""
    print("\n  Forced Alignment für EP03 V2...")
    
    # Prüfe ob Dateien vorhanden
    if not MASTER.exists():
        print(f"  FEHLER: Voice Master fehlt: {MASTER}")
        return
    
    if not CLEAN.exists():
        print(f"  FEHLER: Clean Script fehlt: {CLEAN}")
        return
    
    # Lade Text
    text = CLEAN.read_text(encoding="utf-8").strip()
    print(f"  Text: {len(text)} Zeichen")
    
    # Lade API Key
    sys.path.insert(0, str(ROOT.parent / "NOESIS Channel" / "tools"))
    try:
        from elevenlabs_cli import _load_key
        api_key = _load_key()
    except ImportError:
        print("  FEHLER: ElevenLabs CLI nicht verfügbar")
        return
    
    # Erstelle Request
    body, boundary = multipart(MASTER, text)
    
    req = Request(
        "https://api.elevenlabs.io/v1/forced-alignment",
        data=body,
        headers={
            "xi-api-key": api_key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json"
        },
        method="POST"
    )
    
    # Sende Request
    print("  Sende an ElevenLabs API...")
    try:
        with urlopen(req, timeout=600) as res:
            data = json.loads(res.read().decode())
    except HTTPError as e:
        print(f"  FEHLER: HTTP {e.code}")
        print(f"  {e.read().decode(errors='replace')[:800]}")
        return
    
    # Speichere Alignment
    data.update({
        "source_text": text,
        "audio": str(MASTER.resolve()),
        "audio_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest()
    })
    
    ALIGNMENT.parent.mkdir(parents=True, exist_ok=True)
    ALIGNMENT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    # Statistik
    chars = data.get("characters", [])
    words = data.get("words", [])
    
    print(f"\n  Alignment gespeichert: {ALIGNMENT.name}")
    print(f"  Zeichen: {len(chars)}")
    print(f"  Wörter: {len(words)}")
    
    if chars:
        total_duration = chars[-1].get("end", 0)
        print(f"  Dauer: {total_duration:.2f}s")
    
    return data


if __name__ == "__main__":
    align()
