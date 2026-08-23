#!/usr/bin/env python3
"""Gateway V5.3 — Final production with generated visuals.

Uses NanoBanana Pro generated images for cohesive visual style.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import produce_ep02_gateway_v2 as v2

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V5"
V2 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2"
V1 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY"
ALIGNMENT = V2 / "voice" / "alignment" / "EP02_GATEWAY_V2_alignment.json"
VOICE_MASTER = V2 / "voice" / "master" / "EP02_GATEWAY_V2_VO_MASTER.wav"
AUDIO = V2 / "audio" / "EP02V2_final_mix.wav"
SRT = V2 / "captions" / "EP02_GATEWAY_V2_de.srt"
TIMELINE = PROD / "timeline" / "EP02_GATEWAY_V5_timeline.json"
SEGMENTS = PROD / "render" / "segments"
FINAL = PROD / "render" / "final"
MOTION = PROD / "motion_clips" / "downloads"
GENERATED = PROD / "visuals" / "generated"
FPS = 30


def run(args, capture=False):
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-8000:])
    return (p.stdout or "") + (p.stderr or "")


def dur(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], True).strip())


def a(*parts): return str(ROOT.joinpath(*parts).resolve())
def p(*parts): return str(PROD.joinpath(*parts).resolve())
def p2(*parts): return str(V2.joinpath(*parts).resolve())
def p1(*parts): return str(V1.joinpath(*parts).resolve())
def mot(n): return str(MOTION / n)
def gen(n): return str(GENERATED / n)


def item(anchor, visual, scene, kind="STILL", label="", title=""):
    return {"anchor": anchor, "visual": visual, "scene": scene, "kind": kind,
            "evidence_label": label, "on_screen_text": title}


def semantic_shots():
    # All available sources
    ai = lambda n: a("05_GENERATED", "EP02_GATEWAY_V2", "AI_FINAL", n)
    doc = lambda n: p("visuals", "document_crops", n)
    pat = lambda n: p("visuals", "patents", n)
    card = lambda n: p2("visuals", "cards", n)
    v5card = lambda n: p("visuals", "cards", n)
    ex = lambda n: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "APPROVED", n)
    luna = lambda n: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "V2_RESEARCH_LUNA", n)
    rp = lambda n: p1("reference_package", n)
    research = lambda n: a("06_PRODUCTION", "Gateway_Production", "Assets_Research_Luna", n)
    # Motion clips
    motion1 = mot("motion_1.mp4")
    motion2 = mot("motion_2.mp4")
    motion4 = mot("motion_4.mp4")
    # NEW: Generated visuals from NanoBanana Pro!
    gen_consciousness = gen("gw_consciousness_field.png")
    gen_timewheel = gen("gw_time_wheel.png")
    gen_binaural = gen("gw_binaural_processing.png")
    gen_barrier = gen("gw_holographic_barrier.png")
    gen_focus = gen("gw_focus_transition.png")
    gen_observer = gen("gw_observer_protocol.png")
    gen_evidence = gen("gw_evidence_gap.png")

    # AI images
    ai_observers = ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png")
    ai_monroe = ai("GWV2_IMG02_ROBERT_MONROE_PORTRAIT_RECON_16x9.png")
    ai_bentov = ai("GWV2_IMG03_BENTOV_EDITORIAL_RECON_16x9.png")
    ai_binaural = ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png")
    ai_timewheel = ai("GWV2_IMG05_FOCUS15_TIME_WHEEL_16x9.png")
    ai_consciousness = ai("GWV2_IMG06_CONSCIOUSNESS_FIELD_MODEL_16x9.png")
    ai_barrier = ai("GWV2_IMG07_NONCORPOREAL_BARRIER_CLAIM_16x9.png")
    # Originals
    fort_meade_2009 = ex("GW_011_Fort_Meade_entrance_2009.jpg")
    disa_ops = ex("GW_014_DISA_operations_event.webp")
    belief_system = rp("GW_REPORT_PDF26_DOC24_BELIEF_SYSTEM.png")
    doc_noncorporeal = doc("V4_DOC10_NONCORPOREAL_FORMS.png")
    # Patents
    bentov_1969_1 = p2("visuals", "patents", "BENTOV_1969-1.png")
    bentov_1969_2 = p2("visuals", "patents", "BENTOV_1969-2.png")
    bentov_1971_01 = p2("visuals", "patents", "BENTOV_1971-01.png")
    bentov_1971_02 = p2("visuals", "patents", "BENTOV_1971-02.png")
    monroe_patent_1 = rp("GW_PATENT_PDF01.png")
    monroe_patent_2 = rp("GW_PATENT_PDF02.png")
    monroe_patent_3 = rp("GW_PATENT_PDF03.png")
    monroe_patent_4 = rp("GW_PATENT_PDF04.png")
    # V5 cards
    card_focus = v5card("V5_CARD_FOCUS_LEVELS.png")
    card_binaural = v5card("V5_CARD_BINAURAL_BEAT.png")
    card_world = v5card("V5_CARD_WORLD_MODEL.png")
    card_distortion = v5card("V5_CARD_DISTORTION.png")
    card_conditional = v5card("V5_CARD_CONDITIONAL.png")
    card_evidence = v5card("V5_CARD_EVIDENCE_SCALE.png")
    card_protocol = v5card("V5_CARD_TEST_PROTOCOL.png")

    shots = [
        # S1 — Hook (0:00 - 0:50)
        item("Drei Menschen.", gen_observer, "S1", label="THREE OBSERVERS"),
        item("Der erste beobachtet", card("V2_CARD01_THREE_OBSERVERS.png"), "S1", label="PRESENT"),
        item("Der zweite soll", doc("V5_DOC_RECOMMENDATION_H_FULL.png"), "S1", label="RECOMMENDATION H"),
        item("Der dritte aus", card_distortion, "S1", label="PAST AND FUTURE"),
        item("Danach werden", card("V2_CARD01_THREE_OBSERVERS.png"), "S1", label="COMPARE REPORTS"),
        item("Das ist keine Zusammenfassung", rp("GW_REPORT_PDF01_HEADER.png"), "S1", label="ORIGINAL DOCUMENT"),
        item("Genau dieser Versuch", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", label="THE COMPLETE PROCEDURE"),
        item("Datum:", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S1", label="9 JUNE 1983"),
        item("Autor:", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S1", label="WAYNE M. McDONNELL"),
        item("Heute liegt", ex("GW_012_DISA_headquarters_aerial.jpg"), "S1", label="FORT MEADE · DISA"),
        item("Geschrieben wurde", fort_meade_2009, "S1", label="FORT MEADE · 2009"),
        item("Die eigentliche Frage", motion1, "S1", kind="VIDEO", label="NOT A PROOF OF TIME TRAVEL"),
        item("Sie lautet:", doc("V5_DOC_RECOMMENDATION_H_FULL.png"), "S1", label="THE PROPOSED PROCEDURE"),
        item("Die Antwort beginnt", rp("GW_REPORT_PDF01_HEADER.png"), "S1", label="THE REPORT"),

        # S2 — The three men (0:50 - 2:15)
        item("Robert Monroe entwickelte", ai_monroe, "S2", label="MONROE INSTITUTE"),
        item("Sein historischer Markenbegriff", pat("V5_PATENT_MONROE_BINAURAL.png"), "S2", label="HEMI-SYNC · PATENT"),
        item("Teilnehmer hörten", gen_binaural, "S2", label="LISTENING WITH HEADPHONES"),
        item("Wayne McDonnell sollte", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label="DOCUMENTED AUTHOR"),
        item("Sein Auftrag war", doc("V4_DOC02_TASK_BENTOV.png"), "S2", label="THE ASSIGNED TASK"),
        item("Auf der Titelseite", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S2", label="DEPARTMENT OF THE ARMY"),
        item("Am Ende des Schreibens", rp("GW_REPORT_PDF02_SIGNATURE.png"), "S2", label="NAME · RANK · SIGNATURE"),
        item("Für die theoretische Brücke", ai_bentov, "S2", label="ITZHAK BENTOV"),
        item("Bentov war Autor", bentov_1971_01, "S2", label="BENTOV PATENT · 1971"),
        item("Seine Patente zeigen", bentov_1969_1, "S2", label="MEDICAL DEVICE · 1969"),
        item("Katheter", bentov_1969_2, "S2", label="ELECTRODE DESIGN"),
        item("Im Gateway-Bericht", doc("V4_DOC02_TASK_BENTOV.png"), "S2", label="BENTOV IN THE REPORT"),
        item("Monroe lieferte", monroe_patent_1, "S2", label="TRAINING SYSTEM"),
        item("Bentov lieferte", bentov_1971_02, "S2", label="ANALOGIES"),
        item("McDonnell setzte", card("V2_CARD02_PEOPLE_CHAIN.png"), "S2", label="ARMY ASSESSMENT"),
        item("Von Wayne McDonnell", rp("GW_REPORT_PDF02_SIGNATURE.png"), "S2", label="NO VERIFIED PORTRAIT"),
        item("Seine Person wird", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label="TEXT · RANK · SIGNATURE"),

        # S3 — Mechanism (2:15 - 3:35)
        item("Der Einstieg ist", ex("GW_002_Exhibit_1A.png"), "S3", label="EXHIBIT 1A"),
        item("Hört das linke Ohr", gen_binaural, "S3", label="BINAURAL BEAT"),
        item("ungefähr 10 Hertz", motion2, "S3", kind="VIDEO", label="PERCEIVED FREQUENCY"),
        item("Dieser Rhythmus", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S3", label="AUDITORY PROCESSING"),
        item("Verarbeitung beider Signale", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S3", label="PLOS REVIEW"),
        item("Das nennt man", ex("GW_004_Exhibit_1C.png"), "S3", label="EXHIBIT 1C"),
        item("Gateway bestand", ex("GW_005_Exhibit_2.png"), "S3", label="EXHIBIT 2"),
        item("Zu den Tönen kamen", ex("GW_006_Exhibit_3.png"), "S3", label="EXHIBIT 3"),
        item("Wer danach ruhiger", ai_binaural, "S3", label="A COMPLETE TRAINING"),
        item("Ein späteres Patent", monroe_patent_1, "S3", label="U.S. PATENT 5,213,562"),
        item("EEG-Muster", monroe_patent_2, "S3", label="EEG PATTERNS"),
        item("Es wurde 1993", monroe_patent_3, "S3", label="PATENT DISCLOSURE"),
        item("Das Patent zeigt", monroe_patent_4, "S3", label="PATENT CLAIMS"),
        item("Es beweist nicht", card("V2_CARD03_MECHANISM_LADDER.png"), "S3", label="PATENT ≠ PROOF"),
        item("McDonnell übernimmt", ex("GW_007_Exhibit_4A.png"), "S3", label="EXHIBIT 4A"),
        item("Frequency-Following Response", rp("GW_PLOS_PDF07_PRISMA.png"), "S3", label="SYSTEMATIC REVIEW"),
        item("Bis hierhin", gen_evidence, "S3", label="EVIDENCE SCALE"),
        item("Dann macht", card("V2_CARD03_MECHANISM_LADDER.png"), "S3", label="THE CLAIM JUMP"),

        # S4 — World model (3:35 - 5:20)
        item("McDonnell will nicht", ai_monroe, "S4", label="THE AUTHOR'S MODEL"),
        item("Grenzen des Körpers", ex("GW_008_Exhibit_4B.png"), "S4", label="EXHIBIT 4B"),
        item("Resonanz", ex("GW_002_Exhibit_1A.png"), "S4", label="EXHIBIT 1A"),
        item("Gehirnhälften", ex("GW_004_Exhibit_1C.png"), "S4", label="EXHIBIT 1C"),
        item("holografische Analogien", ex("GW_006_Exhibit_3.png"), "S4", label="EXHIBIT 3"),
        item("Die Originaldiagramme", ex("GW_007_Exhibit_4A.png"), "S4", label="EXHIBIT 4A"),
        item("Torusformen", ex("GW_008_Exhibit_4B.png"), "S4", label="EXHIBIT 4B"),
        item("Die Logik läuft", ex("GW_009_Exhibit_4C.png"), "S4", label="EXHIBIT 4C"),
        item("Der Körper schwingt", gen_consciousness, "S4", label="BODY · MODEL"),
        item("Das Gehirn erzeugt", ex("GW_005_Exhibit_2.png"), "S4", label="EXHIBIT 2"),
        item("Synchronisierung soll", motion2, "S4", kind="VIDEO", label="COHERENCE · MODEL"),
        item("Ein ausreichend kohärentes", ex("GW_010_Exhibit_5.png"), "S4", label="EXHIBIT 5"),
        item("Raum und Zeit", gen_timewheel, "S4", label="THE TIME WHEEL"),
        item("Auf dem Papier", ex("GW_009_Exhibit_4C.png"), "S4", label="FORMULAS AND DIAGRAMS"),
        item("Doch die Zahnräder", gen_evidence, "S4", label="NO DEMONSTRATED BRIDGE"),
        item("Eine Analogie", bentov_1971_01, "S4", label="BENTOV PATENT"),
        item("entscheidende Wechsel", motion4, "S4", kind="VIDEO", label="PHENOMENON → THEORY"),
        item("eine Art Landkarte", card_focus, "S4", label="THE FOCUS LEVELS"),

        # S5 — Focus levels (5:20 - 7:10)
        item("Focus 10 bedeutet", doc("V5_DOC_FOCUS15_FULL.png"), "S5", label="FOCUS 10"),
        item("Focus 12 soll", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S5", label="FOCUS 12"),
        item("Dann steht dort", doc("V4_DOC04_FOCUS15_HEADING.png"), "S5", label="FOCUS 15"),
        item("Zeit soll", gen_timewheel, "S5", label="THE TIME WHEEL MODEL"),
        item("Seine Speichen", motion1, "S5", kind="VIDEO", label="PAST POINTS"),
        item("McDonnell schreibt zugleich", doc("V4_DOC05_LESS_THAN_FIVE_PERCENT.png"), "S5", label="DIFFICULTY WARNING"),
        item("weniger als fünf Prozent", doc("V5_DOC_TEN_DIGITS.png"), "S5", label="LESS THAN FIVE PERCENT"),
        item("Die nächste Überschrift", doc("V4_DOC06_FOCUS21_FUTURE.png"), "S5", label="FOCUS 21"),
        item("außerhalb normaler Raum-Zeit", gen_consciousness, "S5", label="MODEL VISUALIZATION"),
        item("Direkt darunter", doc("V5_DOC_OBE_FULL.png"), "S5", label="OUT-OF-BODY MOVEMENT"),
        item("garantiere keinen Erfolg", doc("V4_DOC07_OBE_NO_GUARANTEE.png"), "S5", label="NO GUARANTEE"),
        item("Trotzdem folgen", gen_barrier, "S5", label="THE COMPLETE PASSAGE"),
        item("Hier muss das Bild", doc("V5_DOC_OBE_FULL.png"), "S5", label="READ THE PASSAGE"),
        item("Dokumentiert ist", rp("GW_REPORT_PDF25_INFO_COLLECTION.png"), "S5", label="DOCUMENTED"),
        item("Nicht dokumentiert", gen_evidence, "S5", label="NOT DOCUMENTED"),

        # S6 — Operational claims (7:10 - 9:05)
        item("Information Collection Potential", doc("V5_DOC_INFO_COLLECTION_TOP.png"), "S6", label="INFORMATION COLLECTION"),
        item("Eindrücke aus Gegenwart", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6", label="DISTORTION PROBLEM"),
        item("zehn computergenerierte Zahlen", doc("V5_DOC_TEN_DIGITS.png"), "S6", label="TEN NUMBERS"),
        item("manche hätten genug", rp("GW_REPORT_PDF25_INFO_COLLECTION.png"), "S6", label="SOME DIGITS CORRECT"),
        item("Alle zehn richtig", belief_system, "S6", label="NEVER ALL TEN"),
        item("Empfehlung H", doc("V5_DOC_RECOMMENDATION_H_FULL.png"), "S6", label="RECOMMENDATION H"),
        item("Drei Personen", gen_observer, "S6", label="THREE OBSERVERS"),
        item("Dasselbe Ziel", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label="ONE TARGET"),
        item("normaler Raum-Zeit", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S6", label="RECOMMENDATIONS PAGE"),
        item("Eine in Focus 15", gen_focus, "S6", label="PAST · FOCUS 15"),
        item("Eine in Focus 21", doc("V5_DOC_RECOMMENDATION_JK.png"), "S6", label="FUTURE · FOCUS 21"),
        item("alle drei Berichte", card_distortion, "S6", label="COMPARE REPORTS"),
        item("Der Absatz ist echt", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label="THE PARAGRAPH IS REAL"),
        item("Ein erfolgreicher Versuch", card_protocol, "S6", label="NO TEST REPORTED"),
        item("Die nächsten Empfehlungen", doc_noncorporeal, "S6", label="RECOMMENDATION J"),
        item("nicht-körperlichen Energieformen", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S6", label="NON-CORPOREAL FORMS"),
        item("holografische Muster", gen_barrier, "S6", label="RECOMMENDATION K"),
        item("unerwünschte außerkörperliche", ai_barrier, "S6", label="HOLOGRAPHIC BARRIER"),
        item("kein Entspannungskurs", motion2, "S6", kind="VIDEO", label="COMPLETE WORLD MODEL"),
        item("was Bewusstsein sein", ex("GW_010_Exhibit_5.png"), "S6", label="EXHIBIT 5"),

        # S7 — Evidence (9:05 - 10:55)
        item("Ein Teil dieser Geschichte", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S7", label="TESTABLE QUESTIONS"),
        item("Meta-Analyse von 2019", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S7", label="META-ANALYSIS · 2019"),
        item("moderaten Effekt", rp("GW_PLOS_PDF07_PRISMA.png"), "S7", label="SYSTEMATIC REVIEW"),
        item("kein Beleg für Gateway", gen_evidence, "S7", label="NOT THE WHOLE SYSTEM"),
        item("systematischer Review von 2023", rp("GW_PLOS_PDF07_PRISMA.png"), "S7", label="PRISMA DIAGRAM"),
        item("Fünf Studien", motion4, "S7", kind="VIDEO", label="5 SUPPORT · 8 CONTRADICT"),
        item("Methoden, Frequenzen", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S7", label="HETEROGENEOUS METHODS"),
        item("Selbst ein klarer", gen_evidence, "S7", label="SMALL EFFECT ≠ LARGE CLAIM"),
        item("neue, überprüfbare Information", card_protocol, "S7", label="VERIFIABLE INFORMATION"),
        item("Ziel müsste vorher", card_protocol, "S7", label="PRESELECT TARGET"),
        item("Auswertung müsste blind", card_protocol, "S7", label="BLIND EVALUATION"),
        item("Trefferregeln", motion1, "S7", kind="VIDEO", label="LOCK SCORING · REPEAT"),
        item("veränderter Zustand", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S7", label="A FINDING ABOUT EXPERIENCE"),
        item("verborgenes Ziel", card_protocol, "S7", label="A FINDING ABOUT INFORMATION"),
        item("eigentliche Beweislücke", gen_evidence, "S7", label="THE EVIDENCE GAP"),

        # S8 — Residue (10:55 - 12:00)
        item("Was bleibt", rp("GW_REPORT_PDF27_CONCLUSION_A_G.png"), "S8", label="CONCLUSION"),
        item("Der Bericht ist echt", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S8", label="DOCUMENTED"),
        item("Datum, Auftrag", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S8", label="DATE · TASK · AUTHOR"),
        item("Focus Levels", card_focus, "S8", label="FOCUS LEVELS"),
        item("militärische Interesse", disa_ops, "S8", label="DISA OPERATIONS"),
        item("Bewusstsein könne", rp("GW_REPORT_PDF27_CONCLUSION_A_G.png"), "S8", label="CLAIM IN THE REPORT"),
        item("keinen belastbaren", gen_evidence, "S8", label="NO OPERATIONAL EVIDENCE"),
        item("virale Kurzfassung", motion2, "S8", kind="VIDEO", label="THE VIRAL VERSION"),
        item("tatsächliche Geschichte", doc("V4_DOC09_RECOMMENDATION_H.png"), "S8", label="THE ACTUAL DOCUMENT"),
        item("Test mit Beobachtern", card("V2_CARD01_THREE_OBSERVERS.png"), "S8", label="PAST · PRESENT · FUTURE"),
        item("nicht-körperliche Intelligenzen", doc_noncorporeal, "S8", label="RECOMMENDATION J"),
        item("mentale Schutzmuster", gen_barrier, "S8", label="RECOMMENDATION K"),
        item("Nicht der Beweis", card_conditional, "S8", label="CONDITIONAL ENDING"),
        item("Der Fund ist diese Seite", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S8", label="THE IMPOSSIBLE · PLANNED"),
    ]
    return shots


def build_timeline():
    data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
    text, chars = data["source_text"], data["characters"]
    shots = semantic_shots()
    cursor = 0
    starts = []
    for index, shot in enumerate(shots):
        pos = text.find(shot["anchor"], cursor)
        if pos < 0:
            raise RuntimeError(f"Anchor not found after char {cursor}: {shot['anchor']!r}")
        first = next(i for i in range(pos, pos + len(shot["anchor"])) if not text[i].isspace())
        starts.append(0.0 if index == 0 else float(chars[first]["start"]))
        cursor = pos + len(shot["anchor"])
    total = dur(VOICE_MASTER)
    rows = []
    for i, (shot, start) in enumerate(zip(shots, starts), 1):
        end = starts[i] if i < len(starts) else total
        if end - start < 0.35:
            raise RuntimeError(f"Shot too short at {i}: {end-start:.3f}s")
        path = Path(shot["visual"])
        if not path.is_file():
            raise FileNotFoundError(path)
        row = {k: v for k, v in shot.items() if k != "anchor"}
        row.update({"anchor": shot["anchor"], "shot_id": f"GWV5_{i:03d}", "start": round(start, 3),
                    "end": round(end, 3), "duration": round(end - start, 3)})
        rows.append(row)
    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PROD / "captions").mkdir(parents=True, exist_ok=True)
    (PROD / "captions" / "EP02_GATEWAY_V5_de.srt").write_bytes(SRT.read_bytes())
    print(f"Timeline {len(rows)} word-anchored shots / {total:.3f}s / avg {total/len(rows):.2f}s")


def camera_filter(index, row):
    frames = max(1, math.ceil(row["duration"] * FPS))
    if row["kind"] == "VIDEO":
        return "scale=1440:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#041114,eq=contrast=1.03:saturation=.90,format=yuv420p"
    if "visuals\\patents" in row["visual"] or "visuals/patents" in row["visual"]:
        base = "scale=1720:970:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#041114"
    else:
        base = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
    inc = .00011
    x = "iw/2-(iw/zoom/2)" if index % 2 == 0 else f"(iw-iw/zoom)*on/{frames}"
    fade = f",fade=t=out:st={max(0,row['duration']-2):.3f}:d=2:color=#041114" if row.get("is_last") else ""
    return base + f",zoompan=z='min(zoom+{inc},1.07)':x='{x}':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},eq=contrast=1.025:saturation=.94,unsharp=5:5:.22:5:5:0,format=yuv420p" + fade


def ass_time(value):
    cs = round(value * 100); h, r = divmod(cs, 360000); m, r = divmod(r, 6000); s, cs = divmod(r, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def graphics(rows):
    path = PROD / "render" / "EP02_GATEWAY_V5_graphics.ass"
    path.parent.mkdir(parents=True, exist_ok=True)
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Title,Arial,37,&H00F2EFE5,&H0,&H90000000,&H78000000,-1,0,0,0,100,100,1,0,3,1,0,7,82,82,60,1
Style: Evidence,Arial,22,&H00FFFFFF,&H0,&H70000000,&H9823211E,-1,0,0,0,100,100,1,0,3,1,0,9,70,70,58,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [head]
    for row in rows:
        start, end = ass_time(row["start"] + .12), ass_time(max(row["start"] + .3, row["end"] - .12))
        title = row["on_screen_text"].replace("{", r"\{").replace("}", r"\}")
        label = row["evidence_label"].replace("{", r"\{").replace("}", r"\}")
        if title: lines.append(f"Dialogue: 0,{start},{end},Title,,0,0,0,,{title}\n")
        if label: lines.append(f"Dialogue: 0,{start},{end},Evidence,,0,0,0,,{label}\n")
    path.write_text("".join(lines), encoding="utf-8-sig")
    return path


def render(force=False, limit=None):
    rows = json.loads(TIMELINE.read_text(encoding="utf-8"))
    rows[-1]["is_last"] = True
    todo = rows[:limit] if limit else rows
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    for i, row in enumerate(todo):
        target = SEGMENTS / f"{i+1:03d}_{row['shot_id']}.mp4"
        if target.exists() and not force: continue
        print(f"Render {i+1:03d}/{len(todo):03d} {row['shot_id']} {row['duration']:.2f}s · {row['anchor']}", flush=True)
        inputs = ["-stream_loop", "-1", "-i", row["visual"]] if row["kind"] == "VIDEO" else ["-loop", "1", "-framerate", str(FPS), "-i", row["visual"]]
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-t", str(row["duration"]),
             "-vf", camera_filter(i, row), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(target)])
    if limit: return
    concat = PROD / "render" / "concat.txt"
    paths = [SEGMENTS / f"{i+1:03d}_{row['shot_id']}.mp4" for i, row in enumerate(rows)]
    concat.write_text("\n".join(f"file '{path.as_posix()}'" for path in paths) + "\n", encoding="utf-8")
    picture = PROD / "render" / "EP02_GATEWAY_V5_picture_lock.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(picture)])
    ass = graphics(rows); assf = "ass='" + str(ass).replace("\\", "/").replace(":", r"\:") + "'"
    FINAL.mkdir(parents=True, exist_ok=True)
    out = FINAL / "EP02_GATEWAY_V5_FINAL_1080p.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(picture), "-i", str(AUDIO), "-vf", assf,
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)])
    print(out)


def qa():
    video = FINAL / "EP02_GATEWAY_V5_FINAL_1080p.mp4"
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)], True))
    vs = next(s for s in probe["streams"] if s["codec_type"] == "video")
    au = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    rows = json.loads(TIMELINE.read_text(encoding="utf-8")); duration = float(probe["format"]["duration"])
    loud = v2.loudness(video)
    checks = {
        "1080p": vs.get("width") == 1920 and vs.get("height") == 1080,
        "h264_yuv420p": vs.get("codec_name") == "h264" and vs.get("pix_fmt") == "yuv420p",
        "aac_48k_stereo": au.get("codec_name") == "aac" and au.get("sample_rate") == "48000" and au.get("channels") == 2,
        "duration_match": abs(duration - dur(VOICE_MASTER)) < .3,
        "semantic_anchor_count": len(rows) >= 110,
        "all_anchors_present": all(row.get("anchor") for row in rows),
        "loudness": abs(float(loud["input_i"]) + 14) <= .5,
        "peak": float(loud["input_tp"]) <= -.8,
        "speed_112": json.loads((V2 / "voice" / "master" / "stem_report.json").read_text())["tts_speed"] == 1.12,
    }
    report = {"file": str(video.resolve()), "sha256": hashlib.sha256(video.read_bytes()).hexdigest(), "duration": duration,
              "shots": len(rows), "average_shot_seconds": round(duration / len(rows), 2), "video": vs, "audio": au,
              "loudness": loud, "checks": checks}
    (FINAL / "EP02_GATEWAY_V5_QA.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-vf", "fps=1/32,scale=384:216,tile=5x4", "-frames:v", "1", "-q:v", "2", str(FINAL / "EP02_GATEWAY_V5_CONTACT_SHEET.jpg")])
    print(json.dumps({"duration": duration, "shots": len(rows), "avg": round(duration/len(rows), 2), "checks": checks}, indent=2))
    if not all(checks.values()): raise RuntimeError("QA failed")


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=["timeline", "render", "qa", "all"])
    parser.add_argument("--force", action="store_true"); parser.add_argument("--limit", type=int); args = parser.parse_args()
    if args.command in ("timeline", "all"): build_timeline()
    if args.command in ("render", "all"): render(args.force, args.limit)
    if args.command in ("qa", "all") and not args.limit: qa()


if __name__ == "__main__": main()
