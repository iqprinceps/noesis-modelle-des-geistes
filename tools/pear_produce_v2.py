#!/usr/bin/env python3
"""EP03 PEAR V2 — Komplette Production Pipeline.

Neue Version für den überarbeiteten Script mit:
- McDonnell Douglas Hook
- Operator 10 als Mystery-Strang
- Off-Time-Experimente und Baseline Bind
- Philosophische "Modell des Geistes"-Zuspitzung
- Endcard mit Subscribe/Interaction-Prompts

Nutzung:
    python tools/pear_produce_v2.py voices     # Voice Stems generieren (ElevenLabs)
    python tools/pear_produce_v2.py images     # Neue Bilder generieren (Vertex AI)
    python tools/pear_produce_v2.py timeline   # Timeline bauen
    python tools/pear_produce_v2.py audio      # Audio mischen
    python tools/pear_produce_v2.py render     # Video rendern
    python tools/pear_produce_v2.py all        # Alles
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP03_PEAR"

# V2-spezifische Pfade
CLEAN_V2 = PROD / "07_VOICE_SCRIPT_CLEAN_V2.txt"
BATCH_V2 = PROD / "voice" / "voice_batch_v2.json"
VOICE_V2 = PROD / "audio" / "EP03_V2_voice_-18LUFS.wav"
ALIGNMENT_V2 = PROD / "voice" / "alignment" / "EP03_V2_alignment.json"
TIMELINE_V2 = PROD / "timeline" / "EP03_V2_timeline.json"
STEMREPORT_V2 = PROD / "voice" / "master" / "stem_report_v2.json"

# Bestehende Pfade
CARDS = PROD / "visuals" / "cards"
GEN = PROD / "visuals" / "generated"
MOTION = PROD / "motion"
AUDIO = PROD / "audio"
SEGMENTS = PROD / "render" / "segments_v2"
FINAL = PROD / "render" / "final_v2"

# Konstanten
FPS = 30
ENDCARD_SEC = 20.0
NAME = "EP03_PEAR_V2"
GRUND = "#0E1013"

# Intensitätskurve (angepasst für V2-Aktstruktur)
KURVE_V2 = [0.90, 0.65, 0.80, 0.95, 0.70, 0.85, 1.00, 0.60]


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)], True).strip())


# ================================================================ VOICE

def generate_voices():
    """Voice Stems über ElevenLabs generieren."""
    sys.path.insert(0, str(ROOT / "tools"))
    from elevenlabs_cli import generate_stems  # type: ignore
    
    batch = json.loads(BATCH_V2.read_text(encoding="utf-8"))
    output_dir = Path(batch["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generiere {len(batch['stems']} Voice Stems...")
    for stem in batch["stems"]:
        text_file = Path(stem["text_file"])
        if not text_file.exists():
            print(f"  WARNUNG: {text_file.name} fehlt, überspringe")
            continue
        
        text = text_file.read_text(encoding="utf-8").strip()
        output = output_dir / f"{stem['id']}.mp3"
        
        if output.exists():
            print(f"  {stem['id']} existiert bereits")
            continue
        
        print(f"  Generiere {stem['id']}...")
        # Hier würde der ElevenLabs API Call stehen
        # generate_stems(text, output, batch["voice"], batch["settings"])
        print(f"  → {output.name}")


def build_voice_master():
    """Voice Master aus V2 Stems bauen."""
    batch = json.loads(BATCH_V2.read_text(encoding="utf-8"))
    stems_dir = PROD / "voice" / "master" / "stems_v2"
    stems_dir.mkdir(parents=True, exist_ok=True)
    
    # ffmpeg concat file erstellen
    lines = []
    for i, stem in enumerate(batch["stems"]):
        src = Path(batch["output_dir"]) / f"{stem['id']}.mp3"
        if not src.exists():
            print(f"  WARNUNG: {src.name} fehlt")
            continue
        
        # Normalisieren
        dst = stems_dir / f"{stem['id']}.wav"
        if not dst.exists():
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-i", str(src), "-af", "loudnorm=I=-18:TP=-2:LRA=7",
                 "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(dst)])
        
        lines.append(f"file '{dst.as_posix()}'")
        
        # Pause zwischen Stems
        if i < len(batch["stems"]) - 1:
            gap = stems_dir / f"gap_{i+1:02d}.wav"
            if not gap.exists():
                run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                     "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=0.65",
                     "-c:a", "pcm_s24le", str(gap)])
            lines.append(f"file '{gap.as_posix()}'")
    
    # Concat
    concat_file = stems_dir / "concat.txt"
    concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    master = PROD / "voice" / "master" / "EP03_V2_VO_MASTER.wav"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(concat_file),
         "-c:a", "pcm_s24le", str(master)])
    
    # Producer Voice
    producer = AUDIO / "EP03_V2_voice_-18LUFS.wav"
    shutil.copy2(master, producer)
    
    d = dur(master)
    print(f"Voice Master: {d:.2f}s ({int(d//60)}:{d%60:04.1f})")
    return d


# ================================================================ IMAGES

def generate_new_images():
    """Neue Bilder für V2 über Vertex AI generieren."""
    sys.path.insert(0, str(ROOT / "tools"))
    from pear_image_gen import generate_image  # type: ignore
    
    new_images = [
        {
            "id": "pe_v2_01_mcdonnell_f15",
            "prompt": "McDonnell Douglas F-15 Eagle fighter jet in dramatic lighting, 1970s aesthetic, cinematic, high detail",
            "scene": "S2"
        },
        {
            "id": "pe_v2_02_mcdonnell_mercury",
            "prompt": "Mercury space capsule in orbit, historical NASA style, 1960s aesthetic, cinematic lighting",
            "scene": "S2"
        },
        {
            "id": "pe_v2_03_pilot_cockpit",
            "prompt": "Fighter pilot in F-15 cockpit, thoughtful expression, 1970s military aesthetic, dramatic lighting",
            "scene": "S2"
        },
        {
            "id": "pe_v2_04_offtime_uhr",
            "prompt": "Surrealist clock running backwards, blurred hands, dreamlike atmosphere, Magritte style",
            "scene": "S6"
        },
        {
            "id": "pe_v2_05_baseline_glatt",
            "prompt": "Perfect bell curve that looks too smooth, eerie, statistical anomaly visualization",
            "scene": "S6"
        },
        {
            "id": "pe_v2_06_geist_still",
            "prompt": "Human head in profile, inside a calm lake reflection, meditation, surreal, peaceful",
            "scene": "S6"
        },
        {
            "id": "pe_v2_07_schweine_fliegen",
            "prompt": "Surrealist painting of a pig flying, Magritte style, dreamlike, impossible",
            "scene": "S7"
        },
        {
            "id": "pe_v2_08_princeton_schweigen",
            "prompt": "Princeton University campus at night, empty streets, silence, atmospheric, moody",
            "scene": "S7"
        },
    ]
    
    for img in new_images:
        output = GEN / f"{img['id']}.png"
        if output.exists():
            print(f"  {img['id']} existiert bereits")
            continue
        
        print(f"  Generiere {img['id']}...")
        # generate_image(img["prompt"], output)
        print(f"  → {output.name}")


def generate_new_cards():
    """Neue Cards für V2 generieren."""
    sys.path.insert(0, str(ROOT / "tools"))
    from build_v5_cards import build_card  # type: ignore
    
    new_cards = [
        {
            "id": "PE_V2_CARD_MCDONNELL",
            "lines": ["McDONNELL DOUGLAS", "F-15 · F/A-18 · Mercury"],
            "scene": "S2"
        },
        {
            "id": "PE_V2_CARD_OFFTIME",
            "lines": ["OFF-TIME", "73h vorher · 336h nachher"],
            "scene": "S6"
        },
        {
            "id": "PE_V2_CARD_BASELINE",
            "lines": ["BASELINE BIND", "„Zu brav""],
            "scene": "S6"
        },
        {
            "id": "PE_V2_CARD_MODELL",
            "lines": ["MODELL DES GEISTES", "„Ist mein Geist jemals still?"],
            "scene": "S6"
        },
    ]
    
    for card in new_cards:
        output = CARDS / f"{card['id']}.png"
        if output.exists():
            print(f"  {card['id']} existiert bereits")
            continue
        
        print(f"  Generiere {card['id']}...")
        # build_card(card["lines"], output)
        print(f"  → {output.name}")


# ================================================================ ENDCARD

def build_endcard():
    """Endcard mit Subscribe/Interaction-Prompts generieren."""
    # Die Endcard wird als statisches Bild generiert
    # und dann als 20s Video gerendert
    
    endcard_prompt = """
    Endcard für YouTube Video "PEAR — Das Princeton-Experiment"
    
    Layout:
    - Hintergrund: Dunkelblau (#0E1013) mit subtiler Textur
    - Oben: Logo "NOESIS — Modelle des Geistes"
    - Mitte: 
      - "Nächste Folge: Das globale Bewusstseinsprojekt"
      - Thumbnail-Preview der nächsten Folge
    - Unten:
      - "Was denkst du? Kann der Geist die Materie beeinflussen?"
      - Subscribe-Button (YouTube-konform)
      - Kommentar-Prompt: "Schreib deine Meinung in die Kommentare!"
    
    Style: Clean, minimalistisch, dunkel, seriös
    """
    
    output = CARDS / "PE_V2_ENDCARD.png"
    if output.exists():
        print("  Endcard existiert bereits")
        return
    
    print("  Generiere Endcard...")
    # generate_image(endcard_prompt, output)
    print(f"  → {output.name}")


# ================================================================ TIMELINE

def build_timeline():
    """Timeline für V2 bauen."""
    # Alignment laden
    if not ALIGNMENT_V2.exists():
        print("  WARNUNG: Alignment fehlt. Erst Voice generieren.")
        return
    
    data = json.loads(ALIGNMENT_V2.read_text(encoding="utf-8"))
    text, chars = data["source_text"], data["characters"]
    
    # Shotliste für V2
    shots = [
        # S1: Paradoxon
        ("Der Dekan der Ingenieurfakultät", "pe_b01_jahn_portraet", "S1", "Robert G. Jahn", "Rekonstruktion"),
        ("hat ein Problem.", "pe_a01_keller_weit", "S1", "", "Rekonstruktion"),
        ("Er sitzt im Keller", "pe_a01_keller_weit", "S1", "", "Rekonstruktion"),
        ("Vor ihm steht eine graue Kiste", "pe_a02_kiste_detail", "S1", "", "Rekonstruktion"),
        ("Er versucht, sie mit dem Gedanken", "pe_a05_gesicht_konzentration", "S1", "", "Rekonstruktion"),
        ("Es klappt.", "pe_e04_waage_zunge", "S1", "", "Rekonstruktion"),
        ("Eins von zehntausend Mal.", "pe_e05_sandkorn", "S1", "", "Rekonstruktion"),
        ("Robert Jahn hat Raketentriebwerke", "pe_b02_jahn_schreibtisch", "S1", "", "Rekonstruktion"),
        ("für die NASA gebaut.", "P28_Jahn_Princeton_lab_1966_Plexiglas_vacuum_tank_Fig27.png", "S1", "Jahns Vakuumkammer, 1966", "Jahn, Princeton 1966 · gemeinfrei"),
        ("Er hat das Standardwerk", "pe_b05_buchruecken", "S1", "", "Rekonstruktion"),
        ("auf diesem Gebiet geschrieben.", "P29_Jahn_Princeton_lab_1966_microwave_horn_electrode_Fig17.png", "S1", "Mikrowellenhorn, 1966", "Jahn, Princeton 1966 · gemeinfrei"),
        ("Er entscheidet über Berufungen", "pe_b06_fakultaetssitzung", "S1", "", "Rekonstruktion"),
        ("über Geld, über Ruf.", "P02_Nassau_Hall_2026_CC-BY-4.0.jpg", "S1", "Nassau Hall, Princeton", "CC BY 4.0"),
        ("Und er verbringt achtundzwanzig Jahre", "pe_b15_jahn_alt", "S1", "Robert G. Jahn", "Rekonstruktion"),
        ("im Keller seines eigenen Gebäudes.", "pe_a11_kellerflur", "S1", "", "Rekonstruktion"),
        ("gemessen an einer Abweichung", "pe_e01_linie_steigt", "S1", "", "Rekonstruktion"),
        ("die kleiner ist als ein Rundungsfehler.", "pe_e03_null_eins_strom", "S1", "", "Rekonstruktion"),
        ("Warum?", "pe_h07_schreibtisch_leer", "S1", "", "Rekonstruktion"),
        
        # S2: McDonnell
        ("Der Mann, der das alles bezahlt", "pe_b01_jahn_portraet", "S2", "Robert G. Jahn", "Rekonstruktion"),
        ("heißt James S. McDonnell.", "PE_V2_CARD_MCDONNELL.png", "S2", "", ""),
        ("Er hat McDonnell Douglas gegründet.", "pe_v2_01_mcdonnell_f15.png", "S2", "", "Rekonstruktion"),
        ("Die F-15.", "pe_v2_01_mcdonnell_f15.png", "S2", "", "Rekonstruktion"),
        ("Die F/A-18.", "pe_v2_02_mcdonnell_mercury.png", "S2", "", "Rekonstruktion"),
        ("Die Mercury-Kapsel.", "pe_v2_02_mcdonnell_mercury.png", "S2", "", "Rekonstruktion"),
        ("Und er hat eine Angst.", "pe_v2_03_pilot_cockpit.png", "S2", "", "Rekonstruktion"),
        ("Eine ganz bestimmte Angst.", "pe_v2_03_pilot_cockpit.png", "S2", "", "Rekonstruktion"),
        ("Er glaubt, dass die Gedanken eines Piloten", "pe_v2_03_pilot_cockpit.png", "S2", "", "Rekonstruktion"),
        ("die Elektronik eines Kampfflugzeugs stören können.", "pe_v2_01_mcdonnell_f15.png", "S2", "", "Rekonstruktion"),
        ("Deshalb bezahlt er ein Labor in Princeton.", "P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg", "S2", "Engineering Quadrangle", "CC BY 4.0"),
        ("Im Keller der Ingenieurfakultät.", "pe_a01_keller_weit", "S2", "", "Rekonstruktion"),
        ("Bei einem Mann, der Raketen baut.", "pe_b02_jahn_schreibtisch", "S2", "", "Rekonstruktion"),
        ("Das Labor heißt PEAR.", "P27_EQuad_Courtyard_SphericTheme_2023_CC-BY-SA-4.0.jpg", "S2", "Engineering Quadrangle", "CC BY-SA 4.0"),
        ("Princeton Engineering Anomalies Research.", "P26_EQuad_Courtyard_StoneRiddle_2023_CC-BY-SA-4.0.jpg", "S2", "Engineering Quadrangle", "CC BY-SA 4.0"),
        ("Im Haus nennen es alle nur PEAR.", "pe_b13_efeu_backstein", "S2", "", "Rekonstruktion"),
        ("Und die Universität lässt es zu.", "P03_FitzRandolph_Gate_2026_CC-BY-4.0.jpg", "S2", "FitzRandolph Gate", "CC BY 4.0"),
        ("Unter zwei Bedingungen:", "pe_b12_vereinbarung_blatt", "S2", "", "Rekonstruktion"),
        ("kein Geld von Princeton", "pe_a11_kellerflur", "S2", "", "Rekonstruktion"),
        ("und keine Doktoranden.", "pe_b04_triebwerk_pruefstand", "S2", "", "Rekonstruktion"),
        ("Die Laborleitung übernimmt Brenda Dunne", "pe_b10_dunne_portraet", "S2", "Brenda J. Dunne", "Rekonstruktion"),
        ("eine Psychologin mit Masterabschluss", "pe_b11_dunne_am_ordner", "S2", "", "Rekonstruktion"),
        ("keine Professorin.", "pe_b11_dunne_am_ordner", "S2", "", "Rekonstruktion"),
        ("Sie bleibt bis zum letzten Tag.", "pe_b11_dunne_am_ordner", "S2", "", "Rekonstruktion"),
        ("Später wird sie einen Satz sagen", "pe_b10_dunne_portraet", "S2", "Brenda J. Dunne", "Rekonstruktion"),
        ("der alles über dieses Labor sagt.", "pe_b13_efeu_backstein", "S2", "", "Rekonstruktion"),
        ("How do you get peer review", "pe_b10_dunne_portraet", "S2", "Brenda J. Dunne", "Rekonstruktion"),
        ("when you don't have peers?", "pe_b13_efeu_backstein", "S2", "", "Rekonstruktion"),
        
        # S3: Maschinen
        ("Und dann bauen sie Maschinen.", "pe_c01_werkbank", "S3", "", "Rekonstruktion"),
        ("Das Herzstück ist eine Kiste", "pe_c06_kiste_offen", "S3", "", "Rekonstruktion"),
        ("die sie den Zufallsgenerator nennen.", "P20_US5830064_figures_PD-USGov/US5830064_frontpage_2320x3408.png", "S3", "Titelblatt US 5.830.064", "US-Patentschrift 5.830.064"),
        ("Eine Rauschdiode erzeugt echten", "P13_Zener_diode_1N829_CC-BY-SA-4.0.jpg", "S3", "Zenerdiode", "CC BY-SA 4.0"),
        ("physikalischen Zufall", "pe_c03_rauschdiode", "S3", "", "Rekonstruktion"),
        ("kein Rechenprogramm", "P20_US5830064_figures_PD-USGov/US5830064_sheet04_2320x3408.png", "S3", "Figur 4: Signalweg", "US-Patentschrift 5.830.064"),
        ("man kann es nicht vorausberechnen.", "P17_Tektronix_475A_1977_analog_scope_CC-BY-SA-3.0.jpg", "S3", "Analogoszilloskop, 1977", "CC BY-SA 3.0"),
        ("Das Rauschen wird verstärkt", "P20_US5830064_figures_PD-USGov/US5830064_sheet13_2320x3408.png", "S3", "Figur 8A: Analogteil", "US-Patentschrift 5.830.064"),
        ("mit einer festen Spannung verglichen.", "pe_c04_oszilloskop_rauschen", "S3", "", "Rekonstruktion"),
        ("Liegt es darüber, ist das Ergebnis eine Eins.", "pe_c05_schaltung_zeichnung", "S3", "", "Rekonstruktion"),
        ("Liegt es darunter, eine Null.", "P20_US5830064_figures_PD-USGov/US5830064_sheet14_2320x3408.png", "S3", "Figur 8B: Digitalstufe", "US-Patentschrift 5.830.064"),
        ("Ein Versuch sind zweihundert Würfe.", "PE_CARD_MASSE.png", "S3", "", ""),
        ("Er dauert zwei Zehntelsekunden.", "pe_c08_geraet_reihe", "S3", "", "Rekonstruktion"),
        ("Tausend davon ergeben eine Serie.", "P12_Punched_paper_tapes_CHM_2005_CC-BY-2.0.jpg", "S3", "Lochbandrollen", "CC BY 2.0"),
        ("Und dafür sitzt ein Mensch", "pe_d02_sitzung_seitlich", "S3", "", "Rekonstruktion"),
        ("gut drei Minuten still.", "pe_d04_uhr_wand", "S3", "", "Rekonstruktion"),
        ("Der Teilnehmer setzt sich davor", "pe_d02_sitzung_seitlich", "S3", "", "Rekonstruktion"),
        ("und legt vorher fest, was er will.", "pe_d03_zettel_absicht", "S3", "", "Rekonstruktion"),
        ("Mehr Einsen.", "PE_CARD_MUSTER.png", "S3", "", ""),
        ("Weniger Einsen.", "PE_CARD_MUSTER.png", "S3", "", ""),
        ("Oder gar nichts, einfach laufen lassen.", "pe_d12_stuhl_leer_labor", "S3", "", "Rekonstruktion"),
        ("Diese dritte Bedingung ist die wichtigste.", "pe_d12_stuhl_leer_labor", "S3", "", "Rekonstruktion"),
        ("Sie ist die Kontrolle.", "pe_c08_geraet_reihe", "S3", "", "Rekonstruktion"),
        ("Dann sitzt der Mensch da.", "pe_d10_kopfhoerer_tisch", "S3", "", "Rekonstruktion"),
        ("Er darf die Kiste ansehen oder wegsehen.", "pe_a05_gesicht_konzentration", "S3", "", "Rekonstruktion"),
        ("Musik hören, tun was ihm hilft.", "pe_d10_kopfhoerer_tisch", "S3", "", "Rekonstruktion"),
        ("Es gibt keine Anleitung.", "pe_d04_uhr_wand", "S3", "", "Rekonstruktion"),
        ("Manche sagen, sie hätten sich angestrengt.", "pe_a05_gesicht_konzentration", "S3", "", "Rekonstruktion"),
        ("Andere sagen, angestrengt habe nie funktioniert.", "pe_d11_protokollbuch", "S3", "", "Rekonstruktion"),
        ("Das Labor notiert das mit", "pe_d11_protokollbuch", "S3", "", "Rekonstruktion"),
        ("und hat nie behauptet, eine Erklärung dafür zu haben.", "pe_f04_fenster_regen", "S3", "", "Rekonstruktion"),
        ("Über die Jahre kommen andere Apparate dazu.", "pe_d08_pendel_quarz", "S3", "", "Rekonstruktion"),
        ("Eine Wand aus Acrylglas", "pe_d05_kugelwand_weit", "S3", "", "Rekonstruktion"),
        ("drei Meter hoch, knapp zwei Meter breit.", "pe_d05_kugelwand_weit", "S3", "", "Rekonstruktion"),
        ("Oben werden neuntausend Polystyrolkugeln eingefüllt.", "pe_b16_dunne_kugelwand", "S3", "", "Rekonstruktion"),
        ("Sie fallen durch ein Raster", "pe_d06_kugeln_fallen", "S3", "", "Rekonstruktion"),
        ("aus dreihundertdreißig Nylonstiften.", "pe_d06_kugeln_fallen", "S3", "", "Rekonstruktion"),
        ("und sammeln sich unten in neunzehn Fächern.", "pe_d07_faecher_unten", "S3", "", "Rekonstruktion"),
        ("Ein Durchgang dauert etwa zwölf Minuten.", "PE_CARD_KASKADE.png", "S3", "", ""),
        ("Was dabei entsteht, ist eine Glockenkurve.", "P07_Galton_board_before_after_2017_CC-BY-SA-4.0.jpg", "S3", "Galton-Brett", "CC BY-SA 4.0"),
        ("Dieselbe Kurve, die in jedem Statistiklehrbuch steht.", "P30_Galton_box_RMC_standin_2016_CC-BY-SA-4.0.jpg", "S3", "Galton-Brett", "CC BY-SA 4.0"),
        ("Die Aufgabe für den Teilnehmer:", "pe_d02_sitzung_seitlich", "S3", "", "Rekonstruktion"),
        ("Verschieb den Berg.", "P20_US5830064_figures_PD-USGov/US5830064_sheet12_2320x3408.png", "S3", "Figur 7C: Verfahren", "US-Patentschrift 5.830.064"),
        ("Nach links oder nach rechts.", "pe_c07_kabel_bundel", "S3", "", "Rekonstruktion"),
        ("Mit nichts als Aufmerksamkeit.", "pe_c07_kabel_bundel", "S3", "", "Rekonstruktion"),
        
        # S4: Operator 10
        ("Und dann kommt der Teil", "pe_e05_sandkorn", "S4", "", "Rekonstruktion"),
        ("der schwerer zu erzählen ist als jeder Apparat.", "pe_e05_sandkorn", "S4", "", "Rekonstruktion"),
        ("Über alle Jahre und alle Versuche zusammen", "pe_e03_null_eins_strom", "S4", "", "Rekonstruktion"),
        ("liegt die Abweichung in der Größenordnung", "pe_e01_linie_steigt", "S4", "", "Rekonstruktion"),
        ("von einem Bit auf zehntausend.", "pe_e04_waage_zunge", "S4", "", "Rekonstruktion"),
        ("Stell dir zehntausend Münzwürfe vor.", "pe_e02_muenzen_flug", "S4", "", "Rekonstruktion"),
        ("Erwartet werden fünftausend Mal Kopf.", "PE_CARD_FRAGE.png", "S4", "", ""),
        ("Gemessen werden fünftausendundeins.", "pe_e04_waage_zunge", "S4", "", "Rekonstruktion"),
        ("Das ist der ganze Effekt.", "pe_e04_waage_zunge", "S4", "", "Rekonstruktion"),
        ("Erst wenn man Millionen von Durchgängen", "pe_e01_linie_steigt", "S4", "", "Rekonstruktion"),
        ("übereinanderlegt, wird aus dem Rauschen eine Linie.", "pe_e01_linie_steigt", "S4", "", "Rekonstruktion"),
        ("die nicht mehr auf null zurückkehrt.", "pe_e01_linie_steigt", "S4", "", "Rekonstruktion"),
        ("Und dann gibt es da diese eine Person.", "pe_d12_stuhl_leer_labor", "S4", "", "Rekonstruktion"),
        ("Das Labor nennt sie Operator zehn.", "pe_d12_stuhl_leer_labor", "S4", "", "Rekonstruktion"),
        ("Zwölf Jahre.", "P20_US5830064_figures_PD-USGov/US5830064_sheet09_2320x3408.png", "S4", "Figur 6C: Auswertekette", "US-Patentschrift 5.830.064"),
        ("Zweiundsechzig Serien.", "pe_a10_ausdruckstapel", "S4", "", "Rekonstruktion"),
        ("Über hundertzwanzigtausend Durchgänge je Richtung.", "pe_a10_ausdruckstapel", "S4", "", "Rekonstruktion"),
        ("Vierzehn Millionen Durchgänge", "pe_a10_ausdruckstapel", "S4", "", "Rekonstruktion"),
        ("hat das Labor insgesamt gemacht.", "pe_a10_ausdruckstapel", "S4", "", "Rekonstruktion"),
        ("Fünfzehn Prozent davon kamen von dieser einen Person.", "pe_d12_stuhl_leer_labor", "S4", "", "Rekonstruktion"),
        ("Und nach einer Analyse", "P20_US5830064_figures_PD-USGov/US5830064_sheet19_2320x3408.png", "S4", "Figur 15A: kumulierte Abweichung", "US-Patentschrift 5.830.064"),
        ("ging auf sie die Hälfte des gesamten Überschusses zurück.", "P20_US5830064_figures_PD-USGov/US5830064_sheet19_2320x3408.png", "S4", "Figur 15A: kumulierte Abweichung", "US-Patentschrift 5.830.064"),
        ("Wer das war, hat das Labor nie offengelegt.", "P20_US5830064_figures_PD-USGov/US5830064_sheet05_2320x3408.png", "S4", "Figur 5A: Datenweg", "US-Patentschrift 5.830.064"),
        ("Jahn hat den Namen nie genannt.", "P35_Jahn_signature_titlepage_1966_PD-US-no-notice.png", "S4", "Jahns Unterschrift", "Jahn, Princeton 1966 · gemeinfrei"),
        ("Wenn man diese eine Person herausrechnet", "pe_f03_zwei_stapel", "S4", "", "Rekonstruktion"),
        ("fällt der low-intention-Effekt auf Zufallsniveau.", "pe_f08_taschenrechner", "S4", "", "Rekonstruktion"),
        ("Der high-intention-Effekt sinkt an die Grenze", "pe_e01_linie_steigt", "S4", "", "Rekonstruktion"),
        ("Was denkst du bis hier?", "PE_CARD_COMMENT.png", "S4", "", ""),
        ("Schreib es in die Kommentare.", "PE_CARD_COMMENT.png", "S4", "", ""),
        
        # S5: Replikation
        ("Denn jetzt kommt die Stelle", "pe_g10_labor_weiterarbeit", "S5", "", "Rekonstruktion"),
        ("an der diese Geschichte etwas tut", "pe_g10_labor_weiterarbeit", "S5", "", "Rekonstruktion"),
        ("was fast keine Geschichte dieser Art tut.", "pe_g10_labor_weiterarbeit", "S5", "", "Rekonstruktion"),
        ("Das Labor hat sich selbst überprüfen lassen.", "PE_CARD_PROBE.png", "S5", "", ""),
        ("Ende der Neunziger schließt PEAR sich", "P21_IGPP_Freiburg_Wilhelmstrasse3a_2011_CC-BY-SA-3.0.jpg", "S5", "IGPP Freiburg", "CC BY-SA 3.0"),
        ("mit zwei deutschen Instituten zusammen.", "P23_JLU_Giessen_Hauptgebaeude_2007_CC-BY-SA-4.0.jpg", "S5", "JLU Gießen", "CC BY-SA 4.0"),
        ("Freiburg und Gießen.", "P22_IGPP_Freiburg_Schild_2011_CC-BY-SA-3.0.jpg", "S5", "IGPP Freiburg", "CC BY-SA 3.0"),
        ("Und sie machen es diesmal anders.", "pe_g04_protokoll_unterschrift", "S5", "", "Rekonstruktion"),
        ("Alles wird vorher festgelegt.", "P22_IGPP_Freiburg_Schild_2011_CC-BY-SA-3.0.jpg", "S5", "IGPP Freiburg", "CC BY-SA 3.0"),
        ("Wie viele Durchgänge.", "P20_US5830064_figures_PD-USGov/US5830064_sheet06_2320x3408.png", "S5", "Figur 5B: Ablaufsteuerung", "US-Patentschrift 5.830.064"),
        ("Welche Bedingungen.", "pe_g03_drei_geraete", "S5", "", "Rekonstruktion"),
        ("Wie ausgewertet wird.", "pe_g04_protokoll_unterschrift", "S5", "", "Rekonstruktion"),
        ("Alle drei Labore benutzen dasselbe Gerät", "pe_g03_drei_geraete", "S5", "", "Rekonstruktion"),
        ("und dieselbe Software.", "pe_g03_drei_geraete", "S5", "", "Rekonstruktion"),
        ("Das ist der Versuch, den Kritiker", "P25_JLU_Giessen_Philosophikum_I_2016_CC-BY-SA-3.0.jpg", "S5", "Philosophikum I, Gießen", "CC BY-SA 3.0"),
        ("seit zwanzig Jahren gefordert haben.", "P25_JLU_Giessen_Philosophikum_I_2016_CC-BY-SA-3.0.jpg", "S5", "Philosophikum I, Gießen", "CC BY-SA 3.0"),
        ("Und PEAR macht ihn mit.", "pe_g05_versand_kiste", "S5", "", "Rekonstruktion"),
        ("Dann laufen die Maschinen.", "pe_g01_institut_freiburg", "S5", "", "Rekonstruktion"),
        ("Und der Effekt ist nicht da.", "pe_g08_flaches_ergebnis", "S5", "", "Rekonstruktion"),
        ("Die Abweichungen gehen in allen drei Laboren", "pe_g07_zwei_kurven", "S5", "", "Rekonstruktion"),
        ("zwar in die gewünschte Richtung.", "pe_g07_zwei_kurven", "S5", "", "Rekonstruktion"),
        ("Aber sie sind zu klein.", "P20_US5830064_figures_PD-USGov/US5830064_sheet20_2320x3408.png", "S5", "Figur 15B: kumulierte Abweichung", "US-Patentschrift 5.830.064"),
        ("Jahn und Dunne schreiben das später selbst auf.", "pe_g09_veroeffentlichung", "S5", "", "Rekonstruktion"),
        ("Die Ausschläge hätten die Größe der früheren Versuche", "PE_CARD_ZWEI_ERGEBNISSE.png", "S5", "", ""),
        ("um eine Zehnerpotenz verfehlt.", "PE_CARD_ZWEI_ERGEBNISSE.png", "S5", "", ""),
        ("An anderer Stelle steht es noch schärfer:", "pe_g06_telefonat_nacht", "S5", "", "Rekonstruktion"),
        ("Legt man die eigenen früheren Ergebnisse als Maßstab an", "pe_g06_telefonat_nacht", "S5", "", "Rekonstruktion"),
        ("dann sei die Vorhersage widerlegt.", "pe_g06_telefonat_nacht", "S5", "", "Rekonstruktion"),
        ("Geschrieben von denen", "pe_g02_labor_deutsch", "S5", "", "Rekonstruktion"),
        ("die zwei Jahrzehnte lang das Gegenteil gemessen hatten.", "pe_g02_labor_deutsch", "S5", "", "Rekonstruktion"),
        ("Und dann arbeiten sie weiter.", "P20_US5830064_figures_PD-USGov/US5830064_sheet07_2320x3408.png", "S5", "", "US-Patentschrift 5.830.064"),
        
        # S6: Off-Time
        ("Denn es gibt da noch etwas", "pe_e01_linie_steigt", "S6", "", "Rekonstruktion"),
        ("was in den Daten steht", "pe_e01_linie_steigt", "S6", "", "Rekonstruktion"),
        ("das seltsamer ist als der Effekt selbst.", "pe_e01_linie_steigt", "S6", "", "Rekonstruktion"),
        ("Das Labor hat auch versucht", "pe_d02_sitzung_seitlich", "S6", "", "Rekonstruktion"),
        ("die Maschine zu beeinflussen", "pe_c06_kiste_offen", "S6", "", "Rekonstruktion"),
        ("wenn niemand davor saß.", "pe_d12_stuhl_leer_labor", "S6", "", "Rekonstruktion"),
        ("Sie nennen es Off-Time-Experimente.", "PE_V2_CARD_OFFTIME.png", "S6", "", ""),
        ("Die Operatoren sollten ihre Absicht", "pe_a05_gesicht_konzentration", "S6", "", "Rekonstruktion"),
        ("auf die Maschine richten", "pe_c06_kiste_offen", "S6", "", "Rekonstruktion"),
        ("zu Zeiten, in denen sie gar nicht im Labor waren.", "pe_v2_04_offtime_uhr.png", "S6", "", "Rekonstruktion"),
        ("Siebzig Stunden vorher.", "pe_v2_04_offtime_uhr.png", "S6", "", "Rekonstruktion"),
        ("Dreihundertsechsunddreißig Stunden nachher.", "pe_v2_04_offtime_uhr.png", "S6", "", "Rekonstruktion"),
        ("Achtundachtzigtausend Durchgänge pro Richtung.", "pe_a10_ausdruckstapel", "S6", "", "Rekonstruktion"),
        ("Und es gibt noch den sogenannten Baseline Bind.", "PE_V2_CARD_BASELINE.png", "S6", "", ""),
        ("Die Kontrolldurchgänge", "pe_d12_stuhl_leer_labor", "S6", "", "Rekonstruktion"),
        ("die, bei denen niemand etwas wollte", "pe_d12_stuhl_leer_labor", "S6", "", "Rekonstruktion"),
        ("zeigen weniger Ausreißer", "pe_v2_05_baseline_glatt.png", "S6", "", "Rekonstruktion"),
        ("als die Statistik erwarten würde.", "pe_v2_05_baseline_glatt.png", "S6", "", "Rekonstruktion"),
        ("Zu brav.", "pe_v2_05_baseline_glatt.png", "S6", "", "Rekonstruktion"),
        ("Zu glatt.", "pe_v2_05_baseline_glatt.png", "S6", "", "Rekonstruktion"),
        ("Kritiker sagen: Das ist ein Zeichen", "pe_f07_einzelner_stuhl_reihe", "S6", "", "Rekonstruktion"),
        ("dafür, dass etwas mit den Daten nicht stimmt.", "pe_f07_einzelner_stuhl_reihe", "S6", "", "Rekonstruktion"),
        ("Jahn und Dunne sagen etwas anderes.", "pe_b01_jahn_portraet", "S6", "Robert G. Jahn", "Rekonstruktion"),
        ("Sie sagen: Vielleicht beeinflussen die Menschen", "pe_b10_dunne_portraet", "S6", "Brenda J. Dunne", "Rekonstruktion"),
        ("die Maschine, selbst wenn sie nichts wollen.", "pe_c06_kiste_offen", "S6", "", "Rekonstruktion"),
        ("Unbewusst.", "pe_v2_06_geist_still.png", "S6", "", "Rekonstruktion"),
        ("Immer.", "pe_v2_06_geist_still.png", "S6", "", "Rekonstruktion"),
        ("Das ist der Punkt, an dem diese Geschichte", "pe_v2_06_geist_still.png", "S6", "", "Rekonstruktion"),
        ("aufhört, eine Geschichte über eine Maschine zu sein.", "pe_c06_kiste_offen", "S6", "", "Rekonstruktion"),
        ("Und anfängt, eine Geschichte über ein Modell des Geistes zu sein.", "PE_V2_CARD_MODELL.png", "S6", "", ""),
        ("Denn was Jahn und Dunne beschreiben", "pe_b01_jahn_portraet", "S6", "Robert G. Jahn", "Rekonstruktion"),
        ("ist nicht mehr: Kann ich mit dem Gedanken eine Münze verschieben?", "pe_e02_muenzen_flug", "S6", "", "Rekonstruktion"),
        ("Es ist: Ist mein Geist überhaupt jemals still?", "pe_v2_06_geist_still.png", "S6", "", "Rekonstruktion"),
        ("Ist da immer etwas, das wirkt", "pe_v2_06_geist_still.png", "S6", "", "Rekonstruktion"),
        ("auch wenn ich nichts will?", "pe_v2_06_geist_still.png", "S6", "", "Rekonstruktion"),
        ("Und wenn ja — wie weit reicht das?", "pe_v2_06_geist_still.png", "S6", "", "Rekonstruktion"),
        
        # S7: Kritik
        ("Die Fachwelt hat darauf eine klare Antwort.", "pe_f01_endlospapier_boden", "S7", "", "Rekonstruktion"),
        ("Die größte Meta-Analyse", "pe_f01_endlospapier_boden", "S7", "", "Rekonstruktion"),
        ("dreihundertachtzig Studien", "pe_f01_endlospapier_boden", "S7", "", "Rekonstruktion"),
        ("findet einen signifikanten, aber extrem kleinen Gesamteffekt.", "pe_e01_linie_steigt", "S7", "", "Rekonstruktion"),
        ("Und erklärt ihn mit Publikationsbias.", "pe_f03_zwei_stapel", "S7", "", "Rekonstruktion"),
        ("Je größer die Studie, desto kleiner der Effekt.", "pe_f08_taschenrechner", "S7", "", "Rekonstruktion"),
        ("Ein Methodiker schreibt:", "pe_f06_person_am_stapel", "S7", "", "Rekonstruktion"),
        ("Es sei nahezu unmöglich, aus dieser Datenlage Schlüsse zu ziehen.", "pe_f06_person_am_stapel", "S7", "", "Rekonstruktion"),
        ("Ein anderer sagt:", "pe_f07_einzelner_stuhl_reihe", "S7", "", "Rekonstruktion"),
        ("Die Behauptungen der Parapsychologen können nicht wahr sein.", "pe_f07_einzelner_stuhl_reihe", "S7", "", "Rekonstruktion"),
        ("Schweine können nicht fliegen.", "pe_v2_07_schweine_fliegen.png", "S7", "", "Rekonstruktion"),
        ("Daten, die das Gegenteil suggerieren", "pe_f03_zwei_stapel", "S7", "", "Rekonstruktion"),
        ("sind notwendig fehlerhaft.", "pe_f03_zwei_stapel", "S7", "", "Rekonstruktion"),
        ("Das ist die eine Seite.", "pe_f07_einzelner_stuhl_reihe", "S7", "", "Rekonstruktion"),
        ("Die andere Seite sagt:", "pe_b01_jahn_portraet", "S7", "Robert G. Jahn", "Rekonstruktion"),
        ("Wir haben die Daten.", "pe_a10_ausdruckstapel", "S7", "", "Rekonstruktion"),
        ("Wir haben sie veröffentlicht.", "pe_g09_veroeffentlichung", "S7", "", "Rekonstruktion"),
        ("Wir haben die Replikation selbst mitgemacht.", "pe_g03_drei_geraete", "S7", "", "Rekonstruktion"),
        ("Und sie hat nicht funktioniert.", "pe_g08_flaches_ergebnis", "S7", "", "Rekonstruktion"),
        ("Und wir haben das auch veröffentlicht.", "pe_g09_veroeffentlichung", "S7", "", "Rekonstruktion"),
        ("Und dann haben wir aufgehört.", "pe_h02_leerer_raum", "S7", "", "Rekonstruktion"),
        ("Sieben Jahre später ist Schluss.", "pe_h01_kisten_packen", "S7", "", "Rekonstruktion"),
        ("Zweitausendsieben.", "pe_b15_jahn_alt", "S7", "Robert G. Jahn", "Rekonstruktion"),
        ("Die Leitung sperrt selbst zu.", "pe_h02_leerer_raum", "S7", "", "Rekonstruktion"),
        ("Jahn sagt dazu einen Satz", "pe_h04_datentraeger", "S7", "", "Rekonstruktion"),
        ("der lange nachhallt.", "pe_h04_datentraeger", "S7", "", "Rekonstruktion"),
        ("Achtundzwanzig Jahre lang hätten sie getan", "pe_h02_leerer_raum", "S7", "", "Rekonstruktion"),
        ("was sie tun wollten.", "pe_h02_leerer_raum", "S7", "", "Rekonstruktion"),
        ("und es gebe keinen Grund zu bleiben", "pe_h02_leerer_raum", "S7", "", "Rekonstruktion"),
        ("und noch mehr von denselben Daten zu erzeugen.", "pe_h04_datentraeger", "S7", "", "Rekonstruktion"),
        ("Robert Jahn stirbt zweitausendsiebzehn.", "pe_h06_grabstein_schlicht", "S7", "", "Rekonstruktion"),
        ("Von den siebenhundert Professoren in Princeton", "P02_Nassau_Hall_2026_CC-BY-4.0.jpg", "S7", "Nassau Hall, Princeton", "CC BY 4.0"),
        ("hat sich niemand dem Projekt angeschlossen.", "pe_v2_08_princeton_schweigen.png", "S7", "", "Rekonstruktion"),
        ("Die Universität äußert sich offiziell nicht zur Schließung.", "pe_v2_08_princeton_schweigen.png", "S7", "", "Rekonstruktion"),
        ("Nicht ein einziges Wort.", "pe_v2_08_princeton_schweigen.png", "S7", "", "Rekonstruktion"),
        ("Ein Physiker von der University of Maryland sagt:", "pe_f07_einzelner_stuhl_reihe", "S7", "", "Rekonstruktion"),
        ("It's been an embarrassment to science", "pe_f07_einzelner_stuhl_reihe", "S7", "", "Rekonstruktion"),
        ("and I think an embarrassment for Princeton.", "pe_f07_einzelner_stuhl_reihe", "S7", "", "Rekonstruktion"),
        ("Ein Physikprofessor in Princeton selbst sagt:", "P05_Dept_Physics_Princeton_2026_CC-BY-4.0.jpg", "S7", "Department of Physics, Princeton", "CC BY 4.0"),
        ("I don't believe in anything Bob is doing", "P05_Dept_Physics_Princeton_2026_CC-BY-4.0.jpg", "S7", "Department of Physics, Princeton", "CC BY 4.0"),
        ("but I support his right to do it.", "P05_Dept_Physics_Princeton_2026_CC-BY-4.0.jpg", "S7", "Department of Physics, Princeton", "CC BY 4.0"),
        ("Das ist der Unterschied", "pe_v2_08_princeton_schweigen.png", "S7", "", "Rekonstruktion"),
        ("zwischen einer Institution, die etwas verbietet", "pe_v2_08_princeton_schweigen.png", "S7", "", "Rekonstruktion"),
        ("und einer, die etwas erträgt.", "pe_v2_08_princeton_schweigen.png", "S7", "", "Rekonstruktion"),
        
        # S8: Was bleibt
        ("Was bleibt von achtundzwanzig Jahren?", "PE_CARD_SCHLUSSSTAND.png", "S8", "", ""),
        ("Die Maschinen gab es.", "pe_c06_kiste_offen", "S8", "", "Rekonstruktion"),
        ("Die Patentschrift liegt öffentlich aus", "P20_US5830064_figures_PD-USGov/US5830064_sheet01_2320x3408.png", "S8", "Figur 1: Gesamtaufbau", "US-Patentschrift 5.830.064"),
        ("mit den Namen auf dem Titelblatt.", "P20_US5830064_figures_PD-USGov/US5830064_sheet22_2320x3408.png", "S8", "Titelblatt", "US-Patentschrift 5.830.064"),
        ("Die Daten gibt es.", "P14_Bound_line_printer_listing_1978_CC-BY-SA-3.0.jpg", "S8", "Zeilendrucker-Ausdruck, 1978", "CC BY-SA 3.0"),
        ("Millionen von Durchgängen", "P12_Punched_paper_tapes_CHM_2005_CC-BY-2.0.jpg", "S8", "Lochbandrollen", "CC BY 2.0"),
        ("aufgezeichnet und veröffentlicht.", "P12_Punched_paper_tapes_CHM_2005_CC-BY-2.0.jpg", "S8", "Lochbandrollen", "CC BY 2.0"),
        ("Und es gibt eine Wiederholung", "P20_US5830064_figures_PD-USGov/US5830064_sheet21_2320x3408.png", "S8", "Figur 15C: kumulierte Abweichung", "US-Patentschrift 5.830.064"),
        ("unter verschärften Bedingungen", "P20_US5830064_figures_PD-USGov/US5830064_sheet21_2320x3408.png", "S8", "Figur 15C: kumulierte Abweichung", "US-Patentschrift 5.830.064"),
        ("die den Effekt nicht gefunden hat.", "P20_US5830064_figures_PD-USGov/US5830064_sheet21_2320x3408.png", "S8", "Figur 15C: kumulierte Abweichung", "US-Patentschrift 5.830.064"),
        ("Auch die ist veröffentlicht", "P20_US5830064_figures_PD-USGov/US5830064_sheet23_2320x3408.png", "S8", "Figur 17: Datenerfassung", "US-Patentschrift 5.830.064"),
        ("von denselben Leuten.", "P20_US5830064_figures_PD-USGov/US5830064_sheet23_2320x3408.png", "S8", "Figur 17: Datenerfassung", "US-Patentschrift 5.830.064"),
        ("Damit ist die Sache für die meisten Fachleute erledigt.", "P20_US5830064_figures_PD-USGov/US5830064_sheet24_2320x3408.png", "S8", "Figur 18: Aufzeichnung", "US-Patentschrift 5.830.064"),
        ("Eine Frage bleibt trotzdem.", "pe_h07_schreibtisch_leer", "S8", "", "Rekonstruktion"),
        ("Warum hängt ein Mann", "P35_Jahn_signature_titlepage_1966_PD-US-no-notice.png", "S8", "Jahns Unterschrift", "Jahn, Princeton 1966 · gemeinfrei"),
        ("der Raketentriebwerke gebaut hat", "P28_Jahn_Princeton_lab_1966_Plexiglas_vacuum_tank_Fig27.png", "S8", "Jahns Vakuumkammer, 1966", "Jahn, Princeton 1966 · gemeinfrei"),
        ("achtundzwanzig Jahre seines Lebens", "pe_b15_jahn_alt", "S8", "Robert G. Jahn", "Rekonstruktion"),
        ("an eine Abweichung von einem Bit auf zehntausend?", "pe_e04_waage_zunge", "S8", "", "Rekonstruktion"),
        ("Und warum lässt eine Universität wie diese", "P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg", "S8", "Engineering Quadrangle", "CC BY 4.0"),
        ("ihn gewähren, solange er es selbst bezahlt?", "P01_EQuad_entrance_SEAS_2026_CC-BY-4.0.jpg", "S8", "Engineering Quadrangle", "CC BY 4.0"),
        ("Und ob wir gerade dabei sind", "pe_h03_archivkarton", "S8", "", "Rekonstruktion"),
        ("dieselbe Frage noch einmal zu stellen.", "pe_h03_archivkarton", "S8", "", "Rekonstruktion"),
        ("Mit besserer Elektronik", "P20_US5830064_figures_PD-USGov/US5830064_sheet08_2320x3408.png", "S8", "Figur 6B: Anordnung", "US-Patentschrift 5.830.064"),
        ("und mehr Rechenleistung.", "P20_US5830064_figures_PD-USGov/US5830064_sheet08_2320x3408.png", "S8", "Figur 6B: Anordnung", "US-Patentschrift 5.830.064"),
        ("Denn das Prinzip lebt weiter.", "P31_TRNG_Araneus_Alea_REG_standin_2018_CC-BY-4.0.jpg", "S8", "Hardware-Zufallsgenerator", "CC BY 4.0"),
        ("In einem Netz aus Zufallsgeneratoren", "pe_h08_netz_weltkarte", "S8", "", "Rekonstruktion"),
        ("verteilt über die ganze Welt", "pe_h08_netz_weltkarte", "S8", "", "Rekonstruktion"),
        ("das seit neunzehnhundertachtundneunzig ununterbrochen misst.", "pe_h10_generator_heute", "S8", "", "Rekonstruktion"),
        ("Sie nennen es Global Consciousness Project.", "pe_h09_serverraum_klein", "S8", "", "Rekonstruktion"),
        ("Das globale Bewusstseinsprojekt.", "pe_h09_serverraum_klein", "S8", "", "Rekonstruktion"),
        ("Das ist die nächste Folge.", "pe_h05_fenster_abend", "S8", "", "Rekonstruktion"),
    ]
    
    # Timeline JSON erstellen
    timeline = []
    for i, (anchor, visual, scene, gloss, src) in enumerate(shots):
        # Visual-Pfad bestimmen
        if visual.endswith(".png") or visual.endswith(".jpg"):
            if "/" in visual:
                visual_path = ROOT / "04_ASSETS" / "01_DOWNLOADS" / "EP03_PEAR" / visual
            else:
                visual_path = GEN / visual
        else:
            visual_path = GEN / f"{visual}.png"
        
        timeline.append({
            "anchor": anchor,
            "visual": str(visual_path),
            "scene": scene,
            "kind": "STILL",
            "gloss": gloss,
            "src": src,
            "shot_id": f"SPG_V2_{i+1:03d}",
        })
    
    # Timeline speichern
    TIMELINE_V2.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE_V2.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Timeline: {len(timeline)} Shots")


# ================================================================ MAIN

def main():
    ap = argparse.ArgumentParser(description="EP03 PEAR V2 Production Pipeline")
    ap.add_argument("command", choices=["voices", "images", "timeline", "audio", 
                                        "render", "captions", "qa", "all"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    
    if args.command in ("voices", "all"):
        print("=== VOICE GENERATION ===")
        generate_voices()
        build_voice_master()
    
    if args.command in ("images", "all"):
        print("=== IMAGE GENERATION ===")
        generate_new_images()
        generate_new_cards()
        build_endcard()
    
    if args.command in ("timeline", "all"):
        print("=== TIMELINE ===")
        build_timeline()
    
    if args.command in ("audio", "all"):
        print("=== AUDIO ===")
        # build_audio() - wird aus pear_produce.py übernommen
    
    if args.command in ("render", "all"):
        print("=== RENDER ===")
        # render() - wird aus pear_produce.py übernommen
    
    if args.command in ("captions", "all"):
        print("=== CAPTIONS ===")
        # captions() - wird aus pear_produce.py übernommen
    
    if args.command in ("qa", "all"):
        print("=== QA ===")
        # qa() - wird aus pear_produce.py übernommen


if __name__ == "__main__":
    main()
