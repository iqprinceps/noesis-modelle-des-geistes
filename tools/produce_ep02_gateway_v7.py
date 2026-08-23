#!/usr/bin/env python3
"""Gateway V6 — optimierte Fassung.

Aenderungen gegenueber V5:

1. Alle drei Pexels-Stockclips entfernt (Kettlebell-Mann, Nachtclub,
   Netzwerk-Loop) — 10 Shots, 49 s. Ersetzt durch die ungenutzten
   AI_FINAL-Rekonstruktionen und neue editorische Karten.
2. Drei-Beobachter-Bild korrigiert (V5 hatte zweimal "OBSERVER 1: PAST").
3. Deutsche Einblendung plus Quellenzeile auf jedem Dokumentshot.
4. PRISMA-Flussdiagramm entfernt (unlesbar), durch lesbare Karte ersetzt.
5. DISA-Luftbild nicht mehr unter "Archiv der CIA"; Kontextfotos mit Jahr.
6. Vollbild statt Pad — V5 liess bis zu 69 Prozent der Flaeche schwarz.
7. Ken Burns von ~1,5 auf ~6 Prozent, Blende an jeder Szenengrenze.
8. Musikbett mit Anteil ueber 620 Hz und drei Intensitaetsstufen.
9. 20 s Endcard mit Zuschauerfrage und Verweis auf EP01.

Die Voice bleibt unveraendert. Alle Shotgrenzen haengen weiter an den
Wortzeitstempeln aus dem V2-Alignment, deshalb bleibt die Synchronisation
exakt erhalten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V7"
V5 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V5"
V2 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2"
V1 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY"

ALIGNMENT = PROD / "voice" / "alignment" / "EP02_GATEWAY_V7_alignment.json"
VOICE = PROD / "audio" / "EP02V7_voice_-18LUFS.wav"
MASTER = PROD / "voice" / "master" / "EP02_GATEWAY_V7_VO_MASTER.wav"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN_V7.txt"

TIMELINE = PROD / "timeline" / "EP02_GATEWAY_V7_timeline.json"
SEGMENTS = PROD / "render" / "segments"
FINAL = PROD / "render" / "final"
AUDIO = PROD / "audio"
CARDS6 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V6" / "visuals" / "cards"

FPS = 30
ENDCARD_SEC = 20.0
NAME = "EP02_GATEWAY_V7"


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


# ----------------------------------------------------------------- Quellen

def a(*p): return str(ROOT.joinpath(*p).resolve())
def v5(*p): return str(V5.joinpath(*p).resolve())
def v2(*p): return str(V2.joinpath(*p).resolve())
def v1(*p): return str(V1.joinpath(*p).resolve())
def c6(n): return str((V6 / "visuals" / "cards" / n).resolve())
def mo(n): return str((PROD / "motion" / n).resolve())
def v5g(n): return v5("visuals", "generated", n)
def g7(n): return str((PROD / "visuals" / "generated" / n).resolve())

ai = lambda n: a("05_GENERATED", "EP02_GATEWAY_V2", "AI_FINAL", n)
# Dokumente aus dem V6-Ordner: dort sind die eingebrannten englischen Kopf-
# und Fusszeilen entfernt (tools/gw_clean_docs.py), damit nicht oben Englisch
# und unten die neue deutsche Einblendung steht.
V6 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V6"
doc = lambda n: str((V6 / "visuals" / "documents" / n).resolve())
pat = lambda n: str((V6 / "visuals" / "documents" / n).resolve())
v5card = lambda n: v5("visuals", "cards", n)
card = lambda n: v2("visuals", "cards", n)
v2pat = lambda n: v2("visuals", "patents", n)
ex = lambda n: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "APPROVED", n)
rp = lambda n: v1("reference_package", n)

# AI-Rekonstruktionen. IMG01/05/06 lagen in V5 komplett ungenutzt herum,
# waehrend an ihrer Stelle Stockclips liefen.
AI_OBSERVERS = ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png")
AI_MONROE = ai("GWV2_IMG02_ROBERT_MONROE_PORTRAIT_RECON_16x9.png")
AI_BENTOV = ai("GWV2_IMG03_BENTOV_EDITORIAL_RECON_16x9.png")
AI_LISTEN = ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png")
AI_WHEEL = ai("GWV2_IMG05_FOCUS15_TIME_WHEEL_16x9.png")
AI_FIELD = ai("GWV2_IMG06_CONSCIOUSNESS_FIELD_MODEL_16x9.png")
AI_BARRIER = ai("GWV2_IMG07_NONCORPOREAL_BARRIER_CLAIM_16x9.png")

REPORT = "U.S. Army Gateway Report · 9. Juni 1983"
PATENT = "US-Patent 5.213.562 · Robert A. Monroe · 1993"
REVIEW = "Systematischer Review 2023 · Open Access"
RECON = "Rekonstruktion"


def s(anchor, visual, scene, gloss="", src="", kind="STILL"):
    return {"anchor": anchor, "visual": visual, "scene": scene, "kind": kind,
            "gloss": gloss, "src": src}


def shots():
    return [
        # ------------------------------------------------- S1 Drei Beobachter
        s("Drei Menschen. Ein Ziel.", c6("V6_CARD_OBSERVER_PROTOCOL.png"), "S1"),
        s("Der erste beobachtet es jetzt.", AI_OBSERVERS, "S1", src=RECON),
        s("Der zweite soll dasselbe Ziel", mo("zeitrad.mp4"), "S1", kind="VIDEO"),
        s("Der dritte aus der unmittelbaren Zukunft.", v5g("gw_focus_transition.png"), "S1"),
        s("Danach werden ihre Angaben verglichen.", c6("V6_CARD_OBSERVER_PROTOCOL.png"), "S1"),
        s("Gelesen hat das kaum jemand.", rp("GW_REPORT_PDF01_HEADER.png"), "S1",
          "Absender: Department of the Army", REPORT),
        s("Es steht in einem Bericht", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", src=REPORT),
        s("Datum:", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S1",
          "9. Juni 1983, Fort George G. Meade", REPORT),
        s("Autor:", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S1",
          "Unterschrift: Wayne M. McDonnell, LTC", REPORT),
        s("Heute liegt eine freigegebene", g7("gw7_archive_shelves.png"), "S1", src=RECON),
        s("Daher kommt der berühmte Name", c6("V6_CARD_MYTH.png"), "S1"),
        s("Geschrieben wurde die Akte", ex("GW_011_Fort_Meade_entrance_2009.jpg"), "S1",
          "Fort George G. Meade", "Aufnahme 2009"),
        s("Bleibt die Frage, die wirklich zählt.", c6("V6_CARD_QUESTION.png"), "S1"),
        s("Und wie weit ist er damit gegangen?", AI_FIELD, "S1", src=RECON),
        s("Weiter, als die meisten vermuten.", doc("V4_DOC10_NONCORPOREAL_FORMS.png"), "S1",
          "Empfehlung J, Seite 27", REPORT),
        s("Auf den letzten Seiten empfiehlt er", g7("gw7_perimeter_night.png"), "S1", src=RECON),
        s("Aber der Reihe nach.", g7("gw7_mcdonnell_desk.png"), "S1", src=RECON),

        # -------------------------------------------------- S2 Die drei Männer
        s("Die Antwort beginnt mit Kopfhörern", AI_LISTEN, "S2", src=RECON),
        s("Monroe war Radiomanager.", AI_MONROE, "S2", "Robert Monroe, 1915–1995", RECON),
        s("Bis er anfing, Erfahrungen zu beschreiben", g7("gw7_monroe_first_obe.png"), "S2", src=RECON),
        s("Statt zum Arzt zu gehen", g7("gw7_monroe_console.png"), "S2", src=RECON),
        s("Am Monroe Institute in Virginia", v5g("gw_binaural_processing.png"), "S2"),
        s("Sein Markenbegriff dafür", rp("GW_PATENT_PDF01.png"), "S2",
          "Hemi-Sync, eingetragene Marke", PATENT),
        s("Wayne McDonnell bekam den Auftrag",
          doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2",
          "Lieutenant Colonel, U.S. Army Intelligence", REPORT),
        s("Praktische Verwendbarkeit.", doc("V4_DOC02_TASK_BENTOV.png"), "S2",
          "Auftrag: Mechanik und praktische Nutzbarkeit", REPORT),
        s("Auf der Titelseite steht", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S2",
          "Absender: U.S. Army Operational Group", REPORT),
        s("Für die Theorie dahinter", AI_BENTOV, "S2", "Itzhak Bentov, 1923–1979", RECON),
        s("Itzhak Bentov, geboren in der Tschechoslowakei", v2pat("BENTOV_1971-01.png"), "S2",
          src="US-Patentschrift · Itzhak Bentov, 1971"),
        s("Er war Ingenieur.", v2pat("BENTOV_1969-1.png"), "S2",
          src="US-Patentschrift · Itzhak Bentov, 1969"),
        s("Von ihm stammt der steuerbare Herzkatheter", v2pat("BENTOV_1969-2.png"), "S2",
          "Steuerbarer Herzkatheter", "US-Patentschrift · Itzhak Bentov, 1969"),
        s("Und er hatte eine zweite Obsession.", mo("resonanz.mp4"), "S2", kind="VIDEO"),
        s("Bentov war überzeugt", mo("resonanz.mp4"), "S2", kind="VIDEO"),
        s("Dass Herz und Aorta", v5g("gw_consciousness_field.png"), "S2"),
        s("Und dass Bewusstsein sich auf dieser", AI_FIELD, "S2", src=RECON),
        s("Er rechnete das durch.", v2pat("BENTOV_1971-01.png"), "S2",
          src="US-Patentschrift · Itzhak Bentov, 1971"),
        s("Er nannte es die Mechanik des Bewusstseins.", v2pat("BENTOV_1971-02.png"), "S2",
          "„Stalking the Wild Pendulum“, 1977", "Itzhak Bentov"),
        s("Am 25. Mai 1979 saß Bentov", g7("gw7_flight191_gate.png"), "S2", src=RECON),
        s("Er war auf dem Weg nach Kalifornien", mo("resonanz.mp4"), "S2", kind="VIDEO"),
        s("Kurz nach dem Start", c6("V6_CARD_FLIGHT191.png"), "S2"),
        s("Vier Jahre später wird ein Offizier", g7("gw7_mcdonnell_desk.png"), "S2", src=RECON),
        s("Monroe lieferte das Training.", c6("V6_CARD_PEOPLE.png"), "S2"),
        s("Was dabei herauskam, beginnt harmlos.", AI_LISTEN, "S2", src=RECON),

        # ------------------------------------------------------- S3 Zwei Töne
        s("Setz Kopfhörer auf.", g7("gw7_headphones_macro.png"), "S3", src=RECON),
        s("Links läuft ein Ton", mo("binaural.mp4"), "S3", kind="VIDEO"),
        s("Rechts mit 410.", mo("binaural.mp4"), "S3", kind="VIDEO"),
        s("Du hörst weder das eine", mo("binaural.mp4"), "S3", kind="VIDEO"),
        s("Etwa zehn Mal pro Sekunde.", c6("V6_CARD_HERTZ.png"), "S3"),
        s("Ein dritter Rhythmus", ex("GW_002_Exhibit_1A.png"), "S3", src=REPORT + " · Exhibit 1A"),
        s("Er entsteht erst in deinem Kopf", a("06_PRODUCTION", "Gateway_Production",
          "Assets_Research_Luna", "GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S3",
          "Binaural gegen monaural", "eNeuro · CC BY 4.0"),
        s("Das nennt man einen binauralen Beat.", c6("V6_CARD_BINAURAL.png"), "S3"),
        s("Genau das war Monroes Ansatzpunkt.", g7("gw7_monroe_console.png"), "S3", src=RECON),
        s("Wenn zwei Töne einen Rhythmus", ex("GW_004_Exhibit_1C.png"), "S3",
          src=REPORT + " · Exhibit 1C"),
        s("Beide Gehirnhälften auf dasselbe Muster", ex("GW_005_Exhibit_2.png"), "S3",
          src=REPORT + " · Exhibit 2"),
        s("Einen Zustand herstellen", g7("gw7_chec_booth.png"), "S3", src=RECON),
        s("Monroe hat das Verfahren später patentieren lassen.", rp("GW_PATENT_PDF01.png"), "S3",
          "Binaurale Beats und EEG-Muster", PATENT),
        s("US-Patent, erteilt 1993", rp("GW_PATENT_PDF02.png"), "S3", "Erteilt 1993", PATENT),
        s("Schwarz auf weiß, mit Aktenzeichen.", rp("GW_PATENT_PDF03.png"), "S3", src=PATENT),
        s("Bis hierhin ist alles nachvollziehbar.", c6("V6_CARD_EVIDENCE.png"), "S3"),
        s("Dann macht die Akte einen Sprung", mo("feld.mp4"), "S3", kind="VIDEO"),

        # ------------------------------------------------------ S4 Der Sprung
        s("McDonnell geht es um die größere Frage.", ex("GW_007_Exhibit_4A.png"), "S4",
          src=REPORT + " · Exhibit 4A"),
        s("Wie kann Bewusstsein den Körper verlassen?", g7("gw7_obe_ceiling.png"), "S4", src=RECON),
        s("Und er baut dafür eine Maschine aus Begriffen.", c6("V6_CARD_WORLD_MODEL.png"), "S4"),
        s("Der Körper schwingt", mo("resonanz.mp4"), "S4", kind="VIDEO"),
        s("Das Gehirn erzeugt elektrische Muster", ex("GW_004_Exhibit_1C.png"), "S4",
          src=REPORT + " · Exhibit 1C"),
        s("Synchronisierung macht diese Muster", mo("feld.mp4"), "S4", kind="VIDEO"),
        s("verbindet sich mit einem größeren", ex("GW_010_Exhibit_5.png"), "S4",
          src=REPORT + " · Exhibit 5"),
        s("Einem Feld, in dem Raum und Zeit", v5g("gw_time_wheel.png"), "S4"),
        s("Die Diagramme dazu sehen aus wie Maschinenbau.", ex("GW_008_Exhibit_4B.png"), "S4",
          src=REPORT + " · Exhibit 4B"),
        s("Wirbel.", ex("GW_009_Exhibit_4C.png"), "S4", src=REPORT + " · Exhibit 4C"),
        s("Torusformen.", ex("GW_006_Exhibit_3.png"), "S4", src=REPORT + " · Exhibit 3"),
        s("Verschachtelte Systeme", ex("GW_003_Exhibit_1B.png"), "S4",
          src=REPORT + " · Exhibit 1B"),
        s("Und das alles steht in einem Dokument", g7("gw7_report_stack.png"), "S4", src=RECON),
        
        s("der Unterschrift eines Nachrichtendienstoffiziers", rp("GW_REPORT_PDF02_SIGNATURE.png"), "S4",
          "Rang, Name, Unterschrift", REPORT),
        s("Und dieser Offizier zeichnet jetzt eine Landkarte.", c6("V6_CARD_FOCUS.png"), "S4"),

        # ------------------------------------------------------- S5 Die Stufen
        s("Sie heißt Focus Levels.", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S5", src=REPORT),
        s("Nummerierte Zustände.", c6("V6_CARD_FOCUS.png"), "S5"),
        s("Focus 10: der Geist wach", doc("V5_DOC_FOCUS15_FULL.png"), "S5",
          "Focus 10: Geist wach, Körper schläft", REPORT),
        s("Focus 12: die Aufmerksamkeit weitet sich", v5g("gw_focus_transition.png"), "S5"),
        s("Und dann steht in der Akte eine Überschrift", doc("V4_DOC04_FOCUS15_HEADING.png"), "S5",
          "„Travel into the Past“ · Reise in die Vergangenheit", REPORT + " · Seite 24"),
        s("Focus 15. Travel into the Past.", AI_WHEEL, "S5", src=RECON),
        s("Zeit, schreibt McDonnell, soll man sich", mo("zeitrad.mp4"), "S5", kind="VIDEO"),
        s("Die Nabe ist der Punkt", mo("zeitrad.mp4"), "S5", kind="VIDEO"),
        s("Die Speichen führen nach außen", AI_WHEEL, "S5", src=RECON),
        s("Wer Focus 15 erreicht", g7("gw7_obe_ceiling.png"), "S5", src=RECON),
        s("Er fügt hinzu:", doc("V4_DOC05_LESS_THAN_FIVE_PERCENT.png"), "S5",
          "Weniger als fünf Prozent erreichen diesen Zustand", REPORT),
        s("Fünf Prozent.", c6("V6_CARD_FIVE_PERCENT.png"), "S5"),
        s("Bei fünf, so die Akte, schon.", g7("gw7_empty_chair.png"), "S5", src=RECON),
        s("Die nächste Überschrift lautet Focus 21.", doc("V4_DOC06_FOCUS21_FUTURE.png"), "S5",
          "„The Future“ · Die Zukunft", REPORT + " · Seite 24"),
        s("Direkt darunter beginnt der Abschnitt", doc("V5_DOC_OBE_FULL.png"), "S5",
          "Abschnitt 31: Der außerkörperliche Zustand", REPORT),
        s("Und der Bericht wird handfest.", doc("V4_DOC07_OBE_NO_GUARANTEE.png"), "S5", src=REPORT),
        s("Aus dem Körper rollen.", g7("gw7_monroe_first_obe.png"), "S5", src=RECON),
        s("Sich nach oben lösen.", g7("gw7_empty_chair.png"), "S5", src=RECON),
        s("Anweisungen, wie in einem Handbuch.", doc("V5_DOC_OBE_FULL.png"), "S5", src=REPORT),
        s("Wenn du an diesem Punkt denkst", c6("V6_CARD_COMMENT.png"), "S5"),

        # ----------------------------------------------------- S6 Zehn Ziffern
        s("Denn irgendwann stellt McDonnell die Frage", g7("gw7_typewriter_page.png"), "S6", src=RECON),
        s("Kann man damit etwas herausfinden?", doc("V5_DOC_INFO_COLLECTION_TOP.png"), "S6",
          "Abschnitt 33: Informationsgewinnung", REPORT + " · Seite 25"),
        s("Und in der Akte steht ein Versuch.", g7("gw7_ten_digits.png"), "S6", src=RECON),
        s("Ein Computer erzeugt zehn Ziffern.", doc("V5_DOC_TEN_DIGITS.png"), "S6",
          "Zehn computererzeugte Ziffern", REPORT),
        s("Die Zahlen liegen an einem anderen Ort.", g7("gw7_ten_digits.png"), "S6", src=RECON),
        s("Niemand im Raum kennt sie.", g7("gw7_three_stations.png"), "S6", src=RECON),
        s("Die Teilnehmer sollen sie", g7("gw7_chec_booth.png"), "S6", src=RECON),
        s("Das Ergebnis ist der merkwürdigste Satz", g7("gw7_ten_digits.png"), "S6", src=RECON),
        s("Manche, schreibt McDonnell, trafen genug Ziffern", c6("V6_CARD_DIGITS.png"), "S6"),
        s("Alle zehn bekam niemand.", doc("V5_DOC_TEN_DIGITS.png"), "S6", src=REPORT),
        s("Halte kurz an dieser Stelle.", g7("gw7_ten_digits.png"), "S6", src=RECON),
        s("Ein sauberer Volltreffer wäre eine gute Geschichte.", c6("V6_CARD_EVIDENCE.png"), "S6"),
        s("Was McDonnell beschreibt, ist etwas anderes.", v5g("gw_evidence_gap.png"), "S6"),
        s("Und schlecht genug, um nichts zu beweisen.", g7("gw7_report_stack.png"), "S6", src=RECON),
        s("Er nennt auch den Grund", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6",
          "Abschnitt 33: Verzerrung", REPORT),
        s("Verzerrung.", c6("V6_CARD_DISTORTION.png"), "S6"),
        s("Im außerkörperlichen Zustand, schreibt er", mo("feld.mp4"), "S6", kind="VIDEO"),
        s("Der Beobachter weiß nicht", v5g("gw_test_consciousness.png"), "S6"),
        s("Und gegen dieses eine Problem", doc("V5_DOC_RECOMMENDATION_H_FULL.png"), "S6",
          "Empfehlung H im vollen Wortlaut", REPORT + " · Seite 27"),

        # ---------------------------------------------------- S7 Empfehlung H
        s("Drei Personen. Dasselbe Ziel.", c6("V6_CARD_OBSERVER_PROTOCOL.png"), "S7"),
        s("Eine beobachtet in normaler Raum-Zeit.", g7("gw7_three_stations.png"), "S7", src=RECON),
        s("Eine in Focus 15", AI_WHEEL, "S7", src=RECON),
        s("Eine in Focus 21", v5g("gw_focus_transition.png"), "S7"),
        s("Danach werden alle drei Berichte verglichen.", doc("V4_DOC09_RECOMMENDATION_H.png"),
          "S7", src=REPORT),
        s("Was übereinstimmt, ist das Ziel.", g7("gw7_three_stations.png"), "S7", src=RECON),
        s("Das ist Empfehlung H.", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S7",
          src=REPORT + " · Seite 27"),
        s("Und die Liste geht weiter.", doc("V5_DOC_RECOMMENDATION_JK.png"), "S7", src=REPORT),
        s("Empfehlung J:", doc("V4_DOC10_NONCORPOREAL_FORMS.png"), "S7",
          "„intelligent, non-corporal energy forms“", REPORT + " · Seite 27"),
        s("Aufgeführt als Einsatzrisiko", AI_BARRIER, "S7", src=RECON),
        
        s("Empfehlung K:", doc("V4_DOC11_HOLOGRAPHIC_BARRIER.png"), "S7",
          "Holografische Muster um sensible Anlagen", REPORT + " · Seite 27"),
        s("um unerwünschte außerkörperliche Präsenzen", v5g("gw_holographic_barrier.png"), "S7"),
        s("Lies das noch einmal.", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S7", src=REPORT),
        s("Ein Offizier der US Army empfiehlt", g7("gw7_typewriter_page.png"), "S7", src=RECON),
        s("Gegen Eindringlinge, die keinen Körper haben.", g7("gw7_perimeter_night.png"), "S7", src=RECON),
        s("Was hier steht, ist eine Verteidigungsdoktrin", c6("V6_CARD_STATUS.png"), "S7"),

        # ------------------------------------------------------ S8 Was bleibt
        s("Vierzig Jahre später lässt sich davon", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S8", src=REVIEW),
        s("Der Ton.", g7("gw7_headphones_macro.png"), "S8", src=RECON),
        s("Ob zwei leicht verschiedene Töne", mo("binaural.mp4"), "S8", kind="VIDEO"),
        s("Eine Meta-Analyse von 2019", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S8",
          "Meta-Analyse 2019: 22 Studien, moderater Effekt", "Meta-Analyse 2019 · Open Access"),
        s("Ein Review von 2023 fragte enger", c6("V6_CARD_STUDIES.png"), "S8"),
        s("Fünf Studien dafür, acht dagegen.", a("06_PRODUCTION", "Gateway_Production",
          "Assets_Research_Luna", "GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S8",
          src="eNeuro · CC BY 4.0"),
        s("Der Ton ist damit vermessen.", c6("V6_CARD_EVIDENCE.png"), "S8"),
        s("Denn zwischen einem veränderten Zustand", v5g("gw_evidence_gap.png"), "S8"),
        s("Was bleibt, ist die Akte selbst.", rp("GW_REPORT_PDF27_CONCLUSION_A_G.png"), "S8",
          "Schlussfolgerungen A–G", REPORT + " · Seite 27"),
        s("Der Bericht ist echt.", g7("gw7_report_stack.png"), "S8", src=RECON),
        s("Die Focus Levels stehen darin.", c6("V6_CARD_FOCUS.png"), "S8"),
        s("Travel into the Past steht darin.", doc("V4_DOC04_FOCUS15_HEADING.png"), "S8", src=REPORT),
        s("Die zehn Ziffern stehen darin.", doc("V5_DOC_TEN_DIGITS.png"), "S8", src=REPORT),
        s("Die nicht-körperlichen Intelligenzen stehen darin.",
          g7("gw7_corridor_night.png"), "S8", src=RECON),
        s("Die virale Kurzfassung lautet:", c6("V6_CARD_MYTH.png"), "S8"),
        s("Die tatsächliche Geschichte ist seltsamer.", g7("gw7_mcdonnell_desk.png"), "S8", src=RECON),
        s("las die Arbeit eines Mannes", g7("gw7_flight191_gate.png"), "S8", src=RECON),
        s("und hielt das Ganze für ernst genug", doc("V5_DOC_RECOMMENDATION_H_FULL.png"), "S8",
          src=REPORT),
        
        s("Der Fund ist diese Seite.", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S8",
          "Der Fund ist diese Seite", REPORT + " · Seite 27"),
    ]


# --------------------------------------------------------------- Timeline

def build_timeline():
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
            raise RuntimeError(f"Shot zu kurz bei {i}: {end - start:.3f}s")
        p = Path(shot["visual"])
        if not p.is_file():
            raise FileNotFoundError(p)
        if shot["kind"] == "VIDEO":
            aspect = 16 / 9          # die Bewegtbilder entstehen nativ in 1920x1080
        else:
            with Image.open(p) as im:
                aspect = im.width / im.height
        # Alles, was merklich vom 16:9-Format abweicht, darf nicht beschnitten
        # werden — in beide Richtungen. Patentseiten (0.68) verlieren sonst
        # ueber die Haelfte der Hoehe, die breiten Originaldiagramme des
        # Berichts (bis 2.70) bis zu 34 Prozent der Breite. Nur echte Fotos
        # und die 16:9-Vorlagen werden formatfuellend beschnitten.
        row = dict(shot)
        row.update({"shot_id": f"GWV7_{i:03d}", "start": round(start, 3),
                    "end": round(end, 3), "duration": round(end - start, 3),
                    "aspect": round(aspect, 3), "contain": not (1.62 <= aspect <= 1.95)})
        rows.append(row)
    # Szenengrenzen markieren
    for i, r in enumerate(rows):
        r["scene_first"] = i == 0 or rows[i - 1]["scene"] != r["scene"]
        r["scene_last"] = i == len(rows) - 1 or rows[i + 1]["scene"] != r["scene"]
    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gl = sum(1 for r in rows if r["gloss"] or r["src"])
    print(f"Timeline: {len(rows)} Shots / {total:.2f}s / Ø {total/len(rows):.2f}s · {gl} mit Einblendung")
    return rows


# ------------------------------------------------------------------ Bild

def camera_filter(index, row):
    """Vollbild statt Pad. V5 liess bis zu 69 Prozent der Flaeche schwarz.

    Quellen, die vom 16:9-Format abweichen, duerfen dabei nicht beschnitten
    werden — bei 1530x1980 blieben sonst nur 43 Prozent der Seite stehen, bei
    Exhibit 1C (2.70) nur 66 Prozent der Breite. Sie werden vollstaendig
    eingepasst;
    den Rand fuellt eine unscharfe, abgedunkelte Kopie derselben Vorlage statt
    schwarzer Balken.
    """
    frames = max(1, math.ceil(row["duration"] * FPS))
    if row.get("contain"):
        base = (
            "split=2[bg][fg];"
            "[bg]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            "gblur=sigma=44,eq=brightness=-0.62:saturation=0.42:contrast=0.88[b];"
            # In beide Richtungen einpassen: nur die Hoehe zu skalieren liesse
            # Exhibit 1C (AR 2.70) mit 2689 px Breite wieder ueberlaufen.
            "[fg]scale=1856:996:force_original_aspect_ratio=decrease:flags=lanczos[f];"
            "[b][f]overlay=(W-w)/2:(H-h)/2"
        )
    else:
        base = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
    # Eingepasste Vorlagen bekommen nur eine sehr leichte Fahrt: bei 6 Prozent
    # Zoom wuerden Rand und Beschriftung der Diagramme wieder wegwandern.
    inc = 0.00018 if row.get("contain") else 0.00045   # V5: 0.00011, unsichtbar
    cap = 1.045 if row.get("contain") else 1.12
    d = index % 4
    if d == 0:
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif d == 1:
        x, y = f"(iw-iw/zoom)*on/{frames}", "ih/2-(ih/zoom/2)"
    elif d == 2:
        x, y = "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*on/{frames}"
    else:
        x, y = f"(iw-iw/zoom)*(1-on/{frames})", "ih/2-(ih/zoom/2)"
    f = (base + f",zoompan=z='min(zoom+{inc},{cap})':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS}"
         ",eq=contrast=1.03:saturation=.93,unsharp=5:5:.24:5:5:0,format=yuv420p")
    # Blende an jeder Szenengrenze — ersetzt die in V5 voellig fehlenden
    # Uebergaenge zwischen den acht Akten.
    if row.get("scene_first"):
        f += ",fade=t=in:st=0:d=0.35:color=#041114"
    if row.get("scene_last"):
        f += f",fade=t=out:st={max(0, row['duration'] - 0.35):.3f}:d=0.35:color=#041114"
    return f


def ass_time(v):
    cs = round(v * 100); h, r = divmod(cs, 360000); m, r = divmod(r, 6000); sec, cs = divmod(r, 100)
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"


def graphics(rows):
    """Deutsche Einblendung plus Quellenzeile — in V5 war das komplett leer."""
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
Style: Gloss,Arial,44,&H00E0EBEE,&H0,&HC8140A04,&HC8140A04,-1,0,0,0,100,100,0,0,3,14,0,1,86,420,132,1
Style: Src,Arial,25,&H00D3D25B,&H0,&HC8140A04,&HC8140A04,0,0,0,0,100,100,1,0,3,10,0,1,86,420,92,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    out = [head]
    for r in rows:
        if r["duration"] < 1.6:
            continue                      # zu kurz zum Lesen
        st = ass_time(r["start"] + 0.20)
        en = ass_time(max(r["start"] + 0.9, r["end"] - 0.18))
        fade = r"{\fad(220,220)}"
        if r["gloss"]:
            out.append(f"Dialogue: 0,{st},{en},Gloss,,0,0,0,,{fade}{r['gloss']}\n")
        if r["src"]:
            out.append(f"Dialogue: 0,{st},{en},Src,,0,0,0,,{fade}{r['src']}\n")
    path.write_text("".join(out), encoding="utf-8-sig")
    print(f"Grafikspur: {len(out) - 1} Einblendungen")
    return path


def render(force=False, limit=None):
    rows = json.loads(TIMELINE.read_text(encoding="utf-8"))
    todo = rows[:limit] if limit else rows
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    for i, row in enumerate(todo):
        target = SEGMENTS / f"{i+1:03d}_{row['shot_id']}.mp4"
        # Nur ueberspringen, wenn das Segment auch wirklich lesbar ist. Ein
        # abgebrochener Lauf hinterlaesst sonst eine halb geschriebene Datei,
        # die der Concat stillschweigend auslaesst.
        if target.exists() and not force:
            try:
                dur(target)
                continue
            except RuntimeError:
                print(f"  {target.name} beschaedigt, wird neu gebaut")
                target.unlink()
        print(f"  {i+1:03d}/{len(todo):03d} {row['shot_id']} {row['duration']:5.2f}s · {row['anchor'][:38]}", flush=True)
        inputs = (["-stream_loop", "-1", "-i", row["visual"]] if row["kind"] == "VIDEO"
                  else ["-loop", "1", "-framerate", str(FPS), "-i", row["visual"]])
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
             "-t", f"{row['duration']:.3f}", "-vf", camera_filter(i, row),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(target)])
    if limit:
        return
    # Endcard
    endcard = SEGMENTS / "999_ENDCARD.mp4"
    if not endcard.exists() or force:
        print("  Endcard")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-loop", "1", "-framerate", str(FPS), "-i", str(CARDS6 / "V6_ENDCARD.png"),
             "-t", f"{ENDCARD_SEC:.3f}",
             "-vf", ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
                     f"zoompan=z='min(zoom+0.00016,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                     f":d=1:s=1920x1080:fps={FPS},fade=t=in:st=0:d=0.6:color=#041114,"
                     f"fade=t=out:st={ENDCARD_SEC-1.2:.2f}:d=1.2:color=#041114,format=yuv420p"),
             "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(endcard)])

    concat = PROD / "render" / "concat.txt"
    paths = [SEGMENTS / f"{i+1:03d}_{r['shot_id']}.mp4" for i, r in enumerate(rows)] + [endcard]
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in paths) + "\n", encoding="utf-8")
    picture = PROD / "render" / f"{NAME}_picture_lock.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-c", "copy", str(picture)])

    ass = graphics(rows)
    assf = "ass='" + str(ass).replace("\\", "/").replace(":", r"\:") + "'"
    FINAL.mkdir(parents=True, exist_ok=True)
    out = FINAL / f"{NAME}_FINAL_1080p.mp4"
    mix = AUDIO / "EP02V7_final_mix.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(picture), "-i", str(mix), "-vf", assf,
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
         "-movflags", "+faststart", "-shortest", str(out)])
    print(f"Fertig: {out}")


# ------------------------------------------------------------------ Audio

def build_audio():
    """Neues Bett: Anteil ueber 620 Hz und drei Intensitaetsstufen.

    V5: lowpass 620 Hz, -33 LUFS, LRA 0.00 — auf Handy-Lautsprechern
    vollstaendig unhoerbar und ohne jede Dramaturgie.
    """
    AUDIO.mkdir(parents=True, exist_ok=True)
    voice_len = dur(VOICE)
    total = voice_len + ENDCARD_SEC

    # Intensitaetshuellkurve: Hook an, Mittelteil zurueck, Focus-Levels und
    # Finale wieder auf. Werte in Sekunden auf der fertigen Zeitachse.
    # Kurve entlang der acht Akte. Spitze in Akt 6 und 7 — zehn Ziffern und
    # die Empfehlungen J und K sind die Stelle, an der die Folge kippt.
    env = ("0.85*between(t,0.0,58.7)"
           "+0.58*between(t,58.7,179.7)"
           "+0.70*between(t,179.7,247.6)"
           "+0.88*between(t,247.6,298.0)"
           "+0.74*between(t,298.0,383.4)"
           "+0.92*between(t,383.4,453.3)"
           "+1.00*between(t,453.3,524.0)"
           "+0.66*gt(t,524.0)")

    low = (f"aevalsrc='0.075*sin(2*PI*49*t)+0.030*sin(2*PI*73.42*t+0.25*sin(2*PI*t/37))"
           f"|0.075*sin(2*PI*49.3*t)+0.030*sin(2*PI*73.42*t+0.25*sin(2*PI*t/43))':s=48000:d={total}")
    # Harmonische Schicht im hoerbaren Band — die fehlte in V5 komplett
    mid = (f"aevalsrc='0.030*sin(2*PI*880*t)*(0.5+0.5*sin(2*PI*t/23))"
           f"+0.022*sin(2*PI*1174.7*t)*(0.5+0.5*sin(2*PI*t/31))"
           f"|0.030*sin(2*PI*880.6*t)*(0.5+0.5*sin(2*PI*t/29))"
           f"+0.022*sin(2*PI*1318.5*t)*(0.5+0.5*sin(2*PI*t/19))':s=48000:d={total}")
    noise = f"anoisesrc=color=pink:amplitude=.030:r=48000:d={total}"

    raw = AUDIO / "EP02V7_bed_raw.wav"
    bed = AUDIO / "EP02V7_bed_-30LUFS.wav"
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

    premix = AUDIO / "EP02V7_premix.wav"
    final = AUDIO / "EP02V7_final_mix.wav"
    # Labelnamen duerfen nicht wie Stream-Specifier aussehen ([v] waere Video),
    # und ein Label darf nur einmal verbraucht werden — daher asplit.
    mix = (
        f"[0:a]apad=pad_dur={ENDCARD_SEC},atrim=0:{total},pan=stereo|c0=c0|c1=c0,"
        "asplit=2[vox][key];"
        "[1:a][key]sidechaincompress=threshold=0.03:ratio=8:attack=25:release=520[duck];"
        "[vox][duck]amix=inputs=2:weights='1 1':normalize=0,alimiter=limit=0.94[out]"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(VOICE), "-i", str(bed), "-filter_complex", mix,
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
           "bed": "Eigensynthese, Anteil ueber 620 Hz, drei Intensitaetsstufen",
           "rights": "Original procedural synthesis; no samples."}
    (AUDIO / "audio_mix_report.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    print(f"Audio: {total:.2f}s · {v['input_i']} LUFS · TP {v['input_tp']}")


# ------------------------------------------------------------------- SRT

def srt_time(v: float) -> str:
    ms = round(v * 1000)
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    sec, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def captions():
    """Untertitel aus dem Alignment, satzweise, lange Saetze geteilt.

    Grenze bei 84 Zeichen: zwei Zeilen a 42 sind auf dem Handy noch lesbar.
    """
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
        if len(satz) <= 84:
            spans.append((start, end, satz))
            continue
        # zu lang: an der Wortgrenze moeglichst mittig teilen
        woerter = satz.split()
        mitte = len(woerter) // 2
        links = " ".join(woerter[:mitte])
        cut = text.find(links, m.start()) + len(links)
        tcut = float(chars[min(cut, len(chars) - 1)]["end"])
        spans.append((start, tcut, links))
        spans.append((tcut, end, " ".join(woerter[mitte:])))
    lines = []
    for i, (a, b, s) in enumerate(spans, 1):
        lines += [str(i), f"{srt_time(a)} --> {srt_time(b)}", s, ""]
    (PROD / "captions").mkdir(parents=True, exist_ok=True)
    (PROD / "captions" / f"{NAME}_de.srt").write_text("\n".join(lines), encoding="utf-8-sig")
    lang = sum(1 for _, _, s in spans if len(s) > 84)
    print(f"Untertitel: {len(spans)} Bloecke, {lang} ueber 84 Zeichen")


# -------------------------------------------------------------------- QA

def qa():
    video = FINAL / f"{NAME}_FINAL_1080p.mp4"
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                            "-of", "json", str(video)], True))
    vs = next(s for s in probe["streams"] if s["codec_type"] == "video")
    au = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    rows = json.loads(TIMELINE.read_text(encoding="utf-8"))
    d = float(probe["format"]["duration"])
    loud = loudness(video)
    expect = dur(VOICE) + ENDCARD_SEC
    checks = {
        "1080p": vs.get("width") == 1920 and vs.get("height") == 1080,
        "h264_yuv420p": vs.get("codec_name") == "h264" and vs.get("pix_fmt") == "yuv420p",
        "aac_48k_stereo": (au.get("codec_name") == "aac" and au.get("sample_rate") == "48000"
                           and au.get("channels") == 2),
        "dauer_stimmt": abs(d - expect) < 0.5,
        "endcard_vorhanden": d > dur(VOICE) + ENDCARD_SEC - 1.0,
        "keine_stockclips": not any("motion_" in r["visual"] for r in rows),
        "kein_prisma": not any("PRISMA" in r["visual"] for r in rows),
        "einblendungen": sum(1 for r in rows if r["gloss"] or r["src"]) >= 60,
        "loudness": abs(float(loud["input_i"]) + 14) <= 0.5,
        "peak": float(loud["input_tp"]) <= -0.8,
    }
    rep = {"file": str(video.resolve()),
           "sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
           "duration": d, "shots": len(rows) + 1,
           "average_shot_seconds": round(dur(VOICE) / len(rows), 2),
           "glosses": sum(1 for r in rows if r["gloss"]),
           "source_labels": sum(1 for r in rows if r["src"]),
           "unique_visuals": len({r["visual"] for r in rows}),
           "video": vs, "audio": au, "loudness": loud, "checks": checks}
    (FINAL / f"{NAME}_QA.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video),
         "-vf", "fps=1/30,scale=384:216,tile=5x4", "-frames:v", "1", "-q:v", "2",
         str(FINAL / f"{NAME}_CONTACT_SHEET.jpg")])
    print(json.dumps({k: v for k, v in rep.items()
                      if k in ("duration", "shots", "glosses", "source_labels",
                               "unique_visuals", "checks")}, indent=2, ensure_ascii=False))
    if not all(checks.values()):
        raise RuntimeError("QA fehlgeschlagen: " + ", ".join(k for k, v in checks.items() if not v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["timeline", "audio", "render", "captions", "qa", "all"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    if args.command in ("timeline", "all"):
        build_timeline()
    if args.command in ("audio", "all"):
        build_audio()
    if args.command in ("render", "all"):
        render(args.force, args.limit)
    if args.command in ("captions", "all"):
        captions()
    if args.command in ("qa", "all") and not args.limit:
        qa()


if __name__ == "__main__":
    main()
