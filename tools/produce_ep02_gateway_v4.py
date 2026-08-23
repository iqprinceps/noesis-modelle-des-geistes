#!/usr/bin/env python3
"""Gateway V4 — Final production with clean highlight document crops.

This script produces the complete V4 video using:
- Clean, continuous highlight document crops (V4)
- Same word-anchored timeline as V3
- Same audio and voice master from V2
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
PROD = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V4"
V3 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V3_SYNC"
V2 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V2"
V1 = ROOT / "06_PRODUCTION" / "EP02_GATEWAY"
ALIGNMENT = V2 / "voice" / "alignment" / "EP02_GATEWAY_V2_alignment.json"
VOICE_MASTER = V2 / "voice" / "master" / "EP02_GATEWAY_V2_VO_MASTER.wav"
AUDIO = V2 / "audio" / "EP02V2_final_mix.wav"
SRT = V2 / "captions" / "EP02_GATEWAY_V2_de.srt"
TIMELINE = PROD / "timeline" / "EP02_GATEWAY_V4_timeline.json"
SEGMENTS = PROD / "render" / "segments"
FINAL = PROD / "render" / "final"
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


def item(anchor, visual, scene, kind="STILL", label="", title=""):
    return {"anchor": anchor, "visual": visual, "scene": scene, "kind": kind,
            "evidence_label": label, "on_screen_text": title}


def semantic_shots():
    ai = lambda n: a("05_GENERATED", "EP02_GATEWAY_V2", "AI_FINAL", n)
    doc = lambda n: p("visuals", "document_crops", n)  # V4 document crops!
    card = lambda n: p2("visuals", "cards", n)
    patent = lambda n: p2("visuals", "patents", n)
    ex = lambda n: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "APPROVED", n)
    luna = lambda n: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "V2_RESEARCH_LUNA", n)
    rp = lambda n: p1("reference_package", n)
    oldai = lambda *parts: a("05_GENERATED", "EP02_GATEWAY", *parts)
    research = lambda n: a("06_PRODUCTION", "Gateway_Production", "Assets_Research_Luna", n)

    shots = [
        # S1 — the exact hook beats.
        item("Drei Menschen.", ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"), "S1", label="RECONSTRUCTION"),
        item("Der erste beobachtet", card("V2_CARD01_THREE_OBSERVERS.png"), "S1", label="PRESENT"),
        item("Der zweite soll", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", label="PAST · IN THE REPORT"),
        item("Der dritte aus", card("V2_CARD01_THREE_OBSERVERS.png"), "S1", label="FUTURE"),
        item("Danach werden", card("V2_CARD01_THREE_OBSERVERS.png"), "S1", label="COMPARE REPORTS"),
        item("Das ist keine Zusammenfassung", ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"), "S1", label="RECONSTRUCTION"),
        item("Genau dieser Versuch", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", label="ORIGINAL PASSAGE"),
        item("Datum:", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S1", label="9 JUNE 1983"),
        item("Autor:", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S1", label="WAYNE M. McDONNELL"),
        item("Heute liegt", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S1", label="CIA ARCHIVE COPY · ARMY REPORT"),
        item("Geschrieben wurde", luna("GWV2_IMG_001_Fort_Meade_entrance_2009_PD.jpg"), "S1", label="FORT MEADE · 2009"),
        item("Die eigentliche Frage", card("V2_CARD01_THREE_OBSERVERS.png"), "S1", label="NOT A PROOF OF TIME TRAVEL"),
        item("Sie lautet:", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", label="PROPOSED PROCEDURE"),
        item("Die Antwort beginnt", ai("GWV2_IMG02_ROBERT_MONROE_PORTRAIT_RECON_16x9.png"), "S1", label="PORTRAIT RECONSTRUCTION", title="ROBERT MONROE"),

        # S2 — each person appears only when named.
        item("Robert Monroe entwickelte", ai("GWV2_IMG02_ROBERT_MONROE_PORTRAIT_RECON_16x9.png"), "S2", label="PORTRAIT RECONSTRUCTION", title="ROBERT MONROE"),
        item("Sein historischer Markenbegriff", ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"), "S2", label="HEMI-SYNC · HISTORICAL TERM"),
        item("Teilnehmer hörten", luna("GWV2_VID_001_Computer_Meditation_CC_BY_SA_3.0.ogv"), "S2", kind="VIDEO", label="CONTEXT · NOT GATEWAY FOOTAGE"),
        item("Wayne McDonnell sollte", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label="DOCUMENTED AUTHOR", title="WAYNE M. McDONNELL"),
        item("Sein Auftrag war", doc("V4_DOC02_TASK_BENTOV.png"), "S2", label="THE ASSIGNED TASK"),
        item("Auf der Titelseite", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S2", label="DEPARTMENT OF THE ARMY"),
        item("Am Ende des Schreibens", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label="NAME · RANK · SIGNATURE"),
        item("Für die theoretische Brücke", ai("GWV2_IMG03_BENTOV_EDITORIAL_RECON_16x9.png"), "S2", label="DRAMATIZED RECONSTRUCTION", title="ITZHAK BENTOV · NOT A PHOTOGRAPH"),
        item("Bentov war Autor", ai("GWV2_IMG03_BENTOV_EDITORIAL_RECON_16x9.png"), "S2", label="DRAMATIZED RECONSTRUCTION"),
        item("Seine Patente zeigen", patent("BENTOV_1971-01.png"), "S2", label="U.S. PATENT · 1971"),
        item("Katheter", patent("BENTOV_1969-1.png"), "S2", label="U.S. PATENT · 1969"),
        item("Im Gateway-Bericht", doc("V4_DOC02_TASK_BENTOV.png"), "S2", label="BENTOV IN THE REPORT"),
        item("Monroe lieferte", ai("GWV2_IMG02_ROBERT_MONROE_PORTRAIT_RECON_16x9.png"), "S2", label="TRAINING SYSTEM"),
        item("Bentov lieferte", patent("BENTOV_1971-02.png"), "S2", label="ANALOGIES"),
        item("McDonnell setzte", card("V2_CARD02_PEOPLE_CHAIN.png"), "S2", label="ARMY ASSESSMENT"),
        item("Von Wayne McDonnell", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label="NO VERIFIED PORTRAIT"),
        item("Seine Person wird", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label="NO INVENTED FACE"),
        item("Wir bleiben bei", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label="TEXT · RANK · SIGNATURE"),

        # S3 — mechanism and patent follow the spoken explanation.
        item("Der Einstieg ist", ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"), "S3", label="RECONSTRUCTION"),
        item("Hört das linke Ohr", p1("qa_renders", "CARD02_BINAURAL_BEAT.png"), "S3", label="400 Hz · 410 Hz"),
        item("ungefähr 10 Hertz", p1("qa_renders", "CARD02_BINAURAL_BEAT.png"), "S3", label="PERCEIVED 10 Hz BEAT"),
        item("Dieser Rhythmus", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S3", label="AUDITORY PROCESSING"),
        item("Verarbeitung beider Signale", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S3", label="BINAURAL PROCESSING"),
        item("Das nennt man", p1("qa_renders", "CARD02_BINAURAL_BEAT.png"), "S3", label="BINAURAL BEAT"),
        item("Gateway bestand", ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"), "S3", label="MORE THAN TWO TONES"),
        item("Zu den Tönen kamen", luna("GWV2_VID_001_Computer_Meditation_CC_BY_SA_3.0.ogv"), "S3", kind="VIDEO", label="CONTEXT · NOT GATEWAY FOOTAGE"),
        item("Wer danach ruhiger", ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"), "S3", label="A COMPLETE TRAINING PACKAGE"),
        item("Ein späteres Patent", rp("GW_PATENT_PDF01.png"), "S3", label="U.S. PATENT 5,213,562"),
        item("EEG-Muster", rp("GW_PATENT_PDF02.png"), "S3", label="PATENT DRAWING"),
        item("Es wurde 1993", rp("GW_PATENT_PDF01.png"), "S3", label="1993 · TEN YEARS LATER"),
        item("Das Patent zeigt", rp("GW_PATENT_PDF03.png"), "S3", label="PATENT DISCLOSURE"),
        item("Es beweist nicht", card("V2_CARD03_MECHANISM_LADDER.png"), "S3", label="PATENT ≠ PROOF"),
        item("McDonnell übernimmt", ex("GW_002_Exhibit_1A.png"), "S3", label="MODEL IN THE REPORT"),
        item("Frequency-Following Response", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S3", label="RESEARCH FIGURE"),
        item("Bis hierhin", card("V2_CARD05_EVIDENCE_SCALE.png"), "S3", label="PERCEPTION · ATTENTION · BRAIN ACTIVITY"),
        item("Dann macht", card("V2_CARD03_MECHANISM_LADDER.png"), "S3", label="THE CLAIM JUMP"),

        # S4 — the report's diagram chain.
        item("McDonnell will nicht", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S4", label="THE AUTHOR'S MODEL"),
        item("Grenzen des Körpers", ai("GWV2_IMG06_CONSCIOUSNESS_FIELD_MODEL_16x9.png"), "S4", label="MODEL VISUALIZATION"),
        item("Resonanz", ex("GW_002_Exhibit_1A.png"), "S4", label="ORIGINAL DIAGRAM"),
        item("Gehirnhälften", ex("GW_004_Exhibit_1C.png"), "S4", label="ORIGINAL DIAGRAM"),
        item("holografische Analogien", ex("GW_006_Exhibit_3.png"), "S4", label="ORIGINAL DIAGRAM"),
        item("Die Originaldiagramme", ex("GW_007_Exhibit_4A.png"), "S4", label="ORIGINAL DIAGRAM"),
        item("Torusformen", ex("GW_008_Exhibit_4B.png"), "S4", label="ORIGINAL DIAGRAM"),
        item("Die Logik läuft", card("V2_CARD03_MECHANISM_LADDER.png"), "S4", label="THE REPORT'S LOGIC"),
        item("Der Körper schwingt", ex("GW_005_Exhibit_2.png"), "S4", label="BODY · MODEL"),
        item("Das Gehirn erzeugt", ex("GW_004_Exhibit_1C.png"), "S4", label="BRAIN · MODEL"),
        item("Synchronisierung soll", card("V2_CARD03_MECHANISM_LADDER.png"), "S4", label="COHERENCE · MODEL"),
        item("Ein ausreichend kohärentes", ai("GWV2_IMG06_CONSCIOUSNESS_FIELD_MODEL_16x9.png"), "S4", label="INFORMATION FIELD · SPECULATION"),
        item("Raum und Zeit", ex("GW_010_Exhibit_5.png"), "S4", label="ORIGINAL DIAGRAM"),
        item("Auf dem Papier", ex("GW_009_Exhibit_4C.png"), "S4", label="FORMULAS AND DIAGRAMS"),
        item("Doch die Zahnräder", card("V2_CARD03_MECHANISM_LADDER.png"), "S4", label="NO DEMONSTRATED BRIDGE"),
        item("Eine Analogie", ai("GWV2_IMG03_BENTOV_EDITORIAL_RECON_16x9.png"), "S4", label="DRAMATIZED RECONSTRUCTION"),
        item("entscheidende Wechsel", card("V2_CARD05_EVIDENCE_SCALE.png"), "S4", label="PHENOMENON → SPECULATIVE THEORY"),
        item("eine Art Landkarte", p1("qa_renders", "CARD03_FOCUS_LEVELS.png"), "S4", label="THE FOCUS LEVELS"),

        # S5 — headings and warnings appear at the exact spoken phrases.
        item("Focus 10 bedeutet", p1("qa_renders", "CARD03_FOCUS_LEVELS.png"), "S5", label="FOCUS 10"),
        item("Focus 12 soll", p1("qa_renders", "CARD03_FOCUS_LEVELS.png"), "S5", label="FOCUS 12"),
        item("Dann steht dort", doc("V4_DOC04_FOCUS15_HEADING.png"), "S5", label="FOCUS 15 · IN THE REPORT"),
        item("Zeit soll", ai("GWV2_IMG05_FOCUS15_TIME_WHEEL_16x9.png"), "S5", label="MODEL VISUALIZATION"),
        item("Seine Speichen", ai("GWV2_IMG05_FOCUS15_TIME_WHEEL_16x9.png"), "S5", label="PAST · MODEL VISUALIZATION"),
        item("McDonnell schreibt zugleich", doc("V4_DOC05_LESS_THAN_FIVE_PERCENT.png"), "S5", label="DIFFICULTY WARNING"),
        item("weniger als fünf Prozent", doc("V4_DOC05_LESS_THAN_FIVE_PERCENT.png"), "S5", label="LESS THAN FIVE PERCENT"),
        item("Die nächste Überschrift", doc("V4_DOC06_FOCUS21_FUTURE.png"), "S5", label="FOCUS 21 · IN THE REPORT"),
        item("außerhalb normaler Raum-Zeit", oldai("STYLE_REFERENCES", "IMG02_GW_STYLE_CONCEPTUAL_16x9.png"), "S5", label="MODEL VISUALIZATION"),
        item("Direkt darunter", doc("V4_DOC07_OBE_NO_GUARANTEE.png"), "S5", label="THE OUT-OF-BODY MOVEMENT"),
        item("garantiere keinen Erfolg", doc("V4_DOC07_OBE_NO_GUARANTEE.png"), "S5", label="NO GUARANTEE"),
        item("Trotzdem folgen", oldai("AI_RECONSTRUCTIONS", "IMG06_GW_OUT_OF_BODY_CONCEPT_16x9.png"), "S5", label="RECONSTRUCTION"),
        item("Hier muss das Bild", doc("V4_DOC07_OBE_NO_GUARANTEE.png"), "S5", label="READ THE COMPLETE PASSAGE"),
        item("Dokumentiert ist", p1("qa_renders", "CARD03_FOCUS_LEVELS.png"), "S5", label="DOCUMENTED: LEVELS AND TECHNIQUES"),
        item("Nicht dokumentiert", card("V2_CARD05_EVIDENCE_SCALE.png"), "S5", label="NOT DOCUMENTED: VERIFIED TIME INFORMATION"),

        # S6 — operational claims.
        item("Information Collection Potential", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6", label="INFORMATION COLLECTION"),
        item("Eindrücke aus Gegenwart", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6", label="THE REPORT'S DISTORTION PROBLEM"),
        item("zehn computergenerierte Zahlen", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6", label="TEN COMPUTER-GENERATED NUMBERS"),
        item("manche hätten genug", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6", label="SOME DIGITS"),
        item("Alle zehn richtig", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6", label="NEVER ALL TEN"),
        item("Empfehlung H", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label="RECOMMENDATION H"),
        item("Drei Personen", ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"), "S6", label="RECONSTRUCTION"),
        item("Dasselbe Ziel", card("V2_CARD01_THREE_OBSERVERS.png"), "S6", label="ONE TARGET"),
        item("normaler Raum-Zeit", card("V2_CARD01_THREE_OBSERVERS.png"), "S6", label="PRESENT"),
        item("Eine in Focus 15", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label="PAST · FOCUS 15"),
        item("Eine in Focus 21", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label="FUTURE · FOCUS 21"),
        item("alle drei Berichte", card("V2_CARD01_THREE_OBSERVERS.png"), "S6", label="COMPARE REPORTS"),
        item("Der Absatz ist echt", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label="THE PARAGRAPH IS REAL"),
        item("Ein erfolgreicher Versuch", card("V2_CARD04_TEST_PROTOCOL.png"), "S6", label="NO SUCCESSFUL TEST REPORTED"),
        item("Die nächsten Empfehlungen", doc("V4_DOC10_NONCORPOREAL_FORMS.png"), "S6", label="THE NEXT RECOMMENDATIONS"),
        item("nicht-körperlichen Energieformen", doc("V4_DOC10_NONCORPOREAL_FORMS.png"), "S6", label="RECOMMENDATION J"),
        item("holografische Muster", doc("V4_DOC11_HOLOGRAPHIC_BARRIER.png"), "S6", label="RECOMMENDATION K"),
        item("unerwünschte außerkörperliche", ai("GWV2_IMG07_NONCORPOREAL_BARRIER_CLAIM_16x9.png"), "S6", label="CLAIM VISUALIZATION"),
        item("kein Entspannungskurs", card("V2_CARD03_MECHANISM_LADDER.png"), "S6", label="A COMPLETE WORLD MODEL"),
        item("was Bewusstsein sein", ai("GWV2_IMG07_NONCORPOREAL_BARRIER_CLAIM_16x9.png"), "S6", label="CLAIM VISUALIZATION"),

        # S7 — evidence standards.
        item("Ein Teil dieser Geschichte", ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"), "S7", label="TESTABLE QUESTIONS"),
        item("Meta-Analyse von 2019", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S7", label="META-ANALYSIS · 2019"),
        item("moderaten Effekt", card("V2_CARD05_EVIDENCE_SCALE.png"), "S7", label="MODERATE AVERAGE EFFECT"),
        item("kein Beleg für Gateway", card("V2_CARD03_MECHANISM_LADDER.png"), "S7", label="NOT THE WHOLE GATEWAY SYSTEM"),
        item("systematischer Review von 2023", rp("GW_PLOS_PDF07_PRISMA.png"), "S7", label="SYSTEMATIC REVIEW · 2023"),
        item("Fünf Studien", p1("qa_renders", "CARD05_CLAIM_GAP.png"), "S7", label="5 SUPPORT · 8 CONTRADICT · 1 MIXED"),
        item("Methoden, Frequenzen", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S7", label="HETEROGENEOUS METHODS"),
        item("Selbst ein klarer", card("V2_CARD05_EVIDENCE_SCALE.png"), "S7", label="SMALL EFFECT ≠ LARGE CLAIM"),
        item("neue, überprüfbare Information", ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"), "S7", label="VERIFIABLE NEW INFORMATION"),
        item("Ziel müsste vorher", card("V2_CARD04_TEST_PROTOCOL.png"), "S7", label="PRESELECT TARGET"),
        item("Auswertung müsste blind", card("V2_CARD04_TEST_PROTOCOL.png"), "S7", label="BLIND EVALUATION"),
        item("Trefferregeln", card("V2_CARD04_TEST_PROTOCOL.png"), "S7", label="LOCK SCORING · REPEAT"),
        item("veränderter Zustand", ai("GWV2_IMG04_BINAURAL_LISTENING_CLOSEUP_16x9.png"), "S7", label="A FINDING ABOUT EXPERIENCE"),
        item("verborgenes Ziel", ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"), "S7", label="A FINDING ABOUT INFORMATION"),
        item("eigentliche Beweislücke", card("V2_CARD05_EVIDENCE_SCALE.png"), "S7", label="THE EVIDENCE GAP"),

        # S8 — concise evidence residue and callback.
        item("Was bleibt", p1("qa_renders", "CARD06_EVIDENCE_RESIDUE.png"), "S8", label="WHAT REMAINS"),
        item("Der Bericht ist echt", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S8", label="DOCUMENTED"),
        item("Datum, Auftrag", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S8", label="DATE · TASK · AUTHOR"),
        item("Focus Levels", p1("qa_renders", "CARD03_FOCUS_LEVELS.png"), "S8", label="FOCUS LEVELS · DOCUMENTED"),
        item("militärische Interesse", luna("GWV2_IMG_001_Fort_Meade_entrance_2009_PD.jpg"), "S8", label="MILITARY ASSESSMENT"),
        item("Bewusstsein könne", ai("GWV2_IMG06_CONSCIOUSNESS_FIELD_MODEL_16x9.png"), "S8", label="CLAIM IN THE REPORT"),
        item("keinen belastbaren", card("V2_CARD05_EVIDENCE_SCALE.png"), "S8", label="NO ROBUST OPERATIONAL EVIDENCE"),
        item("virale Kurzfassung", ai("GWV2_IMG01_THREE_OBSERVERS_16x9.png"), "S8", label="THE VIRAL VERSION"),
        item("tatsächliche Geschichte", doc("V4_DOC09_RECOMMENDATION_H.png"), "S8", label="THE ACTUAL DOCUMENT"),
        item("Test mit Beobachtern", card("V2_CARD01_THREE_OBSERVERS.png"), "S8", label="PAST · PRESENT · FUTURE"),
        item("nicht-körperliche Intelligenzen", doc("V4_DOC10_NONCORPOREAL_FORMS.png"), "S8", label="RECOMMENDATION J"),
        item("mentale Schutzmuster", doc("V4_DOC11_HOLOGRAPHIC_BARRIER.png"), "S8", label="RECOMMENDATION K"),
        item("Nicht der Beweis", doc("V4_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png"), "S8", label="THE CONDITIONAL ENDING"),
        item("Der Fund ist diese Seite", doc("V4_DOC09_RECOMMENDATION_H.png"), "S8", label="THE IMPOSSIBLE · PLANNED ON PAPER"),
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
        row.update({"anchor": shot["anchor"], "shot_id": f"GWV4_{i:03d}", "start": round(start, 3),
                    "end": round(end, 3), "duration": round(end - start, 3)})
        rows.append(row)
    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PROD / "captions").mkdir(parents=True, exist_ok=True)
    (PROD / "captions" / "EP02_GATEWAY_V4_de.srt").write_bytes(SRT.read_bytes())
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
    path = PROD / "render" / "EP02_GATEWAY_V4_graphics.ass"
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
    picture = PROD / "render" / "EP02_GATEWAY_V4_picture_lock.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(picture)])
    ass = graphics(rows); assf = "ass='" + str(ass).replace("\\", "/").replace(":", r"\:") + "'"
    FINAL.mkdir(parents=True, exist_ok=True)
    out = FINAL / "EP02_GATEWAY_V4_FINAL_1080p.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(picture), "-i", str(AUDIO), "-vf", assf,
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)])
    print(out)


def qa():
    video = FINAL / "EP02_GATEWAY_V4_FINAL_1080p.mp4"
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
    (FINAL / "EP02_GATEWAY_V4_QA.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-vf", "fps=1/32,scale=384:216,tile=5x4", "-frames:v", "1", "-q:v", "2", str(FINAL / "EP02_GATEWAY_V4_CONTACT_SHEET.jpg")])
    print(json.dumps({"duration": duration, "shots": len(rows), "avg": round(duration/len(rows), 2), "checks": checks}, indent=2))
    if not all(checks.values()): raise RuntimeError("QA failed")


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=["timeline", "render", "qa", "all"])
    parser.add_argument("--force", action="store_true"); parser.add_argument("--limit", type=int); args = parser.parse_args()
    if args.command in ("timeline", "all"): build_timeline()
    if args.command in ("render", "all"): render(args.force, args.limit)
    if args.command in ("qa", "all") and not args.limit: qa()


if __name__ == "__main__": main()
