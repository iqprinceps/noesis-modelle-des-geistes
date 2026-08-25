from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "EP06_SPRECHERFASSUNG_FINAL.md"
SOURCE = ROOT / "source"
SYNC = ROOT / "sync"

TAKE_META = {
    "001": ("S1", "DEZEMBER_1963", "unmittelbar, sehr ruhig"),
    "002": ("S1", "DER_KOERPER_ANTWORTET_NICHT", "nah, ohne Horrorspiel"),
    "003": ("S1", "EIN_MUSTER_DAS_ER_NICHT_KANNTE", "neugierig, Gedanke öffnet sich"),
    "004": ("S2", "FOGO_ISLAND", "sachlich, ortsnah"),
    "005": ("S2", "UNANGENEHM_PRAEZISE", "persönlich, präzise"),
    "006": ("S2", "WAS_KOMMT_ZUERST", "fragend, zügiger Schluss"),
    "007": ("S3", "REM_ATONIE", "anschaulich, unangestrengt"),
    "008": ("S3", "DER_TIMINGFEHLER", "klar, körperlich"),
    "009": ("S3", "DER_KOERPER_FUEHLT_SICH_FREMD_AN", "empathisch, keine Panik"),
    "010": ("S3", "WO_DAS_RAETSEL_BEGINNT", "leise Spannung"),
    "011": ("S4", "DREI_WIEDERKEHRENDE_FAMILIEN", "forschend"),
    "012": ("S4", "INTRUDER_INCUBUS_SCHWEBEN", "bildhaft, kontrolliert"),
    "013": ("S4", "WARUM_GERADE_DIESE_FORMEN", "offen, hin zum Experiment"),
    "014": ("S5", "TAKEUCHI_1992", "nüchtern, konkret"),
    "015": ("S5", "DER_UNTERBROCHENE_SCHLAF", "verständlich, keine Methodenlehre"),
    "016": ("S5", "SECHS_EPISODEN", "Ergebnis deutlich landen lassen"),
    "017": ("S5", "UND_TROTZDEM_KOMMT_ETWAS_MIT", "erst sachlich, dann befremdet"),
    "018": ("S6", "HEUTE_NACHT", "direkte, intime Ansprache"),
    "019": ("S6", "KOERPER_ODER_BESUCHER", "klarer CTA, keine Ironie"),
    "020": ("S6", "DIE_OFFENE_AUFGABE", "ruhig, gedanklich"),
    "021": ("S7", "ALARM_OHNE_URSACHE", "nachvollziehbar, zügig"),
    "022": ("S7", "AUS_EINEM_SCHATTEN_WIRD_EINE_SCHULTER", "bildhaft, nicht dogmatisch"),
    "023": ("S7", "DIE_PRAESENZ_KOMMT_ZUERST", "langsamer, Mystery-Peak"),
    "024": ("S8", "ZURUECK_ZU_HUFFORD", "geerdet"),
    "025": ("S8", "WARUM_WIRD_AUS_LAEHMUNG_EINE_BEGEGNUNG", "offen, keine Auflösung spielen"),
    "026": ("S8", "BRIDGET_BISHOP", "dokumentarisch, letzter Satz trocken"),
}

OUT = "IMAGE_GENERATION_KIT/03_GENERATED_OUTPUT/NanoBanana_2K_Series"
CARDS = "IMAGE_GENERATION_KIT/03_GENERATED_OUTPUT/CARDS"
ORIG = "IMAGE_GENERATION_KIT/02_ASSETS"


def current(name: str) -> tuple[str, str, str]:
    return name.split("_", 1)[0], "GENERATED_STILL", f"{OUT}/{name}"


def clip(name: str) -> tuple[str, str, str]:
    return name.split("_", 1)[0], "VEO_CLIP", f"{OUT}/{name}"


def card(name: str) -> tuple[str, str, str]:
    return name.split("_", 1)[0], "CARD", f"{CARDS}/{name}"


def original(asset_id: str, name: str) -> tuple[str, str, str]:
    return asset_id, "ORIGINAL_ASSET", f"{ORIG}/{name}"


def planned(asset_id: str, cls: str) -> tuple[str, str, str]:
    return asset_id, cls, f"PLANNED/{asset_id}"


def cue(asset, anchor, motion, sfx="NONE", note=""):
    return (*asset, anchor, motion, sfx, note)


IMG = {name.split("_", 1)[0]: current(name) for name in [
    "IMG001_1963_BEDROOM_DOOR.png", "IMG002_FOOTSTEPS_APPROACH.png",
    "IMG003_HAND_WILL_NOT_MOVE.png", "IMG004_MATTRESS_WEIGHT.png",
    "IMG005_CHEST_PRESSURE_CLOSE.png", "IMG006_MALEVOLENT_PRESENCE_NEGATIVE_SPACE.png",
    "IMG007_FOGO_PLACE_ANCHOR_RECON.png", "IMG008_OLD_HAG_BEDROOM_PATTERN.png",
    "IMG009_REM_BODY_STILL.png", "IMG010_REM_RECORD_EDIT_BASE.png",
    "IMG011_WAKE_BODY_LAG.png", "IMG012_ARM_COMMAND_NO_RESPONSE.png",
    "IMG013_INTRUDER_DOORWAY.png", "IMG014_INCUBUS_PRESSURE.png",
    "IMG015_VESTIBULAR_FLOAT.png", "IMG016_THREE_FAMILIES_TRIPTYCH_BASE.png",
    "IMG017_SLEEP_LAB_WIDE_RECON.png", "IMG018_SLEEP_INTERRUPTION_CLOCK.png",
    "IMG019_RETURN_TO_BED_RECON.png", "IMG020_EEG_AWAKE_BODY_STILL_BASE.png",
    "IMG021_LAB_HALLUCINATION_AMBIGUOUS.png", "IMG022_VIEWER_BEDROOM_TWO_STEPS.png",
    "IMG023_BODY_OR_VISITOR_SPLIT_BASE.png", "IMG024_EYE_CORNER_FORM.png",
    "IMG025_ALARM_WITHOUT_CAUSE.png", "IMG026_SOUND_BECOMES_STEP.png",
    "IMG027_SHADOW_BECOMES_SHOULDER.png", "IMG028_PRESENCE_BEFORE_FORM.png",
    "IMG029_OBSERVING_INTELLIGENCE_AMBIGUOUS.png", "IMG030_HUFFORD_RETURN_WITHOUT_PORTRAIT.png",
    "IMG031_NAMES_OVER_SAME_ROOM_BASE.png", "IMG032_BEDROOM_TO_COURT_HANDOFF.png",
    "SHOT01_EMPTY_HALLWAY.png", "SHOT02_FOGO_MAP_TABLE.png",
    "SHOT03_REM_VS_SLOW_WAVE_SOURCE_TABLE.png", "SHOT04_EMPTY_BEDROOM_SHADOWS.png",
    "SHOT05_LAB_SENSOR_MACRO.png", "SHOT06_CTA_EMPTY_ROOM.png",
    "SHOT07_EMPTY_CORNER_AFTER_PRESENCE.png", "SHOT08_DAWN_AFTER_PARALYSIS.png",
]}

CLIP = {name.split("_", 1)[0]: clip(name) for name in [
    "CLIP001_SOUL_BODY_OFFSET.mp4", "CLIP002_REM_SIGNAL_GATE.mp4",
    "CLIP003_OLD_HAG_THRESHOLD.mp4", "CLIP004_PRESENCE_GEOMETRY.mp4",
]}

CARD = {name.split("_", 1)[0]: card(name) for name in [
    "CARD001_REM_ATONIE.png", "CARD002_DREI_ERLEBNISFAMILIEN.png",
    "CARD003_TAKEUCHI_1992.png", "CARD004_PRAESENZMODELL.png",
    "CARD005_FOGO_FELDFORSCHUNG.png", "CARD006_CTA_KOERPER_BESUCHER.png",
    "CARD007_ENDCARD.png",
]}

O = {
    "O01": original("ORIG_FOGO_VILLAGE", "EP06_Fogo_Island_Newfoundland_fishing_village_2002.jpg"),
    "O02": original("ORIG_FOGO_CHART_1873", "EP06_Fogo_Island_to_Cape_Bonavista_Admiralty_Chart_1873.jpg"),
    "O03": original("ORIG_REM_PSG", "EP06_REM_Polysomnography_30sec.png"),
    "O04": original("ORIG_NHLBI_SLEEP_STUDIES", "EP06_Sleep_Studies_NHLBI_Polysomnography.jpg"),
    "O05": original("ORIG_SLOW_WAVE_PSG", "EP06_Slow_Wave_Sleep_PSG.jpg"),
    "O06": original("ORIG_STAGE1_PSG", "EP06_Sleep_EEG_Stage_1_PSG.jpg"),
    "O07": original("ORIG_STAGE2_PSG", "EP06_Sleep_EEG_Stage_2_PSG.jpg"),
    "O08": original("ORIG_SLEEP_PHASES", "EP06_Simplified_Sleep_Phases.jpg"),
    "O09": original("ORIG_PSG_TRACE", "EP06_Polysomnography_trace.png"),
    "O10": original("ORIG_SENSOR_CONNECTIONS", "EP06_Polysomnography_sensor_connections.jpg"),
    "O11": original("ORIG_PSG_TESTER", "EP06_Polysomnography_tester.jpg"),
    "O12": original("ORIG_PSG_MODEL_SIDE", "EP06_Polysomnography_model_side.jpg"),
    "O13": original("ORIG_PSG_EQUIPPED_PATIENT", "EP06_Polysomnography_equipped_patient.jpg"),
    "O14": original("ORIG_64_CHANNEL_CAP", "EP06_64_Channel_EEG_Cap.jpg"),
    "O15": original("ORIG_EEG_ICON", "EP06_EEG_Cap_Icon.svg"),
    "O16": original("ORIG_FOGO_DISTRICT_MAP", "EP06_Fogo_Island_Cape_Freels_map.svg"),
}

N = {
    "NEW_IMG033_HUFFORD_1963_STUDENT_RECON": ("IMG033", "PLANNED_GENERATED_STILL", "PLANNED/IMG033_HUFFORD_1963_STUDENT_RECON.png"),
    "NEW_IMG034_DOOR_HANDLE_NO_RESPONSE": ("IMG034", "PLANNED_GENERATED_STILL", "PLANNED/IMG034_DOOR_HANDLE_NO_RESPONSE.png"),
    "NEW_IMG035_VOICE_WITHOUT_SOUND": ("IMG035", "PLANNED_GENERATED_STILL", "PLANNED/IMG035_VOICE_WITHOUT_SOUND.png"),
    "NEW_IMG036_HUFFORD_FIELD_NOTES": ("IMG036", "PLANNED_GENERATED_STILL", "PLANNED/IMG036_HUFFORD_FIELD_NOTES.png"),
    "NEW_IMG037_CULTURE_EXPERIENCE_FORK": ("IMG037", "PLANNED_GENERATED_STILL", "PLANNED/IMG037_CULTURE_EXPERIENCE_FORK.png"),
    "NEW_IMG038_BREATH_INTEROCEPTION": ("IMG038", "PLANNED_GENERATED_STILL", "PLANNED/IMG038_BREATH_INTEROCEPTION.png"),
    "NEW_IMG039_CLUSTER_OBJECT_STUDY": ("IMG039", "PLANNED_GENERATED_STILL", "PLANNED/IMG039_CLUSTER_OBJECT_STUDY.png"),
    "NEW_IMG040_INTERRUPTION_PROTOCOL_OBJECTS": ("IMG040", "PLANNED_GENERATED_STILL", "PLANNED/IMG040_INTERRUPTION_PROTOCOL_OBJECTS.png"),
    "NEW_IMG041_SIX_EPISODES_MARKERS": ("IMG041", "PLANNED_GENERATED_STILL", "PLANNED/IMG041_SIX_EPISODES_MARKERS.png"),
    "NEW_IMG042_AGENT_DETECTION_LAYERS": ("IMG042", "PLANNED_GENERATED_STILL", "PLANNED/IMG042_AGENT_DETECTION_LAYERS.png"),
    "NEW_IMG043_PRESENCE_BEFORE_IMAGE": ("IMG043", "PLANNED_GENERATED_STILL", "PLANNED/IMG043_PRESENCE_BEFORE_IMAGE.png"),
    "NEW_IMG044_BRIDGET_TESTIMONY_HANDOFF": ("IMG044", "PLANNED_GENERATED_STILL", "PLANNED/IMG044_BRIDGET_TESTIMONY_HANDOFF.png"),
    "NEW_IMG045_DECEMBER_WINDOW_CONTEXT": ("IMG045", "PLANNED_GENERATED_STILL", "PLANNED/IMG045_DECEMBER_WINDOW_CONTEXT.png"),
    "NEW_CARD008_HUFFORD_1963_1982": ("CARD008", "PLANNED_CARD", "PLANNED/CARD008_HUFFORD_1963_1982.png"),
    "NEW_CARD009_WAKE_REM_OVERLAP": ("CARD009", "PLANNED_CARD", "PLANNED/CARD009_WAKE_REM_OVERLAP.png"),
    "NEW_CARD010_TAKEUCHI_PROTOCOL": ("CARD010", "PLANNED_CARD", "PLANNED/CARD010_TAKEUCHI_PROTOCOL.png"),
    "NEW_CARD011_SIX_EPISODES": ("CARD011", "PLANNED_CARD", "PLANNED/CARD011_SIX_EPISODES.png"),
    "NEW_CARD012_REALNESS_AND_CAUSE": ("CARD012", "PLANNED_CARD", "PLANNED/CARD012_REALNESS_AND_CAUSE.png"),
    "NEW_CARD013_OPEN_PRESENCE_QUESTION": ("CARD013", "PLANNED_CARD", "PLANNED/CARD013_OPEN_PRESENCE_QUESTION.png"),
    "NEW_CARD014_PRIVATE_NIGHT_PUBLIC_RECORD": ("CARD014", "PLANNED_CARD", "PLANNED/CARD014_PRIVATE_NIGHT_PUBLIC_RECORD.png"),
    "NEW_CLIP005_MOTOR_FREEZE": ("CLIP005", "PLANNED_TRANSFORM_CLIP", "PLANNED/CLIP005_MOTOR_FREEZE.mp4"),
    "NEW_CLIP006_THREE_FAMILIES": ("CLIP006", "PLANNED_TRANSFORM_CLIP", "PLANNED/CLIP006_THREE_FAMILIES.mp4"),
    "NEW_CLIP007_INTERRUPTION_CYCLE": ("CLIP007", "PLANNED_TRANSFORM_CLIP", "PLANNED/CLIP007_INTERRUPTION_CYCLE.mp4"),
    "NEW_CLIP008_SIX_EPISODES_SIGNAL": ("CLIP008", "PLANNED_TRANSFORM_CLIP", "PLANNED/CLIP008_SIX_EPISODES_SIGNAL.mp4"),
    "NEW_CLIP009_REALNESS_CAUSE_SPLIT": ("CLIP009", "PLANNED_TRANSFORM_CLIP", "PLANNED/CLIP009_REALNESS_CAUSE_SPLIT.mp4"),
    "NEW_CLIP010_SHADOW_COMPLETION": ("CLIP010", "PLANNED_TRANSFORM_CLIP", "PLANNED/CLIP010_SHADOW_COMPLETION.mp4"),
    "NEW_ORIG01_BRAINSTEM_ANATOMY": ("ORIG017", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG017_BRAINSTEM_ANATOMY.png"),
    "NEW_ORIG02_SLEEP_CYCLE_HYPNOGRAM": ("ORIG018", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG018_SLEEP_CYCLE_HYPNOGRAM.svg"),
    "NEW_ORIG03_CIRCADIAN_RHYTHM_NIH": ("ORIG019", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG019_CIRCADIAN_RHYTHM_NIH.jpg"),
    "NEW_ORIG04_EEG_62_CHANNEL_CC0": ("ORIG020", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG020_EEG_62_CHANNEL_CC0.svg"),
    "NEW_ORIG05_AMYGDALA_ANIMATION": ("ORIG021", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG021_AMYGDALA_ANIMATION.gif"),
    "NEW_ORIG06_OBE_ICON": ("ORIG022", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG022_OBE_ICON.svg"),
    "NEW_ORIG07_SLEEP_DEPRIVATION": ("ORIG023", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG023_SLEEP_DEPRIVATION.svg"),
    "NEW_ORIG08_1960S_DORM_CONTEXT": ("ORIG024", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG024_1960S_DORM_CONTEXT.jpg"),
    "NEW_ORIG09_ORAL_HISTORY_RECORDER": ("ORIG025", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG025_ORAL_HISTORY_RECORDER.jpg"),
    "NEW_ORIG10_SALEM_COURT_1876": ("ORIG026", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG026_SALEM_COURT_1876.jpg"),
    "NEW_ORIG11_BRIDGET_BISHOP_RECORD": ("ORIG027", "PLANNED_ORIGINAL_ASSET", "PLANNED/ORIG027_BRIDGET_BISHOP_RECORD.jpg"),
}


M_STILL = "GENTLE_PUSH_MAX_1.025_EASED"
M_HOLD = "STATIC_HOLD"
M_SOURCE = "CONTAIN_STATIC_NO_CROP"
M_SOURCE_MOVE = "CONTAIN_STATIC_NO_CROP"
M_CARD = "STATIC_NO_ZOOM_NO_PAN"
M_CLIP = "NATIVE_MOTION_NO_RETIME_NO_EXTRA_CAMERA"

# Twenty non-card leitmotifs may return once with a new statement. Every other
# second use and every third use is replaced by a unique semantic companion.
# This keeps repeated non-card slots below the 15% series lock.
ALLOW_REPEAT_TWICE = {
    "IMG002", "IMG003", "IMG005", "IMG007", "IMG009", "IMG011",
    "IMG013", "IMG014", "IMG016", "IMG024", "IMG026", "IMG028",
    "IMG030", "IMG031", "IMG037", "IMG038", "IMG043",
    "ORIG_REM_PSG", "ORIG_FOGO_VILLAGE", "ORIG_SENSOR_CONNECTIONS",
}

V = {
"001": [
    cue(N["NEW_IMG033_HUFFORD_1963_STUDENT_RECON"], "Dezember 1963 / Hufford", M_STILL, "ROOMTONE_DORM"),
    cue(N["NEW_IMG045_DECEMBER_WINDOW_CONTEXT"], "Dezember / Winter / Nacht", M_HOLD, "WINTER_WINDOW_AIR"),
    cue(N["NEW_ORIG08_1960S_DORM_CONTEXT"], "College-Kontext", M_SOURCE, "ROOMTONE_DORM", "Jahr + Kontextlabel"),
    cue(IMG["IMG001"], "dunkles Zimmer / Tür", M_STILL, "DOOR_LATCH_SOFT"),
    cue(IMG["SHOT01"], "Tür geht auf", M_HOLD, "ROOMTONE_DARK"),
    cue(IMG["IMG002"], "Schritte", M_STILL, "FOOTSTEPS_DISTANT_2"),
    cue(N["NEW_IMG034_DOOR_HANDLE_NO_RESPONSE"], "direkt auf ihn zu", M_STILL, "FOOTSTEP_SINGLE_NEAR"),
],
"002": [
    cue(IMG["IMG003"], "Arm bewegt sich nicht", M_HOLD, "FABRIC_HAND_MICRO"),
    cue(N["NEW_CLIP005_MOTOR_FREEZE"], "motorischer Befehl blockiert", M_CLIP, "EEG_TICK_SUBTLE", "wissenschaftliche Metapher"),
    cue(IMG["IMG004"], "Matratze gibt nach", M_STILL, "MATTRESS_WEIGHT_SOFT"),
    cue(IMG["IMG005"], "Gewicht auf der Brust", M_HOLD, "BREATH_BODY_LOW"),
    cue(N["NEW_IMG035_VOICE_WITHOUT_SOUND"], "kein Ton", M_STILL, "ROOMTONE_DROP"),
    cue(IMG["IMG006"], "Da ist etwas", M_HOLD, "LOW_AIR_TEXTURE"),
],
"003": [
    cue(IMG["IMG030"], "spätere Arbeit", M_STILL, "PENCIL_NOTE"),
    cue(N["NEW_IMG036_HUFFORD_FIELD_NOTES"], "keine Vorbekanntschaft", M_HOLD, "PAPER_NOTE"),
    cue(IMG["IMG007"], "Jahre später / Neufundland", M_STILL, "COAST_WIND_LOW"),
    cue(O["O01"], "Ort wird konkret", M_SOURCE_MOVE, "COAST_WIND_LOW", "Original · PD"),
    cue(IMG["SHOT02"], "Muster auf der Karte", M_SOURCE, "NONE"),
    cue(IMG["IMG031"], "offene Frage / Erzählmuster", M_STILL, "MUSIC_PULSE_SOFT"),
],
"004": [
    cue(O["O01"], "Neufundland / Fogo", M_SOURCE_MOVE, "COAST_WIND_LOW", "Original · PD"),
    cue(IMG["IMG007"], "Fogo Island", M_STILL, "HARBOR_WIND_LOW"),
    cue(O["O02"], "Inselkontext", M_SOURCE, "NONE", "Originalkarte 1873 · PD"),
    cue(IMG["SHOT02"], "lokale Verortung", M_SOURCE, "NONE"),
    cue(O["O16"], "Fogo Island–Cape Freels", M_SOURCE, "NONE", "YELLOW · Attribution/SA prüfen"),
    cue(IMG["SHOT04"], "to have the Old Hag", M_HOLD, "TAPE_RECORDER_ROOM"),
],
"005": [
    cue(IMG["IMG008"], "vertrautes Zimmer", M_STILL, "ROOMTONE_COAST_HOUSE"),
    cue(N["NEW_ORIG09_ORAL_HISTORY_RECORDER"], "Erzählungen gesammelt", M_SOURCE_MOVE, "TAPE_CLICK_SINGLE"),
    cue(IMG["IMG030"], "Hufford sammelt Berichte", M_STILL, "PENCIL_NOTE"),
    cue(CARD["CARD005"], "experience-centered approach", M_CARD, "NONE"),
    cue(N["NEW_IMG036_HUFFORD_FIELD_NOTES"], "1963 → 1982", M_HOLD, "PAPER_TURN_SOFT"),
    cue(IMG["IMG031"], "Buch / Überlieferung", M_HOLD, "TAPE_HISS_LOW"),
],
"006": [
    cue(N["NEW_IMG037_CULTURE_EXPERIENCE_FORK"], "Was kommt zuerst?", M_STILL, "MUSIC_HARMONIC_OPEN"),
    cue(IMG["IMG009"], "Übergang zum Körper", M_STILL, "LOW_BODY_TONE"),
    cue(N["NEW_ORIG01_BRAINSTEM_ANATOMY"], "REM-Atonie ankündigen", M_SOURCE, "NONE"),
    cue(N["NEW_ORIG03_CIRCADIAN_RHYTHM_NIH"], "Schlaf als Rhythmus", M_SOURCE, "NONE", "Original · NIH/PD"),
    cue(N["NEW_ORIG02_SLEEP_CYCLE_HYPNOGRAM"], "REM-Phase", M_SOURCE, "EEG_TICK_SUBTLE"),
    cue(N["NEW_ORIG07_SLEEP_DEPRIVATION"], "Schlafarchitektur", M_SOURCE, "NONE"),
],
"007": [
    cue(O["O03"], "REM-Schlaf", M_SOURCE, "EEG_TICK_SUBTLE", "Original · PD"),
    cue(IMG["IMG010"], "REM-Aufzeichnung", M_SOURCE, "EEG_TICK_SUBTLE"),
    cue(O["O05"], "Kontrast Tiefschlaf", M_SOURCE, "NONE", "Original · PD"),
    cue(O["O08"], "Schlafphasen", M_SOURCE, "NONE", "YELLOW · Attribution/SA prüfen"),
    cue(IMG["SHOT03"], "REM versus Slow Wave", M_SOURCE, "NONE"),
    cue(N["NEW_ORIG01_BRAINSTEM_ANATOMY"], "Hirnstamm / Hemmung", M_SOURCE, "LOW_NEURAL_TICK"),
    cue(CARD["CARD001"], "REM-Atonie", M_CARD, "NONE"),
],
"008": [
    cue(IMG["IMG011"], "Timing gerät auseinander", M_HOLD, "MUSIC_LAYER_SPLIT"),
    cue(CLIP["CLIP001"], "Wachheit / Körper versetzt", M_CLIP, "SOFT_PHASE_SHIFT", "subjektive Timing-Visualisierung"),
    cue(IMG["IMG003"], "Befehl im Arm", M_STILL, "NONE"),
    cue(CLIP["CLIP002"], "Signal trifft auf Hemmung", M_CLIP, "EEG_TICK_SUBTLE", "wissenschaftliche Metapher"),
    cue(IMG["IMG012"], "Arm reagiert nicht", M_HOLD, "FABRIC_HAND_MICRO"),
    cue(N["NEW_CARD009_WAKE_REM_OVERLAP"], "Wach + REM-Atonie", M_CARD, "NONE"),
],
"009": [
    cue(IMG["IMG005"], "Brustkorb", M_HOLD, "BREATH_BODY_LOW"),
    cue(N["NEW_IMG038_BREATH_INTEROCEPTION"], "Atmung fühlt sich fremd an", M_STILL, "BREATH_BODY_LOW"),
    cue(IMG["IMG014"], "Druck / Incubus-Symptom", M_HOLD, "FABRIC_PRESSURE_SOFT"),
    cue(O["O04"], "medizinischer Rahmen", M_SOURCE, "LAB_ROOMTONE_LOW", "Original · NHLBI/PD"),
    cue(O["O10"], "Sensorik", M_SOURCE_MOVE, "CABLE_TOUCH_SOFT", "YELLOW · Attribution/SA prüfen"),
    cue(IMG["IMG023"], "Körper versus Deutung", M_HOLD, "MUSIC_QUESTION_LOW"),
],
"010": [
    cue(IMG["IMG013"], "Schritte im Flur", M_STILL, "FOOTSTEP_SINGLE_FAR"),
    cue(IMG["IMG006"], "Anwesenheit", M_HOLD, "LOW_AIR_TEXTURE"),
    cue(IMG["IMG024"], "Form im Augenwinkel", M_HOLD, "CURTAIN_RUSTLE_SOFT"),
    cue(IMG["IMG028"], "Präsenz vor Form", M_HOLD, "ROOMTONE_WIDE"),
    cue(CLIP["CLIP004"], "Geometrie wird Gestalt", M_CLIP, "FABRIC_AIR_SOFT", "Wahrnehmungsvervollständigung"),
    cue(N["NEW_IMG042_AGENT_DETECTION_LAYERS"], "Frage nach Präsenz", M_HOLD, "NONE"),
],
"011": [
    cue(N["NEW_ORIG04_EEG_62_CHANNEL_CC0"], "Forschung / Daten", M_SOURCE, "EEG_TICK_SUBTLE"),
    cue(N["NEW_IMG039_CLUSTER_OBJECT_STUDY"], "Berichte ordnen sich", M_STILL, "PAPER_SORT_SOFT"),
    cue(IMG["IMG016"], "drei Familien", M_HOLD, "MUSIC_THREE_NOTES"),
    cue(CARD["CARD002"], "Cheyne-Taxonomie", M_CARD, "NONE"),
    cue(O["O15"], "Mess-/Forschungsebene", M_SOURCE, "NONE", "Original · CC0"),
    cue(N["NEW_ORIG05_AMYGDALA_ANIMATION"], "Gefahrensystem als Kontext", M_SOURCE, "LOW_BODY_TONE", "nur anatomischer Kontext"),
],
"012": [
    cue(IMG["IMG013"], "Intruder", M_STILL, "FOOTSTEP_SINGLE_FAR"),
    cue(IMG["IMG014"], "Incubus", M_HOLD, "BREATH_BODY_LOW"),
    cue(IMG["IMG015"], "vestibulär", M_STILL, "AIR_ROTATION_SOFT"),
    cue(N["NEW_ORIG06_OBE_ICON"], "Außerkörpererfahrung", M_SOURCE, "NONE"),
    cue(N["NEW_IMG038_BREATH_INTEROCEPTION"], "Atem und Druck", M_HOLD, "BREATH_BODY_LOW"),
    cue(N["NEW_ORIG07_SLEEP_DEPRIVATION"], "Schlafstörungskontext", M_SOURCE, "NONE"),
    cue(N["NEW_CLIP006_THREE_FAMILIES"], "drei Erlebnisfamilien verändern die Wahrnehmung", M_CLIP, "MUSIC_THREE_NOTES", "drei echte Zustandswechsel, keine Kamerafahrt"),
],
"013": [
    cue(IMG["IMG025"], "Wiederholung / Alarm", M_STILL, "MUSIC_PULSE_SOFT"),
    cue(IMG["IMG027"], "Gefahr konstruiert", M_HOLD, "NONE"),
    cue(IMG["IMG029"], "beobachtende Agency", M_HOLD, "ROOMTONE_WIDE"),
    cue(N["NEW_IMG042_AGENT_DETECTION_LAYERS"], "Gefahr und Verursacher", M_STILL, "LOW_NEURAL_TICK"),
    cue(N["NEW_ORIG03_CIRCADIAN_RHYTHM_NIH"], "neurophysiologischer Mischzustand", M_SOURCE, "NONE"),
    cue(N["NEW_ORIG02_SLEEP_CYCLE_HYPNOGRAM"], "Übergang ins Labor", M_SOURCE, "MUSIC_TRANSITION_TICK"),
],
"014": [
    cue(O["O11"], "Schlaflabor", M_SOURCE_MOVE, "LAB_ROOMTONE_LOW", "YELLOW · Attribution/SA prüfen"),
    cue(O["O12"], "Versuchsperson", M_SOURCE_MOVE, "LAB_ROOMTONE_LOW", "YELLOW · Persönlichkeit/SA prüfen"),
    cue(IMG["IMG017"], "sechzehn gesunde Personen", M_STILL, "LAB_ROOMTONE_LOW", "Rekonstruktion; nicht Takeuchi-Original"),
    cue(IMG["IMG018"], "1992 / gezielter Versuch", M_STILL, "CLOCK_TICK_SOFT"),
    cue(CARD["CARD003"], "Takeuchi 1992", M_CARD, "NONE"),
    cue(N["NEW_CARD010_TAKEUCHI_PROTOCOL"], "Fragestellung", M_CARD, "NONE"),
],
"015": [
    cue(IMG["IMG019"], "zurück ins Bett", M_HOLD, "LAB_ROOMTONE_LOW"),
    cue(O["O13"], "Sensoren am Körper", M_SOURCE_MOVE, "CABLE_TOUCH_SOFT", "YELLOW · Lizenz/Person prüfen"),
    cue(O["O10"], "Sensoranschlüsse", M_SOURCE_MOVE, "CABLE_TOUCH_SOFT", "YELLOW · Attribution/SA prüfen"),
    cue(IMG["SHOT05"], "Muskeltonus", M_HOLD, "EEG_TICK_SUBTLE"),
    cue(N["NEW_IMG040_INTERRUPTION_PROTOCOL_OBJECTS"], "wecken / eine Stunde / zurück", M_STILL, "CLOCK_TICK_SOFT"),
    cue(O["O14"], "EEG-Kappe", M_SOURCE_MOVE, "NONE", "YELLOW · Attribution/SA prüfen"),
    cue(N["NEW_CLIP007_INTERRUPTION_CYCLE"], "Schlaf / wach / zurück", M_CLIP, "CLOCK_TICK_SOFT", "Ablaufwechsel statt Kamerafahrt"),
],
"016": [
    cue(N["NEW_CARD011_SIX_EPISODES"], "sechs Episoden", M_CARD, "MUSIC_RESULT_SOFT"),
    cue(N["NEW_IMG041_SIX_EPISODES_MARKERS"], "Ergebnis konkret", M_HOLD, "SIX_TICKS_SOFT"),
    cue(IMG["IMG020"], "wach im EEG / Körper still", M_STILL, "EEG_TICK_SUBTLE"),
    cue(O["O03"], "REM-Kurve", M_SOURCE, "NONE", "Original · PD"),
    cue(O["O06"], "Stage 1 Vergleich", M_SOURCE, "NONE", "Original · PD"),
    cue(O["O07"], "Stage 2 Vergleich", M_SOURCE, "NONE", "Original · PD"),
    cue(N["NEW_CLIP008_SIX_EPISODES_SIGNAL"], "sechs Episoden im Messverlauf", M_CLIP, "SIX_TICKS_SOFT", "sechs Marker entstehen nacheinander"),
],
"017": [
    cue(IMG["IMG021"], "Labor und Wahrnehmung", M_HOLD, "LAB_ROOMTONE_LOW"),
    cue(O["O04"], "messbarer Zustand", M_SOURCE, "NONE", "Original · NHLBI/PD"),
    cue(O["O09"], "Messkurve", M_SOURCE, "EEG_TICK_SUBTLE", "YELLOW · Attribution/SA prüfen; keine Takeuchi-Kurve behaupten"),
    cue(O["O15"], "Muskelhemmung / Messkontext", M_SOURCE, "EEG_TICK_SUBTLE", "Original · CC0"),
    cue(IMG["IMG023"], "Präsenz psychologisch offen", M_HOLD, "MUSIC_QUESTION_LOW"),
],
"018": [
    cue(IMG["IMG022"], "du wachst auf", M_HOLD, "BEDROOM_ROOMTONE"),
    cue(IMG["IMG002"], "zwei Schritte", M_STILL, "FOOTSTEPS_DISTANT_2"),
    cue(IMG["IMG026"], "Geräusch neben dem Bett", M_HOLD, "FLOOR_CREAK_SINGLE"),
    cue(IMG["IMG024"], "dunkle Form im Augenwinkel", M_HOLD, "CURTAIN_RUSTLE_SOFT"),
    cue(IMG["SHOT06"], "Fehler oder Besucher", M_HOLD, "ROOMTONE_DROP"),
],
"019": [
    cue(CARD["CARD006"], "KÖRPER / BESUCHER", M_CARD, "NONE", "mindestens 4,5 s statisch"),
    cue(O["O03"], "körperlicher Rahmen", M_SOURCE, "LOW_BODY_TONE", "Original · PD"),
    cue(IMG["SHOT07"], "Erlebnis bleibt real", M_HOLD, "MUSIC_HARMONIC_OPEN"),
    cue(O["O06"], "subjektive Wirklichkeit / messbarer Rahmen", M_SOURCE, "LOW_AIR_TEXTURE", "Original · PD"),
    cue(N["NEW_IMG037_CULTURE_EXPERIENCE_FORK"], "Übergang Mechanik/Erlebnis", M_STILL, "MUSIC_TRANSITION_TICK"),
],
"020": [
    cue(N["NEW_CARD012_REALNESS_AND_CAUSE"], "offene Aufgabe", M_CARD, "NONE"),
    cue(IMG["IMG025"], "Wehrlosigkeit / Alarm", M_STILL, "MUSIC_PULSE_SOFT"),
    cue(IMG["IMG029"], "absichtsvoll erlebt", M_HOLD, "ROOMTONE_WIDE"),
    cue(N["NEW_CLIP009_REALNESS_CAUSE_SPLIT"], "Form entsteht", M_CLIP, "FABRIC_AIR_SOFT", "Erlebnis und Erklärung trennen sich sichtbar"),
    cue(N["NEW_IMG043_PRESENCE_BEFORE_IMAGE"], "Verursacher vor Bild", M_HOLD, "LOW_AIR_TEXTURE"),
],
"021": [
    cue(N["NEW_ORIG05_AMYGDALA_ANIMATION"], "Alarmsystem", M_SOURCE, "LOW_BODY_TONE", "Anatomiekontext, keine monokausale Behauptung"),
    cue(N["NEW_IMG042_AGENT_DETECTION_LAYERS"], "Ursache fehlt", M_STILL, "LOW_NEURAL_TICK"),
    cue(IMG["IMG023"], "Körper meldet Widerspruch", M_HOLD, "BREATH_BODY_LOW"),
    cue(CARD["CARD004"], "Alarm → Verursacher", M_CARD, "NONE"),
    cue(IMG["IMG025"], "Bedrohung früh erkennen", M_STILL, "MUSIC_PULSE_SOFT"),
],
"022": [
    cue(IMG["IMG026"], "Knacken wird Schritt", M_HOLD, "FLOOR_CREAK_SINGLE"),
    cue(IMG["IMG027"], "Schatten wird Schulter", M_HOLD, "ROOMTONE_WIDE"),
    cue(N["NEW_CLIP010_SHADOW_COMPLETION"], "Gestalt vervollständigt sich", M_CLIP, "FABRIC_AIR_SOFT", "Wahrnehmungsmetapher"),
    cue(O["O07"], "Alltagsobjekt / körperlicher Rahmen", M_SOURCE, "CURTAIN_RUSTLE_SOFT", "Original · PD"),
    cue(IMG["IMG028"], "Unsicherheit wird Gestalt", M_STILL, "MUSIC_HARMONIC_TENSION"),
],
"023": [
    cue(IMG["IMG029"], "beobachtend / intelligent", M_HOLD, "ROOMTONE_WIDE"),
    cue(N["NEW_IMG043_PRESENCE_BEFORE_IMAGE"], "Präsenz vor Gestalt", M_HOLD, "LOW_AIR_TEXTURE"),
    cue(CLIP["CLIP003"], "Old-Hag-Schwelle", M_CLIP, "CHAIR_WOOD_SOFT", "Folklore-/Oral-History-Visualisierung"),
    cue(IMG["IMG031"], "Menschen geben Namen", M_STILL, "TAPE_HISS_LOW"),
    cue(IMG["SHOT07"], "Gestalt überlebt Erzählenden", M_HOLD, "MUSIC_RELEASE_DARK_TO_WARM"),
],
"024": [
    cue(IMG["IMG030"], "zurück zu Hufford", M_STILL, "PENCIL_NOTE"),
    cue(N["NEW_CARD008_HUFFORD_1963_1982"], "1963 / 1982", M_CARD, "NONE"),
    cue(O["O01"], "Tradition / Ort", M_SOURCE_MOVE, "COAST_WIND_LOW", "Original · PD"),
    cue(O["O02"], "Fogo-Archivanker", M_SOURCE, "NONE", "Originalkarte 1873 · PD"),
    cue(O["O08"], "belastbarer körperlicher Stand", M_SOURCE, "NONE", "YELLOW · Attribution/SA prüfen"),
],
"025": [
    cue(IMG["IMG009"], "REM-Atonie", M_HOLD, "LOW_BODY_TONE"),
    cue(IMG["IMG011"], "Mischzustand", M_HOLD, "SOFT_PHASE_SHIFT"),
    cue(IMG["IMG016"], "wiederkehrende Familien", M_HOLD, "MUSIC_THREE_NOTES"),
    cue(IMG["IMG027"], "Erlebnisfamilien", M_HOLD, "NONE"),
    cue(N["NEW_CARD013_OPEN_PRESENCE_QUESTION"], "Warum Begegnung?", M_CARD, "MUSIC_QUESTION_LOW"),
],
"026": [
    cue(IMG["IMG032"], "Nacht wird Gerichtsakte", M_STILL, "PAPER_NOTE"),
    cue(N["NEW_IMG044_BRIDGET_TESTIMONY_HANDOFF"], "Aussage über Brustdruck", M_HOLD, "QUILL_PAPER_SOFT"),
    cue(N["NEW_ORIG10_SALEM_COURT_1876"], "Salem vor Gericht", M_SOURCE, "COURT_ROOMTONE_LOW", "spätere Darstellung klar datieren"),
    cue(N["NEW_ORIG11_BRIDGET_BISHOP_RECORD"], "Bridget Bishop", M_SOURCE, "PAPER_TURN_SOFT", "nur verifiziertes PD-Dokument"),
    cue(IMG["SHOT08"], "private Nacht / öffentlicher Nachhall", M_HOLD, "MUSIC_HANDOFF_EP07"),
    cue(N["NEW_CARD014_PRIVATE_NIGHT_PUBLIC_RECORD"], "private Nacht wird öffentliche Wahrheit", M_CARD, "MUSIC_HANDOFF_EP07"),
]}


ACT_BEDS = {
    "S1": "MX_LOW_0.90+MX_NOISE_ROOM",
    "S2": "MX_LOW_0.72+MX_HARMONIC_COAST",
    "S3": "MX_LOW_0.60+MX_HARMONIC_SCIENCE",
    "S4": "MX_LOW_0.72+MX_HARMONIC_THREE_NOTE",
    "S5": "MX_LOW_0.84+MX_HARMONIC_LAB",
    "S6": "MX_LOW_0.88+MX_NOISE_ROOM",
    "S7": "MX_LOW_1.00+MX_HARMONIC_PRESENCE",
    "S8": "MX_LOW_0.66+MX_HARMONIC_RESOLUTION",
}


def tc(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def read_takes() -> dict[str, str]:
    raw = SCRIPT.read_text(encoding="utf-8")
    blocks = re.findall(
        r"^### TAKE (\d{3})[^\n]*\n\n(.*?)(?=^### TAKE \d{3}|^---\s*$)",
        raw,
        flags=re.MULTILINE | re.DOTALL,
    )
    takes = {num: text.strip() for num, text in blocks}
    if set(takes) != set(TAKE_META):
        raise RuntimeError(f"Take mismatch: {sorted(set(TAKE_META) ^ set(takes))}")
    return takes


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()
    return value[:46] or "SEMANTIC_INSERT"


def main() -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    SYNC.mkdir(parents=True, exist_ok=True)
    takes = read_takes()
    (ROOT / "EP06_VOICE_SCRIPT_CLEAN.txt").write_text(
        "\n\n".join(takes[num] for num in sorted(takes)) + "\n",
        encoding="utf-8",
    )

    manifest_rows = []
    timing = {}
    cursor = 0.0
    for num in sorted(takes):
        act, slug, delivery = TAKE_META[num]
        text = takes[num]
        words = len(re.findall(r"\b[\wÄÖÜäöüß]+(?:-[\wÄÖÜäöüß]+)*\b", text))
        # EP04A's completed George master averaged about 2.24 spoken words/s.
        # This remains an estimate until the actual stems are measured.
        duration = round(words / 2.24, 1)
        start = cursor
        end = start + duration
        filename = f"EP06_TAKE_{num}_{slug}.txt"
        (SOURCE / filename).write_text(text + "\n", encoding="utf-8")
        manifest_rows.append({
            "take_id": f"EP06_TAKE_{num}_{slug}", "act": act, "title": slug,
            "word_count": words, "estimated_speech_seconds": f"{duration:.1f}",
            "estimated_start": tc(start), "estimated_end": tc(end),
            "source_file": f"source/{filename}", "delivery": delivery,
            "voice_status": "TEXT_READY_NOT_GENERATED",
        })
        timing[num] = (start, end)
        cursor = end + 0.25

    with (ROOT / "take_manifest.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=manifest_rows[0].keys())
        writer.writeheader(); writer.writerows(manifest_rows)

    sync_rows = []
    shot_no = 1
    seen_per_act = defaultdict(set)
    base_seen = Counter()
    derivatives = []
    derivative_no = 9
    for num in sorted(takes):
        act, slug, _ = TAKE_META[num]
        start, end = timing[num]
        cues = V[num]
        segment = (end - start) / len(cues)
        for i, (asset_id, asset_class, path, anchor, motion, sfx, note) in enumerate(cues):
            if asset_id in seen_per_act[act]:
                raise RuntimeError(f"Repeat inside {act}: {asset_id}")
            seen_per_act[act].add(asset_id)
            base_seen[asset_id] += 1
            final_id, final_class, final_path = asset_id, asset_class, path
            is_card_or_clip = "CARD" in asset_class or "CLIP" in asset_class
            repeat_allowed = asset_id in ALLOW_REPEAT_TWICE and base_seen[asset_id] <= 2
            if not is_card_or_clip and base_seen[asset_id] > 1 and not repeat_allowed:
                final_id = f"SHOT{derivative_no:02d}"
                filename = f"{final_id}_{slugify(anchor)}.png"
                final_class = (
                    "PLANNED_EDITORIAL_DERIVATIVE"
                    if "ORIGINAL_ASSET" in asset_class
                    else "PLANNED_GENERATED_DERIVATIVE"
                )
                final_path = f"PLANNED/{filename}"
                derivatives.append({
                    "asset_id": final_id,
                    "filename": filename,
                    "take": f"EP06_TAKE_{num}_{slug}",
                    "act": act,
                    "anchor": anchor,
                    "base_asset": asset_id,
                    "base_path": path,
                    "method": "EDITORIAL_CROP_OR_DETAIL" if "ORIGINAL_ASSET" in asset_class else "NEW_IMAGEGEN_COMPANION",
                })
                derivative_no += 1
            v_start = start + i * segment
            v_end = end if i == len(cues) - 1 else start + (i + 1) * segment
            sync_rows.append({
                "shot_id": f"A{shot_no:03d}",
                "take_id": f"EP06_TAKE_{num}_{slug}",
                "act": act,
                "take_start_est": tc(start),
                "take_end_est": tc(end),
                "visual_start_est": tc(v_start),
                "visual_end_est": tc(v_end),
                "semantic_anchor": anchor,
                "asset_id": final_id,
                "asset_class": final_class,
                "asset_path_or_plan": final_path,
                "asset_status": "MISSING_TO_CREATE_OR_LICENSE" if final_class.startswith("PLANNED_") else "READY",
                "motion_policy": motion,
                "sfx_cue": sfx,
                "music_atmo": ACT_BEDS[act],
                "edit_note": note,
            })
            shot_no += 1

    # The endcard is deliberately static and outside the main voice timing.
    end_start = cursor + 0.55
    sync_rows.append({
        "shot_id": f"A{shot_no:03d}", "take_id": "ENDCARD", "act": "ENDCARD",
        "take_start_est": tc(end_start), "take_end_est": tc(end_start + 20.0),
        "visual_start_est": tc(end_start), "visual_end_est": tc(end_start + 20.0),
        "semantic_anchor": "Gehirn oder Muster? / Endscreen",
        "asset_id": "CARD007", "asset_class": "CARD",
        "asset_path_or_plan": f"{CARDS}/CARD007_ENDCARD.png", "asset_status": "READY",
        "motion_policy": M_CARD, "sfx_cue": "NONE",
        "music_atmo": "MX_HARMONIC_RESOLUTION_FADE_20S", "edit_note": "Exakt 20 s; YouTube-Endscreen-Flächen frei halten",
    })

    with (SYNC / "EP06_VOICE_VISUAL_SYNC.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=sync_rows[0].keys())
        writer.writeheader(); writer.writerows(sync_rows)

    # Every concrete card and every real/planned transform clip is used once.
    card_counts = Counter(row["asset_id"] for row in sync_rows if "CARD" in row["asset_class"])
    clip_counts = Counter(row["asset_id"] for row in sync_rows if "CLIP" in row["asset_class"])
    if max(card_counts.values(), default=0) > 1:
        raise RuntimeError(f"Card repeated: {card_counts}")
    if max(clip_counts.values(), default=0) > 1:
        raise RuntimeError(f"Clip repeated: {clip_counts}")

    derivative_doc = [
        "# EP06 — Semantic Derivative Batch",
        "",
        "These inserts replace repeated frames. Every output is a distinct 16:9, 2560×1440 shot named `SHOTxx`; none is a camera-only duplicate.",
        "",
        "## Global rules",
        "",
        "- Generated companion: use the base only for palette/material continuity; change framing, scale, arrangement, background and lighting. Do not recreate the same composition.",
        "- Original derivative: deterministic full/passage/detail crop only when it communicates the listed new anchor. Never alter source content or labels.",
        "- Bright readable midtones, no crushed black, no text invented by image generation, no bed added unless named in the anchor.",
        "- Cards are not part of this batch and remain static.",
        "",
    ]
    for item in derivatives:
        derivative_doc += [
            f"### `{item['filename']}`",
            "",
            f"- Take/act: `{item['take']}` / `{item['act']}`",
            f"- New semantic anchor: {item['anchor']}",
            f"- Base reference: `{item['base_path']}` (`{item['base_asset']}`)",
            f"- Method: `{item['method']}`",
            "- Execution brief: Create a genuinely distinct editorial companion for the new semantic anchor above. Preserve factual context and series palette, but change composition and information hierarchy. No camera-variant clone, no new written text, no logo, no watermark, no neon, no horror cliché.",
            "",
        ]
    (ROOT / "SEMANTIC_DERIVATIVE_BATCH.md").write_text("\n".join(derivative_doc) + "\n", encoding="utf-8")

    counts = Counter(row["asset_id"] for row in sync_rows)
    classes = Counter(row["asset_class"] for row in sync_rows)
    missing = sorted({row["asset_id"] for row in sync_rows if row["asset_status"] != "READY"})
    repeated = sorted(((k, v) for k, v in counts.items() if v > 1), key=lambda x: (-x[1], x[0]))
    original_unique = {row["asset_id"] for row in sync_rows if "ORIGINAL_ASSET" in row["asset_class"]}
    ready_unique = {row["asset_id"] for row in sync_rows if row["asset_status"] == "READY"}
    all_unique = set(counts)
    noncard = [row for row in sync_rows if row["act"] != "ENDCARD" and "CARD" not in row["asset_class"]]
    noncard_counts = Counter(row["asset_id"] for row in noncard)
    repeated_slots = sum(value - 1 for value in noncard_counts.values())
    repeat_pct = repeated_slots / len(noncard) * 100 if noncard else 0.0
    main_rows = [row for row in sync_rows if row["act"] != "ENDCARD"]

    def as_seconds(value: str) -> float:
        hh, mm, ss = value.split(":")
        return int(hh) * 3600 + int(mm) * 60 + float(ss)

    def row_duration(row: dict[str, str]) -> float:
        return as_seconds(row["visual_end_est"]) - as_seconds(row["visual_start_est"])

    main_duration = as_seconds(main_rows[-1]["visual_end_est"])
    card_seconds = sum(row_duration(row) for row in main_rows if "CARD" in row["asset_class"])
    original_seconds = sum(
        row_duration(row) for row in main_rows
        if "ORIGINAL_ASSET" in row["asset_class"] or "EDITORIAL_DERIVATIVE" in row["asset_class"]
    )
    ordinary_stills = [
        row for row in main_rows
        if "GENERATED_STILL" in row["asset_class"] or "GENERATED_DERIVATIVE" in row["asset_class"]
    ]
    moved_stills = [row for row in ordinary_stills if row["motion_policy"].startswith("GENTLE_PUSH")]
    clip_rows = [row for row in main_rows if "CLIP" in row["asset_class"]]
    max_shot = max(row_duration(row) for row in main_rows)
    first_change = row_duration(main_rows[0])
    clean_text = "\n\n".join(takes[num] for num in sorted(takes)).strip()
    word_count = len(re.findall(r"\b[\wÄÖÜäöüß]+(?:-[\wÄÖÜäöüß]+)*\b", clean_text))
    char_count = len(clean_text)

    audit = [
        "# EP06 — Originalasset- und Wiederholungs-Audit",
        "",
        "**Status:** Planung vor Voice-/Bildgenerierung  ",
        f"**Hauptschnitt:** {len(sync_rows)-1} visuelle Einsätze + 1 statische 20-s-Endcard  ",
        f"**Geschätztes Voice-Ende:** `{tc(cursor-0.25)}`  ",
        f"**Geschätztes Videoende inkl. Endcard:** `{tc(end_start+20.0)}`",
        f"**Reinschrift:** {word_count} Wörter · {char_count} Zeichen inkl. Leerzeichen",
        "",
        "## Gates",
        "",
        f"- Einmalige Motive im geplanten Schnitt: **{len(all_unique)}**.",
        f"- Davon aktuelle/noch zu beschaffende Originalassets: **{len(original_unique)}**.",
        f"- Bereits produktionsbereite eindeutige Assets: **{len(ready_unique)}**.",
        f"- Noch zu erstellende oder zu lizenzierende eindeutige Assets: **{len(missing)}**.",
        f"- Wiederholung desselben Assets innerhalb eines Akts: **0** (hart validiert).",
        f"- Wiederholungs-Slots ohne Karten/Endcard: **{repeated_slots}/{len(noncard)} = {repeat_pct:.2f}%** (Limit 15%).",
        f"- Höchste Verwendung eines Basisassets: **{max(noncard_counts.values())}×** (Lock: normalerweise höchstens 2×).",
        f"- Semantische Ersatzshots für frühere Wiederholungen: **{len(derivatives)}** (`SHOT09` ff.).",
        f"- Erster Bildwechsel: **{first_change:.3f} s** (Lock ≤2,5 s).",
        f"- Längster geplanter Shot: **{max_shot:.3f} s** (Lock <9 s).",
        f"- Original-/Quellenlaufzeit inkl. echter Detailderivate: **{original_seconds/main_duration*100:.2f}%** (Ziel EP06 25–35%).",
        f"- Kartenlaufzeit ohne Endcard: **{card_seconds/main_duration*100:.2f}%** (Ziel 8–12%).",
        f"- Bewegte gewöhnliche Stills: **{len(moved_stills)}/{len(ordinary_stills)} = {len(moved_stills)/len(ordinary_stills)*100:.2f}%** (Lock 40–60%).",
        f"- Einmalige Transformationsclips: **{len(clip_rows)}**, im Mittel ein Clip je **{main_duration/len(clip_rows):.2f} s** (Ziel 45–75 s).",
        "- Karten: immer `STATIC_NO_ZOOM_NO_PAN`.",
        "- Originaldokumente, Quellentafeln und Karten: vollständig statisch und lesbar; kontextuelle Originalfotos wären selbst im Ausnahmefall auf max. 1,008 begrenzt.",
        "- Generierte Stills: ruhiger Push bis maximal 1,025 oder statischer Hold.",
        "- Veo-Clips: native Bewegung, kein Retiming und keine zusätzliche Kamerafahrt.",
        "",
        "## Klassen im Schnitt",
        "",
        "| Klasse | Einsätze |",
        "|---|---:|",
    ]
    audit += [f"| {k} | {v} |" for k, v in sorted(classes.items())]
    audit += ["", "## Wiederholte Assets", "", "| Asset | Einsätze |", "|---|---:|"]
    audit += [f"| `{k}` | {v} |" for k, v in repeated]
    audit += ["", "## Noch fehlende IDs", ""]
    audit += [f"- `{item}`" for item in missing]
    audit += [
        "",
        "## Redaktionelle Originalasset-Regeln",
        "",
        "- Generische Schlaflaborfotos werden niemals als Bildmaterial des Takeuchi-Versuchs ausgegeben.",
        "- Jede historische Darstellung erhält sichtbare Jahres-/Kontextangabe in der Edit-Quellzeile.",
        "- YELLOW-Assets bleiben bis zum finalen Lizenz-, Attribution- und Persönlichkeitsrechtscheck gesperrt.",
        "- RED-/reference-only Material wird nicht in den Schnitt gelegt.",
        "- Hufford und Cheyne werden nicht durch erfundene Porträts identifiziert; Rekonstruktionen zeigen Handlung, Rückenansicht oder Hände und tragen die Quellzeile `Rekonstruktion`.",
        "- Karten und Dokumente bleiben statisch, vollständig sichtbar und werden nie zum dekorativen Ken-Burns-Hintergrund.",
    ]
    (ROOT / "ORIGINAL_ASSET_REPEAT_AUDIT.md").write_text("\n".join(audit) + "\n", encoding="utf-8")

    print(f"takes={len(takes)} shots={len(sync_rows)-1} unique={len(all_unique)} missing={len(missing)} repeat={repeat_pct:.2f}% derivatives={len(derivatives)} voice={tc(cursor-0.25)}")


if __name__ == "__main__":
    main()
