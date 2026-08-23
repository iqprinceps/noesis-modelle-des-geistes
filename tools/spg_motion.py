#!/usr/bin/env python3
"""EP01A Die Spiegel — prozedurale Bewegtbilder.

Abgeleitet von `tools/gw_motion.py` (EP02 Gateway V7); die Vorlage bleibt
unveraendert. Gleiche Bauweise — Frames mit numpy/PIL, dann ffmpeg, kein
Browser, deterministisch — aber in der Kozyrev-Palette aus
`06_PRODUCTION/EP01_KOZYREV_V2/VISUAL_SPEC.md`.

Vier Clips, genau die vier aus der Vorgabe:

  polarlicht   Aurora-Baender, die ueber den Bildschirm wandern und atmen
  magnetfeld   Feldlinien der Erde, die im Zentrum ausduennen und aufreissen
  spirale      Die Aluminiumspirale von oben, rotierend, mit Brennpunkt
  zeitfluss    Ein Strom aus Partikeln, der die Richtung verliert
"""

from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL" / "motion"
TMP = OUT / "_frames"

W, H, FPS = 1920, 1080, 30

NAVY = (10, 20, 40)          # 0A1428  arktisches Nachtblau
NAVY_L = (20, 36, 63)        # 14243F
AURORA = (63, 217, 160)      # 3FD9A0  Polarlicht
AURORA_D = (30, 122, 92)     # 1E7A5C
ALU = (216, 203, 168)        # D8CBA8  Aluminium
ALU_L = (240, 232, 210)      # F0E8D2
KUPFER = (224, 135, 63)      # E0873F  Kupfer
VIOLETT = (123, 94, 167)     # 7B5EA7
DIM = (143, 160, 168)        # 8FA0A8


def run(args):
    p = subprocess.run(args, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-4000:])


def backdrop() -> Image.Image:
    """Nachtblau mit Verlauf nach oben und weicher Vignette."""
    img = Image.new("RGB", (W, H), NAVY)
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=int(255 * (1 - y / H) ** 1.4))
    img = Image.composite(Image.new("RGB", (W, H), NAVY_L), img, grad)
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * .30, -H * .45, W * 1.30, H * 1.45], fill=255)
    return Image.composite(img, Image.new("RGB", (W, H), (5, 11, 23)),
                           v.filter(ImageFilter.GaussianBlur(200)))


def grain(img: Image.Image, amount=4) -> Image.Image:
    a = np.asarray(img).astype(np.int16)
    rng = np.random.default_rng(7)
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


# ------------------------------------------------------------- polarlicht

def polarlicht(seconds=10.0):
    """Aurora-Vorhaenge, die wandern und atmen.

    Gebaut als weiche vertikale Baender: eine Grundkurve laeuft ueber die
    Breite, darauf sitzen Strahlen, die nach oben ausduennen. Danach ein
    Gaussblur — so entsteht die Faltung, die ein Nordlicht hat, ohne dass
    ein Partikel-Overlay noetig waere.
    """
    frames_start()
    n = int(seconds * FPS)
    base = backdrop()
    rng = np.random.default_rng(19)
    sterne = [(rng.integers(0, W), rng.integers(0, int(H * .62)),
               rng.integers(90, 210)) for _ in range(220)]
    for k in range(n):
        t = k / FPS
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        for x, y, a in sterne:
            d.point((int(x), int(y)), fill=(230, 235, 240, int(a)))
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        for b, (phase, hoehe, dicht, farbe) in enumerate((
                (0.0, 470, 26, AURORA), (1.9, 620, 34, AURORA_D),
                (3.4, 390, 22, VIOLETT))):
            drift = t * (14 + b * 6)
            for x in range(-40, W + 40, dicht):
                u = (x + drift) / W
                y0 = (hoehe + 96 * math.sin(2 * math.pi * (1.4 * u + t * .07 + phase))
                      + 44 * math.sin(2 * math.pi * (3.1 * u - t * .05)))
                puls = 0.42 + 0.58 * (0.5 + 0.5 * math.sin(2 * math.pi * (t / 6.5) + u * 5 + phase))
                lang = (250 + 210 * math.sin(2 * math.pi * (2.2 * u + t * .04 + phase))) * puls
                schritte = 15
                for i in range(schritte):
                    f = i / schritte
                    yy = y0 - lang * f
                    a = int(150 * puls * (1 - f) ** 1.5)
                    if a < 4:
                        continue
                    col = mix(farbe, ALU_L, 0.34 * (1 - f))
                    bd.line([(x, yy), (x, yy - lang / schritte - 1)],
                            fill=col + (a,), width=dicht + 8)
                a0 = int(190 * puls)
                bd.line([(x, y0), (x, y0 + 26)],
                        fill=mix(farbe, ALU_L, .5) + (a0,), width=dicht + 6)
        band = band.filter(ImageFilter.GaussianBlur(17))
        img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
        # Spiegelung des Lichts auf der Schneeflaeche unten
        d = ImageDraw.Draw(img, "RGBA")
        for y in range(int(H * .80), H, 3):
            f = (y - H * .80) / (H * .20)
            d.line([(0, y), (W, y)], fill=AURORA_D + (int(30 * (1 - f)),))
        grain(img).save(TMP / f"f_{k:05d}.png")
    return encode("polarlicht", seconds)


# ------------------------------------------------------------- magnetfeld

def magnetfeld(seconds=9.0):
    """Erdfeldlinien, die im Zentrum ausduennen und aufreissen.

    Das ist die Bildlogik hinter dem Satz, mit dem die Gruppe den Aufbau
    begruendet: der Aufenthalt in einem geschwaechten Feld. Die Linien
    verlieren ueber den Clip Dichte und Helligkeit, bis in der Mitte ein
    Loch steht.
    """
    frames_start()
    n = int(seconds * FPS)
    base = backdrop()
    cx, cy = W // 2, H // 2
    for k in range(n):
        t = k / FPS
        # 0 = geschlossenes Feld, 1 = aufgerissen; einmal hin und zurueck
        auf = 0.5 - 0.5 * math.cos(2 * math.pi * t / seconds)
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        # Erdkoerper
        r = 128
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(16, 30, 54),
                  outline=mix(ALU, NAVY, .35) + (200,), width=3)
        d.ellipse([cx - r, cy - r, cx + r, cy + r * .18],
                  outline=(60, 90, 110, 120), width=2)
        for i in range(13):
            s = 1.30 + i * 0.44
            a_base = 235 - i * 8
            pts_o, pts_u = [], []
            for grad in range(-88, 89, 2):
                w = math.radians(grad)
                rr = r * s * math.cos(w) ** 2
                if rr < r:
                    continue
                pts_o.append((cx + rr * math.cos(w), cy - rr * math.sin(w) * .84))
                pts_u.append((cx - rr * math.cos(w), cy - rr * math.sin(w) * .84))
            # Ausduennen: je naeher am Zentrum, desto frueher reisst es
            naehe = max(0.0, 1.0 - i / 5.5)
            a = int(max(0, a_base * (1 - auf * naehe)))
            if a < 6:
                continue
            col = mix(AURORA, VIOLETT, min(1.0, i / 16))
            for pts in (pts_o, pts_u):
                if len(pts) > 2:
                    d.line(pts, fill=col + (a,), width=4 if i < 5 else 3, joint="curve")
        # Der Riss im Zentrum
        if auf > 0.15:
            rr = 60 + 430 * auf
            d.ellipse([cx - rr, cy - rr * .84, cx + rr, cy + rr * .84],
                      outline=KUPFER + (int(200 * auf),), width=4)
            for i in range(26):
                ang = 2 * math.pi * i / 26 + t * .12
                x1 = cx + rr * .82 * math.cos(ang)
                y1 = cy + rr * .82 * .84 * math.sin(ang)
                x2 = cx + rr * 1.10 * math.cos(ang)
                y2 = cy + rr * 1.10 * .84 * math.sin(ang)
                d.line([(x1, y1), (x2, y2)], fill=KUPFER + (int(165 * auf),), width=3)
        grain(img).save(TMP / f"f_{k:05d}.png")
    return encode("magnetfeld", seconds)


# ---------------------------------------------------------------- spirale

def spirale(seconds=10.0):
    """Die Aluminiumspirale von oben, rotierend, mit Brennpunkt.

    Sechs gebogene Platten, offen, mit Einstiegsspalt — dieselbe Geometrie
    wie in den Bildern. In der Mitte der Stuhl, davor der Brennpunkt, den
    die Kruemmung erzeugt.
    """
    frames_start()
    n = int(seconds * FPS)
    base = backdrop()
    cx, cy = W // 2, H // 2 + 10
    R = 430
    for k in range(n):
        t = k / FPS
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        rot = math.degrees(t * 0.20)
        # Bodenring
        for f in (1.62, 1.30):
            d.ellipse([cx - R * f, cy - R * f * .74, cx + R * f, cy + R * f * .74],
                      outline=(30, 52, 80, 120), width=2)
        # Sechs gebogene Platten als Kreisboegen; der Spalt bleibt offen
        for i in range(6):
            a0 = rot + i * 60 + 7          # 7 Grad Luft = sichtbarer Spalt
            a1 = a0 + 46
            for lage, (rr, breite, col, alpha) in enumerate((
                    (R, 20, ALU, 240), (R - 21, 12, ALU_L, 210),
                    (R - 39, 7, AURORA, 165))):
                box = [cx - rr, cy - rr * .74, cx + rr, cy + rr * .74]
                d.arc(box, a0, a1, fill=col + (alpha,), width=breite)
            # Innenreflex
            box = [cx - (R - 58), cy - (R - 58) * .74, cx + (R - 58), cy + (R - 58) * .74]
            d.arc(box, a0 + 6, a1 - 6, fill=AURORA_D + (125,), width=24)
        # Einstiegsspalt betonen: der Sektor ohne Platte
        luecke = rot + 6 * 60 + 7
        d.arc([cx - R, cy - R * .74, cx + R, cy + R * .74],
              luecke - 14, luecke - 1, fill=KUPFER + (170,), width=4)
        # Brennpunkt: 50 cm vor der Flaeche, hier als atmender Kupferpunkt
        puls = 0.5 + 0.5 * math.sin(2 * math.pi * t / 2.6)
        for rr, a in ((200, 48), (138, 70), (82, 100)):
            r2 = rr * (0.94 + 0.10 * puls)
            d.ellipse([cx - r2, cy - r2 * .74, cx + r2, cy + r2 * .74],
                      outline=KUPFER + (int(a * (0.5 + 0.5 * puls)),), width=2)
        rr = 20 + 9 * puls
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=KUPFER + (240,))
        # Der Stuhl im Zentrum, schematisch von oben
        d.rectangle([cx - 34, cy - 31, cx + 34, cy + 31],
                    outline=ALU + (165,), width=4)
        grain(img).save(TMP / f"f_{k:05d}.png")
    return encode("spirale", seconds)


# -------------------------------------------------------------- zeitfluss

def zeitfluss(seconds=11.0):
    """Ein Strom aus Partikeln, der die Richtung verliert und rueckwaerts laeuft.

    Bild fuer die Stelle, an der das Gefuehl fuer Dauer sich aufloest: der
    Strom laeuft, wird unentschieden, kehrt um. Die Farbe wechselt dabei von
    Polarlicht nach Violett — Violett ist im Farbkonzept die Vergangenheit.
    """
    frames_start()
    n = int(seconds * FPS)
    base = backdrop()
    rng = np.random.default_rng(41)
    m = 1500
    px = rng.uniform(0, W, m)
    py = rng.normal(H / 2, 175, m)
    sp = rng.uniform(0.6, 1.55, m)
    gr = rng.uniform(0.4, 1.0, m)
    for k in range(n):
        t = k / FPS
        # +1 vorwaerts, 0 stillstehend, -1 rueckwaerts
        richtung = math.cos(2 * math.pi * t / seconds)
        img = base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        # Stromlinien im Hintergrund
        for i in range(9):
            y0 = 150 + i * 96
            pts = [(x, y0 + 26 * math.sin(2 * math.pi * (x / W * 1.6 + t * .06 * richtung)))
                   for x in range(0, W + 1, 12)]
            d.line(pts, fill=(34, 68, 100, 130), width=2, joint="curve")
        vor = mix(AURORA, ALU_L, .18)
        zurueck = VIOLETT
        for i in range(m):
            v = 4.6 * sp[i] * richtung
            px[i] = (px[i] + v) % W
            py[i] += 0.30 * math.sin(t * 0.9 + i * 0.21)
            x, y = px[i], py[i]
            if abs(richtung) < 0.16:
                col, a = KUPFER, 200          # der Moment ohne Richtung
            elif richtung > 0:
                col, a = vor, int(120 + 135 * gr[i])
            else:
                col, a = zurueck, int(120 + 135 * gr[i])
            lang = 5 + 30 * abs(richtung) * sp[i]
            d.line([(x, y), (x - lang * (1 if richtung >= 0 else -1), y)],
                   fill=col + (a,), width=3)
        # Kupferne Marke in der Mitte: der Punkt, an dem es kippt
        if abs(richtung) < 0.30:
            a = int(180 * (1 - abs(richtung) / 0.30))
            d.line([(W // 2, 120), (W // 2, H - 120)], fill=KUPFER + (a,), width=2)
        grain(img).save(TMP / f"f_{k:05d}.png")
    return encode("zeitfluss", seconds)


def main():
    print("Baue Bewegtbilder (Kozyrev-Palette):")
    polarlicht()
    magnetfeld()
    spirale()
    zeitfluss()
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
