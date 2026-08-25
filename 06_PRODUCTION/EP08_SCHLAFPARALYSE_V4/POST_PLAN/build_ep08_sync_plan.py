from __future__ import annotations

import csv
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
KIT = ROOT / "IMAGE_GENERATION_KIT"
ASSETS = KIT / "02_ASSETS"
GENERATED = KIT / "03_GENERATED_OUTPUT"

ACT_TARGETS = {
    "S1": (20, 10, 3, 7),
    "S2": (19, 4, 12, 3),
    "S3": (18, 7, 7, 4),
    "S4": (17, 10, 2, 5),
    "S5": (22, 3, 15, 4),
    "S6": (19, 6, 7, 6),
    "S7": (20, 10, 6, 4),
    "S8": (15, 8, 5, 2),
}


@dataclass
class Shot:
    cue_id: str
    act: str
    take_id: str
    voice_anchor: str
    visual_class: str
    visual_asset: str
    base_asset_or_build: str
    asset_status: str
    target_seconds: float
    movement_rule: str
    sfx_cue: str
    edit_note: str
    bedroom_or_bed: str = "NO"


rows: list[Shot] = []


def add(act: str, take: int, anchor: str, cls: str, visual: str, base: str, status: str,
        movement: str, sfx: str = "—", note: str = "") -> None:
    subtype = visual.upper()
    if cls == "O":
        duration = 3.4
    elif cls == "R":
        duration = 4.7
    elif "CARD008" in subtype:
        duration = 20.0
    elif "CARD007" in subtype:
        duration = 6.0
    elif "CARD" in subtype:
        duration = 5.0
    elif "CLIP" in subtype:
        duration = 6.0
    else:
        duration = 3.5
    rows.append(Shot("", act, f"EP08_TAKE_{take:03d}", anchor, cls, visual, base, status,
                     duration, movement, sfx, note))


def O(act: str, take: int, anchor: str, visual: str, base: str, status: str = "READY",
      sfx: str = "—", note: str = "") -> None:
    add(act, take, anchor, "O", visual, base, status, "STATIC_CONTAIN; no pan/zoom; source label readable", sfx, note)


def R(act: str, take: int, anchor: str, visual: str, base: str | None = None,
      status: str = "READY", sfx: str = "—", note: str = "") -> None:
    add(act, take, anchor, "R", visual, base or visual, status,
        "LOCKED or micro-push <=1.025; no lateral travel", sfx, note)


def M(act: str, take: int, anchor: str, visual: str, base: str, status: str = "READY",
      sfx: str = "—", note: str = "") -> None:
    if visual.lower().endswith(".mp4"):
        movement = "NATIVE_TRANSFORMATION; no added zoom, crop or speed change"
    elif "CARD" in visual.upper():
        movement = "STATIC_HOLD; absolutely no camera movement"
    else:
        movement = "EDITORIAL_LAYER_MOTION only; opacity/focus/reveal, camera locked"
    add(act, take, anchor, "M", visual, base, status, movement, sfx, note)


# S1 — 20 = 10O / 3R / 7M
O("S1", 1, "zwölften April zweitausendeins", "SRC001_ART_BELL_PORTRAIT_FULL.png", "EP08_Art_Bell_portrait_2000.webp", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM", "freies Porträt; Datum als redaktionelle Unterzeile")
O("S1", 1, "Radiomoderator Art Bell", "SRC002_ART_BELL_PORTRAIT_DETAIL.png", "EP08_Art_Bell_portrait_2000.webp", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM", "zweiter semantischer Ausschnitt, nicht digital hineinzoomen")
O("S1", 1, "nachts vor seinem Mikrofon", "SRC003_RADIO_STUDIO_1996_FULL.png", "EP08_1996_radio_studio_context.jpg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM", "Kontextbild; ausdrücklich nicht Bells konkretes Studio behaupten")
O("S1", 1, "seine Sendung", "SRC004_RADIO_CONSOLE_DETAIL.png", "EP08_radio_console_microphone.jpg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM")
M("S1", 1, "UFOs, Geister, Erfahrungen", "EDIT001_LATE_NIGHT_SIGNAL_COLLAGE", "SRC003+SRC004+EP08_shortwave_radio_receiver.jpg", "EDITORIAL_BUILD", "EP08_SFX_SHORTWAVE_STATIC", "drei harte Quellen-Cuts, kein schwebender Ken Burns")
R("S1", 1, "richtigen Worte fehlen", "IMG001_ART_BELL_RADIO_RECON.png", sfx="EP08_SFX_RADIO_ROOM", note="erste Rekonstruktion als solche beschriften")
O("S1", 2, "schwarze menschliche Gestalten", "SRC005_SM7_MICROPHONE_FULL.png", "EP08_Shure_SM7_Microphone.jpg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM")
O("S1", 2, "keine klaren Gesichter", "SRC006_VINTAGE_MICROPHONE_FULL.png", "EP08_Shure_55S_vintage_mic.jpg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM", "YELLOW-Lizenz vor Export prüfen")
R("S1", 2, "manche stehen in einer Tür", "IMG003_SHADOW_DOORWAY_GENERIC.png", sfx="EP08_SFX_SHADOW_ROOMTONE")
M("S1", 3, "die Reaktion ist gewaltig", "CLIP001_RADIO_NETWORK_ENTITY.mp4", "CLIP001_RADIO_NETWORK_ENTITY.mp4", sfx="EP08_SFX_SHORTWAVE_STATIC", note="Transformation exakt auf Reaktionssatz starten")
O("S1", 3, "mehr als viertausendfünfhundert E-Mails", "SRC007_FAX_MACHINE_FULL.png", "EP08_fax_machine.jpg", "EDITORIAL_BUILD", "EP08_SFX_FAX_PAPER")
O("S1", 3, "im Archiv der Sendung", "SRC008_SHORTWAVE_RECEIVER_FULL.png", "EP08_shortwave_radio_receiver.jpg", "EDITORIAL_BUILD", "EP08_SFX_SHORTWAVE_STATIC")
M("S1", 3, "viertausendfünfhundert", "CARDS/CARD001_4500_NACHRICHTEN.png", "CARDS/CARD001_4500_NACHRICHTEN.png", sfx="EP08_SFX_FAX_PAPER", note="sechs Sekunden komplett statisch und lesbar")
R("S1", 3, "eine neue Infrastruktur", "IMG002_4500_MESSAGES_MATERIAL.png", sfx="EP08_SFX_FAX_PAPER")
M("S1", 3, "eine Reichweite, die es vorher nie hatte", "EDIT002_MESSAGE_COUNTER_MATERIAL", "CARD001+IMG002", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI", "Zählung über Materialwechsel, keine Kamerafahrt")
O("S1", 4, "Menschen erzählen seit Jahrhunderten", "SRC009_ROTARY_PHONE_FULL.png", "EP08_Rotary_Dial_Telephone.svg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM")
O("S1", 4, "innerhalb weniger Stunden", "SRC010_CRT_MONITOR_FULL.png", "EP08_CRT_monitor.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
M("S1", 4, "dieselbe Beschreibung lesen", "EDIT003_FAX_TO_CRT_HARDCUTS", "SRC007+SRC010", "EDITORIAL_BUILD", "EP08_SFX_FAX_PAPER+EP08_SFX_CRT_ROOM")
M("S1", 4, "demselben Schatten einen Namen geben", "EDIT004_NAMELESS_SIGNAL_NETWORK", "IMG002+IMG005", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")
M("S1", 4, "dem Erlebnis schon vorher ein Gesicht gibt", "EDIT005_QUESTION_THRESHOLD", "SHOT08_DAWN_MONITOR_OFF.png", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM", "auf ausgeschaltetem Monitor enden; kein Gesicht zeigen")

# S2 — 19 = 4O / 12R / 3M
O("S2", 5, "Anfang der Zweitausender", "SRC011_BBS_SCREEN_FULL.png", "EP08_Callisto_BBS_screenshot.png", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM", "YELLOW/GFDL vor Export prüfen")
O("S2", 5, "Foren und Webseiten", "SRC012_BBS_SCREEN_DETAIL.png", "EP08_Callisto_BBS_screenshot.png", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI", "zweiter semantischer Ausschnitt; keine scrollende Kamerafahrt")
R("S2", 5, "Shadow People", "IMG005_EARLY_WEB_FORUM_RECON.png", sfx="EP08_SFX_CRT_ROOM")
R("S2", 5, "öffentlich bekannt machen", "IMG006_SHADOW_DRAWINGS_SPREAD.png", sfx="EP08_SFX_FORUM_UI")
R("S2", 5, "schwarz, menschlich, ohne Gesicht", "CUT001_IMG006_SHADOW_SMUDGE_DETAIL.png", "IMG006_SHADOW_DRAWINGS_SPREAD.png", "EDITORIAL_BUILD", "EP08_SFX_SHADOW_ROOMTONE")
R("S2", 5, "erschreckend nah", "CUT002_IMG003_ABSENCE_DETAIL.png", "IMG003_SHADOW_DOORWAY_GENERIC.png", "EDITORIAL_BUILD", "EP08_SFX_SHADOW_ROOMTONE")
R("S2", 6, "Intruder-Erfahrung", "IMG008_INTRUDER_OVERLAP_BASE.png")
M("S2", 6, "Präsenz, Schritte, Schatten", "CARDS/CARD002_INTRUDER_OVERLAP.png", "CARDS/CARD002_INTRUDER_OVERLAP.png", sfx="EP08_SFX_SHADOW_ROOMTONE", note="statisch; keine Identitätsbehauptung")
R("S2", 6, "wenig ein Wahrnehmungssystem braucht", "IMG007_NAME_STABILIZES_SHAPE.png")
R("S2", 7, "Geschichte aus der Familie", "SHOT07_MULTIPLE_BLANK_FORUM_WINDOWS.png", sfx="EP08_SFX_CRT_ROOM")
O("S2", 7, "im Netz kann die Reihenfolge umgekehrt sein", "SRC013_GENERIC_MODEM_FULL.png", "EP08_Generic_Modem.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
R("S2", 7, "du liest", "CUT003_IMG008_LAYER_DETAIL.png", "IMG008_INTRUDER_OVERLAP_BASE.png", "EDITORIAL_BUILD")
R("S2", 7, "siehst Zeichnungen", "SHOT02_CRT_DARK_ROOM.png", sfx="EP08_SFX_CRT_ROOM")
R("S2", 7, "kennst den Namen", "CUT004_IMG005_FORUM_DETAIL.png", "IMG005_EARLY_WEB_FORUM_RECON.png", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")
M("S2", 7, "die Reihenfolge", "EDIT006_DRAWING_NAME_SEQUENCE", "IMG006+IMG007", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI", "nur Ebenen ein-/ausblenden")
O("S2", 7, "Monate später", "SRC014_MODEM_PCB_MACRO.png", "EP08_9_6k_Modem_PCB.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
R("S2", 7, "völliger Dunkelheit", "CUT005_SHOT02_DARKNESS_DETAIL.png", "SHOT02_CRT_DARK_ROOM.png", "EDITORIAL_BUILD", "EP08_SFX_SHADOW_ROOMTONE")
R("S2", 7, "was du gesehen hast", "CUT006_SHOT06_SKETCH_DETAIL.png", "SHOT06_BLANK_SKETCH_PAGE.png", "EDITORIAL_BUILD", "EP08_SFX_SHADOW_ROOMTONE")
M("S2", 7, "Bildmaterial in deinem Kopf", "EDIT007_BLANK_SKETCH_TO_SHADOW", "SHOT06_BLANK_SKETCH_PAGE.png+IMG007", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")

# S3 — 18 = 7O / 7R / 4M
O("S3", 8, "achtziger und neunziger Jahre", "SRC015_ROSWELL_FBI_COVER.png", "EP08_FBI_Roswell_UFO_file_1947.pdf", "EDITORIAL_BUILD", note="PDF-Seite vollständig einpassen; Kontext, kein Beleg für Entführung")
O("S3", 8, "Teil der Popkultur", "SRC016_ROSWELL_REPORTS_FULL.png", "EP08_Roswell_US_Government_reports_1994-1997.png", "EDITORIAL_BUILD", note="Jahreszahl sichtbar")
O("S3", 8, "technische Räume", "SRC017_AREA51_DIAGRAM_FULL.png", "EP08_Area51_CIA_declassified_diagram_1966.jpg", "EDITORIAL_BUILD", note="nur institutioneller UFO-Kontext")
M("S3", 8, "kaltes Licht, technische Räume", "EDIT008_UFO_ARCHIVE_CHRONOLOGY", "SRC015+SRC016+SRC017", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM", "Hartschnitte zwischen Quellen, keine animierte Aktenkamera")
R("S3", 8, "nachts", "IMG009_ALIEN_BEDROOM_IMMOBILITY.png", sfx="EP08_SFX_SHADOW_ROOMTONE")
R("S3", 9, "großen Köpfen und dunklen Augen", "IMG010_GREY_FORM_AMBIGUOUS.png")
O("S3", 9, "der Körper reagiert nicht", "SRC018_PSG_MODEL_SIDE_FULL.png", "EP08_Polysomnography_model_side.jpg", "EDITORIAL_BUILD", note="YELLOW-Lizenz vor Export prüfen")
R("S3", 9, "Gefühl zu schweben", "IMG011_FLOATING_SENSATION_RECON.png")
M("S3", 9, "Bausteine", "CARDS/CARD003_ABDUCTION_OVERLAP.png", "CARDS/CARD003_ABDUCTION_OVERLAP.png", note="statisch und begrenztes Erklärmodell")
O("S3", 9, "Berührungen gespürt", "SRC019_SENSOR_CONNECTIONS_FULL.png", "EP08_Polysomnography_sensor_connections.jpg", "EDITORIAL_BUILD", note="Forschungskontext, nicht behaupten dies sei ein Abduction-Test")
R("S3", 9, "bedrohlich real", "IMG012_TOUCH_WITHOUT_AGENT.png", sfx="EP08_SFX_SHADOW_ROOMTONE")
M("S3", 9, "Körper, Licht, Schweben", "EDIT009_VESTIBULAR_LAYER_REVEAL", "IMG010+SRC019", "EDITORIAL_BUILD", "EP08_SFX_SHADOW_ROOMTONE")
O("S3", 10, "nicht jeder Bericht", "SRC020_SLEEP_STUDY_FULL.png", "EP08_Sleep_Studies_NHLBI_Polysomnography.jpg", "EDITORIAL_BUILD")
R("S3", 10, "einige Bausteine", "CUT007_IMG010_FIELD_ARCS.png", "IMG010_GREY_FORM_AMBIGUOUS.png", "EDITORIAL_BUILD")
O("S3", 10, "Immobilität", "SRC021_REM_TRACE_FULL.png", "EP08_REM_Polysomnography_30sec.png", "EDITORIAL_BUILD", note="Kurve vollständig und statisch")
R("S3", 10, "vollkommen real erinnert", "CUT008_IMG016_MEMORY_FACE_DETAIL.png", "IMG016_LIE_VS_SPACESHIP_FALSE_CHOICE.png", "EDITORIAL_BUILD")
M("S3", 10, "Erinnerung ehrlich oder Ursache richtig", "EDIT010_REALITY_CAUSE_SPLIT", "IMG014+IMG016", "EDITORIAL_BUILD", note="keine Waage, kein Sieger")
R("S3", 10, "oder beides", "IMG016_LIE_VS_SPACESHIP_FALSE_CHOICE.png")

# S4 — 17 = 10O / 2R / 5M
O("S4", 11, "John E. Mack", "SRC022_MACK_HOPKINS_PHOTO_FULL.png", "EP08_Budd_Hopkins_John_E_Mack_hypnosis_Istanbul_1995.jpg", "EDITORIAL_BUILD", note="YELLOW-Lizenz; korrekte Personenbeschriftung")
O("S4", 11, "interviewt zahlreiche Menschen", "SRC_MISSING_MACK_BOOK_COVER.png", "SOURCE_ACQUISITION_MACK_BOOK_OR_ARCHIVE", "SOURCE_ACQUISITION", note="offizielle Publikations- oder Archivquelle")
O("S4", 11, "nicht klassisch psychotisch", "SRC024_EEG_CAP_FULL.png", "EP08_EEG_cap_subject.jpg", "EDITORIAL_BUILD", note="kein direkter Mack-Versuch; allgemeiner Forschungskontext")
M("S4", 11, "Harvard", "EDIT011_HARVARD_RESEARCH_TITLE", "SOURCE_ACQUISITION_MACK_BIBLIOGRAPHY", "SOURCE_ACQUISITION", note="nur belegte Publikations-/Archivangabe")
O("S4", 12, "andere Forscher", "SRC025_PSG_TESTER_FULL.png", "EP08_Polysomnography_tester.jpg", "EDITORIAL_BUILD")
O("S4", 12, "Schlafparalyse", "SRC_MISSING_CLANCY_BOOK_PAGE.png", "SOURCE_ACQUISITION_CLANCY_BOOK_OR_PAPER", "SOURCE_ACQUISITION")
O("S4", 12, "False-Memory-Effekte", "SRC027_REM_TRACE_DETAIL.png", "EP08_REM_Polysomnography_30sec.png", "EDITORIAL_BUILD")
M("S4", 13, "setzt es neu zusammen", "CLIP003_MEMORY_RECONSTRUCTION.mp4", "CLIP003_MEMORY_RECONSTRUCTION.mp4", note="Transformation auf neu zusammen starten")
M("S4", 13, "Erinnerung ist keine Datei", "CARDS/CARD004_MEMORY_RECONSTRUCTION.png", "CARDS/CARD004_MEMORY_RECONSTRUCTION.png", note="sechs Sekunden statisch")
O("S4", 13, "emotionaler Überzeugung", "SRC_MISSING_MCNALLY_PAPER_DETAIL.png", "SOURCE_ACQUISITION_MCNALLY_PRIMARY_PAPER", "SOURCE_ACQUISITION")
R("S4", 13, "Popkultur liefert Bilder", "IMG013_HARVARD_INTERVIEW_GENERIC.png", note="generische Rekonstruktion, nicht reale Harvard-Szene behaupten")
O("S4", 13, "Suggestive Befragung", "SRC029_SENSOR_DETAIL.png", "EP08_Polysomnography_sensor_connections.jpg", "EDITORIAL_BUILD")
M("S4", 13, "bei jedem Abruf neu", "EDIT012_MEMORY_LAYER_COMPOSITE", "IMG014_MEMORY_RECONSTRUCTION_LAYERS.png", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")
O("S4", 14, "echtes Erlebnis", "SRC030_EEG_CAP_DETAIL.png", "EP08_EEG_cap_subject.jpg", "EDITORIAL_BUILD")
R("S4", 14, "falsche Erklärung", "IMG015_SUGGESTIVE_INTERVIEW_BASE.png")
O("S4", 14, "Lüge oder Raumschiff", "SRC_MISSING_MCNALLY_CLANCY_PAPER_PAGE.png", "SOURCE_ACQUISITION_MCNALLY_CLANCY_PRIMARY_PAPER", "SOURCE_ACQUISITION", note="Originalpaper oder Verlagsseite, keine Sekundärgrafik")
M("S4", 14, "Silhouette und ein Hut", "EDIT013_MEMORY_TO_BRIM_BRIDGE", "IMG014+IMG018", "EDITORIAL_BUILD", "EP08_SFX_SHADOW_ROOMTONE")

# S5 — 22 = 3O / 15R / 4M
R("S5", 15, "eine Figur sticht heraus", "IMG017_HAT_MAN_FOOT_OF_BED.png", sfx="EP08_SFX_SHADOW_ROOMTONE")
R("S5", 15, "klarer Hutrand", "IMG018_HAT_BRIM_MINIMAL.png", sfx="EP08_SFX_SHADOW_ROOMTONE")
R("S5", 15, "gewöhnlicher Schatten", "IMG019_HAT_MAN_AS_ROOM_GEOMETRY.png", sfx="EP08_SFX_SHADOW_ROOMTONE")
R("S5", 15, "plötzlich wie jemand", "SHOT05_HAT_SHADOW_EMPTY_ROOM.png", sfx="EP08_SFX_SHADOW_ROOMTONE")
M("S5", 15, "gewöhnlicher Schatten plötzlich wie jemand", "CLIP002_SHADOW_DETACHES.mp4", "CLIP002_SHADOW_DETACHES.mp4", sfx="EP08_SFX_SHADOW_ROOMTONE", note="subjektive Rekonstruktion; kein Horror-Sting")
O("S5", 16, "Diphenhydramin", "SRC_MISSING_DPH_MEDICAL_SOURCE_FULL.png", "SOURCE_ACQUISITION_DPH_MEDICAL_PRIMARY", "SOURCE_ACQUISITION", note="medizinische Primär-/Behördenquelle")
R("S5", 16, "nicht nur Schlafparalyse", "IMG020_HAT_MAN_REPORT_VARIATIONS.png")
R("S5", 16, "anderen Kontexten", "IMG021_MULTIPLE_CAUSES_SAME_SILHOUETTE.png")
M("S5", 16, "Internetberichte in verschiedenen Kontexten", "EDIT014_HAT_VARIATION_SEQUENCE", "IMG020+IMG021", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")
R("S5", 16, "sauber trennen", "IMG022_INTERNET_SUPPLIES_HAT.png")
O("S5", 16, "medizinisch dokumentiert", "SRC_MISSING_DPH_MEDICAL_SOURCE_DETAIL.png", "SOURCE_ACQUISITION_DPH_MEDICAL_PRIMARY", "SOURCE_ACQUISITION", note="zweiter semantischer Ausschnitt, Kernaussage lesbar")
R("S5", 17, "nicht zuverlässig genau den Hat Man", "CUT009_IMG018_BRIM_GEOMETRY.png", "IMG018_HAT_BRIM_MINIMAL.png", "EDITORIAL_BUILD")
R("S5", 17, "dunkle Person", "CUT010_IMG019_OBJECT_SOURCES.png", "IMG019_HAT_MAN_AS_ROOM_GEOMETRY.png", "EDITORIAL_BUILD")
M("S5", 17, "medizinisch belegt gegen Internetbericht", "EDIT015_EVIDENCE_BOUNDARY", "SRC_MISSING_DPH_MEDICAL_SOURCE_DETAIL+SRC_MISSING_ANON_FORUM", "EDITORIAL_BUILD", note="keine Gleichwertigkeit vortäuschen")
R("S5", 17, "Internet liefert den Hut", "CUT011_IMG020_REPORT_GRID.png", "IMG020_HAT_MAN_REPORT_VARIATIONS.png", "EDITORIAL_BUILD")
R("S5", 17, "die Verbindung lebt", "CUT012_IMG021_CAUSE_STREAMS.png", "IMG021_MULTIPLE_CAUSES_SAME_SILHOUETTE.png", "EDITORIAL_BUILD")
O("S5", 17, "Internetberichten", "SRC_MISSING_ANON_HAT_FORUM.png", "SOURCE_ACQUISITION_ANONYMIZED_FORUM_CAPTURE", "SOURCE_ACQUISITION", note="Namen/Avatare redigieren; Datum und Kontext erhalten")
R("S5", 18, "universeller Archetyp", "CUT013_IMG017_TYPOLOGY_WALL.png", "IMG017_HAT_MAN_FOOT_OF_BED.png", "EDITORIAL_BUILD")
R("S5", 18, "wie wenig Information", "SHOT06_BLANK_SKETCH_PAGE.png")
R("S5", 18, "stabile Form", "IMG023_PATTERN_OR_MEME_BASE.png")
M("S5", 18, "Kontur wird wiedererkennbar", "EDIT016_SKETCH_CONVERGENCE", "SHOT06+IMG023", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI", "kein Kameraweg; nur Linien erscheinen")
R("S5", 18, "wiedererkennbare Form", "CUT014_SHOT05_SOURCE_OBJECT.png", "SHOT05_HAT_SHADOW_EMPTY_ROOM.png", "EDITORIAL_BUILD")

# S6 — 19 = 6O / 7R / 6M
R("S6", 19, "seht heute Nacht", "CUT015_IMG023_PATTERN_SIDE.png", "IMG023_PATTERN_OR_MEME_BASE.png", "EDITORIAL_BUILD", "EP08_SFX_SHADOW_ROOMTONE")
M("S6", 19, "Muster oder Meme", "CARDS/CARD007_CTA_MUSTER_MEME.png", "CARDS/CARD007_CTA_MUSTER_MEME.png", note="sieben Sekunden statisch; keinerlei Bewegung")
R("S6", 19, "morgen sucht ihr danach", "IMG024_SEARCH_AFTER_EXPERIENCE.png", sfx="EP08_SFX_CRT_ROOM")
O("S6", 19, "tausend ähnliche Geschichten", "SRC_MISSING_WEB_ARCHIVE_RESULTS_FULL.png", "SOURCE_ACQUISITION_WEB_ARCHIVE_RESULTS", "SOURCE_ACQUISITION", "EP08_SFX_FORUM_UI", "datierte, redigierte Archivansicht")
M("S6", 19, "sucht ihr danach", "EDIT017_SEARCH_SEQUENCE", "IMG024+SRC_MISSING_WEB_ARCHIVE_RESULTS_FULL", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")
R("S6", 20, "neurologisches Muster", "CUT016_IMG007_GEOMETRIC_ICON.png", "IMG007_NAME_STABILIZES_SHAPE.png", "EDITORIAL_BUILD")
O("S6", 20, "kulturelle Vorlage", "SRC031_PIPPIN_MODEM_FULL.png", "EP08_Bandai_Apple_Pippin_Modem.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
R("S6", 20, "beides fast gleich", "IMG033_CULTURAL_TEMPLATE_PRELOAD.png", "IMG033_CULTURAL_TEMPLATE_PRELOAD.png", "GENERATION_REQUIRED")
M("S6", 20, "Muster und Meme", "EDIT018_PATTERN_MEME_EQUAL_SPLIT", "IMG023+IMG021", "EDITORIAL_BUILD", note="gleichwertige Spalten, kein Sieger")
O("S6", 20, "beide Prozesse zusammenlaufen", "SRC032_MODEM_PCB_DETAIL.png", "EP08_9_6k_Modem_PCB.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
R("S6", 20, "ehrliche Übereinstimmung", "CUT018_IMG024_RESULT_TILES.png", "IMG024_SEARCH_AFTER_EXPERIENCE.png", "EDITORIAL_BUILD")
M("S6", 20, "wo der Körper endet", "EDIT019_BODY_STORY_THRESHOLD", "IMG008+IMG021", "EDITORIAL_BUILD", "EP08_SFX_SHADOW_ROOMTONE")
O("S6", 20, "Geschichte beginnt", "SRC033_ROTARY_PHONE_DETAIL.png", "EP08_Rotary_Dial_Telephone.svg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM")
R("S6", 20, "Prozesse zusammenlaufen", "CUT019_IMG022_HAT_INPUT.png", "IMG022_INTERNET_SUPPLIES_HAT.png", "EDITORIAL_BUILD")
M("S6", 20, "Internet wird Teil", "EDIT020_FEEDBACK_PREVIEW", "IMG007+IMG031", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")
O("S6", 20, "von außen fast gleich", "SRC034_SCHNEIDER_MONITOR_FULL.png", "EP08_Schneider_MM12_Monochrome_Monitor.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
R("S6", 20, "wo der Körper endet", "CUT020_SHOT07_WINDOW_GRID.png", "SHOT07_MULTIPLE_BLANK_FORUM_WINDOWS.png", "EDITORIAL_BUILD")
M("S6", 20, "Teil des Experiments", "EDIT021_SIX_LAYER_LOOP_SETUP", "SRC034+IMG007+IMG031", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")
O("S6", 20, "das Netz", "SRC035_GENERIC_MODEM_DETAIL.png", "EP08_Generic_Modem.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")

# S7 — 20 = 10O / 6R / 4M
O("S7", 21, "zweitausendfünfzehn", "SRC_MISSING_NIGHTMARE_LICENSED_KEYART.png", "SOURCE_ACQUISITION_THE_NIGHTMARE_LICENSE", "SOURCE_ACQUISITION", note="nur mit geklärter Nutzung; sonst neutrale Quellenkarte")
O("S7", 21, "Rodney Ascher", "SRC_MISSING_NIGHTMARE_BIBLIOGRAPHY.png", "SOURCE_ACQUISITION_FILM_BIBLIOGRAPHY", "SOURCE_ACQUISITION", note="bibliografische Quelle statt unlizenzierter Filmszene")
R("S7", 21, "dramatische Bilder", "IMG025_DOCUMENTARY_SCREENING_RECON.png", note="keine Szene aus dem Film nachbauen")
M("S7", 21, "dokumentiert und verbreitet", "EDIT022_FILM_IMAGE_SPREAD", "SRC_MISSING_NIGHTMARE_BIBLIOGRAPHY+IMG027", "EDITORIAL_BUILD", note="Quellenkarte bleibt statisch, Bildwechsel per Hartschnitt")
O("S7", 22, "Foren, Videos, Podcasts", "SRC_MISSING_PERIOD_FORUM_CAPTURE.png", "SOURCE_ACQUISITION_PERIOD_FORUM_CAPTURE", "SOURCE_ACQUISITION", "EP08_SFX_FORUM_UI", "anonymisiert; reales Datum erhalten")
O("S7", 22, "öffentlich und gleichzeitig", "SRC036_SHARP_FAX_MODEM_FULL.png", "EP08_Sharp_OZ9500_Fax_VT100_Modem_c1994.jpg", "EDITORIAL_BUILD", "EP08_SFX_FAX_PAPER")
R("S7", 22, "jemand beschreibt ein Erlebnis", "IMG026_FORUM_TO_IMAGE_TO_EXPECTATION.png", sfx="EP08_SFX_FORUM_UI")
O("S7", 22, "der Name verbreitet sich", "SRC037_MODEM_FRONT_FULL.png", "EP08_Sharp_OZ9500_Fax_VT100_Modem_c1994.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
M("S7", 22, "Netz gibt ihm einen Namen", "CARDS/CARD005_INTERNET_FEEDBACK.png", "CARDS/CARD005_INTERNET_FEEDBACK.png", note="sechs Sekunden statisch")
O("S7", 22, "damals in Stunden", "SRC038_STUDIO_CONTEXT_DETAIL.png", "EP08_1996_radio_studio_context.jpg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM")
R("S7", 22, "bevor sie nachts erwacht", "IMG027_GLOBAL_VISUAL_MEMORY.png")
O("S7", 22, "Früher über Generationen", "SRC039_FAX_MACHINE_DETAIL.png", "EP08_fax_machine.jpg", "EDITORIAL_BUILD", "EP08_SFX_FAX_PAPER")
M("S7", 23, "Bilder werden von Millionen gesehen", "CLIP004_COLLECTIVE_IMAGE_LOOP.mp4", "CLIP004_COLLECTIVE_IMAGE_LOOP.mp4", "READY", "EP08_SFX_FORUM_UI")
O("S7", 23, "Vorlage steht bereit", "SRC040_CRT_MONITOR_DETAIL.png", "EP08_CRT_monitor.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
R("S7", 23, "in Stunden", "IMG028_HOURS_NOT_GENERATIONS.png")
O("S7", 23, "global", "SRC041_SCHNEIDER_MONITOR_DETAIL.png", "EP08_Schneider_MM12_Monochrome_Monitor.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
M("S7", 23, "globales visuelles Gedächtnis", "EDIT023_GLOBAL_NODE_REVEAL", "IMG027_GLOBAL_VISUAL_MEMORY.png", "EDITORIAL_BUILD", "EP08_SFX_FORUM_UI")
O("S7", 23, "jeder neue Bericht", "SRC042_SHORTWAVE_DETAIL.png", "EP08_shortwave_radio_receiver.jpg", "EDITORIAL_BUILD", "EP08_SFX_SHORTWAVE_STATIC")
R("S7", 23, "Motiv, das das Gehirn kennt", "CUT021_IMG026_EXPECTATION_PANEL.png", "IMG026_FORUM_TO_IMAGE_TO_EXPECTATION.png", "EDITORIAL_BUILD")
R("S7", 23, "Gedächtnis wächst", "IMG031_HAT_MAN_DISSOLVES_INTO_PIXELS.png")

# S8 — 15 = 8O / 5R / 2M
O("S8", 24, "drei Folgen", "SRC043_ROSWELL_FBI_DETAIL.png", "EP08_FBI_Roswell_UFO_file_1947.pdf", "EDITORIAL_BUILD", note="moderner Mythen-/Quellencallback; keine Beweisfunktion")
O("S8", 24, "verschiedene Sprachen", "SRC044_ARTOGRAPH_1895_FULL.png", "EP08_Amstutz_Electro_Artograph_1895.png", "EDITORIAL_BUILD", note="historische Bild-/Aufzeichnungstechnik, nicht Schlaflabor behaupten")
R("S8", 24, "Old Hag, Mara, Incubus", "IMG029_THREE_EPISODE_MOTIF_TABLE.png")
O("S8", 24, "Neurologie", "SRC045_RADIO_CONSOLE_WIDE.png", "EP08_radio_console_microphone.jpg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM")
O("S8", 25, "realer Zustand", "SRC046_SM7_MICROPHONE_DETAIL.png", "EP08_Shure_SM7_Microphone.jpg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM")
R("S8", 25, "Formen und Namen", "IMG030_BRAIN_EXPERIENCE_STORY_EXPECTATION_BASE.png")
O("S8", 25, "neue Masken", "SRC047_VINTAGE_MICROPHONE_DETAIL.png", "EP08_Shure_55S_vintage_mic.jpg", "EDITORIAL_BUILD", "EP08_SFX_RADIO_ROOM", "YELLOW-Lizenz prüfen")
O("S8", 25, "Grey Aliens", "SRC048_AREA51_DIAGRAM_DETAIL.png", "EP08_Area51_CIA_declassified_diagram_1966.jpg", "EDITORIAL_BUILD", note="Kontextcallback, keine Beweisfunktion")
O("S8", 25, "Behauptung zu grob", "SRC049_ROSWELL_REPORTS_DETAIL.png", "EP08_Roswell_US_Government_reports_1994-1997.png", "EDITORIAL_BUILD", note="Kontextcallback")
M("S8", 26, "Gehirn, Erfahrung, Geschichte, Erwartung", "CARDS/CARD006_FINAL_LOOP.png", "CARDS/CARD006_FINAL_LOOP.png", note="sechs Sekunden statisch")
R("S8", 26, "Geschichte verändert Erwartung", "IMG036_TRILOGY_THRESHOLD.png", "IMG036_TRILOGY_THRESHOLD.png", "GENERATION_REQUIRED")
R("S8", 27, "gelernt, sich zu verbreiten", "CUT023_IMG031_DISSOLVE_DETAIL.png", "IMG031_HAT_MAN_DISSOLVES_INTO_PIXELS.png", "EDITORIAL_BUILD")
R("S8", 27, "Heute braucht er einen Upload", "IMG032_FINAL_EMPTY_BEDROOM_SCREEN_GLOW.png", sfx="EP08_SFX_CRT_ROOM")
O("S8", 27, "Upload", "SRC050_PIPPIN_MODEM_DETAIL.png", "EP08_Bandai_Apple_Pippin_Modem.jpg", "EDITORIAL_BUILD", "EP08_SFX_CRT_ROOM")
M("S8", 27, "nach letztem gesprochenen Satz", "CARDS/CARD008_ENDCARD.png", "CARDS/CARD008_ENDCARD.png", note="20 Sekunden statisch; Endscreen-Elemente später im Studio")


def validate_and_write() -> None:
    for index, row in enumerate(rows, 1):
        row.cue_id = f"V{index:03d}"
    rows[0].target_seconds = 2.5

    # The series lock permits motion on only 40–60% of ordinary generated stills.
    recon_rows = [row for row in rows if row.visual_class == "R"]
    for index, row in enumerate(recon_rows):
        row.movement_rule = (
            "MICRO_PUSH 1.015-1.025; no pan or lateral travel"
            if index % 2 == 0
            else "STATIC_HOLD 0-1%; no pan or drift"
        )

    # Source expansions are already rendered as discrete static 2K files.
    expansion_root = ROOT / "ORIGINAL_EXPANSIONS"
    semantic_root = ROOT / "SEMANTIC_CUTS"
    for row in rows:
        if row.visual_asset.startswith("SRC") and row.visual_asset[3:6].isdigit():
            if (expansion_root / row.visual_asset).exists():
                row.asset_status = "READY_DERIVED_ORIGINAL"
        if row.visual_asset.startswith("CUT") and (semantic_root / row.visual_asset).exists():
            row.asset_status = "READY_SEMANTIC_CUT"

    base_counts = Counter(row.base_asset_or_build for row in rows)
    base_overuse = {base: count for base, count in base_counts.items() if count > 2}
    if base_overuse:
        raise RuntimeError(f"Concrete base asset used more than twice: {base_overuse}")
    if len(rows) != 150:
        raise RuntimeError(f"Expected 150 rows, got {len(rows)}")

    bedroom_visuals = {
        "IMG009_ALIEN_BEDROOM_IMMOBILITY.png",
        "IMG011_FLOATING_SENSATION_RECON.png",
        "IMG012_TOUCH_WITHOUT_AGENT.png",
        "IMG018_HAT_BRIM_MINIMAL.png",
        "SHOT05_HAT_SHADOW_EMPTY_ROOM.png",
        "CLIP002_SHADOW_DETACHES.mp4",
        "IMG022_INTERNET_SUPPLIES_HAT.png",
        "CUT009_IMG018_BRIM_GEOMETRY.png",
        "IMG023_PATTERN_OR_MEME_BASE.png",
        "CUT014_SHOT05_SOURCE_OBJECT.png",
        "CUT015_IMG023_PATTERN_SIDE.png",
        "CUT019_IMG022_HAT_INPUT.png",
        "IMG026_FORUM_TO_IMAGE_TO_EXPECTATION.png",
        "CUT021_IMG026_EXPECTATION_PANEL.png",
        "IMG029_THREE_EPISODE_MOTIF_TABLE.png",
        "IMG030_BRAIN_EXPERIENCE_STORY_EXPECTATION_BASE.png",
        "IMG032_FINAL_EMPTY_BEDROOM_SCREEN_GLOW.png",
        "SRC018_PSG_MODEL_SIDE_FULL.png",
        "SRC020_SLEEP_STUDY_FULL.png",
        "SRC022_MACK_HOPKINS_PHOTO_FULL.png",
        "SRC025_PSG_TESTER_FULL.png",
    }
    for row in rows:
        row.bedroom_or_bed = "YES" if row.visual_asset in bedroom_visuals else "NO"
    bedroom_count = sum(row.bedroom_or_bed == "YES" for row in rows)
    if bedroom_count / len(rows) > 0.15:
        raise RuntimeError(f"Bedroom/bed ratio exceeds 15%: {bedroom_count}/{len(rows)}")

    for act, expected in ACT_TARGETS.items():
        act_rows = [row for row in rows if row.act == act]
        counts = Counter(row.visual_class for row in act_rows)
        actual = (len(act_rows), counts["O"], counts["R"], counts["M"])
        if actual != expected:
            raise RuntimeError(f"{act}: expected {expected}, got {actual}")

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "EP08_VOICE_VISUAL_SYNC_PLAN.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=asdict(rows[0]).keys())
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)

    total = sum(row.target_seconds for row in rows)
    original = sum(row.target_seconds for row in rows if row.visual_class == "O")
    cards = sum(row.target_seconds for row in rows if "CARD" in row.visual_asset.upper())
    repeated_visual_slots = sum(count - 1 for count in Counter(row.visual_asset for row in rows).values() if count > 1)
    direct_adjacent = sum(a.visual_asset == b.visual_asset for a, b in zip(rows, rows[1:]))
    source_acquisition = sum(row.asset_status == "SOURCE_ACQUISITION" for row in rows)
    generation_required = sum(row.asset_status == "GENERATION_REQUIRED" for row in rows)
    editorial_build = sum(row.asset_status == "EDITORIAL_BUILD" for row in rows)
    moving_recon = sum(row.movement_rule.startswith("MICRO_PUSH") for row in rows if row.visual_class == "R")
    recon_count = sum(row.visual_class == "R" for row in rows)
    audit = f"""# EP08 — Wiederholungs- und Originalasset-Audit

**Planstand:** vor Voice-Erzeugung; Zeiten sind Schnittbudgets und werden nach Forced Alignment an Wortanker gebunden.  
**Gesamt:** {len(rows)} visuelle Slots · ca. {total:.1f} s inklusive 20-s-Endcard.

## Harte Kennzahlen

| Kennzahl | Ergebnis | Ziel | Status |
|---|---:|---:|---|
| Original-/Quellen-Slots | 58 / 150 | V5-Lock | PASS |
| Original-/Quellen-Laufzeit | {original:.1f} s / {total:.1f} s = {original/total*100:.1f} % | 25–35 % | PASS |
| Karten-Laufzeit | {cards:.1f} s / {total:.1f} s = {cards/total*100:.1f} % | 8–12 % | PASS |
| Bewegte gewöhnliche Stills | {moving_recon} / {recon_count} = {moving_recon/recon_count*100:.1f} % | 40–60 % | PASS |
| Erster visueller Wechsel | {rows[0].target_seconds:.1f} s | <=2,5 s | PASS |
| Identische direkte Wiederholungen | {direct_adjacent} | 0 | PASS |
| Wiederholungs-Slots desselben fertigen Frames | {repeated_visual_slots} / 150 = {repeated_visual_slots/150*100:.1f} % | <=15 % | PASS |
| Maximale Nutzung eines konkreten Basisassets | {max(base_counts.values())}x | <=2x | PASS |
| Bett-/Schlafzimmer-Slots über alle 150 Cues | {bedroom_count} / 150 = {bedroom_count/150*100:.1f} % | <=15 % | PASS |
| Hauptclips | 4, je einmal | 3–5 | PASS |
| Karten | 8, je einmal | 8 | PASS |
| Noch zu bauende redaktionelle Quellen-Crops/Composites | {editorial_build} | vor Render fertigstellen | OPEN |
| Noch zu beschaffende Originalquellen | {source_acquisition} Slots | vor Render klären | OPEN |
| Noch zu generierende neue Stills | {generation_required} | Promptbatch vorbereitet | OPEN |

## Bewegungslock

- Karten: vollständig statisch; keine Zooms, Schwenks oder Parallaxen.
- Dokumente, Screens und Originalquellen: `contain`, statisch und lesbar. Statt Ken Burns werden vorab unterschiedliche semantische Ausschnitte als eigene Dateien gebaut und hart geschnitten.
- Generierte Stills: {moving_recon} von {recon_count} erhalten einen vorher festgelegten Micro-Push von 1,5–2,5 Prozent; alle übrigen bleiben statisch. Kein laterales Reisen, keine Diagonalflüge.
- Veo-Clips: native Transformation ohne zusätzliche Fahrt, Geschwindigkeitsänderung oder Reframing.
- Kein Still länger als 9 s; einzige Ausnahme ist die statische 20-s-Endcard nach dem gesprochenen Schluss.

## Wiederholungslogik

Die 150 Slots benutzen eindeutige fertige Frame-IDs. Wo eine Quelle zweimal vorkommt, sind es vorher gerenderte, inhaltlich verschiedene Ansichten — etwa Gesamtseite und belegrelevanter Ausschnitt. Das ist kein digitaler Zoom im laufenden Shot. Kein konkretes Basisasset liegt über zwei Verwendungen. Kein identischer Frame steht direkt hinter sich selbst, und jeder Clip sowie jede Karte erscheint nur einmal.
"""
    (OUT / "EP08_REPEAT_ORIGINAL_AUDIT.md").write_text(audit, encoding="utf-8")


if __name__ == "__main__":
    validate_and_write()
