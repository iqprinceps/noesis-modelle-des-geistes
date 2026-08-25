#!/usr/bin/env python3
"""Generate the complete EP04A/EP04B Jung-Kundalini V5 still package.

The script parses the canonical NanoBanana prompt documents, resolves only the
named local references, and renders 2K 16:9 images with Vertex AI
``gemini-3-pro-image`` (Nano Banana Pro). Outputs land in a raw QA folder first.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures as futures
import hashlib
import json
import mimetypes
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SERIES_ROOT = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1"
RAW_ROOT = SERIES_ROOT / "00_RAW_VERTEX"
FINAL_ROOT = SERIES_ROOT / "FINAL_STILLS"
REFERENCE_ROOT = SERIES_ROOT / "REFERENCES_EP04AB"
STYLE_ROOT = ROOT / "05_GENERATED" / "EP04_JUNG_CHAKREN" / "STYLE_REFERENCES"
MODEL = "gemini-3-pro-image"
LOCATION = "global"

PROMPT_DOCS = {
    "EP04A": [
        ROOT / "PRODUCTION_SUMMARY" / "EP04A_JUNG_KUNDALINI_V5" / "NANOBANANA_PROMPTS_V5_S1_S3.md",
        ROOT / "PRODUCTION_SUMMARY" / "EP04A_JUNG_KUNDALINI_V5" / "NANOBANANA_PROMPTS_V5_S4_S6.md",
        ROOT / "PRODUCTION_SUMMARY" / "EP04A_JUNG_KUNDALINI_V5" / "NANOBANANA_PROMPTS_V5_S7_S8.md",
    ],
    "EP04B": [
        ROOT / "PRODUCTION_SUMMARY" / "EP04B_CHAKRA_GENEALOGIE_V5" / "NANOBANANA_PROMPTS_V5_S1_S4.md",
        ROOT / "PRODUCTION_SUMMARY" / "EP04B_CHAKRA_GENEALOGIE_V5" / "NANOBANANA_PROMPTS_V5_S5_S8.md",
    ],
}

EXPECTED = {"EP04A": {"MAIN": 44, "RESERVE": 8}, "EP04B": {"MAIN": 20, "RESERVE": 4}}

# Generated anchors are added only to keep recurring visual objects coherent.
DEPENDENCIES = {
    "EP04A_IMG005_JUNG_BEFORE_UNKNOWN_MAP.png": ["EP04A_IMG002_JUNG_WARNING_RECON.png"],
    "EP04A_IMG006_TRAIN_1913_NORMAL.png": ["EP04A_IMG002_JUNG_WARNING_RECON.png"],
    "EP04A_IMG007_TRAIN_YELLOW_FLOOD.png": ["EP04A_IMG006_TRAIN_1913_NORMAL.png"],
    "EP04A_IMG009_JUNG_TRAIN_REACTION.png": [
        "EP04A_IMG002_JUNG_WARNING_RECON.png",
        "EP04A_IMG006_TRAIN_1913_NORMAL.png",
    ],
    "EP04A_IMG015_CAVE_WIDE.png": ["EP04A_IMG004_RED_SUN_UNDER_WATER_FLASH.png"],
    "EP04A_IMG016_BEETLE_RED_SUN_MACRO.png": [
        "EP04A_IMG004_RED_SUN_UNDER_WATER_FLASH.png",
        "EP04A_IMG015_CAVE_WIDE.png",
    ],
    "EP04A_IMG017_CORPSE_DISTANT_WATER.png": ["EP04A_IMG015_CAVE_WIDE.png"],
    "EP04A_IMG018_BLACK_SNAKE_CAVE_WIDE.png": [
        "EP04A_IMG003_BLACK_SNAKE_HOOK.png",
        "EP04A_IMG015_CAVE_WIDE.png",
    ],
    "EP04A_IMG021_SEMINAR_RETURN_ANONYMOUS.png": ["EP04A_IMG001_SEMINAR_ROOM_WIDE.png"],
    "EP04A_IMG022_SEMINAR_JUNG_HAND_POINTER.png": [
        "EP04A_IMG001_SEMINAR_ROOM_WIDE.png",
        "EP04A_IMG002_JUNG_WARNING_RECON.png",
    ],
    "EP04A_IMG030_CONVERSATION_AFFECT_SHIFT.png": ["EP04A_IMG029_CONVERSATION_BEFORE_TURN.png"],
    "EP04A_IMG031_SUBJECTIVE_COMPRESSION.png": ["EP04A_IMG029_CONVERSATION_BEFORE_TURN.png"],
    "EP04A_IMG032_ANAHATA_BREATH_OPEN.png": ["EP04A_IMG029_CONVERSATION_BEFORE_TURN.png"],
    "EP04A_IMG033_OBSERVER_STEP_BACK.png": ["EP04A_IMG029_CONVERSATION_BEFORE_TURN.png"],
    "EP04A_IMG035_BODY_REACTION_SEQUENCE_STILL.png": ["EP04A_IMG034_PHONE_NAME_ONLY.png"],
    "EP04A_IMG036_REPLY_FORMING_UNREADABLE.png": ["EP04A_IMG034_PHONE_NAME_ONLY.png"],
    "EP04A_IMG037_TWO_SECOND_HOVER.png": ["EP04A_IMG034_PHONE_NAME_ONLY.png"],
    "EP04A_IMG038_RELEASE_PULLBACK.png": [
        "EP04A_IMG034_PHONE_NAME_ONLY.png",
        "EP04A_IMG035_BODY_REACTION_SEQUENCE_STILL.png",
    ],
    "EP04A_IMG043_BLACK_SNAKE_RESIDUE.png": [
        "EP04A_IMG003_BLACK_SNAKE_HOOK.png",
        "EP04A_IMG015_CAVE_WIDE.png",
    ],
    "EP04A_IMG044_INNER_MAP_INTEGRATION.png": ["EP04A_IMG015_CAVE_WIDE.png"],
    "EP04A_RSV01_CAVE_WATER_DETAIL.png": ["EP04A_IMG015_CAVE_WIDE.png"],
    "EP04A_RSV08_BLACK_WATER_CLOSE.png": ["EP04A_IMG015_CAVE_WIDE.png"],
    "EP04B_IMG002_RAINBOW_LAYER_PEEL.png": ["EP04B_IMG001_MODERN_RAINBOW_MAP.png"],
    "EP04B_IMG003_MODERN_POSTER_IN_ROOM.png": ["EP04B_IMG001_MODERN_RAINBOW_MAP.png"],
    "EP04B_IMG015_MODERN_SPECTRUM_INTERFACE.png": ["EP04B_IMG001_MODERN_RAINBOW_MAP.png"],
    "EP04B_IMG018_MAP_ABSORBS_CONTEXTS.png": ["EP04B_IMG001_MODERN_RAINBOW_MAP.png"],
    "EP04B_IMG019_SEAMS_SIDE_VIEW.png": ["EP04B_IMG001_MODERN_RAINBOW_MAP.png"],
    "EP04B_IMG020_FINAL_HEADON_AND_SEAMS.png": [
        "EP04B_IMG001_MODERN_RAINBOW_MAP.png",
        "EP04B_IMG019_SEAMS_SIDE_VIEW.png",
    ],
}

THUMBNAILS = [
    {
        "episode": "EP04A",
        "kind": "THUMBNAIL",
        "name": "EP04A_THUMB_JUNG_SCHLANGE.png",
        "references": ["STYLE_CONCEPTUAL.png", "EP04A_Jung_portrait_PD.jpg"],
        "prompt": (
            "Create a high-impact 16:9 YouTube documentary thumbnail composition for a German investigative "
            "episode about C. G. Jung, Kundalini and a recurring black-snake motif. Use the authentic Jung portrait "
            "only to preserve recognizable identity. Jung is the dominant left/center focal point, serious and "
            "intellectually alert. From graphite darkness on the opposite side, a natural matte-black snake curves "
            "into frame as a subjective motif, not a monster and not in a religious Kundalini pose. Preserve a clean "
            "paper-texture zone separated by a visible edge for a later real historical source composite. Strong "
            "small-size readability, crisp separation, deep blue-black and graphite, restrained warm paper accent, "
            "subtle film grain. No built-in text, glowing chakras, aura, Red Book imitation, magical energy, fake "
            "archive scan or watermark."
        ),
    },
    {
        "episode": "EP04B",
        "kind": "THUMBNAIL",
        "name": "EP04B_THUMB_MODERN_MAP_BASE.png",
        "references": ["STYLE_INFOGRAPHIC.png"],
        "prompt": (
            "Create a high-impact 16:9 YouTube documentary thumbnail base for a German historical investigation "
            "into how the modern seven-rainbow chakra map developed. On the left, show a crisp contemporary vertical "
            "sequence of exactly seven simple colored circles in visible-spectrum order on a neutral dark human "
            "silhouette or poster-like field. On the right, leave a strong clean archival-paper zone with a visible "
            "physical seam and enough contrast for a real historical six-center artwork to be composited later. "
            "The composition must read at very small size. Deep graphite background, restrained warm paper, clean "
            "spectrum color only on the modern side, crisp separation, subtle texture. No built-in text, fake old "
            "art, Sanskrit, deities, aura, fake stamp or watermark."
        ),
    },
]

GLOBAL_LOCK = """Generate exactly one finished 2K landscape documentary still in 16:9.
The supplied images are references, not edit targets. Keep natural lifted midtones and visible shadow detail.
Human anatomy must be plausible with correct hands and no duplicate limbs or people.
No captions, labels, subtitles, logos, signatures, watermarks, invented interface words or decorative typography.
No fake historical document, fake quotation, mystical neon, occult clutter, CGI sheen or plastic skin.
Historical reconstructions must look cinematic and honest, never like counterfeit archive evidence.
Preserve editor-friendly negative space where requested. Follow every scene-specific constraint literally."""

PROMPT_REFINEMENTS = {
    "EP04A_IMG002_JUNG_WARNING_RECON.png": (
        "Identity correction: the lecturer is unmistakably C. G. Jung at about age 57 in 1932. Match the supplied "
        "portrait's facial geometry, high forehead, hairline, eye spacing, nose, compact moustache, jaw and thin "
        "round spectacles. Do not substitute a generic professor. Keep a natural documentary likeness, not a "
        "waxwork or face-swap look. He holds exactly one wooden pointer in his right hand; his left hand is empty. "
        "No second pointer, cane, duplicate object or extra hand."
    ),
    "EP04A_IMG005_JUNG_BEFORE_UNKNOWN_MAP.png": (
        "Identity correction: preserve the supplied portrait's unmistakable C. G. Jung facial structure at his "
        "historically appropriate 1932 age. No generic bespectacled professor and no altered moustache, jaw or "
        "hairline. The map contains no readable invented writing or pseudo-historical diagrams."
    ),
    "EP04A_IMG006_TRAIN_1913_NORMAL.png": (
        "Age and identity correction: this is C. G. Jung in 1913 at about age 38, not an elderly man. Preserve the "
        "supplied portrait's recognizable facial geometry while making him naturally younger. Establish this exact "
        "person, suit and train compartment as the continuity anchor for the reaction shot. Do not include a "
        "newspaper, timetable, ticket, station sign, printed notice or any readable or pseudo-readable characters."
    ),
    "EP04A_IMG009_JUNG_TRAIN_REACTION.png": (
        "Continuity correction: show the exact same younger C. G. Jung, suit, seat, window and train compartment as "
        "the supplied generated train anchor. Do not change face, age, wardrobe, camera side or carriage design."
    ),
    "EP04A_IMG020_PHILEMON_DISTANCE.png": (
        "Mandatory replacement of fantasy elements: show no physical horns and no literal wings anywhere in the "
        "image. His headwear is a simple soft folded cloth cap whose silhouette is only faintly unusual; it must not "
        "resemble a Viking, ram, demon or helmet. A narrow muted kingfisher-blue scarf or cloak edge behind one "
        "shoulder provides the entire wing association—no feathers, wing anatomy or paired shapes. He remains a "
        "distant materially human elderly man in plain cloth, not a fantasy character."
    ),
    "EP04A_IMG022_SEMINAR_JUNG_HAND_POINTER.png": (
        "Strict identity and evidence correction: reproduce the SAME 1932 Carl Jung seen in the supplied generated "
        "Jung anchor—same older age, receding grey hair, round wire glasses, moustache, facial geometry, black "
        "three-piece suit and white shirt. This must look like a later angle from the same seminar, not another actor "
        "or a younger lecturer. Preserve the room anchor. The entire tabletop is bare polished wood: no papers, "
        "pages, charts, folders, books, labels or marks anywhere. The flip chart is completely blank. He holds the "
        "same single plain wooden pointer used in the anchor; no second pointer or writing tool."
    ),
    "EP04A_IMG010_CLINICAL_GROUNDING_DESK.png": (
        "Text-safety correction: show only blank reverse sides of papers, closed neutral folders and the period "
        "stopwatch-like equipment. No handwriting, diagrams, labels, digits, graph marks, table cells, letter-like "
        "strokes or pseudo-readable data anywhere. The factual reference informs period materials but is not copied "
        "or reinvented in the visible frame. Keep the clinician anonymous and the desk methodical."
    ),
    "EP04A_IMG039_LONDON_PRINT_PROCESS_1919.png": (
        "Text-safety correction: all paper must be blank, folded, face-down or too shallow-focus to contain any "
        "visible characters. No open printed pages, type proofs, title fragments, letter-like marks or pseudo-text. "
        "Explain printing through type cases, roller, binding hands and stacks of cream paper only."
    ),
    "EP04A_IMG041_MAP_TRAVEL_DESK.png": (
        "Human editorial correction: remove every connecting thread, string, pin, arrow and conspiracy-board cue. "
        "Compose three quiet material groups separated naturally by empty wooden desk space: one closed plain "
        "South-Asian-style folio, one closed British clothbound book, and one stack of blank European seminar paper. "
        "All surfaces are completely free of letters, pseudo-writing, dates, diagrams, Sanskrit and symbols. The "
        "relationship is communicated by spatial progression and changing material, not explicit connectors."
    ),
    "EP04A_IMG025_INNER_GRAVITY_ROOM.png": (
        "Intensity correction: keep the scene psychologically plausible and physically grounded. "
        "Show no loose papers anywhere in the image—none on desk, chair, floor or air—so nothing can appear airborne. "
        "No floating furniture, objects, clothing or hair. All visible objects remain supported by the floor or table; "
        "suggest inner gravity only through a barely perceptible camera cant, posture, framing and directional light. "
        "This is subtle subjective pressure, not telekinesis or a supernatural event."
    ),
    "EP04A_IMG028_MANIPURA_BODY_MACRO.png": (
        "Reaction correction: all three micro-reactions must be visibly readable in one naturalistic frame: fingers "
        "tighten against the chair, jaw muscles set in profile, and the upper chest visibly lifts beneath ordinary "
        "clothing. Keep exactly two hands and two arms; no collage borders, labels or anatomical graphics. Absolutely "
        "no smoke, vapor, flame, glow, heat haze, aura or colored effect around the chest—the rising fabric and posture "
        "alone show the breath."
    ),
    "EP04A_IMG030_CONVERSATION_AFFECT_SHIFT.png": (
        "Continuity correction: this is the very next moment with the exact same two adults, clothing, table, chairs, "
        "room, lamps, window, time of day and camera side as the supplied conversation anchor. The shift is subtle: "
        "slightly tense fingers and shoulders, no shouting, accusation, historical costume or third person."
    ),
    "EP04A_IMG031_SUBJECTIVE_COMPRESSION.png": (
        "Continuity and anatomy correction: use the exact same adult, clothing and room from the conversation anchor. "
        "The person has exactly two arms and two hands with no ghost limbs, duplicate body, reflection double or "
        "period change. Compression comes only from lens, darkness at the edges and closer framing."
    ),
    "EP04A_IMG032_ANAHATA_BREATH_OPEN.png": (
        "Continuity correction: use the exact same adult, clothing, chair, table, room, window and practical lamps as "
        "the conversation anchor. Do not invent a new apartment or solitary character. Show release through lower "
        "shoulders, more surrounding space and camera distance only."
    ),
    "EP04A_IMG033_OBSERVER_STEP_BACK.png": (
        "Continuity correction: use the exact same adult, clothing and contemporary room as the conversation anchor. "
        "Keep one physically plausible person; the near shoulder and distant view are created by reflection or "
        "doorway perspective, not a ghost, clone or historical interior."
    ),
    "EP04A_IMG034_PHONE_NAME_ONLY.png": (
        "Interface correction: the device is a truly generic unbranded black-glass smartphone. The display contains "
        "only soft neutral rectangles and one blurred sender area—no Apple/iPhone/iMessage appearance, no recognizable "
        "icons, no keyboard letters, no readable UI words and no logo. Establish this exact hand, sleeve, phone and "
        "evening room as continuity anchors."
    ),
    "EP04A_IMG035_BODY_REACTION_SEQUENCE_STILL.png": (
        "Object correction: the phone is the same generic modern black glass smartphone established in the "
        "preceding shot, held in one hand. Do not show a landline handset, coiled cord, desk telephone or vintage "
        "receiver. Preserve the three micro-reactions in one continuous naturalistic composition."
    ),
    "EP04A_IMG036_REPLY_FORMING_UNREADABLE.png": (
        "Interface and continuity correction: preserve the exact generic phone, hand, sleeve and room from the "
        "supplied anchor. The keyboard is an abstract defocused grid with no recognizable letters, numbers, icons, "
        "brand conventions or readable characters anywhere."
    ),
    "EP04A_IMG037_TWO_SECOND_HOVER.png": (
        "Continuity correction: preserve the exact same generic phone, hand, sleeve, skin tone, lighting and room as "
        "the supplied anchor. The send area is only an abstract neutral shape, not a recognizable app button."
    ),
    "EP04A_IMG038_RELEASE_PULLBACK.png": (
        "Continuity correction: reveal the exact same anonymous adult, sleeve, phone and evening room established by "
        "the two supplied generated anchors. The same unbranded smartphone is visibly lowered in one hand. No new "
        "person, apartment, era or device."
    ),
    "EP04B_IMG006_SIX_PLUS_ABOVE_BASE.png": (
        "Human editorial correction: avoid a technical infographic, HUD, dashboard, tile system, wiring diagram, "
        "nested boxes or connector maze. Use one tactile warm paper sheet with EXACTLY SEVEN circle marks total: "
        "EXACTLY SIX lightly hand-drawn neutral circles below one horizontal divider, stacked in a vertical rhythm, "
        "and EXACTLY ONE seventh circle above that divider. Count carefully: six below plus one above, no missing "
        "circle and no additional circles anywhere. Slight graphite irregularity and real paper fibers should make "
        "it feel composed by a human editor while remaining clear and contemporary."
    ),
    "EP04B_IMG007_LONDON_PRINT_SHOP_1919.png": (
        "Composition correction: show one continuous wide-angle documentary reconstruction of a single print shop "
        "at one moment. No collage, montage, contact sheet, split screen, grid, repeated hands or tiled vignettes. "
        "Use foreground type case, midground binding hands and background press to explain the process through depth."
    ),
    "EP04B_IMG020_FINAL_HEADON_AND_SEAMS.png": (
        "Continuity correction: the TOP sheet must unmistakably show the same contemporary minimal seven-circle "
        "body map as the supplied modern-map anchor: exactly seven plain solid circles, simple modern silhouette, "
        "clean restrained spectrum colors, no chakra glyphs, no lotus ornaments, no Sanskrit and no manuscript "
        "drawing on the top layer. Keep the camera mostly head-on. Only along the right-hand edge may several older "
        "paper and acetate layers peek out as tactile seams; those lower layers contain no readable text or invented "
        "symbols. The message is a usable modern image whose construction history remains visible."
    ),
    "EP04B_RSV03_MODERN_BOOKSHELF_WELLNESS.png": (
        "Text-safety correction: show a contemporary studio shelf with plain solid-color cloth and paper book spines "
        "that are completely blank. Absolutely no letters, words, title fragments, logos, numbers, pseudo-writing or "
        "typographic marks anywhere. Turn most spines slightly away and keep them softly out of focus. A small clear "
        "seven-color abstract card may provide the wellness context without any writing or branded cover design."
    ),
}


_token_cache: dict[str, Any] = {}
_token_lock = threading.Lock()
_log_lock = threading.Lock()


def access_token() -> str:
    now = time.time()
    with _token_lock:
        if _token_cache.get("expires", 0) > now + 60:
            return str(_token_cache["value"])
        gcloud = os.environ.get(
            "GCLOUD_CMD",
            r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
        )
        command = [gcloud if Path(gcloud).exists() else "gcloud", "auth", "application-default", "print-access-token"]
        result = subprocess.run(command, check=True, capture_output=True, text=True, shell=True, timeout=60)
        value = result.stdout.strip()
        if not value:
            raise RuntimeError("No ADC access token. Run: gcloud auth application-default login")
        _token_cache.update(value=value, expires=now + 3300)
        return value


def project_id() -> str:
    value = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not value:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set")
    return value


def parse_prompt_document(path: Path, episode: str) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    pattern = re.compile(
        rf"(?ms)^({episode}_(?:IMG\d{{3}}|RSV\d{{2}})_[^\r\n]+\.png)\s*\r?\n"
        r"Referenz:\s*([^\r\n]+)\s*\r?\nPrompt:\s*\r?\n"
        rf"(.+?)(?=\r?\n\r?\n(?:{episode}_(?:IMG\d{{3}}|RSV\d{{2}})_|---)|\Z)"
    )
    jobs = []
    for name, refs_text, prompt in pattern.findall(text):
        refs = [item.strip() for item in refs_text.split(";") if item.strip() and item.strip().lower() != "keine"]
        jobs.append(
            {
                "episode": episode,
                "kind": "MAIN" if "_IMG" in name else "RESERVE",
                "name": name.strip(),
                "references": refs,
                "prompt": prompt.strip(),
                "source": str(path.relative_to(ROOT)),
            }
        )
    return jobs


def load_jobs(include_thumbnails: bool = False) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for episode, paths in PROMPT_DOCS.items():
        for path in paths:
            jobs.extend(parse_prompt_document(path, episode))
    names = [job["name"] for job in jobs]
    if len(names) != len(set(names)):
        raise RuntimeError("Duplicate output filename in canonical prompt documents")
    for episode, expected in EXPECTED.items():
        for kind, count in expected.items():
            actual = sum(job["episode"] == episode and job["kind"] == kind for job in jobs)
            if actual != count:
                raise RuntimeError(f"{episode} {kind}: expected {count}, parsed {actual}")
    if include_thumbnails:
        jobs.extend(THUMBNAILS)
    return jobs


def reference_index() -> dict[str, Path]:
    paths = [path for path in REFERENCE_ROOT.rglob("*") if path.is_file()]
    paths.extend(path for path in STYLE_ROOT.glob("*") if path.is_file())
    index: dict[str, Path] = {}
    duplicates: dict[str, list[Path]] = {}
    for path in paths:
        if path.name in index and index[path.name] != path:
            duplicates.setdefault(path.name, [index[path.name]]).append(path)
        else:
            index[path.name] = path
    if duplicates:
        detail = "; ".join(f"{name}: {items}" for name, items in duplicates.items())
        raise RuntimeError(f"Ambiguous reference filenames: {detail}")
    return index


def output_path(job: dict[str, Any]) -> Path:
    return RAW_ROOT / job["episode"] / job["kind"] / job["name"]


def dependency_paths(job: dict[str, Any]) -> list[Path]:
    return [RAW_ROOT / job["episode"] / "MAIN" / name for name in DEPENDENCIES.get(job["name"], [])]


def mime_type(path: Path) -> str:
    guessed = mimetypes.guess_type(path.name)[0]
    return guessed or "image/png"


def image_part(path: Path) -> dict[str, Any]:
    return {
        "inlineData": {
            "mimeType": mime_type(path),
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


def role_for_reference(name: str, number: int) -> str:
    if name.startswith("STYLE_"):
        return (
            f"Image {number} ({name}) is a style reference only. Match restrained palette, documentary lighting, "
            "texture and tonal readability; do not copy its people, objects or composition."
        )
    if "Jung_portrait" in name:
        return (
            f"Image {number} ({name}) is an authentic identity reference for C. G. Jung only. Preserve recognizable "
            "adult facial identity without copying pose, background or photographic damage."
        )
    return (
        f"Image {number} ({name}) is a factual historical/object reference. Use only as requested; do not redraw, "
        "rewrite, beautify or invent content inside it."
    )


def request_parts(job: dict[str, Any], refs: dict[str, Path]) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    roles: list[str] = []
    number = 1
    for name in job["references"]:
        path = refs.get(name)
        if path is None or not path.is_file():
            raise FileNotFoundError(f"Missing named reference for {job['name']}: {name}")
        parts.append(image_part(path))
        roles.append(role_for_reference(name, number))
        number += 1
    for path in dependency_paths(job):
        if not path.is_file():
            raise FileNotFoundError(f"Missing generated continuity anchor for {job['name']}: {path.name}")
        parts.append(image_part(path))
        roles.append(
            f"Image {number} ({path.name}) is a generated continuity anchor. Preserve only the recurring subject's "
            "design, materials, palette and physical proportions while following the new composition literally."
        )
        number += 1
    text = (
        "Use case: historical-scene / conceptual documentary still\n"
        "Asset type: German YouTube documentary series shot\n"
        + ("Input images:\n" + "\n".join(roles) + "\n" if roles else "")
        + f"Primary request:\n{job['prompt']}\n"
        + (f"\nShot-specific correction:\n{PROMPT_REFINEMENTS[job['name']]}\n" if job["name"] in PROMPT_REFINEMENTS else "")
        + f"\n{GLOBAL_LOCK}"
    )
    parts.append({"text": text})
    return parts


def post_json(url: str, payload: dict[str, Any], attempts: int = 8) -> dict[str, Any]:
    waits = [8, 15, 30, 45, 60, 90, 120]
    last_error: Exception | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=420) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:1200]
            last_error = RuntimeError(f"HTTP {exc.code}: {body}")
            if exc.code not in {429, 500, 502, 503, 504} or attempt == attempts - 1:
                raise last_error from None
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == attempts - 1:
                raise
        wait = waits[min(attempt, len(waits) - 1)]
        print(f"  retry in {wait}s ({attempt + 2}/{attempts}): {last_error}", flush=True)
        time.sleep(wait)
    raise RuntimeError(f"generation failed: {last_error}")


def generate(job: dict[str, Any], refs: dict[str, Path], overwrite: bool) -> dict[str, Any]:
    destination = output_path(job)
    if destination.is_file() and not overwrite:
        with Image.open(destination) as image:
            return {"status": "SKIPPED", "width": image.width, "height": image.height, "bytes": destination.stat().st_size}
    payload = {
        "contents": [{"role": "user", "parts": request_parts(job, refs)}],
        "generationConfig": {
            "candidateCount": 1,
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"},
        },
    }
    url = (
        f"https://aiplatform.googleapis.com/v1/projects/{project_id()}/locations/{LOCATION}/"
        f"publishers/google/models/{MODEL}:generateContent"
    )
    response = post_json(url, payload)
    image_bytes: bytes | None = None
    for candidate in response.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                image_bytes = base64.b64decode(inline["data"])
                break
        if image_bytes:
            break
    if not image_bytes:
        finish = (response.get("candidates") or [{}])[0].get("finishReason", "unknown")
        raise RuntimeError(f"No image returned (finishReason={finish})")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(image_bytes)
    with Image.open(destination) as image:
        width, height = image.size
        image.verify()
    return {
        "status": "GENERATED",
        "width": width,
        "height": height,
        "bytes": destination.stat().st_size,
        "sha256": hashlib.sha256(image_bytes).hexdigest(),
    }


def append_log(record: dict[str, Any]) -> None:
    SERIES_ROOT.mkdir(parents=True, exist_ok=True)
    path = SERIES_ROOT / "vertex_generation_log.jsonl"
    with _log_lock, path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_stage(jobs: list[dict[str, Any]], refs: dict[str, Path], workers: int, overwrite: bool) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    with futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        future_map = {pool.submit(generate, job, refs, overwrite): job for job in jobs}
        for future in futures.as_completed(future_map):
            job = future_map[future]
            try:
                result = future.result()
                record = {"timestamp": time.time(), "model": MODEL, "name": job["name"], **result}
                append_log(record)
                print(
                    f"{result['status']:9s} {job['name']} {result['width']}x{result['height']} "
                    f"{result['bytes']} bytes",
                    flush=True,
                )
            except Exception as exc:  # noqa: BLE001
                failures.append({"name": job["name"], "error": str(exc)})
                append_log({"timestamp": time.time(), "model": MODEL, "name": job["name"], "status": "FAILED", "error": str(exc)})
                print(f"FAILED    {job['name']}: {exc}", flush=True)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", choices=["EP04A", "EP04B", "ALL"], default="ALL")
    parser.add_argument("--kind", choices=["MAIN", "RESERVE", "THUMBNAIL", "ALL"], default="ALL")
    parser.add_argument("--only", default="", help="Comma-separated exact filenames or filename stems")
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--include-thumbnails", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    jobs = load_jobs(include_thumbnails=args.include_thumbnails)
    if args.episode != "ALL":
        jobs = [job for job in jobs if job["episode"] == args.episode]
    if args.kind != "ALL":
        jobs = [job for job in jobs if job["kind"] == args.kind]
    if args.only:
        wanted = {item.strip() for item in args.only.split(",") if item.strip()}
        jobs = [job for job in jobs if job["name"] in wanted or Path(job["name"]).stem in wanted]
    if not jobs:
        raise SystemExit("No matching generation jobs")

    refs = reference_index()
    missing = sorted({name for job in jobs for name in job["references"] if name not in refs})
    if missing:
        raise SystemExit("Missing reference files: " + ", ".join(missing))
    if args.list:
        for index, job in enumerate(jobs, 1):
            deps = DEPENDENCIES.get(job["name"], [])
            print(f"{index:03d} {job['episode']} {job['kind']:9s} {job['name']} refs={len(job['references'])} deps={len(deps)}")
        return 0

    print(f"Model={MODEL} location={LOCATION} project={project_id()} jobs={len(jobs)} workers={args.jobs}")
    remaining = {job["name"]: job for job in jobs}
    selected_names = set(remaining)
    failures: list[dict[str, str]] = []
    while remaining:
        ready = []
        for job in remaining.values():
            deps = DEPENDENCIES.get(job["name"], [])
            if all(
                (RAW_ROOT / job["episode"] / "MAIN" / name).is_file()
                or name not in selected_names
                for name in deps
            ):
                ready.append(job)
        if not ready:
            unresolved = {name: DEPENDENCIES.get(name, []) for name in remaining}
            raise RuntimeError(f"Unresolved generation dependency: {unresolved}")
        print(f"STAGE ready={len(ready)} remaining={len(remaining)}", flush=True)
        stage_failures = run_stage(ready, refs, args.jobs, args.overwrite)
        failed_names = {item["name"] for item in stage_failures}
        failures.extend(stage_failures)
        for job in ready:
            remaining.pop(job["name"], None)
        if failed_names:
            blocked = [
                name for name, job in remaining.items() if any(dep in failed_names for dep in DEPENDENCIES.get(job["name"], []))
            ]
            for name in blocked:
                failures.append({"name": name, "error": "blocked by failed continuity anchor"})
                remaining.pop(name, None)

    if failures:
        print(json.dumps({"failures": failures}, ensure_ascii=False, indent=2), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
