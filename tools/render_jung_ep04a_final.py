#!/usr/bin/env python3
"""Render the complete EP04A Jung/Kundalini review cut.

The motion path reproduces the proven V4.2 camera treatment: 8K spatial
oversampling, 120 fps temporal oversampling, four-frame averaging, and a global
eight-shot motion cycle.  Every segment is normalized to 1080p30 before concat.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1"
VOICE_DIR = SERIES / "VOICE_EP04A"
RENDER = SERIES / "RENDER_EP04A"
ASSETS = RENDER / "assets"
SEGMENTS = RENDER / "segments_v2_final"
FINAL = RENDER / "final"
ARRANGEMENT = SERIES / "ARRANGEMENT" / "EP04A_SHOT_ORDER.csv"
SYNC = VOICE_DIR / "sync" / "EP04A_VOICE_VISUAL_SYNC.csv"
VOICE = VOICE_DIR / "master" / "EP04A_GEORGE_VO_MASTER.wav"
VOICE_REPORT = VOICE_DIR / "master" / "stem_report.json"
SFX_DIR = RENDER / "audio" / "sfx_stems"
MIX = RENDER / "audio" / "EP04A_GEORGE_SFX_MIX.wav"
OUTRO_SFX = RENDER / "audio" / "EP04A_OUTRO_SFX_20S.wav"
TIMELINE = RENDER / "timeline" / "EP04A_RENDER_TIMELINE_V2.json"
RENDER_MANIFEST = RENDER / "EP04A_RENDER_MANIFEST_V2.json"
VIDEO_ONLY = FINAL / "EP04A_JUNG_KUNDALINI_VIDEO_ONLY_V2.mp4"
OUTPUT = FINAL / "EP04A_JUNG_KUNDALINI_FINAL_V2.mp4"

FPS = 30
SUB = 4
SW, SH = 7680, 4320
BG = "#0A0A0F"
OUTRO_SECONDS = 20.0
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi"}

MAIN = SERIES / "FINAL_STILLS" / "EP04A" / "MAIN"
RESERVE = SERIES / "FINAL_STILLS" / "EP04A" / "RESERVE"
MOTION = SERIES / "MOTION_BASES_2K" / "EP04A"
REFS = SERIES / "REFERENCES_EP04AB"
REFS05 = SERIES / "REFERENCES_EP05"
LEGACY = ROOT / "06_PRODUCTION" / "EP04_JUNG" / "visuals" / "final"
LEGACY_VIDEO = ROOT / "06_PRODUCTION" / "EP04_JUNG" / "visuals" / "V4.2" / "video"
REWORK = ASSETS / "rework_v2"


def run(args: list[str], capture: bool = False) -> str:
    result = subprocess.run(args, text=True, capture_output=capture)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "command failed")[-10000:])
    return (result.stdout or "") + (result.stderr or "")


def duration(path: Path) -> float:
    return float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ], True).strip())


def p(*parts: str) -> Path:
    return SERIES.joinpath(*parts)


def parse_paths(raw: str) -> list[Path]:
    return [Path(item.strip()) for item in (raw or "").split(";") if item.strip()]


def create_editorial_assets() -> dict[str, Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    REWORK.mkdir(parents=True, exist_ok=True)

    def ui_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        candidates = [
            Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        ]
        for candidate in candidates:
            if candidate.is_file():
                return ImageFont.truetype(str(candidate), size)
        return ImageFont.load_default()

    base = Image.open(MAIN / "EP04A_IMG002_JUNG_WARNING_RECON.png").convert("RGBA")
    label = Image.open(MOTION / "A-G05_REKONSTRUKTION_LABEL.png").convert("RGBA")
    recon = ASSETS / "EP04A_IMG002_REKONSTRUKTION_LABEL.png"
    Image.alpha_composite(base, label).convert("RGB").save(recon, optimize=True)

    base = Image.open(MAIN / "EP04A_IMG005_JUNG_BEFORE_UNKNOWN_MAP.png").convert("RGBA")
    label = Image.open(MOTION / "A-G05_OFFENE_PARALLELE_LABEL.png").convert("RGBA")
    parallel = ASSETS / "EP04A_IMG005_OFFENE_PARALLELE_LABEL.png"
    Image.alpha_composite(base, label).convert("RGB").save(parallel, optimize=True)

    portrait_path = REFS / "EP04A" / "01_ORIGINAL_GREEN" / "PORTRAITS" / "EP04A_Jung_portrait_PD.jpg"
    plate_path = (
        REFS / "00_SHARED" / "01_ORIGINAL_GREEN" / "SERPENT_POWER"
        / "SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg"
    )
    canvas = Image.new("RGB", (2560, 1440), "#111113")
    portrait = ImageOps.contain(Image.open(portrait_path).convert("RGB"), (1000, 1180), Image.Resampling.LANCZOS)
    plate = ImageOps.contain(Image.open(plate_path).convert("RGB"), (1040, 1120), Image.Resampling.LANCZOS)
    for image, center_x in ((portrait, 680), (plate, 1880)):
        frame = ImageOps.expand(image, border=14, fill="#d8d0bf")
        shadow = Image.new("RGBA", (frame.width + 70, frame.height + 70), (0, 0, 0, 0))
        shadow_box = Image.new("RGBA", frame.size, (0, 0, 0, 175))
        shadow.paste(shadow_box, (35, 35))
        shadow = shadow.filter(ImageFilter.GaussianBlur(22))
        x = center_x - frame.width // 2
        y = 720 - frame.height // 2
        canvas.paste(shadow, (x - 35, y - 35), shadow)
        canvas.paste(frame, (x, y))
    draw = ImageDraw.Draw(canvas)
    draw.line((1280, 200, 1280, 1240), fill="#746d62", width=2)
    composite = ASSETS / "EP04A_A059_JUNG_INDIA_OPEN_COMPOSITE.png"
    canvas.save(composite, optimize=True)

    rng_seed = 40419
    dry = Image.new("RGB", (2560, 1440), BG)
    draw = ImageDraw.Draw(dry)
    for index in range(160):
        x = (index * 1597 + rng_seed) % 2560
        y = (index * 881 + rng_seed * 3) % 1440
        shade = 14 + (index % 8)
        draw.point((x, y), fill=(shade, shade, shade + 2))
    dry = dry.filter(ImageFilter.GaussianBlur(1.2))
    dry_path = ASSETS / "EP04A_A027_DRY_BLACK_ROOM.png"
    dry.save(dry_path, optimize=True)

    line = dry.copy()
    draw = ImageDraw.Draw(line)
    points = []
    for x in range(560, 2001, 20):
        phase = (x - 560) / 1440
        y = 720 + int(26 * math.sin(phase * math.pi * 1.35) * (1 - phase))
        points.append((x, y))
    draw.line(points, fill="#817d76", width=2)
    line_path = ASSETS / "EP04A_A062_MINIMAL_PROBLEM_LINE.png"
    line.save(line_path, optimize=True)

    # One calm explanatory card replaces the abstract ICH-BIN-WUT tile
    # sequence.  It reads as a complete thought and remains spatially locked.
    meaning = Image.new("RGB", (2560, 1440), "#101114")
    draw = ImageDraw.Draw(meaning)
    draw.text((170, 150), "ZWISCHEN GEFÜHL UND HANDLUNG", font=ui_font(38, True), fill="#8DC7CD")
    draw.line((170, 220, 930, 220), fill="#31565A", width=3)
    draw.text((170, 405), "Die Wut ist noch da.", font=ui_font(94, True), fill="#F3EFE6")
    draw.text((170, 555), "Nur sie entscheidet nicht mehr allein,", font=ui_font(76), fill="#E2DDD2")
    draw.text((170, 665), "was als Nächstes passiert.", font=ui_font(76), fill="#E2DDD2")
    draw.ellipse((178, 900, 208, 930), fill="#D05A52")
    draw.text((250, 870), "In diesem kurzen Abstand entsteht eine Wahl.", font=ui_font(48), fill="#AFA99E")
    meaning_path = REWORK / "EP04A_CARD_ABSTAND_VERSTAENDLICH.png"
    meaning.save(meaning_path, optimize=True)

    # Dedicated YouTube end screen: one preview surface and one subscribe
    # target, with generous safe space for the platform's clickable overlays.
    outro = Image.new("RGB", (2560, 1440), "#0E1013")
    draw = ImageDraw.Draw(outro)
    draw.text((150, 110), "MODELLE DES GEISTES", font=ui_font(34, True), fill="#89C4CB")
    draw.line((150, 170, 700, 170), fill="#2B4A4E", width=3)
    draw.text((150, 315), "Als Nächstes", font=ui_font(58), fill="#B9B4AA")
    draw.text((150, 405), "JUNG UND PAULI", font=ui_font(104, True), fill="#F2EEE5")
    draw.multiline_text(
        (150, 560), "Träume, Zufälle und eine\nungewöhnliche Freundschaft", font=ui_font(54),
        fill="#D1CCC1", spacing=18,
    )
    pauli_path = REFS05 / "EP05" / "01_ORIGINAL_GREEN" / "PORTRAITS" / "SRC02_Wolfgang_Pauli_1945.jpg"
    pauli = ImageOps.fit(Image.open(pauli_path).convert("RGB"), (810, 820), Image.Resampling.LANCZOS)
    panel_x, panel_y = 1570, 220
    outro.paste(pauli, (panel_x, panel_y))
    draw.rectangle((panel_x, panel_y, panel_x + 810, panel_y + 820), outline="#837D73", width=4)
    draw.rectangle((panel_x, panel_y + 720, panel_x + 810, panel_y + 820), fill="#111317")
    draw.text((panel_x + 35, panel_y + 744), "NÄCHSTE FOLGE", font=ui_font(38, True), fill="#F3EFE6")
    button = (150, 1120, 650, 1230)
    draw.rounded_rectangle(button, radius=24, fill="#C53832")
    draw.polygon([(195, 1150), (195, 1200), (238, 1175)], fill="white")
    draw.text((275, 1142), "ABONNIEREN", font=ui_font(42, True), fill="white")
    draw.text((150, 1280), "Danke fürs Zuschauen.", font=ui_font(34), fill="#87847D")
    outro_path = REWORK / "EP04A_ENDCARD_JUNG_PAULI_20S.png"
    outro.save(outro_path, optimize=True)

    return {
        "recon": recon, "parallel": parallel, "composite": composite,
        "dry": dry_path, "line": line_path, "meaning": meaning_path, "outro": outro_path,
    }


def special_assets(editorial: dict[str, Path]) -> dict[str, list[Path]]:
    lotus = (
        REFS / "00_SHARED" / "01_ORIGINAL_GREEN" / "SERPENT_POWER"
        / "SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg"
    )
    legacy = lambda name: LEGACY / name
    clip = lambda name: LEGACY_VIDEO / name
    return {
        # S1: Hook.  No empty seminar pads and no repeated master plate.
        "A001": [legacy("EP04_S5_052_zuerich_1932.png")],
        "A002": [legacy("EP04_S5_060_kundalini_an_der_wurzel.png")],
        "A003": [
            legacy("EP04_S5_057_jung_am_rednerpult.png"),
            legacy("EP04_S5_059_zwei_zuhoerer.png"),
            MOTION / "A-G02_WARNUNG_PARAPHRASE.png",
        ],
        "A004": [legacy("EP04_S1_007_die_flut.png")],
        "A005": [MAIN / "EP04A_IMG004_RED_SUN_UNDER_WATER_FLASH.png"],
        "A006": [clip("VE05_aufsteigende_schlange.mp4")],
        "A007": [
            legacy("EP04_S7_102_hand_auf_der_landkarte.png"),
            MAIN / "EP04A_IMG005_JUNG_BEFORE_UNKNOWN_MAP.png",
            legacy("EP04_S4_044_mandala.png"),
        ],

        # S2: train, war and clinical grounding.
        "A008": [legacy("EP04_S1_001_lok_viadukt.png"), MAIN / "EP04A_IMG006_TRAIN_1913_NORMAL.png"],
        "A009": [
            legacy("EP04_S1_004_freud_und_jung.png"),
            REFS / "EP04A" / "01_ORIGINAL_GREEN" / "GATHERINGS" / "EP04A_Clark_University_group_1909_PD.jpg",
        ],
        "A010": [MAIN / "EP04A_IMG009_JUNG_TRAIN_REACTION.png"],
        "A011": [clip("VE01_die_gelbe_flut.mp4")],
        "A012": [clip("VE02_das_meer_wird_zu_blut.mp4"), legacy("EP04_S1_009_meer_wird_zu_blut.png")],
        "A013": [
            legacy("EP04_S1_011_burghoelzli.png"),
            legacy("EP04_S2_015_feder_und_tintenfass.png"),
            REFS / "EP04A" / "01_ORIGINAL_GREEN" / "CLINIC_DOCUMENTS" / "EP04A_Jung_Association_Method_1910_PD.png",
        ],
        "A014": [MAIN / "EP04A_IMG011_BURGHOELZLI_MEMORY_ROOM.png"],
        "A015": [
            legacy("EP04_S1_013_zeitungen_1914.png"),
            REFS / "EP04A" / "01_ORIGINAL_GREEN" / "MAPS" / "EP04A_Europe_1914_Shepherd_PD.jpg",
        ],
        "A016": [legacy("EP04_S1_008_truemmer_im_wasser.png"), legacy("EP04_S1_006_haende_auf_den_knien.png")],
        "A017": [REWORK / "EP04A_REWORK_FILLED_NOTEBOOK_1913_2K.png"],

        # S3: active imagination.  Each Philemon beat receives a distinct image.
        "A018": [
            legacy("EP04_S2_014_arbeitszimmer_bei_nacht.png"),
            legacy("EP04_S4_046_folio_bei_kerzenlicht.png"),
            MAIN / "EP04A_IMG013_WAITING_FOR_IMAGES.png",
        ],
        "A019": [MAIN / "EP04A_IMG014_VERTICAL_FALL.png"],
        "A020": [MAIN / "EP04A_IMG015_CAVE_WIDE.png"],
        "A021": [MAIN / "EP04A_IMG017_CORPSE_DISTANT_WATER.png", legacy("EP04_S2_018_der_schwarze_kaefer.png")],
        "A022": [MAIN / "EP04A_IMG019_ELIAS_SALOME_FRAGMENTS.png"],
        "A023": [legacy("EP04_S3_030_schwarze_schlange_schiefer.png")],
        "A024": [
            legacy("EP04_S3_028_elias.png"),
            legacy("EP04_S3_029_salome.png"),
            legacy("EP04_S3_032_philemon.png"),
            MAIN / "EP04A_IMG020_PHILEMON_DISTANCE.png",
        ],
        "A025": [clip("IMG40_autonome_struktur_V3.mp4"), legacy("EP04_S3_038_vogelschwarm.png")],
        "A026": [
            REFS / "EP04A" / "02_REVIEW_YELLOW" / "PLACES" / "EP04A_Jung_House_Kuesnacht_CC-BY-SA-3.0.jpg",
            legacy("EP04_S2_023_praxis_bei_tageslicht.png"),
            legacy("EP04_S2_024_gedeckter_tisch.png"),
        ],
        "A027": [editorial["dry"]],

        # S4: seminar and the disciplined context of the source tradition.
        "A028": [legacy("EP04_S5_054_der_vortragssaal.png")],
        "A029": [
            REFS / "EP04A" / "02_REVIEW_YELLOW" / "PORTRAITS" / "EP04A_Jakob_Wilhelm_Hauer_1935_Bundesarchiv_CC-BY-SA-3.0.jpg",
            legacy("EP04_S5_053_eingang_des_clubs.png"),
            legacy("EP04_S5_053_haus_gemeindestrasse.png"),
        ],
        "A030": [
            legacy("EP04_S5_061_wirbelsaeule_und_aufstieg.png"),
            legacy("EP04_S5_062_hoehle_und_tafel.png"),
            MOTION / "A-G06_HISTORISCHE_CHAKRA_QUELLE.png",
        ],
        "A031": [legacy("EP04_S7_088_gelehrte_am_palmblatt.png"), legacy("EP04_S5_068_die_tafel_wird_aufgehaengt.png")],
        "A032": [
            legacy("EP04_S7_100_jung_mit_der_lupe.png"),
            ASSETS / "SHARED_BOOK_001_PLATE_I.png",
            legacy("EP04_S6_083_galvanometer_auf_null.png"),
        ],
        "A033": [MAIN / "EP04A_IMG025_INNER_GRAVITY_ROOM.png", legacy("EP04_S5_065_kamin_im_arbeitszimmer.png")],
        "A034": [MOTION / "A-G07_BODEN_AFFEKT_ABSTAND.png", legacy("EP04_S3_040_autonome_struktur.png")],

        # S5/S6: one understandable path from embodiment to choice.
        "A035": [
            legacy("EP04_S5_064_riss_im_boden.png"),
            legacy("EP04_S5_066_familienbild_schreibtisch.png"),
            legacy("EP04_S2_025_arztkoffer_und_muetze.png"),
        ],
        "A036": [clip("IMG80_offenes_fenster_V3.mp4")],
        "A037": [legacy("EP04_S6_076_hitzeflimmern.png"), MAIN / "EP04A_IMG028_MANIPURA_BODY_MACRO.png"],
        "A038": [MAIN / "EP04A_IMG029_CONVERSATION_BEFORE_TURN.png"],
        "A039": [
            MAIN / "EP04A_IMG030_CONVERSATION_AFFECT_SHIFT.png",
            legacy("EP04_S6_075_der_streit.png"),
            MAIN / "EP04A_IMG031_SUBJECTIVE_COMPRESSION.png",
        ],
        "A040": [MAIN / "EP04A_IMG033_OBSERVER_STEP_BACK.png"],
        "A041": [MAIN / "EP04A_IMG032_ANAHATA_BREATH_OPEN.png", legacy("EP04_S8_111_am_ufer.png")],
        "A042": [
            legacy("EP04_S6_079_beobachter_vor_der_flamme.png"),
            editorial["meaning"],
            legacy("EP04_S6_080_offenes_fenster.png"),
        ],
        "A043": [legacy("EP04_S6_081_zwei_stuehle.png")],
        "A044": [REWORK / "EP04A_REWORK_PHONE_MESSAGE_2K.png"],
        "A045": [MAIN / "EP04A_IMG035_BODY_REACTION_SEQUENCE_STILL.png", legacy("EP04_S6_071_schreibtisch_der_sorgen.png")],
        "A046": [REWORK / "EP04A_REWORK_PHONE_REPLY_HOVER_2K.png", RESERVE / "EP04A_RSV06_PHONE_ROOM_ALT.png"],
        "A047": [MAIN / "EP04A_IMG037_TWO_SECOND_HOVER.png"],
        "A048": [
            MAIN / "EP04A_IMG038_RELEASE_PULLBACK.png",
            legacy("EP04_S8_112_land_ohne_wege.png"),
            legacy("EP04_S6_084_sahasrara_loest_sich_auf.png"),
        ],
        "A049": [
            legacy("EP04_S8_109_die_augen.png"),
            MOTION / "A-G10_KARTE_SPIEGEL.png",
            legacy("EP04_S7_094_modernes_chakra_poster.png"),
            legacy("EP04_S7_095_der_esoterikladen.png"),
        ],
        "A050": [ASSETS / "SHARED_BOOK_001_TITLE_1924.png"],

        # S7/S8: actual printed sources, their travel, and the Pauli handoff.
        "A051": [clip("IMG46_folio_kerzenlicht_V3.mp4"), MOTION / "A-G11_1919_1924_QUELLENDISZIPLIN.png"],
        "A052": [ASSETS / "SHARED_BOOK_001_TITLE_DETAIL.png"],
        "A053": [MOTION / "A-G12_SECHS_SAHASRARA.png", ASSETS / "SHARED_BOOK_001_ILLUSTRATIONS.png", lotus],
        "A054": [legacy("EP04_S7_096_portraet_leadbeater.png"), legacy("EP04_S7_097_farbtherapie_apparat.png")],
        "A055": [
            legacy("EP04_S7_087_high_court_kalkutta.png"),
            MOTION / "A-G13_KARTE_REIST.png",
            legacy("EP04_S7_086_portraet_woodroffe.png"),
        ],
        "A056": [REFS / "EP04A" / "01_ORIGINAL_GREEN" / "PORTRAITS" / "EP04A_Jung_portrait_PD.jpg"],
        "A057": [legacy("EP04_S7_101_ueberblendung_hoehle_tafel.png"), MAIN / "EP04A_IMG043_BLACK_SNAKE_RESIDUE.png"],
        "A058": [legacy("EP04_S6_082_ajna.png"), legacy("EP04_S4_048_farbschichten_detail.png")],
        "A059": [
            editorial["composite"],
            legacy("EP04_S7_087_die_richter.png"),
            legacy("EP04_S8_104_der_tresorraum.png"),
            legacy("EP04_S4_049_steinturm_am_see.png"),
        ],
        "A060": [RESERVE / "EP04A_RSV08_BLACK_WATER_CLOSE.png", legacy("EP04_S3_031_der_kopf_hebt_sich.png")],
        "A061": [
            REFS05 / "EP05" / "01_ORIGINAL_GREEN" / "PORTRAITS" / "SRC02_Wolfgang_Pauli_1945.jpg",
            legacy("EP04_S8_117_portraet_pauli.png"),
            MOTION / "A-G14_PAULI_HANDOFF.png",
        ],
        "A062": [editorial["line"]],
    }


def image_shape(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def is_card(path: Path) -> bool:
    return path.parent == MOTION or path.name.startswith("A-G") or "_CARD_" in path.name or "ENDCARD" in path.name


def needs_contain(path: Path) -> bool:
    if path.suffix.lower() in VIDEO_EXT:
        return True
    width, height = image_shape(path)
    ratio = width / max(1, height)
    return not 1.62 <= ratio <= 1.95


def build_timeline() -> list[dict]:
    editorial = create_editorial_assets()
    special = special_assets(editorial)
    report = json.loads(VOICE_REPORT.read_text(encoding="utf-8"))
    total_seconds = float(report["master_duration"])
    voice_frames = int(round(total_seconds * FPS))
    total_frames = voice_frames + int(round(OUTRO_SECONDS * FPS))

    with ARRANGEMENT.open("r", encoding="utf-8-sig", newline="") as handle:
        arrangement = {row["cue_id"]: row for row in csv.DictReader(handle)}
    with SYNC.open("r", encoding="utf-8-sig", newline="") as handle:
        sync_rows = list(csv.DictReader(handle))
    first_by_cue: dict[str, dict] = {}
    for row in sync_rows:
        cue = row["cue_id"]
        if cue not in first_by_cue or float(row["cue_start"]) < float(first_by_cue[cue]["cue_start"]):
            first_by_cue[cue] = row

    cue_ids = sorted(arrangement, key=lambda cue: int(cue[1:]))
    cue_start_frames = []
    for index, cue_id in enumerate(cue_ids):
        seconds = 0.0 if index == 0 else float(first_by_cue[cue_id]["cue_start"])
        cue_start_frames.append(max(0, min(voice_frames - 1, int(round(seconds * FPS)))))
    cue_start_frames.append(voice_frames)

    shots: list[dict] = []
    asset_ledger = {}
    for cue_index, cue_id in enumerate(cue_ids):
        row = arrangement[cue_id]
        start_frame = cue_start_frames[cue_index]
        end_frame = cue_start_frames[cue_index + 1]
        if end_frame <= start_frame:
            end_frame = start_frame + 1
        assets = special.get(cue_id, parse_paths(row.get("resolved_paths", "")))
        assets = [path.resolve() for path in assets]
        missing = [str(path) for path in assets if not path.is_file()]
        if missing:
            raise SystemExit(f"Missing assets for {cue_id}: {missing}")
        if not assets:
            raise SystemExit(f"No asset bound for {cue_id}")
        asset_ledger[cue_id] = [str(path) for path in assets]

        pace = (row.get("pace") or "normal").casefold()
        cue_frames = end_frame - start_frame
        # V2 is hand-curated: the number of bound assets is the editorial shot
        # count.  Never cycle a short asset list merely to satisfy a mechanical
        # pacing rule; that was the main source of visible repetition in V1.
        target_count = min(len(assets), cue_frames)
        if cue_frames / target_count / FPS > 8.6:
            raise SystemExit(f"{cue_id} needs another unique visual: {cue_frames / target_count / FPS:.2f}s per shot")
        base_frames, remainder = divmod(cue_frames, target_count)
        cursor = start_frame
        for local_index in range(target_count):
            frame_count = base_frames + (1 if local_index < remainder else 0)
            visual = assets[local_index % len(assets)]
            kind = "VIDEO" if visual.suffix.lower() in VIDEO_EXT else ("CARD" if is_card(visual) else "STILL")
            shots.append({
                "shot_id": f"{cue_id}_{local_index + 1:02d}",
                "cue_id": cue_id,
                "section": row["section"],
                "anchor": row["voice_anchor"],
                "pace": pace,
                "visual": str(visual),
                "kind": kind,
                "contain": needs_contain(visual),
                "start_frame": cursor,
                "end_frame": cursor + frame_count,
                "start": round(cursor / FPS, 6),
                "end": round((cursor + frame_count) / FPS, 6),
                "duration": round(frame_count / FPS, 6),
                "frame_count": frame_count,
                "primary_visual": row["primary_visual"],
                "edit_function": row["edit_function"],
            })
            cursor += frame_count

    outro_asset = editorial["outro"].resolve()
    outro_frames = total_frames - voice_frames
    shots.append({
        "shot_id": "OUTRO_01",
        "cue_id": "OUTRO",
        "section": "S9",
        "anchor": "YouTube-Endscreen und Vorschau Jung und Pauli",
        "pace": "hold",
        "visual": str(outro_asset),
        "kind": "CARD",
        "contain": False,
        "start_frame": voice_frames,
        "end_frame": total_frames,
        "start": round(voice_frames / FPS, 6),
        "end": round(total_frames / FPS, 6),
        "duration": round(outro_frames / FPS, 6),
        "frame_count": outro_frames,
        "primary_visual": "next episode preview and subscribe end screen",
        "edit_function": "youtube_endscreen",
    })
    asset_ledger["OUTRO"] = [str(outro_asset)]

    for index, shot in enumerate(shots):
        shot["scene_first"] = index == 0 or shots[index - 1]["section"] != shot["section"]
        shot["scene_last"] = index == len(shots) - 1 or shots[index + 1]["section"] != shot["section"]

    TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    TIMELINE.write_text(json.dumps({
        "episode": "EP04A", "fps": FPS, "duration": total_frames / FPS,
        "frame_count": total_frames, "shots": shots,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RENDER_MANIFEST.write_text(json.dumps({
        "episode": "EP04A", "cue_count": len(cue_ids), "shot_count": len(shots),
        "video_clip_count": sum(shot["kind"] == "VIDEO" for shot in shots),
        "assets": asset_ledger,
        "motion": "V2 restrained 8K/120fps still camera; cards locked; source clips unmodified spatially",
        "editorial_rules": {
            "direct_duplicate_assets": 0,
            "blank_notebook_board_paper_motifs": 0,
            "card_camera_motion": "none",
            "video_camera_motion": "none",
        },
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Timeline: {len(cue_ids)} cues -> {len(shots)} shots -> {total_frames} frames")
    return shots


def camera_filter(index: int, shot: dict) -> str:
    if shot["kind"] == "CARD":
        return (
            "scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:{BG},fps={FPS},"
            "eq=contrast=1.02:saturation=1.02,format=yuv420p"
        )
    frames = shot["frame_count"] * SUB
    lin = f"(on/{frames})"
    ease = f"(0.6*{lin}+0.4*({lin}*{lin}*(3-2*{lin})))"
    tempo = min(1.0, max(.62, shot["duration"] / 7.0))
    pan_tempo = .46 * tempo
    center_x, center_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    right, down = "(iw-iw/zoom)", "(ih-ih/zoom)"

    def traverse(distance: str, backwards: bool = False) -> str:
        start = .5 - pan_tempo / 2 if not backwards else .5 + pan_tempo / 2
        direction = pan_tempo if not backwards else -pan_tempo
        return f"{distance}*({start:.4f}+{direction:.4f}*{ease})"

    if shot["contain"]:
        pairs = [(1.015, .020), (1.040, -.018)]
        z0, dz = pairs[index % 2]
        z1 = z0 + dz * tempo
        x, y = center_x, center_y
    else:
        movements = [
            (1.020, .025, center_x, center_y),
            (1.045, -.020, center_x, center_y),
            (1.045, 0.0, traverse(right), center_y),
            (1.045, 0.0, traverse(right, True), center_y),
            (1.040, 0.0, center_x, traverse(down, True)),
            (1.025, .018, traverse(right), traverse(down)),
            (1.050, -.016, traverse(right, True), center_y),
            (1.040, 0.0, center_x, traverse(down)),
        ]
        z0, dz, x, y = movements[index % 8]
        z1 = z0 + dz * tempo
    z1 = min(1.065, max(1.008, z1))
    zoom = f"{z0:.4f}+({z1-z0:.4f})*{ease}"
    return (
        f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS*SUB},"
        f"tmix=frames={SUB}:weights='1 1 1 1',fps={FPS},"
        "eq=contrast=1.03:saturation=1.04,unsharp=5:5:.24:5:5:0,format=yuv420p"
    )


def full_filter(index: int, shot: dict) -> tuple[str, bool]:
    camera = camera_filter(index, shot)
    loop = f",loop=loop=-1:size=1:start=0,fps={FPS*SUB}"
    if shot["kind"] == "CARD":
        result = f"loop=loop=-1:size=1:start=0,{camera}"
        complex_filter = False
    elif shot["kind"] == "VIDEO" and shot["contain"]:
        # The legacy Veo files are 1080x1920 containers with a genuine 16:9
        # image letterboxed in the vertical centre.  Recover that image instead
        # of nesting the pre-existing black bars in another portrait frame.
        result = (
            "crop=iw:iw*9/16:0:(ih-iw*9/16)/2,"
            "scale=1920:1080:flags=lanczos,"
            f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
            "eq=contrast=1.02:saturation=1.02,format=yuv420p"
        )
        complex_filter = False
    elif shot["kind"] == "VIDEO":
        result = (
            "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,"
            f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
            "eq=contrast=1.02:saturation=1.02,format=yuv420p"
        )
        complex_filter = False
    elif shot["contain"]:
        base = (
            "[0:v]split=2[bg][fg];"
            "[bg]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
            "gblur=sigma=103,eq=brightness=-0.66:saturation=0.28:contrast=0.82[back];"
            "[fg]scale=3688:1968:force_original_aspect_ratio=decrease:flags=lanczos,"
            "pad=iw+24:ih+24:12:12:0x2E2418[front];"
            "[back][front]overlay=(W-w)/2:(H-h)/2[comp];"
            f"[comp]{loop.lstrip(',') + ',' if loop else ''}{camera}[vout]"
        )
        result = base
        complex_filter = True
    else:
        result = (
            f"scale={SW}:{SH}:force_original_aspect_ratio=increase,crop={SW}:{SH}"
            f"{loop},{camera}"
        )
        complex_filter = False
    if shot["scene_first"]:
        result = result.replace("[vout]", "") if complex_filter else result
        result += f",fade=t=in:st=0:d=0.35:color={BG}"
        if complex_filter:
            result += "[vout]"
    if shot["scene_last"]:
        if complex_filter:
            result = result[:-6]
        result += f",fade=t=out:st={max(0.0, shot['duration']-.35):.3f}:d=0.35:color={BG}"
        if complex_filter:
            result += "[vout]"
    return result, complex_filter


def render_one(index: int, shot: dict) -> tuple[int, str, str]:
    target = SEGMENTS / f"{index + 1:03d}_{shot['shot_id']}.mp4"
    if target.is_file() and abs(duration(target) - shot["duration"]) <= .06:
        return index, "skip", target.name
    vf, complex_filter = full_filter(index, shot)
    input_args = ["-stream_loop", "-1", "-i", shot["visual"]] if shot["kind"] == "VIDEO" else ["-i", shot["visual"]]
    command = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *input_args,
        "-sws_flags", "lanczos+accurate_rnd+full_chroma_int",
        "-t", f"{shot['duration']:.6f}",
    ]
    if complex_filter:
        command += ["-filter_complex", vf, "-map", "[vout]"]
    else:
        command += ["-vf", vf]
    command += [
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-threads", "3", str(target),
    ]
    run(command)
    return index, "render", target.name


def render_segments(shots: list[dict], workers: int) -> None:
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(render_one, index, shot) for index, shot in enumerate(shots)]
        complete = 0
        for future in as_completed(futures):
            index, action, name = future.result()
            complete += 1
            print(f"[{complete:03d}/{len(shots):03d}] {action:6} {index + 1:03d} {name}", flush=True)


def mix_audio() -> None:
    sfx = sorted(SFX_DIR.glob("EP04A_SFX_*.wav"))
    if len(sfx) != 9:
        raise SystemExit(f"Expected 9 SFX stems, found {len(sfx)}. Run build_jung_ep04a_sfx.py")
    MIX.parent.mkdir(parents=True, exist_ok=True)
    inputs = ["-i", str(VOICE)]
    for path in sfx:
        inputs += ["-i", str(path)]
    sfx_inputs = "".join(f"[{index}:a]" for index in range(1, len(sfx) + 1))
    filt = (
        f"{sfx_inputs}amix=inputs={len(sfx)}:normalize=0:dropout_transition=0[sfx];"
        "[sfx][0:a]sidechaincompress=threshold=.015:ratio=4:attack=20:release=250[ducked];"
        "[0:a]pan=stereo|c0=c0|c1=c0[voice];"
        "[voice][ducked]amix=inputs=2:normalize=0:duration=first,"
        "loudnorm=I=-14:TP=-1:LRA=8[aout]"
    )
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
        "-filter_complex", filt, "-map", "[aout]", "-ar", "48000", "-ac", "2",
        "-c:a", "pcm_s24le", str(MIX),
    ])
    print(f"Audio mix: {MIX}")


def assemble(shots: list[dict]) -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    concat = FINAL / "concat.txt"
    concat.write_text("\n".join(
        f"file '{(SEGMENTS / f'{index + 1:03d}_{shot['shot_id']}.mp4').as_posix()}'"
        for index, shot in enumerate(shots)
    ) + "\n", encoding="utf-8")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat),
        "-c:v", "libx264", "-preset", "medium", "-crf", "16",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(VIDEO_ONLY),
    ])
    if not OUTRO_SFX.is_file():
        raise SystemExit(f"Missing outro sound: {OUTRO_SFX}. Run build_jung_ep04a_outro_sfx.py")
    target_duration = shots[-1]["end_frame"] / FPS
    outro_start = shots[-1]["start_frame"] / FPS
    delay_ms = int(round(outro_start * 1000))
    audio_filter = (
        f"[1:a]apad=pad_dur={OUTRO_SECONDS:.3f},atrim=0:{target_duration:.6f}[base];"
        f"[2:a]adelay={delay_ms}|{delay_ms},volume=.78[outro];"
        f"[base][outro]amix=inputs=2:duration=longest:normalize=0,"
        f"atrim=0:{target_duration:.6f},alimiter=limit=.95[aout]"
    )
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(VIDEO_ONLY), "-i", str(MIX), "-i", str(OUTRO_SFX),
        "-filter_complex", audio_filter,
        "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2",
        "-t", f"{target_duration:.6f}", "-movflags", "+faststart", str(OUTPUT),
    ])
    print(f"Final: {OUTPUT}")


def qa(shots: list[dict]) -> None:
    errors = []
    for index, shot in enumerate(shots):
        path = SEGMENTS / f"{index + 1:03d}_{shot['shot_id']}.mp4"
        if not path.is_file():
            errors.append(f"missing {path.name}")
            continue
        measured = duration(path)
        if abs(measured - shot["duration"]) > .06:
            errors.append(f"duration {path.name} {measured:.3f}/{shot['duration']:.3f}")
    probe = json.loads(run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(OUTPUT),
    ], True)) if OUTPUT.is_file() else {}
    streams = probe.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), {})
    final_duration = float(probe.get("format", {}).get("duration", 0.0) or 0.0)
    expected = round(shots[-1]["end_frame"] / FPS, 6)
    if abs(final_duration - expected) > .08:
        errors.append(f"final duration {final_duration:.3f}/{expected:.3f}")
    if video.get("width") != 1920 or video.get("height") != 1080 or video.get("r_frame_rate") != "30/1":
        errors.append(f"video format {video}")
    if audio.get("sample_rate") != "48000" or audio.get("channels") != 2:
        errors.append(f"audio format {audio}")
    qa_report = {
        "episode": "EP04A", "status": "PASS" if not errors else "FAIL",
        "cue_count": len({shot["cue_id"] for shot in shots}), "shot_count": len(shots),
        "video_clip_count": sum(shot["kind"] == "VIDEO" for shot in shots),
        "duration_seconds": final_duration, "expected_seconds": expected,
        "video": video, "audio": audio, "errors": errors,
    }
    (FINAL / "EP04A_FINAL_QA_V2.json").write_text(
        json.dumps(qa_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"QA: {qa_report['status']} ({len(errors)} errors)")
    if errors:
        raise SystemExit("; ".join(errors[:10]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="all", choices=["plan", "render", "mix", "assemble", "qa", "all"])
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    shots = build_timeline()
    if args.command == "plan":
        return 0
    if args.command in {"render", "all"}:
        render_segments(shots, max(1, min(4, args.workers)))
    if args.command in {"mix", "all"}:
        mix_audio()
    if args.command in {"assemble", "all"}:
        assemble(shots)
    if args.command in {"qa", "all"}:
        qa(shots)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
