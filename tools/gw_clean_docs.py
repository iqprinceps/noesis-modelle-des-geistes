#!/usr/bin/env python3
"""Entfernt die eingebrannten englischen Kopf- und Fusszeilen aus den
Dokument- und Patentbildern.

V4/V5 hatten Titel wie "Army header, date and subject" und ein Badge
"IN THE REPORT" fest im PNG. Zusammen mit der neuen deutschen Einblendung
in V6 stuende oben Englisch und unten Deutsch — doppelt beschriftet.

Das Dokument selbst liegt sicher zwischen y=300 und y=860; die Beschriftung
sitzt ausserhalb. Wir uebermalen nur die Randbaender mit der exakten
Hintergrundfarbe und tasten das Dokument nicht an.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC_DIRS = [
    ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V5" / "visuals" / "document_crops",
    ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V5" / "visuals" / "patents",
    ROOT / "06_PRODUCTION" / "EP02_GATEWAY" / "reference_package",
]
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V6" / "visuals" / "documents"

TOP = 150          # oberes Band inkl. Titel und Badge
BOTTOM_FROM = 1006  # unteres Band mit der Quellzeile
SAFE_TOP, SAFE_BOTTOM = 300, 860   # hier darf nie uebermalt werden


def content_rows(im: Image.Image, bg: tuple[int, int, int]) -> list[int]:
    px = im.load()
    rows = []
    for y in range(0, im.height, 2):
        if max(abs(sum(px[x, y]) - sum(bg)) for x in range(0, im.width, 8)) > 30:
            rows.append(y)
    return rows


def clean(path: Path) -> tuple[bool, str]:
    im = Image.open(path).convert("RGB")
    if im.size != (1920, 1080):
        return False, f"uebersprungen (Groesse {im.size})"
    bg = im.getpixel((6, 6))
    rows = content_rows(im, bg)
    if not rows:
        return False, "uebersprungen (kein Inhalt erkannt)"
    # Sicherheitsnetz: nichts anfassen, wenn das Dokument bis in die Baender reicht
    if min(rows) < 40 or max(rows) > 1070:
        return False, "uebersprungen (Inhalt reicht in die Raender)"
    d = ImageDraw.Draw(im)
    painted = []
    if any(y < TOP for y in rows):
        d.rectangle((0, 0, im.width, TOP), fill=bg)
        painted.append("oben")
    if any(y > BOTTOM_FROM for y in rows):
        d.rectangle((0, BOTTOM_FROM, im.width, im.height), fill=bg)
        painted.append("unten")
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / path.name)
    return True, ("bereinigt " + "+".join(painted)) if painted else "kopiert (nichts zu tun)"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    n_clean = n_copy = 0
    for d in SRC_DIRS:
        for p in sorted(d.glob("*.png")):
            ok, msg = clean(p)
            if ok:
                if "bereinigt" in msg:
                    n_clean += 1
                else:
                    n_copy += 1
            else:
                shutil.copy2(p, OUT / p.name)
                n_copy += 1
            print(f"  {p.name:<42} {msg}")
    print(f"\n{n_clean} bereinigt, {n_copy} unveraendert uebernommen -> {OUT}")


if __name__ == "__main__":
    main()
