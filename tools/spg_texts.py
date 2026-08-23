#!/usr/bin/env python3
"""EP01A Die Spiegel — Sprechtexte aus der Reinschrift ableiten.

Abgeleitet von `tools/gw_v7_texts.py` (EP02 Gateway V7). Die Vorlage bleibt
unveraendert; hier stehen nur die Pfade, die Aktgrenzen und die Zahlenliste
dieser Folge.

Es gibt genau eine Textquelle: `07_VOICE_SCRIPT_CLEAN.txt`. Daraus entstehen
die acht Sprechtexte fuer George. Dieselbe Reinschrift geht unveraendert ins
Forced Alignment, in die Untertitel und in die Bildanker.

Ersetzt werden ausschliesslich Zahlen und Datumsangaben. Namen und russische
Begriffe bleiben stehen — Lautschrift-Kruecken erzeugen genau die Pausen, die
stoeren (Produktionsstandard § 6).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN.txt"
OUT = PROD / "voice" / "source"
BATCH = PROD / "voice" / "voice_batch.json"
RAW = PROD / "voice" / "raw_stems"

VOICE = "JBFqnCBsd6RMkjVDRZzb"
VOICE_NAME = "George - Warm, Captivating Storyteller"
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.58, "similarity_boost": 0.80, "style": 0.08,
            "speed": 1.06, "use_speaker_boost": True}
SEED = 2402

# Acht Akte nach Produktionsstandard § 1. Die Grenzen liegen auf Absaetzen der
# Reinschrift; massgeblich ist die dramaturgische Aufgabe des Akts.
#
#   1 Hook             die Sitzung in der Spirale, dann die Quelle
#   2 Die Menschen     Nowosibirsk, Kaznacheev, Trofimov
#   3 Die Maschine     Masse, Bauform, Patent — nachpruefbar
#   4 Der Kozyrev-Raum der Sprung: geschwaechtes Feld, Ferninformation
#   5 Die Protokolle   die Landkarte der Berichte, Mid-Roll-CTA am Ende
#   6 Aurora Borealis  der Moment, in dem etwas versucht wird
#   7 Dikson           das wildeste Bild, voll ausgespielt
#   8 Was bleibt       pruefbar, offen, Schlussbild und Ausblick auf EP01
AKTE = [
    ("01_HOOK", "Du sitzt auf einem Stuhl aus Metall."),
    ("02_DIE_MENSCHEN", "Im Netz heißt diese Konstruktion Zeitmaschine."),
    ("03_DIE_MASCHINE", "Gebogene Platten aus Aluminiumlegierung."),
    ("04_KOZYREV_RAUM", "Was die beiden über das Innere sagen"),
    ("05_DIE_PROTOKOLLE", "Am häufigsten die Farbe."),
    ("06_AURORA_BOREALIS", "Denn was 1990 und 1991 folgt"),
    ("07_DIKSON", "Der Ablauf ist für alle Teilnehmer gleich."),
    ("08_WAS_BLEIBT", "Was bleibt davon übrig?"),
]

# Nur Zahlen und Daten. Reihenfolge zaehlt: laengere Muster zuerst.
ZAHLEN = [
    (r"\b1990 und 1991\b", "neunzehnhundertneunzig und neunzehnhunderteinundneunzig"),
    (r"\b1958\b", "neunzehnhundertachtundfünfzig"),
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
    if starts != sorted(starts):
        raise SystemExit("Aktanfaenge stehen nicht in der Reihenfolge der Reinschrift")
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
            log.append(f"{muster.strip(chr(92) + 'b')} ({n}x)")
    return text, log


def main():
    clean = CLEAN.read_text(encoding="utf-8").strip()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    for alt in OUT.glob("*.txt"):
        alt.unlink()

    stems, gesamt = [], 0
    print(f"Reinschrift: {len(clean.split())} Woerter\n")
    for name, teil in split_acts(clean):
        spoken, log = to_spoken(teil)
        rest = re.findall(r"\d+", spoken)
        if rest:
            raise SystemExit(f"{name}: Ziffern uebrig: {rest}")
        sid = f"EP01A_VO_{name}"
        ziel = OUT / f"{sid}.txt"
        ziel.write_text(spoken + "\n", encoding="utf-8")
        stems.append({"id": sid, "text_file": str(ziel.resolve())})
        gesamt += len(spoken)
        print(f"  {name:<20} {len(teil.split()):4d} W  {len(spoken):5d} Z  "
              f"{', '.join(log) if log else '-'}")

    BATCH.parent.mkdir(parents=True, exist_ok=True)
    BATCH.write_text(json.dumps({
        "voice": VOICE, "voice_name": VOICE_NAME, "model": MODEL,
        "settings": SETTINGS, "seed": SEED, "output_format": "mp3_44100_128",
        "output_dir": str(RAW.resolve()), "stems": stems,
        "quelle": str(CLEAN.resolve()),
        "hinweis": ("Sprechtexte werden aus der Reinschrift abgeleitet, nicht "
                    "getrennt gepflegt. Aenderungen immer in der Reinschrift."),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(stems)} Stems - {gesamt} Zeichen - Batch: {BATCH.name}")


if __name__ == "__main__":
    main()
