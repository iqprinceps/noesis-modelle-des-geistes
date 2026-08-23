#!/usr/bin/env python3
"""EP04 Jung — Grafikbaukasten.

Abgeleitet von `tools/pear_graphics.py` (EP03); Bauweise, Raster und
Schriftgroessen bleiben unveraendert, damit die Karten im Kanal
gleich aussehen. Neu ist nur die Palette.

Die Farben kommen aus der Folge selbst: das Blauschwarz der Hoehle, das
Tuerkis und Rostorange des Eisvogels — Philemons Fluegel — und das Rot des
Ledereinbands. Kein Bernstein wie in EP03, damit die Folgen sich im Regal
unterscheiden.

Zwei Regeln aus der VISUAL_SPEC sind hart eingebaut:
  * hoechstens vier Eintraege je Karte
  * keine Fussnote, die die Karte wieder einkassiert
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP04_JUNG"
OUT = PROD / "visuals" / "cards"

W, H = 1920, 1080

# Palette EP04
NACHT = (11, 14, 20)          # 0B0E14  Hoehlenschwarz
NACHT_L = (22, 27, 36)        # 161B24
EISVOGEL = (94, 200, 214)     # 5EC8D6  Tuerkis — traegt die Auszeichnung
EISVOGEL_D = (38, 96, 108)    # 26606C
ROST = (206, 106, 58)         # CE6A3A  Rostorange der Unterseite
PAPIER = (232, 228, 218)      # E8E4DA
PAPIER_H = (246, 244, 238)    # F6F4EE
DIM = (118, 128, 142)         # 76808E
LINIE = (40, 46, 58)

F = "C:/Windows/Fonts/"


def font(size: int, bold: bool = False, narrow: bool = False) -> ImageFont.FreeTypeFont:
    if narrow:
        name = "ARIALNB.TTF" if bold else "ARIALN.TTF"
    else:
        name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(F + name, size)


def canvas(vignette: bool = True) -> Image.Image:
    img = Image.new("RGB", (W, H), NACHT)
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=int(150 * (1 - y / H) ** 1.3))
    img = Image.composite(Image.new("RGB", (W, H), NACHT_L), img, grad)
    if vignette:
        v = Image.new("L", (W, H), 0)
        ImageDraw.Draw(v).ellipse([-W * .28, -H * .42, W * 1.28, H * 1.42], fill=255)
        v = v.filter(ImageFilter.GaussianBlur(190))
        img = Image.composite(img, Image.new("RGB", (W, H), (4, 6, 12)), v)
    return img


def grain(img: Image.Image, amount: int = 5) -> Image.Image:
    import numpy as np
    a = np.asarray(img).astype("int16")
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


def eyebrow(d, x, y, s, col=EISVOGEL):
    text(d, (x, y), s.upper(), font(22, True, True), col, spacing=4)


def rule(d, x1, y, x2, col=LINIE, wdt=2):
    d.line([(x1, y), (x2, y)], fill=col, width=wdt)


def footer(d, s):
    text(d, (82, H - 52), s.upper(), font(19, False, True), (92, 104, 122), spacing=3)


def tri(d, x, y, size, col, left=False):
    s = size
    pts = [(x + s, y - s), (x + s, y + s), (x - s, y)] if left else \
          [(x - s, y - s), (x - s, y + s), (x + s, y)]
    d.polygon(pts, fill=col)


def save(img: Image.Image, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    grain(img).save(path)
    print(f"  {name}")
    return path


# ------------------------------------------------------------ rechte Haelfte

def signet(d, cx=1520, cy=612, R=250):
    """Die zusammengerollte Schlange — das Motiv der Folge."""
    for i in range(3):
        r = R - i * 46
        d.ellipse((cx - r, cy - r * .78, cx + r, cy + r * .78),
                  outline=EISVOGEL_D, width=3)
    schritt = 150
    for k in range(schritt):
        t = k / (schritt - 1)
        w = 2.4 * math.pi * t
        r = R * (.30 + .58 * t)
        x = cx + r * math.cos(w)
        y = cy + r * .78 * math.sin(w)
        rad = 3 + 7 * t
        col = EISVOGEL if t > .55 else EISVOGEL_D
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col)
    d.ellipse((cx + R * .80, cy - 12, cx + R * .80 + 22, cy + 10), fill=ROST)


def gr_stammbaum(d, cx=1520, cy=600):
    """Die Kette der Ueberlieferung, Stufe fuer Stufe."""
    stufen = [("1577", "Bengalen"), ("1919", "London"), ("1927", "Adyar"),
              ("1930er", "Farbtherapie"), ("1977", "Regenbogen")]
    x = cx - 300
    y0 = cy - 210
    for i, (jahr, ort) in enumerate(stufen):
        y = y0 + i * 108
        col = ROST if i >= 3 else EISVOGEL
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=col)
        if i:
            d.line([(x, y - 99), (x, y - 12)], fill=LINIE, width=3)
        text(d, (x + 34, y - 22), jahr, font(38, True), PAPIER_H)
        text(d, (x + 34, y + 12), ort, font(26), DIM)


def gr_sechs(d, cx=1520, cy=600):
    """Eine grosse Sechs. Mehr braucht die Karte nicht."""
    text(d, (cx, cy - 190), "6", font(320, True), EISVOGEL, anchor="ma")
    rule(d, cx - 190, cy + 190, cx + 190, EISVOGEL_D, 3)
    text(d, (cx, cy + 216), "ZENTREN", font(30, True, True), PAPIER, anchor="ma", spacing=8)


def gr_sprung(d, cx=1520, cy=600):
    """Vom Feuer zur Luft: unten dichte warme Punkte, oben weite kuehle."""
    import random
    rng = random.Random(4)
    for i in range(420):
        t = rng.random() ** 1.6
        y = cy + 250 - t * 500
        streu = 150 + t * 130
        x = cx + rng.uniform(-streu, streu)
        r = 7 - 5 * t
        col = ROST if t < .45 else EISVOGEL
        alpha = int(230 - 120 * t)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (alpha,))
    text(d, (cx, cy + 292), "FEUER", font(26, True, True), ROST, anchor="ma", spacing=6)
    text(d, (cx, cy - 330), "LUFT", font(26, True, True), EISVOGEL, anchor="ma", spacing=6)


def gr_weltkarte(d, cx=1520, cy=600):
    """Vier Orte, drei Boegen. Keine Kuestenlinien — nur die Kette."""
    orte = [("KALKUTTA", cx - 250, cy + 170), ("LONDON", cx - 60, cy - 60),
            ("ZÜRICH", cx + 110, cy + 30), ("KALIFORNIEN", cx + 250, cy + 210)]
    for i in range(len(orte) - 1):
        x1, y1 = orte[i][1], orte[i][2]
        x2, y2 = orte[i + 1][1], orte[i + 1][2]
        for k in range(26):
            t = k / 25
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t - math.sin(math.pi * t) * 54
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=EISVOGEL_D)
    for name, x, y in orte:
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=EISVOGEL)
        text(d, (x, y + 22), name, font(22, True, True), PAPIER, anchor="ma", spacing=3)


def gr_serpent(d, cx=1520, cy=600):
    """Ein aufgestellter Band, halb geoeffnet, von der Seite."""
    # Buchblock
    d.polygon([(cx - 150, cy + 240), (cx - 20, cy + 190),
               (cx - 20, cy - 210), (cx - 150, cy - 160)], fill=(214, 208, 192))
    for i in range(16):
        x = cx - 146 + i * 8
        d.line([(x, cy + 238 - i * 3), (x, cy - 158 - i * 3)],
               fill=(178, 170, 152), width=1)
    # Deckel
    d.polygon([(cx - 158, cy + 248), (cx - 12, cy + 196),
               (cx - 12, cy - 216), (cx - 158, cy - 168)],
              outline=(126, 52, 40), width=4)
    d.polygon([(cx - 12, cy + 196), (cx + 150, cy + 236),
               (cx + 150, cy - 176), (cx - 12, cy - 216)],
              fill=(84, 28, 24), outline=(126, 52, 40), width=4)
    # blinde Praegung: ein Ring, kein Titel
    d.ellipse((cx + 24, cy - 66, cx + 116, cy + 26), outline=(132, 60, 46), width=4)
    d.ellipse((cx + 46, cy - 44, cx + 94, cy + 4), outline=(132, 60, 46), width=3)


def gr_schichten(d, cx=1520, cy=600):
    """Sechzehn Jahre als Schichten — unten roh, oben ausgearbeitet."""
    for i in range(16):
        t = i / 15
        y = cy + 230 - i * 30
        breite = 60 + 190 * (1 - abs(t - .5) * 1.2)
        col = EISVOGEL if t > .62 else (EISVOGEL_D if t > .3 else (52, 58, 70))
        d.rounded_rectangle((cx - breite, y - 9, cx + breite, y + 9), 6, fill=col)
    text(d, (cx, cy + 266), "1913 – 1930", font(26, True, True), DIM,
         anchor="ma", spacing=5)


def gr_gefaess(d, cx=1520, cy=600):
    """Ein Gefaess, und was ueber seinen Rand hinaus steigt."""
    d.arc((cx - 150, cy - 40, cx + 150, cy + 280), 0, 180, fill=EISVOGEL_D, width=6)
    d.line([(cx - 150, cy + 110), (cx - 150, cy - 30)], fill=EISVOGEL_D, width=6)
    d.line([(cx + 150, cy + 110), (cx + 150, cy - 30)], fill=EISVOGEL_D, width=6)
    d.line([(cx - 182, cy - 30), (cx + 182, cy - 30)], fill=EISVOGEL_D, width=6)
    import random
    rng = random.Random(9)
    for i in range(150):
        t = rng.random() ** 1.4
        y = cy - 40 - t * 300
        x = cx + rng.uniform(-70 - t * 150, 70 + t * 150)
        r = 6 - 4 * t
        d.ellipse((x - r, y - r, x + r, y + r),
                  fill=ROST + (int(220 - 130 * t),))


def gr_umschlag(d, cx=1520, cy=600):
    """Ein Umschlag: eine Zeile gesetzt, eine Zeile leer."""
    d.rounded_rectangle((cx - 190, cy - 250, cx + 190, cy + 250), 6,
                        fill=(30, 36, 46), outline=(58, 68, 84), width=3)
    rule(d, cx - 130, cy - 60, cx + 130, (86, 100, 120), 4)
    rule(d, cx - 130, cy - 20, cx + 60, (86, 100, 120), 4)
    text(d, (cx, cy + 60), "ARTHUR AVALON", font(28, True, True), PAPIER,
         anchor="ma", spacing=4)
    # die zweite Zeile bleibt offen
    d.line([(cx - 130, cy + 132), (cx + 130, cy + 132)], fill=ROST, width=3)
    for x in range(cx - 130, cx + 130, 22):
        d.line([(x, cy + 132), (x + 11, cy + 132)], fill=(30, 36, 46), width=5)


def gr_traeume(d, cx=1520, cy=600):
    """Tausend Punkte, vierhundert davon hell."""
    import random
    rng = random.Random(7)
    punkte = []
    for i in range(1000):
        punkte.append((cx + rng.uniform(-250, 250), cy + rng.uniform(-230, 230)))
    for i, (x, y) in enumerate(punkte):
        hell = i % 5 < 2
        r = 3.4 if hell else 2.2
        d.ellipse((x - r, y - r, x + r, y + r),
                  fill=EISVOGEL if hell else (46, 54, 66))
    text(d, (cx, cy + 268), "400 VON 1.000", font(26, True, True), EISVOGEL,
         anchor="ma", spacing=5)


# ------------------------------------------------------------------- Karten

def list_card(name, eyebrow_txt, title, rows, quelle, grafik=None) -> Path:
    if len(rows) > 4:
        raise ValueError(f"{name}: {len(rows)} Eintraege, erlaubt sind vier")
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    (grafik or signet)(d)
    eyebrow(d, 82, 78, eyebrow_txt)
    text(d, (82, 116), title, font(60, True), PAPIER_H)
    rule(d, 82, 202, 1838)
    y = 268 if len(rows) >= 3 else 360
    schritt = {1: 0, 2: 190, 3: 176, 4: 176}[len(rows)]
    for label, desc in rows:
        d.rectangle((82, y + 6, 90, y + 56), fill=ROST)
        text(d, (118, y), label, font(40, True), EISVOGEL)
        text(d, (118, y + 58), desc, font(32), (206, 214, 216))
        y += schritt
    footer(d, quelle)
    return save(img, name)


def zitat_karte(name, eyebrow_txt, zeilen, quelle, uebersetzung="") -> Path:
    """Ein Zitat, gross, mit Sprecher darunter. Kein Kommentar dazu."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, eyebrow_txt)
    rule(d, 82, 132, 1838)
    y = 330 if not uebersetzung else 262
    d.text((150, y - 46), "“", font=font(150, True), fill=EISVOGEL_D + (220,))
    for z in zeilen:
        text(d, (960, y), z, font(52, True), PAPIER_H, anchor="ma")
        y += 76
    if uebersetzung:
        y += 26
        for z in uebersetzung.split("|"):
            text(d, (960, y), z, font(34), DIM, anchor="ma")
            y += 48
        y += 8
    text(d, (960, max(y + 40, 806)), quelle, font(30, True, True), EISVOGEL,
         anchor="ma", spacing=4)
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, name)


def satz_karte(name, eyebrow_txt, zeilen, unterzeile="", quelle="") -> Path:
    """Eine Aussage, mittig, ohne Liste. Fuer Begriffe und Wendepunkte."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, eyebrow_txt)
    rule(d, 82, 132, 1838)
    y = 400 if not unterzeile else 360
    for i, z in enumerate(zeilen):
        text(d, (960, y), z, font(64, True),
             EISVOGEL if i == len(zeilen) - 1 and len(zeilen) > 1 else PAPIER_H,
             anchor="ma")
        y += 88
    if unterzeile:
        y += 40
        text(d, (960, y), unterzeile, font(34), DIM, anchor="ma")
    footer(d, quelle or "NOESIS · Modelle des Geistes")
    return save(img, name)


# ----------------------------------------------------------------- S2 bis S4

def k_aktive_imagination():
    return satz_karte(
        "JU_CARD_AKTIVE_IMAGINATION.png", "Die Methode", ["AKTIVE IMAGINATION"],
        "Kein Zuschauen. Beteiligung.")


def k_philemon_zitat():
    return zitat_karte(
        "JU_CARD_ZITAT_PHILEMON.png", "Philemon",
        ["Thoughts were like animals in the forest,",
         "or people in a room, or birds in the air."],
        "C. G. Jung, Erinnerungen, Träume, Gedanken",
        "Gedanken seien wie Tiere im Wald. Wie Menschen in einem Zimmer.|"
        "Wie Vögel in der Luft. Man begegnet ihnen. Man macht sie nicht.")


def k_psychische_objektivitaet():
    return satz_karte(
        "JU_CARD_PSYCHISCHE_OBJEKTIVITAET.png", "Was Jung daraus zog",
        ["PSYCHISCHE OBJEKTIVITÄT"],
        "Etwas im eigenen Kopf, das man nicht selbst herstellt.")


def k_begriffe():
    return list_card(
        "JU_CARD_BEGRIFFE.png", "Was aus sechzehn Jahren wurde",
        "JEDER BEGRIFF",
        [("DAS KOLLEKTIVE UNBEWUSSTE", "die Schicht unter der persönlichen Erinnerung"),
         ("DIE ARCHETYPEN", "die Gestalten, die dort von selbst auftreten"),
         ("DIE INDIVIDUATION", "der Weg, auf dem ein Mensch er selbst wird"),
         ("DAS SELBST", "das Ganze, das mehr ist als das Ich")],
        "Das Rote Buch — Liber Novus, 1913–1930")


# ------------------------------------------------------------------- S5

def k_hauer():
    return list_card(
        "JU_CARD_HAUER.png", "Der Mann eine Woche zuvor",
        "JAKOB WILHELM HAUER",
        [("OKTOBER 1932", "spricht in Zürich über tantrischen Yoga"),
         ("30. JULI 1933", "gründet die Deutsche Glaubensbewegung"),
         ("1934", "spätestens jetzt Mitglied der SS")],
        "Horst Junginger, Universität Tübingen")


def k_warnung():
    return zitat_karte(
        "JU_CARD_ZITAT_WARNUNG.png", "Zürich, Herbst 1932",
        ["These things are really dangerous and ought not to be",
         "meddled with in our typically Western way."],
        "C. G. Jung",
        "Diese Dinge seien wirklich gefährlich, und man solle sie nicht|"
        "auf unsere typisch westliche Weise anfassen.")


def k_drei_warnungen():
    return list_card(
        "JU_CARD_DREI_WARNUNGEN.png", "Vier Abende lang", "SEINE WARNUNG",
        [("DAS GEFÄSS FEHLT", "Der Europäer nimmt die Technik und lässt den Rahmen liegen"),
         ("DAS WOLLEN IST FALSCH", "Wer etwas erreichen will, benutzt das falsche Werkzeug"),
         ("OHNE HALT ÜBERNIMMT ES", "Die Inhalte erleuchten nicht. Sie nehmen den Platz ein")],
        "Seminar über Kundalini-Yoga, 1932")


def k_cta():
    return satz_karte(
        "JU_CARD_CTA.png", "Kurze Zwischenfrage",
        ["Hattest du je einen Gedanken,", "der nicht von dir kam?"],
        "Schreib es in die Kommentare.")


# ------------------------------------------------------------------- S6

def k_uebergang():
    return satz_karte(
        "JU_CARD_UEBERGANG.png", "Jungs Lesart",
        ["MULADHARA", "→  MANIPURA"],
        "Vom konkreten Problem zum Affekt, der einen ergreift.")


def k_sprung():
    return list_card(
        "JU_CARD_SPRUNG.png", "Der entscheidende Schritt", "MANIPURA → ANAHATA",
        [("FEUER", "Der Mensch ist mit seinem Erleben identisch"),
         ("LUFT", "Zwischen Impuls und Handlung entsteht eine Lücke")],
        "Seminar über Kundalini-Yoga, 1932", grafik=gr_sprung)


def k_emotion():
    return satz_karte(
        "JU_CARD_EMOTION.png", "Der ganze Unterschied",
        ["„Ich BIN diese Emotion.“", "„Ich HABE diese Emotion.“"],
        "Vom Brennen zum Atmen.")


# ------------------------------------------------------------------- S7

def k_serpent_power():
    return list_card(
        "JU_CARD_SERPENT_POWER.png", "Die westliche Standardquelle",
        "THE SERPENT POWER",
        [("ARTHUR AVALON", "Deckname von Sir John Woodroffe"),
         ("LUZAC & CO., LONDON", "Verlag der Erstausgabe"),
         ("1919", "Erscheinungsjahr"),
         ("ṢAṬ-CAKRA-NIRŪPAṆA", "der übersetzte Text, Bengalen 1577")],
        "The Serpent Power, London 1919", grafik=gr_serpent)


def k_sechs():
    return satz_karte(
        "JU_CARD_SECHS.png", "Der Titel des Originals",
        ["Ṣaṭ-cakra-nirūpaṇa", "Beschreibung der sechs Zentren"],
        "Sahasrara kommt im Text vor. Als Chakra gezählt wird es dort nicht.",
        "Bengalen, 1577")


def k_ghose():
    return list_card(
        "JU_CARD_GHOSE.png", "Der Name auf keinem Umschlag",
        "ATAL BIHARI GHOSE",
        [("BENGALISCHER GELEHRTER", "leistete über Jahrzehnte die Sanskrit-Arbeit"),
         ("ARTHUR AVALON", "der Deckname lieh ihm den Rang eines britischen Richters"),
         ("KATHLEEN TAYLOR, 2001", "arbeitete die Zusammenarbeit als erste auf")],
        "Kathleen Taylor, Sir John Woodroffe, Tantra and Bengal")


def k_stammbaum():
    return list_card(
        "JU_CARD_STAMMBAUM.png", "Wie die Karte entstand", "DREI JAHRHUNDERTE",
        [("SECHS WERDEN SIEBEN", "beim Weiterzählen im Westen"),
         ("DIE FARBEN KOMMEN DAZU", "ab den dreißiger Jahren, festgezurrt um 1977"),
         ("VIER LÄNDER", "Menschen, die einander nie begegnet sind")],
        "Bengalen 1577 · London 1919 · Adyar 1927 · 1977",
        grafik=gr_stammbaum)


def k_weltkarte():
    return list_card(
        "JU_CARD_WELTKARTE.png", "Die Kette", "VON KALKUTTA NACH KALIFORNIEN",
        [("1919 LONDON", "Woodroffe übersetzt, Ghose arbeitet ungenannt"),
         ("1932 ZÜRICH", "Jung liest die Karte als Psychologie"),
         ("1977 KALIFORNIEN", "der Regenbogen wird endgültig festgelegt")],
        "NOESIS · Modelle des Geistes", grafik=gr_weltkarte)


# ------------------------------------------------------------------- S8

def k_wer_sprach():
    return satz_karte(
        "JU_CARD_WER_SPRACH.png", "Was offen bleibt",
        ["WER HAT GESPROCHEN?"],
        "Was Philemon war, hat Jung nie gesagt.")


def k_flaschenpost():
    return zitat_karte(
        "JU_CARD_ZITAT_FLASCHENPOST.png", "Das Rote Buch",
        ["Eine Flaschenpost, ins Meer geworfen —", "in der Hoffnung, jemand findet sie."],
        "Sonu Shamdasani, Herausgeber",
        "Geworfen zwischen 1913 und 1930. Gefunden 2009.")


def k_pauli():
    return list_card(
        "JU_CARD_PAULI.png", "Im selben Jahr", "ÜBER TAUSEND TRÄUME",
        [("JANUAR 1932", "erste Konsultation bei Jung"),
         ("PROFESSOR AN DER ETH", "später Nobelpreis für Physik"),
         ("VIERHUNDERT", "davon hat Jung in seiner Arbeit verwendet")],
        "Atom and Archetype — Die Pauli/Jung-Briefe")


def k_endcard():
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (960, 168), "NOESIS", font(46, True), EISVOGEL, anchor="ma", spacing=14)
    rule(d, 660, 246, 1260)

    text(d, (960, 316), "Hattest du je einen Gedanken,", font(58, True), PAPIER_H,
         anchor="ma")
    text(d, (960, 390), "der nicht von dir kam?", font(58, True), ROST, anchor="ma")
    text(d, (960, 504), "Schreib es in die Kommentare.", font(36), DIM, anchor="ma")

    # Endscreen-Flaeche rechts unten bleibt frei
    d.rounded_rectangle((150, 640, 800, 1000), 10, fill=(12, 26, 34),
                        outline=(44, 82, 96), width=2)
    text(d, (190, 690), "NÄCHSTE FOLGE", font(24, True, True), EISVOGEL, spacing=4)
    text(d, (190, 742), "Pauli und Jung", font(48, True), PAPIER_H)
    text(d, (190, 812), "Ein Nobelpreisträger bringt tausend Träume", font(30), DIM)
    text(d, (190, 854), "zu einem Psychiater. Zürich, 1932.", font(30), DIM)
    tri(d, 202, 942, 13, ROST)
    text(d, (228, 926), "Jetzt ansehen", font(32, True), ROST)

    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "JU_ENDCARD.png")


ALLE = [k_aktive_imagination, k_philemon_zitat, k_psychische_objektivitaet,
        k_begriffe, k_hauer, k_warnung, k_drei_warnungen, k_cta,
        k_uebergang, k_sprung, k_emotion, k_serpent_power, k_sechs,
        k_ghose, k_stammbaum, k_weltkarte, k_wer_sprach, k_flaschenpost,
        k_pauli, k_endcard]


def main():
    print(f"EP04 — {len(ALLE)} Karten nach {OUT.relative_to(ROOT)}")
    for f in ALLE:
        f()


if __name__ == "__main__":
    main()
