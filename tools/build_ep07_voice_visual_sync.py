from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4"
KIT = EP / "IMAGE_GENERATION_KIT"
OUT = KIT / "03_GENERATED_OUTPUT" / "NanoBanana_Pro_2K_Series"
CARDS = KIT / "03_GENERATED_OUTPUT" / "CARDS"
ASSETS = KIT / "02_ASSETS"
DEST = EP / "EP07_VOICE_VISUAL_SYNC.csv"
SCRIPT = EP / "EP07_SPRECHERFASSUNG_GEORGE_FINAL.md"
VOICE_DIR = EP / "VOICE_EP07"


# Planned windows are editorial estimates. Forced alignment replaces them after
# George has been generated; the text anchors and order remain canonical.
TAKES = [
    ("001", "S1", 0, 23, "Comans Nacht", "ROOM_1692"),
    ("002", "S1", 23, 47, "Lähmung, Druck, bekanntes Muster", "PRESSURE_DRY"),
    ("003", "S1", 47, 76, "Gericht und öffentliche Konsequenz", "COURT_TRANSITION"),
    ("004", "S2", 76, 103, "Füsslis Nachtmahr", "GALLERY_AIR"),
    ("005", "S2", 103, 128, "Das wiedererkannte Motiv", "CANVAS_DETAIL"),
    ("006", "S2", 128, 154, "Viele Ursprünge", "PAPER_GEOGRAPHY"),
    ("007", "S3", 154, 180, "Mahr, Incubus, Kanashibari", "CULTURAL_PAPER"),
    ("008", "S3", 180, 205, "Jinn, China, Old Hag", "CULTURAL_ROOM"),
    ("009", "S3", 205, 229, "Körper vor Mythos", "THRESHOLD_TONE"),
    ("010", "S4", 229, 254, "Historische Deutungswelt", "CHURCH_DISTANCE"),
    ("011", "S4", 254, 280, "Gegenmaßnahmen", "OBJECT_FOLEY"),
    ("012", "S4", 280, 307, "Private Nacht wird öffentlich", "COURT_TRANSITION"),
    ("013", "S5", 307, 333, "Huffords Feldarbeit", "FIELD_TAPE"),
    ("014", "S5", 333, 358, "Erfahrung vor Erzählung", "PENCIL_PAPER"),
    ("015", "S5", 358, 384, "Kultur wirkt danach", "LOW_FEEDBACK"),
    ("016", "S6", 384, 407, "Zwei Menschen, gleiche Nacht", "TWO_ROOMS"),
    ("017", "S6", 407, 431, "CTA Erfahrung oder Kultur", "CTA_SILENCE"),
    ("018", "S7", 431, 454, "Studie Ägypten und Dänemark", "RESEARCH_DESK"),
    ("019", "S7", 454, 479, "Zwei Deutungsräume", "TWO_ROOMS"),
    ("020", "S7", 479, 504, "Angst, Dauer und Häufigkeit", "CLINICAL_PULSE"),
    ("021", "S7", 504, 529, "Rückkopplung", "FEEDBACK_RISE"),
    ("022", "S8", 529, 555, "Rückkehr nach Salem", "COURT_RETURN"),
    ("023", "S8", 555, 582, "Körper, Kultur, Körper", "MATERIAL_BREATH"),
    ("024", "S8", 582, 607, "Langsame Überlieferung", "PRINT_TO_WIRE"),
    ("025", "S8", 607, 632, "Radio und frühes Internet", "RADIO_HANDOFF"),
    ("026", "END", 632, 652, "Endcard", "END_TONE"),
]


# Token prefixes: IMG/SHOT existing still, CLIP existing motion, CARD existing
# card, SRC source-derived editor frame, NEW paid generation still missing,
# ORIG missing original/source acquisition.
CUES = {
    "001": [
        ("Salem, Massachusetts", "IMG001_SALEM_BEDROOM_COMAN_RECON.png"),
        ("Mai sechzehnhundertzweiundneunzig", "SRC:EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf:p1_full"),
        ("Richard Coman", "SRC:EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf:p1_name_and_opening"),
        ("liegt nachts wach", "IMG002_COMAN_TRIES_TO_WAKE_WIFE.png"),
        ("drückt ihn nieder", "SRC:EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf:p1_pressure_passage"),
        ("Salem als konkreter Ort", "SRC:EP07_Salem_Village_1692_map_Upham_1866.jpg:full_map"),
    ],
    "002": [
        ("weder sprechen noch bewegen", "IMG012_EXPERIENCE_BEFORE_STORY.png"),
        ("Starre und Druck", "CLIP002_NIGHTMARE_PRESSURE.mp4"),
        ("Comans Formulierung", "SRC:EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf:p1_cannot_speak_nor_stir"),
        ("bekanntes Schlafmuster", "SRC:EP07_REM_Polysomnography_30sec.png:full_trace"),
        ("Messsensoren statt Dämon", "SRC:EP07_Sleep_Studies_NHLBI_Polysomnography.jpg:sensor_detail"),
        ("heutige Schlafparalyse", "NEW:IMG033_AWAKE_BRAIN_BODY_LOCK.png"),
    ],
    "003": [
        ("Welt ohne Schlafmedizin", "IMG003_PRIVATE_NIGHT_TO_COURT.png"),
        ("Aussage unter Eid", "SRC:EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf:p2_signature_and_oath"),
        ("Bridget Bishop vor Gericht", "SRC:EP07_Bridget_Bishop_Examination_1692.pdf:p1_full"),
        ("neunzehnter April", "SRC:EP07_Bridget_Bishop_Examination_1692.pdf:p1_heading_date"),
        ("größeres Verfahren", "IMG004_BRIDGET_BISHOP_COURT_CONTEXT_RECON.png"),
        ("konkrete historische Frau", "SRC:EP07_Bridget_Bishop_lithograph.jpg:full_portrait"),
        ("privat wird öffentlich", "CLIP003_SALEM_PUBLIC_TRANSFORMATION.mp4"),
    ],
    "004": [
        ("Henry Füssli", "SRC:EP07_Fuseli_The_Nightmare_1781.jpg:full_painting"),
        ("Frau rücklings", "SRC:EP07_Fuseli_The_Nightmare_1781.jpg:woman_detail"),
        ("Gestalt auf der Brust", "SRC:EP07_Fuseli_The_Nightmare_1781.jpg:incubus_detail"),
        ("Pferdekopf", "SRC:EP07_Fuseli_The_Nightmare_1781.jpg:horse_detail"),
        ("Motiv im Raum", "IMG005_NIGHTMARE_MOTIF_ROOM_BASE.png"),
    ],
    "005": [
        ("anderer Künstler", "SRC:EP07_Abildgaard_Nightmare_1800.jpg:full_painting"),
        ("Druckmotiv", "SRC:EP07_Abildgaard_Nightmare_1800.jpg:figure_detail"),
        ("Bild wandert weiter", "SHOT04_FUSELI_TO_SCREEN_TRANSITION.png"),
        ("Druck als Bildform", "NEW:IMG024_NIGHTMARE_PRINT_WORKSHOP.png"),
        ("Angriff statt freier Fantasie", "SRC:EP07_Abildgaard_Nightmare_1800.jpg:pressure_detail"),
    ],
    "006": [
        ("ähnliche Abläufe", "IMG006_SAME_MECHANIC_DIFFERENT_ROOMS.png"),
        ("weit auseinanderliegende Orte", "SRC:EP07_Salem_Village_1692_map_Upham_1866.jpg:map_edge_detail"),
        ("kein einzelner Ursprung", "NEW:IMG025_MANY_ORIGINS_ARCHIVE_TABLE.png"),
        ("körperliches Rohmaterial", "NEW:IMG026_SHARED_MECHANIC_RELIEF.png"),
        ("historische Tiefe", "SRC:EP07_Queen_of_the_Night_Burney_Relief.jpg:full_object"),
        ("Relief als getrenntes Museumsobjekt", "IMG008_BURNEY_RELIEF_SOURCE_ROOM.png"),
    ],
    "007": [
        ("viele Namen", "SHOT02_MANY_NAMES_PAPER_LAYERS.png"),
        ("Mahr und Incubus", "SRC:EP07_Jinn_from_Ali_manuscript.png:full_manuscript"),
        ("japanischer Bildraum", "SRC:EP07_Kunisada_The_Ghost.jpg:full_print"),
        ("anderes japanisches Motiv", "SRC:EP07_Yoshitoshi_Shoki.jpg:full_print"),
        ("Gebundensein", "NEW:IMG027_KANASHIBARI_THRESHOLD.png"),
        ("Namen im Überblick", "CARD001_VIELE_NAMEN.png"),
    ],
    "008": [
        ("Jinn als Deutung", "SRC:EP07_Jinn_from_Ali_manuscript.png:figure_detail"),
        ("älterer Bildanker", "SRC:EP07_Queen_of_the_Night_Burney_Relief.jpg:face_detail"),
        ("Neufundland", "NEW:IMG028_NEWFOUNDLAND_ORAL_HISTORY.png"),
        ("Neufundland als Ort", "ORIG:ORIG_NEWFOUNDLAND_MAP_PD.png:full_map"),
        ("chinesische Überlieferung", "ORIG:ORIG_CHINESE_GHOST_PRESSURE_SOURCE_PD.png:source_detail"),
        ("keine einfache Familie", "IMG007_MARA_INCUBUS_KANASHIBARI_BASE.png"),
    ],
    "009": [
        ("Zustand zuerst", "IMG012_EXPERIENCE_BEFORE_STORY.png"),
        ("Worte entstehen", "IMG013_BODY_TO_STORY_FLOW_BASE.png"),
        ("kulturelle Form bildet sich", "CLIP001_CULTURAL_MASKS.mp4"),
        ("Erlebnis vor Bekanntschaft", "NEW:IMG032_UNNAMED_FIRST_EPISODE.png"),
        ("ein Name wartet bereits", "NEW:IMG051_NAME_WAITING_IN_SHADOW.png"),
        ("älteres Schwellenmotiv", "SRC:EP07_Queen_of_the_Night_Burney_Relief.jpg:talons_detail"),
    ],
    "010": [
        ("historische Deutungswelt", "SRC:EP07_Malleus_Maleficarum_1928_Wellcome.pdf:p1_title_and_metadata"),
        ("Dämonologie und Hexerei", "SRC:EP07_Malleus_1494_Bull_Innocent_VIII_Wellcome.jpg:full_page"),
        ("frühneuzeitlicher Raum", "IMG009_MEDIEVAL_BEDROOM_EXPLANATION.png"),
        ("Anschuldigung im Bild", "SRC:EP07_Examination_of_a_Witch_Matteson_1853.jpg:full_painting_later_depiction"),
        ("Erklärungen der Umgebung", "NEW:IMG029_HOUSEHOLD_EXPLANATION_CHOICES.png"),
    ],
    "011": [
        ("alltägliche Gegenmaßnahmen", "IMG010_RITUAL_RESPONSE_TABLE.png"),
        ("gedruckte Dämonologie", "SRC:EP07_Malleus_Maleficarum_1928_Wellcome.pdf:editor_selected_relevant_passage"),
        ("Gerichtsordnung", "SRC:EP07_Trial_George_Jacobs_Salem_LOC.jpg:full_later_depiction"),
        ("Gemeinschaft", "SRC:EP07_Witchcraft_at_Salem_Village_1876.jpg:full_later_depiction"),
        ("Handlung gegen das Wesen", "NEW:IMG030_RITUAL_AS_PRACTICAL_RESPONSE.png"),
        ("Ritual bringt Erleichterung", "SHOT01_SALEM_EMPTY_BED.png"),
    ],
    "012": [
        ("persönlich wird öffentlich", "IMG003_PRIVATE_NIGHT_TO_COURT.png"),
        ("Publikum sammelt sich", "NEW:IMG050_PRIVATE_TO_PUBLIC_NETWORK.png"),
        ("Gericht als spätere Darstellung", "SRC:EP07_Trial_George_Jacobs_Salem_LOC.jpg:court_detail_later_depiction"),
        ("Gemeinschaft als spätere Darstellung", "SRC:EP07_Witchcraft_at_Salem_Village_1876.jpg:crowd_detail_later_depiction"),
        ("private Nacht wird Gericht", "CARD002_PRIVATNACHT_GERICHT.png"),
        ("unterschriebene Untersuchung", "SRC:EP07_Bridget_Bishop_Examination_1692.pdf:p1_signature_detail"),
    ],
    "013": [
        ("Hufford hört zu", "IMG011_HUFFORD_FIELD_NOTES_RECON.png"),
        ("Aufzeichnung und Notizen", "SHOT03_CASSETTE_NOTEBOOK_MACRO.png"),
        ("Huffords Buch als Forschungsanker", "ORIG:ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED.png:full_cover"),
        ("Neufundland verorten", "ORIG:ORIG_NEWFOUNDLAND_MAP_PD.png:newfoundland_detail"),
        ("Interview im Tageslicht", "NEW:IMG031_HUFFORD_FIELD_INTERVIEW.png"),
        ("Erinnerungsort statt Horrorbild", "SRC:EP07_Proctors_Ledge_Memorial.jpg:full_context"),
    ],
    "014": [
        ("Grundmuster vor Überlieferung", "NEW:IMG043_FIRST_EPISODE_BODY_TRACE.png"),
        ("unbenannter erster Anfall", "NEW:IMG032_UNNAMED_FIRST_EPISODE.png"),
        ("Hufford als Autor", "ORIG:ORIG_HUFFORD_PORTRAIT_LICENSED.png:portrait"),
        ("Körper wird Erzählung", "IMG013_BODY_TO_STORY_FLOW_BASE.png"),
        ("Druckereignis", "NEW:IMG056_PRESSURE_AS_MEMORY_RELIEF.png"),
        ("Huffords Umkehrung", "CARD003_HUFFORD_INVERSION.png"),
    ],
    "015": [
        ("Erfahrung und Kultur", "IMG015_EXPERIENCE_CULTURE_DECISION_BASE.png"),
        ("mögliche Rückkopplung", "IMG017_FEAR_SLEEP_FEEDBACK_LOOP_BASE.png"),
        ("Erzählung wird Körper", "IMG018_STORY_BECOMES_BODY.png"),
        ("Schlafmechanik als Boden", "NEW:IMG033_AWAKE_BRAIN_BODY_LOCK.png"),
        ("kulturelle Formen", "NEW:IMG055_CULTURAL_FORM_SETTLES.png"),
    ],
    "016": [
        ("zwei Menschen", "IMG014_TWO_PEOPLE_SAME_BODY_DIFFERENT_MODEL.png"),
        ("gleicher Ausgangszustand", "IMG016_EGYPT_DENMARK_MATCHED_BEDROOMS.png"),
        ("körperlicher Start", "NEW:IMG044_SAME_BODY_TWO_INTERPRETATIONS.png"),
        ("Druck und Präsenz", "NEW:IMG053_PRESSURE_PRESENCE_RELIEF.png"),
        ("zwei Erwartungen", "NEW:IMG034_TWO_EXPECTATIONS_THRESHOLD.png"),
    ],
    "017": [
        ("Erfahrung oder Kultur", "CARD006_CTA_ERFAHRUNG_KULTUR.png"),
        ("Entscheidung offen halten", "IMG015_EXPERIENCE_CULTURE_DECISION_BASE.png"),
        ("Formen verschieben sich", "NEW:IMG049_DECISION_LAYERS_HOLD.png"),
        ("viele Namen", "NEW:IMG060_WORD_LAYERS_CTA_BG.png"),
        ("Forschungsfrage", "ORIG:ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED.png:title_detail"),
        ("Frage zwischen zwei Modellen", "NEW:IMG052_QUESTION_BETWEEN_MODELS.png"),
    ],
    "018": [
        ("Jalal und Hinton", "ORIG:ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER.png:title_authors"),
        ("Studienaufbau", "ORIG:ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER.png:methods_detail"),
        ("Kulturvergleich", "CARD004_AEGYPTEN_DAENEMARK.png"),
        ("Ägypten verorten", "ORIG:ORIG_EGYPT_MAP_PD.png:full_map"),
        ("Dänemark verorten", "ORIG:ORIG_DENMARK_MAP_PD.png:full_map"),
    ],
    "019": [
        ("ägyptische Interviewumgebung", "NEW:IMG035_EGYPT_INTERVIEW_CONTEXT.png"),
        ("dänische Interviewumgebung", "NEW:IMG036_DENMARK_INTERVIEW_CONTEXT.png"),
        ("ägyptischer Quellenanker", "ORIG:ORIG_EGYPT_SLEEP_PARALYSIS_SOURCE.png:source_detail"),
        ("dänischer Quellenanker", "ORIG:ORIG_DENMARK_SLEEP_PARALYSIS_SOURCE.png:source_detail"),
        ("zwei Deutungsräume", "IMG014_TWO_PEOPLE_SAME_BODY_DIFFERENT_MODEL.png"),
        ("gleiches Phänomen", "IMG016_EGYPT_DENMARK_MATCHED_BEDROOMS.png"),
    ],
    "020": [
        ("Angst und Häufigkeit", "IMG017_FEAR_SLEEP_FEEDBACK_LOOP_BASE.png"),
        ("Ergebnis im Originalpaper", "ORIG:ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER.png:results_detail"),
        ("REM-Messspur", "SRC:EP07_REM_Polysomnography_30sec.png:rem_segment_detail"),
        ("Schlaflabor als Realität", "SRC:EP07_Sleep_Studies_NHLBI_Polysomnography.jpg:full_photo"),
        ("Kreislauf ohne Dämon", "NEW:IMG037_FEAR_SLEEP_DAY_NIGHT_LOOP.png"),
        ("Erzählung wird Körper", "IMG018_STORY_BECOMES_BODY.png"),
    ],
    "021": [
        ("Rückkopplungsmodell", "CARD005_FEEDBACK_LOOP.png"),
        ("Kreislauf wird sichtbar", "CLIP004_FEEDBACK_ENTITY.mp4"),
        ("Körperlicher Ausgangspunkt", "NEW:IMG045_EXPECTATION_ENTERS_BODY.png"),
        ("Messspur als Detail", "SRC:EP07_REM_Polysomnography_30sec.png:micro_arousal_detail"),
        ("Erwartung prägt Körper", "NEW:IMG046_RAW_MATERIAL_TO_FORM.png"),
        ("Studienzitat", "ORIG:ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER.png:citation_block"),
    ],
    "022": [
        ("Salem-Schleife", "IMG019_SALEM_LOOP_RETURN.png"),
        ("Comans Originalseite", "SRC:EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf:p1_full_return"),
        ("Bridget Bishop", "SRC:EP07_Bridget_Bishop_lithograph.jpg:portrait_return"),
        ("öffentliche Anklage", "SRC:EP07_Witchcraft_at_Salem_Village_1876.jpg:full_return_later_depiction"),
        ("Schatten werden Öffentlichkeit", "NEW:IMG057_PUBLIC_MEMORY_SHADOWS.png"),
        ("historische Konsequenz", "SRC:EP07_Bridget_Bishop_execution_archive_scan.png:full_scan"),
    ],
    "023": [
        ("Körper liefert Rohmaterial", "NEW:IMG054_BODY_RAW_MATERIAL.png"),
        ("Erzählung wirkt zurück", "NEW:IMG048_STORY_BODY_RETURN.png"),
        ("Erfahrung und Form verschränkt", "NEW:IMG038_BODY_CULTURE_BRAID.png"),
        ("Füsslis kulturelle Form", "SRC:EP07_Fuseli_The_Nightmare_1781.jpg:full_return"),
        ("Huffords Gegenmodell", "ORIG:ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED.png:cover_return"),
        ("Erwartungskreislauf", "NEW:IMG047_CULTURE_FEEDBACK_BRAID.png"),
    ],
    "024": [
        ("Salem als langsamer Übertragungsraum", "SRC:EP07_Salem_Village_1692_map_Upham_1866.jpg:full_return"),
        ("Predigten und Bücher", "SRC:EP07_Malleus_1494_Bull_Innocent_VIII_Wellcome.jpg:title_detail"),
        ("anderes Nachtmahrbild", "SRC:EP07_Abildgaard_Nightmare_1800.jpg:full_return"),
        ("Neufundland als nächste Station", "ORIG:ORIG_NEWFOUNDLAND_MAP_PD.png:full_return"),
        ("Generationen der Überlieferung", "NEW:IMG039_GENERATIONS_OF_NIGHT_STORIES.png"),
        ("Tempo kippt", "NEW:IMG040_PRINT_TO_RADIO_NETWORK.png"),
    ],
    "025": [
        ("frühe Mediengeschwindigkeit", "IMG020_MEDIA_SPEED_HANDOFF.png"),
        ("Füssli neben frühem Bildschirm", "NEW:IMG059_FUSELI_TO_SCREEN_STATIC.png"),
        ("Art-Bell-Sendung als Originalanker", "ORIG:ORIG_ART_BELL_2001_BROADCAST_SOURCE.png:source_frame"),
        ("Radio ohne Moderatorenimitat", "NEW:IMG041_2001_RADIO_STUDIO_HANDOFF.png"),
        ("frühes Internet", "NEW:IMG042_EARLY_WEB_SHADOW_NETWORK.png"),
        ("Netzwerk beschleunigt", "NEW:IMG058_RADIO_NETWORK_TRANSFORMATION_END_FRAME.png"),
    ],
    "026": [("Erlebnis oder Erzählung", "CARD007_ENDCARD.png")],
}


STATIC_EXISTING = {
    "IMG003_PRIVATE_NIGHT_TO_COURT.png",
    "IMG005_NIGHTMARE_MOTIF_ROOM_BASE.png",
    "IMG008_BURNEY_RELIEF_SOURCE_ROOM.png",
    "IMG019_SALEM_LOOP_RETURN.png",
    "SHOT04_FUSELI_TO_SCREEN_TRANSITION.png",
}
RECON_EXISTING = {
    "IMG001_SALEM_BEDROOM_COMAN_RECON.png",
    "IMG002_COMAN_TRIES_TO_WAKE_WIFE.png",
    "IMG004_BRIDGET_BISHOP_COURT_CONTEXT_RECON.png",
    "IMG009_MEDIEVAL_BEDROOM_EXPLANATION.png",
    "IMG011_HUFFORD_FIELD_NOTES_RECON.png",
    "IMG016_EGYPT_DENMARK_MATCHED_BEDROOMS.png",
}


def fmt(seconds: float) -> str:
    minutes = int(seconds // 60)
    rest = seconds - minutes * 60
    return f"{minutes:02d}:{rest:05.2f}"


def slug(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Z0-9]+", "_", normalized.upper()).strip("_")


def build_take_package() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^### TAKE (\d{3}) - (.+)$", source, flags=re.MULTILINE))
    if len(matches) != 26:
        raise SystemExit(f"Expected 26 takes in speaker script, got {len(matches)}")

    take_windows = {take_id: (section, start, end) for take_id, section, start, end, _, _ in TAKES}
    source_dir = VOICE_DIR / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for index, match in enumerate(matches):
        take_id, title = match.group(1), match.group(2).strip()
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        body = source[body_start:body_end].strip()
        filename = f"EP07_TAKE_{take_id}_{slug(title)}.txt"
        path = source_dir / filename
        path.write_text(body + "\n", encoding="utf-8")
        section, start, end = take_windows[take_id]
        words = len(re.findall(r"\b[\wÄÖÜäöüß'-]+\b", body, flags=re.UNICODE))
        manifest.append(
            {
                "take_id": f"EP07_TAKE_{take_id}",
                "section": section,
                "title": title,
                "plan_start": fmt(start),
                "plan_end": fmt(end),
                "word_count": words,
                "character_count": len(body),
                "source_file": str(path),
                "voice_status": "TEXT_READY_NOT_GENERATED",
            }
        )

    with (VOICE_DIR / "EP07_TAKE_MANIFEST.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)


def resolve(token: str):
    if token.startswith("SRC:"):
        _, filename, variant = token.split(":", 2)
        asset_id = f"SRC_{Path(filename).stem}_{variant}"
        return (
            asset_id,
            "ORIGINAL_SOURCE",
            str(EP / "04_EDITOR_DERIVATIVES" / f"{asset_id}.png"),
            "DERIVE_STATIC_FRAME",
            "STATIC_CONTAIN_OR_SEMANTIC_CROP",
            "Quelle und Jahr unten links; keine Bewegung",
            str(ASSETS / filename),
        )
    if token.startswith("ORIG:"):
        _, filename, variant = token.split(":", 2)
        asset_id = f"ORIG_{Path(filename).stem}_{variant}"
        return (
            asset_id,
            "ORIGINAL_SOURCE",
            str(EP / "04_EDITOR_DERIVATIVES" / f"{asset_id}.png"),
            "MISSING_ACQUISITION",
            "STATIC_CONTAIN_OR_SEMANTIC_CROP",
            "Nur nach Rechteprüfung; Quelle und Jahr unten links",
            str(ASSETS / filename),
        )
    if token.startswith("NEW:"):
        filename = token.split(":", 1)[1]
        return (
            Path(filename).stem,
            "GENERATED_STILL",
            str(OUT / filename),
            "MISSING_GENERATION",
            "HOLD_OR_GENTLE_1P5_TO_2P5_PERCENT",
            "Bei historischer Szene: Rekonstruktion; sonst kein Overlay",
            "",
        )
    if token.startswith("CARD"):
        return (
            Path(token).stem,
            "CARD",
            str(CARDS / token),
            "READY",
            "LOCKED_STATIC_NO_ZOOM_NO_PAN_NO_DRIFT",
            "Keine zusätzliche Typografie",
            "",
        )
    if token.startswith("CLIP"):
        label = "Subjektive Visualisierung" if token in {"CLIP002_NIGHTMARE_PRESSURE.mp4", "CLIP004_FEEDBACK_ENTITY.mp4"} else "Kulturelle Visualisierung"
        return (
            Path(token).stem,
            "TRANSFORM_CLIP",
            str(OUT / token),
            "READY",
            "NATIVE_MOTION_NO_ADDITIONAL_CAMERA",
            label,
            "",
        )
    status = "READY" if (OUT / token).exists() else "MISSING"
    if token in STATIC_EXISTING:
        motion = "LOCKED_STATIC_SOURCE_COMPOSITE"
    else:
        motion = "HOLD_OR_GENTLE_1P5_TO_2P5_PERCENT"
    overlay = "Rekonstruktion" if token in RECON_EXISTING else "Kein Zusatztext"
    return Path(token).stem, "GENERATED_STILL", str(OUT / token), status, motion, overlay, ""


def main() -> None:
    rows = []
    cue_number = 1
    movable_still_index = 0
    for take_id, section, start, end, take_anchor, sfx in TAKES:
        cues = CUES[take_id]
        duration = end - start
        card_slots = [i for i, (_, token) in enumerate(cues) if token.startswith("CARD")]
        if take_id == "026":
            durations = [duration]
        elif card_slots:
            fixed = 5.5
            normal = (duration - fixed * len(card_slots)) / (len(cues) - len(card_slots))
            durations = [fixed if i in card_slots else normal for i in range(len(cues))]
        else:
            durations = [duration / len(cues)] * len(cues)

        cursor = float(start)
        for (voice_anchor, token), cue_duration in zip(cues, durations):
            asset_id, kind, path, status, motion, overlay, source_master = resolve(token)
            if kind == "GENERATED_STILL" and motion == "HOLD_OR_GENTLE_1P5_TO_2P5_PERCENT":
                movable_still_index += 1
                motion = (
                    "GENTLE_ZOOM_1P5_TO_2P5_PERCENT"
                    if movable_still_index % 2 == 0
                    else "HOLD_STATIC_0_TO_1_PERCENT"
                )
            cue_start = cursor
            cue_end = min(float(end), cursor + cue_duration)
            rows.append(
                {
                    "cue_id": f"V{cue_number:03d}",
                    "take_id": f"EP07_TAKE_{take_id}",
                    "section": section,
                    "plan_start": fmt(cue_start),
                    "plan_end": fmt(cue_end),
                    "timing_method": "PLAN_ESTIMATE_REPLACE_WITH_FORCED_ALIGNMENT",
                    "take_anchor": take_anchor,
                    "voice_anchor": voice_anchor,
                    "asset_id": asset_id,
                    "asset_type": kind,
                    "asset_path": path,
                    "source_master": source_master,
                    "asset_status": status,
                    "movement_rule": motion,
                    "overlay_rule": overlay,
                    "sfx_key": sfx,
                    "edit_note": "Hard cut within act; 0.35 s dissolve only at act boundary",
                }
            )
            cue_number += 1
            cursor = cue_end

    DEST.parent.mkdir(parents=True, exist_ok=True)
    with DEST.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    if len(rows) != 146:
        raise SystemExit(f"Expected 146 sync rows, got {len(rows)}")
    build_take_package()
    print(f"Wrote {DEST} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
