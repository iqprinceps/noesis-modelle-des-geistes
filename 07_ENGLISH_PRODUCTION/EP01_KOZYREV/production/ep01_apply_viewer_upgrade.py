#!/usr/bin/env python3
"""Apply the rights-cleared, viewer-led no-repeat EP01 picture upgrade."""

from __future__ import annotations

import csv
import json
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
CUE = EP / "06_TIMELINE" / "EP01_EN_VISUAL_CUE_SHEET.csv"
REQUIRED = EP / "06_TIMELINE" / "EP01_EN_REQUIRED_ASSET_SET.json"


REPLACEMENTS = {
    "KZ_SRC_KOZYREV_SECOND_AUTHENTIC_CONTEXT": (
        "KZ_HISTORY_PULKOVO_OBSERVATORY",
        "04_ASSETS/GENERATED/DETERMINISTIC/KZ_HISTORY_PULKOVO_OBSERVATORY.png",
        "ARCHIVE",
        "Move from Kozyrev's portrait into the public-domain observatory world that grounds his profession.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_SRC_KOZYREV_ASTRONOMER_CONTEXT": (
        "KZ_HISTORY_PULKOVO_REFRACTOR",
        "04_ASSETS/GENERATED/DETERMINISTIC/KZ_HISTORY_PULKOVO_REFRACTOR.png",
        "ARCHIVE",
        "Show a distinct public-domain Pulkovo refractor when Kozyrev's astronomical work is named.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_SRC_KOZYREV_THIRD_AUTHENTIC_CONTEXT": (
        "KZ_HISTORY_KOZYREV_NOT_CHAMBER_BUILDER",
        "04_ASSETS/GENERATED/DETERMINISTIC/KZ_HISTORY_KOZYREV_NOT_CHAMBER_BUILDER.png",
        "ARCHIVE",
        "Return to a genuinely new public-domain astronomy context and the 1983/1996 chronology, not an earlier patent crop.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_SRC_PATENT_HEIGHT": (
        "KZ_PHYSICAL_PANEL_SCALE",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_PHYSICAL_PANEL_SCALE.png",
        "RECONSTRUCTION",
        "Make the stated 2.8-metre maximum physically legible through human scale, without invented labels.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_SRC_PATENT_PANEL_COUNT": (
        "KZ_PHYSICAL_PANEL_ARRAY",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_PHYSICAL_PANEL_ARRAY.png",
        "RECONSTRUCTION",
        "Reveal six overlapping curved panels as a plausible construction state, not another document crop.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_EXPERIENCE_NOT_INFORMATION": (
        "KZ_SENSORY_HAND_ON_ALUMINUM",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_SENSORY_HAND_ON_ALUMINUM.png",
        "RECONSTRUCTION",
        "Translate the distinction into touch, reflection and bodily sensing at the chamber wall.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_MODEL_ORDINARY_VARIABLES": (
        "KZ_CLIP_PHYSICAL_VARIABLES_SENSOR_RIG",
        "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PHYSICAL_VARIABLES_SENSOR_RIG.mp4",
        "RECONSTRUCTION",
        "Let ordinary sensor readings develop while the voice names sound, temperature, reflections and body sensing.",
        "PROGRESSIVE_MOTION",
    ),
    "KZ_MODEL_INFORMATION_ACROSS_DISTANCE": (
        "KZ_OBSERVER_DISTANCE_REFLECTION",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_OBSERVER_DISTANCE_REFLECTION.png",
        "INNER_HYPOTHESIS",
        "Make the distance hypothesis spatially concrete through restrained reflected bands and an unreachable point.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_FEELING_NOT_TEST": (
        "KZ_SUBJECTIVE_REPORT_HAND",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_SUBJECTIVE_REPORT_HAND.png",
        "RECONSTRUCTION",
        "Ground subjective testimony in the physical act of recording a report after isolation.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_PSYCHOLOGY_PREDICTION": (
        "KZ_PSYCHOLOGY_ISOLATION_BODY",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_PSYCHOLOGY_ISOLATION_BODY.png",
        "RECONSTRUCTION",
        "Show the psychology prediction as a human body under sensory isolation, not an abstract card.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_PHYSICAL_PREDICTION": (
        "KZ_PHYSICAL_MEASUREMENT_CLOSEUP",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_PHYSICAL_MEASUREMENT_CLOSEUP.png",
        "RECONSTRUCTION",
        "Move to an ordinary analog measurement close-up for the physical prediction.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_RANDOM_TARGET_BOUNDARY": (
        "KZ_RANDOM_TARGET_SEALED_VAULT",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_RANDOM_TARGET_SEALED_VAULT.png",
        "RECONSTRUCTION",
        "Make the random-target boundary tangible in a separate room with sealed choices and controlled access.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_PATENTED_MEANS_PROVEN": (
        "KZ_ONLINE_PATENT_AUTHORITY",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_ONLINE_PATENT_AUTHORITY.png",
        "EXPLANATORY_MODEL",
        "Use a contemporary patent-search moment to expose the authority shortcut from patented to proven.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_PATENT_CAN_SHOW": (
        "KZ_PATENT_PROVENANCE_DESK",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_PATENT_PROVENANCE_DESK.png",
        "EXPLANATORY_MODEL",
        "Show what a patent can establish through a sober provenance desk: document, drawing and material sample.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_PATENT_NOT_CERTIFY": (
        "KZ_EMPTY_RESULT_TRAY",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CLUSTER_BREAKS/KZ_EMPTY_RESULT_TRAY.png",
        "EXPLANATORY_MODEL",
        "End the authority trap on an empty results tray and baseline instrument: documentation is not replication.",
        "STATIC_OR_NEAR_STATIC",
    ),
}


def main() -> int:
    with CUE.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)

    changed = 0
    for row in rows:
        old = row["visual_state_id"]
        if old not in REPLACEMENTS:
            continue
        new, path, mode, action, motion = REPLACEMENTS[old]
        row["visual_state_id"] = new
        row["selected_asset_id"] = new
        row["selected_file_path"] = path
        row["visual_mode_internal"] = mode
        row["visual_action"] = action
        row["motion_class"] = motion
        row["visible_mode_badge"] = "NO"
        row["allowed_context_line"] = "NO"
        changed += 1

    with CUE.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    required = json.loads(REQUIRED.read_text(encoding="utf-8"))
    required_changed = 0
    for family in required.values():
        modes = []
        for state in family.get("states", []):
            old = state.get("state_id", "")
            if old in REPLACEMENTS:
                new, path, mode, action, motion = REPLACEMENTS[old]
                state["state_id"] = new
                state["selected_file_path"] = path
                state["visual_action"] = action
                state["motion_class"] = motion
                state["content_sha256"] = "PENDING_FINALIZER"
                required_changed += 1
            cue_id = state.get("cue_id")
            cue = next((row for row in rows if row["cue_id"] == cue_id), None)
            if cue and cue["visual_mode_internal"] not in modes:
                modes.append(cue["visual_mode_internal"])
        family["visual_modes_internal"] = modes
        family["visible_mode_badge"] = "NO"
    REQUIRED.write_text(json.dumps(required, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if changed != len(REPLACEMENTS) or required_changed != len(REPLACEMENTS):
        raise RuntimeError(
            f"Expected {len(REPLACEMENTS)} replacements; cue={changed}, required={required_changed}"
        )
    print(json.dumps({"cue_replacements": changed, "required_replacements": required_changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
