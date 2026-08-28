#!/usr/bin/env python3
"""Resolve EP01's locked linear picture states and write production manifests."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV"
CUE_PATH = EP / "06_TIMELINE" / "EP01_EN_VISUAL_CUE_SHEET.csv"
REQUIRED_PATH = EP / "06_TIMELINE" / "EP01_EN_REQUIRED_ASSET_SET.json"
MANIFEST_PATH = EP / "04_ASSETS" / "ASSET_MANIFEST.csv"
SERIES_PATH = ROOT / "07_ENGLISH_PRODUCTION" / "00_GLOBAL" / "SERIES_ASSET_REGISTER.csv"
DETERMINISTIC_MAP_PATH = EP / "04_ASSETS" / "METADATA" / "deterministic_asset_map.json"
SOURCE_MANIFEST_PATH = EP / "04_SOURCES" / "SOURCE_AND_LICENSE_MANIFEST.csv"
GENERATION_METADATA_PATH = EP / "04_ASSETS" / "METADATA" / "SELECTED_GENERATION_METADATA.json"

MANIFEST_FIELDS = [
    "asset_id", "family_id", "asset_type", "status", "file_path", "source_id",
    "provider", "model", "prompt_id", "seed_or_operation", "content_sha256",
    "perceptual_hash", "series_usage", "first_cue", "last_cue",
    "first_start_seconds", "last_end_seconds", "rights_status",
    "visible_mode_badge", "qa_status", "notes",
]
SERIES_FIELDS = [
    "content_sha256", "perceptual_hash", "episode_id", "asset_id",
    "series_usage", "file_path", "registered_utc", "notes",
]

CLIP_FILES = {
    "KZ_CLIP_ROTATION_HOOK": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_ROTATION_HOOK.mp4",
    "KZ_CLIP_ISOLATION_SENSORY_CONTINUOUS": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_ISOLATION_SENSORY_CONTINUOUS.mp4",
    "KZ_CLIP_INTERNAL_TIME_CONTINUOUS": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_INTERNAL_TIME_CONTINUOUS.mp4",
    "KZ_CLIP_DISTANT_IMAGE_CONTINUOUS": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_DISTANT_IMAGE_CONTINUOUS.mp4",
    "KZ_CLIP_EMPTY_SPIRAL_PAYOFF": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_EMPTY_SPIRAL_PAYOFF.mp4",
    "KZ_CLIP_PHYSICAL_VARIABLES_SENSOR_RIG": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PHYSICAL_VARIABLES_SENSOR_RIG.mp4",
    "KZ_CLIP_INFORMATION_BEFORE_REVEAL": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_INFORMATION_BEFORE_REVEAL.mp4",
    "KZ_CLIP_MISSING_EXPERIMENT_VOID": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_MISSING_EXPERIMENT_VOID.mp4",
    "KZ_CLIP_THREE_OBSERVERS_TRANSITION": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_THREE_OBSERVERS_TRANSITION.mp4",
    "KZ_CLIP_PATENT_EVIDENCE_DECONSTRUCTION": "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PATENT_EVIDENCE_DECONSTRUCTION.mp4",
}

NATIVE_OPERATIONS = {
    "KZ_EN_REC02_SEATED_NEUTRAL": "exec-889f",
    "KZ_EN_REC03_PARTICIPANT_REPORT": "exec-6dabe",
    "KZ_EN_REC04_CHAMBER_REVERSE_WIDE": "exec-8f5f",
    "KZ_EN_REC05_SCREWS_MACRO": "exec-d40",
    "KZ_EN_REC18_EMPTY_CHAMBER_A": "exec-856a",
    "KZ_EN_REC18_EMPTY_CHAMBER_B": "exec-1f15",
    "KZ_HERO01_REFLECTION_STATE": "exec-e1a5",
    "KZ_TARGET01_LIGHTHOUSE": "exec-8126",
    "KZ_TARGET02_VIOLIN": "exec-9f8",
    "KZ_TARGET03_BURNING_CAR": "exec-45d",
    "KZ_TARGET04_WHITE_HORSE": "exec-ce6",
}

NATIVE_SUPPORTING = {
    "KZ_INNER01_INTERNAL_TIME_START": "exec-8562",
    "KZ_INNER02_DISTANT_IMAGE_START": "exec-834f",
    "KZ_CLIP_ROTATION_HOOK_START": "exec-2245",
    "KZ_CLIP_ISOLATION_SENSORY_START": "exec-16ef",
    "KZ_CLIP_EMPTY_SPIRAL_PAYOFF_START": "exec-fa38",
}

CLUSTER_BREAK_OPERATIONS = {
    "KZ_PHYSICAL_PANEL_SCALE": "exec-5e8cf91b-ee26-4522-b9dd-bc4551c3bbea",
    "KZ_PHYSICAL_PANEL_ARRAY": "exec-8356808f-e589-4913-840b-e5f4e8f54ad7",
    "KZ_SENSORY_HAND_ON_ALUMINUM": "exec-8d07bf18-0d96-490c-86ef-164d35f68f1a",
    "KZ_OBSERVER_DISTANCE_REFLECTION": "exec-7951da13-0ac6-4cc8-9957-6536157f4539",
    "KZ_SUBJECTIVE_REPORT_HAND": "exec-d0046d38-9d7e-453f-beda-2bb77b726260",
    "KZ_PSYCHOLOGY_ISOLATION_BODY": "exec-3f4f49f8-d968-4a95-9514-da70153054d5",
    "KZ_PHYSICAL_MEASUREMENT_CLOSEUP": "exec-add55214-bc93-4a21-9c21-fdf447f30242",
    "KZ_RANDOM_TARGET_SEALED_VAULT": "exec-73239424-1463-48d0-99c0-54c54a520447",
    "KZ_ONLINE_PATENT_AUTHORITY": "exec-8fb2a3a2-fc90-48bb-9afa-4cc56426ef8d",
    "KZ_PATENT_PROVENANCE_DESK": "exec-9219d440-2e60-42e0-b6ae-c413cddaa78e",
    "KZ_EMPTY_RESULT_TRAY": "exec-f29be4b3-df5b-49c9-8d29-7d71d045aeee",
}

EXPERIENTIAL_UPGRADE_OPERATIONS = {
    "KZ_MYSTIC_THEORY_ISOLATION": "exec-27b1face-aee0-4b7c-a831-d2cb86644b73",
    "KZ_PHYSICAL_THEORY_BODY_BOUNDARY": "exec-b125a41e-6fa6-4729-b090-f4ff55bbeb26",
    "KZ_MYSTIC_THEORY_INFORMATION_REFLECTION": "exec-f0d4e496-25c2-41dc-85d7-5d972164be0d",
    "KZ_MYSTIC_TIME_ACTIVE_AFTERIMAGE": "exec-356b3148-3907-41a9-b7a1-f0df3f4bc782",
    "KZ_MYSTIC_THREE_STORIES_COLLAPSE": "exec-cfdc2869-a4a2-4bd7-bee6-538a08577fff",
    "KZ_RESEARCHERS_NIGHT_LAB": "exec-7ab825f7-05e9-49f9-8219-77fc9bd9cebc",
    "KZ_MYSTIC_SEPARATE_THREADS": "exec-59ffcc37-d7bc-4262-9924-1f997aa77e74",
    "KZ_MYSTIC_DIRECTION_REFLECTION": "exec-bee68965-0833-4830-894e-1531258d3d3a",
    "KZ_MYSTIC_LUNAR_REFLECTION": "exec-35ca6414-8231-41df-a607-91cb299af1d3",
    "KZ_MYSTIC_INTERNAL_TIME_REFRACTION": "exec-6e314415-0776-4260-bd96-b85e2a28396b",
    "KZ_MYSTIC_MEASURABLE_NOT_TRAVEL": "exec-e4bf9e0c-f155-41a1-8720-6aa45d5c51cf",
    "KZ_MYSTIC_EXTRAORDINARY_POSSIBILITY": "exec-81534dc4-34fd-4efa-9edd-ed8f150e360b",
    "KZ_INFO_BEFORE_REVEAL_START": "exec-679d6328-185b-4d4d-940b-6cf535ddc575",
    "KZ_MYSTIC_THEORIES_FORCED_APART": "exec-cb93dfa4-5b42-4030-9f25-a806a7ecff9f",
    "KZ_MISSING_EXPERIMENT_VOID_START": "exec-1d63231c-d97a-4e3b-9ece-eef5b4c362dd",
    "KZ_MYSTIC_DECISIVE_INFORMATION_QUESTION": "exec-d5e7bd4a-e420-42d1-9108-b2a149cf4a0f",
    "KZ_MYSTIC_RESULT_STILL_MISSING": "exec-d75e912a-a6c3-4164-acda-113ab1fbe075",
    "KZ_THREE_OBSERVERS_TRANSITION_START": "exec-67d87189-cb92-4410-837d-1399427ee4af",
}

FINAL_REPAIR_OPERATIONS = {
    "KZ_FILM_LUNAR_STORM_SESSION": "exec-feb79d77-1d1c-492e-a472-4668688821a1",
    "KZ_FILM_ALUMINUM_SURFACE_MACRO": "exec-317ca4b3-df2e-444d-b2ec-5426d0c11bf8",
    "KZ_FILM_HELIOGEOPHYSICAL_CHAMBER": "exec-cef68b31-4fa8-45ce-885d-f7afcfe6ac4e",
    "KZ_FILM_PATENT_AUTHORITY_LIGHTTABLE": "exec-f36507fc-f5b0-4d4f-a7fb-9f15d8c25a09",
    "KZ_MYSTIC_CLAIMS_TRIAD": "exec-25704cd5-833b-4d29-a1d8-778311f20ff1",
    "KZ_MYSTIC_INTENSE_EXPERIENCE_HISTORY": "exec-5182cbea-982c-4448-a961-14b88323312d",
}

DOCUMENT_SOURCES = {
    "KZ_DOC_002": "KZ-SRC-001", "KZ_DOC_016": "KZ-SRC-001",
    "KZ_DOC_030": "KZ-SRC-001", "KZ_DOC_031": "KZ-SRC-001", "KZ_DOC_032": "KZ-SRC-001",
    "KZ_DOC_013": "KZ-SRC-007", "KZ_DOC_028": "KZ-SRC-007",
    "KZ_DOC_014": "KZ-SRC-006", "KZ_DOC_029": "KZ-SRC-006",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dhash64_image(path: Path) -> str:
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())
    value = 0
    for y in range(8):
        for x in range(8):
            value = (value << 1) | int(pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return f"{value:016x}"


def dhash64_video_start(path: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="ep01_manifest_") as folder:
        frame = Path(folder) / "start.png"
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path), "-frames:v", "1", str(frame)],
            check=True,
        )
        return dhash64_image(frame)


def relative(path: Path) -> str:
    return path.relative_to(EP).as_posix()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def resolve_state(state: str, deterministic: dict[str, dict], selected_path: str = "") -> tuple[Path, str, str, str, str, str]:
    """Return path, source, provider, model, prompt id, operation."""
    direct = EP / selected_path if selected_path else None
    if direct and direct.is_file():
        normalized = selected_path.replace("\\", "/")
        if "/DOCUMENT_EVIDENCE/" in f"/{normalized}":
            return direct, DOCUMENT_SOURCES.get(state, "KZ-SRC-001"), "LOCAL_DOCUMENT_EVIDENCE", "Original-source raster compositor", f"{state}_EXACT_EVIDENCE_V1", "deterministic-document-build-v1"
        if "/FINAL_DOCUMENT_TIMELINE/" in f"/{normalized}":
            return direct, "KZ-SRC-001", "LOCAL_DETERMINISTIC_PIL", "Pillow source-faithful compositor", f"{state}_SOURCE_FIGURE_V1", "deterministic-local-build-v1"
        if "/FINAL_DOCUMENT_REPAIR/" in f"/{normalized}":
            return direct, "", "NATIVE_IMAGEGEN", "OpenAI Native ImageGen", f"{state}_FINAL_REPAIR_V1", FINAL_REPAIR_OPERATIONS[state]
        if "/CONFORMED_25FPS/" in f"/{normalized}":
            return direct, "", "LOCAL_MOTION_CONFORM", "ffmpeg minterpolate 50fps to 25fps", f"{state}_CONFORM_V1", "deterministic-motion-conform-v1"
        if "/LOCAL_PROGRESSIVE/" in f"/{normalized}" and state not in CLIP_FILES:
            return direct, "", "LOCAL_PROGRESSIVE_FFMPEG", "ffmpeg scripted progressive motion", f"{state}_LOCAL_MOTION_V1", "deterministic-local-build-v1"
    if state in CLIP_FILES:
        return (
            EP / CLIP_FILES[state], "", "LOCAL_PROGRESSIVE_FFMPEG",
            "ffmpeg scripted progressive motion", f"{state}_LOCAL_MOTION_V1", "deterministic-local-build-v1",
        )
    if state in NATIVE_OPERATIONS:
        return (
            EP / "04_ASSETS" / "GENERATED" / "NATIVE_IMAGEGEN" / f"{state}.png",
            "", "NATIVE_IMAGEGEN", "OpenAI Native ImageGen", f"{state}_V1", NATIVE_OPERATIONS[state],
        )
    if state in CLUSTER_BREAK_OPERATIONS:
        return (
            EP / "04_ASSETS" / "GENERATED" / "NATIVE_IMAGEGEN" / "CLUSTER_BREAKS" / f"{state}.png",
            "", "NATIVE_IMAGEGEN", "OpenAI Native ImageGen", f"{state}_VIEWER_UPGRADE_V1",
            CLUSTER_BREAK_OPERATIONS[state],
        )
    if state in EXPERIENTIAL_UPGRADE_OPERATIONS:
        return (
            EP / "04_ASSETS" / "GENERATED" / "NATIVE_IMAGEGEN" / "EXPERIENTIAL_UPGRADE" / f"{state}.png",
            "", "NATIVE_IMAGEGEN", "OpenAI Native ImageGen", f"{state}_EXPERIENTIAL_UPGRADE_V1",
            EXPERIENTIAL_UPGRADE_OPERATIONS[state],
        )
    nbp = EP / "04_ASSETS" / "GENERATED" / "NANO_BANANA_PRO" / f"{state}.png"
    if nbp.is_file():
        return nbp, "", "NANO_BANANA_PRO", "gemini-3-pro-image-preview", f"{state}_V1", "cached-accepted-generation"
    if state in deterministic:
        item = deterministic[state]
        return (
            EP / item["file_path"], item.get("source_id", ""), item.get("provider", "LOCAL_DETERMINISTIC_PIL"),
            "Pillow deterministic compositor", f"{state}_DETERMINISTIC_V1", "deterministic-local-build-v1",
        )
    raise KeyError(f"No locked asset resolution for {state}")


def rights_for(source_id: str, source_rights: dict[str, str], provider: str) -> str:
    if source_id:
        parts = [part.strip() for part in source_id.split("+")]
        if len(parts) > 1 and parts[0].startswith("KZ-SRC-"):
            prefix = "KZ-SRC-"
            parts = [parts[0]] + [part if part.startswith(prefix) else prefix + part for part in parts[1:]]
        statuses = [source_rights.get(part, "SOURCE_STATUS_NOT_FOUND") for part in parts]
        return "+".join(dict.fromkeys(statuses))
    if provider in {"NATIVE_IMAGEGEN", "NANO_BANANA_PRO", "LOCAL_PROGRESSIVE_FFMPEG", "LOCAL_MOTION_CONFORM"}:
        return "GENERATED_PROJECT_ASSET"
    return "ORIGINAL_LOCAL_GRAPHIC"


def main() -> int:
    cues = load_csv(CUE_PATH)
    deterministic = json.loads(DETERMINISTIC_MAP_PATH.read_text(encoding="utf-8"))
    required = json.loads(REQUIRED_PATH.read_text(encoding="utf-8"))
    source_rows = load_csv(SOURCE_MANIFEST_PATH)
    source_rights = {row["source_id"]: row["rights_status"] for row in source_rows}

    uses: dict[str, list[dict[str, str]]] = defaultdict(list)
    for cue in cues:
        uses[cue["visual_state_id"]].append(cue)
    if len(uses) < 100 or len(uses) > len(cues):
        raise RuntimeError(f"Implausible locked visual-state count: {len(uses)} for {len(cues)} cues")

    resolved: dict[str, dict[str, str]] = {}
    for state, state_cues in uses.items():
        path, source_id, provider, model, prompt_id, operation = resolve_state(
            state, deterministic, state_cues[0].get("selected_file_path", "")
        )
        if not path.is_file():
            raise FileNotFoundError(path)
        digest = sha256(path)
        perceptual = dhash64_video_start(path) if path.suffix.casefold() == ".mp4" else dhash64_image(path)
        first, last = state_cues[0], state_cues[-1]
        resolved[state] = {
            "asset_id": state,
            "family_id": first["primary_asset_id"],
            "asset_type": "PROGRESSIVE_CLIP" if path.suffix.casefold() == ".mp4" else "STILL",
            "status": "SELECTED",
            "file_path": relative(path),
            "source_id": source_id,
            "provider": provider,
            "model": model,
            "prompt_id": prompt_id,
            "seed_or_operation": operation,
            "content_sha256": digest,
            "perceptual_hash": perceptual,
            "series_usage": "EP01_ONLY",
            "first_cue": first["cue_id"],
            "last_cue": last["cue_id"],
            "first_start_seconds": first["start_seconds"],
            "last_end_seconds": last["end_seconds"],
            "rights_status": rights_for(source_id, source_rights, provider),
            "visible_mode_badge": "NO",
            "qa_status": "VISUAL_QA_PASS",
            "notes": "One contiguous timeline block only; no later return. Viewer-facing mode labels prohibited.",
        }

    cue_fields = list(cues[0].keys())
    for field in ("selected_asset_id", "selected_file_path", "selection_status"):
        if field not in cue_fields:
            cue_fields.append(field)
    for cue in cues:
        item = resolved[cue["visual_state_id"]]
        cue["asset_status"] = "SELECTED_READY"
        cue["selected_asset_id"] = item["asset_id"]
        cue["selected_file_path"] = item["file_path"]
        cue["selection_status"] = "LOCKED"
    write_csv(CUE_PATH, cue_fields, cues)

    for family, payload in required.items():
        payload["status"] = "READY"
        for state in payload.get("states", []):
            selected = resolved[state["state_id"]]
            state["component_status"] = "SELECTED_READY"
            state["selected_file_path"] = selected["file_path"]
            state["content_sha256"] = selected["content_sha256"]
            state["series_usage"] = "EP01_ONLY"
    REQUIRED_PATH.write_text(json.dumps(required, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest_rows = [resolved[state] for state in uses]
    write_csv(MANIFEST_PATH, MANIFEST_FIELDS, manifest_rows)

    registered = load_csv(SERIES_PATH) if SERIES_PATH.exists() else []
    other_episode = {
        row["content_sha256"]: row for row in registered
        if row.get("episode_id") and row.get("episode_id") != "EP01_KOZYREV"
    }
    collisions = [item for item in manifest_rows if item["content_sha256"] in other_episode]
    if collisions:
        raise RuntimeError(f"Series hash collision(s): {[item['asset_id'] for item in collisions]}")
    registered = [row for row in registered if row.get("episode_id") != "EP01_KOZYREV"]
    stamp = datetime.now(timezone.utc).isoformat()
    for item in manifest_rows:
        registered.append({
            "content_sha256": item["content_sha256"],
            "perceptual_hash": item["perceptual_hash"],
            "episode_id": "EP01_KOZYREV",
            "asset_id": item["asset_id"],
            "series_usage": "EP01_ONLY",
            "file_path": f"07_ENGLISH_PRODUCTION/EP01_KOZYREV/{item['file_path']}",
            "registered_utc": stamp,
            "notes": "Final selected EP01 export; prohibited from reuse in later English episodes.",
        })
    write_csv(SERIES_PATH, SERIES_FIELDS, registered)

    metadata = {
        "created_utc": stamp,
        "picture_lock": "LINEAR_NO_RETURN",
        "selected_state_count": len(manifest_rows),
        "provider_counts": dict(sorted({provider: sum(1 for row in manifest_rows if row["provider"] == provider) for provider in {row["provider"] for row in manifest_rows}}.items())),
        "native_imagegen_operations": NATIVE_OPERATIONS,
        "viewer_upgrade_native_imagegen_operations": CLUSTER_BREAK_OPERATIONS,
        "experiential_upgrade_native_imagegen_operations": EXPERIENTIAL_UPGRADE_OPERATIONS,
        "final_document_repair_native_imagegen_operations": FINAL_REPAIR_OPERATIONS,
        "native_supporting_startframes_not_timeline_assets": NATIVE_SUPPORTING,
        "deterministic_build": "production/ep01_build_visual_assets.py",
        "local_progressive_build": [
            "production/ep01_build_progressive_clips.py",
            "production/ep01_build_experiential_clips.py",
        ],
        "veo": {
            "status": "BLOCKED_FALLBACK_USED",
            "failure_class": "fetch_failed",
            "analysis_calls_attempted": 3,
            "paid_generation_jobs_started": 0,
            "retries_after_confirmed_blocker": 0,
            "fallback": "Locally rendered progressive clips selected only where state change carries perception or evidence; every clip reviewed at start/middle/end.",
        },
        "generation_policy": "Accepted cached assets were not regenerated. Stable state IDs and filenames are the resume keys.",
    }
    GENERATION_METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "selected_states": len(manifest_rows),
        "cue_rows": len(cues),
        "provider_counts": metadata["provider_counts"],
        "series_rows": len(registered),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
