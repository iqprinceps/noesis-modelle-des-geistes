#!/usr/bin/env python3
"""Gateway V7 — prozedurale Bewegtbilder.

V5 hatte vier HTML-Canvas-Simulationen im Ordner `motion_clips`, die nie
gerendert wurden; stattdessen liefen drei Pexels-Stockclips im Schnitt.
Hier entstehen die Bewegtbilder direkt: Frames mit numpy/PIL, dann ffmpeg.
Kein Browser noetig, deterministisch, exakt in der Markenpalette.

Vier Clips:
  binaural   zwei Toene werden zur Schwebung — traegt Akt 3
  resonanz   Bentovs Koerper als schwingender Oszillator — Akt 2
  zeitrad    Focus 15, Speichen in die Vergangenheit — Akt 5
  feld       Rauschen ordnet sich zu einem Gitter — Akt 4, der Sprung
"""

from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V7" / "motion"
TMP = OUT / "_frames"

W, H, FPS = 1920, 1080, 30
NAVY = (4, 17, 20)
CYAN = (91, 210, 211)
GOLD = (224, 174, 71)
WHITE = (238, 235, 224)


def run(args):
    p = subprocess.run(args, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-4000:])


def backdrop() -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * .3, -H * .45, W * 1.3, H * 1.45], fill=255)
    return Image.composite(img, Image.new("RGB", (W, H), (2, 9, 11)),
                           v.filter(ImageFilter.GaussianBlur(200)))


def encode(name: str, seconds: float):
    """Frames -> mp4. Loop-tauglich, weil alle Clips periodisch sind."""
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{name}.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-framerate", str(FPS), "-i", str(TMP / "f_%05d.png"),
         "-t", f"{seconds:.3f}", "-c:v", "libx264", "-preset", "slow",
         "-crf", "16", "-pix_fmt", "yuv420p", str(target)])
    shutil.rmtree(TMP, ignore_errors=True)
    print(f"  {name}.mp4  {seconds:.1f}s")
    return target


def frames_start():
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)


def grain(img: Image.Image, amount=4) -> Image.Image:
    a = np.asarray(img).astype(np.int16)
    rng = np.random.default_rng(7)
    return Image.fromarray(np.clip(a + rng.integers(-amount, amount + 1, a.shape[:2])[:, :, None],
                                   0, 255).astype("uint8"))


# --------------------------------------------------------------- binaural

def binaural(seconds=9.0):
    """400 Hz links, 410 Hz rechts, darunter die Schwebung mit 10 Hz."""
    frames_start()
    n = int(seconds * FPS)
    base = backdrop()
    for k in range(n):
        t = k / FPS
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        for y0, freq, col, lbl in ((300, 21.0, CYAN, "LINKS"), (540, 21.5, CYAN, "RECHTS")):
            pts = [(x, y0 + 62 * math.sin(2 * math.pi * (freq * (x - 260) / 1400 - t * 0.55)))
                   for x in range(260, 1680, 3)]
            d.line(pts, fill=col + (215,), width=3, joint="curve")
        # Schwebung: Traeger mit langsamer Huellkurve. Die Differenz der
        # beiden Frequenzen ist im Bild zu klein, um sichtbar zu werden —
        # deshalb wird sie hier auf vier Perioden ueber die Breite gestreckt.
        pts = []
        for x in range(260, 1680, 3):
            u = (x - 260) / 1400
            env = abs(math.cos(math.pi * (4.0 * u - t * 0.55)))
            pts.append((x, 830 + 128 * env * math.sin(2 * math.pi * (21.25 * u - t * 0.55))))
        d.line(pts, fill=GOLD + (240,), width=4, joint="curve")
        # wandernder Lesekopf
        px = 260 + (t * 235) % 1420
        d.line([(px, 214), (px, 946)], fill=(255, 255, 255, 34), width=2)
        grain(img).save(TMP / f"f_{k:05d}.png")
    return encode("binaural", seconds)


# --------------------------------------------------------------- resonanz

def resonanz(seconds=8.0):
    """Ein Oszillator im Zentrum, Wellen laufen nach aussen — Bentov."""
    frames_start()
    n = int(seconds * FPS)
    base = backdrop()
    cx, cy = W // 2, H // 2
    for k in range(n):
        t = k / FPS
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        puls = 0.5 + 0.5 * math.sin(2 * math.pi * t / 1.1)      # Herzschlag
        for i in range(18):
            phase = (t / 2.6 + i / 18) % 1.0
            r = 70 + phase * 1180
            a = int(190 * (1 - phase) ** 1.7)
            if a < 6:
                continue
            col = GOLD if i % 5 == 0 else CYAN
            d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62],
                      outline=col + (a,), width=2)
        rr = 26 + 12 * puls
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=GOLD + (235,))
        d.ellipse([cx - rr * 2.3, cy - rr * 2.3, cx + rr * 2.3, cy + rr * 2.3],
                  outline=GOLD + (int(90 * puls),), width=3)
        grain(img).save(TMP / f"f_{k:05d}.png")
    return encode("resonanz", seconds)


# ---------------------------------------------------------------- zeitrad

def zeitrad(seconds=10.0):
    """Nabe = Gegenwart, Speichen fuehren in die Vergangenheit."""
    frames_start()
    n = int(seconds * FPS)
    base = backdrop()
    cx, cy, R = W // 2, H // 2, 660
    for k in range(n):
        t = k / FPS
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        rot = t * 0.085
        for i in range(16):
            ang = 2 * math.pi * i / 16 + rot
            gl = 0.5 + 0.5 * math.sin(2 * math.pi * (t / 3.4) - i * 0.52)
            a = int(60 + 150 * gl)
            x2, y2 = cx + R * math.cos(ang), cy + R * 0.58 * math.sin(ang)
            d.line([(cx, cy), (x2, y2)], fill=CYAN + (a,), width=2)
            rr = 10 + 12 * gl
            d.ellipse([x2 - rr, y2 - rr, x2 + rr, y2 + rr], fill=CYAN + (a,))
        for f in (1.0, 0.74, 0.48):
            d.ellipse([cx - R * f, cy - R * .58 * f, cx + R * f, cy + R * .58 * f],
                      outline=(38, 82, 90, 190), width=2)
        d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=GOLD + (240,))
        grain(img).save(TMP / f"f_{k:05d}.png")
    return encode("zeitrad", seconds)


# ------------------------------------------------------------------- feld

def feld(seconds=9.0):
    """Rauschen ordnet sich zu einem Gitter und zerfaellt wieder.

    Bildlogik fuer den Satz, an dem die Akte den Sprung macht: aus
    ungeordneter Aktivitaet wird ein kohaerentes Muster.
    """
    frames_start()
    n = int(seconds * FPS)
    base = backdrop()
    rng = np.random.default_rng(23)
    cols, rows = 26, 15
    jitter = rng.normal(0, 1, (rows, cols, 2))
    for k in range(n):
        t = k / FPS
        # 0 = Chaos, 1 = Ordnung; einmal hin und zurueck
        ordn = 0.5 - 0.5 * math.cos(2 * math.pi * t / seconds)
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        pts = np.zeros((rows, cols, 2))
        for r in range(rows):
            for c in range(cols):
                gx = 190 + c * (1540 / (cols - 1))
                gy = 150 + r * (780 / (rows - 1))
                amp = 128 * (1 - ordn)
                pts[r, c] = (gx + jitter[r, c, 0] * amp
                             + 18 * math.sin(t * 1.2 + r * .6 + c * .3),
                             gy + jitter[r, c, 1] * amp
                             + 18 * math.cos(t * 1.0 + c * .5))
        la = int(150 * ordn)
        if la > 5:
            for r in range(rows):
                for c in range(cols - 1):
                    d.line([tuple(pts[r, c]), tuple(pts[r, c + 1])],
                           fill=CYAN + (la,), width=1)
            for c in range(cols):
                for r in range(rows - 1):
                    d.line([tuple(pts[r, c]), tuple(pts[r + 1, c])],
                           fill=CYAN + (la,), width=1)
        for r in range(rows):
            for c in range(cols):
                x, y = pts[r, c]
                rr = 2.0 + 2.2 * ordn
                col = GOLD if (r * cols + c) % 37 == 0 else CYAN
                d.ellipse([x - rr, y - rr, x + rr, y + rr],
                          fill=col + (int(110 + 130 * ordn),))
        grain(img).save(TMP / f"f_{k:05d}.png")
    return encode("feld", seconds)


def main():
    print("Baue Bewegtbilder:")
    binaural()
    resonanz()
    zeitrad()
    feld()
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
