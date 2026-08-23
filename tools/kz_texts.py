#!/usr/bin/env python3
"""EP01 Kozyrev V2 — Sprechtexte aus der Reinschrift ableiten.

Abgeleitet von `tools/gw_v7_texts.py` (EP02 Gateway V7). Die Vorlage bleibt
unveraendert; hier stehen nur die Pfade, die Aktgrenzen und die Zahlenliste
dieser Folge.

Es gibt genau eine Textquelle: `07_VOICE_SCRIPT_CLEAN_V2.txt`. Daraus
entstehen die acht Sprechtexte fuer George. Dieselbe Reinschrift geht spaeter
unveraendert ins Forced Alignment, in die Untertitel und in die Bildanker.

Ersetzt werden ausschliesslich Zahlen und Datumsangaben. Namen und russische
Begriffe bleiben stehen — Lautschrift-Kruecken erzeugen genau die Pausen,
die stoeren (Produktionsstandard § 6).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP01_KOZYREV_V2"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN_V2.txt"
OUT = PROD / "voice" / "source"
BATCH = PROD / "voice" / "voice_batch.json"
RAW = PROD / "voice" / "raw_stems"

VOICE = "JBFqnCBsd6RMkjVDRZzb"
VOICE_NAME = "George - Warm, Captivating Storyteller"
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.58, "similarity_boost": 0.80, "style": 0.08,
            "speed": 1.06, "use_speaker_boost": True}
SEED = 2402

# Acht Akte nach Produktionsstandard § 1. Die Grenzen liegen auf Leerzeilen
# der Reinschrift; massgeblich ist der inhaltliche Aufbau.
#
#   1 Hook            die Spirale, das Patent, die zwei Fragen
#   2 Kozyrev         Verhaftung, Lager, Zeittheorie, Tod  (Biografie-Wendung)
#   3 Die Maschine    das Patent auf Papier, Masse, Titel
#   4 Kozyrev-Raum    der Sprung: geschwaechtes Feld, Ferninformation
#   5 Die Protokolle  was berichtet wird, ausgebreitet, Mid-Roll-CTA
#   6 Aurora Borealis der Moment, in dem etwas passiert
#   7 Das Patent      das wildeste Bild, voll ausgespielt
#   8 Was bleibt      pruefbar, offen, Schlussbild
AKTE = [
    ("01_HOOK", "In einem Labor in Sibirien"),
    ("02_KOZYREV", "Im November 1936 klopft es"),
    ("03_DIE_MASCHINE", "Dann reichen in Nowosibirsk zwei Männer"),
    ("04_KOZYREV_RAUM", "Die Antwort steht in den Texten"),
    ("05_DIE_PROTOKOLLE", "Über Jahrzehnte sammeln die Forscher"),
    ("06_AURORA_BOREALIS", "Das Experiment trug den Namen"),
    ("07_DAS_PATENT", "Man muss sich dieses Bild"),
    ("08_WAS_BLEIBT", "Die Anlagen existieren."),
]

# Nur Zahlen und Daten. Reihenfolge zaehlt: laengere Muster zuerst.
ZAHLEN = [
    (r"\b1990 und 1991\b", "neunzehnhundertneunzig und neunzehnhunderteinundneunzig"),
    (r"\b1936\b", "neunzehnhundertsechsunddreißig"),
    (r"\b1941\b", "neunzehnhunderteinundvierzig"),
    (r"\b1946\b", "neunzehnhundertsechsundvierzig"),
    (r"\b1983\b", "neunzehnhundertdreiundachtzig"),
    (r"\b1991\b", "neunzehnhunderteinundneunzig"),
    (r"\b1996\b", "neunzehnhundertsechsundneunzig"),
    (r"\b1998\b", "neunzehnhundertachtundneunzig"),
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
        rest = re.findall(r"\d+", spoken)
        if rest:
            raise SystemExit(f"{name}: Ziffern uebrig: {rest}")
        sid = f"EP01V2_VO_{name}"
        ziel = OUT / f"{sid}.txt"
        ziel.write_text(spoken + "\n", encoding="utf-8")
        stems.append({"id": sid, "text_file": str(ziel.resolve())})
        gesamt += len(spoken)
        print(f"  {name:<22} {len(teil.split()):4d} W  {len(spoken):5d} Z  "
              f"{', '.join(log) if log else '—'}")

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
