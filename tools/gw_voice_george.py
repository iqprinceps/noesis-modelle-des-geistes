#!/usr/bin/env python3
"""EP02 Gateway — Voice-Umstellung auf George.

Erzeugt bereinigte Sprechtexte und die Batch-Konfiguration fuer
JBFqnCBsd6RMkjVDRZzb ("George - Warm, Captivating Storyteller").

Warum die Lautschrift-Kruecken rausfliegen:

Die V2-Texte waren fuer eine deutsche Stimme praepariert — "Wäin Em
Mak-Donnell", "C I A", "U S Army", "E E G". Die getrennten Buchstaben und
die Bindestriche sind genau die Stellen, an denen das Modell Pausen setzt.
George ist eine englischsprachige Stimme und spricht "Wayne M. McDonnell",
"Gateway", "Focus", "Monroe" und "Fort Meade" ohne jede Hilfe korrekt.

Die Einstellungen entsprechen der bereits erprobten deutschen
George-Konfiguration aus E01 DeBeers (18_multilang/de) — nicht den
Gateway-V2-Werten. Vor allem die Geschwindigkeit: 1.06 statt 1.12.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2" / "voice" / "source"
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V6" / "voice" / "source"
BATCH = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V6" / "voice" / "voice_batch.json"
RAW = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V6" / "voice" / "raw_stems"

VOICE = "JBFqnCBsd6RMkjVDRZzb"          # George - Warm, Captivating Storyteller
MODEL = "eleven_multilingual_v2"

# Erprobt in NOESIS E01 DeBeers, deutsche Fassung
SETTINGS = {
    "stability": 0.58,
    "similarity_boost": 0.80,
    "style": 0.08,
    "speed": 1.06,                       # Gateway V2 lief auf 1.12
    "use_speaker_boost": True,
}
SEED = 2402

# Die Schreibweise fuer "CIA" entscheidet der Hoertest
# (voice_test/G_* gegen H_* gegen I_*). Hier eine Zeile aendern.
CIA = "CIA"

ERSETZUNGEN = [
    # getrennte Buchstaben -> zusammen; das Getrenntschreiben erzeugt die Pausen
    (r"\bC I A\b", CIA),
    (r"\bU S Army\b", "US Army"),
    (r"\bE E G\b", "EEG"),
    # deutsche Lautschrift fuer einen englischen Namen — George braucht das nicht
    (r"Wäin Em Mak-Donnell", "Wayne M. McDonnell"),
    (r"Mak-Donnell", "McDonnell"),
    (r"Mak-Donnells", "McDonnells"),
]


def clean(text: str) -> tuple[str, list[str]]:
    treffer = []
    for muster, ersatz in ERSETZUNGEN:
        text, n = re.subn(muster, ersatz, text)
        if n:
            treffer.append(f"{muster} -> {ersatz} ({n}x)")
    return text, treffer


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    stems = []
    print("Bereinige Sprechtexte:\n")
    for p in sorted(SRC.glob("*.txt")):
        text, treffer = clean(p.read_text(encoding="utf-8"))
        ziel = OUT / p.name
        ziel.write_text(text, encoding="utf-8")
        stems.append({"id": p.stem, "text_file": str(ziel.resolve())})
        print(f"  {p.stem[9:40]:<34} {', '.join(treffer) if treffer else 'unveraendert'}")
    batch = {
        "voice": VOICE,
        "voice_name": "George - Warm, Captivating Storyteller",
        "model": MODEL,
        "settings": SETTINGS,
        "seed": SEED,
        "output_format": "mp3_44100_128",
        "output_dir": str(RAW.resolve()),
        "stems": stems,
        "hinweis": ("Einstellungen aus der erprobten deutschen George-Fassung "
                    "von NOESIS E01 DeBeers. Gateway V2 lief auf speed 1.12, "
                    "was den holprigen Rhythmus mitverursacht hat."),
    }
    BATCH.parent.mkdir(parents=True, exist_ok=True)
    BATCH.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    zeichen = sum(len((OUT / s["id"]).with_suffix(".txt").read_text(encoding="utf-8"))
                  for s in stems)
    print(f"\n{len(stems)} Stems · {zeichen} Zeichen · Schreibweise CIA = {CIA!r}")
    print(f"Batch: {BATCH}")


if __name__ == "__main__":
    main()
