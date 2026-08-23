#!/usr/bin/env python3
"""EP03 PEAR — Timeline, Ton, Render, Untertitel, QA.

Abgeleitet von `tools/produce_ep02_gateway_v7.py`; die Vorlage bleibt
unveraendert. Uebernommen sind Bauweise und alle Lehren, die dort im Code
stehen: Vollbild statt Pad, Einpassen fuer alles, was vom 16:9-Format
abweicht, Ken Burns mit sichtbaren sechs Prozent, Blende an jeder Aktgrenze,
Segmentpruefung mit ffprobe vor dem Ueberspringen, Musikbett mit Anteil ueber
620 Hz.

Geaendert sind Pfade, Farbwelt (Kozyrev statt Gateway), die Aktgrenzen — sie
werden hier aus dem Stem-Report berechnet statt fest eingetragen — und die
Shotliste.

    python tools/spg_produce.py prepare     # GIF und Patentseiten aufbereiten
    python tools/spg_produce.py all
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

ALIGNMENT = PROD / "voice" / "alignment" / "EP03_PEAR_alignment.json"
VOICE = PROD / "audio" / "EP03_voice_-18LUFS.wav"
STEMREPORT = PROD / "voice" / "master" / "stem_report.json"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN.txt"

TIMELINE = PROD / "timeline" / "EP03_PEAR_timeline.json"
SEGMENTS = PROD / "render" / "segments"
FINAL = PROD / "render" / "final"
AUDIO = PROD / "audio"
CARDS = PROD / "visuals" / "cards"
GEN = PROD / "visuals" / "generated"
MOTION = PROD / "motion"
DOCS = PROD / "visuals" / "documents"

FPS = 30
# Zwischenschritte je Ausgabebild. Die Fahrt wird viermal so fein
# gerechnet und dann gemittelt; das nimmt der Rundung von zoompan die
# letzte Stufe. Siehe camera_filter().
SUB = 4
ENDCARD_SEC = 20.0
NAME = "EP03_PEAR"
GRUND = "#0E1013"          # Institutsgrau, Blendenfarbe

# Vorlauf und Pausen aus tools/spg_voice.py — fuer die Aktgrenzen
PRE, GAP = 0.35, 0.65

# Intensitaetskurve nach Produktionsstandard § 6, entlang der acht Akte
KURVE = [0.85, 0.58, 0.70, 0.88, 0.74, 0.92, 1.00, 0.66]


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


def loudness(path: Path, target=-14.0, peak=-1.0, lra=7.0) -> dict:
    import re
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
               "-af", f"loudnorm=I={target}:TP={peak}:LRA={lra}:print_format=json",
               "-f", "null", "-"], True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', out, re.S)[-1])


def aktgrenzen() -> list[float]:
    """Startzeit jedes Akts auf der Tonspur, aus dem Stem-Report."""
    rep = json.loads(STEMREPORT.read_text(encoding="utf-8"))
    t, starts = PRE, []
    for i, stem in enumerate(rep["stems"]):
        starts.append(t)
        t += stem["duration"] + (GAP if i < len(rep["stems"]) - 1 else 0.0)
    starts.append(t)
    return starts


# ----------------------------------------------------------------- Quellen

def g(n): return str((GEN / f"{n}.png").resolve())
def c(n): return str((CARDS / f"{n}.png").resolve())
def mo(n): return str((MOTION / f"{n}.mp4").resolve())
def d(n): return str((DOCS / n).resolve())
def a(*p): return str(ROOT.joinpath(*p).resolve())


DL = ("04_ASSETS", "01_DOWNLOADS", "EP03_PEAR")
PAT = ("04_ASSETS", "01_DOWNLOADS", "EP03_PEAR", "P20_US5830064_figures_PD-USGov")


def pt(n):
    """Blatt der US-Patentschrift 5.830.064."""
    return a(*PAT, f"US5830064_{n}_2320x3408.png")


# --- Echtes Material. Was hier steht, ist fotografiert oder gedruckt, nicht
# --- erzeugt. Bei EP01A lag der Anteil bei elf Prozent und die Folge wirkte
# --- dadurch behauptet; hier gibt es genug, um auf ein Drittel zu kommen.
EQUAD       = a(*DL, "P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg")
NASSAU      = a(*DL, "P02_Nassau_Hall_2026_CC-BY-4.0.jpg")
GATE        = a(*DL, "P03_FitzRandolph_Gate_2026_CC-BY-4.0.jpg")
BLAIR       = a(*DL, "P06_Blair_Arch_2026_CC-BY-4.0.jpg")
HOF1        = a(*DL, "P26_EQuad_Courtyard_StoneRiddle_2023_CC-BY-SA-4.0.jpg")
HOF2        = a(*DL, "P27_EQuad_Courtyard_SphericTheme_2023_CC-BY-SA-4.0.jpg")
GALTON      = a(*DL, "P07_Galton_board_before_after_2017_CC-BY-SA-4.0.jpg")
GALTON2     = a(*DL, "P30_Galton_box_RMC_standin_2016_CC-BY-SA-4.0.jpg")
SKOP89      = a(*DL, "P08_Tektronix_2467_scope_1989_PD-USGov-DOE.jpg")
SKOP83      = a(*DL, "P09_Tektronix_7903_scope_1983_PD-USGov-DOE.jpg")
SKOP77      = a(*DL, "P17_Tektronix_475A_1977_analog_scope_CC-BY-SA-3.0.jpg")
LOCHBAND    = a(*DL, "P10_Mylar_punched_tape_1979_CC-BY-SA-3.0.jpg")
LOCHSTANZER = a(*DL, "P11_Papertape_punch_reader_CHM_CC-BY-SA-4.0.jpg")
LOCHROLLEN  = a(*DL, "P12_Punched_paper_tapes_CHM_2005_CC-BY-2.0.jpg")
ZENER       = a(*DL, "P13_Zener_diode_1N829_CC-BY-SA-4.0.jpg")
AUSDRUCK78  = a(*DL, "P14_Bound_line_printer_listing_1978_CC-BY-SA-3.0.jpg")
DRUCKER     = a(*DL, "P15_CDC_501_line_printer_CC-BY-SA-3.0.jpg")
DRUCKWALZE  = a(*DL, "P16_Line_printer_drum_CC-BY-SA-3.0.jpg")
TRNG        = a(*DL, "P31_TRNG_Araneus_Alea_REG_standin_2018_CC-BY-4.0.jpg")
JAHN_TANK   = a(*DL, "P28_Jahn_Princeton_lab_1966_Plexiglas_vacuum_tank_Fig27.png")
JAHN_HORN   = a(*DL, "P29_Jahn_Princeton_lab_1966_microwave_horn_electrode_Fig17.png")
JAHN_SONDE  = a(*DL, "P34_Jahn_Princeton_lab_1966_field_probe_coil_Fig01_PD-US-no-notice.png")
JAHN_INTER  = a(*DL, "P33_Jahn_Princeton_lab_1966_microwave_interferometer_Fig18_PD-US-no-notice.png")
JAHN_SIGNAT = a(*DL, "P35_Jahn_signature_titlepage_1966_PD-US-no-notice.png")
IGPP        = a(*DL, "P21_IGPP_Freiburg_Wilhelmstrasse3a_2011_CC-BY-SA-3.0.jpg")
IGPP_SCHILD = a(*DL, "P22_IGPP_Freiburg_Schild_2011_CC-BY-SA-3.0.jpg")
GIESSEN     = a(*DL, "P23_JLU_Giessen_Hauptgebaeude_2007_CC-BY-SA-4.0.jpg")
GIESSEN2    = a(*DL, "P25_JLU_Giessen_Philosophikum_I_2016_CC-BY-SA-3.0.jpg")

# Quellzeilen nach Produktionsstandard § 4: sie benennen das Blatt, sie
# kommentieren nicht.
REKON   = "Rekonstruktion"
PATENT  = "US-Patentschrift 5.830.064"
NASA66  = "Jahn, Princeton 1966 · gemeinfrei"
CCBY4   = "CC BY 4.0"
CCBYSA4 = "CC BY-SA 4.0"
CCBYSA3 = "CC BY-SA 3.0"
CCBY2   = "CC BY 2.0"
PD_DOE  = "US Department of Energy · gemeinfrei"


def s(anchor, visual, scene, gloss="", src="", kind="STILL"):
    return {"anchor": anchor, "visual": visual, "scene": scene, "kind": kind,
            "gloss": gloss, "src": src}


def shots():
    """Die Shotliste, an Textankern statt an Sekunden.

    Verteilung nach Produktionsstandard: bei EP01A lagen 74 Prozent auf
    Rekonstruktionen, weil es zu diesem Thema fast nichts Freies gibt. Hier
    gibt es 56 brauchbare Archivstuecke — 25 Patentblaetter, Jahns eigene
    Laborfotos von 1966, die Technik der Zeit. Die ist hier keine Deko: wenn
    der Text von einer Rauschdiode spricht, ist das echte Foto einer Diode die
    richtige Einstellung, nicht ein erzeugtes Bild davon.
    """
    return [
        # ============================================================ S1 Hook
        s("Du sitzt in einem Kellerraum", g("pe_a01_keller_weit"), "S1", src=REKON),
        s("Vor dir steht eine graue Kiste", g("pe_a02_kiste_detail"), "S1", src=REKON),
        s("Die Kiste wirft eine Münze.", mo("muenzwurf"), "S1", kind="VIDEO"),
        s("Tausend Mal in der Sekunde", g("pe_a03_ziffern_makro"), "S1", src=REKON),
        s("aus einem Rauschen, das niemand", SKOP83, "S1",
          "Analogoszilloskop, 1983", PD_DOE),
        s("Deine Aufgabe ist einfach", g("pe_a04_person_ruecken"), "S1", src=REKON),
        s("Du sollst wollen, dass mehr Einsen", g("pe_a05_gesicht_konzentration"), "S1",
          src=REKON),
        s("Ohne Knopf, ohne Berührung.", g("pe_a06_hand_am_tisch"), "S1", src=REKON),
        s("Du sitzt still.", g("pe_d04_uhr_wand"), "S1", src=REKON),
        s("Dann zählt die Maschine aus.", g("pe_a07_zaehler_laeuft"), "S1", src=REKON),
        s("Die Abweichung ist winzig.", g("pe_a09_kurve_millimeter"), "S1", src=REKON),
        s("So klein, dass sie in einem einzelnen", g("pe_a08_papierstreifen"), "S1",
          src=REKON),
        s("Also machst du es noch einmal.", SKOP89, "S1", "Analogoszilloskop, 1989", PD_DOE),
        s("Und irgendwann sind es Millionen", mo("abweichung"), "S1", kind="VIDEO"),
        s("und die Abweichung zeigt immer noch", g("pe_a10_ausdruckstapel"), "S1",
          src=REKON),
        s("Dieser Raum lag im Keller", EQUAD, "S1",
          "Engineering Quadrangle, Princeton", CCBY4),
        s("Er war achtundzwanzig Jahre lang", g("pe_a11_kellerflur"), "S1", src=REKON),
        s("Geleitet hat ihn der Dekan", g("pe_a13_schreibtisch_dekan"), "S1", src=REKON),
        s("Wie kommt so etwas an eine Universität", GATE, "S1",
          "FitzRandolph Gate, Princeton", CCBY4),
        s("Und warum haben die Leute", g("pe_a12_tuer_keller"), "S1", src=REKON),

        # ======================================================= S2 Der Mann
        s("Der Mann heißt Robert Jahn.", g("pe_b01_jahn_portraet"), "S2",
          "Robert G. Jahn", REKON),
        s("In seinem Fach hatte er einen Namen", g("pe_b02_jahn_schreibtisch"), "S2",
          src=REKON),
        s("Jahn war Ingenieur für Antriebstechnik.", JAHN_TANK, "S2",
          "Jahns Vakuumkammer, Princeton 1966", NASA66),
        s("Elektrische Triebwerke für Raumfahrzeuge", JAHN_HORN, "S2",
          "Elektrodenkopf mit Mikrowellenhorn, 1966", NASA66),
        s("das Standardwerk auf diesem Gebiet", g("pe_b05_buchruecken"), "S2", src=REKON),
        s("Er hat für die NASA gearbeitet", JAHN_INTER, "S2",
          "Mikrowelleninterferometer, 1966", NASA66),
        s("und ab neunzehnhunderteinundsiebzig", NASSAU, "S2",
          "Nassau Hall, Princeton", CCBY4),
        s("Wer in Princeton Dekan", g("pe_b06_fakultaetssitzung"), "S2", src=REKON),
        s("entscheidet über Berufungen", g("pe_a13_schreibtisch_dekan"), "S2", src=REKON),
        s("Jahn hatte diesen Posten fünfzehn Jahre.", BLAIR, "S2",
          "Blair Arch, Princeton", CCBY4),
        s("Später beschreibt er selbst", JAHN_SONDE, "S2",
          "Feldsondenaufbau, Princeton 1966", NASA66),
        s("Dekan, Professor für Raumfahrttechnik", HOF1, "S2",
          "Hof des Engineering Quadrangle", CCBYSA4),
        s("Das ist der Punkt, an dem die Geschichte", g("pe_b09_hoersaal_leer"), "S2",
          src=REKON),
        s("Denn zwischen siebenundsiebzig", g("pe_b07_studentenarbeit"), "S2", src=REKON),
        s("Ob menschliche Aufmerksamkeit", g("pe_b08_notizbuch_offen"), "S2", src=REKON),
        s("Wer diese Arbeit geschrieben hat", g("pe_b12_vereinbarung_blatt"), "S2",
          src=REKON),
        s("Jahn nennt in seinen eigenen Aufsätzen", JAHN_SIGNAT, "S2",
          "Jahns Unterschrift, Princeton 1966", NASA66),
        s("Er sieht sich die Zahlen an", g("pe_b14_jahn_entscheidung"), "S2", src=REKON),
        s("Neunzehnhundertneunundsiebzig richtet er", g("pe_a01_keller_weit"), "S2",
          src=REKON),
        s("Princeton Engineering Anomalies Research.", HOF2, "S2",
          "Engineering Quadrangle, Princeton", CCBYSA4),
        s("Die Laborleitung übernimmt Brenda Dunne", g("pe_b10_dunne_portraet"), "S2",
          "Brenda J. Dunne", REKON),
        s("Sie bleibt bis zum letzten Tag.", g("pe_b11_dunne_am_ordner"), "S2", src=REKON),
        s("Und die Universität lässt ihn machen.", g("pe_b03_vakuumkammer"), "S2",
          src=REKON),
        s("kein Geld von Princeton", g("pe_a11_kellerflur"), "S2", src=REKON),
        s("Das heißt, wer hier mitarbeitet", g("pe_b04_triebwerk_pruefstand"), "S2", src=REKON),
        s("Dunne wird es später auf eine Formel", g("pe_b13_efeu_backstein"), "S2",
          src=REKON),

        # ==================================================== S3 Die Maschine
        s("Und dann bauen sie Maschinen.", g("pe_c01_werkbank"), "S3", src=REKON),
        s("Das Herzstück ist eine Kiste", g("pe_c06_kiste_offen"), "S3", src=REKON),
        s("Es gibt sie auf Papier", pt("frontpage"), "S3",
          "Titelblatt US 5.830.064", PATENT),
        s("Auf dem Titelblatt stehen die Namen", pt("sheet02"), "S3",
          "Erfinder: Dunne, Jahn, Nelson", PATENT),
        s("Als Anmelder ist eine Firma eingetragen", c("PE_CARD_PATENT"), "S3"),
        s("Und darin steht, wie das Ding funktioniert.", pt("sheet04"), "S3",
          "Figur 4: der Signalweg", PATENT),
        s("Am Anfang steht eine Rauschdiode.", ZENER, "S3",
          "Zenerdiode, Bauform der Zeit", CCBYSA4),
        s("Ein Bauteil, das von sich aus zittert.", g("pe_c03_rauschdiode"), "S3",
          src=REKON),
        s("Dieses Zittern ist echter physikalischer", mo("rauschen"), "S3", kind="VIDEO"),
        s("man kann es nicht vorausberechnen", SKOP77, "S3",
          "Analogoszilloskop, 1977", CCBYSA3),
        s("Das Rauschen wird verstärkt", pt("sheet13"), "S3",
          "Figur 8A: der Analogteil", PATENT),
        s("Liegt es darüber, ist das Ergebnis eine Eins.",
          g("pe_c04_oszilloskop_rauschen"), "S3", src=REKON),
        s("Dahinter sitzt eine Schaltung", pt("sheet14"), "S3",
          "Figur 8B: die Digitalstufe", PATENT),
        s("Das klingt nach einer Kleinigkeit", g("pe_c02_platine_makro"), "S3", src=REKON),
        s("Sie bügelt aus, wenn die Elektronik", g("pe_c05_schaltung_zeichnung"), "S3",
          src=REKON),
        s("Am Ende kommen Nullen und Einsen", LOCHBAND, "S3",
          "Gelochtes Mylarband, um 1979", CCBYSA3),
        s("und ein Zähler addiert sie.", LOCHSTANZER, "S3",
          "Lochstreifenstanzer und -leser", CCBYSA4),
        s("Ein Versuch sind zweihundert Würfe.", c("PE_CARD_MASSE"), "S3"),
        s("Tausend davon ergeben eine Serie", LOCHROLLEN, "S3",
          "Lochbandrollen", CCBY2),
        s("Das Labor selbst beschreibt es so", g("pe_c08_geraet_reihe"), "S3", src=REKON),
        s("Es sei im Grunde, als würfe man", mo("muenzwurf"), "S3", kind="VIDEO"),
        s("Erwartungswert: die Hälfte.", g("pe_c09_patent_mappe"), "S3", src=REKON),

        # ===================================================== S4 Der Ablauf
        s("Und der Ablauf im Labor ist immer gleich.", g("pe_d01_labor_weit"), "S4",
          src=REKON),
        s("Der Teilnehmer setzt sich davor", g("pe_d02_sitzung_seitlich"), "S4",
          src=REKON),
        s("und legt vorher fest, was er will.", g("pe_d03_zettel_absicht"), "S4",
          src=REKON),
        s("Mehr Einsen.", c("PE_CARD_MUSTER"), "S4"),
        s("Diese dritte Bedingung ist die wichtigste.", g("pe_d12_stuhl_leer_labor"), "S4",
          src=REKON),
        s("Wenn die Maschine auch ohne Absicht", g("pe_c08_geraet_reihe"), "S4",
          src=REKON),
        s("Dann sitzt der Mensch da.", g("pe_d10_kopfhoerer_tisch"), "S4", src=REKON),
        s("Es gibt keine Anleitung.", g("pe_d04_uhr_wand"), "S4", src=REKON),
        s("Manche sagen, sie hätten sich angestrengt.",
          g("pe_a05_gesicht_konzentration"), "S4", src=REKON),
        s("Das Labor notiert das mit", g("pe_d11_protokollbuch"), "S4", src=REKON),
        s("Über die Jahre kommen andere Apparate", g("pe_d08_pendel_quarz"), "S4",
          src=REKON),
        s("Ein Springbrunnen.", g("pe_d09_springbrunnen"), "S4", src=REKON),
        s("Der eindrucksvollste Aufbau", g("pe_d05_kugelwand_weit"), "S4", src=REKON),
        s("Oben werden neuntausend Polystyrolkugeln", g("pe_b16_dunne_kugelwand"), "S4",
          src=REKON),
        s("Sie fallen durch ein Raster", g("pe_d06_kugeln_fallen"), "S4", src=REKON),
        s("und sammeln sich unten in neunzehn Fächern.", g("pe_d07_faecher_unten"), "S4",
          src=REKON),
        s("Ein Durchgang dauert etwa zwölf Minuten.", c("PE_CARD_KASKADE"), "S4"),
        s("Was dabei entsteht, ist eine Glockenkurve.", GALTON, "S4",
          "Galton-Brett, vorher und nachher", CCBYSA4),
        s("Dieselbe Kurve, die in jedem Statistiklehrbuch", GALTON2, "S4",
          "Galton-Brett", CCBYSA4),
        s("Die Aufgabe für den Teilnehmer", mo("kaskade"), "S4", kind="VIDEO"),
        s("Nach links oder nach rechts.", pt("sheet12"), "S4", "Figur 7C: das Verfahren in vier Schritten", PATENT),
        s("Mit nichts als Aufmerksamkeit.", g("pe_c07_kabel_bundel"), "S4",
          src=REKON),

        # ======================================================= S5 Die Zahl
        s("Und dann kommt der Teil", g("pe_e05_sandkorn"), "S5", src=REKON),
        s("Über alle Jahre und alle Versuche", g("pe_e03_null_eins_strom"), "S5",
          src=REKON),
        s("Stell dir zehntausend Münzwürfe vor.", g("pe_e02_muenzen_flug"), "S5",
          src=REKON),
        s("Erwartet werden fünftausend Mal Kopf.", c("PE_CARD_FRAGE"), "S5"),
        s("Das ist der ganze Effekt.", g("pe_e04_waage_zunge"), "S5", src=REKON),
        s("Erst wenn man Millionen von Durchgängen", g("pe_e01_linie_steigt"), "S5",
          src=REKON),

        # ===================================================== S6 Die Kritik
        s("Genau darüber ist jahrzehntelang", g("pe_f01_endlospapier_boden"), "S6",
          src=REKON),
        s("Und der Streit ist berechtigt.", g("pe_f04_fenster_regen"), "S6", src=REKON),
        s("Wo ein Effekt so klein ist", AUSDRUCK78, "S6",
          "Gebundener Zeilendrucker-Ausdruck, 1978", CCBYSA3),
        s("Wann hört man auf zu messen?", DRUCKER, "S6",
          "Zeilendrucker CDC 501", CCBYSA3),
        s("Wer wertet aus?", g("pe_f06_person_am_stapel"), "S6", src=REKON),
        s("Was passiert mit Serien", DRUCKWALZE, "S6",
          "Druckwalze eines Zeilendruckers", CCBYSA3),
        s("Wer lange genug misst", g("pe_f03_zwei_stapel"), "S6", src=REKON),
        s("Genau deshalb legt man in der Wissenschaft", pt("sheet03"), "S6",
          src=REKON),
        s("Ein Effekt von einem Bit auf zehntausend", g("pe_f08_taschenrechner"), "S6",
          src=REKON),
        s("Kritiker haben genau da angesetzt.", g("pe_f07_einzelner_stuhl_reihe"), "S6",
          src=REKON),
        s("Dort taucht eine Versuchsperson auf", g("pe_d12_stuhl_leer_labor"), "S6",
          src=REKON),
        s("Zwölf Jahre.", pt("sheet09"), "S6", "Figur 6C: die Auswertekette", PATENT),
        s("Vierzehn Millionen Durchgänge", g("pe_a10_ausdruckstapel"), "S6", src=REKON),
        s("Und nach einer Analyse", pt("sheet19"), "S6",
          "Figur 15A: kumulierte Abweichung", PATENT),
        s("Wer das war, hat das Labor nie offengelegt.",
          pt("sheet05"), "S6", "Figur 5A: der Datenweg", PATENT),
        s("Was denkst du bis hier?", c("PE_CARD_COMMENT"), "S6"),

        # ====================================================== S7 Die Probe
        s("Denn jetzt kommt die Stelle", g("pe_g10_labor_weiterarbeit"), "S7", src=REKON),
        s("Das Labor hat sich selbst überprüfen lassen.", c("PE_CARD_PROBE"), "S7"),
        s("Ende der Neunziger schließt PEAR sich", IGPP, "S7",
          "Institut für Grenzgebiete der Psychologie, Freiburg", CCBYSA3),
        s("Freiburg und Gießen.", GIESSEN, "S7",
          "Justus-Liebig-Universität Gießen", CCBYSA4),
        s("Und sie machen es diesmal anders.", g("pe_g04_protokoll_unterschrift"), "S7",
          src=REKON),
        s("Alles wird vorher festgelegt.", IGPP_SCHILD, "S7",
          "Institut für Grenzgebiete der Psychologie, Freiburg", CCBYSA3),
        s("Wie viele Durchgänge.", pt("sheet06"), "S7", "Figur 5B: die Ablaufsteuerung", PATENT),
        s("Alle drei Labore benutzen dasselbe Gerät", g("pe_g03_drei_geraete"), "S7",
          src=REKON),
        s("Das ist der Versuch, den Kritiker", GIESSEN2, "S7",
          "Philosophikum I, Gießen", CCBYSA3),
        s("Und PEAR macht ihn mit.", g("pe_g05_versand_kiste"), "S7", src=REKON),
        s("Dann laufen die Maschinen.", g("pe_g01_institut_freiburg"), "S7", src=REKON),
        s("Und der Effekt ist nicht da.", g("pe_g08_flaches_ergebnis"), "S7", src=REKON),
        s("Die Abweichungen gehen in allen drei", g("pe_g07_zwei_kurven"), "S7",
          src=REKON),
        s("Aber sie sind zu klein.", pt("sheet20"), "S7",
          "Figur 15B: kumulierte Abweichung", PATENT),
        s("Jahn und Dunne schreiben das später", g("pe_g09_veroeffentlichung"), "S7",
          src=REKON),
        s("Die Ausschläge hätten die Größe", c("PE_CARD_ZWEI_ERGEBNISSE"), "S7"),
        s("An anderer Stelle steht es noch schärfer", g("pe_g06_telefonat_nacht"), "S7",
          src=REKON),
        s("Geschrieben von denen", g("pe_g02_labor_deutsch"), "S7", src=REKON),
        s("Und dann arbeiten sie weiter.", pt("sheet07"), "S7",
          src=REKON),

        # ==================================================== S8 Was bleibt
        s("Sieben Jahre später ist Schluss.", g("pe_h01_kisten_packen"), "S8", src=REKON),
        s("Zweitausendsieben ist Schluss.", g("pe_b15_jahn_alt"), "S8",
          "Robert G. Jahn", REKON),
        s("Jahn sagt dazu einen Satz", g("pe_h04_datentraeger"), "S8", src=REKON),
        s("Achtundzwanzig Jahre lang hätten sie getan", g("pe_h02_leerer_raum"), "S8",
          src=REKON),
        s("Robert Jahn stirbt zweitausendsiebzehn.", g("pe_h06_grabstein_schlicht"), "S8",
          src=REKON),
        s("Was bleibt von achtundzwanzig Jahren?", c("PE_CARD_SCHLUSSSTAND"), "S8"),
        s("Die Maschinen gab es.", g("pe_c06_kiste_offen"), "S8", src=REKON),
        s("Die Patentschrift liegt öffentlich aus", pt("sheet01"), "S8",
          "Figur 1: Gesamtaufbau", PATENT),
        s("mit den Namen auf dem Titelblatt.", pt("sheet22"), "S8",
          "Titelblatt US 5.830.064", PATENT),
        s("Die Daten gibt es.", AUSDRUCK78, "S8", "Gebundener Zeilendrucker-Ausdruck, 1978", CCBYSA3),
        s("Millionen von Durchgängen", LOCHROLLEN, "S8",
          "Lochbandrollen", CCBY2),
        s("Und es gibt eine Wiederholung", pt("sheet21"), "S8",
          "Figur 15C: kumulierte Abweichung", PATENT),
        s("Auch die ist veröffentlicht", pt("sheet23"), "S8", "Figur 17: die Datenerfassung", PATENT),
        s("Damit ist die Sache für die meisten", pt("sheet24"), "S8", "Figur 18: die Aufzeichnung", PATENT),
        s("Eine Frage bleibt trotzdem.", g("pe_h07_schreibtisch_leer"), "S8", src=REKON),
        s("Warum hängt ein Mann", JAHN_SIGNAT, "S8",
          "Jahns Unterschrift, Princeton 1966", NASA66),
        s("Und warum lässt eine Universität", EQUAD, "S8",
          "Engineering Quadrangle, Princeton", CCBY4),
        s("Und ob wir gerade dabei sind", g("pe_h03_archivkarton"), "S8", src=REKON),
        s("Mit besserer Elektronik", pt("sheet08"), "S8",
          "Figur 6B: die Anordnung", PATENT),
        s("Denn das Prinzip lebt weiter.", TRNG, "S8", "Hardware-Zufallsgenerator, heutige Bauform", CCBY4),
        s("In einem Netz aus Zufallsgeneratoren", g("pe_h08_netz_weltkarte"), "S8",
          src=REKON),
        s("das seit neunzehnhundertachtundneunzig", g("pe_h10_generator_heute"), "S8",
          src=REKON),
        s("Sie nennen es Global Consciousness Project.", g("pe_h09_serverraum_klein"), "S8",
          src=REKON),
        s("Das ist die nächste Folge.", g("pe_h05_fenster_abend"), "S8", src=REKON),
    ]

def prepare():
    """GIF-Zeichnung und Patentseiten in verwendbare PNG bringen.

    ffmpeg zieht aus dem einbildigen GIF das Standbild; die Patentseiten
    kommen mit PyMuPDF bei 200 dpi heraus, damit die Schrift bei 1080p noch
    Struktur hat.
    """
    DOCS.mkdir(parents=True, exist_ok=True)
    gif = ROOT.joinpath(*DL, "WIKIMEDIA_COMMONS", "KZ_WC_04_PATENT_APPARATUS_1992.gif")
    ziel = DOCS / "KZ_PATENT_APPARATUS_1992.png"
    if not ziel.exists():
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(gif),
             "-frames:v", "1", str(ziel)])
        print(f"  {ziel.name}")
    import fitz
    pdf = ROOT.joinpath(*DL, "K04_RU2122446C1_patent_AMBER.pdf")
    doc = fitz.open(pdf)
    for i in range(doc.page_count):
        ziel = DOCS / f"KZ_PATENT_SEITE_{i + 1:02d}.png"
        if ziel.exists():
            continue
        pix = doc[i].get_pixmap(dpi=200)
        pix.save(ziel)
        print(f"  {ziel.name}  {pix.width}x{pix.height}")
    doc.close()


# --------------------------------------------------------------- Timeline

def build_timeline(vorab=False):
    """vorab=True: Timeline schon bauen, waehrend noch Motive erzeugt werden.

    Die Shotgrenzen haengen ausschliesslich am Alignment, nicht an den
    Bilddateien — die Timeline ist also bereits endgueltig, sobald der
    Sprechtext steht. Fehlende Motive sind durchweg 16:9 aus der eigenen
    Erzeugung; ihr Seitenverhaeltnis ist damit bekannt. So laufen die
    Segmente der fertigen Motive schon, waehrend der Rest noch entsteht.
    """
    data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    text, chars = data["source_text"], data["characters"]
    sh = shots()
    cursor, starts = 0, []
    for i, shot in enumerate(sh):
        pos = text.find(shot["anchor"], cursor)
        if pos < 0:
            raise RuntimeError(f"Anker nicht gefunden ab {cursor}: {shot['anchor']!r}")
        first = next(k for k in range(pos, pos + len(shot["anchor"])) if not text[k].isspace())
        starts.append(0.0 if i == 0 else float(chars[first]["start"]))
        cursor = pos + len(shot["anchor"])
    total = dur(VOICE)
    rows = []
    for i, (shot, start) in enumerate(zip(sh, starts), 1):
        end = starts[i] if i < len(starts) else total
        if end - start < 0.35:
            raise RuntimeError(f"Shot zu kurz bei {i}: {end - start:.3f}s · {shot['anchor']!r}")
        p = Path(shot["visual"])
        if not p.is_file():
            if not vorab:
                raise FileNotFoundError(p)
            aspect = 16 / 9              # eigene Erzeugung, immer 16:9
        elif shot["kind"] == "VIDEO":
            aspect = 16 / 9              # Bewegtbild entsteht nativ in 1920x1080
        else:
            with Image.open(p) as im:
                aspect = im.width / im.height
        row = dict(shot)
        row.update({"shot_id": f"SPG_{i:03d}", "start": round(start, 3),
                    "end": round(end, 3), "duration": round(end - start, 3),
                    "aspect": round(aspect, 3), "contain": not (1.62 <= aspect <= 1.95)})
        rows.append(row)
    for i, r in enumerate(rows):
        r["scene_first"] = i == 0 or rows[i - 1]["scene"] != r["scene"]
        r["scene_last"] = i == len(rows) - 1 or rows[i + 1]["scene"] != r["scene"]
    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gl = sum(1 for r in rows if r["gloss"] or r["src"])
    print(f"Timeline: {len(rows)} Shots / {total:.2f}s / "
          f"Ø {total / len(rows):.2f}s · {gl} mit Einblendung · "
          f"{len({r['visual'] for r in rows})} Einzelbilder")
    return rows


# ------------------------------------------------------------------ Bild

def camera_filter(index, row):
    """Ken Burns, ueberabgetastet und mit gedaempften Enden.

    Zwei Fehler steckten hier vorher drin, beide sichtbar als Zappeln:

    1. `zoompan` bekam ein Bild in Ausgabegroesse. Seine x- und y-Werte sind
       ganzzahlig, ein Schritt war also ein voller Ausgabepixel — die Fahrt
       lief in Stufen. Das Bild wird jetzt auf 7680x4320 gebracht, bevor
       `zoompan` daraufsieht; ein ganzzahliger Schritt ist damit ein Viertel
       Ausgabepixel. Gemessen an der Streuung der Bilddifferenzen von Bild zu
       Bild: 0,26 vorher, 0,05 jetzt. Kosten: rund 15 Prozent Rechenzeit,
       weil ohnehin die grosse Vorlage dekodiert wird.

    2. Die Strecke war fuer jeden Shot gleich, die Dauer nicht. Ein Shot von
       einer Sekunde bekam denselben Zoom wie einer von acht — bei kurzen
       Shots wurde daraus ein Ruck. Die Strecke haengt jetzt an der Dauer
       (`tempo`), die Geschwindigkeit bleibt ueber die Folge gleich.

    Ueberabtastung allein reicht nicht ueberall. Bei einer langsamen Fahrt
    betraegt der Schritt je Bild weniger als einen Ausgabepixel; die Rundung
    macht daraus abwechselnd zwei und drei Eingangspixel, und das sieht man.
    Feiner rechnen hilft nur begrenzt — gemessen an einem der langsamsten
    Shots: 0,40 bei 7680, 0,24 bei 11520, 0,17 bei 15360, bei jedesmal
    deutlich mehr Rechenzeit.

    Deshalb wird die Fahrt zusaetzlich in vier Zwischenschritten je
    Ausgabebild gerechnet und gemittelt (`tmix`). Die vier Positionen runden
    unterschiedlich, ihr Mittel bewegt sich in Vierteln — derselbe Shot
    liegt damit bei 0,089 statt 0,400, also auf dem Wert einer sauberen
    Fahrt. Nebenbei entsteht die Bewegungsunschaerfe, die eine Kamera
    ohnehin hat.

    Bewegtbild laeuft ohne das: es bringt eigene Bewegung mit, bekommt nur
    eine ruhige Fahrt aus der Mitte und liegt damit schon beim Wert des
    Clips selbst.

    Dazu laufen die Enden weich an und aus: 60 Prozent linear, 40 Prozent
    Smoothstep. Die Spitzengeschwindigkeit liegt damit bei 1,2 statt 1,5 des
    Mittels — genug, dass Anfang und Ende nicht schlagen, zu wenig, dass es
    in der Mitte zieht.
    """
    sub = 1 if row["kind"] == "VIDEO" else SUB
    frames = max(1, math.ceil(row["duration"] * FPS)) * sub

    # Ueberabtastung: Basis, auf der zoompan rechnet. Bewegtbild bringt
    # eigene Bewegung mit und liegt ohnehin nur in 1920 vor — dort reicht
    # die Haelfte und spart die Haelfte der Rechenzeit.
    SW, SH = (5760, 3240) if row["kind"] == "VIDEO" else (7680, 4320)
    fg_w, fg_h = (SW * 1844) // 1920, (SH * 984) // 1080
    kante = max(6, SW // 320)

    if row.get("contain"):
        # Der Grund war eine unscharfe Kopie der Vorlage, nur abgedunkelt.
        # Bei Patentseiten ist die Vorlage flaechig cremefarben — der Grund
        # wurde damit zu einem flachen Grau, das zwei Drittel des Bildes
        # einnimmt und nichts erzaehlt. Er wird jetzt zusaetzlich ins
        # Nachtblau der Folge gezogen und randseitig abgedunkelt, und das
        # Blatt bekommt eine schmale warme Kante, damit es aufliegt statt
        # zu schweben.
        base = (
            f"split=2[bg][fg];"
            f"[bg]scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH},"
            f"gblur=sigma={SW // 37},eq=brightness=-0.66:saturation=0.28:contrast=0.82,"
            f"colorbalance=bs=0.22:bm=0.10:rs=-0.06,"
            f"vignette=angle=PI/4.2[b];"
            f"[fg]scale={fg_w}:{fg_h}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=iw+{kante * 2}:ih+{kante * 2}:{kante}:{kante}:0x2E2418[f];"
            f"[b][f]overlay=(W-w)/2:(H-h)/2"
        )
    else:
        base = (f"scale={SW}:{SH}:force_original_aspect_ratio=increase,"
                f"crop={SW}:{SH}")

    # Weiche Enden: 60 % linear, 40 % Smoothstep
    lin = f"(on/{frames})"
    p = f"(0.6*{lin}+0.4*({lin}*{lin}*(3-2*{lin})))"

    # Strecke nach Dauer. 3,6 s ist der Mittelwert der Folge und bekommt die
    # volle Strecke; kuerzere Shots weniger, laengere mehr.
    tempo = min(1.55, max(0.50, row["duration"] / 3.6))

    mitte_x, mitte_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"

    # Ueber die volle Breite hinaus gibt es nichts zu fahren — zoompan
    # klemmt x sonst am Rand fest und die Fahrt bleibt mitten im Shot stehen.
    tempo_quer = min(1.0, tempo)

    def quer(weg, rueckwaerts=False):
        """Mittige Fahrt ueber `weg`, Laenge nach tempo."""
        a = 0.5 - tempo_quer / 2 if not rueckwaerts else 0.5 + tempo_quer / 2
        b = tempo_quer if not rueckwaerts else -tempo_quer
        return f"{weg}*({a:.4f}+{b:.4f}*{p})"

    rechts, unten = "(iw-iw/zoom)", "(ih-ih/zoom)"

    if row.get("contain"):
        # Eingepasste Vorlagen: sanfter, sonst wandert die Beschriftung raus
        paare = [(1.000, 0.050), (1.050, -0.050)]
        z0, dz = paare[index % len(paare)]
        z1 = z0 + dz * tempo
        x, y = mitte_x, mitte_y
    else:
        # Zoom und echte Fahrt im Wechsel. Ein reiner Zoom liest sich auf
        # dunklen, weichen Motiven kaum; die Fahrt wird gesehen.
        bewegungen = [
            (1.03, 0.15, mitte_x, mitte_y),                 # Hineinfahren
            (1.18, -0.15, mitte_x, mitte_y),                # Herausfahren
            (1.14, 0.0, quer(rechts), mitte_y),             # Schwenk rechts
            (1.14, 0.0, quer(rechts, True), mitte_y),       # Schwenk links
            (1.13, 0.0, mitte_x, quer(unten, True)),        # Fahrt nach oben
            (1.05, 0.13, quer(rechts), quer(unten)),        # diagonal hinein
            (1.17, -0.11, quer(rechts, True), mitte_y),     # Schwenk und heraus
            (1.13, 0.0, mitte_x, quer(unten)),              # Fahrt nach unten
        ]
        if row["kind"] == "VIDEO":
            # Bewegtbild bewegt sich schon. Ein Schwenk obendrauf legt zwei
            # Bewegungen uebereinander, und die Summe wirkt unruhig — hier
            # nur eine ruhige Fahrt aus der Mitte.
            z0, dz = (1.02, 0.07) if index % 2 == 0 else (1.09, -0.07)
            x, y = mitte_x, mitte_y
        else:
            z0, dz, x, y = bewegungen[index % len(bewegungen)]
        z1 = z0 + dz * tempo

    # Unter 1.0 zeigt zoompan neben dem Bild schwarz, ueber 1.30 wird aus der
    # Fahrt ein Ausschnitt.
    z1 = min(1.30, max(1.005, z1))

    zexpr = f"{z0:.4f}+({z1 - z0:.4f})*{p}"
    # Bei einem Standbild lief die Skalierung auf 7680 fuer jedes einzelne
    # Eingangsbild — bei vier Zwischenschritten also 120-mal je Sekunde
    # dasselbe Ergebnis. Der loop-Filter haelt das fertig skalierte Bild und
    # gibt es aus; die Skalierung laeuft genau einmal. Gemessen am selben
    # Segment: 175 s statt 308 s.
    einmal = (f",loop=loop=-1:size=1:start=0,fps={FPS * sub}"
              if row["kind"] != "VIDEO" else "")
    mittel = (f",tmix=frames={sub}:weights='{' '.join('1' * sub)}',fps={FPS}"
              if sub > 1 else "")
    f = (base + einmal
         + f",zoompan=z='{zexpr}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS * sub}"
         + mittel
         + ",eq=contrast=1.03:saturation=1.04,unsharp=5:5:.24:5:5:0,scale=w=iw:h=ih:in_range=auto:out_range=tv,format=yuv420p")
    if row.get("scene_first"):
        f += f",fade=t=in:st=0:d=0.35:color={GRUND}"
    if row.get("scene_last"):
        f += (f",fade=t=out:st={max(0, row['duration'] - 0.35):.3f}:d=0.35:color={GRUND}")
    return f


def ass_time(v):
    cs = round(v * 100)
    h, r = divmod(cs, 360000)
    m, r = divmod(r, 6000)
    sec, cs = divmod(r, 100)
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def graphics(rows):
    """Deutsche Beschriftung plus Quellzeile, unten links (§ 4).

    Farben im ASS-Format &HAABBGGRR: Beschriftung in Aluminium hell
    (F0E8D2), Quellzeile in Polarlichtgruen (3FD9A0), Kasten in Nachtblau.
    """
    path = PROD / "render" / f"{NAME}_graphics.ass"
    path.parent.mkdir(parents=True, exist_ok=True)
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Gloss,Arial,44,&H00D2E8F0,&H0,&HC828140A,&HC828140A,-1,0,0,0,100,100,0,0,3,14,0,1,86,420,132,1
Style: Src,Arial,25,&H00A0D93F,&H0,&HC828140A,&HC828140A,0,0,0,0,100,100,1,0,3,10,0,1,86,420,92,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    fade = r"{\fad(220,220)}"
    out = [head]
    beschriftungen = 0
    for r in rows:
        if r["duration"] < 1.6 or not r["gloss"]:
            continue
        st = ass_time(r["start"] + 0.20)
        en = ass_time(max(r["start"] + 0.9, r["end"] - 0.18))
        out.append(f"Dialogue: 0,{st},{en},Gloss,,0,0,0,,{fade}{r['gloss']}\n")
        beschriftungen += 1

    # Quellzeilen: gleiche Zeile ueber mehrere Shots hinweg zusammenfassen.
    # Fast jedes Motiv dieser Folge ist eine Rekonstruktion; einzeln gesetzt
    # blendet dasselbe Wort ueber Minuten im Sekundentakt aus und wieder ein.
    # Als ein durchgehender Eintrag steht es ruhig und liegt trotzdem auf
    # jedem Shot, den es kennzeichnen muss.
    laeufe, quellen = [], 0
    for r in rows:
        if r["duration"] < 1.6 or not r["src"]:
            continue
        quellen += 1
        if laeufe and laeufe[-1][2] == r["src"] and abs(laeufe[-1][1] - r["start"]) < 0.9:
            laeufe[-1][1] = r["end"]
        else:
            laeufe.append([r["start"], r["end"], r["src"]])
    for start, end, quelle in laeufe:
        st = ass_time(start + 0.20)
        en = ass_time(max(start + 0.9, end - 0.18))
        out.append(f"Dialogue: 0,{st},{en},Src,,0,0,0,,{fade}{quelle}\n")

    path.write_text("".join(out), encoding="utf-8-sig")
    print(f"Grafikspur: {beschriftungen} Beschriftungen, "
          f"{quellen} Quellzeilen in {len(laeufe)} Läufen")
    return path


def render(force=False, limit=None, teilweise=False):
    rows = json.loads(TIMELINE.read_text(encoding="utf-8"))
    todo = rows[:limit] if limit else rows
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    offen = 0

    # Die Segmente haengen nicht voneinander ab, also laufen mehrere
    # nebeneinander. Ein einzelner Lauf nutzt im Filterteil rund anderthalb
    # Kerne — gemessen 29,5 Prozent von sechs. Serienbetrieb liess also vier
    # Kerne stehen. Ein Drittel der Kerne bleibt als Luft fuer das System.
    arbeiter = max(1, min(4, (os.cpu_count() or 4) // 2 + 1))

    aufgaben = []
    for i, row in enumerate(todo):
        target = SEGMENTS / f"{i + 1:03d}_{row['shot_id']}.mp4"
        if teilweise and not Path(row["visual"]).is_file():
            offen += 1
            continue
        if target.exists() and not force:
            try:
                dur(target)
                continue
            except RuntimeError:
                print(f"  {target.name} beschaedigt, wird neu gebaut")
                target.unlink()
        aufgaben.append((i, row, target))

    def bauen(auftrag):
        i, row, target = auftrag
        inputs = (["-stream_loop", "-1", "-i", row["visual"]] if row["kind"] == "VIDEO"
                  else ["-i", row["visual"]])
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
             "-sws_flags", "lanczos+accurate_rnd+full_chroma_int",
             "-t", f"{row['duration']:.3f}", "-vf", camera_filter(i, row),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(target)])
        return i, row

    if aufgaben:
        print(f"  {len(aufgaben)} Segmente, {arbeiter} parallel", flush=True)
        fertig = 0
        with cf.ThreadPoolExecutor(max_workers=arbeiter) as pool:
            for i, row in pool.map(bauen, aufgaben):
                fertig += 1
                print(f"  {fertig:03d}/{len(aufgaben):03d} {row['shot_id']} "
                      f"{row['duration']:5.2f}s · {row['anchor'][:38]}", flush=True)
    if teilweise:
        print(f"  {len(todo) - offen} Segmente fertig, {offen} warten noch auf ihr Motiv")
        return
    if limit:
        return
    endcard = SEGMENTS / "999_ENDCARD.mp4"
    if not endcard.exists() or force:
        print("  Endcard")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-loop", "1", "-framerate", str(FPS), "-i", str(CARDS / "PE_ENDCARD.png"),
             "-t", f"{ENDCARD_SEC:.3f}",
             "-sws_flags", "lanczos+accurate_rnd+full_chroma_int",
             "-vf", ("scale=5760:3240:force_original_aspect_ratio=increase,crop=5760:3240,"
                     f"zoompan=z='1.0+0.05*(on/{int(ENDCARD_SEC * FPS)})':x='iw/2-(iw/zoom/2)'"
                     f":y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},"
                     f"fade=t=in:st=0:d=0.6:color={GRUND},"
                     f"fade=t=out:st={ENDCARD_SEC - 1.2:.2f}:d=1.2:color={GRUND},format=yuv420p"),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(endcard)])

    concat = PROD / "render" / "concat.txt"
    paths = [SEGMENTS / f"{i + 1:03d}_{r['shot_id']}.mp4" for i, r in enumerate(rows)] + [endcard]
    for p in paths:
        dur(p)                                  # jedes Segment lesbar? sonst Abbruch
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in paths) + "\n",
                      encoding="utf-8")
    picture = PROD / "render" / f"{NAME}_picture_lock.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c", "copy", str(picture)])

    ass = graphics(rows)
    assf = "ass='" + str(ass).replace("\\", "/").replace(":", r"\:") + "'"
    FINAL.mkdir(parents=True, exist_ok=True)
    out = FINAL / f"{NAME}_FINAL_1080p.mp4"
    mix = AUDIO / f"{NAME}_final_mix.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(picture), "-i", str(mix),
         "-vf", assf + ",scale=w=iw:h=ih:in_range=auto:out_range=tv"
                      ",format=yuv420p",
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", str(out)])
    print(f"Fertig: {out}")


# ------------------------------------------------------------------ Audio

def build_audio():
    AUDIO.mkdir(parents=True, exist_ok=True)
    voice_len = dur(VOICE)
    total = voice_len + ENDCARD_SEC

    grenzen = aktgrenzen()
    teile = []
    for i, wert in enumerate(KURVE):
        a0 = grenzen[i]
        if i < len(KURVE) - 1:
            teile.append(f"{wert}*between(t,{a0:.2f},{grenzen[i + 1]:.2f})")
        else:
            teile.append(f"{wert}*gt(t,{a0:.2f})")
    env = "+".join(teile)
    print("  Intensitaetskurve: " + " ".join(f"{w:.2f}@{grenzen[i]:.0f}s"
                                             for i, w in enumerate(KURVE)))

    low = (f"aevalsrc='0.075*sin(2*PI*49*t)+0.030*sin(2*PI*73.42*t+0.25*sin(2*PI*t/37))"
           f"|0.075*sin(2*PI*49.3*t)+0.030*sin(2*PI*73.42*t+0.25*sin(2*PI*t/43))'"
           f":s=48000:d={total}")
    mid = (f"aevalsrc='0.030*sin(2*PI*880*t)*(0.5+0.5*sin(2*PI*t/23))"
           f"+0.022*sin(2*PI*1174.7*t)*(0.5+0.5*sin(2*PI*t/31))"
           f"|0.030*sin(2*PI*880.6*t)*(0.5+0.5*sin(2*PI*t/29))"
           f"+0.022*sin(2*PI*1318.5*t)*(0.5+0.5*sin(2*PI*t/19))':s=48000:d={total}")
    noise = f"anoisesrc=color=pink:amplitude=.030:r=48000:d={total}"

    raw = AUDIO / f"{NAME}_bed_raw.wav"
    bed = AUDIO / f"{NAME}_bed_-30LUFS.wav"
    fc = (
        "[0:a]lowpass=f=520,aecho=.8:.45:900|2100:.05|.02[lo];"
        "[1:a]highpass=f=700,lowpass=f=2600,aecho=.7:.5:1700|3300:.16|.09,"
        "volume=0.55[mi];"
        "[2:a]highpass=f=300,lowpass=f=4200,volume=.12[n];"
        "[lo][mi][n]amix=inputs=3:weights='1 0.62 0.20':normalize=0,"
        f"volume='{env}':eval=frame,"
        f"afade=t=in:st=0:d=3,afade=t=out:st={total - 4:.2f}:d=4,"
        "alimiter=limit=0.9[out]"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", low, "-f", "lavfi", "-i", mid, "-f", "lavfi", "-i", noise,
         "-filter_complex", fc, "-map", "[out]", "-ac", "2", "-ar", "48000",
         "-c:a", "pcm_s24le", str(raw)])

    st = loudness(raw, -30.0, -6.0)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
         "-af", (f"loudnorm=I=-30:TP=-6:LRA=7:measured_I={st['input_i']}:"
                 f"measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:"
                 f"measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true"),
         "-ac", "2", "-ar", "48000", "-c:a", "pcm_s24le", str(bed)])

    premix = AUDIO / f"{NAME}_premix.wav"
    final = AUDIO / f"{NAME}_final_mix.wav"
    mixf = (
        f"[0:a]apad=pad_dur={ENDCARD_SEC},atrim=0:{total},pan=stereo|c0=c0|c1=c0,"
        "asplit=2[vox][key];"
        "[1:a][key]sidechaincompress=threshold=0.03:ratio=8:attack=25:release=520[duck];"
        "[vox][duck]amix=inputs=2:weights='1 1':normalize=0,alimiter=limit=0.94[out]"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VOICE), "-i", str(bed), "-filter_complex", mixf,
         "-map", "[out]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s24le", str(premix)])

    st = loudness(premix)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(premix),
         "-af", (f"loudnorm=I=-14:TP=-1:LRA=7:measured_I={st['input_i']}:"
                 f"measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:"
                 f"measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true"),
         "-ac", "2", "-ar", "48000", "-c:a", "pcm_s24le", str(final)])
    v = loudness(final)
    rep = {"duration": round(total, 3), "voice_seconds": round(voice_len, 3),
           "endcard_seconds": ENDCARD_SEC, "final_verify": v,
           "aktgrenzen": [round(x, 2) for x in grenzen], "kurve": KURVE,
           "bed": "Eigensynthese, Anteil ueber 620 Hz, acht Intensitaetsstufen",
           "rights": "Original procedural synthesis; no samples."}
    (AUDIO / "audio_mix_report.json").write_text(json.dumps(rep, indent=2) + "\n",
                                                 encoding="utf-8")
    print(f"Audio: {total:.2f}s · {v['input_i']} LUFS · TP {v['input_tp']}")


# ------------------------------------------------------------------- SRT

def srt_time(v: float) -> str:
    ms = round(v * 1000)
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    sec, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def captions():
    import re
    data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    text, chars = data["source_text"], data["characters"]
    spans = []
    for m in re.finditer(r"[^.!?\n]+[.!?]*", text):
        satz = m.group().strip()
        if not satz:
            continue
        try:
            first = next(i for i in range(m.start(), m.end()) if not text[i].isspace())
            last = next(i for i in range(m.end() - 1, m.start() - 1, -1) if not text[i].isspace())
        except StopIteration:
            continue
        start, end = float(chars[first]["start"]), float(chars[last]["end"])
        # Rekursiv teilen, bis jeder Block unter 84 Zeichen liegt. Eine
        # einzelne Halbierung reicht bei sehr langen Saetzen nicht — in der
        # ersten Fassung blieb genau ein Block mit 88 Zeichen stehen.
        def teile(t0, t1, s0, roh):
            if len(roh) <= 84:
                spans.append((t0, t1, roh))
                return
            woerter = roh.split()
            mitte = len(woerter) // 2
            links = " ".join(woerter[:mitte])
            rechts = " ".join(woerter[mitte:])
            cut = text.find(links, s0) + len(links)
            tcut = float(chars[min(cut, len(chars) - 1)]["end"])
            teile(t0, tcut, s0, links)
            teile(tcut, t1, text.find(rechts, cut), rechts)

        teile(start, end, m.start(), satz)
    lines = []
    for i, (x, y, t) in enumerate(spans, 1):
        lines += [str(i), f"{srt_time(x)} --> {srt_time(y)}", t, ""]
    (PROD / "captions").mkdir(parents=True, exist_ok=True)
    (PROD / "captions" / f"{NAME}_de.srt").write_text("\n".join(lines), encoding="utf-8-sig")
    lang = sum(1 for _, _, t in spans if len(t) > 84)
    print(f"Untertitel: {len(spans)} Bloecke, {lang} ueber 84 Zeichen")


# -------------------------------------------------------------------- QA

def qa():
    video = FINAL / f"{NAME}_FINAL_1080p.mp4"
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                            "-of", "json", str(video)], True))
    vs = next(x for x in probe["streams"] if x["codec_type"] == "video")
    au = next(x for x in probe["streams"] if x["codec_type"] == "audio")
    rows = json.loads(TIMELINE.read_text(encoding="utf-8"))
    dd = float(probe["format"]["duration"])
    loud = loudness(video)
    expect = dur(VOICE) + ENDCARD_SEC
    einzel = len({r["visual"] for r in rows})
    import collections
    zaehler = collections.Counter(r["visual"] for r in rows)
    checks = {
        "1080p": vs.get("width") == 1920 and vs.get("height") == 1080,
        "h264_yuv420p": vs.get("codec_name") == "h264" and vs.get("pix_fmt") == "yuv420p",
        "aac_48k_stereo": (au.get("codec_name") == "aac" and au.get("sample_rate") == "48000"
                           and au.get("channels") == 2),
        "30fps": vs.get("r_frame_rate") == "30/1",
        "dauer_stimmt": abs(dd - expect) < 0.5,
        "endcard_vorhanden": dd > dur(VOICE) + ENDCARD_SEC - 1.0,
        "shots_145_155": 145 <= len(rows) <= 155,
        "einzelbilder_85": einzel >= 85,
        "wiederholung_max4": max(zaehler.values()) <= 4,
        "einblendungen": sum(1 for r in rows if r["gloss"] or r["src"]) >= 60,
        "loudness": abs(float(loud["input_i"]) + 14) <= 0.5,
        "peak": float(loud["input_tp"]) <= -0.8,
    }
    rep = {"file": str(video.resolve()),
           "sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
           "duration": dd, "shots": len(rows) + 1,
           "average_shot_seconds": round(dur(VOICE) / len(rows), 2),
           "glosses": sum(1 for r in rows if r["gloss"]),
           "source_labels": sum(1 for r in rows if r["src"]),
           "unique_visuals": einzel, "max_repeat": max(zaehler.values()),
           "video": vs, "audio": au, "loudness": loud, "checks": checks}
    (FINAL / f"{NAME}_QA.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video),
         "-vf", "fps=1/30,scale=384:216,tile=5x4", "-frames:v", "1", "-q:v", "2",
         str(FINAL / f"{NAME}_CONTACT_SHEET.jpg")])
    print(json.dumps({k: v for k, v in rep.items()
                      if k in ("duration", "shots", "average_shot_seconds", "glosses",
                               "source_labels", "unique_visuals", "max_repeat", "checks")},
                     indent=2, ensure_ascii=False))
    if not all(checks.values()):
        raise RuntimeError("QA fehlgeschlagen: " + ", ".join(k for k, v in checks.items() if not v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["prepare", "timeline", "audio", "render",
                                        "captions", "qa", "all"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--vorab", action="store_true",
                    help="Timeline und Segmente bauen, solange Motive fehlen")
    args = ap.parse_args()
    if args.command in ("prepare", "all"):
        prepare()
    if args.command in ("timeline", "all"):
        build_timeline(args.vorab)
    if args.command in ("audio", "all"):
        build_audio()
    if args.command in ("render", "all"):
        render(args.force, args.limit, args.vorab)
    if args.command in ("captions", "all"):
        captions()
    if args.command in ("qa", "all") and not args.limit and not args.vorab:
        qa()


if __name__ == "__main__":
    main()
