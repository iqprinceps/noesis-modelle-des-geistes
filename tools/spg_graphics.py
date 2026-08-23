#!/usr/bin/env python3
"""EP01A Die Spiegel — Grafikbaukasten.

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
PROD = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL"
OUT = PROD / "visuals" / "cards"
GEN = PROD / "visuals" / "generated"
THUMB = PROD / "thumbnail"

W, H = 1920, 1080

NAVY = (10, 20, 40)          # 0A1428
NAVY_L = (20, 36, 63)        # 14243F
AURORA = (63, 217, 160)      # 3FD9A0
AURORA_D = (30, 122, 92)     # 1E7A5C
ALU = (216, 203, 168)        # D8CBA8
ALU_L = (240, 232, 210)      # F0E8D2
KUPFER = (224, 135, 63)      # E0873F
VIOLETT = (123, 94, 167)     # 7B5EA7
DIM = (143, 160, 168)        # 8FA0A8
LINIE = (34, 56, 88)

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
    """Aufriss eines gebogenen Elements mit Massketten."""
    x0, x1 = cx - 150, cx + 150
    y0, y1 = cy - 250, cy + 250
    d.arc([x0 - 60, y0, x0 + 120, y1], 90, 270, fill=ALU + (230,), width=9)
    d.arc([x1 - 120, y0, x1 + 60, y1], 270, 90, fill=ALU + (230,), width=9)
    for yy in (y0, y1):
        d.line([(x0 + 30, yy), (x1 - 30, yy)], fill=(30, 56, 88, 200), width=2)
    d.line([(x1 + 110, y0), (x1 + 110, y1)], fill=KUPFER + (220,), width=2)
    for yy in (y0, y1):
        d.line([(x1 + 96, yy), (x1 + 124, yy)], fill=KUPFER + (220,), width=2)
    text(d, (x1 + 138, cy - 16), "2,80 m", font(26, True), KUPFER)
    d.line([(x0, y1 + 60), (x1, y1 + 60)], fill=KUPFER + (220,), width=2)
    for xx in (x0, x1):
        d.line([(xx, y1 + 46), (xx, y1 + 74)], fill=KUPFER + (220,), width=2)
    text(d, (cx, y1 + 82), "1,20 m", font(26, True), KUPFER, anchor="ma")
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=AURORA + (235,))
    d.line([(x0 + 40, cy), (cx - 16, cy)], fill=AURORA + (140,), width=2)


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
                        outline=(30, 56, 88, 200), width=2)
    text(d, (cx, cy - 96), "RU", font(34, True), AURORA, anchor="ma", spacing=8)
    text(d, (cx, cy - 44), "2 122 446", font(76, True), ALU_L, anchor="ma")
    text(d, (cx, cy + 56), "C 1", font(38, True), KUPFER, anchor="ma", spacing=6)


def gr_aurora(d, cx=1520, cy=600):
    """Sender im Spiegel, Bogen, Empfaenger mit Blatt."""
    sx, sy = cx - 210, cy - 130
    d.arc([sx - 74, sy - 56, sx + 74, sy + 56], 20, 340, fill=ALU + (225,), width=8)
    d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=KUPFER + (235,))
    ex, ey = cx + 210, cy + 150
    d.rounded_rectangle((ex - 62, ey - 78, ex + 62, ey + 78), 4,
                        fill=(232, 228, 214, 235))
    d.ellipse([ex - 26, ey - 26, ex + 26, ey + 26], outline=(60, 70, 80, 230), width=4)
    pts = []
    for i in range(41):
        t_ = i / 40
        pts.append((sx + (ex - sx) * t_,
                    sy + (ey - sy) * t_ - 150 * math.sin(math.pi * t_)))
    for i in range(0, 40, 2):
        d.line([pts[i], pts[i + 1]], fill=AURORA + (200,), width=3)


def gr_dikson(d, cx=1520, cy=600):
    """Breitengrade, ein Punkt weit im Norden."""
    for i, r in enumerate((300, 236, 172, 108)):
        d.ellipse([cx - r, cy - r * .42, cx + r, cy + r * .42],
                  outline=(30, 56, 88, 210), width=2)
    d.line([(cx - 320, cy), (cx + 320, cy)], fill=(30, 56, 88, 210), width=2)
    py = cy - 150
    d.ellipse([cx - 300, py - 126, cx + 300, py + 126], outline=AURORA_D + (200,), width=3)
    d.ellipse([cx - 14, py - 14, cx + 14, py + 14], fill=KUPFER + (240,))
    d.ellipse([cx - 30, py - 30, cx + 30, py + 30], outline=KUPFER + (150,), width=2)
    text(d, (cx, py - 78), "DIKSON", font(26, True), KUPFER, anchor="ma", spacing=5)


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
        "KZ_CARD_PATENT.png", "Die Anlage auf Papier", "DAS PATENT",
        [("RU 2 122 446 C1", "Registernummer der Russischen Föderation"),
         ("ANGEMELDET 1996", "Anmeldung beim Patentamt"),
         ("ERTEILT 1998", "Erteilung der Schutzschrift"),
         ("ZWEI SEITEN", "Aufbau, Maße und Anordnung der Elemente")],
        "Patentschrift RU 2122446 C1", grafik=gr_patent)


def karte_masse() -> Path:
    return list_card(
        "KZ_CARD_MASSE.png", "Was in der Schrift steht", "DIE KONSTRUKTION",
        [("2,80 METER", "Höhe eines gebogenen Elements"),
         ("1,20 METER", "Breite eines gebogenen Elements"),
         ("VIER BIS ZEHN", "Elemente, zu einem offenen Zylinder oder einer Spirale"),
         ("50 ZENTIMETER", "Abstand des Brennpunkts vor der geschliffenen Fläche")],
        "Patentschrift RU 2122446 C1", grafik=gr_masse)


def karte_muster() -> Path:
    return list_card(
        "KZ_CARD_MUSTER.png", "Was sich in den Protokollen wiederholt",
        "DREI MUSTER",
        [("FARBE", "Leuchtende Flächen und konzentrische Ringe, nach wenigen Minuten"),
         ("SZENEN", "Landschaften, fremde Innenräume, Gesichter"),
         ("ZEITGEFÜHL", "Zwanzig Minuten werden auf Stunden geschätzt")],
        "Protokolle des Instituts, Nowosibirsk", grafik=gr_muster)


def karte_aurora() -> Path:
    return list_card(
        "KZ_CARD_AURORA.png", "Der Ablauf des Versuchs", "AURORA BOREALIS",
        [("FESTE MINUTE", "Alle Beteiligten arbeiten nach derselben Uhrzeit"),
         ("EIN SYMBOL", "Der Sender konzentriert sich auf Kreis, Kreuz oder Dreieck"),
         ("BLATT UND STIFT", "Die Empfänger zeichnen auf, was bei ihnen ankommt"),
         ("KURZWELLE UND ZEITUNG", "So wird der Termin verbreitet")],
        "Angaben der Beteiligten, 1990 und 1991", grafik=gr_aurora)


def karte_dikson() -> Path:
    return list_card(
        "KZ_CARD_DIKSON.png", "Der Ort am Nordpolarmeer", "DIKSON",
        [("3.000 KILOMETER", "nördlich von Nowosibirsk"),
         ("MINUS 40 GRAD", "im Winter"),
         ("MONATE OHNE SONNE", "Polarnacht über der Siedlung"),
         ("EIN PAAR HUNDERT", "Menschen leben dort")],
        "Ortsangaben zur Siedlung Dikson", grafik=gr_dikson)


def karte_schlussstand() -> Path:
    return list_card(
        "KZ_CARD_SCHLUSSSTAND.png", "Der Stand heute", "WAS ES GIBT",
        [("DIE ANLAGEN", "In Nowosibirsk aufgebaut, fotografiert, begehbar"),
         ("DIE PROTOKOLLE", "Tausende Berichte über mehr als dreißig Jahre"),
         ("DIE PATENTSCHRIFT", "Maße und Aufbau öffentlich einsehbar"),
         ("DIE AUSWERTUNGEN", "Stammen bis heute aus dem Kreis der Beteiligten")],
        "NOESIS · Modelle des Geistes", grafik=gr_schlussstand)


def karte_frage() -> Path:
    """Die Frage, die Akt 8 traegt. Ein Satz, gross, ohne Zusatz."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, "Seit fast dreißig Jahren")
    rule(d, 82, 132, 1838)
    text(d, (960, 380), "Die Maße sind öffentlich.", font(56), ALU_L, anchor="ma")
    text(d, (960, 470), "Aluminium ist kein seltener Rohstoff.", font(56), ALU_L, anchor="ma")
    text(d, (960, 640), "Warum hat es niemand", font(78, True), KUPFER, anchor="ma")
    text(d, (960, 736), "nachgebaut?", font(78, True), KUPFER, anchor="ma")
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "KZ_CARD_FRAGE.png")


def karte_zeitmaschine() -> Path:
    """Das Wort, unter dem die Konstruktion im Netz laeuft — und was die
    Erbauer stattdessen sagen. Traegt die Umdeutung im Hook."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, "Zwei Beschreibungen derselben Anlage")
    rule(d, 82, 132, 1838)
    d.rounded_rectangle((110, 250, 930, 830), 10, fill=(14, 26, 48),
                        outline=(48, 72, 110), width=2)
    text(d, (520, 320), "IM NETZ", font(26, True, True), DIM, anchor="ma", spacing=5)
    text(d, (520, 430), "ZEITMASCHINE", font(64, True), (206, 214, 216), anchor="ma")
    text(d, (520, 560), "Das Wort haben die Erbauer", font(30), DIM, anchor="ma")
    text(d, (520, 604), "nie benutzt.", font(30), DIM, anchor="ma")
    d.rounded_rectangle((990, 250, 1810, 830), 10, fill=(12, 34, 34),
                        outline=AURORA_D, width=3)
    text(d, (1400, 320), "IM INSTITUT", font(26, True, True), AURORA, anchor="ma", spacing=5)
    text(d, (1400, 430), "KOZYREV-RAUM", font(64, True), AURORA, anchor="ma")
    text(d, (1400, 560), "Ein Zustand, in dem Information", font(30), (206, 214, 216), anchor="ma")
    text(d, (1400, 604), "von außen ankommt.", font(30), (206, 214, 216), anchor="ma")
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "KZ_CARD_ZEITMASCHINE.png")


def karte_comment() -> Path:
    """Mid-Roll-CTA, binaer gestellt — das kostet den Zuschauer eine Sekunde."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (960, 268), "Alles Einbildung —", font(64, True), ALU_L, anchor="ma")
    text(d, (960, 350), "oder ist da etwas?", font(64, True), ALU_L, anchor="ma")
    d.rounded_rectangle((470, 500, 900, 660), 10, fill=(12, 40, 34),
                        outline=AURORA, width=3)
    text(d, (685, 546), "JA", font(72, True), AURORA, anchor="ma")
    d.rounded_rectangle((1020, 500, 1450, 660), 10, fill=(44, 22, 14),
                        outline=KUPFER, width=3)
    text(d, (1235, 546), "NEIN", font(72, True), KUPFER, anchor="ma")
    text(d, (960, 742), "Schreib es in die Kommentare.", font(38), DIM, anchor="ma")
    text(d, (960, 828), "Gleich kommt der Versuch, den sie", font(34), KUPFER, anchor="ma")
    text(d, (960, 874), "am Nordpolarmeer aufgebaut haben.", font(34), KUPFER, anchor="ma")
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "KZ_CARD_COMMENT.png")


def endcard() -> Path:
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (960, 168), "NOESIS", font(46, True), AURORA, anchor="ma", spacing=14)
    rule(d, 660, 246, 1260)

    text(d, (960, 316), "Würdest du dich", font(60, True), ALU_L, anchor="ma")
    text(d, (960, 392), "in die Spiegel setzen?", font(60, True), KUPFER, anchor="ma")
    text(d, (960, 506), "Ja oder nein — schreib es in die Kommentare.",
         font(36), DIM, anchor="ma")

    # Endscreen-Flaeche rechts unten bleibt frei
    d.rounded_rectangle((150, 640, 800, 1000), 10, fill=(14, 28, 50),
                        outline=(48, 72, 110), width=2)
    text(d, (190, 690), "NÄCHSTE FOLGE", font(24, True, True), AURORA, spacing=4)
    text(d, (190, 742), "Nikolai Kozyrev", font(48, True), ALU_L)
    text(d, (190, 812), "Zehn Jahre Lager. Ein Teleskop.", font(30), DIM)
    text(d, (190, 854), "Und die Zeit als Kraft.", font(30), DIM)
    tri(d, 202, 942, 13, KUPFER)
    text(d, (228, 926), "Jetzt ansehen", font(32, True), KUPFER)

    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "KZ_ENDCARD.png")


# --------------------------------------------------------------- Thumbnail

def thumbnail(motiv: str = "spg_thumb_held") -> Path:
    """Ein Motiv, ein deutsches Schlagwort, hoher Kontrast.

    ZEITMASCHINE mit Fragezeichen ist der Suchbegriff und der
    Kommentartreiber — deshalb steht das Wort gross und ungebrochen im Bild.

    Der erste Entwurf zeigte ein Gesicht aus dem Bildgenerator. Ein Gesicht
    ist die Stelle, an der ein erzeugtes Bild zuerst auffliegt, und es hat den
    Blick auf sich gezogen statt auf die Anlage. Das Motiv zeigt die Person
    jetzt von hinten als Silhouette; erkennbar bleibt der Raum.

    Die Lesbarkeitsprobe bei 246 px entsteht im selben Lauf.
    """
    import numpy as np

    base = GEN / f"{motiv}.png"
    if not base.is_file():
        raise SystemExit(f"Motiv fehlt: {base}")
    img = Image.open(base).convert("RGB").resize((W, H), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.22)
    img = ImageEnhance.Color(img).enhance(1.28)

    # Polarlicht im Inneren der Spirale anheben, damit die Farbe bei 246 px
    # noch als Farbe ankommt und nicht als graues Rauschen.
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([880, 20, 1620, 620], fill=(18, 62, 48))
    gd.ellipse([1010, 60, 1500, 470], fill=(30, 96, 74))
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    img = Image.fromarray(np.clip(np.asarray(img).astype("int16")
                                  + np.asarray(glow).astype("int16"),
                                  0, 255).astype("uint8"))

    # Abdunkelung links als Verlauf — Textgrund, nicht Balken
    scrim = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scrim)
    for x in range(W):
        sd.line([(x, 0), (x, H)], fill=int(250 * max(0.0, 1 - x / 1040) ** 1.25))
    img = Image.composite(Image.new("RGB", (W, H), (4, 10, 22)), img, scrim)

    # Untere Kante absenken, damit der Ankerkasten aufsitzt
    fuss = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fuss)
    for y in range(H):
        fd.line([(0, y), (W, y)], fill=int(120 * max(0.0, (y - 760) / 320) ** 1.3))
    img = Image.composite(Image.new("RGB", (W, H), (4, 10, 22)), img, fuss)

    d = ImageDraw.Draw(img, "RGBA")

    # Eyebrow
    d.rectangle((96, 150, 108, 202), fill=KUPFER)
    text(d, (136, 152), "SIBIRIEN · PATENT RU 2122446", font(38, True, True),
         AURORA, spacing=6)

    # Schlagwort, zweizeilig. Einzeilig lief "ZEITMASCHINE?" ueber das Motiv
    # und stand mit gruener Schrift auf gruen reflektierendem Metall — bei
    # 246 px war die zweite Haelfte weg. Zwei Zeilen bleiben in der dunklen
    # linken Haelfte und tragen deutlich weiter.
    #
    # Farben wie in EP02: erste Zeile hell, zweite Zeile warm. Gruen auf
    # gruenem Polarlicht war der Fehler des ersten Entwurfs.
    f1 = font(166, True)
    schatten = (2, 8, 16)
    for dx, dy in ((6, 7), (0, 0)):
        text(d, (92 + dx, 246 + dy), "ZEIT", f1, schatten if dx else ALU_L)
        x = 92 + dx
        text(d, (x, 408 + dy), "MASCHINE", f1, schatten if dx else KUPFER)
        x += d.textlength("MASCHINE", font=f1)
        text(d, (x, 408 + dy), "?", f1, schatten if dx else AURORA)

    # Die Unterzeile treibt die Frage weiter. Ein "Sie sagen: nein." stand
    # hier vorher und hat die Ueberschrift im selben Bild zurueckgenommen.
    f2 = font(70, True)
    for dx, dy in ((4, 5), (0, 0)):
        text(d, (96 + dx, 614 + dy), "Die Erbauer meiden das Wort.", f2,
             schatten if dx else ALU_L)

    # Ein harter Anker, keine Textwand
    d.rounded_rectangle((92, 762, 1014, 922), 8, fill=(8, 20, 40, 236),
                        outline=AURORA_D, width=3)
    text(d, (126, 788), "TAUSENDE PROTOKOLLE", font(46, True), ALU_L)
    text(d, (126, 854), "ÜBER DREISSIG JAHRE · NOWOSIBIRSK", font(32), DIM)

    THUMB.mkdir(parents=True, exist_ok=True)
    img = grain(img, 4)
    voll = THUMB / "EP01A_SPIEGEL_THUMBNAIL.png"
    img.save(voll, quality=97)
    img.resize((1280, 720), Image.LANCZOS).save(
        THUMB / "EP01A_SPIEGEL_THUMBNAIL_1280x720.jpg", quality=94)
    klein = img.resize((246, 138), Image.LANCZOS)
    klein.save(THUMB / "_probe_246px.png")
    # Probe direkt neben das Vollbild legen, damit beides in einem Blick liegt
    probe = Image.new("RGB", (1280, 1104), (6, 12, 24))
    probe.paste(img.resize((1280, 720), Image.LANCZOS), (0, 0))
    pd = ImageDraw.Draw(probe)
    text(pd, (24, 748), "LESBARKEITSPROBE", font(24, True, True), AURORA, spacing=4)
    text(pd, (24, 788), "links: Originalgröße 246 px — so groß ist das Bild in der "
                        "YouTube-App", font(24), DIM)
    text(pd, (24, 822), "rechts: dieselben Pixel, zweifach vergrößert", font(24), DIM)
    probe.paste(klein, (24, 866))                       # exakt 246 px breit
    probe.paste(klein.resize((492, 276), Image.NEAREST), (330, 866))
    probe.save(THUMB / "_lesbarkeitsprobe.png")
    print(f"  Thumbnail  {img.size}  + 1280x720 + 246px-Probe")
    return voll


def main():
    print("Baue Grafiken EP01A Die Spiegel:")
    karte_patent()
    karte_masse()
    karte_muster()
    karte_aurora()
    karte_dikson()
    karte_schlussstand()
    karte_frage()
    karte_zeitmaschine()
    karte_comment()
    endcard()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "thumbnail":
        thumbnail(*sys.argv[2:3])
    else:
        main()
