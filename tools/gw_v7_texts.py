#!/usr/bin/env python3
"""EP02 Gateway V7 — Sprechtexte aus der Reinschrift ableiten.

Es gibt genau eine Textquelle: `07_VOICE_SCRIPT_CLEAN_V7.txt`. Daraus
entstehen die acht Sprechtexte fuer George. Die Reinschrift geht spaeter
unveraendert ins Forced Alignment, in die Untertitel und in die Bildanker.

Nur so bleiben Gesprochenes, Untertitel und Timeline garantiert deckungsgleich.
V2 hatte zwei getrennt gepflegte Fassungen — das ist die Fehlerquelle, die
wir hier vermeiden.

Ersetzt werden ausschliesslich Zahlen und Datumsangaben. Englische Begriffe
und Namen bleiben stehen: George ist eine englischsprachige Stimme und
spricht sie von sich aus korrekt.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V7"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN_V7.txt"
OUT = PROD / "voice" / "source"
BATCH = PROD / "voice" / "voice_batch.json"
RAW = PROD / "voice" / "raw_stems"

VOICE = "JBFqnCBsd6RMkjVDRZzb"
VOICE_NAME = "George - Warm, Captivating Storyteller"
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.58, "similarity_boost": 0.80, "style": 0.08,
            "speed": 1.06, "use_speaker_boost": True}
SEED = 2402

# Akte: Titel und die Zeile, mit der der Akt beginnt
AKTE = [
    ("01_DREI_BEOBACHTER", "Drei Menschen. Ein Ziel."),
    ("02_DIE_DREI_MAENNER", "Die Antwort beginnt mit Kopfhörern"),
    ("03_ZWEI_TOENE", "Setz Kopfhörer auf."),
    ("04_DER_SPRUNG", "McDonnell geht es um die größere Frage."),
    ("05_DIE_STUFEN", "Sie heißt Focus Levels."),
    ("06_ZEHN_ZIFFERN", "Denn irgendwann stellt McDonnell"),
    ("07_EMPFEHLUNG_H", "Drei Personen. Dasselbe Ziel."),
    ("08_WAS_BLEIBT", "Vierzig Jahre später lässt sich davon"),
]

# Nur Zahlen und Daten. Reihenfolge zaehlt: laengere Muster zuerst.
ZAHLEN = [
    (r"\b9\. Juni 1983\b", "neunten Juni neunzehnhundertdreiundachtzig"),
    (r"\b25\. Mai 1979\b", "fünfundzwanzigsten Mai neunzehnhundertneunundsiebzig"),
    (r"\bFlug 191\b", "Flug einhunderteinundneunzig"),
    (r"\b400 Hertz\b", "vierhundert Hertz"),
    (r"\bRechts mit 410\b", "Rechts mit vierhundertzehn"),
    (r"\b22 Studien\b", "zweiundzwanzig Studien"),
    (r"\bFocus 10\b", "Focus zehn"),
    (r"\bFocus 12\b", "Focus zwölf"),
    (r"\bFocus 15\b", "Focus fünfzehn"),
    (r"\bFocus 21\b", "Focus einundzwanzig"),
    (r"\b1993\b", "neunzehnhundertdreiundneunzig"),
    (r"\b1983\b", "neunzehnhundertdreiundachtzig"),
    (r"\b2019\b", "zweitausendneunzehn"),
    (r"\b2023\b", "zweitausenddreiundzwanzig"),
]


def split_acts(text: str) -> list[tuple[str, str]]:
    starts = []
    for name, marker in AKTE:
        pos = text.find(marker)
        if pos < 0:
            raise SystemExit(f"Aktanfang nicht gefunden: {marker!r}")
        starts.append((pos, name))
    starts.sort()
    out = []
    for i, (pos, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        out.append((name, text[pos:end].strip()))
    return out


def to_spoken(text: str) -> tuple[str, list[str]]:
    log = []
    for muster, ersatz in ZAHLEN:
        text, n = re.subn(muster, ersatz, text)
        if n:
            log.append(f"{muster.strip(chr(92)+'b')} ({n}x)")
    return text, log


def main():
    clean = CLEAN.read_text(encoding="utf-8").strip()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    for alt in OUT.glob("*.txt"):
        alt.unlink()

    stems, gesamt = [], 0
    print(f"Reinschrift: {len(clean.split())} Wörter\n")
    for name, teil in split_acts(clean):
        spoken, log = to_spoken(teil)
        sid = f"EP02V7_VO_{name}"
        ziel = OUT / f"{sid}.txt"
        ziel.write_text(spoken + "\n", encoding="utf-8")
        stems.append({"id": sid, "text_file": str(ziel.resolve())})
        gesamt += len(spoken)
        print(f"  {name:<22} {len(teil.split()):4d} W  {', '.join(log) if log else '—'}")

    BATCH.parent.mkdir(parents=True, exist_ok=True)
    BATCH.write_text(json.dumps({
        "voice": VOICE, "voice_name": VOICE_NAME, "model": MODEL,
        "settings": SETTINGS, "seed": SEED, "output_format": "mp3_44100_128",
        "output_dir": str(RAW.resolve()), "stems": stems,
        "quelle": str(CLEAN.resolve()),
        "hinweis": ("Sprechtexte werden aus der Reinschrift abgeleitet, nicht "
                    "getrennt gepflegt. Aenderungen immer in der Reinschrift."),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(stems)} Stems · {gesamt} Zeichen · Batch: {BATCH.name}")


if __name__ == "__main__":
    main()
