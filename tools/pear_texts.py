#!/usr/bin/env python3
"""EP03 PEAR — Sprechtexte aus der Reinschrift ableiten.

Abgeleitet von `tools/spg_texts.py`. Eine Textquelle:
`07_VOICE_SCRIPT_CLEAN.txt`. Daraus entstehen die acht Sprechtexte fuer
George. Dieselbe Reinschrift geht unveraendert ins Forced Alignment, in die
Untertitel und in die Bildanker.

Ersetzt werden nur Zahlen und Einheiten, die George sonst falsch betont.
Namen und englische Begriffe bleiben stehen — Lautschrift-Kruecken erzeugen
genau die Pausen, die stoeren (Produktionsstandard § 6).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"
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

# Acht Akte nach Produktionsstandard § 1. Die Grenze ist der erste Satz des
# Akts, woertlich aus der Reinschrift.
AKTE = [
    ("EP03_VO_01_HOOK",        "Du sitzt in einem Kellerraum"),
    ("EP03_VO_02_DER_MANN",    "Der Mann heißt Robert Jahn."),
    ("EP03_VO_03_DIE_MASCHINE", "Und dann bauen sie Maschinen."),
    ("EP03_VO_04_DER_ABLAUF",  "Und der Ablauf im Labor ist immer gleich."),
    ("EP03_VO_05_DIE_ZAHL",    "Und dann kommt der Teil, der schwerer zu erzählen ist"),
    ("EP03_VO_06_DIE_KRITIK",  "Genau darüber ist jahrzehntelang gestritten worden."),
    ("EP03_VO_07_DIE_PROBE",   "Denn jetzt kommt die Stelle, an der diese Geschichte"),
    ("EP03_VO_08_WAS_BLEIBT",  "Was bleibt von achtundzwanzig Jahren?"),
]

ZAHLEN = [
    (r"\bPEAR\b", "Pier"),          # englische Aussprache, sonst "Peh-Ah-Er"
    (r"\bPear Inc\b", "Pier Inc"),
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


def main() -> None:
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    text = CLEAN.read_text(encoding="utf-8").strip()

    stems, gesamt = [], 0
    for name, akt in split_acts(text):
        sprech, log = to_spoken(akt)
        ziel = OUT / f"{name}.txt"
        ziel.write_text(sprech + "\n", encoding="utf-8")
        stems.append({"id": name, "text_file": str(ziel.resolve())})
        w = len(akt.split()); gesamt += w
        print(f"{name:26s} {w:4d} Woerter  ~{w / 2.33:5.1f}s"
              f"   {', '.join(log) or '—'}")

    BATCH.write_text(json.dumps({
        "voice": VOICE, "voice_name": VOICE_NAME, "model": MODEL,
        "settings": SETTINGS, "seed": SEED,
        "output_format": "mp3_44100_128",
        "output_dir": str(RAW.resolve()),
        "stems": stems,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{gesamt} Woerter gesamt  ~{gesamt / 2.33 / 60:.1f} min")
    print(f"Batchdatei: {BATCH}")


if __name__ == "__main__":
    main()
