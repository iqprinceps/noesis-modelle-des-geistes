#!/usr/bin/env python3
"""Vertical 9:16 plates cut from the acquired originals.

The teaser is carried by reconstructions, but the claims in it are carried by
photographs: the crown with the projectile actually in it, and the two popes who
actually read the envelope and said nothing. A reconstruction cannot do that work,
because the whole point of those beats is that the thing is real.

Most of these originals are already portrait, several within a few percent of
9:16, so cropping costs almost nothing. The crown is the exception: it is a wide
frame and the crop is deliberately tight on the projectile, which is the only part
of it the teaser is about.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01" / "03_VISUALS" / "ASSETS" / "SELECTED" / "AUTHENTIC"
OUT = ROOT / "tmp" / "imagegen" / "ep13_short_plates"
AR = 9 / 16

# id, source file, focus x, focus y, zoom, what it is for
PLATES = [
    ("OR01_CROWN_BULLET", "EP13_HA01_crown_bullet_CTV_2017.png", 0.534, 0.497, 1.0,
     "the real crown, cropped tight on the real projectile"),
    ("OR02_JOHN_XXIII", "EP13_Pope_John_XXIII_1959_jpg.jpg", 0.50, 0.42, 1.0,
     "the first pope who read it and did not publish it"),
    ("OR03_PAUL_VI", "EP13_Pope_Paul_VI_visiting_U_N_United_Nations_New_York_LCCN2020732639_jpg.jpg",
     0.50, 0.35, 1.0, "the second pope who read it and sent it back"),
    ("OR04_CHILDREN_1917", "EP13_Children_of_F_tima_portrait_Attributed_to_Joshua_Benoliel_Ilustra_o_Po.jpg",
     0.50, 0.45, 1.0, "the three children, 1917"),
    ("OR05_FIRST_STATUE", "EP13_X_First_Sculpture_of_Our_Lady_of_Fatima_jpg.jpg", 0.50, 0.45, 1.0,
     "the first sculpture of Our Lady of Fatima"),
    ("OR06_CROWNED_STATUE", "EP13_20190530_Spain_and_Portugal_El_Camino_Pilgrimage_0300_48002497997_.jpg",
     0.50, 0.30, 1.0, "the crowned statue, upright"),
    ("OR07_NEWSPAPER_1917", "EP13_Newspaper_fatima_353_jpg.jpg", 0.50, 0.40, 1.0,
     "a 1917 newspaper page on the reported apparitions"),
]


def plate(src: pathlib.Path, fx: float, fy: float, zoom: float) -> Image.Image:
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = im.size
    # widest 9:16 window the source can give, then the requested zoom on top
    cw = min(w, h * AR) / zoom
    ch = cw / AR
    if ch > h:
        ch = h
        cw = ch * AR
    cx, cy = w * fx, h * fy
    left = min(max(0.0, cx - cw / 2), w - cw)
    top = min(max(0.0, cy - ch / 2), h - ch)
    box = im.crop((round(left), round(top), round(left + cw), round(top + ch)))
    if box.width < 1080:
        box = box.resize((1080, round(1080 / AR)), Image.LANCZOS)
    return box


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(OUT))
    a = ap.parse_args()
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for pid, name, fx, fy, zoom, why in PLATES:
        src = SRC / name
        if not src.is_file():
            print(f"MISSING {name}")
            continue
        img = plate(src, fx, fy, zoom)
        dest = outdir / f"EP13_{pid}.png"
        img.save(dest)
        b = dest.read_bytes()
        rows.append({"plate_id": pid, "file": dest.name, "source": name,
                     "size": f"{img.width}x{img.height}", "bytes": len(b),
                     "sha256": hashlib.sha256(b).hexdigest(), "purpose": why})
        print(f"OK  {pid:20s} {img.width}x{img.height}  {why}")
    with (outdir / "PLATE_MANIFEST.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} plates -> {outdir}")


if __name__ == "__main__":
    main()
