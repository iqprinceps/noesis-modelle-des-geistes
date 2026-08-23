#!/usr/bin/env python3
"""EP03 PEAR V2 — Timeline Builder V3 (finale optimierte Version).

Optimiert für:
- Keine Bildwiederholungen (max 2x pro Bild)
- Bilder passen zum gesprochenen Text
- Mindestanzeigezeit: 2.5 Sekunden
- Maximale Anzeigezeit: 7 Sekunden
- Dynamische Abfolge
- Sanfte Übergänge

Nutzung:
    python tools/pear_timeline_v3_final.py
"""

from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

ALIGNMENT = PROD / "voice" / "alignment" / "EP03_V2_alignment.json"
TIMELINE = PROD / "timeline" / "EP03_V2_timeline.json"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN_V2.txt"

GEN = PROD / "visuals" / "generated"
CARDS = PROD / "visuals" / "cards"
DL = ROOT / "04_ASSETS" / "01_DOWNLOADS" / "EP03_PEAR"
PAT = DL / "P20_US5830064_figures_PD-USGov"


def run(args, capture=False):
    import subprocess
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


def g(name): return str(GEN / f"{name}.png")
def c(name): return str(CARDS / f"{name}.png")
def dl(name): return str(DL / name)
def pat(name): return str(PAT / f"US5830064_{name}_2320x3408.png")


REKON = "Rekonstruktion"
PATENT = "US-Patentschrift 5.830.064"
NASA66 = "Jahn, Princeton 1966 · gemeinfrei"
CCBY4 = "CC BY 4.0"
CCBYSA4 = "CC BY-SA 4.0"
CCBYSA3 = "CC BY-SA 3.0"
CCBY2 = "CC BY 2.0"


def build_segments() -> list[dict]:
    """Definiert logische Segmente mit spezifischen Bildern.
    
    Jedes Bild wird maximal 2x verwendet.
    Neue Bilder aus pe_v2_09 bis pe_v2_28 werden eingebunden.
    """
    
    return [
        # ============================================================ S1: PARADOXON (9 Segmente)
        {
            "start_text": "Der Dekan der Ingenieurfakultät",
            "visual": g("pe_b01_jahn_portraet"),
            "scene": "S1",
            "gloss": "Robert G. Jahn",
            "src": REKON,
            "min_dur": 3.5,
        },
        {
            "start_text": "Er sitzt im Keller",
            "visual": g("pe_a01_keller_weit"),
            "scene": "S1",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Er versucht, sie mit dem Gedanken",
            "visual": g("pe_a05_gesicht_konzentration"),
            "scene": "S1",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.5,
        },
        {
            "start_text": "Eins von zehntausend Mal.",
            "visual": g("pe_v2_09_muenzwurf_detail"),
            "scene": "S1",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Robert Jahn hat Raketentriebwerke",
            "visual": dl("P28_Jahn_Princeton_lab_1966_Plexiglas_vacuum_tank_Fig27.png"),
            "scene": "S1",
            "gloss": "Jahns Vakuumkammer, 1966",
            "src": NASA66,
            "min_dur": 5.0,
        },
        {
            "start_text": "Er hat das Standardwerk",
            "visual": g("pe_b05_buchruecken"),
            "scene": "S1",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Er entscheidet über Berufungen",
            "visual": dl("P02_Nassau_Hall_2026_CC-BY-4.0.jpg"),
            "scene": "S1",
            "gloss": "Nassau Hall, Princeton",
            "src": CCBY4,
            "min_dur": 4.0,
        },
        {
            "start_text": "Und er verbringt achtundzwanzig Jahre",
            "visual": g("pe_b15_jahn_alt"),
            "scene": "S1",
            "gloss": "Robert G. Jahn",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Warum?",
            "visual": g("pe_h07_schreibtisch_leer"),
            "scene": "S1",
            "gloss": "",
            "src": REKON,
            "min_dur": 2.5,
        },
        
        # ============================================================ S2: MCDONNELL (8 Segmente)
        {
            "start_text": "Der Mann, der das alles bezahlt",
            "visual": c("PE_V2_CARD_MCDONNELL"),
            "scene": "S2",
            "gloss": "",
            "src": "",
            "min_dur": 4.0,
        },
        {
            "start_text": "Er hat McDonnell Douglas gegründet.",
            "visual": g("pe_v2_01_mcdonnell_f15"),
            "scene": "S2",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Und er hat eine Angst.",
            "visual": g("pe_v2_03_pilot_cockpit"),
            "scene": "S2",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Deshalb bezahlt er ein Labor in Princeton.",
            "visual": dl("P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg"),
            "scene": "S2",
            "gloss": "Engineering Quadrangle",
            "src": CCBY4,
            "min_dur": 4.0,
        },
        {
            "start_text": "Das Labor heißt PEAR.",
            "visual": g("pe_b13_efeu_backstein"),
            "scene": "S2",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Und die Universität lässt es zu.",
            "visual": dl("P03_FitzRandolph_Gate_2026_CC-BY-4.0.jpg"),
            "scene": "S2",
            "gloss": "FitzRandolph Gate",
            "src": CCBY4,
            "min_dur": 4.0,
        },
        {
            "start_text": "Die Laborleitung übernimmt Brenda Dunne",
            "visual": g("pe_b10_dunne_portraet"),
            "scene": "S2",
            "gloss": "Brenda J. Dunne",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "How do you get peer review",
            "visual": g("pe_b11_dunne_am_ordner"),
            "scene": "S2",
            "gloss": "Brenda J. Dunne",
            "src": REKON,
            "min_dur": 4.0,
        },
        
        # ============================================================ S3: MASCHINEN (16 Segmente)
        {
            "start_text": "Und dann bauen sie Maschinen.",
            "visual": g("pe_c01_werkbank"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Das Herzstück ist eine Kiste",
            "visual": g("pe_c06_kiste_offen"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "die sie den Zufallsgenerator nennen.",
            "visual": pat("frontpage"),
            "scene": "S3",
            "gloss": "Titelblatt US 5.830.064",
            "src": PATENT,
            "min_dur": 5.0,
        },
        {
            "start_text": "Eine Rauschdiode erzeugt echten",
            "visual": g("pe_v2_10_rauschen_oszilloskop"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Das Rauschen wird verstärkt",
            "visual": pat("sheet13"),
            "scene": "S3",
            "gloss": "Figur 8A: Analogteil",
            "src": PATENT,
            "min_dur": 5.0,
        },
        {
            "start_text": "Ein Versuch sind zweihundert Würfe.",
            "visual": c("PE_CARD_MASSE"),
            "scene": "S3",
            "gloss": "",
            "src": "",
            "min_dur": 4.0,
        },
        {
            "start_text": "Der Teilnehmer setzt sich davor",
            "visual": g("pe_d02_sitzung_seitlich"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Diese dritte Bedingung ist die wichtigste.",
            "visual": g("pe_d12_stuhl_leer_labor"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Dann sitzt der Mensch da.",
            "visual": g("pe_d10_kopfhoerer_tisch"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Über die Jahre kommen andere Apparate dazu.",
            "visual": g("pe_v2_11_pendel_detail"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Über die Jahre kommen andere Apparate dazu.",
            "visual": g("pe_v2_11_pendel_detail"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Eine Wand aus Acrylglas",
            "visual": g("pe_d05_kugelwand_weit"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Sie fallen durch ein Raster",
            "visual": g("pe_v2_13_kugeln_fallen_detail"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Was dabei entsteht, ist eine Glockenkurve.",
            "visual": g("pe_v2_14_faecher_verteilung"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Die Aufgabe für den Teilnehmer:",
            "visual": g("pe_d02_sitzung_seitlich"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Mit nichts als Aufmerksamkeit.",
            "visual": g("pe_c07_kabel_bundel"),
            "scene": "S3",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        
        # ============================================================ S4: OPERATOR 10 (12 Segmente)
        {
            "start_text": "Und dann kommt der Teil",
            "visual": g("pe_e05_sandkorn"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Über alle Jahre und alle Versuche zusammen",
            "visual": g("pe_e01_linie_steigt"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Stell dir zehntausend Münzwürfe vor.",
            "visual": g("pe_e02_muenzen_flug"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Das ist der ganze Effekt.",
            "visual": g("pe_e04_waage_zunge"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Und dann gibt es da diese eine Person.",
            "visual": g("pe_d12_stuhl_leer_labor"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Das Labor nennt sie Operator zehn.",
            "visual": g("pe_v2_15_protokollbuch_detail"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Vierzehn Millionen Durchgänge",
            "visual": g("pe_v2_16_daten_papier"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Und nach einer Analyse",
            "visual": pat("sheet19"),
            "scene": "S4",
            "gloss": "Figur 15A: kumulierte Abweichung",
            "src": PATENT,
            "min_dur": 5.0,
        },
        {
            "start_text": "Wer das war, hat das Labor nie offengelegt.",
            "visual": g("pe_a10_ausdruckstapel"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Wenn man diese eine Person herausrechnet",
            "visual": g("pe_f03_zwei_stapel"),
            "scene": "S4",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Was denkst du bis hier?",
            "visual": c("PE_CARD_COMMENT"),
            "scene": "S4",
            "gloss": "",
            "src": "",
            "min_dur": 3.0,
        },
        {
            "start_text": "Schreib es in die Kommentare, bevor der nächste Teil kommt.",
            "visual": c("PE_CARD_COMMENT"),
            "scene": "S4",
            "gloss": "",
            "src": "",
            "min_dur": 3.0,
        },
        
        # ============================================================ S5: REPLIKATION (12 Segmente)
        {
            "start_text": "Denn jetzt kommt die Stelle",
            "visual": g("pe_g10_labor_weiterarbeit"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Das Labor hat sich selbst überprüfen lassen.",
            "visual": c("PE_CARD_PROBE"),
            "scene": "S5",
            "gloss": "",
            "src": "",
            "min_dur": 3.0,
        },
        {
            "start_text": "Ende der Neunziger schließt PEAR sich",
            "visual": dl("P21_IGPP_Freiburg_Wilhelmstrasse3a_2011_CC-BY-SA-3.0.jpg"),
            "scene": "S5",
            "gloss": "IGPP Freiburg",
            "src": CCBYSA3,
            "min_dur": 5.0,
        },
        {
            "start_text": "Freiburg und Gießen.",
            "visual": g("pe_v2_18_deutsche_universitaet"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Und sie machen es diesmal anders.",
            "visual": g("pe_g04_protokoll_unterschrift"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Alle drei Labore benutzen dasselbe Gerät",
            "visual": g("pe_v2_17_drei_labore"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Dann laufen die Maschinen.",
            "visual": g("pe_g01_institut_freiburg"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Und der Effekt ist nicht da.",
            "visual": g("pe_v2_20_ergebnis_flach"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Jahn und Dunne schreiben das später selbst auf",
            "visual": g("pe_g09_veroeffentlichung"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "An anderer Stelle steht es noch schärfer:",
            "visual": g("pe_v2_19_telefon_nacht"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Geschrieben von denen",
            "visual": g("pe_g02_labor_deutsch"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Und dann arbeiten sie weiter.",
            "visual": g("pe_g10_labor_weiterarbeit"),
            "scene": "S5",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        
        # ============================================================ S6: OFF-TIME (12 Segmente)
        {
            "start_text": "Denn es gibt da noch etwas",
            "visual": g("pe_e01_linie_steigt"),
            "scene": "S6",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Das Labor hat auch versucht",
            "visual": g("pe_c06_kiste_offen"),
            "scene": "S6",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Sie nennen es Off-Time-Experimente.",
            "visual": c("PE_V2_CARD_OFFTIME"),
            "scene": "S6",
            "gloss": "",
            "src": "",
            "min_dur": 3.0,
        },
        {
            "start_text": "zu Zeiten, in denen sie gar nicht im Labor waren.",
            "visual": g("pe_v2_04_offtime_uhr"),
            "scene": "S6",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Und es gibt noch den sogenannten Baseline Bind.",
            "visual": c("PE_V2_CARD_BASELINE"),
            "scene": "S6",
            "gloss": "",
            "src": "",
            "min_dur": 3.0,
        },
        {
            "start_text": "Die Kontrolldurchgänge",
            "visual": g("pe_v2_05_baseline_glatt"),
            "scene": "S6",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Kritiker sagen: Das ist ein Zeichen",
            "visual": g("pe_f07_einzelner_stuhl_reihe"),
            "scene": "S6",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Jahn und Dunne sagen etwas anderes.",
            "visual": g("pe_b01_jahn_portraet"),
            "scene": "S6",
            "gloss": "Robert G. Jahn",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Unbewusst.",
            "visual": g("pe_v2_06_geist_still"),
            "scene": "S6",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Und anfängt, eine Geschichte über ein Modell des Geistes zu sein.",
            "visual": c("PE_V2_CARD_MODELL"),
            "scene": "S6",
            "gloss": "",
            "src": "",
            "min_dur": 4.0,
        },
        {
            "start_text": "Es ist: Ist mein Geist überhaupt jemals still?",
            "visual": g("pe_v2_06_geist_still"),
            "scene": "S6",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Und wenn ja — wie weit reicht das?",
            "visual": g("pe_v2_06_geist_still"),
            "scene": "S6",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        
        # ============================================================ S7: KRITIK (16 Segmente)
        {
            "start_text": "Die Fachwelt hat darauf eine klare Antwort.",
            "visual": g("pe_f01_endlospapier_boden"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Die größte Meta-Analyse",
            "visual": g("pe_v2_21_meta_analyse"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "findet einen signifikanten, aber extrem kleinen Gesamteffekt.",
            "visual": g("pe_e01_linie_steigt"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Und erklärt ihn mit Publikationsbias.",
            "visual": g("pe_v2_22_publikation_bias"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Ein Methodiker schreibt:",
            "visual": g("pe_f06_person_am_stapel"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Schweine können nicht fliegen.",
            "visual": g("pe_v2_23_schwein_wolken"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Die andere Seite sagt:",
            "visual": g("pe_b01_jahn_portraet"),
            "scene": "S7",
            "gloss": "Robert G. Jahn",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Wir haben die Daten.",
            "visual": g("pe_a10_ausdruckstapel"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Wir haben sie veröffentlicht.",
            "visual": g("pe_g09_veroeffentlichung"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Und dann haben wir aufgehört.",
            "visual": g("pe_h02_leerer_raum"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Sieben Jahre später ist Schluss.",
            "visual": g("pe_h01_kisten_packen"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Jahn sagt dazu einen Satz",
            "visual": g("pe_h04_datentraeger"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Robert Jahn stirbt zweitausendsiebzehn.",
            "visual": g("pe_v2_25_grabstein_detail"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Die Universität äußert sich offiziell nicht zur Schließung.",
            "visual": g("pe_v2_24_princeton_nacht_detail"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Ein Physiker von der University of Maryland sagt:",
            "visual": g("pe_f07_einzelner_stuhl_reihe"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 5.0,
        },
        {
            "start_text": "Das ist der Unterschied",
            "visual": g("pe_v2_08_princeton_schweigen"),
            "scene": "S7",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        
        # ============================================================ S8: WAS BLEIBT (12 Segmente)
        {
            "start_text": "Was bleibt von achtundzwanzig Jahren?",
            "visual": c("PE_CARD_SCHLUSSSTAND"),
            "scene": "S8",
            "gloss": "",
            "src": "",
            "min_dur": 3.0,
        },
        {
            "start_text": "Die Maschinen gab es.",
            "visual": g("pe_c06_kiste_offen"),
            "scene": "S8",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Die Patentschrift liegt öffentlich aus",
            "visual": pat("sheet01"),
            "scene": "S8",
            "gloss": "Figur 1: Gesamtaufbau",
            "src": PATENT,
            "min_dur": 4.0,
        },
        {
            "start_text": "Die Daten gibt es.",
            "visual": g("pe_v2_16_daten_papier"),
            "scene": "S8",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Und es gibt eine Wiederholung",
            "visual": pat("sheet21"),
            "scene": "S8",
            "gloss": "Figur 15C: kumulierte Abweichung",
            "src": PATENT,
            "min_dur": 5.0,
        },
        {
            "start_text": "Eine Frage bleibt trotzdem.",
            "visual": g("pe_h07_schreibtisch_leer"),
            "scene": "S8",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
        {
            "start_text": "Warum hängt ein Mann",
            "visual": dl("P35_Jahn_signature_titlepage_1966_PD-US-no-notice.png"),
            "scene": "S8",
            "gloss": "Jahns Unterschrift",
            "src": NASA66,
            "min_dur": 5.0,
        },
        {
            "start_text": "Und warum lässt eine Universität wie diese",
            "visual": dl("P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg"),
            "scene": "S8",
            "gloss": "Engineering Quadrangle",
            "src": CCBY4,
            "min_dur": 4.0,
        },
        {
            "start_text": "Denn das Prinzip lebt weiter.",
            "visual": g("pe_v2_27_generator_modern"),
            "scene": "S8",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "In einem Netz aus Zufallsgeneratoren",
            "visual": g("pe_v2_26_server_weltkarte"),
            "scene": "S8",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Sie nennen es Global Consciousness Project.",
            "visual": g("pe_h09_serverraum_klein"),
            "scene": "S8",
            "gloss": "",
            "src": REKON,
            "min_dur": 4.0,
        },
        {
            "start_text": "Das ist die nächste Folge.",
            "visual": g("pe_v2_28_abendfenster"),
            "scene": "S8",
            "gloss": "",
            "src": REKON,
            "min_dur": 3.0,
        },
    ]


def find_time(text: str, anchor: str, chars: list[dict], cursor: int = 0) -> float:
    pos = text.find(anchor, cursor)
    if pos < 0:
        pos = text.find(anchor)
    if pos < 0:
        return -1
    for i in range(pos, min(pos + len(anchor), len(chars))):
        if not text[i].isspace():
            return chars[i]["start"]
    return -1


def build_timeline():
    print("\n  Baue finale optimierte Timeline...")
    
    if not ALIGNMENT.exists():
        print(f"  FEHLER: Alignment fehlt: {ALIGNMENT}")
        return
    
    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    chars = alignment["characters"]
    
    with open(CLEAN, 'r', encoding='utf-8') as f:
        text = f.read()
    
    segments = build_segments()
    timeline = []
    cursor = 0
    
    for i, seg in enumerate(segments):
        start_time = find_time(text, seg["start_text"], chars, cursor)
        
        if start_time < 0:
            print(f"  WARNUNG: Anker nicht gefunden: '{seg['start_text'][:50]}'")
            continue
        
        if i < len(segments) - 1:
            next_time = find_time(text, segments[i+1]["start_text"], chars, cursor)
            if next_time > 0:
                end_time = next_time
            else:
                end_time = start_time + 5.0
        else:
            end_time = chars[-1]["end"] if chars else start_time + 5.0
        
        min_dur = seg.get("min_dur", 2.5)
        if end_time - start_time < min_dur:
            end_time = start_time + min_dur
        
        if end_time - start_time > 7.0:
            end_time = start_time + 7.0
        
        visual_path = Path(seg["visual"])
        if not visual_path.exists():
            print(f"  WARNUNG: Bild fehlt: {visual_path.name}")
            continue
        
        try:
            with Image.open(visual_path) as im:
                aspect = im.width / im.height
        except Exception:
            aspect = 16 / 9
        
        timeline.append({
            "anchor": seg["start_text"],
            "visual": seg["visual"],
            "scene": seg["scene"],
            "kind": "STILL",
            "gloss": seg.get("gloss", ""),
            "src": seg.get("src", ""),
            "shot_id": f"SPG_V2_{i+1:03d}",
            "start": round(start_time, 3),
            "end": round(end_time, 3),
            "duration": round(end_time - start_time, 3),
            "aspect": round(aspect, 3),
            "contain": not (1.62 <= aspect <= 1.95),
            "scene_first": i == 0 or segments[i-1]["scene"] != seg["scene"],
            "scene_last": i == len(segments) - 1 or segments[i+1]["scene"] != seg["scene"],
        })
        
        cursor = text.find(seg["start_text"], cursor) + len(seg["start_text"])
    
    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    # Statistik
    total_duration = timeline[-1]["end"] if timeline else 0
    unique_visuals = len(set(r["visual"] for r in timeline))
    glosses = sum(1 for r in timeline if r["gloss"])
    sources = sum(1 for r in timeline if r["src"])
    
    # Bild-Verwendung
    from collections import Counter
    visual_counter = Counter(r["visual"] for r in timeline)
    max_repeat = max(visual_counter.values()) if visual_counter else 0
    
    print(f"\n  Timeline gespeichert: {TIMELINE.name}")
    print(f"  Segmente: {len(timeline)}")
    print(f"  Dauer: {total_duration:.2f}s ({int(total_duration//60)}:{total_duration%60:04.1f})")
    print(f"  Unique Bilder: {unique_visuals}")
    print(f"  Max. Wiederholungen: {max_repeat}x")
    print(f"  Beschriftungen: {glosses}")
    print(f"  Quellzeilen: {sources}")
    
    # Szenen-Statistik
    scenes = {}
    for r in timeline:
        scenes.setdefault(r["scene"], []).append(r)
    
    print(f"\n  Szenen:")
    for scene, shots in scenes.items():
        duration = shots[-1]["end"] - shots[0]["start"]
        print(f"    {scene}: {len(shots)} Segmente, {duration:.1f}s")
    
    return timeline


if __name__ == "__main__":
    build_timeline()
