#!/usr/bin/env python3
"""Sucht Bilder, in denen Polarlichtfarbe im Innenraum liegt.

Magenta-, Cyan- und Gruenbaender ueber Tisch, Papier, Hand oder Gesicht sind
die Stelle, an der ein erzeugtes Bild sofort auffliegt. Bei EP01A trugen elf
Motive diese Signatur, und der erste Zuschauerbefund war genau der: "man
sieht sofort, dass es KI-Bilder sind".

Gemessen wird der Anteil der Pixel mit hoher Saettigung im Farbbereich
Magenta bis Cyan. Der Wert allein entscheidet nichts — ein Polarlicht ueber
dem Eis gehoert nach oben in die Liste, eine Kuechenszene nicht. Die Liste
ist zum Ansehen, nicht zum blinden Aussortieren.

    python tools/spg_neonpruefung.py <timeline.json> [--grenze 8]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def anteil(pfad: pathlib.Path) -> float:
    """Anteil kraeftiger Magenta- und Cyanpixel, 0 bis 1."""
    im = Image.open(pfad).convert("RGB")
    im.thumbnail((320, 320))
    a = np.asarray(im).astype("float32") / 255
    hell, dunkel = a.max(2), a.min(2)
    saettigung = np.where(hell > 0, (hell - dunkel) / np.maximum(hell, 1e-6), 0)
    h = np.asarray(im.convert("HSV")).astype("float32")[..., 0] * 360 / 255
    bunt = ((saettigung > 0.45) & (hell > 0.25)
            & (((h > 250) & (h < 340)) | ((h > 150) & (h < 210))))
    return float(bunt.mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("--grenze", type=float, default=8.0,
                    help="ab welchem Prozentwert gelistet wird")
    args = ap.parse_args()

    tl = json.loads(pathlib.Path(args.timeline).read_text(encoding="utf-8"))
    rows = tl["shots"] if isinstance(tl, dict) else tl
    pfade = sorted({r["visual"] for r in rows
                    if r["visual"].endswith(".png") and "generated" in r["visual"]})

    werte = sorted(((anteil(pathlib.Path(p)) * 100, pathlib.Path(p).stem)
                    for p in pfade), reverse=True)

    print(f"{len(werte)} erzeugte Motive · Anteil kraeftiges Magenta/Cyan\n")
    for v, n in werte:
        if v < args.grenze:
            break
        print(f"  {v:5.1f} %  {n}")
    print("\nHimmel und Visionen duerfen hier oben stehen. Ein Innenraum in "
          "dieser Liste wird angesehen und in aller Regel neu erzeugt.")


if __name__ == "__main__":
    main()
