#!/usr/bin/env python3
"""Build 2K V5 motion-graphic keyframes for the EP04A/EP04B series.

These are timing-independent end-state/base frames. Animation durations remain
voice-anchored and are intentionally assigned only after voice generation.
"""

from __future__ import annotations

import math
import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1"
REFS = [SERIES / "REFERENCES_EP04AB", SERIES / "REFERENCES_EP05"]
RAW = SERIES / "00_RAW_VERTEX"
OUT = SERIES / "MOTION_BASES_2K"

W, H = 2560, 1440
BG = (12, 16, 23)
PANEL = (26, 32, 42)
PAPER = (231, 226, 213)
WHITE = (244, 243, 238)
MUTED = (151, 160, 173)
CYAN = (94, 200, 214)
CYAN_D = (42, 105, 119)
RED = (173, 57, 54)
GOLD = (202, 159, 82)
LINE = (58, 67, 82)
SPECTRUM = [(210, 50, 46), (238, 126, 31), (243, 195, 54), (67, 171, 87), (58, 141, 207), (77, 80, 178), (150, 71, 183)]
FONT_DIR = Path(r"C:\Windows\Fonts")

VIEWER_COPY = {
    "A-G02": ("Jungs Warnung", "1932 beschreibt Jung Kundalini als psychisch wirkungsvoll – und nicht als harmloses Wissen."),
    "A-G03": ("Zwischen innerem Bild und Weltgeschichte", "Jungs Flutbild von 1913 wird erst durch die Ereignisse von 1914 neu gelesen."),
    "A-G04": ("Zwei Ebenen, keine einfache Ursache", "Ein inneres Bild kann an äußere Ereignisse erinnern, ohne sie vorherzusagen."),
    "A-G06": ("Die historische Chakra-Quelle", "Wir zeigen die überlieferte Darstellung selbst – nicht eine moderne Neuzeichnung."),
    "A-G07": ("Vom Affekt zum Abstand", "Erst Halt finden, dann das Gefühl erkennen, schließlich etwas Abstand gewinnen."),
    "A-G08": ("Ein Satz verändert die Perspektive", "Aus „Ich bin Wut“ wird „Da ist Wut“ – das Gefühl bleibt, aber es ist nicht mehr alles."),
    "A-G10": ("Karte oder Spiegel?", "Zeigt das Bild eine feste innere Ordnung – oder hilft es, Erfahrung zu lesen?"),
    "A-G11": ("1919 ist nicht 1924", "Die Erstausgabe ist belegt; die gezeigte historische Platte stammt aus einer Ausgabe von 1924."),
    "A-G12": ("Sechs Zentren – Sahasrara darüber", "Die historische Quelle zählt sechs Zentren und behandelt Sahasrara gesondert darüber."),
    "A-G13": ("Wie eine Karte reist", "Südasiatische Lehren werden in London veröffentlicht und später in Zürich neu gedeutet."),
    "A-G14": ("Der nächste Gesprächspartner", "Mit Wolfgang Pauli verschiebt sich Jungs Frage von Symbolen zur Physik."),
    "B-G01": ("Die vertraute Karte ist das Ergebnis", "Nimmt man Farbe und feste Reihenfolge zurück, erscheinen ältere Darstellungen mit anderer Ordnung."),
    "B-G02": ("Nicht eine Karte, sondern viele", "Historische Darstellungen unterscheiden sich in Zahl, Form und Anordnung."),
    "B-G03": ("Sechs – und Sahasrara darüber", "Die klassische Quelle zählt anders als das heutige Siebenermodell."),
    "B-G04": ("Sechs Zentren – und eines darüber", "Ob Sahasrara mitgezählt wird, verändert die vertraute Zahl."),
    "B-G05": ("1919 und 1924", "Publikationsgeschichte und erhaltenes Bildmaterial sind nicht dasselbe."),
    "B-G06": ("Ein Netzwerk hinter dem Namen", "John Woodroffe veröffentlichte als Arthur Avalon und arbeitete mit indischen Gelehrten."),
    "B-G07": ("Von Kalkutta nach London", "Lehre, Übersetzung und Druck bewegen sich durch koloniale Verlagswege."),
    "B-G08": ("Wer spricht mit Autorität?", "Erst verweist der Text auf Überlieferung; später tritt persönliche Schau in den Vordergrund."),
    "B-G09": ("Leadbeater gibt den Zentren Farbe", "Seine Bilder von 1927 prägen Formen und Farberwartungen der Moderne."),
    "B-G10": ("Die heutige Karte wächst in Schichten", "Jede Zeit fügt Zahl, Farbe, Körperbild oder Deutung hinzu."),
    "B-G11": ("Das Spektrum ordnet sieben Farben", "Die Regenbogenfolge macht aus verschiedenen Zentren ein geschlossenes modernes System."),
    "B-G12": ("Was später dazukommt", "Farbmodelle, Körperbilder, Psychologie und Gesundheitsratgeber legen neue Bedeutungen darüber."),
    "B-G13": ("Die Karte wandert in den Alltag", "Yoga, Büro, Therapie und Apps verwenden dasselbe Bild für unterschiedliche Zwecke."),
    "B-G14": ("Jung fügt eine psychologische Lesart hinzu", "1932 liest er die Zentren als Stationen innerer Entwicklung."),
    "B-G15": ("Die Nähte bleiben sichtbar", "Von vorn wirkt die Karte selbstverständlich; von der Seite erkennt man ihre historischen Schichten."),
}


def font(size: int, bold: bool = False, narrow: bool = False) -> ImageFont.FreeTypeFont:
    name = "ARIALNB.TTF" if (bold and narrow) else "ARIALN.TTF" if narrow else "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def canvas() -> Image.Image:
    # Warm, lightly imperfect editorial surface instead of a dashboard/HUD field.
    base = Image.new("RGB", (W, H), (22, 24, 27))
    noise = Image.effect_noise((W, H), 18).convert("L").filter(ImageFilter.GaussianBlur(0.45))
    paper = ImageOps.colorize(noise, (12, 14, 17), (40, 39, 36))
    return Image.blend(base, paper, 0.24)


def header(draw: ImageDraw.ImageDraw, code: str, title: str, subtitle: str = "") -> None:
    # The code and production subtitle belong in the edit manifest, never in the viewer-facing frame.
    title, explanation = VIEWER_COPY.get(code, (title.title(), ""))
    size = 58 if len(title) < 38 else 48
    display = ImageFont.truetype(str(FONT_DIR / "georgiab.ttf"), size)
    body = ImageFont.truetype(str(FONT_DIR / "georgia.ttf"), 31)
    draw.text((132, 82), title, font=display, fill=PAPER)
    if explanation:
        lines = textwrap.wrap(explanation, width=92)
        draw.multiline_text((134, 158), "\n".join(lines), font=body, fill=(184, 181, 171), spacing=8)
    draw.line((132, 252, W - 132, 252), fill=(72, 69, 62), width=2)


def footer(draw: ImageDraw.ImageDraw, text: str = "MOTION-BASIS · TIMING NACH VOICE") -> None:
    # Production notes live in the filename/sequence board, not in the artwork.
    return None


def save(image: Image.Image, episode: str, code: str, slug: str) -> Path:
    folder = OUT / episode
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{code}_{slug}.png"
    image.save(path, quality=95)
    print(path.relative_to(ROOT))
    return path


def remove_obsolete(episode: str, filenames: list[str]) -> None:
    folder = OUT / episode
    for filename in filenames:
        path = folder / filename
        if path.is_file():
            path.unlink()


def resolve(name: str) -> Path:
    hits = []
    for root in REFS:
        if root.exists():
            hits.extend(path for path in root.rglob(name) if path.is_file())
    if not hits:
        raise FileNotFoundError(name)
    return hits[0]


def generated(episode: str, prefix: str) -> Path:
    hits = list((RAW / episode).rglob(f"{episode}_{prefix}_*.png"))
    if not hits:
        raise FileNotFoundError(f"generated {episode}_{prefix}")
    return hits[0]


def fit_source(path: Path, box: tuple[int, int, int, int], background=PAPER) -> Image.Image:
    x0, y0, x1, y1 = box
    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source).convert("RGB")
        fitted = ImageOps.contain(source, (x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    panel = Image.new("RGB", (x1 - x0, y1 - y0), background)
    panel.paste(fitted, ((panel.width - fitted.width) // 2, (panel.height - fitted.height) // 2))
    return panel


def source_card(image: Image.Image, path: Path, box: tuple[int, int, int, int], label: str) -> None:
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, 12, fill=(238, 234, 223), outline=(92, 83, 70), width=3)
    inner = (x0 + 18, y0 + 18, x1 - 18, y1 - 78)
    image.paste(fit_source(path, inner), (inner[0], inner[1]))
    draw.text((x0 + 24, y1 - 60), label, font=font(22, True, True), fill=(52, 47, 42))


def center_text(draw: ImageDraw.ImageDraw, text: str, y: int, size: int = 96, color=WHITE) -> None:
    bbox = draw.textbbox((0, 0), text, font=font(size, True))
    draw.text(((W - (bbox[2] - bbox[0])) / 2, y), text, font=font(size, True), fill=color)


def card(code: str, episode: str, title: str, lines: list[str], slug: str, subtitle: str = "") -> None:
    image = canvas()
    draw = ImageDraw.Draw(image)
    header(draw, code, title, subtitle)
    y = 420
    for index, line in enumerate(lines):
        color = CYAN if index == len(lines) - 1 else WHITE
        center_text(draw, line, y, 88 if len(line) < 24 else 66, color)
        y += 132
    footer(draw)
    save(image, episode, code, slug)


def build_ep04a() -> None:
    episode = "EP04A"
    remove_obsolete(
        episode,
        [
            "A-G08_ICH_BIN_WUT.png",
            "A-G08_ICH_BIN_DA_IST.png",
            "A-G08_DA_IST_WUT.png",
        ],
    )

    image = Image.open(generated(episode, "IMG001")).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((100, 88, 620, 258), 12, fill=(10, 15, 22, 220), outline=CYAN_D, width=3)
    draw.text((132, 118), "ZÜRICH", font=font(35, True, True), fill=CYAN)
    draw.text((132, 164), "1932", font=font(66, True), fill=WHITE)
    save(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"), episode, "A-G01", "ZUERICH_1932")

    card("A-G02", episode, "JUNGS SEMINAR", ["ZÜRICH · 1932", "SINNGEMÄSS NACH DEM SEMINARBAND"], "WARNUNG_PARAPHRASE")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G03", "REALITÄTSSCHNITT", "Subjektive Flut verschwindet · reale Karte übernimmt")
    source_card(image, resolve("EP04A_Europe_1914_Shepherd_PD.jpg"), (1040, 330, 2360, 1280), "EUROPA · 1914 · HISTORISCHE KARTE")
    draw.text((180, 510), "1913", font=font(126, True), fill=MUTED); draw.line((200, 710, 820, 710), fill=RED, width=12)
    draw.text((180, 780), "1914", font=font(154, True), fill=WHITE); footer(draw, "KEIN PROPHEZEIUNGSBELEG · REALITÄTSSCHNITT")
    save(image, episode, "A-G03", "1913_1914_REALITAET")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G04", "ZWEI FELDER", "Keine Kausalbehauptung")
    draw.rounded_rectangle((160, 390, 1130, 1180), 18, fill=(29, 40, 53), outline=CYAN_D, width=4)
    draw.rounded_rectangle((1430, 390, 2400, 1180), 18, fill=(42, 35, 34), outline=(112, 79, 64), width=4)
    center_text(draw, "?", 630, 170, GOLD)
    draw.text((430, 700), "INNERES", font=font(76, True), fill=CYAN)
    draw.text((1680, 700), "ÄUSSERES", font=font(76, True), fill=PAPER); footer(draw)
    save(image, episode, "A-G04", "INNERES_AEUSSERES")

    image = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((128, H - 190, 606, H - 102), 10, fill=(10, 15, 22, 220), outline=(118, 132, 149, 220), width=2)
    draw.text((162, H - 167), "REKONSTRUKTION", font=font(32, True, True), fill=WHITE)
    save(image, episode, "A-G05", "REKONSTRUKTION_LABEL")

    image = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((128, H - 190, 606, H - 102), 10, fill=(10, 15, 22, 220), outline=(118, 132, 149, 220), width=2)
    draw.text((162, H - 167), "OFFENE PARALLELE", font=font(30, True, True), fill=WHITE)
    save(image, episode, "A-G05", "OFFENE_PARALLELE_LABEL")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G06", "HISTORISCHE QUELLE", "Detailfahrt von unten nach oben")
    source_card(image, resolve("SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg"), (530, 320, 2030, 1310), "THE SERPENT POWER · WELLCOME · CC BY 4.0")
    footer(draw, "ORIGINALPROPORTIONEN ERHALTEN · NICHT KI-NEUZEICHNEN")
    save(image, episode, "A-G06", "HISTORISCHE_CHAKRA_QUELLE")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G07", "", "")
    labels = [("Halt finden", (520, 920), PAPER), ("Gefühl erkennen", (1270, 690), RED), ("Abstand gewinnen", (2020, 500), CYAN)]
    curve = [(390, 980), (760, 900), (1040, 760), (1370, 690), (1660, 620), (2150, 520)]
    draw.line(curve, fill=(111, 106, 96), width=5, joint="curve")
    for label, (x, y), color in labels:
        draw.ellipse((x - 34, y - 34, x + 34, y + 34), fill=color)
        bbox = draw.textbbox((0, 0), label, font=font(39, True))
        draw.text((x - (bbox[2] - bbox[0]) / 2, y + 72), label, font=font(39, True), fill=PAPER)
    footer(draw)
    save(image, episode, "A-G07", "BODEN_AFFEKT_ABSTAND")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G08", "", "")
    center_text(draw, "ICH BIN", 570, 92, PAPER); center_text(draw, "WUT", 720, 150, RED)
    save(image, episode, "A-G08", "01_ICH_BIN_WUT")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G08", "", "")
    draw.text((500, 650), "ICH BIN", font=font(82, True), fill=(111, 106, 100))
    draw.line((930, 715, 1450, 715), fill=(103, 99, 92), width=3)
    draw.text((1540, 620), "WUT", font=font(140, True), fill=(191, 83, 76))
    save(image, episode, "A-G08", "02_ABSTAND_ENTSTEHT")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G08", "", "")
    draw.text((560, 620), "DA IST", font=font(92, True), fill=PAPER)
    draw.text((1580, 610), "WUT", font=font(144, True), fill=CYAN)
    save(image, episode, "A-G08", "03_DA_IST_WUT")

    image = Image.open(generated(episode, "IMG037")).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    save(image, episode, "A-G09", "ZWEI_SEKUNDEN_STILL")

    card("A-G10", episode, "KURZE FRAGE", ["KARTE   |   SPIEGEL"], "KARTE_SPIEGEL", "Beide Antworten gleich gewichtet")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G11", "DAS BUCH IST ÄLTER ALS DIESE ABBILDUNG", "Das Buch erschien 1919; die hier gezeigte Ausgabe stammt von 1924.")
    draw.rounded_rectangle((130, 360, 1050, 1180), 18, fill=PAPER, outline=(106, 93, 73), width=4)
    draw.text((230, 500), "THE SERPENT POWER", font=font(54, True), fill=(42, 37, 31)); draw.text((230, 620), "ARTHUR AVALON", font=font(38, True), fill=(70, 62, 51))
    draw.text((230, 795), "ERSTAUSGABE", font=font(30, True, True), fill=(96, 80, 65)); draw.text((230, 850), "1919", font=font(126, True), fill=RED)
    source_card(image, resolve("SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg"), (1280, 360, 2360, 1180), "GEZEIGTE ABBILDUNG · AUSGABE 1924")
    footer(draw, "BUCH: 1919 · GEZEIGTE AUSGABE: 1924")
    save(image, episode, "A-G11", "1919_1924_QUELLENDISZIPLIN")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G12", "DIE ZAHL IM QUELLENTEXT", "+ Sahasrara darüber")
    source_card(image, resolve("EP04B_Yogin_six_chakras_late18c_PD.jpg"), (220, 330, 980, 1280), "HISTORISCHE DARSTELLUNG MIT SECHS ZENTREN")
    draw.text((1400, 500), "SECHS", font=font(156, True), fill=CYAN); draw.text((1430, 730), "+ SAHASRARA", font=font(48, True), fill=PAPER); draw.text((1430, 800), "DARÜBER", font=font(48, True), fill=PAPER)
    footer(draw)
    save(image, episode, "A-G12", "SECHS_SAHASRARA")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G13", "DIE KARTE REIST", "Quellenlagen bleiben getrennt")
    points = [(420, 970, "SÜDASIEN"), (1280, 540, "LONDON"), (2110, 760, "ZÜRICH")]
    for i in range(len(points)-1):
        x1,y1,_=points[i];x2,y2,_=points[i+1]
        for step in range(36):
            t=step/35; x=x1+(x2-x1)*t; y=y1+(y2-y1)*t-math.sin(math.pi*t)*110
            draw.ellipse((x-4,y-4,x+4,y+4),fill=CYAN_D)
    for x,y,label in points:
        draw.ellipse((x-16,y-16,x+16,y+16),fill=CYAN); bbox=draw.textbbox((0,0),label,font=font(32,True,True)); draw.text((x-(bbox[2]-bbox[0])/2,y+38),label,font=font(32,True,True),fill=WHITE)
    footer(draw, "ORIENTIERUNG · KEIN KAUSALER BEWEISPFAD")
    save(image, episode, "A-G13", "KARTE_REIST")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "A-G14", "NÄCHSTER KNOTEN", "Authentischer Archivanker · keine Quantenpartikel")
    source_card(image, resolve("SRC01_Wolfgang_Pauli_1924.jpg"), (260, 330, 1180, 1280), "WOLFGANG PAULI · 1924")
    draw.text((1430, 590), "WOLFGANG PAULI", font=font(62, True), fill=WHITE); draw.text((1430, 710), "PHYSIKER", font=font(94, True), fill=CYAN); draw.text((1430, 875), "DAS NÄCHSTE", font=font(38, True, True), fill=MUTED); draw.text((1430, 930), "PROBLEM", font=font(86, True), fill=RED)
    footer(draw)
    save(image, episode, "A-G14", "PAULI_HANDOFF")


def build_ep04b() -> None:
    episode = "EP04B"
    remove_obsolete(
        episode,
        [
            "B-G01_MODERNE_KARTE_REVERSE.png",
            "B-G15_FINAL_SEAMS.png",
        ],
    )

    modern_full = Image.open(generated(episode, "IMG001")).convert("RGB")
    modern = ImageOps.fit(modern_full, (1360, 940), Image.Resampling.LANCZOS)

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "B-G01", "", "")
    image.paste(modern, (600, 360)); draw.text((700, 1240), "Die heute vertraute Siebenerkarte", font=font(34), fill=(190, 184, 172))
    save(image, episode, "B-G01", "01_MODERNE_KARTE")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "B-G01", "", "")
    faded = ImageEnhance.Color(modern).enhance(0.08); faded = ImageEnhance.Contrast(faded).enhance(0.84)
    image.paste(faded, (600, 360)); draw.text((865, 1240), "Die Farbe verschwindet", font=font(34), fill=(190, 184, 172))
    save(image, episode, "B-G01", "02_FARBE_VERSCHWINDET")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "B-G01", "", "")
    for i in range(7):
        y = 1090 - i * 115; x = 1190 + (-1 if i % 2 else 1) * (35 + i * 12)
        draw.ellipse((x - 42, y - 42, x + 42, y + 42), fill=(126, 121, 112), outline=(205, 198, 184), width=2)
    draw.text((870, 1240), "Die feste Ordnung lockert sich", font=font(34), fill=(190, 184, 172))
    save(image, episode, "B-G01", "03_ORDNUNG_LOCKERT_SICH")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "B-G01", "", "")
    source_card(image, resolve("EP04B_Yogin_six_chakras_late18c_PD.jpg"), (760, 340, 1800, 1260), "Spätes 18. Jahrhundert · historische Quelle")
    save(image, episode, "B-G01", "04_HISTORISCHE_QUELLE")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw, "B-G02", "VIELE KARTEN", "Originalproportionen bleiben erhalten")
    sources=[("EP04B_Yogin_six_chakras_late18c_PD.jpg","SPÄTES 18. JH."),("EP04B_Sapta_Chakra_1899_PD.jpg","1899"),("SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg","SERPENT POWER"),("EP04B_Leadbeater_7_Chakras_Combined_1927_PD.jpg","1927")]
    for i,(name,label) in enumerate(sources): source_card(image,resolve(name),(90+i*620,340,650+i*620,1250),label)
    footer(draw)
    save(image, episode, "B-G02", "VIELE_KARTEN")

    card("B-G03", episode, "ṢAṬ-CAKRA-NIRŪPAṆA", ["SECHS", "+ SAHASRARA DARÜBER"], "SECHS", "Moderne Erläuterung · keine antike Grafik")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw,"B-G04","SECHS + DARÜBER","Zählen ist bereits Interpretation")
    for i in range(6):
        y=1130-i*130; draw.ellipse((1130,y-42,1214,y+42),fill=CYAN_D); draw.text((1280,y-28),str(i+1),font=font(28,True),fill=MUTED)
    draw.line((1172,360,1172,1110),fill=LINE,width=6); draw.ellipse((1090,280,1254,444),outline=GOLD,width=8); draw.text((1340,320),"SAHASRARA",font=font(46,True),fill=GOLD); draw.text((1340,385),"GETRENNT DARÜBER",font=font(28,True,True),fill=MUTED)
    footer(draw)
    save(image,episode,"B-G04","SECHS_PLUS_DARUEBER")

    image = canvas(); draw = ImageDraw.Draw(image); header(draw,"B-G05","DAS BUCH IST ÄLTER ALS DIESE ABBILDUNG","Das Buch erschien 1919; die hier gezeigte Ausgabe stammt von 1924.")
    draw.rounded_rectangle((180,360,1080,1180),18,fill=PAPER,outline=(102,87,69),width=4); draw.text((270,520),"ERSTAUSGABE",font=font(34,True,True),fill=(80,68,55)); draw.text((270,600),"1919",font=font(150,True),fill=RED); draw.text((270,820),"ARTHUR AVALON",font=font(46,True),fill=(45,40,34))
    source_card(image,resolve("SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg"),(1340,360,2360,1180),"GEZEIGTE ABBILDUNG · AUSGABE 1924")
    footer(draw,"BUCH: 1919 · GEZEIGTE AUSGABE: 1924")
    save(image,episode,"B-G05","1919_1924")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G06","","")
    def name_slip(x: int, y: int, label: str, angle: int = 0) -> None:
        piece=Image.new("RGBA",(650,150),(229,223,207,245));pd=ImageDraw.Draw(piece);bbox=pd.textbbox((0,0),label,font=font(40,True));pd.text(((650-(bbox[2]-bbox[0]))/2,45),label,font=font(40,True),fill=(48,43,38));piece=piece.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(0,0,0,0));image.paste(piece,(x,y),piece)
    name_slip(250,520,"John Woodroffe",-1)
    name_slip(1660,520,"Arthur Avalon",1)
    name_slip(955,1000,"Atal Bihari Ghose",-1)
    draw.line((930,595,1620,595),fill=(139,131,117),width=5)
    draw.polygon([(1620,595),(1580,575),(1580,615)],fill=(139,131,117))
    draw.text((970,520),"veröffentlicht unter dem Namen",font=font(29),fill=(190,182,169))
    draw.line((1280,960,1280,700),fill=(139,131,117),width=5)
    draw.text((1340,805),"wichtige Quelle für Übersetzung\nund gelehrte Vermittlung",font=font(29),fill=(190,182,169),spacing=8)
    save(image,episode,"B-G06","AVALON_NETZWERK")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G07","KALKUTTA → LONDON","Geografie bleibt der Quelle untergeordnet")
    source_card(image,resolve("EP04B_Calcutta_High_Court_Frith_PD.jpg"),(150,350,1110,1210),"HIGH COURT OF CALCUTTA · HISTORISCHE ANSICHT")
    draw.line((1210,780,1740,600),fill=CYAN_D,width=8); draw.polygon([(1740,600),(1690,590),(1715,635)],fill=CYAN)
    draw.text((1830,530),"LONDON",font=font(90,True),fill=WHITE);draw.text((1835,650),"DRUCK · VERLAG · UMLAUF",font=font(28,True,True),fill=MUTED);footer(draw,"ORIENTIERUNG · KEIN SPIONAGE-LOOK")
    save(image,episode,"B-G07","CALCUTTA_LONDON")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G08","AUTORITÄT WECHSELT")
    source_card(image,resolve("SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg"),(160,340,1120,1210),"HIER STEHT ES")
    source_card(image,resolve("EP04B_Leadbeater_c1925_PD.jpg"),(1440,340,2360,1210),"ICH SEHE ES · LEADBEATER")
    draw.text((1168,720),"→",font=font(110,True),fill=CYAN);footer(draw,"KEIN DRITTES AUGE · KEINE AURA")
    save(image,episode,"B-G08","AUTORITAET_WECHSELT")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G09","LEADBEATER · 1927","Farben und Formen nur aus echten Platten isolieren")
    plates=["EP04B_Leadbeater_Root_1927_PD.jpg","EP04B_Leadbeater_Heart_1927_PD.jpg","EP04B_Leadbeater_Throat_1927_PD.jpg","EP04B_Leadbeater_Crown_1927_PD.jpg"]
    for i,name in enumerate(plates): source_card(image,resolve(name),(90+i*620,340,650+i*620,1240),f"ORIGINALPLATTE {i+1}")
    footer(draw,"KEINE NACHKOLORIERUNG")
    save(image,episode,"B-G09","LEADBEATER_PLATTEN")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G10","MUTATIONSSCHICHTEN","Jede Quelle behält ihre Proportionen")
    sources=[("EP04B_Yogin_six_chakras_late18c_PD.jpg","SPÄTES 18. JH."),("EP04B_Sapta_Chakra_1899_PD.jpg","1899"),("SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg","1924"),("EP04B_Leadbeater_7_Chakras_Combined_1927_PD.jpg","1927"),(None,"MODERNE KARTE")]
    for i,(name,label) in enumerate(sources):
        x=100+i*430;y=360+i*65
        path = resolve(name) if name else generated(episode, "IMG001")
        source_card(image,path,(x,y,x+620,y+690),label)
    footer(draw,"TRANSPARENTE LAGEN · SICHTBARE NÄHTE")
    save(image,episode,"B-G10","MUTATION_STACK")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G11","","")
    for i,color in enumerate(SPECTRUM):
        strip=Image.new("RGBA",(238,540),(*color,255));grain=Image.effect_noise(strip.size,16).convert("L");grain=ImageOps.colorize(grain,(0,0,0),(255,255,255)).convert("RGBA");strip=Image.blend(strip,grain,0.08);strip=strip.rotate([-2,1,-1,2,-2,1,-1][i],resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(0,0,0,0));x=220+i*315;image.paste(strip,(x,520+(i%2)*12),strip)
    save(image,episode,"B-G11","SPEKTRUM")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G12","","")
    labels=["Farbmodelle","Körperbilder","Psychologie","New Age","Gesundheitsratgeber"]
    for i,label in enumerate(labels):
        slip=Image.new("RGBA",(680,150),(232,226,211,245));sd=ImageDraw.Draw(slip);sd.text((42,48),label,font=font(39,True),fill=(52,47,42));slip=slip.rotate([-2,1,-1,2,0][i],resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(0,0,0,0));x=230+i*395;y=420+i*120;image.paste(slip,(x,y),slip)
    save(image,episode,"B-G12","LAYERS_ADDED")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G13","","")
    labels=["Yoga-Praxis","Arbeitswelt","Therapie-Sprache","Apps"]
    for i,label in enumerate(labels):
        x=180+i*590;piece=Image.new("RGBA",(470,570),(226,220,205,245));pd=ImageDraw.Draw(piece);pd.line((42,80,428,80),fill=SPECTRUM[i+1],width=8);bbox=pd.textbbox((0,0),label,font=font(36,True));pd.text(((470-(bbox[2]-bbox[0]))/2,245),label,font=font(36,True),fill=(50,46,41));piece=piece.rotate([-1,2,-2,1][i],resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(0,0,0,0));image.paste(piece,(x,470),piece)
    save(image,episode,"B-G13","KULTURELLE_KONTEXTE")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G14","EINE WEITERE SCHICHT","Nicht die letzte Wahrheit")
    source_card(image,resolve("EP04A_Jung_portrait_PD.jpg"),(180,350,1050,1230),"C. G. JUNG · HISTORISCHER ANKER")
    source_card(image,resolve("SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg"),(1510,350,2380,1230),"HISTORISCHE KARTE")
    draw.rounded_rectangle((820,610,1800,900),18,fill=(34,46,60,230),outline=CYAN,width=5);draw.text((930,675),"PSYCHOLOGISCHE DEUTUNG",font=font(40,True),fill=WHITE);draw.text((1090,765),"JUNG · 1932",font=font(56,True),fill=CYAN)
    footer(draw)
    save(image,episode,"B-G14","JUNG_LAYER")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G15","","");front=ImageOps.fit(modern_full,(1160,900),Image.Resampling.LANCZOS);image.paste(front,(700,340));save(image,episode,"B-G15","01_FRONTANSICHT")

    image=canvas();draw=ImageDraw.Draw(image);header(draw,"B-G15","","")
    layers=[
        (resolve("EP04B_Yogin_six_chakras_late18c_PD.jpg"),"spätes 18. Jahrhundert"),
        (resolve("EP04B_Sapta_Chakra_1899_PD.jpg"),"1899"),
        (resolve("SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg"),"1924"),
        (resolve("EP04B_Leadbeater_7_Chakras_Combined_1927_PD.jpg"),"1927"),
        (generated(episode,"IMG001"),"heutige Siebenerkarte"),
    ]
    for i,(path,label) in enumerate(layers):
        piece=Image.new("RGBA",(600,800),(232,226,211,255));pd=ImageDraw.Draw(piece);source=fit_source(path,(28,28,572,690));piece.paste(source,(28,28));pd.text((34,720),label,font=font(27,True),fill=(49,44,39));piece=piece.rotate([-4,-2,0,2,4][i],resample=Image.Resampling.BICUBIC,expand=True,fillcolor=(0,0,0,0));image.paste(piece,(150+i*445,360+(i%2)*28),piece)
    save(image,episode,"B-G15","02_SICHTBARE_SCHICHTEN")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", choices=["EP04A", "EP04B", "ALL"], default="ALL")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.episode in {"EP04A", "ALL"}:
        build_ep04a()
    if args.episode in {"EP04B", "ALL"}:
        build_ep04b()
    print(f"Built motion keyframes for {args.episode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
