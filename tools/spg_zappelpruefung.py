#!/usr/bin/env python3
"""Prueft, ob die Kamerafahrten glatt laufen oder in Stufen.

Der erste Zuschauerbefund zu EP01A war "die Kamerabewegung zappelt und
wackelt". Die Ursache lag in `zoompan`: seine x- und y-Werte sind
ganzzahlig, und bei einem Bild in Ausgabegroesse ist ein Schritt ein voller
Ausgabepixel.

Die naheliegende Kennzahl — die Streuung der Bilddifferenzen — taugt hier
nicht. Eine Fahrt mit weichen Enden aendert ihre Geschwindigkeit
absichtlich, und das schlaegt in der Streuung genauso durch wie echtes
Zappeln. Gemessen wird deshalb die **zweite Differenz**: wie stark sich die
Bilddifferenz von einem Bild zum naechsten aendert, im Verhaeltnis zum
Mittel. Eine weiche Beschleunigung liegt tief, ein Hin und Her von Bild zu
Bild hoch.

Richtwerte nach Produktionsstandard § 3: Median unter 0,10, kein Segment
ueber 0,20 — jeweils fuer Segmente mit einer Bilddifferenz ab 1,0. Darunter
ist die Kennzahl nicht aussagekraeftig, weil das Encoder-Rauschen im
Verhaeltnis zu gross wird.

    python tools/spg_zappelpruefung.py <timeline.json> [--segmente <ordner>]
"""

from __future__ import annotations

import argparse
import io
import json
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GRENZE_MEDIAN = 0.10
GRENZE_EINZEL = 0.20
MINDESTBEWEGUNG = 1.0


def bilder(pfad: pathlib.Path, anzahl: int = 120) -> list[np.ndarray]:
    """Graustufenbilder eines Segments, klein gerechnet."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(pfad),
                        "-frames:v", str(anzahl), "-vf", "scale=480:270",
                        "-f", "image2pipe", "-vcodec", "bmp", "-"],
                       capture_output=True)
    buf, out, i = r.stdout, [], 0
    while i < len(buf) - 6 and buf[i:i + 2] == b"BM":
        groesse = int.from_bytes(buf[i + 2:i + 6], "little")
        out.append(np.asarray(Image.open(io.BytesIO(buf[i:i + groesse])).convert("L"))
                   .astype("int16"))
        i += groesse
    return out


def messen(pfad: pathlib.Path, blende: bool) -> tuple[float, float] | None:
    """(Zappeln, mittlere Bilddifferenz) oder None, wenn nicht messbar."""
    fs = bilder(pfad)
    if len(fs) < 6:
        return None
    d = np.array([np.abs(fs[i] - fs[i - 1]).mean() for i in range(1, len(fs))])
    if blende and len(d) > 26:
        d = d[10:-10]                      # Auf- und Abblende verzerren sonst
    if len(d) < 6 or d.mean() < 0.4:
        return None
    return float(np.abs(np.diff(d)).mean() / d.mean()), float(d.mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("--segmente", default="")
    args = ap.parse_args()

    tl_pfad = pathlib.Path(args.timeline)
    tl = json.loads(tl_pfad.read_text(encoding="utf-8"))
    rows = tl["shots"] if isinstance(tl, dict) else tl
    seg = pathlib.Path(args.segmente) if args.segmente else \
        tl_pfad.parent.parent / "render" / "segments"

    werte = []
    for i, row in enumerate(rows):
        pfad = seg / f"{i + 1:03d}_{row['shot_id']}.mp4"
        if not pfad.is_file():
            continue
        ergebnis = messen(pfad, bool(row.get("scene_first") or row.get("scene_last")))
        if ergebnis:
            werte.append((pfad.stem, *ergebnis, row))

    aussagekraeftig = [w for w in werte if w[2] >= MINDESTBEWEGUNG]
    if not aussagekraeftig:
        raise SystemExit("Keine messbaren Segmente gefunden.")

    v = np.array([w[1] for w in aussagekraeftig])
    ueber = [w for w in aussagekraeftig if w[1] > GRENZE_EINZEL]

    print(f"{len(werte)} Segmente gemessen, davon {len(aussagekraeftig)} mit "
          f"Bilddifferenz ab {MINDESTBEWEGUNG}\n")
    print(f"  Zappeln   Mittel {v.mean():6.3f}   Median {np.median(v):6.3f}")
    print(f"  ueber {GRENZE_EINZEL}: {len(ueber)}")

    if ueber:
        print("\nunruhigste:")
        for name, z, m, row in sorted(ueber, key=lambda w: -w[1])[:10]:
            print(f"  {name}  Zappeln {z:6.3f}  Differenz {m:5.2f}  "
                  f"{pathlib.Path(row['visual']).name}")

    gut = np.median(v) <= GRENZE_MEDIAN and not ueber
    print("\n" + ("BESTANDEN" if gut else "NICHT BESTANDEN"))
    if not gut:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
