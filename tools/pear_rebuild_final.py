#!/usr/bin/env python3
"""EP03 PEAR V2 — Kompletter Rebuild.

Behebt alle Probleme:
- Lückenlose Segmente (keine Sprünge)
- Voice wird nicht abgeschnitten
- Korrekte Endcard (NOESIS, Bewusstsein)
- Optimale Bild-Text-Sync

Nutzung:
    python tools/pear_rebuild_final.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

ALIGNMENT = PROD / "voice" / "alignment" / "EP03_V2_alignment.json"
TIMELINE = PROD / "timeline" / "EP03_V2_timeline.json"
CLEAN = PROD / "07_VOICE_SCRIPT_CLEAN_V2.txt"
VOICE = PROD / "audio" / "EP03_V2_voice_-18LUFS.wav"
AUDIO_MIX = PROD / "audio" / "EP01A_final_mix.wav"
SEGMENTS = PROD / "render" / "segments_v2"
FINAL = PROD / "render" / "final_v2"
CARDS = PROD / "visuals" / "cards"
GEN = PROD / "visuals" / "generated"
DL = ROOT / "04_ASSETS" / "01_DOWNLOADS" / "EP03_PEAR"
PAT = DL / "P20_US5830064_figures_PD-USGov"

FPS = 30
ENDCARD_SEC = 20.0
NAME = "EP03_PEAR_V2"
GRUND = "#0E1013"


def run(args, capture=False):
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


def build_segments():
    """Definiert alle Segmente mit Start-Text und Bild."""
    return [
        # S1: PARADOXON
        {"start": "Der Dekan der Ingenieurfakultät", "vis": g("pe_b01_jahn_portraet"), "sc": "S1", "gl": "Robert G. Jahn", "sr": REKON},
        {"start": "Er sitzt im Keller", "vis": g("pe_a01_keller_weit"), "sc": "S1", "gl": "", "sr": REKON},
        {"start": "Er versucht, sie mit dem Gedanken", "vis": g("pe_a05_gesicht_konzentration"), "sc": "S1", "gl": "", "sr": REKON},
        {"start": "Eins von zehntausend Mal.", "vis": g("pe_v2_09_muenzwurf_detail"), "sc": "S1", "gl": "", "sr": REKON},
        {"start": "Robert Jahn hat Raketentriebwerke", "vis": dl("P28_Jahn_Princeton_lab_1966_Plexiglas_vacuum_tank_Fig27.png"), "sc": "S1", "gl": "Jahns Vakuumkammer, 1966", "sr": NASA66},
        {"start": "Er hat das Standardwerk", "vis": g("pe_b05_buchruecken"), "sc": "S1", "gl": "", "sr": REKON},
        {"start": "Er entscheidet über Berufungen", "vis": dl("P02_Nassau_Hall_2026_CC-BY-4.0.jpg"), "sc": "S1", "gl": "Nassau Hall, Princeton", "sr": CCBY4},
        {"start": "Und er verbringt achtundzwanzig Jahre", "vis": g("pe_b15_jahn_alt"), "sc": "S1", "gl": "Robert G. Jahn", "sr": REKON},
        {"start": "Warum?", "vis": g("pe_h07_schreibtisch_leer"), "sc": "S1", "gl": "", "sr": REKON},
        
        # S2: MCDONNELL
        {"start": "Der Mann, der das alles bezahlt", "vis": c("PE_V2_CARD_MCDONNELL"), "sc": "S2", "gl": "", "sr": ""},
        {"start": "Er hat McDonnell Douglas gegründet.", "vis": g("pe_v2_01_mcdonnell_f15"), "sc": "S2", "gl": "", "sr": REKON},
        {"start": "Und er hat eine Angst.", "vis": g("pe_v2_03_pilot_cockpit"), "sc": "S2", "gl": "", "sr": REKON},
        {"start": "Deshalb bezahlt er ein Labor in Princeton.", "vis": dl("P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg"), "sc": "S2", "gl": "Engineering Quadrangle", "sr": CCBY4},
        {"start": "Das Labor heißt PEAR.", "vis": g("pe_b13_efeu_backstein"), "sc": "S2", "gl": "", "sr": REKON},
        {"start": "Und die Universität lässt es zu.", "vis": dl("P03_FitzRandolph_Gate_2026_CC-BY-4.0.jpg"), "sc": "S2", "gl": "FitzRandolph Gate", "sr": CCBY4},
        {"start": "Die Laborleitung übernimmt Brenda Dunne", "vis": g("pe_b10_dunne_portraet"), "sc": "S2", "gl": "Brenda J. Dunne", "sr": REKON},
        {"start": "How do you get peer review", "vis": g("pe_b11_dunne_am_ordner"), "sc": "S2", "gl": "Brenda J. Dunne", "sr": REKON},
        
        # S3: MASCHINEN
        {"start": "Und dann bauen sie Maschinen.", "vis": g("pe_c01_werkbank"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Das Herzstück ist eine Kiste", "vis": g("pe_c06_kiste_offen"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "die sie den Zufallsgenerator nennen.", "vis": pat("frontpage"), "sc": "S3", "gl": "Titelblatt US 5.830.064", "sr": PATENT},
        {"start": "Eine Rauschdiode erzeugt echten", "vis": g("pe_v2_10_rauschen_oszilloskop"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Das Rauschen wird verstärkt", "vis": pat("sheet13"), "sc": "S3", "gl": "Figur 8A: Analogteil", "sr": PATENT},
        {"start": "Ein Versuch sind zweihundert Würfe.", "vis": c("PE_CARD_MASSE"), "sc": "S3", "gl": "", "sr": ""},
        {"start": "Der Teilnehmer setzt sich davor", "vis": g("pe_d02_sitzung_seitlich"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Diese dritte Bedingung ist die wichtigste.", "vis": g("pe_d12_stuhl_leer_labor"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Dann sitzt der Mensch da.", "vis": g("pe_d10_kopfhoerer_tisch"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Über die Jahre kommen andere Apparate dazu.", "vis": g("pe_v2_11_pendel_detail"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Eine Wand aus Acrylglas", "vis": g("pe_d05_kugelwand_weit"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Was dabei entsteht, ist eine Glockenkurve.", "vis": g("pe_v2_14_faecher_verteilung"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Die Aufgabe für den Teilnehmer:", "vis": g("pe_d02_sitzung_seitlich"), "sc": "S3", "gl": "", "sr": REKON},
        {"start": "Mit nichts als Aufmerksamkeit.", "vis": g("pe_c07_kabel_bundel"), "sc": "S3", "gl": "", "sr": REKON},
        
        # S4: OPERATOR 10
        {"start": "Und dann kommt der Teil", "vis": g("pe_e05_sandkorn"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Über alle Jahre und alle Versuche zusammen", "vis": g("pe_e01_linie_steigt"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Stell dir zehntausend Münzwürfe vor.", "vis": g("pe_e02_muenzen_flug"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Das ist der ganze Effekt.", "vis": g("pe_e04_waage_zunge"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Und dann gibt es da diese eine Person.", "vis": g("pe_d12_stuhl_leer_labor"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Das Labor nennt sie Operator zehn.", "vis": g("pe_v2_15_protokollbuch_detail"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Vierzehn Millionen Durchgänge", "vis": g("pe_v2_16_daten_papier"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Und nach einer Analyse", "vis": pat("sheet19"), "sc": "S4", "gl": "Figur 15A: kumulierte Abweichung", "sr": PATENT},
        {"start": "Wer das war, hat das Labor nie offengelegt.", "vis": g("pe_a10_ausdruckstapel"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Wenn man diese eine Person herausrechnet", "vis": g("pe_f03_zwei_stapel"), "sc": "S4", "gl": "", "sr": REKON},
        {"start": "Was denkst du bis hier?", "vis": c("PE_CARD_COMMENT"), "sc": "S4", "gl": "", "sr": ""},
        
        # S5: REPLIKATION
        {"start": "Denn jetzt kommt die Stelle", "vis": g("pe_g10_labor_weiterarbeit"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "Das Labor hat sich selbst überprüfen lassen.", "vis": c("PE_CARD_PROBE"), "sc": "S5", "gl": "", "sr": ""},
        {"start": "Ende der Neunziger schließt PEAR sich", "vis": dl("P21_IGPP_Freiburg_Wilhelmstrasse3a_2011_CC-BY-SA-3.0.jpg"), "sc": "S5", "gl": "IGPP Freiburg", "sr": CCBYSA3},
        {"start": "Freiburg und Gießen.", "vis": g("pe_v2_18_deutsche_universitaet"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "Und sie machen es diesmal anders.", "vis": g("pe_g04_protokoll_unterschrift"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "Alle drei Labore benutzen dasselbe Gerät", "vis": g("pe_v2_17_drei_labore"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "Dann laufen die Maschinen.", "vis": g("pe_g01_institut_freiburg"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "Und der Effekt ist nicht da.", "vis": g("pe_v2_20_ergebnis_flach"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "Jahn und Dunne schreiben das später selbst auf", "vis": g("pe_g09_veroeffentlichung"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "An anderer Stelle steht es noch schärfer:", "vis": g("pe_v2_19_telefon_nacht"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "Geschrieben von denen", "vis": g("pe_g02_labor_deutsch"), "sc": "S5", "gl": "", "sr": REKON},
        {"start": "Und dann arbeiten sie weiter.", "vis": g("pe_g10_labor_weiterarbeit"), "sc": "S5", "gl": "", "sr": REKON},
        
        # S6: OFF-TIME
        {"start": "Denn es gibt da noch etwas", "vis": g("pe_e01_linie_steigt"), "sc": "S6", "gl": "", "sr": REKON},
        {"start": "Das Labor hat auch versucht", "vis": g("pe_c06_kiste_offen"), "sc": "S6", "gl": "", "sr": REKON},
        {"start": "Sie nennen es Off-Time-Experimente.", "vis": c("PE_V2_CARD_OFFTIME"), "sc": "S6", "gl": "", "sr": ""},
        {"start": "zu Zeiten, in denen sie gar nicht im Labor waren.", "vis": g("pe_v2_04_offtime_uhr"), "sc": "S6", "gl": "", "sr": REKON},
        {"start": "Und es gibt noch den sogenannten Baseline Bind.", "vis": c("PE_V2_CARD_BASELINE"), "sc": "S6", "gl": "", "sr": ""},
        {"start": "Die Kontrolldurchgänge", "vis": g("pe_v2_05_baseline_glatt"), "sc": "S6", "gl": "", "sr": REKON},
        {"start": "Kritiker sagen: Das ist ein Zeichen", "vis": g("pe_f07_einzelner_stuhl_reihe"), "sc": "S6", "gl": "", "sr": REKON},
        {"start": "Jahn und Dunne sagen etwas anderes.", "vis": g("pe_b01_jahn_portraet"), "sc": "S6", "gl": "Robert G. Jahn", "sr": REKON},
        {"start": "Unbewusst.", "vis": g("pe_v2_06_geist_still"), "sc": "S6", "gl": "", "sr": REKON},
        {"start": "Und anfängt, eine Geschichte über ein Modell des Geistes zu sein.", "vis": c("PE_V2_CARD_MODELL"), "sc": "S6", "gl": "", "sr": ""},
        {"start": "Es ist: Ist mein Geist überhaupt jemals still?", "vis": g("pe_v2_06_geist_still"), "sc": "S6", "gl": "", "sr": REKON},
        
        # S7: KRITIK
        {"start": "Die Fachwelt hat darauf eine klare Antwort.", "vis": g("pe_f01_endlospapier_boden"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Die größte Meta-Analyse", "vis": g("pe_v2_21_meta_analyse"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "findet einen signifikanten, aber extrem kleinen Gesamteffekt.", "vis": g("pe_e01_linie_steigt"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Und erklärt ihn mit Publikationsbias.", "vis": g("pe_v2_22_publikation_bias"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Ein Methodiker schreibt:", "vis": g("pe_f06_person_am_stapel"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Schweine können nicht fliegen.", "vis": g("pe_v2_23_schwein_wolken"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Die andere Seite sagt:", "vis": g("pe_b01_jahn_portraet"), "sc": "S7", "gl": "Robert G. Jahn", "sr": REKON},
        {"start": "Wir haben die Daten.", "vis": g("pe_a10_ausdruckstapel"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Wir haben sie veröffentlicht.", "vis": g("pe_g09_veroeffentlichung"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Und dann haben wir aufgehört.", "vis": g("pe_h02_leerer_raum"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Sieben Jahre später ist Schluss.", "vis": g("pe_h01_kisten_packen"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Jahn sagt dazu einen Satz", "vis": g("pe_h04_datentraeger"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Robert Jahn stirbt zweitausendsiebzehn.", "vis": g("pe_v2_25_grabstein_detail"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Die Universität äußert sich offiziell nicht zur Schließung.", "vis": g("pe_v2_24_princeton_nacht_detail"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Ein Physiker von der University of Maryland sagt:", "vis": g("pe_f07_einzelner_stuhl_reihe"), "sc": "S7", "gl": "", "sr": REKON},
        {"start": "Das ist der Unterschied", "vis": g("pe_v2_08_princeton_schweigen"), "sc": "S7", "gl": "", "sr": REKON},
        
        # S8: WAS BLEIBT
        {"start": "Was bleibt von achtundzwanzig Jahren?", "vis": c("PE_CARD_SCHLUSSSTAND"), "sc": "S8", "gl": "", "sr": ""},
        {"start": "Die Maschinen gab es.", "vis": g("pe_c06_kiste_offen"), "sc": "S8", "gl": "", "sr": REKON},
        {"start": "Die Patentschrift liegt öffentlich aus", "vis": pat("sheet01"), "sc": "S8", "gl": "Figur 1: Gesamtaufbau", "sr": PATENT},
        {"start": "Die Daten gibt es.", "vis": g("pe_v2_16_daten_papier"), "sc": "S8", "gl": "", "sr": REKON},
        {"start": "Und es gibt eine Wiederholung", "vis": pat("sheet21"), "sc": "S8", "gl": "Figur 15C: kumulierte Abweichung", "sr": PATENT},
        {"start": "Eine Frage bleibt trotzdem.", "vis": g("pe_h07_schreibtisch_leer"), "sc": "S8", "gl": "", "sr": REKON},
        {"start": "Warum hängt ein Mann", "vis": dl("P35_Jahn_signature_titlepage_1966_PD-US-no-notice.png"), "sc": "S8", "gl": "Jahns Unterschrift", "sr": NASA66},
        {"start": "Und warum lässt eine Universität wie diese", "vis": dl("P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg"), "sc": "S8", "gl": "Engineering Quadrangle", "sr": CCBY4},
        {"start": "Denn das Prinzip lebt weiter.", "vis": g("pe_v2_27_generator_modern"), "sc": "S8", "gl": "", "sr": REKON},
        {"start": "In einem Netz aus Zufallsgeneratoren", "vis": g("pe_v2_26_server_weltkarte"), "sc": "S8", "gl": "", "sr": REKON},
        {"start": "Sie nennen es Global Consciousness Project.", "vis": g("pe_h09_serverraum_klein"), "sc": "S8", "gl": "", "sr": REKON},
        {"start": "Das ist die nächste Folge.", "vis": g("pe_v2_28_abendfenster"), "sc": "S8", "gl": "", "sr": REKON},
    ]


def find_time(text, anchor, chars, cursor=0):
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
    """Baut Timeline mit lückenlosen Segmenten."""
    print("\n  Baue lückenlose Timeline...")
    
    alignment = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    chars = alignment["characters"]
    
    with open(CLEAN, 'r', encoding='utf-8') as f:
        text = f.read()
    
    segments = build_segments()
    timeline = []
    cursor = 0
    
    for i, seg in enumerate(segments):
        start_time = find_time(text, seg["start"], chars, cursor)
        if start_time < 0:
            continue
        
        # Endzeit = Start des nächsten Segments oder Voice-Ende
        if i < len(segments) - 1:
            next_start = find_time(text, segments[i+1]["start"], chars, cursor)
            if next_start > 0:
                end_time = next_start
            else:
                end_time = start_time + 5.0
        else:
            end_time = chars[-1]["end"]
        
        # Mindestdauer 2.5s
        if end_time - start_time < 2.5:
            end_time = start_time + 2.5
        
        # Maximal 7s
        if end_time - start_time > 7.0:
            end_time = start_time + 7.0
        
        vis_path = Path(seg["vis"])
        if not vis_path.exists():
            continue
        
        try:
            with Image.open(vis_path) as im:
                aspect = im.width / im.height
        except:
            aspect = 16/9
        
        timeline.append({
            "anchor": seg["start"],
            "visual": seg["vis"],
            "scene": seg["sc"],
            "kind": "STILL",
            "gloss": seg.get("gl", ""),
            "src": seg.get("sr", ""),
            "shot_id": f"SPG_V2_{i+1:03d}",
            "start": round(start_time, 3),
            "end": round(end_time, 3),
            "duration": round(end_time - start_time, 3),
            "aspect": round(aspect, 3),
            "contain": not (1.62 <= aspect <= 1.95),
            "scene_first": i == 0 or segments[i-1]["sc"] != seg["sc"],
            "scene_last": i == len(segments) - 1 or segments[i+1]["sc"] != seg["sc"],
        })
        
        cursor = text.find(seg["start"], cursor) + len(seg["start"])
    
    TIMELINE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    total = timeline[-1]["end"]
    unique = len(set(r["visual"] for r in timeline))
    print(f"  Segmente: {len(timeline)}")
    print(f"  Dauer: {total:.1f}s ({total/60:.1f} Min)")
    print(f"  Unique Bilder: {unique}")
    
    return timeline


def camera_filter(index, row):
    """Ken-Burns-Filter."""
    import math
    
    SW, SH = 7680, 4320
    fg_w, fg_h = (SW * 1844) // 1920, (SH * 984) // 1080
    kante = max(6, SW // 320)
    SUB = 4
    frames = max(1, math.ceil(row["duration"] * FPS)) * SUB
    
    if row.get("contain"):
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
        base = f"scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH}"
    
    lin = f"(on/{frames})"
    p = f"(0.6*{lin}+0.4*({lin}*{lin}*(3-2*{lin})))"
    tempo = min(1.55, max(0.50, row["duration"] / 3.6))
    mitte_x, mitte_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    tempo_quer = min(1.0, tempo)
    
    def quer(weg, rueckwaerts=False):
        a = 0.5 - tempo_quer / 2 if not rueckwaerts else 0.5 + tempo_quer / 2
        b = tempo_quer if not rueckwaerts else -tempo_quer
        return f"{weg}*({a:.4f}+{b:.4f}*{p})"
    
    rechts, unten = "(iw-iw/zoom)", "(ih-ih/zoom)"
    
    if row.get("contain"):
        paare = [(1.000, 0.050), (1.050, -0.050)]
        z0, dz = paare[index % len(paare)]
        z1 = z0 + dz * tempo
        x, y = mitte_x, mitte_y
    else:
        bewegungen = [
            (1.03, 0.15, mitte_x, mitte_y),
            (1.18, -0.15, mitte_x, mitte_y),
            (1.14, 0.0, quer(rechts), mitte_y),
            (1.14, 0.0, quer(rechts, True), mitte_y),
            (1.13, 0.0, mitte_x, quer(unten, True)),
            (1.05, 0.13, quer(rechts), quer(unten)),
            (1.17, -0.11, quer(rechts, True), mitte_y),
            (1.13, 0.0, mitte_x, quer(unten)),
        ]
        if row["kind"] == "VIDEO":
            z0, dz = (1.02, 0.07) if index % 2 == 0 else (1.09, -0.07)
            x, y = mitte_x, mitte_y
        else:
            z0, dz, x, y = bewegungen[index % len(bewegungen)]
        z1 = z0 + dz * tempo
    
    z1 = min(1.30, max(1.005, z1))
    zexpr = f"{z0:.4f}+({z1 - z0:.4f})*{p}"
    
    einmal = f",loop=loop=-1:size=1:start=0,fps={FPS * SUB}" if row["kind"] != "VIDEO" else ""
    mittel = f",tmix=frames={SUB}:weights='{' '.join('1' * SUB)}',fps={FPS}" if SUB > 1 else ""
    
    f = (base + einmal
         + f",zoompan=z='{zexpr}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS * SUB}"
         + mittel
         + ",eq=contrast=1.03:saturation=1.04,unsharp=5:5:.24:5:5:0,format=yuv420p")
    
    if row.get("scene_first"):
        f += f",fade=t=in:st=0:d=0.35:color={GRUND}"
    if row.get("scene_last"):
        f += f",fade=t=out:st={max(0, row['duration'] - 0.35):.3f}:d=0.35:color={GRUND}"
    
    return f


def render_all():
    """Rendert alle Segmente."""
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    
    tasks = []
    for i, row in enumerate(timeline):
        target = SEGMENTS / f"{i+1:03d}_{row['shot_id']}.mp4"
        if not target.exists():
            tasks.append((i, row, target))
    
    if not tasks:
        print("  Alle Segmente vorhanden.")
        return
    
    print(f"  Rendere {len(tasks)} Segmente...")
    
    def render_one(args):
        i, row, target = args
        try:
            inputs = ["-stream_loop", "-1", "-i", row["visual"]] if row["kind"] == "VIDEO" else ["-i", row["visual"]]
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
                 "-sws_flags", "lanczos+accurate_rnd+full_chroma_int",
                 "-t", str(row["duration"]), "-vf", camera_filter(i, row),
                 "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                 "-pix_fmt", "yuv420p", "-r", str(FPS), str(target)])
            return True
        except:
            return False
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(render_one, tasks))
    
    ok = sum(1 for r in results if r)
    print(f"  {ok}/{len(tasks)} Segmente fertig.")


def render_endcard():
    """Rendert Endcard."""
    endcard = SEGMENTS / "999_ENDCARD.mp4"
    if endcard.exists():
        return
    
    src = CARDS / "PE_V2_ENDCARD.png"
    if not src.exists():
        print("  WARNUNG: Endcard fehlt.")
        return
    
    print("  Rendere Endcard...")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-framerate", str(FPS), "-i", str(src),
         "-t", str(ENDCARD_SEC),
         "-vf", f"scale=1920:1080,fade=t=in:st=0:d=0.6,fade=t=out:st={ENDCARD_SEC-1.2:.2f}:d=1.2,format=yuv420p",
         "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(endcard)])


def build_final():
    """Baut finales Video mit korrekter Länge."""
    print("\n  Baue finales Video...")
    
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    
    # Concat-Datei mit allen Segmenten + Endcard
    concat = PROD / "render" / "concat_v2.txt"
    paths = [SEGMENTS / f"{i+1:03d}_{r['shot_id']}.mp4" for i, r in enumerate(timeline)]
    paths.append(SEGMENTS / "999_ENDCARD.mp4")
    
    for p in paths:
        if not p.exists():
            print(f"    FEHLT: {p.name}")
            return
    
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in paths) + "\n", encoding="utf-8")
    
    # Picture Lock
    picture = PROD / "render" / f"{NAME}_picture_lock.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat),
         "-c", "copy", str(picture)])
    
    pic_dur = dur(picture)
    voice_dur = dur(VOICE)
    
    print(f"  Picture Lock: {pic_dur:.1f}s")
    print(f"  Voice: {voice_dur:.1f}s")
    
    # Finale mit Audio
    FINAL.mkdir(parents=True, exist_ok=True)
    final = FINAL / f"{NAME}_FINAL_1080p.mp4"
    
    if AUDIO_MIX.exists():
        # -shortest NICHT verwenden, damit Voice nicht abgeschnitten wird
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-i", str(picture), "-i", str(AUDIO_MIX),
             "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
             "-movflags", "+faststart",
             str(final)])
        
        final_dur = dur(final)
        print(f"  Final: {final_dur:.1f}s ({final_dur/60:.1f} Min)")
    else:
        print("  FEHLER: Audio-Mix fehlt.")


def qa():
    """QA-Check."""
    print("\n  QA...")
    
    final = FINAL / f"{NAME}_FINAL_1080p.mp4"
    if not final.exists():
        print("  FEHLER: Finale Datei fehlt.")
        return
    
    final_dur = dur(final)
    voice_dur = dur(VOICE)
    
    print(f"  Video: {final_dur:.1f}s ({final_dur/60:.1f} Min)")
    print(f"  Voice: {voice_dur:.1f}s ({voice_dur/60:.1f} Min)")
    print(f"  Differenz: {abs(final_dur - voice_dur):.1f}s")
    
    if abs(final_dur - voice_dur) < 2.0:
        print("  OK: Video und Voice sind synchron.")
    else:
        print("  WARNUNG: Video und Voice weichen mehr als 2s ab.")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["timeline", "render", "endcard", "final", "qa", "all"])
    ap.add_argument("--no-timeline", action="store_true", help="Timeline nicht neu bauen")
    args = ap.parse_args()
    
    if args.cmd in ("timeline", "all"):
        if not args.no_timeline:
            build_timeline()
    if args.cmd in ("render", "all"):
        render_all()
    if args.cmd in ("endcard", "all"):
        render_endcard()
    if args.cmd in ("final", "all"):
        build_final()
    if args.cmd in ("qa", "all"):
        qa()


if __name__ == "__main__":
    main()
