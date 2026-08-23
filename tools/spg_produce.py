#!/usr/bin/env python3
"""EP01A Die Spiegel — Timeline, Ton, Render, Untertitel, QA.

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
PROD = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL"

ALIGNMENT = PROD / "voice" / "alignment" / "EP01A_SPIEGEL_alignment.json"
VOICE = PROD / "audio" / "EP01A_voice_-18LUFS.wav"
STEMREPORT = PROD / "voice" / "master" / "stem_report.json"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN.txt"

TIMELINE = PROD / "timeline" / "EP01A_SPIEGEL_timeline.json"
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
NAME = "EP01A_SPIEGEL"
GRUND = "#0A1428"          # arktisches Nachtblau, Blendenfarbe

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


DL = ("04_ASSETS", "01_DOWNLOADS", "EP01_KOZYREV")
CUR = ("04_ASSETS", "02_CURATED", "EP01_KOZYREV", "APPROVED")

KOZ_PORTRAIT = a(*DL, "K01_kozyrev_portrait_1959_CC0.png")
ANLAGE_S1 = a(*DL, "WIKIMEDIA_COMMONS", "KZ_WC_02_BIG_S1_2015.jpg")
ANLAGE_G2PF = a(*DL, "WIKIMEDIA_COMMONS", "KZ_WC_01_HORIZONTAL_BIG_G2PF_2015.jpg")
ANLAGE_SERMEGA = a(*CUR, "KZ_003_Kozyrev_mirrors_modern_photo_2014.jpg")
PATENT_APPARAT = d("KZ_PATENT_APPARATUS_1992.png")          # aus GIF, prepare()
# Seiten der Patentschrift, aus dem PDF (prepare()). Seite 2 ist die
# englische Kurzfassung und bleibt draussen — Dokumentbilder duerfen keine
# eingebrannten englischen Kopfzeilen tragen (Produktionsstandard § 4).
# Die Einzeldateien K05a-c waeren mit 75x120 px bei 1080p unlesbar.
PATENT_S1 = d("KZ_PATENT_SEITE_01.png")     # russische Titelseite mit Fig. 1
PATENT_FORMEL = d("KZ_PATENT_SEITE_05.png")  # Formel der Erfindung
PATENT_FIG2 = d("KZ_PATENT_SEITE_06.png")    # Fig. 2, offener Zylinder
PATENT_FIG4 = d("KZ_PATENT_SEITE_08.png")    # Fig. 4, Spirale mit Spalt
PULKOWO_REFRAKTOR = a(*CUR, "KZ_004_Pulkovo_big_refractor.jpg")
MOND_ALPHONSUS = a(*DL, "K06_Alphonsus_LRO_NASA_PD.png")
KOZ_GRAB = a(*DL, "K08_kozyrev_grave_pulkovo_CC-BY-SA-4.0.jpg")
APPARAT_ZEICHNUNG = a(*DL, "K03_kozyrev_mirror_original_1996_CC-BY-SA-4.0.jpg")
TRACERS = a(*DL, "NASA_SVS", "NASA_TRACERS_MAGNETIC_RECONNECTION_1080p.mov")

# Quellzeilen nach § 4: sie benennen das gezeigte Blatt, sie kommentieren nicht.
REKON = "Rekonstruktion"
PATENT = "Patentschrift RU 2122446 C1"
BRATTARB = "Foto: Brattarb, 2015 · CC BY-SA 3.0"
SERMEGA = "Foto: SerMega · CC BY-SA 4.0"
CC0 = "Foto: gemeinfrei · CC0"
CCBYSA4 = "Foto: CC BY-SA 4.0"
NASA = "NASA · gemeinfrei"
SVS = "NASA Goddard Space Flight Center · TRACERS"


def s(anchor, visual, scene, gloss="", src="", kind="STILL"):
    return {"anchor": anchor, "visual": visual, "scene": scene, "kind": kind,
            "gloss": gloss, "src": src}


def shots():
    return [
        # ============================================================ S1 Hook
        s("Du sitzt auf einem Stuhl aus Metall.", g("spg_stuhl_detail"), "S1", src=REKON),
        s("Um dich herum steht eine Spirale", g("spg_sitzung_weit"), "S1",
          "Spirale aus poliertem Aluminium, offen bis auf einen Spalt", REKON),
        s("Sie schließt sich hinter dir", g("spg_spalt_schliesst"), "S1", src=REKON),
        s("Das Licht geht aus.", g("spg_licht_geht_aus"), "S1", src=REKON),
        s("Es ist so still", g("spg_stille_ohr"), "S1", src=REKON),
        s("Nach etwa vier Minuten beginnt es.", g("spg_schimmern_rand"), "S1", src=REKON),
        s("Dann Farbe.", g("spg_farbflaechen_rein"), "S1", src=REKON),
        s("Flächen, die wandern.", mo("polarlicht"), "S1", kind="VIDEO"),
        s("Ringe, die sich ineinanderschieben.", g("spg_ringe"), "S1", src=REKON),
        s("Der Raum ist vollständig dunkel.", g("spg_kozyrev_raum_leer"), "S1", src=REKON),
        s("Nach zehn Minuten werden daraus Bilder.",
          g("spg_landschaft_aus_licht"), "S1", src=REKON),
        s("Ein Zimmer mit einem Fenster.", g("spg_zimmer_fenster"), "S1", src=REKON),
        s("Ein Gesicht, das dich ansieht.", g("spg_gesicht_lichtspur"), "S1", src=REKON),
        s("Und irgendwann verlierst du das Gefühl", g("spg_zifferblatt"), "S1", src=REKON),
        s("Als die Tür aufgeht", g("spg_tuer_geht_auf"), "S1", src=REKON),
        s("So steht es in einem Protokoll.", g("spg_protokollblatt_makro"), "S1", src=REKON),
        s("In einem von Tausenden", g("spg_protokollstapel"), "S1", src=REKON),
        s("Was passiert in diesem Raum?", ANLAGE_SERMEGA, "S1",
          "Anlage in Nowosibirsk, Aufnahme 2014", SERMEGA),

        # =================================================== S2 Die Menschen
        s("Im Netz heißt diese Konstruktion Zeitmaschine.", c("KZ_CARD_ZEITMASCHINE"), "S2"),
        s("Wer sie gebaut hat, hat dieses Wort nie benutzt.", ANLAGE_S1, "S2",
          "Anlage BIG-S1, Nowosibirsk 2015", BRATTARB),
        s("Was diese Leute stattdessen behaupten", g("spg_innenflaeche_detail"), "S2", src=REKON),
        s("Sie sagen, in diesem Raum kommt Information an", mo("zeitfluss"), "S2", kind="VIDEO"),
        s("Über Tausende Kilometer.", g("spg_weite_wasser"), "S2", src=REKON),
        s("Ohne Kabel, ohne Sender", g("spg_kurzwelle_empfaenger"), "S2", src=REKON),
        s("Und 1991 haben sie das im großen Maßstab", g("spg_dikson_funkstation"), "S2",
          "Dikson am Nordpolarmeer", REKON),
        s("Mit Stationen am Nordpolarmeer", g("spg_spirale_im_schnee"), "S2", src=REKON),
        s("Wie kommt man auf so eine Idee?", g("spg_notizbuch_zeit"), "S2", src=REKON),
        s("Und was ist bei diesem Versuch herausgekommen?",
          g("spg_blaetterstapel"), "S2", src=REKON),
        s("Nowosibirsk, Ende der achtziger Jahre.",
          g("spg_akademgorodok_winter"), "S2",
          "Akademgorodok bei Nowosibirsk", REKON),
        s("Akademgorodok, eine Wissenschaftsstadt", g("spg_institut_flur"), "S2", src=REKON),
        s("Plattenbauten zwischen Birken", g("spg_taiga_birken"), "S2", src=REKON),
        s("Hier leitet Vlail Kaznacheev ein Institut", g("spg_kaznacheev_labor"), "S2",
          "Vlail Kaznacheev, Institut der Akademie der Wissenschaften", REKON),
        s("Mediziner, Akademiemitglied", g("spg_institut_treppe"), "S2", src=REKON),
        s("Kaznacheev beschäftigt eine Frage", g("spg_mikroskop_makro"), "S2", src=REKON),
        s("Er will wissen, ob Zellen miteinander in Verbindung stehen",
          g("spg_kaznacheev_schreibt"), "S2", src=REKON),
        s("In den sechziger Jahren hat er dazu eine Versuchsreihe",
          g("spg_petrischalen"), "S2", src=REKON),
        s("Zwei Zellkulturen, getrennt durch eine Scheibe aus Quarzglas.",
          g("spg_quarzglas_kulturen"), "S2", "Zwei Kulturen, getrennt durch Quarzglas", REKON),
        s("Die eine wird mit einem Virus infiziert.", g("spg_kolben_allein"), "S2", src=REKON),
        s("Die andere berührt sie nie.", g("spg_hand_am_notizbuch"), "S2", src=REKON),
        s("Nach seinen Angaben erkrankt auch die zweite.",
          g("spg_protokollblatt_makro"), "S2", src=REKON),
        s("Durch Glas hindurch, ohne Kontakt.", g("spg_glasscheibe_durchblick"), "S2", src=REKON),
        s("Ob dieser Befund trägt, ist bis heute umstritten.",
          g("spg_institut_aussen_winter"), "S2", src=REKON),
        s("Für Kaznacheev war er der Anfang von allem.",
          g("spg_journalregal"), "S2", src=REKON),
        s("Sein engster Mitarbeiter heißt Alexander Trofimov.",
          g("spg_trofimov_aufzeichnungen"), "S2", "Alexander Trofimov", REKON),
        s("Und die beiden bauen etwas", g("spg_werkstatt_platten"), "S2", src=REKON),

        # =================================================== S3 Die Maschine
        s("Gebogene Platten aus Aluminiumlegierung.", APPARAT_ZEICHNUNG, "S3",
          "Konstruktionszeichnung der Apparatur, 1996", CCBYSA4),
        s("Bis zu zwei Meter achtzig hoch", c("KZ_CARD_MASSE"), "S3"),
        s("Die Innenseite geschliffen und poliert", g("spg_schleifen_hand"), "S3",
          "Geschliffene Innenseite", REKON),
        s("Die Krümmung erzeugt einen Brennpunkt", g("spg_brennpunkt"), "S3",
          "Brennpunkt, fünfzig Zentimeter vor der Fläche", REKON),
        s("Vier bis zehn dieser Elemente ergeben einen offenen Zylinder.",
          PATENT_FIG2, "S3", "Figur 2: gebogene Platten, offener Zylinder", PATENT),
        s("Oder eine Spirale, mit einem Spalt zum Einsteigen.", mo("spirale"), "S3", kind="VIDEO"),
        s("In einer Variante steht das Ganze auf einer motorisierten Plattform",
          g("spg_drehplattform"), "S3",
          "Motorisierte Drehplattform", REKON),
        s("Das alles steht in einem Patent.", g("spg_zeichnung_wird_bau"), "S3", src=REKON),
        s("Russische Föderation, Nummer zwei Millionen", PATENT_S1, "S3",
          "Titelseite RU 2122446 C1", PATENT),
        s("Angemeldet 1996, erteilt 1998.", PATENT_FIG4, "S3",
          "Figur 4: Spirale mit Einstiegsspalt", PATENT),
        s("Es gibt diese Maschine wirklich.", c("KZ_CARD_PATENT"), "S3"),
        s("Das ist der Teil, den man am schwersten glaubt", ANLAGE_G2PF, "S3",
          "Horizontale Anlage BIG-G2pf, 2015", BRATTARB),
        s("und der am leichtesten zu belegen ist", PATENT_APPARAT, "S3",
          "Zeichnung der Anlage zur Patentschrift", SERMEGA),

        # ================================================ S4 Der Kozyrev-Raum
        s("Was die beiden über das Innere sagen", g("spg_innenflaeche_detail"), "S4", src=REKON),
        s("Die polierten Wände schwächen das Magnetfeld der Erde ab.",
          mo("magnetfeld"), "S4", kind="VIDEO"),
        s("In diesem geschwächten Feld, sagen sie", g("spg_magnetfeld_schwach"), "S4", src=REKON),
        s("wird ein Mensch für etwas empfänglich", g("spg_spirale_oben"), "S4",
          "Sechs Elemente, ein Einstiegsspalt", REKON),
        s("Sie nennen den Zustand den Kozyrev-Raum.", c("KZ_CARD_ZEITMASCHINE"), "S4"),
        s("Nach einem Astronomen", KOZ_PORTRAIT, "S4", "Nikolai Kozyrev, 1959", CC0),
        s("Und dann setzen sie Menschen hinein", g("spg_sitzung_weit"), "S4", src=REKON),
        s("Über die Jahre wird daraus ein Berg von Protokollen.",
          g("spg_protokollstapel"), "S4", src=REKON),
        s("Und darin wiederholt sich alles so oft",
          g("spg_protokollblatt_makro"), "S4", src=REKON),
        s("Woher kommen diese Bilder?", c("KZ_CARD_MUSTER"), "S4"),

        # ================================================== S5 Die Protokolle
        s("Am häufigsten die Farbe.", g("spg_farbwellen"), "S5", src=REKON),
        s("Fast jeder berichtet davon", g("spg_schimmern_rand"), "S5", src=REKON),
        s("Leuchtende Flächen.", mo("polarlicht"), "S5", kind="VIDEO"),
        s("Konzentrische Ringe.", g("spg_ringe"), "S5", src=REKON),
        s("Dann die Bilder.", c("KZ_CARD_MUSTER"), "S5"),
        s("Bei vielen beginnt es mit Landschaften.",
          g("spg_landschaft_aus_licht"), "S5", src=REKON),
        s("Weite Flächen, Wasser, Horizonte.", g("spg_weite_wasser"), "S5", src=REKON),
        s("Manche beschreiben Innenräume", g("spg_zimmer_fenster"), "S5", src=REKON),
        s("Einige beschreiben Gesichter", g("spg_gesichter_im_dunkeln"), "S5", src=REKON),
        s("Manche Teilnehmer ordnen das Gesehene", g("spg_kindheitsszene"), "S5", src=REKON),
        s("Sie sagen, sie hätten Szenen aus ihrer Kindheit", mo("zeitfluss"), "S5", kind="VIDEO"),
        s("Und sie beschreiben es so", g("spg_vision_innenraum"), "S5", src=REKON),
        s("Dann die Zeit.", g("spg_zifferblatt"), "S5", src=REKON),
        s("Das Gefühl für Dauer löst sich auf.", g("spg_waerme_haut"), "S5", src=REKON),
        s("Zwanzig Minuten werden auf Stunden geschätzt.",
          g("spg_uhr_gleichzeitig"), "S5", src=REKON),
        s("Eine Stunde vergeht wie ein Augenblick.", g("spg_zeiger_trennen"), "S5", src=REKON),
        s("Dazu kommt der Körper.", g("spg_stille_ohr"), "S5", src=REKON),
        s("Kribbeln in den Händen", g("spg_haende_ruhig"), "S5",
          "Kribbeln in den Händen", REKON),
        s("Wärme im Gesicht.", g("spg_waerme_gesicht"), "S5", src=REKON),
        s("Bei manchen ein starkes Unbehagen", g("spg_unbehagen"), "S5", src=REKON),
        s("Trofimov fällt dabei etwas auf", g("spg_trofimov_aufzeichnungen"), "S5", src=REKON),
        s("Menschen, die im hohen Norden geboren wurden",
          g("spg_geburtsort_norden"), "S5", src=REKON),
        s("Er führt es auf das Magnetfeld ihrer Kindheit zurück.",
          g("spg_kompass_dreht"), "S5", src=REKON),
        s("Halte kurz an dieser Stelle.", g("spg_kozyrev_raum_leer"), "S5", src=REKON),
        s("Ein dunkler Metallraum, in dem ein Mensch still sitzt",
          g("spg_leerer_stuhl"), "S5",
          "Der Stuhl im Zentrum", REKON),
        s("Farbmuster im Dunkeln produziert das Sehsystem",
          g("spg_vision_bandmuster"), "S5", src=REKON),
        s("Die Gruppe in Nowosibirsk weiß das.", g("spg_labor_nachbau_leer"), "S5", src=REKON),
        s("Ein Erlebnis kann von innen kommen.", g("spg_vision_wasserlinie"), "S5", src=REKON),
        s("Eine Information nicht.", g("spg_blaetterstapel"), "S5", src=REKON),
        s("Wie prüft man das?", g("spg_kuechentisch_warm"), "S5", src=REKON),
        s("Schreib mir vorher in die Kommentare", c("KZ_CARD_COMMENT"), "S5"),

        # =============================================== S6 Aurora Borealis
        s("Denn was 1990 und 1991 folgt", g("spg_dikson_funkstation"), "S6", src=REKON),
        s("Das Experiment heißt Aurora Borealis.", mo("polarlicht"), "S6", kind="VIDEO"),
        s("Nordlicht.", g("spg_nordlicht_ueber_masten"), "S6",
          "Nordlicht über der Antennenanlage", REKON),
        s("Die Überlegung ist einfach und in der Ausführung wahnsinnig.",
          c("KZ_CARD_AURORA"), "S6"),
        s("Wenn dieser Raum Information über Entfernung trägt",
          mo("zeitfluss"), "S6", kind="VIDEO"),
        s("wo das Magnetfeld der Erde von sich aus am dünnsten ist", TRACERS, "S6",
          "Magnetische Rekonnexion am Erdfeld", SVS, kind="VIDEO"),
        s("In die Arktis.", g("spg_dikson_hafen"), "S6", src=REKON),
        s("Also bringen sie die Spiegel nach Dikson.",
          g("spg_verladung_polarkreis"), "S6", src=REKON),
        s("Eine Siedlung am Rand des Nordpolarmeers", c("KZ_CARD_DIKSON"), "S6"),
        s("Im Winter monatelang dunkel", g("spg_kabel_im_eis"), "S6", src=REKON),
        s("Man muss sich den Aufwand vorstellen.", g("spg_montagehalle"), "S6", src=REKON),
        s("Aluminiumplatten von fast drei Metern Höhe",
          g("spg_kisten_entladen"), "S6", src=REKON),
        s("aufgebaut in einem Ort, in dem ein paar hundert Menschen leben",
          g("spg_kabeltrommel_schnee"), "S6", src=REKON),
        s("Und über allem steht in diesen Nächten das Nordlicht.",
          g("spg_aurora_ueber_eis"), "S6", src=REKON),
        s("Genau das Phänomen, nach dem sie den Versuch benennen.",
          g("spg_spirale_im_schnee"), "S6",
          "Die Anlage im Freien, Polarnacht", REKON),

        # ======================================================== S7 Dikson
        s("Der Ablauf ist für alle Teilnehmer gleich.", c("KZ_CARD_AURORA"), "S7"),
        s("Zu einer festgelegten Minute setzt sich jemand in den Spiegel",
          g("spg_sender_im_spiegel"), "S7",
          "Senderseite: ein einzelnes Symbol", REKON),
        s("und konzentriert sich auf ein einziges einfaches Symbol",
          g("spg_spirale_im_schnee"), "S7", src=REKON),
        s("Einen Kreis.", g("spg_kreis_gezeichnet"), "S7", src=REKON),
        s("Ein Kreuz.", g("spg_kreuz_gezeichnet"), "S7", src=REKON),
        s("Ein Dreieck.", g("spg_dreieck_gezeichnet"), "S7", src=REKON),
        s("Zur selben Minute sitzen irgendwo auf der Welt Menschen",
          g("spg_uhr_gleichzeitig"), "S7", src=REKON),
        s("Die Empfängerseite besteht aus einer Uhrzeit",
          g("spg_empfaenger_zweiter"), "S7",
          "Empfängerseite: Uhrzeit, Blatt, Stift", REKON),
        s("Koordiniert wird das über Kurzwelle",
          g("spg_kurzwelle_empfaenger"), "S7", src=REKON),
        s("und über Aufrufe in Zeitungen", g("spg_zeitungsseite"), "S7", src=REKON),
        s("Nach Angaben der Beteiligten machen Tausende mit",
          g("spg_kurzwelle_detail"), "S7", src=REKON),
        s("Stell dir vor, was das für ein Bild abgibt.",
          g("spg_blaetter_ausgebreitet"), "S7", src=REKON),
        s("Ein Institut der Akademie der Wissenschaften stellt Aluminiumspiralen",
          g("spg_nordlicht_ueber_masten"), "S7", src=REKON),
        s("Die Auswertung meldet auffällige Übereinstimmungen.",
          g("spg_protokollstapel"), "S7", src=REKON),
        s("Am deutlichsten bei den einfachen Formen.",
          g("spg_zwei_blaetter_vergleich"), "S7", src=REKON),
        s("Und stärker in den Phasen, in denen die geomagnetische Aktivität niedrig ist.",
          TRACERS, "S7", src=SVS, kind="VIDEO"),
        s("Genau dann, sagen sie, ist der Kanal offen.", mo("magnetfeld"), "S7", kind="VIDEO"),

        # ==================================================== S8 Was bleibt
        s("Was bleibt davon übrig?", c("KZ_CARD_SCHLUSSSTAND"), "S8"),
        s("Die Anlagen gibt es.", ANLAGE_SERMEGA, "S8", src=SERMEGA),
        s("Es existieren Fotos, Baupläne, eine Patentnummer.", ANLAGE_G2PF, "S8", src=BRATTARB),
        s("In Nowosibirsk stehen sie bis heute", g("spg_besucher_heute"), "S8", src=REKON),
        s("Die Protokolle gibt es.", g("spg_protokollstapel"), "S8", src=REKON),
        s("Tausende Berichte über Jahrzehnte", c("KZ_CARD_MUSTER"), "S8"),
        s("Was fehlt, ist eine Wiederholung durch jemanden",
          g("spg_labor_nachbau_leer"), "S8", src=REKON),
        s("Alle Auswertungen stammen bis heute", g("spg_patentmappe_offen"), "S8", src=REKON),
        s("Und das ist die eigentlich merkwürdige Sache",
          g("spg_anlage_heute_leer"), "S8",
          "Die Anlage heute", REKON),
        s("Der Aufbau steht auf zwei Seiten Patentschrift.", PATENT_FORMEL, "S8",
          "Formel der Erfindung: die Ansprüche", PATENT),
        s("Die Maße sind öffentlich.", g("spg_patentmappe"), "S8", src=REKON),
        s("Aluminium ist kein seltener Rohstoff.", g("spg_platte_profil"), "S8", src=REKON),
        s("Seit fast dreißig Jahren könnte jedes Labor",
          g("spg_anlage_heute_besuch"), "S8", src=REKON),
        s("Warum hat es niemand getan?", c("KZ_CARD_FRAGE"), "S8"),
        s("Bleibt eine letzte Frage.", g("spg_leerer_stuhl"), "S8", src=REKON),
        s("Diese Maschine trägt den Namen eines Mannes", KOZ_PORTRAIT, "S8",
          "Nikolai Kozyrev, 1959", CC0),
        s("Nikolai Kozyrev stirbt 1983", KOZ_GRAB, "S8",
          "Grab am Pulkowo-Observatorium", CCBYSA4),
        s("Er war Astrophysiker.", PULKOWO_REFRAKTOR, "S8",
          "Großer Refraktor, Pulkowo-Observatorium", "Aufnahme gemeinfrei"),
        s("Er verbrachte zehn Jahre in einem sowjetischen Lager.",
          g("spg_lagerwerkstatt"), "S8",
          "Werkstattarbeit im Lager", REKON),
        s("Er richtete 1958 ein Teleskop auf den Mond", g("spg_teleskop_mond"), "S8",
          "Beobachtung des Mondes, 1958", REKON),
        s("und behauptete etwas, für das ihn der führende Mondforscher",
          MOND_ALPHONSUS, "S8", "Krater Alphonsus", NASA),
        s("Und er hat sein halbes Leben damit zugebracht",
          g("spg_schreibtisch_rechenschieber"), "S8", src=REKON),
        s("dass die Zeit eine Kraft ist", g("spg_waage_kreisel"), "S8",
          "Waage und Kreisel, Kozyrevs Messaufbau", REKON),
        s("Das ist die nächste Folge.", g("spg_pulkowo_kuppel"), "S8", src=REKON),
    ]


# ----------------------------------------------------------------- prepare

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
         + ",eq=contrast=1.03:saturation=1.04,unsharp=5:5:.24:5:5:0,format=yuv420p")
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
             "-loop", "1", "-framerate", str(FPS), "-i", str(CARDS / "KZ_ENDCARD.png"),
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
    mix = AUDIO / "EP01A_final_mix.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(picture), "-i", str(mix), "-vf", assf,
         "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
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

    raw = AUDIO / "EP01A_bed_raw.wav"
    bed = AUDIO / "EP01A_bed_-30LUFS.wav"
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

    premix = AUDIO / "EP01A_premix.wav"
    final = AUDIO / "EP01A_final_mix.wav"
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
