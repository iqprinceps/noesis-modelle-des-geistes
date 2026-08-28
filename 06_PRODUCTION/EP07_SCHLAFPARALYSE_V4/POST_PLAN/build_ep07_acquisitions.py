#!/usr/bin/env python3
"""EP07 - die 17 offenen `MISSING_ACQUISITION`-Cues schliessen.

`EP07_MISSING_ASSETS_AND_PROMPTS.md`, Prioritaet A, nennt zehn Masterquellen.
Sie zerfallen in zwei Gruppen:

* **Karten.** Neutrale Verortungskarten fuer Aegypten und Daenemark liegen als
  SVG auf Wikimedia Commons und werden serverseitig als PNG gerendert. Fuer
  Neufundland wird die Admiralty-Seekarte von 1873 genutzt, die bereits fuer
  EP06 beschafft wurde - dieselbe gemeinfreie Vorlage, kein zweiter Download.

* **Lizenz- und Rechtefaelle.** Buchcover, Autorenportraet, Paperseite und
  Sendungsmitschnitt sind nicht frei nutzbar. Sie werden nicht nachgebaut,
  sondern durch bibliografische Quellenkarten ersetzt. Ein generierter
  Buchumschlag oder eine nachgestellte Paperseite waere ein gefaelschter Beleg.

Mehrere Cues teilen sich eine Masterquelle (Titel, Methode, Ergebnis). Wo der
Master eine Karte ist, entstehen daraus verschiedene Ausschnitte; wo er eine
Quellenkarte ist, tragen die Cues Varianten mit unterschiedlichem Schwerpunkt.

    python 06_PRODUCTION/EP07_SCHLAFPARALYSE_V4/POST_PLAN/build_ep07_acquisitions.py
"""
from __future__ import annotations

import csv
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

Image.MAX_IMAGE_PIXELS = None

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
ROOT = EPISODE.parents[1]
EP06_ASSETS = ROOT / "06_PRODUCTION" / "EP06_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "02_ASSETS"
OUT = EPISODE / "ACQUISITION_REPLACEMENTS"
QA = OUT / "QA_CONTACT_SHEETS"
CACHE = OUT / "_raster_cache"

SIZE = (2560, 1440)
INSET = (2240, 1260)
MAX_UPSCALE = 2.4
UA = "NOESIS-production/1.0 (contact: info@iqprinceps.de)"

sys.path.insert(0, str(ROOT / "tools"))
from build_schlafparalyse_cards import (  # noqa: E402
    CORAL, CYAN, GOLD, GREEN, LINE, MUTED, PAPER, VIOLET, WHITE,
    background, draw_wrapped, font, footer, header, rounded_panel, wrap,
)

STATUS_COLORS = {"BELEGT": GREEN, "DOKUMENTIERT": GREEN,
                 "RECHTE OFFEN": MUTED, "NICHT FREI": CORAL}

VIEWER_STATUS = {
    "BELEGT": "DIE QUELLE IST NACHVOLLZIEHBAR",
    "DOKUMENTIERT": "DIE QUELLE IST NACHVOLLZIEHBAR",
    "RECHTE OFFEN": "KEIN FREIES ORIGINALBILD",
    "NICHT FREI": "KEIN FREIES ORIGINALBILD",
}

# Zielname -> (Commons-Datei, Ausschnitt als Anteil oder None fuer Vollansicht)
MAPS = {
    "ORIG_ORIG_EGYPT_MAP_PD_full_map.png": ("Egypt location map.svg", None),
    "ORIG_ORIG_DENMARK_MAP_PD_full_map.png": ("Denmark location map.svg", None),
}

# Neufundland: bereits fuer EP06 beschafft, 9697x14974.
NEWFOUNDLAND = "EP06_Fogo_Island_to_Cape_Bonavista_Admiralty_Chart_1873.jpg"
NEWFOUNDLAND_VIEWS = {
    "ORIG_ORIG_NEWFOUNDLAND_MAP_PD_full_map.png": None,
    "ORIG_ORIG_NEWFOUNDLAND_MAP_PD_newfoundland_detail.png": (0.08, 0.10, 0.66, 0.44),
    # Rueckkehr auf dieselbe Karte, minimal weiter gefasst - derselbe Beleg,
    # aber kein pixelgleicher Frame.
    "ORIG_ORIG_NEWFOUNDLAND_MAP_PD_full_return.png": (0.02, 0.04, 0.98, 0.62),
}

CARDS = [
    dict(filename="ORIG_ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED_full_cover.png",
         section="", title="Das Buch, das den Fall öffnet",
         subtitle="David Hufford untersucht Erfahrung und Erzählung gemeinsam.",
         entries=[("Werk", "The Terror That Comes in the Night, 1982."),
                  ("Inhalt", "Feldforschung auf Neufundland zur Old Hag und Schlafparalyse."),
                  ("Warum kein Cover", "Für den Umschlag liegt keine freie Nutzungserlaubnis vor.")],
         status="RECHTE OFFEN",
         note="Die Buchangabe ist echt. Ein nachgebauter Umschlag wäre kein historischer Beleg.",
         source="Quellenkarte · Werkangabe", accent=VIOLET),
    dict(filename="ORIG_ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED_title_detail.png",
         section="S5 Titel", title="Der Titel benennt die Erfahrung",
         subtitle="„The Terror That Comes in the Night“, 1982.",
         entries=[("Titel", "The Terror That Comes in the Night."),
                  ("Untertitel", "An Experience-Centered Study of Supernatural "
                                 "Assault Traditions."),
                  ("Methode", "Hufford setzt bei der Erfahrung an, nicht bei der "
                              "Frage, ob die Deutung stimmt.")],
         status="DOKUMENTIERT", note="Das Buch ist veröffentlicht und auffindbar.",
         source="Quellenkarte · Titel und Methode", accent=VIOLET),
    dict(filename="ORIG_ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED_cover_return.png",
         section="S5 Rückgriff", title="Zurück zu Hufford",
         subtitle="Der Ausgangspunkt der Folge, noch einmal benannt.",
         entries=[("Ausgangspunkt", "Eine eigene Episode 1963, daraus systematische "
                                    "Feldforschung."),
                  ("Ergebnis", "Berichte ähneln sich auch dort, wo die Überlieferung "
                               "vorher nicht bekannt war."),
                  ("Grenze", "Das belegt kein äußeres Wesen; es verschiebt die Frage.")],
         status="DOKUMENTIERT", note="Zusammenfassung der Forschungsposition.",
         source="Quellenkarte · Rückgriff", accent=VIOLET),
    dict(filename="ORIG_ORIG_HUFFORD_PORTRAIT_LICENSED_portrait.png",
         section="S5 Autor", title="Kein freigegebenes Porträt",
         subtitle="Die Person ist benannt, das Bild ist nicht frei.",
         entries=[("Person", "David J. Hufford, Folklorist und Medizinethnologe."),
                  ("Rolle", "Autor der Neufundland-Studie und Begründer des "
                            "experience-centered approach."),
                  ("Rechte", "Für ein Porträt liegt keine geklärte freie Lizenz vor.")],
         status="RECHTE OFFEN",
         note="Kein generiertes Gesicht: ein erfundenes Porträt einer realen "
              "Person wäre eine Fälschung.",
         source="Quellenkarte · Personenangabe ohne Bild", accent=MUTED),
    dict(filename="ORIG_ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER_title_authors.png",
         section="S7 Studie", title="Der Vergleich zweier Länder",
         subtitle="Warum dieselbe Nacht unterschiedlich schwer wiegt.",
         entries=[("Autoren", "Baland Jalal und Devon E. Hinton."),
                  ("Gegenstand", "Vergleich von Häufigkeit und Belastung durch "
                                 "Schlafparalyse zwischen Ägypten und Dänemark."),
                  ("Bedeutung", "Die kulturelle Deutung verändert, wie stark die "
                                "Erfahrung belastet.")],
         status="DOKUMENTIERT",
         note="Publizierte Vergleichsforschung. Die Folge referiert die "
              "Fragestellung, nicht einzelne Messwerte.",
         source="Bibliografische Quellenkarte · Ersatz für nicht frei nutzbare Paperseite",
         accent=CYAN),
    dict(filename="ORIG_ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER_methods_detail.png",
         section="S7 Methode", title="Wie verglichen wurde",
         subtitle="Zwei Stichproben, dieselbe Erhebung.",
         entries=[("Vorgehen", "Befragung vergleichbarer Gruppen in beiden Ländern "
                               "zu Häufigkeit, Angst und Deutung."),
                  ("Kernidee", "Nicht der Körperzustand unterscheidet sich, sondern "
                               "der Deutungsrahmen."),
                  ("Grenze", "Eine Befragung misst Berichte, keine Nachtereignisse.")],
         status="DOKUMENTIERT", note="Methodenbeschreibung, keine Einzelwerte.",
         source="Quellenkarte · Methode", accent=CYAN),
    dict(filename="ORIG_ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER_results_detail.png",
         section="S7 Befund", title="Derselbe Zustand, andere Last",
         subtitle="Der Unterschied liegt in der Erklärung, nicht im Körper.",
         entries=[("Befund", "Wo die Erfahrung als Angriff durch ein Wesen gedeutet "
                             "wird, fällt die Angst deutlich stärker aus."),
                  ("Folge", "Angst verlängert und verstärkt die nächtliche Episode."),
                  ("Vorsicht", "Das ist ein Zusammenhang, keine bewiesene Ursache.")],
         status="DOKUMENTIERT", note="Richtung des Befundes, ohne Zahlenbehauptung.",
         source="Quellenkarte · Befund", accent=CYAN),
    dict(filename="ORIG_ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER_citation_block.png",
         section="S7 Beleg", title="Woher dieser Vergleich stammt",
         subtitle="Quellenangabe zur Studie.",
         entries=[("Autoren", "Baland Jalal, Devon E. Hinton."),
                  ("Thema", "Schlafparalyse im Kulturvergleich Ägypten – Dänemark."),
                  ("Verwendung", "Die Folge nutzt die Fragestellung und die Richtung "
                                 "des Befundes.")],
         status="DOKUMENTIERT", note="Belegangabe.",
         source="Quellenkarte · Zitationsangabe", accent=CYAN),
    dict(filename="ORIG_ORIG_EGYPT_SLEEP_PARALYSIS_SOURCE_source_detail.png",
         section="S7 Ägypten", title="Der Deutungsrahmen in Ägypten",
         subtitle="Ein bekannter Name für die Nacht.",
         entries=[("Rahmen", "Die Erfahrung wird häufig im Rahmen einer geläufigen "
                             "übernatürlichen Deutung verstanden."),
                  ("Wirkung", "Ein vertrauter Name macht die Nacht erklärbar — "
                              "und zugleich bedrohlicher."),
                  ("Grenze", "Das beschreibt eine Deutungskultur, nicht die Ursache "
                             "des Zustands.")],
         status="DOKUMENTIERT", note="Kontextangabe zur Stichprobe.",
         source="Quellenkarte · kultureller Kontext", accent=GOLD),
    dict(filename="ORIG_ORIG_DENMARK_SLEEP_PARALYSIS_SOURCE_source_detail.png",
         section="S7 Dänemark", title="Der Deutungsrahmen in Dänemark",
         subtitle="Dieselbe Nacht, ein anderer Erklärungsvorrat.",
         entries=[("Rahmen", "Die Erfahrung wird überwiegend physiologisch "
                             "eingeordnet."),
                  ("Wirkung", "Eine körperliche Erklärung nimmt der Nacht einen "
                              "Teil ihrer Bedrohlichkeit."),
                  ("Grenze", "Auch das ist ein Deutungsrahmen, keine Wertung.")],
         status="DOKUMENTIERT", note="Kontextangabe zur Stichprobe.",
         source="Quellenkarte · kultureller Kontext", accent=GOLD),
    dict(filename="ORIG_ORIG_CHINESE_GHOST_PRESSURE_SOURCE_PD_source_detail.png",
         section="", title="Auch in China hat das Drücken einen Namen",
         subtitle="Der Zustand ist weit verbreitet — seine Namen sind regional.",
         entries=[("Überliefert", "Nächtliche Lähmung und Druck gelten als eigenes benanntes Ereignis."),
                  ("Wichtig", "Der Name deutet die Erfahrung; er erklärt nicht ihre körperliche Ursache.")],
         status="NICHT FREI",
         note="Die Bezeichnung ist überliefert. Eine beliebige Geistergrafik würde nichts belegen.",
         source="Quellenkarte · Überlieferungshinweis", accent=CORAL),
    dict(filename="ORIG_ORIG_ART_BELL_2001_BROADCAST_SOURCE_source_frame.png",
         section="", title="Eine Sendung bündelt Tausende Berichte",
         subtitle="Am 12. April 2001 werden dunkle Gestalten zum Radiothema.",
         entries=[("Wirkung", "Aus vielen einzelnen Nächten wird ein gemeinsames Motiv."),
                  ("Warum kein Mitschnitt", "Für die Sendung liegt keine freie "
                                             "Nutzungserlaubnis vor.")],
         status="RECHTE OFFEN", note="Die Sendungsangabe ist belegt. Originalton wird nicht verwendet.",
         source="Quellenkarte · Sendungsangabe", accent=GOLD),
]


def fetch_svg(commons_name: str) -> Path:
    dest = CACHE / (Path(commons_name).stem + ".png")
    if dest.is_file():
        return dest
    url = (f"https://commons.wikimedia.org/wiki/Special:FilePath/"
           f"{urllib.parse.quote(commons_name)}?width=3000")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(req, timeout=120) as res:
        dest.write_bytes(res.read())
    return dest


def load(path: Path) -> Image.Image:
    with Image.open(path) as src:
        if src.mode in ("RGBA", "LA", "P"):
            src = src.convert("RGBA")
            flat = Image.new("RGBA", src.size, (247, 244, 236, 255))
            flat.alpha_composite(src)
            return flat.convert("RGB")
        return src.convert("RGB")


def frame(src: Image.Image, box=None) -> Image.Image:
    if box is not None:
        w, h = src.size
        src = src.crop((round(box[0] * w), round(box[1] * h),
                        round(box[2] * w), round(box[3] * h)))
        return ImageOps.fit(src, SIZE, method=Image.Resampling.LANCZOS)
    bg = ImageOps.fit(src, SIZE, method=Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(52))
    bg = ImageEnhance.Color(bg).enhance(0.24)
    bg = ImageEnhance.Brightness(bg).enhance(0.30)
    bg = Image.blend(bg, Image.new("RGB", SIZE, (16, 13, 11)), 0.50)
    scale = min(INSET[0] / src.width, INSET[1] / src.height, MAX_UPSCALE)
    fg = src.resize((max(1, round(src.width * scale)), max(1, round(src.height * scale))),
                    Image.Resampling.LANCZOS)
    framed = Image.new("RGB", (fg.width + 12, fg.height + 12), (46, 36, 24))
    framed.paste(fg, (6, 6))
    bg.paste(framed, ((SIZE[0] - framed.width) // 2, (SIZE[1] - framed.height) // 2))
    return bg


def build_card(spec: dict) -> Image.Image:
    accent = spec.get("accent", CYAN)
    image = background(accent)
    draw = ImageDraw.Draw(image, "RGBA")
    header(draw, "EP07", spec["section"], spec["title"], spec["subtitle"])
    left_x, right_x, y1 = 112, 1660, 470
    left_w, right_w = right_x - 60 - left_x, SIZE[0] - 112 - right_x
    height = 54
    for _, value in spec["entries"]:
        height += 38 + len(wrap(draw, value, font(33), left_w - 96)) * 43 + 26
    shown_status = VIEWER_STATUS.get(spec["status"], spec["status"])
    status_lines = len(wrap(draw, shown_status, font(36, bold=True), right_w - 88))
    note_lines = len(wrap(draw, spec["note"], font(28), right_w - 88))
    right_h = 196 + status_lines * 48 + 88 + note_lines * 40 + 54
    y2 = min(SIZE[1] - 150, y1 + max(height + 34, right_h, 320))

    rounded_panel(draw, (left_x, y1, right_x - 60, y2), accent)
    y = y1 + 54
    for label, value in spec["entries"]:
        draw.text((left_x + 48, y), label.upper(), font=font(24, bold=True), fill=accent)
        y += 38
        y = draw_wrapped(draw, (left_x + 48, y), value, font(33), PAPER, left_w - 96, 10)
        y += 26

    color = STATUS_COLORS.get(spec["status"], MUTED)
    rounded_panel(draw, (right_x, y1, SIZE[0] - 112, y2), color)
    draw.text((right_x + 44, y1 + 54), "KURZ GESAGT", font=font(24, bold=True), fill=MUTED)
    draw.line((right_x + 44, y1 + 112, SIZE[0] - 156, y1 + 112), fill=color, width=8)
    ty = draw_wrapped(draw, (right_x + 44, y1 + 158), shown_status, font(36, bold=True),
                      WHITE, right_w - 88, 8)
    draw.line((right_x + 44, ty + 26, SIZE[0] - 156, ty + 26), fill=LINE, width=2)
    draw_wrapped(draw, (right_x + 44, ty + 62), spec["note"], font(28), PAPER,
                 right_w - 88, 12)
    source = spec["source"].replace("Bibliografische Quellenkarte · ", "Quelle · ")
    source = source.replace("Quellenkarte · ", "Quelle · ")
    source = source.replace("Ersatz für nicht frei nutzbare Paperseite", "Studienangabe")
    footer(draw, source)
    return image.convert("RGB")


def contact_sheets(files: list[Path]) -> None:
    QA.mkdir(parents=True, exist_ok=True)
    thumb, label_h, cols, rows = (480, 270), 54, 4, 3
    small = ImageFont.load_default(size=17)
    for page, start in enumerate(range(0, len(files), cols * rows), 1):
        batch = files[start:start + cols * rows]
        sheet = Image.new("RGB", (cols * thumb[0], rows * (thumb[1] + label_h)), (14, 12, 18))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(batch):
            with Image.open(path) as im:
                sheet.paste(im.convert("RGB").resize(thumb, Image.Resampling.LANCZOS),
                            ((i % cols) * thumb[0], (i // cols) * (thumb[1] + label_h)))
            draw.text(((i % cols) * thumb[0] + 8,
                       (i // cols) * (thumb[1] + label_h) + thumb[1] + 9),
                      path.stem.replace("ORIG_", "")[:44], fill=(236, 231, 215), font=small)
        sheet.save(QA / f"EP07_ACQUISITION_REPLACEMENTS_{page:02d}.jpg", quality=91)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    manifest: list[dict[str, str]] = []

    for target, (commons, box) in MAPS.items():
        src = load(fetch_svg(commons))
        out = OUT / target
        frame(src, box).save(out, compress_level=6)
        created.append(out)
        manifest.append({"filename": target, "kind": "MAP_PD", "source": commons,
                         "resolution": "2560x1440", "camera_rule": "NO_PAN_NO_ZOOM"})
        print(f"  Karte       {target}  <- {commons}")

    chart = EP06_ASSETS / NEWFOUNDLAND
    if chart.is_file():
        src = load(chart)
        for target, box in NEWFOUNDLAND_VIEWS.items():
            out = OUT / target
            frame(src, box).save(out, compress_level=6)
            created.append(out)
            manifest.append({"filename": target, "kind": "MAP_PD_SHARED_WITH_EP06",
                             "source": NEWFOUNDLAND, "resolution": "2560x1440",
                             "camera_rule": "NO_PAN_NO_ZOOM"})
            print(f"  Seekarte    {target}  <- EP06/{NEWFOUNDLAND[:34]}")
    else:
        print(f"  FEHLT: Neufundland-Seekarte ({chart})")

    for spec in CARDS:
        out = OUT / spec["filename"]
        build_card(spec).save(out, compress_level=6)
        created.append(out)
        manifest.append({"filename": spec["filename"], "kind": "SOURCE_CARD",
                         "source": spec["source"], "resolution": "2560x1440",
                         "camera_rule": "STATIC_CARD"})
        print(f"  Quellenkarte {spec['filename']}")

    with (OUT / "EP07_ACQUISITION_REPLACEMENTS_MANIFEST.csv").open(
            "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)
    contact_sheets(created)
    print(f"\ncreated={len(created)}")


if __name__ == "__main__":
    main()
