#!/usr/bin/env python3
"""Prueft eine Timeline auf Bildwiederholungen.

    python tools/gw_wiederholungen.py 06_PRODUCTION/EP0X_.../timeline/..._timeline.json

Zielwerte aus `01_GLOBAL/00_PRODUKTIONSSTANDARD.md` § 3:
mindestens 85 Einzelbilder, kein Motiv oefter als viermal, und innerhalb
eines Akts kein Motiv zweimal.
"""

from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

ZIEL_EINZELBILDER = 85
MAX_WIEDERHOLUNG = 4


def basename(p: str) -> str:
    return os.path.basename(p.replace("\\", "/"))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    rows = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    namen = [basename(r["visual"]) for r in rows]
    zaehler = collections.Counter(namen)
    dauer = sum(r["duration"] for r in rows)

    print(f"{len(rows)} Shots · {dauer/60:.0f}:{dauer%60:04.1f} · "
          f"Ø {dauer/len(rows):.2f}s\n")

    einzel = len(zaehler)
    hoechste = max(zaehler.values())
    print(f"Einzelbilder: {einzel}"
          + ("  ✓" if einzel >= ZIEL_EINZELBILDER else f"  ← Ziel ≥ {ZIEL_EINZELBILDER}"))
    print(f"Höchste Wiederholung: {hoechste}×"
          + ("  ✓" if hoechste <= MAX_WIEDERHOLUNG else f"  ← Ziel ≤ {MAX_WIEDERHOLUNG}×"))

    print("\n— Mehrfach genutzt —")
    for name, n in zaehler.most_common():
        if n < 2:
            break
        szenen = [r["scene"] for r in rows if basename(r["visual"]) == name]
        doppelt = [s for s, c in collections.Counter(szenen).items() if c > 1]
        flag = "  ← zweimal im selben Akt" if doppelt else ""
        print(f"  {n}×  {name:<48} {sorted(set(szenen))}{flag}")

    print("\n— Direkt aufeinanderfolgend —")
    # Ein Bewegtbild ueber zwei Anker zu halten ist gewollt — die Animation
    # laeuft dann weiter. Zwei gleiche Standbilder hintereinander sind ein
    # Schnitt, der nichts bewirkt.
    folge = [(rows[i]["shot_id"], basename(rows[i]["visual"]))
             for i in range(1, len(rows))
             if rows[i]["visual"] == rows[i - 1]["visual"]
             and rows[i].get("kind") != "VIDEO"]
    print(f"  {len(folge)} Stellen" + ("  ✓" if not folge else ""))
    for sid, nm in folge:
        print(f"    {sid}  {nm}")

    print("\n— Verteilung —")
    art = collections.Counter()
    for r in rows:
        v = r["visual"].replace("\\", "/")
        if r.get("kind") == "VIDEO":
            art["Bewegtbild"] += r["duration"]
        elif "/cards/" in v:
            art["Karte"] += r["duration"]
        elif "/documents/" in v or "reference_package" in v:
            art["Dokument"] += r["duration"]
        elif "AI_FINAL" in v or "/generated/" in v:
            art["Rekonstruktion"] += r["duration"]
        else:
            art["sonstiges"] += r["duration"]
    for k, v in art.most_common():
        print(f"  {k:<16}{v:6.1f}s  {100*v/dauer:4.1f} %")

    fehler = (einzel < ZIEL_EINZELBILDER) + (hoechste > MAX_WIEDERHOLUNG) + bool(folge)
    print(f"\n{'BESTANDEN' if not fehler else str(fehler) + ' Punkte offen'}")
    return 0 if not fehler else 1


if __name__ == "__main__":
    sys.exit(main())
