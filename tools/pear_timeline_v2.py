#!/usr/bin/env python3
"""EP03 PEAR V2 — Timeline Builder mit perfekter Text-Bild-Sync.

Nutzt das Forced Alignment, um jeden gesprochenen Textanker mit dem
exakten Zeitpunkt zu verknüpfen. Das stellt sicher, dass gesprochene
Texte und angezeigte Bilder perfekt synchron sind.

Nutzung:
    python tools/pear_timeline_v2.py
"""

from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

# Pfade
ALIGNMENT = PROD / "voice" / "alignment" / "EP03_V2_alignment.json"
TIMELINE = PROD / "timeline" / "EP03_V2_timeline.json"
VOICE = PROD / "audio" / "EP03_V2_voice_-18LUFS.wav"

# Asset-Verzeichnisse
GEN = PROD / "visuals" / "generated"
CARDS = PROD / "visuals" / "cards"
MOTION = PROD / "motion"
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


def find_anchor_time(text: str, anchor: str, chars: list[dict]) -> float:
    """Findet die Startzeit eines Textankers im Alignment."""
    # Normalisiere Encoding-Probleme
    def normalize(s):
        return s.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    
    # Versuche zuerst exakte Suche
    pos = text.find(anchor)
    
    # Falls nicht gefunden, versuche normalisierte Suche
    if pos < 0:
        norm_text = normalize(text)
        norm_anchor = normalize(anchor)
        pos = norm_text.find(norm_anchor)
    
    if pos < 0:
        return -1
    
    # Finde den ersten nicht-Whitespace-Charakter
    for i in range(pos, min(pos + len(anchor), len(chars))):
        if not text[i].isspace():
            return chars[i]["start"]
    
    return -1


def build_shot_list() -> list[dict]:
    """Erstellt die Shotliste mit Textankern und Bildzuordnungen."""
    
    # Hilfsfunktionen für Pfade
    def g(name): return str(GEN / f"{name}.png")
    def c(name): return str(CARDS / f"{name}.png")
    def mo(name): return str(MOTION / f"{name}.mp4")
    def dl(name): return str(DL / name)
    def pat(name): return str(PAT / f"US5830064_{name}_2320x3408.png")
    
    # Quellzeilen
    REKON = "Rekonstruktion"
    PATENT = "US-Patentschrift 5.830.064"
    NASA66 = "Jahn, Princeton 1966 · gemeinfrei"
    CCBY4 = "CC BY 4.0"
    CCBYSA4 = "CC BY-SA 4.0"
    CCBYSA3 = "CC BY-SA 3.0"
    CCBY2 = "CC BY 2.0"
    PD_DOE = "US Department of Energy · gemeinfrei"
    
    return [
        # ============================================================ S1: PARADOXON
        {"anchor": "Der Dekan der Ingenieurfakultät", "visual": g("pe_b01_jahn_portraet"), "scene": "S1", "gloss": "Robert G. Jahn", "src": REKON},
        {"anchor": "hat ein Problem.", "visual": g("pe_a01_keller_weit"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "Er sitzt im Keller", "visual": g("pe_a01_keller_weit"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "Vor ihm steht eine graue Kiste", "visual": g("pe_a02_kiste_detail"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "Er versucht, sie mit dem Gedanken", "visual": g("pe_a05_gesicht_konzentration"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "Es klappt.", "visual": g("pe_e04_waage_zunge"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "Eins von zehntausend Mal.", "visual": g("pe_e05_sandkorn"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "Robert Jahn hat Raketentriebwerke", "visual": g("pe_b02_jahn_schreibtisch"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "für die NASA gebaut.", "visual": dl("P28_Jahn_Princeton_lab_1966_Plexiglas_vacuum_tank_Fig27.png"), "scene": "S1", "gloss": "Jahns Vakuumkammer, 1966", "src": NASA66},
        {"anchor": "Er hat das Standardwerk", "visual": g("pe_b05_buchruecken"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "auf diesem Gebiet geschrieben.", "visual": dl("P29_Jahn_Princeton_lab_1966_microwave_horn_electrode_Fig17.png"), "scene": "S1", "gloss": "Mikrowellenhorn, 1966", "src": NASA66},
        {"anchor": "Er entscheidet über Berufungen", "visual": g("pe_b06_fakultaetssitzung"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "über Geld, über Ruf.", "visual": dl("P02_Nassau_Hall_2026_CC-BY-4.0.jpg"), "scene": "S1", "gloss": "Nassau Hall, Princeton", "src": CCBY4},
        {"anchor": "Und er verbringt achtundzwanzig Jahre", "visual": g("pe_b15_jahn_alt"), "scene": "S1", "gloss": "Robert G. Jahn", "src": REKON},
        {"anchor": "im Keller seines eigenen Gebäudes.", "visual": g("pe_a11_kellerflur"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "gemessen an einer Abweichung", "visual": g("pe_e01_linie_steigt"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "die kleiner ist als ein Rundungsfehler.", "visual": g("pe_e03_null_eins_strom"), "scene": "S1", "gloss": "", "src": REKON},
        {"anchor": "Warum?", "visual": g("pe_h07_schreibtisch_leer"), "scene": "S1", "gloss": "", "src": REKON},
        
        # ============================================================ S2: MCDONNELL
        {"anchor": "Der Mann, der das alles bezahlt", "visual": g("pe_b01_jahn_portraet"), "scene": "S2", "gloss": "Robert G. Jahn", "src": REKON},
        {"anchor": "heißt James S. McDonnell.", "visual": c("PE_V2_CARD_MCDONNELL"), "scene": "S2", "gloss": "", "src": ""},
        {"anchor": "Er hat McDonnell Douglas gegründet.", "visual": g("pe_v2_01_mcdonnell_f15"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Die F-15.", "visual": g("pe_v2_01_mcdonnell_f15"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Die F/A-18.", "visual": g("pe_v2_02_mcdonnell_mercury"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Die Mercury-Kapsel.", "visual": g("pe_v2_02_mcdonnell_mercury"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Und er hat eine Angst.", "visual": g("pe_v2_03_pilot_cockpit"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Eine ganz bestimmte Angst.", "visual": g("pe_v2_03_pilot_cockpit"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Er glaubt, dass die Gedanken eines Piloten", "visual": g("pe_v2_03_pilot_cockpit"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "die Elektronik eines Kampfflugzeugs stören können.", "visual": g("pe_v2_01_mcdonnell_f15"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Deshalb bezahlt er ein Labor in Princeton.", "visual": dl("P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg"), "scene": "S2", "gloss": "Engineering Quadrangle", "src": CCBY4},
        {"anchor": "Im Keller der Ingenieurfakultät.", "visual": g("pe_a01_keller_weit"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Bei einem Mann, der Raketen baut.", "visual": g("pe_b02_jahn_schreibtisch"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Das Labor heißt PEAR.", "visual": dl("P27_EQuad_Courtyard_SphericTheme_2023_CC-BY-SA-4.0.jpg"), "scene": "S2", "gloss": "Engineering Quadrangle", "src": CCBYSA4},
        {"anchor": "Princeton Engineering Anomalies Research.", "visual": dl("P26_EQuad_Courtyard_StoneRiddle_2023_CC-BY-SA-4.0.jpg"), "scene": "S2", "gloss": "Engineering Quadrangle", "src": CCBYSA4},
        {"anchor": "Im Haus nennen es alle nur PEAR.", "visual": g("pe_b13_efeu_backstein"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Und die Universität lässt es zu.", "visual": dl("P03_FitzRandolph_Gate_2026_CC-BY-4.0.jpg"), "scene": "S2", "gloss": "FitzRandolph Gate", "src": CCBY4},
        {"anchor": "Unter zwei Bedingungen:", "visual": g("pe_b12_vereinbarung_blatt"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "kein Geld von Princeton", "visual": g("pe_a11_kellerflur"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "und keine Doktoranden.", "visual": g("pe_b04_triebwerk_pruefstand"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Die Laborleitung übernimmt Brenda Dunne", "visual": g("pe_b10_dunne_portraet"), "scene": "S2", "gloss": "Brenda J. Dunne", "src": REKON},
        {"anchor": "eine Psychologin mit Masterabschluss", "visual": g("pe_b11_dunne_am_ordner"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "keine Professorin.", "visual": g("pe_b11_dunne_am_ordner"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Sie bleibt bis zum letzten Tag.", "visual": g("pe_b11_dunne_am_ordner"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "Später wird sie einen Satz sagen", "visual": g("pe_b10_dunne_portraet"), "scene": "S2", "gloss": "Brenda J. Dunne", "src": REKON},
        {"anchor": "der alles über dieses Labor sagt.", "visual": g("pe_b13_efeu_backstein"), "scene": "S2", "gloss": "", "src": REKON},
        {"anchor": "How do you get peer review", "visual": g("pe_b10_dunne_portraet"), "scene": "S2", "gloss": "Brenda J. Dunne", "src": REKON},
        {"anchor": "when you don't have peers?", "visual": g("pe_b13_efeu_backstein"), "scene": "S2", "gloss": "", "src": REKON},
        
        # ============================================================ S3: MASCHINEN
        {"anchor": "Und dann bauen sie Maschinen.", "visual": g("pe_c01_werkbank"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Das Herzstück ist eine Kiste", "visual": g("pe_c06_kiste_offen"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "die sie den Zufallsgenerator nennen.", "visual": pat("frontpage"), "scene": "S3", "gloss": "Titelblatt US 5.830.064", "src": PATENT},
        {"anchor": "Eine Rauschdiode erzeugt echten", "visual": dl("P13_Zener_diode_1N829_CC-BY-SA-4.0.jpg"), "scene": "S3", "gloss": "Zenerdiode", "src": CCBYSA4},
        {"anchor": "physikalischen Zufall", "visual": g("pe_c03_rauschdiode"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "kein Rechenprogramm", "visual": pat("sheet04"), "scene": "S3", "gloss": "Figur 4: Signalweg", "src": PATENT},
        {"anchor": "man kann es nicht vorausberechnen.", "visual": dl("P17_Tektronix_475A_1977_analog_scope_CC-BY-SA-3.0.jpg"), "scene": "S3", "gloss": "Analogoszilloskop, 1977", "src": CCBYSA3},
        {"anchor": "Das Rauschen wird verstärkt", "visual": pat("sheet13"), "scene": "S3", "gloss": "Figur 8A: Analogteil", "src": PATENT},
        {"anchor": "mit einer festen Spannung verglichen.", "visual": g("pe_c04_oszilloskop_rauschen"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Liegt es darüber, ist das Ergebnis eine Eins.", "visual": g("pe_c05_schaltung_zeichnung"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Liegt es darunter, eine Null.", "visual": pat("sheet14"), "scene": "S3", "gloss": "Figur 8B: Digitalstufe", "src": PATENT},
        {"anchor": "Ein Versuch sind zweihundert Würfe.", "visual": c("PE_CARD_MASSE"), "scene": "S3", "gloss": "", "src": ""},
        {"anchor": "Er dauert zwei Zehntelsekunden.", "visual": g("pe_c08_geraet_reihe"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Tausend davon ergeben eine Serie, und dafür sitzt", "visual": dl("P12_Punched_paper_tapes_CHM_2005_CC-BY-2.0.jpg"), "scene": "S3", "gloss": "Lochbandrollen", "src": CCBY2},
        {"anchor": "gut drei Minuten still.", "visual": g("pe_d04_uhr_wand"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Der Teilnehmer setzt sich davor", "visual": g("pe_d02_sitzung_seitlich"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "und legt vorher fest, was er will.", "visual": g("pe_d03_zettel_absicht"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Mehr Einsen.", "visual": c("PE_CARD_MUSTER"), "scene": "S3", "gloss": "", "src": ""},
        {"anchor": "Weniger Einsen.", "visual": c("PE_CARD_MUSTER"), "scene": "S3", "gloss": "", "src": ""},
        {"anchor": "Oder gar nichts, einfach laufen lassen.", "visual": g("pe_d12_stuhl_leer_labor"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Diese dritte Bedingung ist die wichtigste.", "visual": g("pe_d12_stuhl_leer_labor"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Sie ist die Kontrolle.", "visual": g("pe_c08_geraet_reihe"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Dann sitzt der Mensch da.", "visual": g("pe_d10_kopfhoerer_tisch"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Er darf die Kiste ansehen oder wegsehen, Musik hören", "visual": g("pe_a05_gesicht_konzentration"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Musik hören, tun was ihm hilft.", "visual": g("pe_d10_kopfhoerer_tisch"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Es gibt keine Anleitung.", "visual": g("pe_d04_uhr_wand"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Manche sagen, sie hätten sich angestrengt.", "visual": g("pe_a05_gesicht_konzentration"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Andere sagen, angestrengt habe nie funktioniert, es gehe nur", "visual": g("pe_d11_protokollbuch"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Das Labor notiert das mit", "visual": g("pe_d11_protokollbuch"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "und hat nie behauptet, eine Erklärung dafür zu haben.", "visual": g("pe_f04_fenster_regen"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Über die Jahre kommen andere Apparate dazu.", "visual": g("pe_d08_pendel_quarz"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Eine Wand aus Acrylglas", "visual": g("pe_d05_kugelwand_weit"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "drei Meter hoch, knapp zwei Meter breit.", "visual": g("pe_d05_kugelwand_weit"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Oben werden neuntausend Polystyrolkugeln eingefüllt, jede keine zwei Zentimeter groß.", "visual": g("pe_b16_dunne_kugelwand"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Sie fallen durch ein Raster aus dreihundertdreißig Nylonstiften", "visual": g("pe_d06_kugeln_fallen"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "und sammeln sich unten in neunzehn Fächern.", "visual": g("pe_d07_faecher_unten"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Ein Durchgang dauert etwa zwölf Minuten.", "visual": c("PE_CARD_KASKADE"), "scene": "S3", "gloss": "", "src": ""},
        {"anchor": "Was dabei entsteht, ist eine Glockenkurve.", "visual": dl("P07_Galton_board_before_after_2017_CC-BY-SA-4.0.jpg"), "scene": "S3", "gloss": "Galton-Brett", "src": CCBYSA4},
        {"anchor": "Dieselbe Kurve, die in jedem Statistiklehrbuch steht.", "visual": dl("P30_Galton_box_RMC_standin_2016_CC-BY-SA-4.0.jpg"), "scene": "S3", "gloss": "Galton-Brett", "src": CCBYSA4},
        {"anchor": "Die Aufgabe für den Teilnehmer:", "visual": g("pe_d02_sitzung_seitlich"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Verschieb den Berg.", "visual": pat("sheet12"), "scene": "S3", "gloss": "Figur 7C: Verfahren", "src": PATENT},
        {"anchor": "Nach links oder nach rechts.", "visual": g("pe_c07_kabel_bundel"), "scene": "S3", "gloss": "", "src": REKON},
        {"anchor": "Mit nichts als Aufmerksamkeit.", "visual": g("pe_c07_kabel_bundel"), "scene": "S3", "gloss": "", "src": REKON},
        
        # ============================================================ S4: OPERATOR 10
        {"anchor": "Und dann kommt der Teil", "visual": g("pe_e05_sandkorn"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "der schwerer zu erzählen ist als jeder Apparat.", "visual": g("pe_e05_sandkorn"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Über alle Jahre und alle Versuche zusammen", "visual": g("pe_e03_null_eins_strom"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "liegt die Abweichung in der Größenordnung", "visual": g("pe_e01_linie_steigt"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "von einem Bit auf zehntausend.", "visual": g("pe_e04_waage_zunge"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Stell dir zehntausend Münzwürfe vor.", "visual": g("pe_e02_muenzen_flug"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Erwartet werden fünftausend Mal Kopf.", "visual": c("PE_CARD_FRAGE"), "scene": "S4", "gloss": "", "src": ""},
        {"anchor": "Gemessen werden fünftausendundeins.", "visual": g("pe_e04_waage_zunge"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Das ist der ganze Effekt.", "visual": g("pe_e04_waage_zunge"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Erst wenn man Millionen von Durchgängen", "visual": g("pe_e01_linie_steigt"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "übereinanderlegt, wird aus dem Rauschen eine Linie, die nicht mehr auf null zurückkehrt.", "visual": g("pe_e01_linie_steigt"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "die nicht mehr auf null zurückkehrt.", "visual": g("pe_e01_linie_steigt"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Und dann gibt es da diese eine Person.", "visual": g("pe_d12_stuhl_leer_labor"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Das Labor nennt sie Operator zehn.", "visual": g("pe_d12_stuhl_leer_labor"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Zwölf Jahre.", "visual": pat("sheet09"), "scene": "S4", "gloss": "Figur 6C: Auswertekette", "src": PATENT},
        {"anchor": "Zweiundsechzig Serien.", "visual": g("pe_a10_ausdruckstapel"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Über hundertzwanzigtausend Durchgänge je Richtung.", "visual": g("pe_a10_ausdruckstapel"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Vierzehn Millionen Durchgänge", "visual": g("pe_a10_ausdruckstapel"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "hat das Labor insgesamt gemacht.", "visual": g("pe_a10_ausdruckstapel"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Fünfzehn Prozent davon kamen von dieser einen Person.", "visual": g("pe_d12_stuhl_leer_labor"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Und nach einer Analyse", "visual": pat("sheet19"), "scene": "S4", "gloss": "Figur 15A: kumulierte Abweichung", "src": PATENT},
        {"anchor": "ging auf sie die Hälfte des gesamten Überschusses zurück.", "visual": pat("sheet19"), "scene": "S4", "gloss": "Figur 15A: kumulierte Abweichung", "src": PATENT},
        {"anchor": "Wer das war, hat das Labor nie offengelegt.", "visual": pat("sheet05"), "scene": "S4", "gloss": "Figur 5A: Datenweg", "src": PATENT},
        {"anchor": "Jahn hat den Namen nie genannt.", "visual": dl("P35_Jahn_signature_titlepage_1966_PD-US-no-notice.png"), "scene": "S4", "gloss": "Jahns Unterschrift", "src": NASA66},
        {"anchor": "Wenn man diese eine Person herausrechnet", "visual": g("pe_f03_zwei_stapel"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "fällt der low-intention-Effekt auf Zufallsniveau.", "visual": g("pe_f08_taschenrechner"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Der high-intention-Effekt sinkt an die Grenze", "visual": g("pe_e01_linie_steigt"), "scene": "S4", "gloss": "", "src": REKON},
        {"anchor": "Was denkst du bis hier?", "visual": c("PE_CARD_COMMENT"), "scene": "S4", "gloss": "", "src": ""},
        {"anchor": "Schreib es in die Kommentare, bevor der nächste Teil kommt.", "visual": c("PE_CARD_COMMENT"), "scene": "S4", "gloss": "", "src": ""},
        
        # ============================================================ S5: REPLIKATION
        {"anchor": "Denn jetzt kommt die Stelle", "visual": g("pe_g10_labor_weiterarbeit"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "an der diese Geschichte etwas tut", "visual": g("pe_g10_labor_weiterarbeit"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "was fast keine Geschichte dieser Art tut.", "visual": g("pe_g10_labor_weiterarbeit"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Das Labor hat sich selbst überprüfen lassen.", "visual": c("PE_CARD_PROBE"), "scene": "S5", "gloss": "", "src": ""},
        {"anchor": "Ende der Neunziger schließt PEAR sich", "visual": dl("P21_IGPP_Freiburg_Wilhelmstrasse3a_2011_CC-BY-SA-3.0.jpg"), "scene": "S5", "gloss": "IGPP Freiburg", "src": CCBYSA3},
        {"anchor": "mit zwei deutschen Instituten zusammen.", "visual": dl("P23_JLU_Giessen_Hauptgebaeude_2007_CC-BY-SA-4.0.jpg"), "scene": "S5", "gloss": "JLU Gießen", "src": CCBYSA4},
        {"anchor": "Freiburg und Gießen.", "visual": dl("P22_IGPP_Freiburg_Schild_2011_CC-BY-SA-3.0.jpg"), "scene": "S5", "gloss": "IGPP Freiburg", "src": CCBYSA3},
        {"anchor": "Und sie machen es diesmal anders.", "visual": g("pe_g04_protokoll_unterschrift"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Alles wird vorher festgelegt.", "visual": dl("P22_IGPP_Freiburg_Schild_2011_CC-BY-SA-3.0.jpg"), "scene": "S5", "gloss": "IGPP Freiburg", "src": CCBYSA3},
        {"anchor": "Wie viele Durchgänge.", "visual": pat("sheet06"), "scene": "S5", "gloss": "Figur 5B: Ablaufsteuerung", "src": PATENT},
        {"anchor": "Welche Bedingungen.", "visual": g("pe_g03_drei_geraete"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Wie ausgewertet wird.", "visual": g("pe_g04_protokoll_unterschrift"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Alle drei Labore benutzen dasselbe Gerät", "visual": g("pe_g03_drei_geraete"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "und dieselbe Software.", "visual": g("pe_g03_drei_geraete"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Das ist der Versuch, den Kritiker", "visual": dl("P25_JLU_Giessen_Philosophikum_I_2016_CC-BY-SA-3.0.jpg"), "scene": "S5", "gloss": "Philosophikum I, Gießen", "src": CCBYSA3},
        {"anchor": "seit zwanzig Jahren gefordert haben.", "visual": dl("P25_JLU_Giessen_Philosophikum_I_2016_CC-BY-SA-3.0.jpg"), "scene": "S5", "gloss": "Philosophikum I, Gießen", "src": CCBYSA3},
        {"anchor": "Und PEAR macht ihn mit.", "visual": g("pe_g05_versand_kiste"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Dann laufen die Maschinen.", "visual": g("pe_g01_institut_freiburg"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Und der Effekt ist nicht da.", "visual": g("pe_g08_flaches_ergebnis"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Die Abweichungen gehen in allen drei Laboren", "visual": g("pe_g07_zwei_kurven"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "zwar in die gewünschte Richtung.", "visual": g("pe_g07_zwei_kurven"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Aber sie sind zu klein.", "visual": pat("sheet20"), "scene": "S5", "gloss": "Figur 15B: kumulierte Abweichung", "src": PATENT},
        {"anchor": "Jahn und Dunne schreiben das später selbst auf, in ihrem eigenen Übersichtsaufsatz:", "visual": g("pe_g09_veroeffentlichung"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Die Ausschläge hätten die Größe der früheren Versuche", "visual": c("PE_CARD_ZWEI_ERGEBNISSE"), "scene": "S5", "gloss": "", "src": ""},
        {"anchor": "um eine Zehnerpotenz verfehlt und nicht einmal ein überzeugendes Signifikanzniveau erreicht.", "visual": c("PE_CARD_ZWEI_ERGEBNISSE"), "scene": "S5", "gloss": "", "src": ""},
        {"anchor": "An anderer Stelle steht es noch schärfer:", "visual": g("pe_g06_telefonat_nacht"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Legt man die eigenen früheren Ergebnisse als Maßstab an", "visual": g("pe_g06_telefonat_nacht"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "dann sei die Vorhersage widerlegt.", "visual": g("pe_g06_telefonat_nacht"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Geschrieben von denen", "visual": g("pe_g02_labor_deutsch"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "die zwei Jahrzehnte lang das Gegenteil gemessen hatten.", "visual": g("pe_g02_labor_deutsch"), "scene": "S5", "gloss": "", "src": REKON},
        {"anchor": "Und dann arbeiten sie weiter.", "visual": pat("sheet07"), "scene": "S5", "gloss": "", "src": PATENT},
        
        # ============================================================ S6: OFF-TIME
        {"anchor": "Denn es gibt da noch etwas", "visual": g("pe_e01_linie_steigt"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "was in den Daten steht", "visual": g("pe_e01_linie_steigt"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "das seltsamer ist als der Effekt selbst.", "visual": g("pe_e01_linie_steigt"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Das Labor hat auch versucht", "visual": g("pe_d02_sitzung_seitlich"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "die Maschine zu beeinflussen", "visual": g("pe_c06_kiste_offen"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "wenn niemand davor saß.", "visual": g("pe_d12_stuhl_leer_labor"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Sie nennen es Off-Time-Experimente.", "visual": c("PE_V2_CARD_OFFTIME"), "scene": "S6", "gloss": "", "src": ""},
        {"anchor": "Die Operatoren sollten ihre Absicht", "visual": g("pe_a05_gesicht_konzentration"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "auf die Maschine richten", "visual": g("pe_c06_kiste_offen"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "zu Zeiten, in denen sie gar nicht im Labor waren.", "visual": g("pe_v2_04_offtime_uhr"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Siebzig Stunden vorher.", "visual": g("pe_v2_04_offtime_uhr"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Dreihundertsechsunddreißig Stunden nachher.", "visual": g("pe_v2_04_offtime_uhr"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Achtundachtzigtausend Durchgänge pro Richtung.", "visual": g("pe_a10_ausdruckstapel"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Und es gibt noch den sogenannten Baseline Bind.", "visual": c("PE_V2_CARD_BASELINE"), "scene": "S6", "gloss": "", "src": ""},
        {"anchor": "Die Kontrolldurchgänge", "visual": g("pe_d12_stuhl_leer_labor"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "die, bei denen niemand etwas wollte", "visual": g("pe_d12_stuhl_leer_labor"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "zeigen weniger Ausreißer", "visual": g("pe_v2_05_baseline_glatt"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "als die Statistik erwarten würde.", "visual": g("pe_v2_05_baseline_glatt"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Zu brav.", "visual": g("pe_v2_05_baseline_glatt"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Zu glatt.", "visual": g("pe_v2_05_baseline_glatt"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Kritiker sagen: Das ist ein Zeichen", "visual": g("pe_f07_einzelner_stuhl_reihe"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "dafür, dass etwas mit den Daten nicht stimmt.", "visual": g("pe_f07_einzelner_stuhl_reihe"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Jahn und Dunne sagen etwas anderes.", "visual": g("pe_b01_jahn_portraet"), "scene": "S6", "gloss": "Robert G. Jahn", "src": REKON},
        {"anchor": "Sie sagen: Vielleicht beeinflussen die Menschen", "visual": g("pe_b10_dunne_portraet"), "scene": "S6", "gloss": "Brenda J. Dunne", "src": REKON},
        {"anchor": "die Maschine, selbst wenn sie nichts wollen.", "visual": g("pe_c06_kiste_offen"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Unbewusst.", "visual": g("pe_v2_06_geist_still"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Immer.", "visual": g("pe_v2_06_geist_still"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Das ist der Punkt, an dem diese Geschichte", "visual": g("pe_v2_06_geist_still"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "aufhört, eine Geschichte über eine Maschine zu sein.", "visual": g("pe_c06_kiste_offen"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Und anfängt, eine Geschichte über ein Modell des Geistes zu sein.", "visual": c("PE_V2_CARD_MODELL"), "scene": "S6", "gloss": "", "src": ""},
        {"anchor": "Denn was Jahn und Dunne beschreiben", "visual": g("pe_b01_jahn_portraet"), "scene": "S6", "gloss": "Robert G. Jahn", "src": REKON},
        {"anchor": "ist nicht mehr: Kann ich mit dem Gedanken eine Münze verschieben?", "visual": g("pe_e02_muenzen_flug"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Es ist: Ist mein Geist überhaupt jemals still?", "visual": g("pe_v2_06_geist_still"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Ist da immer etwas, das wirkt", "visual": g("pe_v2_06_geist_still"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "auch wenn ich nichts will?", "visual": g("pe_v2_06_geist_still"), "scene": "S6", "gloss": "", "src": REKON},
        {"anchor": "Und wenn ja — wie weit reicht das?", "visual": g("pe_v2_06_geist_still"), "scene": "S6", "gloss": "", "src": REKON},
        
        # ============================================================ S7: KRITIK
        {"anchor": "Die Fachwelt hat darauf eine klare Antwort.", "visual": g("pe_f01_endlospapier_boden"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Die größte Meta-Analyse", "visual": g("pe_f01_endlospapier_boden"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "dreihundertachtzig Studien", "visual": g("pe_f01_endlospapier_boden"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "findet einen signifikanten, aber extrem kleinen Gesamteffekt.", "visual": g("pe_e01_linie_steigt"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Und erklärt ihn mit Publikationsbias.", "visual": g("pe_f03_zwei_stapel"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Je größer die Studie, desto kleiner der Effekt — genau das Muster", "visual": g("pe_f08_taschenrechner"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Ein Methodiker schreibt:", "visual": g("pe_f06_person_am_stapel"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Es sei nahezu unmöglich, aus dieser Datenlage Schlüsse zu ziehen.", "visual": g("pe_f06_person_am_stapel"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Ein anderer sagt:", "visual": g("pe_f07_einzelner_stuhl_reihe"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Die Behauptungen der Parapsychologen können nicht wahr sein.", "visual": g("pe_f07_einzelner_stuhl_reihe"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Schweine können nicht fliegen.", "visual": g("pe_v2_07_schweine_fliegen"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Daten, die das Gegenteil suggerieren", "visual": g("pe_f03_zwei_stapel"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "sind notwendig fehlerhaft.", "visual": g("pe_f03_zwei_stapel"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Das ist die eine Seite.", "visual": g("pe_f07_einzelner_stuhl_reihe"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Die andere Seite sagt:", "visual": g("pe_b01_jahn_portraet"), "scene": "S7", "gloss": "Robert G. Jahn", "src": REKON},
        {"anchor": "Wir haben die Daten.", "visual": g("pe_a10_ausdruckstapel"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Wir haben sie veröffentlicht.", "visual": g("pe_g09_veroeffentlichung"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Wir haben die Replikation selbst mitgemacht, und sie hat nicht funktioniert", "visual": g("pe_g03_drei_geraete"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "und wir haben das auch veröffentlicht.", "visual": g("pe_g09_veroeffentlichung"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Und dann haben wir aufgehört.", "visual": g("pe_h02_leerer_raum"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Sieben Jahre später ist Schluss.", "visual": g("pe_h01_kisten_packen"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Zweitausendsieben.", "visual": g("pe_b15_jahn_alt"), "scene": "S7", "gloss": "Robert G. Jahn", "src": REKON},
        {"anchor": "Die Leitung sperrt selbst zu.", "visual": g("pe_h02_leerer_raum"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Jahn sagt dazu einen Satz", "visual": g("pe_h04_datentraeger"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "der lange nachhallt.", "visual": g("pe_h04_datentraeger"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Achtundzwanzig Jahre lang hätten sie getan", "visual": g("pe_h02_leerer_raum"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "was sie tun wollten, und es gebe keinen Grund zu bleiben", "visual": g("pe_h02_leerer_raum"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "und es gebe keinen Grund zu bleiben", "visual": g("pe_h02_leerer_raum"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "und noch mehr von denselben Daten zu erzeugen.", "visual": g("pe_h04_datentraeger"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Robert Jahn stirbt zweitausendsiebzehn.", "visual": g("pe_h06_grabstein_schlicht"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Von den siebenhundert Professoren in Princeton", "visual": dl("P02_Nassau_Hall_2026_CC-BY-4.0.jpg"), "scene": "S7", "gloss": "Nassau Hall, Princeton", "src": CCBY4},
        {"anchor": "hat sich niemand dem Projekt angeschlossen.", "visual": g("pe_v2_08_princeton_schweigen"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Die Universität äußert sich offiziell nicht zur Schließung.", "visual": g("pe_v2_08_princeton_schweigen"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Nicht ein einziges Wort.", "visual": g("pe_v2_08_princeton_schweigen"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Ein Physiker von der University of Maryland sagt:", "visual": g("pe_f07_einzelner_stuhl_reihe"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "It's been an embarrassment to science", "visual": g("pe_f07_einzelner_stuhl_reihe"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "and I think an embarrassment for Princeton.", "visual": g("pe_f07_einzelner_stuhl_reihe"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "Ein Physikprofessor in Princeton selbst sagt:", "visual": dl("P05_Dept_Physics_Princeton_2026_CC-BY-4.0.jpg"), "scene": "S7", "gloss": "Department of Physics, Princeton", "src": CCBY4},
        {"anchor": "I don't believe in anything Bob is doing", "visual": dl("P05_Dept_Physics_Princeton_2026_CC-BY-4.0.jpg"), "scene": "S7", "gloss": "Department of Physics, Princeton", "src": CCBY4},
        {"anchor": "but I support his right to do it.", "visual": dl("P05_Dept_Physics_Princeton_2026_CC-BY-4.0.jpg"), "scene": "S7", "gloss": "Department of Physics, Princeton", "src": CCBY4},
        {"anchor": "Das ist der Unterschied", "visual": g("pe_v2_08_princeton_schweigen"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "zwischen einer Institution, die etwas verbietet", "visual": g("pe_v2_08_princeton_schweigen"), "scene": "S7", "gloss": "", "src": REKON},
        {"anchor": "und einer, die etwas erträgt.", "visual": g("pe_v2_08_princeton_schweigen"), "scene": "S7", "gloss": "", "src": REKON},
        
        # ============================================================ S8: WAS BLEIBT
        {"anchor": "Was bleibt von achtundzwanzig Jahren?", "visual": c("PE_CARD_SCHLUSSSTAND"), "scene": "S8", "gloss": "", "src": ""},
        {"anchor": "Die Maschinen gab es.", "visual": g("pe_c06_kiste_offen"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "Die Patentschrift liegt öffentlich aus", "visual": pat("sheet01"), "scene": "S8", "gloss": "Figur 1: Gesamtaufbau", "src": PATENT},
        {"anchor": "mit den Namen auf dem Titelblatt.", "visual": pat("sheet22"), "scene": "S8", "gloss": "Titelblatt", "src": PATENT},
        {"anchor": "Die Daten gibt es.", "visual": dl("P14_Bound_line_printer_listing_1978_CC-BY-SA-3.0.jpg"), "scene": "S8", "gloss": "Zeilendrucker-Ausdruck, 1978", "src": CCBYSA3},
        {"anchor": "Millionen von Durchgängen", "visual": dl("P12_Punched_paper_tapes_CHM_2005_CC-BY-2.0.jpg"), "scene": "S8", "gloss": "Lochbandrollen", "src": CCBY2},
        {"anchor": "aufgezeichnet und veröffentlicht.", "visual": dl("P12_Punched_paper_tapes_CHM_2005_CC-BY-2.0.jpg"), "scene": "S8", "gloss": "Lochbandrollen", "src": CCBY2},
        {"anchor": "Und es gibt eine Wiederholung", "visual": pat("sheet21"), "scene": "S8", "gloss": "Figur 15C: kumulierte Abweichung", "src": PATENT},
        {"anchor": "unter verschärften Bedingungen", "visual": pat("sheet21"), "scene": "S8", "gloss": "Figur 15C: kumulierte Abweichung", "src": PATENT},
        {"anchor": "die den Effekt nicht gefunden hat.", "visual": pat("sheet21"), "scene": "S8", "gloss": "Figur 15C: kumulierte Abweichung", "src": PATENT},
        {"anchor": "Auch die ist veröffentlicht", "visual": pat("sheet23"), "scene": "S8", "gloss": "Figur 17: Datenerfassung", "src": PATENT},
        {"anchor": "von denselben Leuten.", "visual": pat("sheet23"), "scene": "S8", "gloss": "Figur 17: Datenerfassung", "src": PATENT},
        {"anchor": "Damit ist die Sache für die meisten Fachleute erledigt.", "visual": pat("sheet24"), "scene": "S8", "gloss": "Figur 18: Aufzeichnung", "src": PATENT},
        {"anchor": "Eine Frage bleibt trotzdem.", "visual": g("pe_h07_schreibtisch_leer"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "Warum hängt ein Mann", "visual": dl("P35_Jahn_signature_titlepage_1966_PD-US-no-notice.png"), "scene": "S8", "gloss": "Jahns Unterschrift", "src": NASA66},
        {"anchor": "der Raketentriebwerke gebaut hat", "visual": dl("P28_Jahn_Princeton_lab_1966_Plexiglas_vacuum_tank_Fig27.png"), "scene": "S8", "gloss": "Jahns Vakuumkammer, 1966", "src": NASA66},
        {"anchor": "achtundzwanzig Jahre seines Lebens", "visual": g("pe_b15_jahn_alt"), "scene": "S8", "gloss": "Robert G. Jahn", "src": REKON},
        {"anchor": "an eine Abweichung von einem Bit auf zehntausend?", "visual": g("pe_e04_waage_zunge"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "Und warum lässt eine Universität wie diese", "visual": dl("P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg"), "scene": "S8", "gloss": "Engineering Quadrangle", "src": CCBY4},
        {"anchor": "ihn gewähren, solange er es selbst bezahlt?", "visual": dl("P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg"), "scene": "S8", "gloss": "Engineering Quadrangle", "src": CCBY4},
        {"anchor": "Und ob wir gerade dabei sind", "visual": g("pe_h03_archivkarton"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "dieselbe Frage noch einmal zu stellen.", "visual": g("pe_h03_archivkarton"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "Mit besserer Elektronik", "visual": pat("sheet08"), "scene": "S8", "gloss": "Figur 6B: Anordnung", "src": PATENT},
        {"anchor": "und mehr Rechenleistung.", "visual": pat("sheet08"), "scene": "S8", "gloss": "Figur 6B: Anordnung", "src": PATENT},
        {"anchor": "Denn das Prinzip lebt weiter.", "visual": dl("P31_TRNG_Araneus_Alea_REG_standin_2018_CC-BY-4.0.jpg"), "scene": "S8", "gloss": "Hardware-Zufallsgenerator", "src": CCBY4},
        {"anchor": "In einem Netz aus Zufallsgeneratoren", "visual": g("pe_h08_netz_weltkarte"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "verteilt über die ganze Welt", "visual": g("pe_h08_netz_weltkarte"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "das seit neunzehnhundertachtundneunzig ununterbrochen misst.", "visual": g("pe_h10_generator_heute"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "Sie nennen es Global Consciousness Project.", "visual": g("pe_h09_serverraum_klein"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "Das globale Bewusstseinsprojekt.", "visual": g("pe_h09_serverraum_klein"), "scene": "S8", "gloss": "", "src": REKON},
        {"anchor": "Das ist die nächste Folge.", "visual": g("pe_h05_fenster_abend"), "scene": "S8", "gloss": "", "src": REKON},
    ]


def build_timeline():
    """Baut die Timeline mit exakter Text-Bild-Synchronisation."""
    print("\n  Baue Timeline mit Text-Bild-Sync...")
    
    # Lade Alignment
    if not ALIGNMENT.exists():
        print(f"  FEHLER: Alignment fehlt: {ALIGNMENT}")
        return
    
    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    chars = alignment["characters"]
    
    # Verwende die originale Scriptdatei (korrektes Encoding)
    clean_file = PROD / "07_VOICE_SCRIPT_CLEAN_V2.txt"
    if not clean_file.exists():
        print(f"  FEHLER: Clean Script fehlt: {clean_file}")
        return
    
    # Explizit mit UTF-8 lesen
    with open(clean_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Lade Shotliste
    shots = build_shot_list()
    
    # Finde Zeitpunkte für jeden Anker
    timeline = []
    cursor = 0
    
    for i, shot in enumerate(shots):
        anchor = shot["anchor"]
        
        # Suche im Originaltext
        pos = text.find(anchor, cursor)
        
        # Falls nicht gefunden, versuche ohne Cursor (für verschachtelte Anker)
        if pos < 0:
            pos = text.find(anchor)
        
        if pos < 0:
            print(f"  WARNUNG: Anker nicht gefunden: '{anchor[:50]}...'")
            continue
        
        # Finde Startzeit
        first_char_idx = None
        for j in range(pos, min(pos + len(anchor), len(chars))):
            if not text[j].isspace():
                first_char_idx = j
                break
        
        if first_char_idx is None:
            print(f"  WARNUNG: Kein Zeichen für Anker: '{anchor}'")
            continue
        
        start_time = chars[first_char_idx]["start"]
        
        # Bestimme Endzeit (nächster Shot oder Ende)
        if i < len(shots) - 1:
            next_anchor = shots[i + 1]["anchor"]
            next_pos = text.find(next_anchor, pos + len(anchor))
            if next_pos >= 0:
                next_first = None
                for j in range(next_pos, min(next_pos + len(next_anchor), len(chars))):
                    if not text[j].isspace():
                        next_first = j
                        break
                if next_first is not None:
                    end_time = chars[next_first]["start"]
                else:
                    end_time = start_time + 3.0
            else:
                end_time = start_time + 3.0
        else:
            end_time = alignment["characters"][-1]["end"] if alignment["characters"] else start_time + 3.0
        
        # Prüfe ob Datei existiert
        visual_path = Path(shot["visual"])
        if not visual_path.exists():
            print(f"  WARNUNG: Bild fehlt: {visual_path.name}")
            continue
        
        # Bestimme Aspect Ratio
        try:
            if shot["visual"].endswith(".mp4"):
                aspect = 16 / 9
            else:
                with Image.open(visual_path) as im:
                    aspect = im.width / im.height
        except Exception:
            aspect = 16 / 9
        
        # Erstelle Timeline-Eintrag
        timeline.append({
            "anchor": anchor,
            "visual": shot["visual"],
            "scene": shot["scene"],
            "kind": "VIDEO" if shot["visual"].endswith(".mp4") else "STILL",
            "gloss": shot.get("gloss", ""),
            "src": shot.get("src", ""),
            "shot_id": f"SPG_V2_{i+1:03d}",
            "start": round(start_time, 3),
            "end": round(end_time, 3),
            "duration": round(end_time - start_time, 3),
            "aspect": round(aspect, 3),
            "contain": not (1.62 <= aspect <= 1.95),
            "scene_first": i == 0 or shots[i-1]["scene"] != shot["scene"],
            "scene_last": i == len(shots) - 1 or shots[i+1]["scene"] != shot["scene"],
        })
        
        cursor = pos + len(anchor)
    
    # Speichere Timeline
    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    # Statistik
    total_duration = timeline[-1]["end"] if timeline else 0
    unique_visuals = len(set(r["visual"] for r in timeline))
    glosses = sum(1 for r in timeline if r["gloss"])
    sources = sum(1 for r in timeline if r["src"])
    
    print(f"\n  Timeline gespeichert: {TIMELINE.name}")
    print(f"  Shots: {len(timeline)}")
    print(f"  Dauer: {total_duration:.2f}s ({int(total_duration//60)}:{total_duration%60:04.1f})")
    print(f"  Einzelbilder: {unique_visuals}")
    print(f"  Beschriftungen: {glosses}")
    print(f"  Quellzeilen: {sources}")
    
    # Szenen-Statistik
    scenes = {}
    for r in timeline:
        scenes.setdefault(r["scene"], []).append(r)
    
    print(f"\n  Szenen:")
    for scene, shots in scenes.items():
        duration = shots[-1]["end"] - shots[0]["start"]
        print(f"    {scene}: {len(shots)} Shots, {duration:.1f}s")
    
    return timeline


if __name__ == "__main__":
    build_timeline()
