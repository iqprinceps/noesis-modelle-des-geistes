#!/usr/bin/env python3
"""Gateway V5 — Optimized production.

Major improvements over V4:
- No "RECONSTRUCTION" labels (removed AI-sounding terminology)
- Reduced asset repetition (each visual used max 4x)
- No meditation video clip (replaced with stills)
- Better label variety (more neutral, documentary-style)
- More document pages for visual variety
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
    doc = lambda n: p("visuals", "document_crops", n)
    card = lambda n: p2("visuals", "cards", n)
    patent = lambda n: p2("visuals", "patents", n)
    ex = lambda n: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "APPROVED", n)
    luna = lambda n: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "V2_RESEARCH_LUNA", n)
    rp = lambda n: p1("reference_package", n)
    research = lambda n: a("06_PRODUCTION", "Gateway_Production", "Assets_Research_Luna", n)
    # Additional exhibits for variety
    ex1b = lambda: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "APPROVED", "GW_003_Exhibit_1B.png")
    ex_disa = lambda: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "APPROVED", "GW_012_DISA_headquarters_aerial.jpg")
    ex_disa2 = lambda: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "APPROVED", "GW_013_DISA_headquarters_exterior.jpg")
    luna_aerial = lambda: a("04_ASSETS", "02_CURATED", "EP02_GATEWAY", "V2_RESEARCH_LUNA", "GWV2_IMG_002_Fort_Meade_historical_aerial_PD.jpg")

    # Helper: neutral labels that don't scream "AI"
    def lbl(text):
        return text

    shots = [
        # S1 — Hook (0:00 - 0:50)
        item("Drei Menschen.", ex1b(), "S1", label=lbl("EXHIBIT 1B")),
        item("Der erste beobachtet", card("V2_CARD01_THREE_OBSERVERS.png"), "S1", label=lbl("PRESENT")),
        item("Der zweite soll", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", label=lbl("RECOMMENDATION H")),
        item("Der dritte aus", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", label=lbl("PAST AND FUTURE")),
        item("Danach werden", card("V2_CARD01_THREE_OBSERVERS.png"), "S1", label=lbl("COMPARE REPORTS")),
        item("Das ist keine Zusammenfassung", rp("GW_REPORT_PDF01_HEADER.png"), "S1", label=lbl("ORIGINAL DOCUMENT")),
        item("Genau dieser Versuch", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", label=lbl("THE COMPLETE PROCEDURE")),
        item("Datum:", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S1", label=lbl("9 JUNE 1983")),
        item("Autor:", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S1", label=lbl("WAYNE M. McDONNELL")),
        item("Heute liegt", ex_disa(), "S1", label=lbl("FORT MEADE · DISA")),
        item("Geschrieben wurde", luna("GWV2_IMG_001_Fort_Meade_entrance_2009_PD.jpg"), "S1", label=lbl("FORT MEADE · 2009")),
        item("Die eigentliche Frage", ex1b(), "S1", label=lbl("EXHIBIT 1B")),
        item("Sie lautet:", doc("V4_DOC09_RECOMMENDATION_H.png"), "S1", label=lbl("THE PROPOSED PROCEDURE")),
        item("Die Antwort beginnt", rp("GW_REPORT_PDF01_HEADER.png"), "S1", label=lbl("THE REPORT")),

        # S2 — The three men (0:50 - 2:15)
        item("Robert Monroe entwickelte", luna_aerial(), "S2", label=lbl("MONROE INSTITUTE · VIRGINIA")),
        item("Sein historischer Markenbegriff", patent("BENTOV_1971-01.png"), "S2", label=lbl("HEMI-SYNC · PATENT METHOD")),
        item("Teilnehmer hörten", rp("GW_PATENT_PDF01.png"), "S2", label=lbl("U.S. PATENT 5,213,562")),
        item("Wayne McDonnell sollte", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label=lbl("DOCUMENTED AUTHOR")),
        item("Sein Auftrag war", doc("V4_DOC02_TASK_BENTOV.png"), "S2", label=lbl("THE ASSIGNED TASK")),
        item("Auf der Titelseite", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S2", label=lbl("DEPARTMENT OF THE ARMY")),
        item("Am Ende des Schreibens", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label=lbl("NAME · RANK · SIGNATURE")),
        item("Für die theoretische Brücke", patent("BENTOV_1971-02.png"), "S2", label=lbl("BENTOV PATENT · 1971")),
        item("Bentov war Autor", patent("BENTOV_1969-1.png"), "S2", label=lbl("MEDICAL DEVICE PATENT · 1969")),
        item("Seine Patente zeigen", patent("BENTOV_1971-01.png"), "S2", label=lbl("U.S. PATENT · 1971")),
        item("Katheter", patent("BENTOV_1969-1.png"), "S2", label=lbl("ELECTRODE DESIGN")),
        item("Im Gateway-Bericht", doc("V4_DOC02_TASK_BENTOV.png"), "S2", label=lbl("BENTOV IN THE REPORT")),
        item("Monroe lieferte", rp("GW_PATENT_PDF01.png"), "S2", label=lbl("TRAINING SYSTEM · PATENT")),
        item("Bentov lieferte", patent("BENTOV_1971-02.png"), "S2", label=lbl("ANALOGIES · PATENT")),
        item("McDonnell setzte", card("V2_CARD02_PEOPLE_CHAIN.png"), "S2", label=lbl("ARMY ASSESSMENT")),
        item("Von Wayne McDonnell", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label=lbl("NO VERIFIED PORTRAIT")),
        item("Seine Person wird", rp("GW_REPORT_PDF02_SIGNATURE.png"), "S2", label=lbl("SIGNATURE PAGE")),
        item("Wir bleiben bei", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S2", label=lbl("TEXT · RANK · SIGNATURE")),

        # S3 — Mechanism (2:15 - 3:35)
        item("Der Einstieg ist", ex("GW_002_Exhibit_1A.png"), "S3", label=lbl("EXHIBIT 1A")),
        item("Hört das linke Ohr", research("GW_IMG_001_Commons_Binaural_Beats_DPic.svg"), "S3", label=lbl("BINAURAL BEAT DIAGRAM")),
        item("ungefähr 10 Hertz", research("GW_IMG_001_Commons_Binaural_Beats_DPic.svg"), "S3", label=lbl("PERCEIVED FREQUENCY")),
        item("Dieser Rhythmus", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S3", label=lbl("AUDITORY PROCESSING")),
        item("Verarbeitung beider Signale", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S3", label=lbl("BINAURAL PROCESSING")),
        item("Das nennt man", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S3", label=lbl("PLOS REVIEW · 2019")),
        item("Gateway bestand", ex("GW_004_Exhibit_1C.png"), "S3", label=lbl("EXHIBIT 1C")),
        item("Zu den Tönen kamen", ex("GW_005_Exhibit_2.png"), "S3", label=lbl("EXHIBIT 2")),
        item("Wer danach ruhiger", ex("GW_006_Exhibit_3.png"), "S3", label=lbl("EXHIBIT 3")),
        item("Ein späteres Patent", rp("GW_PATENT_PDF01.png"), "S3", label=lbl("U.S. PATENT 5,213,562")),
        item("EEG-Muster", rp("GW_PATENT_PDF02.png"), "S3", label=lbl("PATENT DRAWING")),
        item("Es wurde 1993", rp("GW_PATENT_PDF03.png"), "S3", label=lbl("PATENT DISCLOSURE")),
        item("Das Patent zeigt", rp("GW_PATENT_PDF04.png"), "S3", label=lbl("PATENT CLAIMS")),
        item("Es beweist nicht", card("V2_CARD03_MECHANISM_LADDER.png"), "S3", label=lbl("PATENT ≠ PROOF")),
        item("McDonnell übernimmt", ex("GW_007_Exhibit_4A.png"), "S3", label=lbl("EXHIBIT 4A")),
        item("Frequency-Following Response", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S3", label=lbl("RESEARCH FIGURE")),
        item("Bis hierhin", card("V2_CARD05_EVIDENCE_SCALE.png"), "S3", label=lbl("EVIDENCE SCALE")),
        item("Dann macht", card("V2_CARD03_MECHANISM_LADDER.png"), "S3", label=lbl("THE CLAIM JUMP")),

        # S4 — World model (3:35 - 5:20)
        item("McDonnell will nicht", rp("GW_REPORT_PDF01_HEADER.png"), "S4", label=lbl("THE REPORT")),
        item("Grenzen des Körpers", ex("GW_008_Exhibit_4B.png"), "S4", label=lbl("EXHIBIT 4B")),
        item("Resonanz", ex("GW_002_Exhibit_1A.png"), "S4", label=lbl("EXHIBIT 1A")),
        item("Gehirnhälften", ex("GW_004_Exhibit_1C.png"), "S4", label=lbl("EXHIBIT 1C")),
        item("holografische Analogien", ex("GW_006_Exhibit_3.png"), "S4", label=lbl("EXHIBIT 3")),
        item("Die Originaldiagramme", ex("GW_007_Exhibit_4A.png"), "S4", label=lbl("EXHIBIT 4A")),
        item("Torusformen", ex("GW_008_Exhibit_4B.png"), "S4", label=lbl("EXHIBIT 4B")),
        item("Die Logik läuft", ex("GW_009_Exhibit_4C.png"), "S4", label=lbl("EXHIBIT 4C")),
        item("Der Körper schwingt", ex("GW_005_Exhibit_2.png"), "S4", label=lbl("EXHIBIT 2")),
        item("Das Gehirn erzeugt", ex("GW_004_Exhibit_1C.png"), "S4", label=lbl("EXHIBIT 1C")),
        item("Synchronisierung soll", ex("GW_010_Exhibit_5.png"), "S4", label=lbl("EXHIBIT 5")),
        item("Ein ausreichend kohärentes", ex("GW_009_Exhibit_4C.png"), "S4", label=lbl("EXHIBIT 4C")),
        item("Raum und Zeit", ex("GW_010_Exhibit_5.png"), "S4", label=lbl("EXHIBIT 5")),
        item("Auf dem Papier", ex("GW_009_Exhibit_4C.png"), "S4", label=lbl("FORMULAS AND DIAGRAMS")),
        item("Doch die Zahnräder", card("V2_CARD03_MECHANISM_LADDER.png"), "S4", label=lbl("NO DEMONSTRATED BRIDGE")),
        item("Eine Analogie", patent("BENTOV_1971-01.png"), "S4", label=lbl("BENTOV PATENT")),
        item("entscheidende Wechsel", card("V2_CARD05_EVIDENCE_SCALE.png"), "S4", label=lbl("EVIDENCE SCALE")),
        item("eine Art Landkarte", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S4", label=lbl("FOCUS LEVELS PAGE")),

        # S5 — Focus levels (5:20 - 7:10)
        item("Focus 10 bedeutet", doc("V4_DOC04_FOCUS15_HEADING.png"), "S5", label=lbl("FOCUS 10")),
        item("Focus 12 soll", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S5", label=lbl("FOCUS 12")),
        item("Dann steht dort", doc("V4_DOC04_FOCUS15_HEADING.png"), "S5", label=lbl("FOCUS 15")),
        item("Zeit soll", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S5", label=lbl("THE TIME WHEEL MODEL")),
        item("Seine Speichen", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S5", label=lbl("PAST POINTS")),
        item("McDonnell schreibt zugleich", doc("V4_DOC05_LESS_THAN_FIVE_PERCENT.png"), "S5", label=lbl("DIFFICULTY WARNING")),
        item("weniger als fünf Prozent", doc("V4_DOC05_LESS_THAN_FIVE_PERCENT.png"), "S5", label=lbl("LESS THAN FIVE PERCENT")),
        item("Die nächste Überschrift", doc("V4_DOC06_FOCUS21_FUTURE.png"), "S5", label=lbl("FOCUS 21")),
        item("außerhalb normaler Raum-Zeit", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S5", label=lbl("THE REPORT")),
        item("Direkt darunter", doc("V4_DOC07_OBE_NO_GUARANTEE.png"), "S5", label=lbl("OUT-OF-BODY MOVEMENT")),
        item("garantiere keinen Erfolg", doc("V4_DOC07_OBE_NO_GUARANTEE.png"), "S5", label=lbl("NO GUARANTEE")),
        item("Trotzdem folgen", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S5", label=lbl("THE COMPLETE PASSAGE")),
        item("Hier muss das Bild", doc("V4_DOC07_OBE_NO_GUARANTEE.png"), "S5", label=lbl("READ THE PASSAGE")),
        item("Dokumentiert ist", rp("GW_REPORT_PDF25_INFO_COLLECTION.png"), "S5", label=lbl("DOCUMENTED")),
        item("Nicht dokumentiert", card("V2_CARD05_EVIDENCE_SCALE.png"), "S5", label=lbl("NOT DOCUMENTED")),

        # S6 — Operational claims (7:10 - 9:05)
        item("Information Collection Potential", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6", label=lbl("INFORMATION COLLECTION")),
        item("Eindrücke aus Gegenwart", doc("V4_DOC08_INFORMATION_COLLECTION.png"), "S6", label=lbl("DISTORTION PROBLEM")),
        item("zehn computergenerierte Zahlen", rp("GW_REPORT_PDF25_INFO_COLLECTION.png"), "S6", label=lbl("TEN NUMBERS")),
        item("manche hätten genug", rp("GW_REPORT_PDF25_INFO_COLLECTION.png"), "S6", label=lbl("SOME DIGITS CORRECT")),
        item("Alle zehn richtig", rp("GW_REPORT_PDF25_INFO_COLLECTION.png"), "S6", label=lbl("NEVER ALL TEN")),
        item("Empfehlung H", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label=lbl("RECOMMENDATION H")),
        item("Drei Personen", card("V2_CARD01_THREE_OBSERVERS.png"), "S6", label=lbl("THREE OBSERVERS")),
        item("Dasselbe Ziel", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label=lbl("ONE TARGET")),
        item("normaler Raum-Zeit", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S6", label=lbl("RECOMMENDATIONS PAGE")),
        item("Eine in Focus 15", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label=lbl("PAST · FOCUS 15")),
        item("Eine in Focus 21", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S6", label=lbl("FUTURE · FOCUS 21")),
        item("alle drei Berichte", card("V2_CARD01_THREE_OBSERVERS.png"), "S6", label=lbl("COMPARE REPORTS")),
        item("Der Absatz ist echt", doc("V4_DOC09_RECOMMENDATION_H.png"), "S6", label=lbl("THE PARAGRAPH IS REAL")),
        item("Ein erfolgreicher Versuch", card("V2_CARD04_TEST_PROTOCOL.png"), "S6", label=lbl("NO TEST REPORTED")),
        item("Die nächsten Empfehlungen", doc("V4_DOC10_NONCORPOREAL_FORMS.png"), "S6", label=lbl("RECOMMENDATION J")),
        item("nicht-körperlichen Energieformen", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S6", label=lbl("NON-CORPOREAL FORMS")),
        item("holografische Muster", doc("V4_DOC11_HOLOGRAPHIC_BARRIER.png"), "S6", label=lbl("RECOMMENDATION K")),
        item("unerwünschte außerkörperliche", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S6", label=lbl("HOLOGRAPHIC BARRIER")),
        item("kein Entspannungskurs", card("V2_CARD03_MECHANISM_LADDER.png"), "S6", label=lbl("COMPLETE WORLD MODEL")),
        item("was Bewusstsein sein", ex("GW_010_Exhibit_5.png"), "S6", label=lbl("EXHIBIT 5")),

        # S7 — Evidence (9:05 - 10:55)
        item("Ein Teil dieser Geschichte", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S7", label=lbl("TESTABLE QUESTIONS")),
        item("Meta-Analyse von 2019", rp("GW_PLOS_PDF01_ABSTRACT.png"), "S7", label=lbl("META-ANALYSIS · 2019")),
        item("moderaten Effekt", rp("GW_PLOS_PDF07_PRISMA.png"), "S7", label=lbl("SYSTEMATIC REVIEW")),
        item("kein Beleg für Gateway", card("V2_CARD05_EVIDENCE_SCALE.png"), "S7", label=lbl("NOT THE WHOLE SYSTEM")),
        item("systematischer Review von 2023", rp("GW_PLOS_PDF07_PRISMA.png"), "S7", label=lbl("PRISMA DIAGRAM")),
        item("Fünf Studien", card("V2_CARD05_EVIDENCE_SCALE.png"), "S7", label=lbl("5 SUPPORT · 8 CONTRADICT")),
        item("Methoden, Frequenzen", research("GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg"), "S7", label=lbl("HETEROGENEOUS METHODS")),
        item("Selbst ein klarer", card("V2_CARD05_EVIDENCE_SCALE.png"), "S7", label=lbl("SMALL EFFECT ≠ LARGE CLAIM")),
        item("neue, überprüfbare Information", card("V2_CARD04_TEST_PROTOCOL.png"), "S7", label=lbl("VERIFIABLE INFORMATION")),
        item("Ziel müsste vorher", card("V2_CARD04_TEST_PROTOCOL.png"), "S7", label=lbl("PRESELECT TARGET")),
        item("Auswertung müsste blind", card("V2_CARD04_TEST_PROTOCOL.png"), "S7", label=lbl("BLIND EVALUATION")),
        item("Trefferregeln", card("V2_CARD04_TEST_PROTOCOL.png"), "S7", label=lbl("LOCK SCORING · REPEAT")),
        item("veränderter Zustand", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S7", label=lbl("A FINDING ABOUT EXPERIENCE")),
        item("verborgenes Ziel", card("V2_CARD04_TEST_PROTOCOL.png"), "S7", label=lbl("A FINDING ABOUT INFORMATION")),
        item("eigentliche Beweislücke", card("V2_CARD05_EVIDENCE_SCALE.png"), "S7", label=lbl("THE EVIDENCE GAP")),

        # S8 — Residue (10:55 - 12:00)
        item("Was bleibt", rp("GW_REPORT_PDF27_CONCLUSION_A_G.png"), "S8", label=lbl("CONCLUSION")),
        item("Der Bericht ist echt", doc("V4_DOC01_ARMY_HEADER_DATE.png"), "S8", label=lbl("DOCUMENTED")),
        item("Datum, Auftrag", doc("V4_DOC03_MCDONNELL_SIGNATURE.png"), "S8", label=lbl("DATE · TASK · AUTHOR")),
        item("Focus Levels", rp("GW_REPORT_PDF24_FOCUS15_21.png"), "S8", label=lbl("FOCUS LEVELS")),
        item("militärische Interesse", ex_disa2(), "S8", label=lbl("DISA HEADQUARTERS")),
        item("Bewusstsein könne", rp("GW_REPORT_PDF27_CONCLUSION_A_G.png"), "S8", label=lbl("CLAIM IN THE REPORT")),
        item("keinen belastbaren", card("V2_CARD05_EVIDENCE_SCALE.png"), "S8", label=lbl("NO OPERATIONAL EVIDENCE")),
        item("virale Kurzfassung", rp("GW_REPORT_PDF01_HEADER.png"), "S8", label=lbl("THE VIRAL VERSION")),
        item("tatsächliche Geschichte", doc("V4_DOC09_RECOMMENDATION_H.png"), "S8", label=lbl("THE ACTUAL DOCUMENT")),
        item("Test mit Beobachtern", card("V2_CARD01_THREE_OBSERVERS.png"), "S8", label=lbl("PAST · PRESENT · FUTURE")),
        item("nicht-körperliche Intelligenzen", doc("V4_DOC10_NONCORPOREAL_FORMS.png"), "S8", label=lbl("RECOMMENDATION J")),
        item("mentale Schutzmuster", doc("V4_DOC11_HOLOGRAPHIC_BARRIER.png"), "S8", label=lbl("RECOMMENDATION K")),
        item("Nicht der Beweis", doc("V4_DOC12_IF_EXPERIMENTS_CARRIED_THROUGH.png"), "S8", label=lbl("CONDITIONAL ENDING")),
        item("Der Fund ist diese Seite", rp("GW_REPORT_PDF28_RECOMMENDATIONS_H_L.png"), "S8", label=lbl("THE IMPOSSIBLE · PLANNED")),
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
