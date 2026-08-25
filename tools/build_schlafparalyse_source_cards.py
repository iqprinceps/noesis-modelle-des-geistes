#!/usr/bin/env python3
"""Quellenkarten fuer nicht beschaffbare Belege (EP08, spaeter EP06/EP07).

Einige im Sync-Plan vorgesehene Originalbelege sind nicht frei beschaffbar:
lizenzpflichtiges Key Art, Forenmitschnitte, Archivansichten hinter
Bot-Erkennung. Der Produktionsplan sieht dafuer ausdruecklich eine
Bibliografie- beziehungsweise Quellenkarte als Ersatz vor.

Diese Karten bauen **keine** Benutzeroberflaeche nach. Ein nachgebauter
Forenthread oder ein erfundener Archiv-Screenshot waere ein gefaelschter Beleg
und genau das, was der Claims-Lock der Folge verbietet. Stattdessen benennt die
Karte die Aussage, die Art der Quelle und - wo es der Claims-Lock verlangt -
ausdruecklich die Beleggrenze.

Aufruf aus dem Repository-Root:
    python tools/build_schlafparalyse_source_cards.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_schlafparalyse_cards import (  # noqa: E402
    CORAL, CYAN, GOLD, GREEN, H, LINE, MUTED, PAPER, VIOLET, W, WHITE,
    background, draw_wrapped, font, footer, header, rounded_panel, wrap,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4" / "SOURCE_CARDS"

# Ampel fuer die Belegstaerke. Die Farbe ist Teil der Aussage.
STATUS_COLORS = {
    "BELEGT": GREEN,
    "DOKUMENTIERT": GREEN,
    "BERICHTE": GOLD,
    "NICHT BELEGT": CORAL,
    "RECHTE OFFEN": MUTED,
}


def source_card(filename: str, section: str, title: str, subtitle: str,
                entries: list[tuple[str, str]], status: str, status_note: str,
                source: str, accent=CYAN) -> dict[str, str]:
    """Belegkarte: links die bibliografischen Zeilen, rechts die Belegampel."""
    image = background(accent)
    draw = ImageDraw.Draw(image, "RGBA")
    header(draw, "EP08", section, title, subtitle)

    left_x, right_x = 112, 1660
    panel_y1 = 470
    left_w = right_x - 60 - left_x
    right_w = W - 112 - right_x

    # Panelhoehe vorab aus dem Umbruch bestimmen, damit kein leeres Feld
    # unter dem Text stehen bleibt.
    def block_height(items: list[tuple[str, str]], body: int, wrap_w: int) -> int:
        total = 54
        for label, value in items:
            total += 38
            total += len(wrap(draw, value, font(body), wrap_w)) * (body + 10)
            total += 26
        return total + 34

    left_h = block_height(entries, 33, left_w - 96)
    status_lines = len(wrap(draw, status, font(40, bold=True), right_w - 88))
    note_lines = len(wrap(draw, status_note, font(28), right_w - 88))
    right_h = 196 + status_lines * 48 + 88 + note_lines * 40 + 54
    panel_y2 = min(H - 150, panel_y1 + max(left_h, right_h, 320))

    # Bibliografieblock
    rounded_panel(draw, (left_x, panel_y1, right_x - 60, panel_y2), accent)
    y = panel_y1 + 54
    for label, value in entries:
        draw.text((left_x + 48, y), label.upper(), font=font(24, bold=True), fill=accent)
        y += 38
        y = draw_wrapped(draw, (left_x + 48, y), value, font(33), PAPER,
                         left_w - 96, 10)
        y += 26

    # Belegampel
    color = STATUS_COLORS.get(status, MUTED)
    rounded_panel(draw, (right_x, panel_y1, W - 112, panel_y2), color)
    draw.text((right_x + 44, panel_y1 + 54), "BELEGLAGE", font=font(24, bold=True), fill=MUTED)
    draw.ellipse((right_x + 44, panel_y1 + 108, right_x + 100, panel_y1 + 164), fill=color + (255,))
    ty = draw_wrapped(draw, (right_x + 44, panel_y1 + 196), status, font(40, bold=True),
                      WHITE, right_w - 88, 8)
    draw.line((right_x + 44, ty + 26, W - 156, ty + 26), fill=LINE, width=2)
    draw_wrapped(draw, (right_x + 44, ty + 62), status_note, font(28), PAPER,
                 right_w - 88, 12)

    footer(draw, source)
    OUT.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUT / filename, format="PNG", optimize=True)
    print(OUT / filename)
    return {"filename": filename, "section": section, "title": title,
            "status": status, "source": source, "resolution": f"{W}x{H}"}


def main() -> None:
    manifest: list[dict[str, str]] = []

    # --- S4 Harvard / Forschung -------------------------------------------
    manifest.append(source_card(
        "SRC051_HARVARD_RESEARCH_TITLE.png", "S4 Harvard",
        "Zwei Wege durch dieselbe Frage",
        "An derselben Universität, mit gegensätzlichem Zugang.",
        [("Psychiatrie", "John E. Mack, Psychiater in Harvard, nimmt die Schilderungen "
                         "seiner Interviewpartner ernst und hält viele von ihnen nicht "
                         "für klassisch psychotisch."),
         ("Psychologie", "Susan Clancy, Richard J. McNally und Kolleginnen und Kollegen "
                         "untersuchen dieselben Berichte auf Schlafparalyse, "
                         "Suggestibilität und False-Memory-Effekte.")],
        "DOKUMENTIERT",
        "Beide Forschungslinien sind publiziert. Die Karte behauptet nicht, "
        "eine Seite habe die andere widerlegt.",
        "Quellenkarte · Forschungsüberblick · kein Einzelnachweis", CYAN))

    manifest.append(source_card(
        "SRC052_MCNALLY_CLANCY_BIBLIOGRAPHY.png", "S4 Erinnerung",
        "Woher die Gegenposition kommt",
        "Die Forschung zu Erinnerung und Suggestibilität, auf die sich die Folge stützt.",
        [("Susan A. Clancy", "Abducted. How People Come to Believe They Were Kidnapped "
                             "by Aliens. Harvard University Press, 2005."),
         ("Richard J. McNally", "Remembering Trauma. Harvard University Press, 2003."),
         ("Gegenstand", "Zusammenhänge zwischen Schlafparalyse, Suggestibilität und der "
                        "Entstehung von Überzeugungen — nicht die Bloßstellung einzelner "
                        "Zeuginnen und Zeugen.")],
        "BELEGT",
        "Publizierte Monografien. Die Folge referiert die Fragestellung, "
        "nicht ein einzelnes Studienergebnis.",
        "Bibliografische Quellenkarte · Ersatz für nicht frei nutzbare Originalseite", CYAN))

    # --- S5 Diphenhydramin -------------------------------------------------
    # Zusammengefasst aus zwei fruehen Karten. Eine "Detailansicht" einer
    # Textkarte traegt keine zusaetzliche Information - sie erzeugte im Schnitt
    # nur eine zweite Textstandzeit im selben Akt.
    manifest.append(source_card(
        "SRC053_DPH_MEDICAL_STATEMENT.png", "S5 Substanz",
        "Was dokumentiert ist — und was nicht",
        "Anticholinerges Delirium ist belegt. Die Gestalt ist es nicht.",
        [("Wirkstoff", "Diphenhydramin, ein sedierendes Antihistaminikum der ersten "
                       "Generation mit anticholinerger Wirkung."),
         ("Dokumentiert", "In hoher Dosis sind anticholinerges Delirium, Verwirrtheit "
                          "und Halluzinationen medizinisch beschrieben."),
         ("Berichtet", "Die Verbindung zu einer großen dunklen Gestalt mit Hutrand "
                       "stammt überwiegend aus Erfahrungsberichten im Netz."),
         ("Folgerung", "Beides darf nebeneinanderstehen. Als Ursache-Wirkungs-Kette "
                       "darf es nicht erzählt werden.")],
        "TEILS BELEGT",
        "Die Substanzwirkung ist dokumentiert. Ein „Hat-Man-Syndrom“ "
        "ist sie ausdrücklich nicht.",
        "Quellenkarte · Substanzwirkung und Beleggrenze · Claims-Lock S08-06/07", GOLD))

    manifest.append(source_card(
        "SRC055_HAT_REPORTS_EVIDENCE_STATUS.png", "S5 Berichte",
        "Die Berichte selbst sind die Quelle",
        "Was Menschen im Netz schildern — und was das trägt.",
        [("Material", "Datierte Erfahrungsberichte in offenen Foren und Kommentarspalten."),
         ("Was sie zeigen", "Dass sich eine sehr ähnliche Beschreibung über viele "
                            "voneinander unabhängige Schilderungen hinweg wiederholt."),
         ("Was sie nicht zeigen", "Keine Diagnose, keine Häufigkeit, keine Ursache.")],
        "BERICHTE",
        "Erfahrungsberichte sind ein Beleg für ein verbreitetes Motiv — "
        "nicht für dessen Ursache.",
        "Quellenkarte · Ersatz für nicht reproduzierbaren Forenmitschnitt", GOLD))

    # --- S6 Netz / Archiv ---------------------------------------------------
    manifest.append(source_card(
        "SRC056_WEB_ARCHIVE_STATUS.png", "S6 Verbreitung",
        "Wie sich das Motiv im Netz ausbreitet",
        "Nachvollziehbar an Datierung und Wiederholung.",
        [("Beobachtung", "Beschreibungen einer großen, hutbewehrten Schattengestalt "
                         "tauchen ab den frühen Zweitausendern in wachsender Zahl auf."),
         ("Mechanik", "Suchergebnisse, Foren und später Videoplattformen führen "
                      "gleichartige Schilderungen zusammen."),
         ("Grenze", "Häufigkeit im Netz misst Sichtbarkeit, nicht Verbreitung "
                    "in der Bevölkerung.")],
        "BERICHTE",
        "Reichweite und Datierung sind nachvollziehbar. Eine Fallzahl "
        "lässt sich daraus nicht ableiten.",
        "Quellenkarte · Ersatz für nicht abrufbare Archivansicht", VIOLET))

    manifest.append(source_card(
        "SRC057_PERIOD_FORUM_STATUS.png", "S6 Frühe Spuren",
        "Die frühe Phase ist schlecht archiviert",
        "Ein Teil der Ursprungsdiskussion ist nicht mehr abrufbar.",
        [("Bestand", "Frühe Foren und Mailinglisten sind teils gelöscht, teils nur "
                     "lückenhaft archiviert."),
         ("Folge", "Der genaue Ursprung einzelner Formulierungen lässt sich heute "
                   "nicht mehr sauber datieren."),
         ("Konsequenz", "Die Folge nennt niemanden als Erfinder des Motivs.")],
        "RECHTE OFFEN",
        "Fehlende Archivierung ist selbst ein Befund — und ein Grund "
        "zur Zurückhaltung.",
        "Quellenkarte · Ersatz für nicht verfügbaren Periodenmitschnitt", MUTED))

    # --- S7 Film ------------------------------------------------------------
    # Werkangabe und Rechtehinweis standen urspruenglich auf zwei Karten und
    # landeten im Schnitt direkt hintereinander - dreizehn Sekunden Fliesstext
    # am Stueck. Der Rechtehinweis ist eine Fussnote der Werkangabe, keine
    # eigene Aussage, und steht jetzt in deren Beleglage.
    manifest.append(source_card(
        "SRC058_NIGHTMARE_BIBLIOGRAPHY.png", "S7 Film",
        "Der Dokumentarfilm als Verstärker",
        "Ein Film bündelt die Schilderungen und gibt ihnen ein Bild.",
        [("Werk", "The Nightmare. Dokumentarfilm von Rodney Ascher, 2015."),
         ("Gegenstand", "Schilderungen von Betroffenen der Schlafparalyse, "
                        "als Spielszenen rekonstruiert."),
         ("Bedeutung für die Folge", "Der Film ist Teil der Verbreitungsgeschichte "
                                     "des Motivs, nicht ihre Ursache.")],
        "DOKUMENTIERT",
        "Werkangabe. Für Key Art und Filmbilder liegt keine freie "
        "Nutzungserlaubnis vor; die Folge zeigt daher kein Filmbild.",
        "Bibliografische Quellenkarte · kein Bildmaterial des Films", VIOLET))

    path = OUT / "EP08_SOURCE_CARDS_MANIFEST.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)
    print(f"\ncreated={len(manifest)}")


if __name__ == "__main__":
    main()
