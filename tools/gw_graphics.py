#!/usr/bin/env python3
"""Gateway V6 — Grafikbaukasten.

Baut alle Karten, das Drei-Beobachter-Bild, die Endcard und das Thumbnail
direkt mit Pillow. Kein KI-Text, kein SVG-Renderer noetig: jeder Buchstabe
steht exakt so im Bild, wie er hier im Code steht.

Palette nach dem Style Key des Projekts (tools/gateway_image_gen.py).
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V6" / "visuals" / "cards"

W, H = 1920, 1080

NAVY = (4, 17, 20)
NAVY_L = (10, 30, 35)
GREY = (42, 58, 63)
CYAN = (91, 210, 211)
CYAN_D = (44, 120, 126)
WHITE = (238, 235, 224)
GOLD = (224, 174, 71)
DIM = (128, 146, 150)

F = "C:/Windows/Fonts/"


def font(size: int, bold: bool = False, narrow: bool = False) -> ImageFont.FreeTypeFont:
    if narrow:
        name = "ARIALNB.TTF" if bold else "ARIALN.TTF"
    else:
        name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(F + name, size)


def canvas(vignette: bool = True) -> Image.Image:
    """Basisflaeche mit leichtem Verlauf und Vignette."""
    img = Image.new("RGB", (W, H), NAVY)
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=int(26 * (1 - y / H)))
    img = Image.composite(Image.new("RGB", (W, H), NAVY_L), img, grad)
    if vignette:
        v = Image.new("L", (W, H), 0)
        ImageDraw.Draw(v).ellipse([-W * 0.28, -H * 0.42, W * 1.28, H * 1.42], fill=255)
        v = v.filter(ImageFilter.GaussianBlur(190))
        img = Image.composite(img, Image.new("RGB", (W, H), (2, 9, 11)), v)
    return img


def grain(img: Image.Image, amount: int = 5) -> Image.Image:
    import numpy as np
    a = np.asarray(img).astype(np.int16)
    rng = np.random.default_rng(11)
    n = rng.integers(-amount, amount + 1, a.shape[:2])[:, :, None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype("uint8"))


def text(d, xy, s, f, fill, anchor="la", spacing=0):
    """Text mit optionaler Laufweite (Pillow kennt kein letter-spacing)."""
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


def eyebrow(d, x, y, s, col=CYAN):
    """Kleine Ueberschriftzeile mit Laufweite."""
    text(d, (x, y), s.upper(), font(22, True, True), col, spacing=4)


def rule(d, x1, y, x2, col=(28, 52, 58), wdt=2):
    d.line([(x1, y), (x2, y)], fill=col, width=wdt)


def footer(d, s):
    text(d, (82, H - 52), s.upper(), font(19, False, True), (86, 104, 108), spacing=3)


def tri(d, x, y, size, col, left=False):
    """Dreieckspfeil — Arial hat keine Pfeilglyphen."""
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


# ---------------------------------------------------------------- Beobachter

def observer_protocol() -> Path:
    """Ersetzt gw_observer_protocol.png.

    Korrekt: Beobachter 1 = GEGENWART (die Narration sagt 'Der erste
    beobachtet es jetzt'), 2 = VERGANGENHEIT, 3 = ZUKUNFT.
    """
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")

    eyebrow(d, 82, 74, "U.S. Army Gateway Report 1983 · Empfehlung H")
    text(d, (82, 112), "DREI BEOBACHTER, DREI ZEITEN", font(62, True), WHITE)
    rule(d, 82, 196, 1838)

    cy = 640
    slots = [
        (470, "2", "VERGANGENHEIT", "Focus 15", CYAN),
        (960, "1", "GEGENWART", "normale Raum-Zeit", GOLD),
        (1450, "3", "ZUKUNFT", "Focus 21", CYAN),
    ]

    # Zielachse
    d.line([(300, cy), (1620, cy)], fill=(26, 48, 54), width=3)
    for x in range(300, 1621, 26):
        d.line([(x, cy), (x + 12, cy)], fill=(38, 74, 82), width=3)

    for x, num, label, sub, col in slots:
        main = col is GOLD
        r = 92 if main else 78
        d.ellipse([x - r - 16, cy - r - 16, x + r + 16, cy + r + 16],
                  fill=(8, 24, 28), outline=(24, 46, 52), width=2)
        d.ellipse([x - r, cy - r, x + r, cy + r], outline=col, width=4 if main else 3)
        text(d, (x, cy - 4), num, font(76 if main else 64, True), col, anchor="mm")
        text(d, (x, cy + r + 62), label, font(34, True), WHITE, anchor="ma")
        text(d, (x, cy + r + 106), sub, font(26), DIM, anchor="ma")

    # Zielobjekt in der Mitte, Zeitachse darunter
    d.rounded_rectangle((860, cy - 336, 1060, cy - 236), 8,
                        fill=(10, 32, 36), outline=GOLD, width=3)
    d.ellipse([936, cy - 310, 984, cy - 262], outline=GOLD, width=3)
    d.line([(960, cy - 236), (960, cy - 92)], fill=(52, 96, 104), width=2)
    text(d, (960, cy - 386), "DASSELBE ZIEL", font(30, True), WHITE, anchor="ma")

    # Zeitpfeile
    d.line([(690, cy - 178), (900, cy - 178)], fill=(52, 96, 104), width=2)
    tri(d, 672, cy - 178, 11, (52, 96, 104), left=True)
    d.line([(1020, cy - 178), (1230, cy - 178)], fill=(52, 96, 104), width=2)
    tri(d, 1248, cy - 178, 11, (52, 96, 104))
    text(d, (690, cy - 216), "rutscht in die Vergangenheit", font(24), DIM, anchor="la")
    text(d, (1230, cy - 216), "rutscht in die Zukunft", font(24), DIM, anchor="ra")

    box = (82, 900, 1838, 992)
    d.rounded_rectangle(box, 6, fill=(8, 26, 30), outline=(30, 58, 64), width=2)
    text(d, (960, 930), "Danach werden alle drei Angaben verglichen.",
         font(32), WHITE, anchor="ma")

    footer(d, "Editorische Grafik nach Empfehlung H · kein Ergebnisbericht")
    return save(img, "V6_CARD_OBSERVER_PROTOCOL.png")


# ------------------------------------------------------------ Ersatz-Karten

def question_card() -> Path:
    """Ersetzt den Kettlebell-Clip bei 0:41 — 'Die eigentliche Frage'."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 74, "Die eigentliche Frage")
    rule(d, 82, 128, 1838)

    y = 330
    for line, col in [("Wie kam ein Militäranalyst dazu,", WHITE),
                      ("Vergangenheit und Zukunft", WHITE),
                      ("als Zielkoordinaten zu behandeln?", GOLD)]:
        text(d, (82, y), line, font(78, True), col)
        y += 128
    footer(d, "U.S. Army Gateway Report · 9. Juni 1983")
    return save(img, "V6_CARD_QUESTION.png")


def study_card() -> Path:
    """Ersetzt den Nachtclub-Clip bei 8:03 — 'Fünf Studien'."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 74, "Systematischer Review 2023")
    text(d, (82, 112), "WAS DIE FORSCHUNG PRÜFT", font(58, True), WHITE)
    rule(d, 82, 196, 1838)

    cols = [
        ("GEPRÜFT", CYAN, ["Aufmerksamkeit und Angst", "Hirnaktivität im EEG"]),
        ("BEFUND", GOLD, ["kleine Effekte", "je nach Methode verschieden"]),
        ("OFFEN", (176, 92, 92), ["Fernwahrnehmung", "Zeitwahrnehmung"]),
    ]
    bw, gap = 540, 60
    for i, (title, col, items) in enumerate(cols):
        x = 82 + i * (bw + gap)
        d.rounded_rectangle((x, 250, x + bw, 830), 8, fill=(8, 26, 30), outline=(28, 54, 60), width=2)
        d.line([(x, 250), (x + bw, 250)], fill=col, width=5)
        text(d, (x + bw / 2, 288), title, font(30, True), col, anchor="ma")
        yy = 372
        for it in items:
            d.ellipse([x + 44, yy + 12, x + 56, yy + 24], fill=col)
            text(d, (x + 78, yy), it, font(30), WHITE)
            yy += 104

    text(d, (960, 892), "Fünf Studien zu Gateway-nahen Fragen — keine zum außergewöhnlichen Anspruch.",
         font(30), DIM, anchor="ma")
    footer(d, "Zusammenfassung des Reviews · editorische Grafik")
    return save(img, "V6_CARD_STUDIES.png")


def myth_card() -> Path:
    """Ersetzt den Kettlebell-Clip bei 9:12 — 'virale Kurzfassung'."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 74, "Legende gegen Akte")
    rule(d, 82, 128, 1838)

    d.rounded_rectangle((82, 230, 930, 830), 8, fill=(26, 12, 12), outline=(96, 44, 44), width=2)
    d.line([(82, 230), (930, 230)], fill=(176, 92, 92), width=5)
    text(d, (506, 272), "DIE VIRALE KURZFASSUNG", font(30, True), (206, 122, 122), anchor="ma")
    text(d, (506, 400), "„Die CIA bewies,", font(52, True), WHITE, anchor="ma")
    text(d, (506, 470), "dass Gateway", font(52, True), WHITE, anchor="ma")
    text(d, (506, 540), "funktioniert.“", font(52, True), WHITE, anchor="ma")
    text(d, (506, 680), "Falsch in drei Punkten:", font(28), (150, 110, 110), anchor="ma")
    text(d, (506, 726), "Autor · Inhalt · Ergebnis", font(28, True), (206, 122, 122), anchor="ma")

    d.rounded_rectangle((990, 230, 1838, 830), 8, fill=(8, 26, 30), outline=(34, 74, 80), width=2)
    d.line([(990, 230), (1838, 230)], fill=GOLD, width=5)
    text(d, (1414, 272), "WAS DIE AKTE TRÄGT", font(30, True), GOLD, anchor="ma")
    yy = 372
    for line in ["Ein Bericht der U.S. Army",
                 "Auftrag: Mechanik und Nutzbarkeit",
                 "Empfehlung H, im Wortlaut"]:
        d.ellipse([1026, yy + 12, 1038, yy + 24], fill=CYAN)
        text(d, (1060, yy), line, font(30), WHITE)
        yy += 84

    footer(d, "Editorische Gegenüberstellung")
    return save(img, "V6_CARD_MYTH.png")


def hertz_card() -> Path:
    """Ersetzt den Kettlebell-Clip bei 2:25 — 'ungefähr 10 Hertz'."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 74, "Binauraler Beat")
    rule(d, 82, 128, 1838)

    def wave(y, freq, col, amp=54, width=3):
        pts = []
        for px in range(300, 1640):
            t = (px - 300) / 1340
            pts.append((px, y + amp * math.sin(2 * math.pi * freq * t)))
        d.line(pts, fill=col, width=width, joint="curve")

    text(d, (150, 246), "LINKS", font(30, True), CYAN, anchor="rm")
    wave(246, 20, CYAN)
    text(d, (1700, 246), "400 Hz", font(32, True), WHITE, anchor="lm")

    text(d, (150, 446), "RECHTS", font(30, True), CYAN, anchor="rm")
    wave(446, 20.5, CYAN)
    text(d, (1700, 446), "410 Hz", font(32, True), WHITE, anchor="lm")

    d.line([(300, 570), (1640, 570)], fill=(28, 52, 58), width=2)

    text(d, (150, 716), "GEHÖRT", font(30, True), GOLD, anchor="rm")
    pts = []
    for px in range(300, 1640):
        t = (px - 300) / 1340
        env = math.sin(math.pi * 0.5 * t * 2)
        pts.append((px, 716 + 76 * env * math.sin(2 * math.pi * 20.25 * t)))
    d.line(pts, fill=GOLD, width=3, joint="curve")
    text(d, (1700, 716), "≈ 10 Hz", font(38, True), GOLD, anchor="lm")

    d.rounded_rectangle((82, 872, 1838, 962), 6, fill=(8, 26, 30), outline=(30, 58, 64), width=2)
    text(d, (960, 902), "Der dritte Rhythmus kommt nicht aus dem Raum — er entsteht im Hören.",
         font(32), WHITE, anchor="ma")
    footer(d, "Editorische Grafik · Werte nach dem Bericht")
    return save(img, "V6_CARD_HERTZ.png")


# -------------------------------------------------------------------- Ende

def endcard() -> Path:
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (960, 168), "NOESIS", font(46, True), CYAN, anchor="ma", spacing=14)
    rule(d, 660, 246, 1260, (30, 58, 64))

    text(d, (960, 316), "Würdest du dich auf", font(60, True), WHITE, anchor="ma")
    text(d, (960, 392), "Empfehlung H einlassen?", font(60, True), GOLD, anchor="ma")
    text(d, (960, 506), "Schreib es in die Kommentare.", font(36), DIM, anchor="ma")

    # Platzhalterflaechen fuer YouTube-Endscreens (rechts unten frei lassen)
    d.rounded_rectangle((150, 640, 800, 1000), 10, fill=(8, 26, 30), outline=(30, 58, 64), width=2)
    text(d, (190, 690), "NÄCHSTE AKTE", font(24, True, True), CYAN, spacing=4)
    text(d, (190, 742), "Der Kozyrev-Spiegel", font(48, True), WHITE)
    text(d, (190, 812), "Eine Maschine, für die es", font(30), DIM)
    text(d, (190, 854), "wirklich ein Patent gibt.", font(30), DIM)
    tri(d, 202, 942, 13, GOLD)
    text(d, (228, 926), "Jetzt ansehen", font(32, True), GOLD)

    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "V6_ENDCARD.png")


def main():
    print("Baue Gateway V6 Grafiken:")
    observer_protocol()
    question_card()
    study_card()
    myth_card()
    hertz_card()
    endcard()


if __name__ == "__main__":
    main()


# --------------------------------------------------------------- Thumbnail

def thumbnail() -> Path:
    """Ersetzt THUMBNAIL01_PAST_FUTURE.png.

    Das alte Thumbnail hatte links eine unlesbare englische Textwand und
    rechts drei generische Piktogramme — bei 246 px Breite ein grauer Fleck.
    Neu: ein Motiv, ein deutsches Wort, hoher Kontrast.
    """
    base = Path(__file__).resolve().parents[1] / "05_GENERATED" / "EP02_GATEWAY_V2" / \
        "AI_FINAL" / "GWV2_IMG05_FOCUS15_TIME_WHEEL_16x9.png"
    img = Image.open(base).convert("RGB").resize((W, H), Image.LANCZOS)

    # Motiv nach rechts schieben, links Platz fuer Typo
    img = img.transform((W, H), Image.AFFINE, (1, 0, -210, 0, 1, 0), Image.BICUBIC)
    img = img.filter(ImageFilter.GaussianBlur(0.4))

    # Kontrast anheben, damit die Silhouette auch klein traegt
    from PIL import ImageEnhance
    img = ImageEnhance.Contrast(img).enhance(1.22)
    img = ImageEnhance.Color(img).enhance(0.88)

    # Abdunkelung links als Verlauf
    scrim = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scrim)
    for x in range(W):
        # max() vor der Potenz: negative Basis hoch 1.5 waere komplex
        sd.line([(x, 0), (x, H)], fill=int(238 * max(0.0, 1 - x / 1180) ** 1.5))
    img = Image.composite(Image.new("RGB", (W, H), (2, 10, 13)), img, scrim)

    d = ImageDraw.Draw(img, "RGBA")

    # Eyebrow
    d.rectangle((96, 250, 104, 296), fill=GOLD)
    text(d, (132, 252), "U.S. ARMY · AKTE 1983", font(38, True, True), CYAN, spacing=7)

    # Headline
    f1 = font(196, True)
    text(d, (92, 320), "ZEIT", f1, WHITE)
    w1 = d.textlength("ZEIT", font=f1)
    text(d, (92 + w1, 320), "REISE", f1, GOLD)
    text(d, (92, 522), "PER BEFEHL?", font(112, True), WHITE)

    # Echter Aktenschnipsel als Authentizitaetsanker
    strip = Image.new("RGB", (760, 132), (232, 228, 214))
    sdr = ImageDraw.Draw(strip)
    mono = ImageFont.truetype(F + "consola.ttf", 21) if (Path(F) / "consola.ttf").exists() \
        else font(21)
    sdr.rectangle((22, 20, 738, 62), fill=(250, 236, 186))
    sdr.text((30, 26), "H. Use multi-focus approach to solve problem of", font=mono, fill=(24, 24, 24))
    sdr.text((30, 68), "distortion in terrestrial information gathering", font=mono, fill=(70, 70, 70))
    sdr.text((30, 96), "trips ... one viewing it at Focus 15 ... Focus 21", font=mono, fill=(70, 70, 70))
    img.paste(strip, (96, 700))
    d.rectangle((96, 700, 856, 832), outline=GOLD, width=4)
    text(d, (96, 852), "ORIGINALWORTLAUT AUS DER AKTE", font(26, True, True), (150, 168, 172), spacing=4)

    out_dir = Path(__file__).resolve().parents[1] / "06_PRODUCTION" / "EP02_GATEWAY_V6" / "thumbnail"
    out_dir.mkdir(parents=True, exist_ok=True)
    img = grain(img, 4)
    img.save(out_dir / "EP02_GATEWAY_V6_THUMBNAIL.png", quality=97)
    img.resize((1280, 720), Image.LANCZOS).save(
        out_dir / "EP02_GATEWAY_V6_THUMBNAIL_1280x720.jpg", quality=94)
    # Lesbarkeitsprobe in Listengroesse
    img.resize((246, 138), Image.LANCZOS).save(out_dir / "_probe_246px.png")
    print(f"  Thumbnail  {img.size}  + 1280x720 + 246px-Probe")
    return out_dir / "EP02_GATEWAY_V6_THUMBNAIL.png"


# ------------------------------------------------------- Deutsche Kartensets
# V2/V5 hatten alle Karten auf Englisch. Fuer ein deutsches Publikum ist das
# dieselbe Lesebarriere wie die Originaldokumente. Hier dieselben Inhalte,
# deutsch und mit engerem Satzspiegel (die alten liessen die halbe Flaeche leer).

def list_card(name, eyebrow_txt, title, rows, note="") -> Path:
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, eyebrow_txt)
    text(d, (82, 116), title, font(60, True), WHITE)
    rule(d, 82, 202, 1838)
    y = 262
    for label, desc in rows:
        d.rectangle((82, y + 6, 90, y + 52), fill=GOLD)
        text(d, (118, y), label, font(38, True), CYAN)
        text(d, (118, y + 54), desc, font(32), (196, 206, 208))
        y += 138
    if note:
        d.rounded_rectangle((82, 902, 1838, 992), 6, fill=(8, 26, 30),
                            outline=(30, 58, 64), width=2)
        text(d, (960, 932), note, font(31), WHITE, anchor="ma")
    footer(d, "U.S. Army Gateway Report · 9. Juni 1983")
    return save(img, name)


def german_list_cards():
    list_card("V6_CARD_BINAURAL.png", "Die akustische Grundlage", "BINAURALER BEAT", [
        ("400 HERTZ", "linkes Ohr"),
        ("410 HERTZ", "rechtes Ohr"),
        ("RUND 10 HERTZ", "der wahrgenommene Beat"),
        ("FREQUENZFOLGE-REAKTION", "Hypothese: das Gehirn folgt diesem Rhythmus"),
    ])
    list_card("V6_CARD_WORLD_MODEL.png", "McDonnells theoretischer Rahmen", "DAS WELTMODELL", [
        ("KÖRPER", "Resonanz und Schwingung"),
        ("GEHIRN", "elektrische Muster"),
        ("KOHÄRENZ", "Synchronisierung beider Hälften"),
        ("FELD", "Informationszugang jenseits von Raum und Zeit"),
    ])
    list_card("V6_CARD_FOCUS.png", "Die Gateway-Progression", "DIE FOCUS-STUFEN", [
        ("FOCUS 10", "Geist wach, Körper tief entspannt"),
        ("FOCUS 12", "erweiterte Aufmerksamkeit"),
        ("FOCUS 15", "im Original: „Travel into the Past“"),
        ("FOCUS 21", "im Original: „The Future“"),
    ])
    list_card("V6_CARD_DISTORTION.png", "Warum drei Beobachter?", "DAS VERZERRUNGSPROBLEM", [
        ("GEGENWART", "aktuelle Wahrnehmung"),
        ("VERGANGENHEIT", "Focus 15, Erinnerungsverzerrung"),
        ("ZUKUNFT", "Focus 21, Erwartungsverzerrung"),
        ("VORSCHLAG", "alle drei Berichte vergleichen"),
    ])
    list_card("V6_CARD_PROTOCOL.png", "Was ein Nachweis bräuchte", "TESTPROTOKOLL", [
        ("ZIEL VORHER FESTLEGEN", "vor Beginn der Sitzung"),
        ("BLIND AUSWERTEN", "Gutachter ohne Vorwissen"),
        ("BEWERTUNG FESTZURREN", "Erfolg vorab definieren"),
        ("UNABHÄNGIG WIEDERHOLEN", "zweites Labor, neue Ziele"),
    ])
    list_card("V6_CARD_STATUS.png", "Stand der Belege", "WAS DIE AKTE TRÄGT", [
        ("DOKUMENTIERT", "Stufen, Techniken, Verfahren, Empfehlungen"),
        ("BEHAUPTET", "Bewusstsein außerhalb des Körpers"),
        ("NICHT NACHGEWIESEN", "geprüfte Information aus anderer Zeit"),
        ("DIE LÜCKE", "kleiner Höreffekt, außergewöhnlicher Anspruch"),
    ])
    list_card("V6_CARD_EVIDENCE.png", "Von Wahrnehmung zu Nachweis", "DIE BEWEISLAGE", [
        ("HÖREFFEKT", "moderat und messbar"),
        ("ENTRAINMENT", "widersprüchliche Befunde"),
        ("ZEITINFORMATION", "keine geprüften Daten"),
        ("FERNWAHRNEHMUNG", "außergewöhnlicher Anspruch, gewöhnliche Belege"),
    ])


def people_chain() -> Path:
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, "Wer das Modell gebaut hat")
    text(d, (82, 116), "TRAINING, THEORIE, BEWERTUNG", font(60, True), WHITE)
    rule(d, 82, 202, 1838)
    people = [("ROBERT MONROE", "Trainingssystem", "1915–1995"),
              ("ITZHAK BENTOV", "Analogien und Modell", "1923–1979"),
              ("WAYNE McDONNELL", "Bewertung für die Army", "Lt. Col., 1983")]
    bw, gap = 540, 60
    for i, (nm, role, life) in enumerate(people):
        x = 82 + i * (bw + gap)
        d.rounded_rectangle((x, 300, x + bw, 760), 8, fill=(8, 26, 30),
                            outline=(30, 58, 64), width=2)
        cx = x + bw // 2
        d.ellipse([cx - 52, 366, cx + 52, 470], outline=GOLD, width=3)
        d.line([(cx, 470), (cx, 528)], fill=GOLD, width=3)
        text(d, (cx, 566), nm, font(34, True), WHITE, anchor="ma")
        text(d, (cx, 614), role, font(29), CYAN, anchor="ma")
        text(d, (cx, 660), life, font(27), DIM, anchor="ma")
        if i < 2:
            ax = x + bw + gap // 2
            d.line([(ax - 18, 530), (ax + 10, 530)], fill=(52, 96, 104), width=3)
            tri(d, ax + 20, 530, 11, (52, 96, 104))
    d.rounded_rectangle((82, 852, 1838, 942), 6, fill=(8, 26, 30), outline=(30, 58, 64), width=2)
    text(d, (960, 882), "Der Bericht verbindet alle drei zu einer Kette.",
         font(32), WHITE, anchor="ma")
    footer(d, "U.S. Army Gateway Report · 9. Juni 1983")
    return save(img, "V6_CARD_PEOPLE.png")


def claim_gap() -> Path:
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 78, "Die Logik des Berichts")
    text(d, (82, 116), "WO DER SPRUNG PASSIERT", font(60, True), WHITE)
    rule(d, 82, 202, 1838)

    left = [("ZWEI TÖNE", "Wahrnehmung", CYAN), ("ENTSPANNUNG", "Erfahrung", CYAN),
            ("KOHÄRENZ", "Modell", GOLD)]
    right = [("INFORMATIONSFELD", "Spekulation", (196, 106, 106)),
             ("VERGANGENHEIT / ZUKUNFT", "außergewöhnlich", (196, 106, 106))]

    # Breiten so, dass die rechte Kette innerhalb von 1920 endet
    y = 470
    x = 96
    for label, sub, col in left:
        w = 254
        d.rounded_rectangle((x, y - 62, x + w, y + 62), 8, fill=(8, 26, 30), outline=col, width=3)
        text(d, (x + w / 2, y - 34), label, font(26, True), WHITE, anchor="ma")
        text(d, (x + w / 2, y + 6), sub, font(24), DIM, anchor="ma")
        if label != "KOHÄRENZ":
            d.line([(x + w + 8, y), (x + w + 34, y)], fill=(52, 96, 104), width=3)
            tri(d, x + w + 44, y, 10, (52, 96, 104))
        x += w + 56

    gx = x - 4
    d.line([(gx, 300), (gx, 700)], fill=(196, 106, 106), width=4)
    for yy in range(300, 700, 22):
        d.line([(gx, yy), (gx, yy + 11)], fill=(20, 20, 24), width=4)
    text(d, (gx, 728), "BEWEISLÜCKE", font(30, True), (206, 122, 122), anchor="ma")

    x = gx + 56
    for label, sub, col in right:
        w = 356
        d.rounded_rectangle((x, y - 62, x + w, y + 62), 8, fill=(26, 12, 12), outline=col, width=3)
        text(d, (x + w / 2, y - 34), label, font(25, True), WHITE, anchor="ma")
        text(d, (x + w / 2, y + 6), sub, font(24), (176, 136, 136), anchor="ma")
        x += w + 34

    text(d, (960, 852), "Links steht, was der Bericht beschreibt. Rechts, was er annimmt.",
         font(31), WHITE, anchor="ma")
    footer(d, "U.S. Army Gateway Report · 9. Juni 1983")
    return save(img, "V6_CARD_CLAIMGAP.png")


def german_cards():
    german_list_cards()
    people_chain()
    claim_gap()


# ---------------------------------------------------------------- V7-Karten

def flight191() -> Path:
    """Die Zaesur in Akt 2. Zurueckhaltend — es sind 273 Tote."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 300, "Chicago O'Hare")
    text(d, (82, 344), "25. MAI 1979", font(96, True), WHITE)
    d.line([(82, 486), (600, 486)], fill=GOLD, width=3)
    text(d, (82, 528), "American Airlines Flug 191", font(48), WHITE)
    text(d, (82, 596), "Itzhak Bentov war an Bord.", font(40), CYAN)
    text(d, (82, 664), "Er war auf dem Weg zu einem Vortrag", font(34), DIM)
    text(d, (82, 710), "über seine Arbeit am Bewusstsein.", font(34), DIM)
    footer(d, "Schwerstes Flugunglück auf amerikanischem Boden")
    return save(img, "V6_CARD_FLIGHT191.png")


def five_percent() -> Path:
    """100 Punkte, fünf davon gold. Macht die Zahl körperlich."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 96, "Focus 15 · nach Angaben des Berichts")
    text(d, (82, 136), "WENIGER ALS FÜNF PROZENT", font(58, True), WHITE)
    rule(d, 82, 222, 1838)
    x0, y0, step = 470, 320, 98
    for i in range(100):
        r, c = divmod(i, 10)
        x, y = x0 + c * step, y0 + r * step
        if i < 5:
            d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=GOLD)
            d.ellipse([x - 36, y - 36, x + 36, y + 36], outline=GOLD + (110,), width=2)
        else:
            d.ellipse([x - 19, y - 19, x + 19, y + 19], fill=(28, 52, 58))
    text(d, (960, 1000), "Bei fünfundneunzig passiert nichts. Bei fünf, so die Akte, schon.",
         font(32), WHITE, anchor="ma")
    return save(img, "V6_CARD_FIVE_PERCENT.png")


def comment_card() -> Path:
    """Mid-Roll-CTA. Bewusst binär — das kostet eine Sekunde."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (960, 300), "Glaubst du bis hier", font(64, True), WHITE, anchor="ma")
    text(d, (960, 382), "noch mit?", font(64, True), WHITE, anchor="ma")
    d.rounded_rectangle((470, 540, 900, 700), 10, fill=(10, 34, 30), outline=CYAN, width=3)
    text(d, (685, 590), "JA", font(72, True), CYAN, anchor="ma")
    d.rounded_rectangle((1020, 540, 1450, 700), 10, fill=(30, 14, 14), outline=(196, 106, 106), width=3)
    text(d, (1235, 590), "NEIN", font(72, True), (206, 122, 122), anchor="ma")
    text(d, (960, 780), "Schreib es in die Kommentare.", font(38), DIM, anchor="ma")
    text(d, (960, 852), "Der nächste Teil ist der Grund,", font(34), GOLD, anchor="ma")
    text(d, (960, 898), "warum diese Akte bis heute diskutiert wird.", font(34), GOLD, anchor="ma")
    footer(d, "NOESIS · Modelle des Geistes")
    return save(img, "V6_CARD_COMMENT.png")


def digits_card() -> Path:
    """Zehn Felder, sechs getroffen. Die Form einer Anomalie."""
    img = canvas()
    d = ImageDraw.Draw(img, "RGBA")
    eyebrow(d, 82, 96, "Der Versuch in der Akte")
    text(d, (82, 136), "ZEHN ZIFFERN", font(58, True), WHITE)
    rule(d, 82, 222, 1838)
    x0, y = 200, 470
    treffer = [1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
    for i, ok in enumerate(treffer):
        x = x0 + i * 158
        col = GOLD if ok else (44, 62, 68)
        d.rounded_rectangle((x, y - 78, x + 118, y + 78), 8,
                            fill=(10, 30, 34), outline=col, width=4 if ok else 2)
        if ok:
            d.ellipse([x + 44, y - 16, x + 74, y + 14], fill=GOLD)
        else:
            d.line([(x + 40, y - 20), (x + 78, y + 18)], fill=(70, 88, 94), width=4)
            d.line([(x + 78, y - 20), (x + 40, y + 18)], fill=(70, 88, 94), width=4)
    text(d, (960, 660), "Genug, um den Autor zu beeindrucken.", font(40, True), WHITE, anchor="ma")
    text(d, (960, 726), "Alle zehn bekam niemand.", font(40, True), GOLD, anchor="ma")
    d.rounded_rectangle((82, 860, 1838, 960), 6, fill=(8, 26, 30), outline=(30, 58, 64), width=2)
    text(d, (960, 894), "Schematische Darstellung — die Akte nennt keine genaue Trefferzahl.",
         font(29), DIM, anchor="ma")
    footer(d, "U.S. Army Gateway Report · 9. Juni 1983")
    return save(img, "V6_CARD_DIGITS.png")


def v7_cards():
    flight191()
    five_percent()
    comment_card()
    digits_card()
