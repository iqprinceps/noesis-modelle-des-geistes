#!/usr/bin/env python3
"""EP03 PEAR — Grafikbaukasten.

Abgeleitet von `tools/gw_graphics.py` (EP02 Gateway V6/V7); die Vorlage bleibt
unveraendert. Gleiche Bauweise mit Pillow — jeder Buchstabe steht exakt so im
Bild, wie er hier im Code steht — aber in der Kozyrev-Palette aus
`06_PRODUCTION/EP01_KOZYREV_V2/VISUAL_SPEC.md`.

Zwei Vorgaben aus der Spec sind hier hart eingebaut:
  * hoechstens vier Eintraege je Karte
  * keine Fussnote, die die Karte wieder einkassiert
"""

from __future__ import annotations

from pathlib import Path

import math

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"
OUT = PROD / "visuals" / "cards"
GEN = PROD / "visuals" / "generated"
THUMB = PROD / "thumbnail"

W, H = 1920, 1080

# Palette EP03: Institutsgrau statt Nachtblau, Bernstein der Schreibtisch-
# lampe statt Kupfer, das Rot der Leuchtziffern als Akzent.
NAVY = (14, 16, 19)          # 0E1013  Institutsgrau
NAVY_L = (26, 29, 34)        # 1A1D22
AURORA = (232, 176, 84)      # E8B054  Bernstein — traegt die Auszeichnung
AURORA_D = (128, 92, 40)     # 805C28
ALU = (206, 200, 186)        # CEC8BA
ALU_L = (238, 234, 224)      # EEEAE0
KUPFER = (226, 78, 58)       # E24E3A  Rot der Leuchtziffern
VIOLETT = (126, 224, 150)    # 7EE096  Phosphorgruen
DIM = (120, 126, 134)        # 787E86
LINIE = (44, 48, 55)

F = "C:/Windows/Fonts/"


def font(size: int, bold: bool = False, narrow: bool = False) -> ImageFont.FreeTypeFont:
    if narrow:
        name = "ARIALNB.TTF" if bold else "ARIALN.TTF"
    else:
        name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(F + name, size)


def canvas(vignette: bool = True) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=int(150 * (1 - y / H) ** 1.3))
    img = Image.composite(Image.new("RGB", (W, H), NAVY_L), img, grad)
    if vignette:
        v = Image.new("L", (W, H), 0)
        ImageDraw.Draw(v).ellipse([-W * .28, -H * .42, W * 1.28, H * 1.42], fill=255)
        v = v.filter(ImageFilter.GaussianBlur(190))
        img = Image.composite(img, Image.new("RGB", (W, H), (5, 11, 23)), v)
    return img


def grain(img: Image.Image, amount: int = 5) -> Image.Image:
    import numpy as np
    a = np.asarray(img).astype(np.int16)
    rng = np.random.default_rng(11)
    n = rng.integers(-amount, amount + 1, a.shape[:2])[:, :, None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype("uint8"))


def text(d, xy, s, f, fill, anchor="la", spacing=0):
    if not spacing:
        d.text(xy, s, font=f, fill=fill, anchor=anchor)
        return
    total = sum(d.textlength(c, font=f) + spacing for c in s) - spacing
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for c in s:
        d.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += d.textlength(c, font=f) + spacing


def eyebrow(d, x, y, s, col=AURORA):
    text(d, (x, y), s.upper(), font(22, True, True), col, spacing=4)


def rule(d, x1, y, x2, col=LINIE, wdt=2):
    d.line([(x1, y), (x2, y)], fill=col, width=wdt)


def footer(d, s):
    text(d, (82, H - 52), s.upper(), font(19, False, True), (96, 116, 140), spacing=3)


def tri(d, x, y, size, col, left=False):
    s = size
    pts = [(x + s, y - s), (x + s, y + s), (x - s, y)] if left else \
          [(x - s, y - s), (x - s, y + s), (x + s, y)]
    d.polygon(pts, fill=col)


def save(img: Image.Image, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    grain(img).save(path, quality=97)
    print(f"  {name}  {img.size}")
    return path


# ------------------------------------------------------------------ Karten

def signet(d, cx=1520, cy=612, R=270):
    """Die Anlage von oben als ruhiges Signet auf der freien rechten Haelfte.

    Sechs gebogene Elemente, ein offener Einstiegsspalt, der Brennpunkt in
    der Mitte — dieselbe Geometrie wie in den Bildern, nur reduziert.
    """
    for f in (1.34, 1.08):
        d.ellipse([cx - R * f, cy - R * f * .74, cx + R * f, cy + R * f * .74],
                  outline=(30, 52, 84, 190), width=2)
    box = [cx - R, cy - R * .74, cx + R, cy + R * .74]
    for i in range(6):
        a0 = i * 60 + 8
        d.arc(box, a0, a0 + 44, fill=AURORA_D + (215,), width=11)
        d.arc([cx - (R - 20), cy - (R - 20) * .74, cx + (R - 20), cy + (R - 20) * .74],
              a0 + 4, a0 + 40, fill=(30, 60, 96, 170), width=6)
    d.arc(box, -8, 6, fill=KUPFER + (200,), width=5)          # der Einstiegsspalt
    for rr, a in ((132, 70), (86, 100)):
        d.ellipse([cx - rr, cy - rr * .74, cx + rr, cy + rr * .74],
                  outline=KUPFER + (a,), width=2)
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=KUPFER + (225,))



# --------------------------------------------------- Grafiken je Listenkarte

def gr_masse(d, cx=1520, cy=600):
    """Zweihundert Wuerfe als Raster, etwa die Haelfte hell. Ein Versuch."""
    import random
    r = random.Random(4)
    spalten, zeilen, schritt = 20, 10, 30
    x0 = cx - spalten * schritt // 2
    y0 = cy - zeilen * schritt // 2
    for i in range(spalten * zeilen):
        x = x0 + (i % spalten) * schritt
        y = y0 + (i // spalten) * schritt
        if r.random() < 0.5:
            d.ellipse([x, y, x + 17, y + 17], fill=AURORA + (230,))
        else:
            d.ellipse([x, y, x + 17, y + 17], outline=DIM + (150,), width=2)
    text(d, (cx, y0 + zeilen * schritt + 26), "200 Bits · ein Versuch",
         font(26, True), DIM, anchor="ma")


def gr_muster(d, cx=1520, cy=600):
    """Drei Baender fuer Farbe, Szenen, Zeitgefuehl."""
    farben = [(AURORA, "Farbe"), ((190, 96, 176), "Szenen"), (KUPFER, "Zeit")]
    y = cy - 230
    for col, _ in farben:
        for i in range(46):
            fx = cx - 300 + i * 13
            a = int(210 * (0.35 + 0.65 * abs(math.sin(i / 5.5))))
            d.line([(fx, y - 42), (fx, y + 42)], fill=col + (a,), width=8)
        y += 165


def gr_patent(d, cx=1520, cy=600):
    """Die Registernummer als Stempelblock."""
    d.rounded_rectangle((cx - 300, cy - 150, cx + 300, cy + 150), 10,
                        outline=KUPFER + (220,), width=5)
    d.rounded_rectangle((cx - 282, cy - 132, cx + 282, cy + 132), 6,
                        outline=LINIE + (200,), width=2)
    text(d, (cx, cy - 96), "US", font(34, True), AURORA, anchor="ma", spacing=8)
    text(d, (cx, cy - 44), "5 830 064", font(76, True), ALU_L, anchor="ma")
    text(d, (cx, cy + 56), "1998", font(38, True), KUPFER, anchor="ma", spacing=6)


def gr_aurora(d, cx=1520, cy=600):
    """Die Glockenkurve in neunzehn Faechern."""
    import math
    faecher, breite = 19, 21
    x0 = cx - faecher * breite // 2
    boden = cy + 190
    for i in range(faecher):
        m = (i - (faecher - 1) / 2) / 4.2
        h = int(300 * math.exp(-m * m / 2))
        x = x0 + i * breite
        d.rectangle([x + 2, boden - h, x + breite - 4, boden],
                    fill=AURORA + (220,) if h > 40 else AURORA_D + (200,))
    d.line([(x0 - 6, boden + 3), (x0 + faecher * breite, boden + 3)],
           fill=DIM + (170,), width=2)
    text(d, (cx, boden + 22), "19 Fächer", font(26, True), DIM, anchor="ma")


def gr_dikson(d, cx=1520, cy=600):
    """Drei Labore, ein Versuchsplan."""
    kasten = [("PRINCETON", AURORA), ("FREIBURG", ALU), ("GIESSEN", ALU)]
    bh, luft = 96, 30
    y0 = cy - (len(kasten) * bh + (len(kasten) - 1) * luft) // 2
    for i, (name, farbe) in enumerate(kasten):
        y = y0 + i * (bh + luft)
        d.rounded_rectangle((cx - 230, y, cx + 230, y + bh), 8,
                            outline=farbe + (200,), width=3)
        text(d, (cx, y + bh // 2 - 18), name, font(34, True), farbe, anchor="ma",
             spacing=4)
        if i < len(kasten) - 1:
            d.line([(cx, y + bh), (cx, y + bh + luft)], fill=DIM + (140,), width=2)
    text(d, (cx, y0 + len(kasten) * (bh + luft) + 4), "ein Versuchsplan",
         font(26, True), DIM, anchor="ma")


def gr_offtime(d, cx=1520, cy=600):
    """Zeitachse: weit vorher, der Lauf, weit nachher."""
    x0, x1 = cx - 300, cx + 300
    d.line([(x0, cy), (x1, cy)], fill=DIM + (170,), width=2)
    # Der Lauf der Maschine sitzt links der Mitte, weil nachher viel mehr Zeit liegt
    lauf = x0 + int((x1 - x0) * 73 / (73 + 336))
    for x, lab, farbe in ((x0, "-73 h", KUPFER), (lauf, "LAUF", AURORA),
                          (x1, "+336 h", KUPFER)):
        d.line([(x, cy - 18), (x, cy + 18)], fill=farbe + (220,), width=3)
        text(d, (x, cy + 34), lab, font(24, True), farbe, anchor="ma")
    d.rectangle([lauf - 5, cy - 9, lauf + 5, cy + 9], fill=AURORA + (235,))
    text(d, (cx, cy - 96), "Absicht ausserhalb der Messzeit",
         font(26, True), DIM, anchor="ma")


def gr_schlussstand(d, cx=1520, cy=600):
    """Vier Felder, drei belegt, eines offen."""
    for i in range(4):
        y = cy - 246 + i * 164
        voll = i < 3
        col = AURORA if voll else KUPFER
        d.rounded_rectangle((cx - 150, y - 56, cx + 150, y + 56), 8,
                            outline=col + (225,), width=4 if voll else 3)
        if voll:
            d.line([(cx - 46, y + 6), (cx - 14, y + 34)], fill=col + (235,), width=9)
            d.line([(cx - 14, y + 34), (cx + 52, y - 32)], fill=col + (235,), width=9)
        else:
            text(d, (cx, y - 40), "?", font(74, True), col, anchor="ma")


def list_card(name, eyebrow_txt, title, rows, quelle, grafik=None) -> Path:
    """Hoechstens vier Eintraege. Die Fusszeile nennt die Quelle, sie
    kommentiert die Karte nicht (VISUAL_SPEC: keine entwertende Fussnote).

    `grafik` zeichnet die rechte Haelfte. Ohne eigene Grafik trugen alle
    Listenkarten dasselbe Ringsignet — sechs fast gleiche Karten, die sich
    im Schnitt als Vorlage lesen.
    """
    if len(rows) > 4:
        raise ValueError(f"{name}: {len(rows)} Eintraege, erlaubt sind vier")
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    (grafik or signet)(d)
    eyebrow(d, 82, 78, eyebrow_txt)
    text(d, (82, 116), title, font(60, True), ALU_L)
    rule(d, 82, 202, 1838)
    hoehe = {1: 0, 2: 150, 3: 130, 4: 0}
    y = 268 if len(rows) >= 3 else 360
    schritt = {1: 0, 2: 190, 3: 176, 4: 176}[len(rows)]
    for label, desc in rows:
        d.rectangle((82, y + 6, 90, y + 56), fill=KUPFER)
        text(d, (118, y), label, font(40, True), AURORA)
        text(d, (118, y + 58), desc, font(32), (206, 214, 216))
        y += schritt
    _ = hoehe
    footer(d, quelle)
    return save(img, name)


def karte_patent() -> Path:
    return list_card(
        "PE_CARD_PATENT.png", "Die Maschine auf Papier", "DIE PATENTSCHRIFT",
        [("US 5.830.064", "Registernummer der Vereinigten Staaten"),
         ("EINGEREICHT 1996", "Anmeldung beim Patentamt"),
         ("ERTEILT 1998", "Erteilung der Schutzschrift"),
         ("JAHN · DUNNE · NELSON", "Erfinder, Anmelder Pear Inc.")],
        "US-Patentschrift 5.830.064", grafik=gr_patent)


def karte_masse() -> Path:
    return list_card(
        "PE_CARD_MASSE.png", "Ein einzelner Versuch", "ZWEIHUNDERT WÜRFE",
        [("1.000 JE SEKUNDE", "Takt, mit dem die Kiste Nullen und Einsen erzeugt"),
         ("200 BITS", "Umfang eines Versuchs"),
         ("0,2 SEKUNDEN", "So lange dauert er"),
         ("1.000 VERSUCHE", "ergeben eine Serie, gut drei Minuten am Stück")],
        "US-Patentschrift 5.830.064", grafik=gr_masse)


def karte_muster() -> Path:
    return list_card(
        "PE_CARD_MUSTER.png", "Der Ablauf im Labor", "DREI BEDINGUNGEN",
        [("MEHR", "Der Teilnehmer will mehr Einsen als Nullen"),
         ("WENIGER", "Er will weniger"),
         ("NICHTS", "Er lässt laufen — das ist die Kontrolle")],
        "Angaben des Labors", grafik=gr_muster)


def karte_aurora() -> Path:
    return list_card(
        "PE_CARD_KASKADE.png", "Die Wand aus Kugeln", "DIE KASKADE",
        [("9.000 KUGELN", "aus Polystyrol, keine zwei Zentimeter groß"),
         ("330 STIFTE", "durch die sie fallen"),
         ("19 FÄCHER", "in denen sie sich sammeln"),
         ("12 MINUTEN", "dauert ein Durchgang")],
        "Angaben des Labors", grafik=gr_aurora)


def karte_dikson() -> Path:
    return list_card(
        "PE_CARD_PROBE.png", "Die Wiederholung mit festem Plan", "DREI LABORE",
        [("PRINCETON", "das Labor selbst"),
         ("FREIBURG", "Institut für Grenzgebiete der Psychologie"),
         ("GIESSEN", "Justus-Liebig-Universität"),
         ("VORHER FESTGELEGT", "Umfang, Bedingungen und Auswertung")],
        "Gemeinsame Veröffentlichung der drei Labore", grafik=gr_dikson)


def karte_schlussstand() -> Path:
    return list_card(
        "PE_CARD_SCHLUSSSTAND.png", "Der Stand heute", "WAS ES GIBT",
        [("DIE MASCHINEN", "gebaut, betrieben, in einer Patentschrift beschrieben"),
         ("DIE DATEN", "Millionen Durchgänge über achtundzwanzig Jahre"),
         ("DIE WIEDERHOLUNG", "unter verschärften Bedingungen, ohne den Effekt"),
         ("VERÖFFENTLICHT", "beides, von denselben Leuten")],
        "NOESIS · Modelle des Geistes", grafik=gr_schlussstand)


def karte_frage() -> Path:
    """Die Zahl, um die es geht. Ein Bild, keine Erklaerung."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, "Der gemessene Effekt")
    rule(d, 82, 132, 1838)
    text(d, (960, 350), "Zehntausend Münzwürfe.", font(56), ALU_L, anchor="ma")
    text(d, (960, 440), "Erwartet: fünftausend Mal Kopf.", font(56), ALU_L, anchor="ma")
    text(d, (960, 620), "Gemessen:", font(60), DIM, anchor="ma")
    text(d, (960, 706), "fünftausendundeins.", font(84, True), AURORA, anchor="ma")
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "PE_CARD_FRAGE.png")


def karte_zeitmaschine() -> Path:
    """Was die Wiederholung erbrachte, in den Worten der Beteiligten selbst.
    Der staerkste Beat der Folge — deshalb bekommt er eine eigene Karte."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, "Dieselben Leute, zwei Ergebnisse")
    rule(d, 82, 132, 1838)
    d.rounded_rectangle((110, 250, 930, 830), 10, fill=(24, 22, 18),
                        outline=(70, 62, 44), width=2)
    text(d, (520, 320), "ZWEI JAHRZEHNTE", font(26, True, True), DIM, anchor="ma", spacing=5)
    text(d, (520, 440), "EIN EFFEKT", font(64, True), AURORA, anchor="ma")
    text(d, (520, 570), "Ein zusätzlicher Treffer", font(30), (206, 202, 190), anchor="ma")
    text(d, (520, 614), "auf zehntausend.", font(30), (206, 202, 190), anchor="ma")
    d.rounded_rectangle((990, 250, 1810, 830), 10, fill=(30, 16, 14),
                        outline=(96, 44, 36), width=3)
    text(d, (1400, 320), "DIE WIEDERHOLUNG", font(26, True, True), KUPFER, anchor="ma",
         spacing=5)
    text(d, (1400, 440), "NICHTS DAVON", font(64, True), KUPFER, anchor="ma")
    text(d, (1400, 570), "Um eine Zehnerpotenz verfehlt,", font(30), (206, 202, 190),
         anchor="ma")
    text(d, (1400, 614), "schreiben sie selbst.", font(30), (206, 202, 190), anchor="ma")
    footer(d, "Gemeinsame Veröffentlichung der drei Labore")
    return save(img, "PE_CARD_ZWEI_ERGEBNISSE.png")


def karte_comment() -> Path:
    """Mid-Roll-CTA, binaer gestellt — das kostet den Zuschauer eine Sekunde."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (960, 268), "Messfehler —", font(64, True), ALU_L, anchor="ma")
    text(d, (960, 350), "oder ist da etwas?", font(64, True), ALU_L, anchor="ma")
    d.rounded_rectangle((470, 500, 900, 660), 10, fill=(12, 40, 34),
                        outline=AURORA, width=3)
    text(d, (685, 546), "JA", font(72, True), AURORA, anchor="ma")
    d.rounded_rectangle((1020, 500, 1450, 660), 10, fill=(44, 22, 14),
                        outline=KUPFER, width=3)
    text(d, (1235, 546), "NEIN", font(72, True), KUPFER, anchor="ma")
    text(d, (960, 742), "Schreib es in die Kommentare.", font(38), DIM, anchor="ma")
    text(d, (960, 828), "Gleich kommt die Stelle, an der das", font(34), KUPFER, anchor="ma")
    text(d, (960, 874), "Labor sich selbst überprüfen ließ.", font(34), KUPFER, anchor="ma")
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "PE_CARD_COMMENT.png")


def endcard() -> Path:
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (960, 168), "NOESIS", font(46, True), AURORA, anchor="ma", spacing=14)
    rule(d, 660, 246, 1260)

    text(d, (960, 316), "Würdest du dich", font(60, True), ALU_L, anchor="ma")
    text(d, (960, 392), "vor die Kiste setzen?", font(60, True), KUPFER, anchor="ma")
    text(d, (960, 506), "Ja oder nein — schreib es in die Kommentare.",
         font(36), DIM, anchor="ma")

    # Endscreen-Flaeche rechts unten bleibt frei
    d.rounded_rectangle((150, 640, 800, 1000), 10, fill=(14, 28, 50),
                        outline=(48, 72, 110), width=2)
    text(d, (190, 690), "NÄCHSTE FOLGE", font(24, True, True), AURORA, spacing=4)
    text(d, (190, 742), "Das globale Netz", font(48, True), ALU_L)
    text(d, (190, 812), "Zufallsgeneratoren rund um die Welt,", font(30), DIM)
    text(d, (190, 854), "die seit 1998 ununterbrochen messen.", font(30), DIM)
    tri(d, 202, 942, 13, KUPFER)
    text(d, (228, 926), "Jetzt ansehen", font(32, True), KUPFER)

    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "PE_ENDCARD.png")


# --------------------------------------------------------------- Thumbnail

def thumbnail(motiv: str = "pe_thumb_held") -> Path:
    """Ein Motiv, ein Schlagwort, hoher Kontrast.

    Aus EP01A uebernommen: kein Gesicht dort, wo der Raum die Hauptsache ist;
    die zweite Zeile nicht in derselben Farbe wie das, worauf sie liegt; und
    die Unterzeile nimmt die Ueberschrift nicht zurueck.

    Der Suchbegriff ist hier nicht das Schlagwort, sondern der Ort. "PRINCETON"
    traegt die Neugier: eine Elite-Universitaet und ein Satz, der dort nicht
    hingehoert.
    """
    import numpy as np

    base = GEN / f"{motiv}.png"
    if not base.is_file():
        raise SystemExit(f"Motiv fehlt: {base}")
    img = Image.open(base).convert("RGB").resize((W, H), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.24)
    img = ImageEnhance.Color(img).enhance(1.22)

    # Das Rot der Leuchtziffern anheben, damit es bei 246 px noch Farbe ist
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([1090, 380, 1590, 760], fill=(58, 12, 8))
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    img = Image.fromarray(np.clip(np.asarray(img).astype("int16")
                                  + np.asarray(glow).astype("int16"),
                                  0, 255).astype("uint8"))

    scrim = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scrim)
    for x in range(W):
        sd.line([(x, 0), (x, H)], fill=int(250 * max(0.0, 1 - x / 1010) ** 1.25))
    img = Image.composite(Image.new("RGB", (W, H), (10, 11, 13)), img, scrim)

    fuss = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fuss)
    for y in range(H):
        fd.line([(0, y), (W, y)], fill=int(120 * max(0.0, (y - 770) / 310) ** 1.3))
    img = Image.composite(Image.new("RGB", (W, H), (10, 11, 13)), img, fuss)

    d = ImageDraw.Draw(img, "RGBA")

    d.rectangle((96, 150, 108, 202), fill=KUPFER)
    text(d, (136, 152), "PRINCETON · 28 JAHRE", font(38, True, True),
         AURORA, spacing=6)

    f1 = font(166, True)
    schatten = (3, 4, 6)
    for dx, dy in ((6, 7), (0, 0)):
        text(d, (92 + dx, 246 + dy), "GEDANKEN", f1, schatten if dx else ALU_L)
        x = 92 + dx
        text(d, (x, 408 + dy), "STEUERN", f1, schatten if dx else KUPFER)
        x += d.textlength("STEUERN", font=f1)
        text(d, (x, 408 + dy), "?", f1, schatten if dx else AURORA)

    f2 = font(70, True)
    for dx, dy in ((4, 5), (0, 0)):
        text(d, (96 + dx, 614 + dy), "Der Dekan glaubte daran.", f2,
             schatten if dx else ALU_L)

    d.rounded_rectangle((92, 762, 1014, 922), 8, fill=(12, 14, 18, 236),
                        outline=AURORA_D, width=3)
    text(d, (126, 788), "EIN TREFFER AUF 10.000", font(46, True), ALU_L)
    text(d, (126, 854), "GEMESSEN ÜBER 28 JAHRE · PRINCETON", font(32), DIM)

    THUMB.mkdir(parents=True, exist_ok=True)
    img = grain(img, 4)
    voll = THUMB / "EP03_PEAR_THUMBNAIL.png"
    img.save(voll, quality=97)
    img.resize((1280, 720), Image.LANCZOS).save(
        THUMB / "EP03_PEAR_THUMBNAIL_1280x720.jpg", quality=94)
    klein = img.resize((246, 138), Image.LANCZOS)
    klein.save(THUMB / "_probe_246px.png")
    probe = Image.new("RGB", (1280, 1104), (10, 11, 13))
    probe.paste(img.resize((1280, 720), Image.LANCZOS), (0, 0))
    pd = ImageDraw.Draw(probe)
    text(pd, (24, 748), "LESBARKEITSPROBE", font(24, True, True), AURORA, spacing=4)
    text(pd, (24, 788), "links: Originalgröße 246 px — so groß ist das Bild in der "
                        "YouTube-App", font(24), DIM)
    text(pd, (24, 822), "rechts: dieselben Pixel, zweifach vergrößert", font(24), DIM)
    probe.paste(klein, (24, 866))
    probe.paste(klein.resize((492, 276), Image.NEAREST), (330, 866))
    probe.save(THUMB / "_lesbarkeitsprobe.png")
    print(f"  Thumbnail  {img.size}  + 1280x720 + 246px-Probe")
    return voll



# ---------------------------------------------------------- Karten der V2

def zitat_karte(name: str, eyebrow_txt: str, zeilen: list[str],
                quelle: str, uebersetzung: str = "") -> Path:
    """Ein Zitat, gross, mit Sprecher darunter. Kein Kommentar dazu.

    Die Folge zeigt beide Seiten mit ihren eigenen Worten. Eine Karte, die
    das Zitat einordnet, nimmt ihm genau die Wirkung.
    """
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, eyebrow_txt)
    rule(d, 82, 132, 1838)
    y = 330 if not uebersetzung else 286
    d.text((150, y - 46), "“", font=font(150, True), fill=AURORA_D + (220,))
    for z in zeilen:
        text(d, (960, y), z, font(52, True), ALU_L, anchor="ma")
        y += 76
    if uebersetzung:
        y += 26
        text(d, (960, y), uebersetzung, font(34), DIM, anchor="ma")
        y += 56
    text(d, (960, max(y + 40, 800)), quelle, font(30, True, True), AURORA,
         anchor="ma", spacing=4)
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, name)


def karte_mcdonnell() -> Path:
    return list_card(
        "PE_CARD_MCDONNELL.png", "Wer das Labor bezahlt hat", "JAMES S. McDONNELL",
        [("McDONNELL DOUGLAS", "Gründer des Flugzeugkonzerns"),
         ("F-15 · F/A-18", "Kampfflugzeuge aus seinem Haus"),
         ("MERCURY", "die Kapsel des ersten US-Raumfahrtprogramms"),
         ("SOMMER 1977", "trifft er Jahn auf einer Tagung")],
        "Danksagungen der PEAR-Veröffentlichungen")


def karte_operator() -> Path:
    return list_card(
        "PE_CARD_OPERATOR.png", "Eine einzelne Versuchsperson", "OPERATOR ZEHN",
        [("12 JAHRE", "so lange nimmt sie teil"),
         ("62 SERIEN", "eigenständige Versuchsreihen"),
         ("120.000+", "Durchgänge je Richtung"),
         ("15 %", "aller vierzehn Millionen Durchgänge des Labors")],
        "Abbildungslegende PEAR 95004", grafik=gr_muster)


def karte_offtime() -> Path:
    return list_card(
        "PE_CARD_OFFTIME.png", "Absicht ohne Anwesenheit", "OFF-TIME",
        [("73 STUNDEN VORHER", "früheste Absicht vor dem Lauf der Maschine"),
         ("336 STUNDEN NACHHER", "späteste Absicht nach dem Lauf"),
         ("87.000", "Durchgänge je Richtung"),
         ("NIEMAND IM RAUM", "die Maschine läuft allein")],
        "Jahn und Dunne, eigene Darstellung", grafik=gr_offtime)


def karte_baseline() -> Path:
    """Der Baseline Bind. Beide Deutungen nebeneinander, ohne Urteil."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, "Die Kontrolldurchgänge sind zu glatt")
    rule(d, 82, 132, 1838)
    d.rounded_rectangle((110, 250, 930, 830), 10, fill=(30, 16, 14),
                        outline=(96, 44, 36), width=3)
    text(d, (520, 320), "DIE KRITIK", font(26, True, True), KUPFER, anchor="ma", spacing=5)
    text(d, (520, 440), "ZU BRAV", font(64, True), KUPFER, anchor="ma")
    text(d, (520, 570), "Mit den Daten stimmt", font(30), (206, 202, 190), anchor="ma")
    text(d, (520, 614), "etwas nicht.", font(30), (206, 202, 190), anchor="ma")
    d.rounded_rectangle((990, 250, 1810, 830), 10, fill=(24, 22, 18),
                        outline=(70, 62, 44), width=3)
    text(d, (1400, 320), "DAS LABOR", font(26, True, True), AURORA, anchor="ma", spacing=5)
    text(d, (1400, 440), "IMMER AKTIV", font(64, True), AURORA, anchor="ma")
    text(d, (1400, 570), "Der Mensch wirkt auch,", font(30), (206, 202, 190), anchor="ma")
    text(d, (1400, 614), "wenn er nichts will.", font(30), (206, 202, 190), anchor="ma")
    footer(d, "Baseline Bind · beide Deutungen")
    return save(img, "PE_CARD_BASELINE.png")


def karte_modell() -> Path:
    """Der Dreh der Folge. Ein Satz, gross, ohne Zusatz."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, "Ab hier geht es nicht mehr um eine Maschine")
    rule(d, 82, 132, 1838)
    text(d, (960, 340), "Die Frage ist nicht mehr,", font(46), DIM, anchor="ma")
    text(d, (960, 404), "ob ich eine Münze verschieben kann.", font(46), DIM, anchor="ma")
    text(d, (960, 570), "Ist mein Geist", font(76, True), ALU_L, anchor="ma")
    text(d, (960, 666), "überhaupt jemals still?", font(76, True), AURORA, anchor="ma")
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "PE_CARD_MODELL.png")


def karte_zwei_lager() -> Path:
    return zitat_karte(
        "PE_CARD_ZWEI_LAGER.png", "Die Gegenposition, zugespitzt",
        ["Schweine können nicht fliegen.",
         "Daten, die das Gegenteil suggerieren,",
         "sind notwendig fehlerhaft."],
        "SINNGEMÄSS NACH EINEM KRITIKER DER PARAPSYCHOLOGIE")


def karte_zitat_dunne() -> Path:
    return zitat_karte(
        "PE_CARD_ZITAT_DUNNE.png", "Brenda Dunne über das Labor",
        ["How do you get peer review",
         "when you don’t have peers?"],
        "BRENDA J. DUNNE · LABORLEITUNG",
        "Wie soll man eine Begutachtung durch Fachkollegen bekommen, "
        "wenn man keine Fachkollegen hat.")


def karte_zitat_park() -> Path:
    return zitat_karte(
        "PE_CARD_ZITAT_PARK.png", "Ein Physiker von aussen",
        ["It’s been an embarrassment to science,",
         "and I think an embarrassment",
         "for Princeton."],
        "PHYSIKER, UNIVERSITY OF MARYLAND",
        "Es war eine Peinlichkeit für die Wissenschaft — "
        "und für Princeton.")


def karte_zitat_happer() -> Path:
    return zitat_karte(
        "PE_CARD_ZITAT_HAPPER.png", "Ein Physiker aus Princeton selbst",
        ["I don’t believe in anything Bob is doing,",
         "but I support his right to do it."],
        "PHYSIKPROFESSOR, PRINCETON",
        "Ich glaube nichts von dem, was Bob tut — "
        "aber ich verteidige sein Recht darauf.")


def main():
    print("Baue Grafiken EP03 PEAR:")
    karte_patent()
    karte_masse()
    karte_muster()
    karte_aurora()
    karte_dikson()
    karte_schlussstand()
    karte_frage()
    karte_zeitmaschine()
    karte_comment()
    karte_mcdonnell()
    karte_operator()
    karte_offtime()
    karte_baseline()
    karte_modell()
    karte_zwei_lager()
    karte_zitat_dunne()
    karte_zitat_park()
    karte_zitat_happer()
    endcard()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "thumbnail":
        thumbnail(*sys.argv[2:3])
    else:
        main()
