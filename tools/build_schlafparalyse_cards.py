#!/usr/bin/env python3
"""Create factual 2K cards, CTAs and endcards for sleep-paralysis EP06-EP08."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
W, H = 2560, 1440
FONT_DIR = Path("C:/Windows/Fonts")
FONT_REGULAR = FONT_DIR / "arial.ttf"
FONT_BOLD = FONT_DIR / "arialbd.ttf"
FONT_SERIF = FONT_DIR / "georgia.ttf"
FONT_SERIF_BOLD = FONT_DIR / "georgiab.ttf"

BG_TOP = (42, 49, 62)
BG_BOTTOM = (19, 27, 39)
PAPER = (238, 231, 211)
WHITE = (248, 246, 239)
MUTED = (179, 190, 199)
GOLD = (224, 168, 83)
CYAN = (91, 204, 207)
VIOLET = (157, 123, 205)
CORAL = (222, 119, 91)
GREEN = (105, 193, 151)
LINE = (93, 111, 132)

EPISODE_DIRS = {
    "EP06": ROOT / "06_PRODUCTION" / "EP06_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT" / "CARDS",
    "EP07": ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT" / "CARDS",
    "EP08": ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT" / "CARDS",
}

EPISODE_LABELS = {
    "EP06": "SCHLAFPARALYSE I",
    "EP07": "SCHLAFPARALYSE II",
    "EP08": "SCHLAFPARALYSE III",
}


def font(size: int, *, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_SERIF_BOLD if serif and bold else FONT_SERIF if serif else FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size)


def background(accent: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (W, H), BG_BOTTOM)
    draw = ImageDraw.Draw(image)
    for y in range(H):
        t = y / (H - 1)
        color = tuple(round(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(3))
        draw.line((0, y, W, y), fill=color)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W * .40, -H * .45, W * 1.15, H * .75), fill=accent + (72,))
    glow = glow.filter(ImageFilter.GaussianBlur(250))
    image = Image.alpha_composite(image.convert("RGBA"), glow)
    texture = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(texture)
    for x in range(-H, W, 96):
        td.line((x, 0, x + H, H), fill=(255, 255, 255, 7), width=1)
    return Image.alpha_composite(image, texture)


def header(draw: ImageDraw.ImageDraw, episode: str, section: str, title: str, subtitle: str = "") -> None:
    # Zuschauerkarte, kein Produktionsboard: keine EP-Codes, Aktkuerzel oder
    # internen Kategorien wie "S4 Harvard" im Bild. Die kleine Serienmarke
    # gibt Orientierung; die eigentliche Aussage beginnt sofort mit dem Titel.
    draw.text((112, 82), f"NOESIS  ·  {EPISODE_LABELS.get(episode, 'SCHLAFPARALYSE')}",
              font=font(28, bold=True), fill=CYAN)
    draw.text((112, 166), title, font=font(72, bold=True, serif=True), fill=WHITE)
    if subtitle:
        draw.text((116, 272), subtitle, font=font(34), fill=MUTED)
    draw.line((112, 360, W - 112, 360), fill=LINE, width=2)


def footer(draw: ImageDraw.ImageDraw, source: str) -> None:
    draw.line((112, H - 102, W - 112, H - 102), fill=(74, 89, 107), width=2)
    draw.text((112, H - 72), source, font=font(22), fill=(146, 160, 174))


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], accent: tuple[int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=34, fill=(31, 40, 53, 225), outline=accent + (225,), width=4)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=fnt) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, fill, max_width: int, spacing: int = 12) -> int:
    x, y = xy
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def flow_card(episode: str, filename: str, section: str, title: str, subtitle: str, nodes: list[tuple[str, str]], source: str, accent=CYAN) -> None:
    image = background(accent)
    draw = ImageDraw.Draw(image, "RGBA")
    header(draw, episode, section, title, subtitle)
    count = len(nodes)
    gap = 42
    total = W - 224
    width = (total - gap * (count - 1)) // count
    y1, y2 = 510, 1118
    for index, (label, desc) in enumerate(nodes):
        x1 = 112 + index * (width + gap)
        x2 = x1 + width
        rounded_panel(draw, (x1, y1, x2, y2), accent if index % 2 == 0 else GOLD)
        draw.ellipse((x1 + 42, y1 + 48, x1 + 104, y1 + 110), fill=(accent if index % 2 == 0 else GOLD) + (255,))
        draw.text((x1 + 135, y1 + 52), f"{index + 1:02d}", font=font(28, bold=True), fill=MUTED)
        draw_wrapped(draw, (x1 + 42, y1 + 160), label, font(43, bold=True), WHITE, width - 84, 10)
        draw_wrapped(draw, (x1 + 42, y1 + 290), desc, font(29), PAPER, width - 84, 12)
        if index < count - 1:
            ax = x2 + gap // 2
            ay = (y1 + y2) // 2
            draw.line((x2 + 8, ay, x2 + gap - 11, ay), fill=GOLD, width=6)
            draw.polygon(((x2 + gap - 11, ay - 14), (x2 + gap - 11, ay + 14), (x2 + gap + 8, ay)), fill=GOLD)
    footer(draw, source)
    save_card(episode, filename, image, title, section, source)


def taxonomy_card(episode: str, filename: str, section: str, title: str, subtitle: str, items: list[tuple[str, str, tuple[int, int, int]]], source: str) -> None:
    image = background(VIOLET)
    draw = ImageDraw.Draw(image, "RGBA")
    header(draw, episode, section, title, subtitle)
    count = len(items)
    gap = 36
    width = (W - 224 - gap * (count - 1)) // count
    for index, (label, desc, color) in enumerate(items):
        x1 = 112 + index * (width + gap)
        rounded_panel(draw, (x1, 500, x1 + width, 1125), color)
        cx = x1 + width // 2
        draw.ellipse((cx - 72, 550, cx + 72, 694), outline=color, width=8)
        draw.line((cx, 574, cx, 670), fill=color, width=7)
        draw.arc((cx - 42, 590, cx + 42, 682), 30, 150, fill=color, width=6)
        draw.text((cx, 760), label, font=font(42, bold=True), fill=WHITE, anchor="ma")
        lines = wrap(draw, desc, font(29), width - 84)
        y = 840
        for line in lines:
            draw.text((cx, y), line, font=font(29), fill=PAPER, anchor="ma")
            y += 46
    footer(draw, source)
    save_card(episode, filename, image, title, section, source)


def compare_card(episode: str, filename: str, section: str, title: str, subtitle: str, left: tuple[str, list[str]], right: tuple[str, list[str]], center: str, source: str) -> None:
    image = background(GOLD)
    draw = ImageDraw.Draw(image, "RGBA")
    header(draw, episode, section, title, subtitle)
    boxes = [(112, 492, 1050, 1125, CYAN), (1510, 492, 2448, 1125, VIOLET)]
    for (x1, y1, x2, y2, color), (label, items) in zip(boxes, (left, right)):
        rounded_panel(draw, (x1, y1, x2, y2), color)
        draw.text(((x1 + x2) // 2, y1 + 86), label, font=font(50, bold=True, serif=True), fill=WHITE, anchor="ma")
        y = y1 + 190
        for item in items:
            draw.ellipse((x1 + 64, y + 10, x1 + 82, y + 28), fill=color)
            y = draw_wrapped(draw, (x1 + 112, y), item, font(31), PAPER, x2 - x1 - 190, 9) + 32
    draw.ellipse((1115, 628, 1445, 958), fill=(40, 48, 61), outline=GOLD, width=7)
    for i, line in enumerate(wrap(draw, center, font(31, bold=True), 250)):
        draw.text((1280, 735 + i * 48), line, font=font(31, bold=True), fill=GOLD, anchor="ma")
    footer(draw, source)
    save_card(episode, filename, image, title, section, source)


def loop_card(episode: str, filename: str, section: str, title: str, subtitle: str, labels: list[str], center: str, source: str) -> None:
    image = background(CYAN)
    draw = ImageDraw.Draw(image, "RGBA")
    header(draw, episode, section, title, subtitle)
    cx, cy, radius = 1280, 800, 370
    points = []
    for index, label in enumerate(labels):
        angle = -math.pi / 2 + index * 2 * math.pi / len(labels)
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        points.append((x, y))
        color = (CYAN, GOLD, VIOLET, CORAL, GREEN)[index % 5]
        draw.ellipse((x - 118, y - 64, x + 118, y + 64), fill=(32, 42, 56), outline=color, width=5)
        for j, line in enumerate(wrap(draw, label, font(28, bold=True), 190)):
            draw.text((x, y - 18 + j * 35), line, font=font(28, bold=True), fill=WHITE, anchor="mm")
    for index, (x1, y1) in enumerate(points):
        x2, y2 = points[(index + 1) % len(points)]
        vx, vy = x2 - x1, y2 - y1
        length = math.hypot(vx, vy)
        sx, sy = x1 + vx / length * 125, y1 + vy / length * 72
        ex, ey = x2 - vx / length * 125, y2 - vy / length * 72
        draw.line((sx, sy, ex, ey), fill=GOLD, width=5)
        draw.ellipse((ex - 7, ey - 7, ex + 7, ey + 7), fill=GOLD)
    draw.ellipse((cx - 185, cy - 185, cx + 185, cy + 185), fill=(27, 36, 50), outline=PAPER, width=4)
    for i, line in enumerate(wrap(draw, center, font(36, bold=True, serif=True), 290)):
        draw.text((cx, cy - 25 + i * 46), line, font=font(36, bold=True, serif=True), fill=PAPER, anchor="mm")
    footer(draw, source)
    save_card(episode, filename, image, title, section, source)


def cta_card(episode: str, filename: str, left: str, right: str, prompt: str) -> None:
    image = background(VIOLET)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((1280, 150), f"NOESIS  ·  {EPISODE_LABELS[episode]}", font=font(28, bold=True), fill=CYAN, anchor="ma")
    draw.text((1280, 300), prompt, font=font(50, serif=True), fill=PAPER, anchor="ma")
    draw.rounded_rectangle((180, 505, 1200, 1080), radius=46, fill=(33, 44, 59), outline=CYAN, width=6)
    draw.rounded_rectangle((1360, 505, 2380, 1080), radius=46, fill=(33, 44, 59), outline=GOLD, width=6)
    draw.text((690, 780), left, font=font(82, bold=True, serif=True), fill=WHITE, anchor="mm")
    draw.text((1870, 780), right, font=font(82, bold=True, serif=True), fill=WHITE, anchor="mm")
    draw.text((1280, 790), "ODER", font=font(26, bold=True), fill=MUTED, anchor="mm")
    draw.text((1280, 1270), "SCHREIB DEINE ANTWORT IN DIE KOMMENTARE", font=font(25, bold=True), fill=(168, 181, 192), anchor="mm")
    save_card(episode, filename, image, f"{left} / {right}", "CTA", "Interaktionskarte")


def endcard(episode: str, filename: str, question: str, handoff: str) -> None:
    image = background(GOLD)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.text((120, 95), "NOESIS", font=font(36, bold=True), fill=CYAN)
    draw.text((120, 148), "MODELLE DES GEISTES", font=font(22, bold=True), fill=MUTED)
    draw.text((120, 295), question, font=font(61, bold=True, serif=True), fill=WHITE)
    draw_wrapped(draw, (124, 405), handoff, font(31), PAPER, 940, 13)
    draw.rounded_rectangle((1390, 230, 2400, 765), radius=38, fill=(26, 35, 49), outline=LINE, width=4)
    draw.text((1895, 485), "NÄCHSTES VIDEO", font=font(32, bold=True), fill=MUTED, anchor="mm")
    draw.rounded_rectangle((1560, 920, 2230, 1190), radius=135, fill=(26, 35, 49), outline=GOLD, width=5)
    draw.text((1895, 1050), "ABONNIEREN", font=font(34, bold=True), fill=WHITE, anchor="mm")
    draw.text((120, 1302), EPISODE_LABELS[episode], font=font(22, bold=True), fill=(145, 160, 176))
    save_card(episode, filename, image, question, "ENDCARD", "THUMBNAIL_ENDCARD_V4.md")


MANIFEST: list[dict[str, str]] = []


def save_card(episode: str, filename: str, image: Image.Image, title: str, card_type: str, source: str) -> None:
    output = EPISODE_DIRS[episode]
    output.mkdir(parents=True, exist_ok=True)
    path = output / filename
    image.convert("RGB").save(path, format="PNG", optimize=True)
    MANIFEST.append({"episode": episode, "filename": filename, "type": card_type, "title": title, "source": source, "resolution": f"{W}x{H}"})
    print(path)


def build_ep06() -> None:
    flow_card("EP06", "CARD001_REM_ATONIE.png", "Körperzustand", "Wach — und trotzdem gelähmt", "Zwei Systeme kehren nicht im selben Moment zurück.", [("BEWUSSTSEIN", "Wachmerkmale kehren zurück."), ("MUSKELHEMMUNG", "Die REM-Atonie bleibt kurz bestehen."), ("WIDERSPRUCH", "Wahrnehmung ist aktiv, Bewegung blockiert.")], "Erklärgrafik · REM-Atonie · keine vollständige Kausalerklärung", CYAN)
    taxonomy_card("EP06", "CARD002_DREI_ERLEBNISFAMILIEN.png", "", "Drei typische Erlebnisse", "Forschende ordnen die Berichte in drei wiederkehrende Gruppen.", [("EINDRINGLING", "Präsenz, Schritte, beobachtet werden", CYAN), ("DRUCK", "Atemnot, Gewicht auf der Brust", CORAL), ("KÖRPERGEFÜHL", "Schweben, Fallen, Außerkörpergefühl", VIOLET)], "Nach J. Allan Cheyne · typische Erlebnisse bei Schlafparalyse")
    flow_card("EP06", "CARD003_TAKEUCHI_1992.png", "", "So wurde Schlafparalyse im Labor beobachtet", "Die Forschenden unterbrachen gezielt den Schlaf.", [("16 PERSONEN", "nahmen am Versuch teil."), ("1 STUNDE WACH", "unterbrach die Nacht."), ("6 EPISODEN", "wurden anschließend dokumentiert.")], "Takeuchi et al. · 1992", GOLD)
    flow_card("EP06", "CARD004_PRAESENZMODELL.png", "Wahrnehmung", "Wie aus Alarm eine Präsenz werden kann", "Ein Modell — keine bewiesene Gesamterklärung.", [("ALARM", "Der Körper meldet Bedrohung."), ("URSACHE FEHLT", "Keine eindeutige Quelle ist sichtbar."), ("SUCHE", "Wahrnehmung gewichtet Schatten und Geräusche."), ("VERURSACHER", "Eine Präsenz wird als Erklärung erlebt.")], "Hypothesenmodell · nicht als Beweis eines äußeren Wesens lesen", VIOLET)
    flow_card("EP06", "CARD005_FOGO_FELDFORSCHUNG.png", "", "Vom Erlebnis zur überprüfbaren Erzählung", "Hufford sammelt Berichte und vergleicht, was Menschen vorher wussten.", [("ERLEBNIS", "Nächtliche Lähmung und Präsenz."), ("GESPRÄCH", "Menschen erzählen ihre Nacht."), ("VERGLEICH", "Berichte mit und ohne Vorwissen.")], "David Hufford · Feldforschung auf Neufundland", GREEN)
    cta_card("EP06", "CARD006_CTA_KOERPER_BESUCHER.png", "KÖRPER", "BESUCHER?", "Was fühlt sich für dich wahrscheinlicher an?")
    endcard("EP06", "CARD007_ENDCARD.png", "GEHIRN ODER MUSTER?", "Nächste Folge: Wer sitzt auf deiner Brust? — Als Schlafparalyse zur Hexe wurde.")
    flow_card("EP06", "CARD008_HUFFORD_1963_1982.png", "Forschungsweg", "Eine Nacht wird zur Forschungsfrage", "Ein persönliches Erlebnis wird nicht zum Beweis, sondern zum Ausgangspunkt systematischer Feldforschung.", [("1963", "eigenes Erlebnis"), ("BEFRAGUNGEN", "Berichte sammeln und vergleichen"), ("1982", "The Terror That Comes in the Night")], "David J. Hufford · autobiografischer Bericht / Buchpublikation", GREEN)
    flow_card("EP06", "CARD009_WAKE_REM_OVERLAP.png", "Mischzustand", "Wachheit kommt zurück", "Bewusstsein und Muskeltonus wechseln nicht zwingend im selben Augenblick.", [("BEWUSSTSEIN", "wach"), ("MUSKELTONUS", "noch gehemmt"), ("ÜBERLAPPUNG", "Sekunden bis Minuten")], "Erklärgrafik · REM-Atonie", CYAN)
    flow_card("EP06", "CARD010_TAKEUCHI_PROTOCOL.png", "Versuchsablauf", "Schlaf · eine Stunde wach · zurück ins Bett", "Der Ablauf verschiebt Schlafbeginn und REM gegeneinander — er garantiert keine Episode.", [("SCHLAF", "erste Schlafphase"), ("WACH", "eine Stunde Unterbrechung"), ("RÜCKKEHR", "erneuter Schlafbeginn")], "Takeuchi et al. · SLEEP 15(3) · 1992", GOLD)
    flow_card("EP06", "CARD011_SIX_EPISODES.png", "", "Sechs Episoden nach unterbrochenem Schlaf", "Nicht bei allen — aber klar dokumentiert.", [("16 PERSONEN", "nahmen am Versuch teil."), ("SCHLAF UNTERBROCHEN", "eine Stunde wach, dann zurück ins Bett."), ("6 EPISODEN", "isolierte Schlafparalyse.")], "Takeuchi et al. · 1992", GOLD)
    compare_card("EP06", "CARD012_REALNESS_AND_CAUSE.png", "Offene Frage", "Beantwortet — und offen", "Die Mechanik erklärt die Lähmung. Die Gestalt erklärt sie nicht.", ("BEANTWORTET", ["Warum Bewegung blockiert ist.", "Wann REM und Wachheit sich überlappen.", "Warum der Zustand messbar ist."]), ("OFFEN", ["Warum Wehrlosigkeit eine Anwesenheit formt.", "Warum ein Verursacher zuerst gehört wird.", "Warum er absichtsvoll wirkt."]), "beides gilt", "Stand der Erklärung · kein Beweis eines äußeren Wesens")
    flow_card("EP06", "CARD013_OPEN_PRESENCE_QUESTION.png", "", "Warum wird aus Lähmung eine Begegnung?", "Der Körper erklärt die Starre — aber noch nicht die Gestalt.", [("LÄHMUNG", "Der körperliche Zustand ist gut erklärt."), ("PRÄSENZ", "Warum daraus ein Gegenüber wird, bleibt offen."), ("NAMEN", "Old Hag, Mara, Incubus, Hexe.")], "Die Namen sind kulturelle Deutungen, keine belegten Wesen", VIOLET)
    flow_card("EP06", "CARD014_PRIVATE_NIGHT_PUBLIC_RECORD.png", "Salem 1692", "Wenn die Nacht aktenkundig wird", "Aus einer Schilderung im Bett wird ein Verfahren.", [("NACHT", "Ein Mann liegt wach und kann sich nicht bewegen."), ("NAME", "Er nennt Bridget Bishop."), ("ANKLAGE", "Das Erlebnis wird Teil einer Hexereianklage."), ("URTEIL", "Wenige Tage später fällt es.")], "Prozessakten von Salem · Übergang zur nächsten Folge", GOLD)


def build_ep07() -> None:
    taxonomy_card("EP07", "CARD001_VIELE_NAMEN.png", "", "Viele Namen für dieselbe Nacht", "Ähnliche Erlebnisse bekommen je nach Kultur andere Gestalten.", [("MAHR / MARA", "europäische Nachtwesen", CYAN), ("INCUBUS", "Druck und Angriff", CORAL), ("KANASHIBARI", "der gebundene Körper", VIOLET), ("JINN / OLD HAG", "regional geprägte Deutungen", GOLD)], "Ähnliche Motive müssen nicht voneinander abstammen")
    flow_card("EP07", "CARD002_PRIVATNACHT_GERICHT.png", "", "Wie eine private Nacht öffentlich wird", "Aus einer persönlichen Schilderung wird ein öffentlicher Vorwurf.", [("NACHT", "Lähmung, Druck, Präsenz."), ("AUSSAGE", "Das Erlebnis bekommt Worte und einen Namen."), ("GERICHT", "Die Deutung wird Teil der Anklage."), ("FOLGE", "Angst erhält öffentliche Macht.")], "Salem 1692 · historischer Kontext")
    flow_card("EP07", "CARD003_HUFFORD_INVERSION.png", "", "Das Erlebnis kann vor der Geschichte kommen", "Hufford findet ähnliche Berichte auch ohne bekanntes Vorbild.", [("ERLEBNIS", "Eine körperlich konkrete Nacht."), ("OHNE VORWISSEN", "Die lokale Geschichte war nicht bekannt."), ("ERZÄHLUNG", "Kultur gibt Form, Name und Bedeutung."), ("RÜCKWIRKUNG", "Deutung verändert Angst und Erwartung.")], "David Hufford · Feldforschung, keine Entwarnung für den Einfluss von Kultur", GREEN)
    compare_card("EP07", "CARD004_AEGYPTEN_DAENEMARK.png", "", "Gleicher Zustand — andere Erklärung", "Die Schlafparalyse ist ähnlich. Angst und Deutung unterscheiden sich.", ("ÄGYPTEN", ["häufiger als Angriff durch ein Wesen gedeutet", "Jinn als vertrauter Erklärungsrahmen", "stärkere Angst in den Berichten"]), ("DÄNEMARK", ["eher körperlich erklärt", "weniger übernatürliche Bedrohung", "geringere Angst in den Berichten"]), "DIESELBE KÖRPERLICHE STÖRUNG", "Jalal, Hinton et al. · Vergleich Ägypten / Dänemark")
    loop_card("EP07", "CARD005_FEEDBACK_LOOP.png", "", "Wenn eine Erzählung körperlich wird", "Kultur erzeugt die Lähmung nicht — kann die nächste Nacht aber mitprägen.", ["ERLEBNIS", "DEUTUNG", "ANGST", "SCHLECHTER SCHLAF"], "DER KREIS VERSTÄRKT SICH", "Erklärmodell · mögliche Rückkopplung, kein Automatismus")
    cta_card("EP07", "CARD006_CTA_ERFAHRUNG_KULTUR.png", "ERFAHRUNG", "KULTUR?", "Was kommt zuerst — und was wirkt zurück?")
    endcard("EP07", "CARD007_ENDCARD.png", "ERLEBNIS ODER ERZÄHLUNG?", "Nächste Folge: Der Mann mit dem Hut — wie das Internet einer Halluzination ein Gesicht gibt.")


def build_ep08() -> None:
    flow_card("EP08", "CARD001_4500_NACHRICHTEN.png", "", "Mehr als 4.500 Reaktionen", "Eine Radiosendung bündelt Tausende ähnliche Schilderungen.", [("SENDUNG", "Shadow People werden zum Thema."), ("REAKTION", "Das Archiv nennt über 4.500 E-Mails."), ("MUSTER", "Viele Beschreibungen ähneln sich."), ("NAME", "Das gemeinsame Bild wird fester.")], "Coast to Coast AM · Archivangabe vom 12. April 2001", GOLD)
    compare_card("EP08", "CARD002_INTRUDER_OVERLAP.png", "Überlappung", "Shadow People und Intruder-Erlebnisse", "Ähnlichkeit ist keine vollständige Gleichsetzung.", ("INTRUDER", ["Lähmung", "Präsenzgefühl", "Schritte oder Bewegung", "Figur im Randsehen"]), ("SHADOW PEOPLE", ["dunkle menschliche Kontur", "Tür- und Flurmotive", "gemeinsamer Name", "medial verbreitetes Bild"]), "ÜBER- LAPPUNG", "Vergleichsgrafik · keine Identitätsbehauptung")
    compare_card("EP08", "CARD003_ABDUCTION_OVERLAP.png", "", "Warum manche Berichte ähnlich klingen", "Einige Bausteine überschneiden sich — aber nicht jeder Entführungsbericht ist Schlafparalyse.", ("SCHLAFPARALYSE", ["Bewegung blockiert", "eine Präsenz im Raum", "Druck oder Berührung", "Licht und verändertes Körpergefühl"]), ("ENTFÜHRUNGSBERICHT", ["ein Wesen oder Handelnder", "ein anderer Ort", "spätere Befragung", "vertraute Bilder aus der Kultur"]), "GEMEINSAME BAUSTEINE", "Ein möglicher Zusammenhang, keine Gesamterklärung")
    flow_card("EP08", "CARD004_MEMORY_RECONSTRUCTION.png", "Gedächtnis", "Erinnerung ist keine unveränderte Aufnahme", "Spätere Informationen können eine Erfahrung neu ordnen.", [("ERLEBNIS", "Mehrdeutig, körperlich, fragmentarisch."), ("BEFRAGUNG", "Fragen setzen neue Schwerpunkte."), ("POPKULTUR", "Bilder und Namen werden verfügbar."), ("REKONSTRUKTION", "Die Erinnerung erhält eine stabilere Form.")], "Gedächtnismodell · keine pauschale Aussage über einzelne Berichte", VIOLET)
    loop_card("EP08", "CARD005_INTERNET_FEEDBACK.png", "", "Das vernetzte Nachtwesen", "Ein Bild reist schneller als die Erfahrung, die es erklären soll.", ["ERFAHRUNG", "POST", "BILD / NAME", "ERWARTUNG", "NÄCHSTE NACHT"], "EIN GEMEINSAMES BILD", "So können Verbreitung und Erwartung einander verstärken")
    loop_card("EP08", "CARD006_FINAL_LOOP.png", "", "Vier Ebenen — ein Erlebnis", "Keine Ebene erklärt allein, warum die Nacht eine Gestalt bekommt.", ["GEHIRN", "ERFAHRUNG", "GESCHICHTE", "ERWARTUNG"], "SCHLAF- PARALYSE", "Was die drei Folgen zusammenführen")
    cta_card("EP08", "CARD007_CTA_MUSTER_MEME.png", "MUSTER", "MEME?", "Entdecken wir eine Form — oder lernen wir sie?")
    endcard("EP08", "CARD008_ENDCARD.png", "ETWAS DRAUSSEN — ODER IN UNS?", "NOESIS — Modelle des Geistes. Die offene Frage bleibt bewusst offen.")


def write_manifests() -> None:
    for episode, output in EPISODE_DIRS.items():
        rows = [row for row in MANIFEST if row["episode"] == episode]
        with (output / "CARDS_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["episode", "filename", "type", "title", "source", "resolution"])
            writer.writeheader()
            writer.writerows(rows)


def write_contact_sheets() -> None:
    for output in EPISODE_DIRS.values():
        paths = sorted(output.glob("CARD*.png"))
        columns = 4
        rows = math.ceil(len(paths) / columns)
        sheet = Image.new("RGB", (columns * 640, rows * 360), (20, 26, 37))
        for index, path in enumerate(paths):
            with Image.open(path) as source:
                tile = source.convert("RGB").resize((640, 360), Image.Resampling.LANCZOS)
            sheet.paste(tile, ((index % columns) * 640, (index // columns) * 360))
        sheet.save(output / "CARDS_CONTACT_SHEET.jpg", quality=90, optimize=True)


def main() -> int:
    build_ep06()
    build_ep07()
    build_ep08()
    write_manifests()
    write_contact_sheets()
    print(f"Created {len(MANIFEST)} cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
