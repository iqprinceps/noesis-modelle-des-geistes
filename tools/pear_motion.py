#!/usr/bin/env python3
"""EP03 PEAR — prozedurale Bewegtbilder.

Abgeleitet von `tools/spg_motion.py`; die Vorlage bleibt unveraendert.
Gleiche Bauweise — Frames mit numpy und PIL, dann ffmpeg, kein Browser,
deterministisch — aber in der Palette dieser Folge.

Vier Clips. Jeder erklaert genau einen Begriff, der sonst nur behauptet
wuerde. Genau dafuer sind sie da; ein Clip, der nur huebsch ist, kommt nicht
in den Schnitt.

  muenzwurf    Zweihundert Bits fallen als Raster ein, etwa halb hell, halb
               dunkel. Das ist ein einzelner Versuch, und man sieht sofort:
               daran ist nichts Auffaelliges.
  abweichung   Dieselben Versuche, uebereinandergelegt. Eine Linie, die
               zittert, gegen null zurueckfaellt — und ueber sehr viele
               Durchgaenge doch nicht mehr ganz zurueckkommt.
  kaskade      Kugeln fallen durch ein Stiftraster in Faecher und bauen die
               Glockenkurve auf. Das Prinzip der Kugelwand in einem Bild.
  rauschen     Das elektrische Rauschen der Diode als Oszilloskopspur, aus
               dem die Nullen und Einsen geschnitten werden.

    python tools/pear_motion.py            # alle vier
    python tools/pear_motion.py kaskade    # einzeln
"""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP03_PEAR" / "motion"
TMP = ROOT / "06_PRODUCTION" / "EP03_PEAR" / "motion" / "_frames"

W, H, FPS = 1920, 1080, 30

# Palette der Folge: Institutsgrau, Bernstein der Schreibtischlampe, das Rot
# der Leuchtziffern, das Gruen des Bildschirmphosphors.
GRUND = (14, 16, 19)
GRUND_L = (26, 29, 34)
BERNSTEIN = (232, 176, 84)
BERNSTEIN_D = (128, 92, 40)
ROT = (226, 78, 58)
PHOSPHOR = (126, 224, 150)
PAPIER = (232, 226, 210)
DIM = (120, 126, 134)


def run(args):
    p = subprocess.run(args, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-4000:])


def backdrop() -> Image.Image:
    """Dunkles Institutsgrau mit leichtem Verlauf und weicher Vignette."""
    img = Image.new("RGB", (W, H), GRUND)
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=int(255 * (1 - y / H) ** 1.5))
    img = Image.composite(Image.new("RGB", (W, H), GRUND_L), img, grad)
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * .30, -H * .45, W * 1.30, H * 1.45], fill=255)
    return Image.composite(img, Image.new("RGB", (W, H), (7, 8, 10)),
                           v.filter(ImageFilter.GaussianBlur(200)))


def grain(img: Image.Image, amount=4) -> Image.Image:
    a = np.asarray(img).astype(np.int16)
    rng = np.random.default_rng(11)
    return Image.fromarray(
        np.clip(a + rng.integers(-amount, amount + 1, a.shape[:2])[:, :, None],
                0, 255).astype("uint8"))


def frames_start():
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)


def encode(name: str, seconds: float):
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{name}.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-framerate", str(FPS), "-i", str(TMP / "f_%05d.png"),
         "-t", f"{seconds:.3f}", "-c:v", "libx264", "-preset", "slow",
         "-crf", "16", "-pix_fmt", "yuv420p", str(target)])
    shutil.rmtree(TMP, ignore_errors=True)
    print(f"  {name}.mp4  {seconds:.1f}s")
    return target


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def weich(t: float) -> float:
    return t * t * (3 - 2 * t)


# --------------------------------------------------------------- muenzwurf

def muenzwurf(seconds=9.0):
    """Zweihundert Bits als Raster. Etwa die Haelfte hell — und das war's."""
    frames_start()
    n = int(seconds * FPS)
    rng = np.random.default_rng(3)
    spalten, zeilen = 20, 10                       # 200 Bits
    zellw, zellh = 62, 62
    x0 = (W - spalten * zellw) // 2
    y0 = (H - zeilen * zellh) // 2 + 20
    # Fuer jeden Durchgang eine neue Zufallsbelegung; alle 2,2 s ein neuer
    runde_dauer = int(2.2 * FPS)
    runden = {}
    for r in range(n // runde_dauer + 2):
        runden[r] = rng.random(spalten * zeilen) < 0.5

    grund = backdrop()
    for f in range(n):
        img = grund.copy()
        d = ImageDraw.Draw(img, "RGBA")
        r, in_runde = divmod(f, runde_dauer)
        bits = runden[r]
        # Bits erscheinen nacheinander, dann steht das Raster kurz
        sichtbar = min(len(bits), int(len(bits) * min(1.0, in_runde / (runde_dauer * 0.45))))
        for i in range(sichtbar):
            cx = x0 + (i % spalten) * zellw + zellw // 2
            cy = y0 + (i // spalten) * zellh + zellh // 2
            an = bool(bits[i])
            alter = sichtbar - i
            frisch = max(0.0, 1.0 - alter / 26.0)
            rad = 17
            if an:
                farbe = mix(BERNSTEIN_D, BERNSTEIN, 0.35 + 0.65 * frisch)
                d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=farbe + (255,))
            else:
                d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                          outline=DIM + (150,), width=2)
        # Zaehlbalken unten: wie weit weicht diese Runde von der Haelfte ab
        if in_runde > runde_dauer * 0.5:
            treffer = int(bits.sum())
            abw = (treffer - len(bits) / 2) / (len(bits) / 2)   # -1 .. +1
            t = weich(min(1.0, (in_runde - runde_dauer * 0.5) / (runde_dauer * 0.25)))
            mitte = W // 2
            breite = int(abw * 260 * t)
            by = y0 + zeilen * zellh + 64
            d.line([(mitte - 300, by), (mitte + 300, by)], fill=DIM + (110,), width=2)
            d.line([(mitte, by - 16), (mitte, by + 16)], fill=DIM + (190,), width=2)
            if breite:
                d.rectangle([min(mitte, mitte + breite), by - 7,
                             max(mitte, mitte + breite), by + 7],
                            fill=mix(BERNSTEIN_D, BERNSTEIN, 0.7) + (int(230 * t),))
        img = grain(img)
        img.save(TMP / f"f_{f:05d}.png")
    return encode("muenzwurf", seconds)


# -------------------------------------------------------------- abweichung

def abweichung(seconds=11.0):
    """Eine Linie, die zittert und ueber sehr viele Schritte nicht heimkehrt."""
    frames_start()
    n = int(seconds * FPS)
    rng = np.random.default_rng(17)
    punkte = 1400
    schritt = rng.normal(0.0, 1.0, punkte)
    schritt += 0.055                                # winziger Zug nach oben
    kurve = np.cumsum(schritt)
    kurve = kurve / max(abs(kurve).max(), 1e-6)     # -1 .. +1

    x0, x1 = 180, W - 180
    mitte_y = H // 2 + 40
    hoehe = 300

    grund = backdrop()
    for f in range(n):
        img = grund.copy()
        d = ImageDraw.Draw(img, "RGBA")
        # Nulllinie
        d.line([(x0, mitte_y), (x1, mitte_y)], fill=DIM + (95,), width=2)
        t = weich(min(1.0, f / (n * 0.86)))
        bis = max(2, int(punkte * t))
        pts = [(x0 + (x1 - x0) * i / (punkte - 1), mitte_y - kurve[i] * hoehe)
               for i in range(bis)]
        # weicher Schatten unter der Linie
        d.line(pts, fill=BERNSTEIN_D + (120,), width=9, joint="curve")
        d.line(pts, fill=BERNSTEIN + (255,), width=3, joint="curve")
        # Kopf der Linie
        hx, hy = pts[-1]
        d.ellipse([hx - 6, hy - 6, hx + 6, hy + 6], fill=BERNSTEIN + (255,))
        img = img.filter(ImageFilter.GaussianBlur(0.4))
        img = grain(img)
        img.save(TMP / f"f_{f:05d}.png")
    return encode("abweichung", seconds)


# ----------------------------------------------------------------- kaskade

def kaskade(seconds=12.0):
    """Kugeln durch ein Stiftraster, unten waechst die Glockenkurve."""
    frames_start()
    n = int(seconds * FPS)
    rng = np.random.default_rng(23)

    reihen = 12
    faecher = 19
    oben, unten = 150, H - 210
    links, rechts = W // 2 - 470, W // 2 + 470
    zeilen_y = [oben + (unten - oben) * r / reihen for r in range(reihen + 1)]

    # Stiftpositionen
    stifte = []
    for r in range(reihen):
        anz = r + 2
        spanne = (rechts - links) * (anz - 1) / (faecher - 1)
        for i in range(anz):
            x = W // 2 - spanne / 2 + spanne * i / max(1, anz - 1)
            stifte.append((x, zeilen_y[r]))

    # Kugeln: jede bekommt eine Bahn aus Links-Rechts-Entscheidungen
    kugeln = 240
    start = rng.integers(0, int(n * 0.62), kugeln)
    wege = rng.random((kugeln, reihen)) < 0.5
    ziel = wege.sum(axis=1) + (faecher - reihen) // 2
    fallzeit = 46

    fach_b = (rechts - links) / faecher
    stand = np.zeros(faecher, dtype=int)

    grund = backdrop()
    for f in range(n):
        img = grund.copy()
        d = ImageDraw.Draw(img, "RGBA")
        # Rahmen
        d.rectangle([links - 26, oben - 46, rechts + 26, unten + 150],
                    outline=DIM + (110,), width=2)
        # Stifte
        for x, y in stifte:
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=DIM + (170,))
        # Faecherlinien
        for i in range(faecher + 1):
            x = links + fach_b * i
            d.line([(x, unten), (x, unten + 148)], fill=DIM + (85,), width=1)

        # gefallene Kugeln zaehlen
        stand[:] = 0
        for k in range(kugeln):
            if f >= start[k] + fallzeit:
                stand[min(faecher - 1, int(ziel[k]))] += 1
        # Fuellstaende
        for i in range(faecher):
            hoehe_px = min(140, stand[i] * 7)
            if hoehe_px:
                x = links + fach_b * i
                d.rectangle([x + 2, unten + 148 - hoehe_px, x + fach_b - 2, unten + 148],
                            fill=mix(BERNSTEIN_D, BERNSTEIN, 0.55) + (240,))

        # fliegende Kugeln
        for k in range(kugeln):
            dt = f - start[k]
            if 0 <= dt < fallzeit:
                p = dt / fallzeit
                r = min(reihen - 1, int(p * reihen))
                lokal = (p * reihen) - r
                links_x = W // 2
                spanne_o = (rechts - links) * (r + 1) / (faecher - 1)
                # grobe seitliche Wanderung nach den Entscheidungen
                versatz = (wege[k, :r + 1].sum() - (r + 1) / 2) * fach_b * 0.92
                x = W // 2 + versatz
                y = oben + (unten - oben) * p
                d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=PAPIER + (255,))
        img = grain(img)
        img.save(TMP / f"f_{f:05d}.png")
    return encode("kaskade", seconds)


# ---------------------------------------------------------------- rauschen

def rauschen(seconds=9.0):
    """Oszilloskopspur: das Rauschen, aus dem die Bits geschnitten werden."""
    frames_start()
    n = int(seconds * FPS)
    rng = np.random.default_rng(29)
    breite = W - 300
    x0 = 150
    mitte_y = H // 2

    # durchgehendes Rauschband, laeuft von rechts nach links durch
    lang = breite * 4
    roh = rng.normal(0, 1, lang)
    # leicht geglaettet, damit es wie ein Verstaerkerausgang aussieht
    kern = np.array([0.25, 0.5, 0.25])
    roh = np.convolve(roh, kern, mode="same")
    roh = roh / max(abs(roh).max(), 1e-6)

    schwelle = 0.12
    grund = backdrop()
    for f in range(n):
        img = grund.copy()
        d = ImageDraw.Draw(img, "RGBA")
        # Raster
        for i in range(1, 10):
            x = x0 + breite * i / 10
            d.line([(x, mitte_y - 260), (x, mitte_y + 260)], fill=(40, 46, 44, 130), width=1)
        for i in range(-2, 3):
            y = mitte_y + i * 110
            d.line([(x0, y), (x0 + breite, y)], fill=(40, 46, 44, 130), width=1)
        # Schwelle
        sy = mitte_y - schwelle * 220
        d.line([(x0, sy), (x0 + breite, sy)], fill=ROT + (150,), width=2)

        versatz = int(f * 9) % (lang - breite)
        ausschnitt = roh[versatz:versatz + breite:2]
        pts = [(x0 + 2 * i, mitte_y - v * 220) for i, v in enumerate(ausschnitt)]
        d.line(pts, fill=PHOSPHOR + (70,), width=7, joint="curve")
        d.line(pts, fill=PHOSPHOR + (255,), width=2, joint="curve")

        # Bits am unteren Rand: was oberhalb der Schwelle lag, wird hell
        by = mitte_y + 330
        schrittw = 26
        for i in range(0, len(ausschnitt), 24):
            an = ausschnitt[i] > schwelle
            bx = x0 + 2 * i
            if bx > x0 + breite - 10:
                break
            d.rectangle([bx, by, bx + schrittw - 6, by + 26],
                        fill=(BERNSTEIN + (235,)) if an else (0, 0, 0, 0),
                        outline=DIM + (150,), width=1)
        img = img.filter(ImageFilter.GaussianBlur(0.5))
        img = grain(img)
        img.save(TMP / f"f_{f:05d}.png")
    return encode("rauschen", seconds)


ALLE = {"muenzwurf": muenzwurf, "abweichung": abweichung,
        "kaskade": kaskade, "rauschen": rauschen}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    namen = sys.argv[1:] or list(ALLE)
    for n in namen:
        if n not in ALLE:
            raise SystemExit(f"Unbekannt: {n}. Verfuegbar: {', '.join(ALLE)}")
        ALLE[n]()


if __name__ == "__main__":
    main()
