#!/usr/bin/env python3
"""Prueft eine Reinschrift gegen den Produktionsstandard.

    python tools/gw_pruefe_text.py 06_PRODUCTION/EP0X_.../07_VOICE_SCRIPT_CLEAN.txt

Meldet die beiden verbotenen Sprachmuster aus
`01_GLOBAL/00_PRODUKTIONSSTANDARD.md` § 2, dazu Umfang, Fragen und
Cliffhanger. Kein Ersatz fuer Lesen — aber es faengt genau die Figuren ab,
die sich beim Schreiben immer wieder einschleichen.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# § 2: "X nicht A. X B." — die Antithese
#
# Kennzeichen ist nicht die Verneinung allein, sondern die Wiederholung
# derselben Aussage im Folgesatz: "sollte nicht beschreiben / sollte bewerten",
# "will nicht erklären / will erklären", "lautet nicht / lautet".
# Deshalb wird geprüft, ob beide Sätze dasselbe Prädikat tragen.
NEGATION = re.compile(r"\bnicht\b|\bkein[emrs]?\b|\bnie\b", re.I)
SONDERN = re.compile(r"^Sondern\b", re.I)

# Wörter, die als geteiltes Prädikat zählen (kein Parser nötig)
PRAEDIKAT = re.compile(
    r"\b(?:ist|war|sind|waren|will|wollte|soll|sollte|lautet|geht|"
    r"bedeutet|heißt|beweist|belegt|zeigt|braucht|macht)\b", re.I)
STOPP = re.compile(r"^(?:Nicht|Kein)\b")


def ist_antithese(a: str, b: str) -> bool:
    """Verneinter Satz, dessen Aussage der Folgesatz positiv wiederholt."""
    if not NEGATION.search(a):
        return False
    if SONDERN.match(b):
        return True
    va = {w.lower() for w in PRAEDIKAT.findall(a)}
    vb = {w.lower() for w in PRAEDIKAT.findall(b)}
    return bool(va & vb) and len(b) < 160

# § 2: Ruecknahmesaetze
RUECKNAHME = [
    (r"[Dd]as ist (?:die|eine) (?:Annahme|Vermutung|Erklärung|Hypothese)", "Rücknahme"),
    (r"[Dd]as ist interessant,? aber", "Rücknahme"),
    (r"beweist (?:aber )?nicht|belegt (?:aber )?nicht|zeigt (?:aber )?nicht", "Rücknahme"),
    (r"[Nn]icht dokumentiert ist|[Dd]okumentiert ist, dass", "Rücknahme"),
    (r"noch kein Beleg|kein Beleg für", "Rücknahme"),
    (r"—\s*(?:nicht|kein)\b|,\s*nicht\s+\w+\.$", "Gedankenstrich-Gegensatz"),
]

# § 2: Produktionsbuchhaltung
BUCHHALTUNG = re.compile(
    r"frei nutzbares Porträt|kein verlässlich identifiziert|"
    r"nicht mit einem erfundenen Gesicht|liegt uns nicht vor", re.I)


def saetze(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    p = Path(sys.argv[1])
    text = p.read_text(encoding="utf-8").strip()
    ss = saetze(text)
    woerter = len(text.split())
    befunde = 0

    print(f"{p.name}\n{woerter} Wörter · {len(ss)} Sätze\n")

    print("— Antithese (§ 2) —")
    treffer = 0
    for i, s in enumerate(ss[:-1]):
        if ist_antithese(s, ss[i + 1]):
            print(f"  [{i}] {s}")
            print(f"       {ss[i+1]}")
            treffer += 1
    # Kurzform ohne Folgesatz: "Nicht poetisch, konkret."
    for i, s in enumerate(ss):
        if STOPP.match(s) and len(s) < 60:
            print(f"  [{i}] {s}")
            treffer += 1
    print(f"  → {treffer} Treffer" + ("  ✓" if treffer == 0 else "  ← ersetzen"))
    befunde += treffer

    print("\n— Rücknahmesätze (§ 2) —")
    treffer = 0
    for muster, art in RUECKNAHME:
        for i, s in enumerate(ss):
            if re.search(muster, s):
                print(f"  [{i}] {art}: {s[:96]}")
                treffer += 1
    print(f"  → {treffer} Treffer" + ("  ✓" if treffer == 0 else "  ← ersetzen"))
    befunde += treffer

    print("\n— Produktionsbuchhaltung (§ 2) —")
    treffer = sum(1 for s in ss if BUCHHALTUNG.search(s))
    for s in ss:
        if BUCHHALTUNG.search(s):
            print(f"  {s[:96]}")
    print(f"  → {treffer} Treffer" + ("  ✓" if treffer == 0 else "  ← streichen"))
    befunde += treffer

    print("\n— Interaktion (§ 1) —")
    fragen = sum(1 for s in ss if s.endswith("?"))
    cta = bool(re.search(r"[Kk]ommentar|[Ss]chreib (?:mir|es)", text))
    print(f"  Fragen: {fragen}" + ("  ✓" if fragen >= 7 else "  ← Ziel ≥ 7"))
    print(f"  CTA im Text: {'ja  ✓' if cta else 'nein  ← fehlt'}")
    if fragen < 7:
        befunde += 1
    if not cta:
        befunde += 1

    print("\n— Umfang (§ 1) —")
    ok = 1300 <= woerter <= 1450
    print(f"  {woerter} Wörter" + ("  ✓" if ok else "  ← Ziel 1.300–1.450"))

    print(f"\n{'BESTANDEN' if befunde == 0 else str(befunde) + ' Punkte offen'}")
    return 0 if befunde == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
