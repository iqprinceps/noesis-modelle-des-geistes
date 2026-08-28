#!/usr/bin/env python3
"""Apply the second, viewer-led experiential picture pass to EP01."""

from __future__ import annotations

import csv
import json
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
CUE = EP / "06_TIMELINE/EP01_EN_VISUAL_CUE_SHEET.csv"
REQUIRED = EP / "06_TIMELINE/EP01_EN_REQUIRED_ASSET_SET.json"


# old state -> (new state, relative path, internal mode, viewer action, motion class)
REPLACEMENTS = {
    "KZ_CARD_THEORY_ISOLATION": (
        "KZ_MYSTIC_THEORY_ISOLATION",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_THEORY_ISOLATION.png",
        "INNER_HYPOTHESIS",
        "Replace the first theory card with an empty, physically real chamber whose bodily trace implies isolation without depicting an entity.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_THEORY_PHYSICAL": (
        "KZ_PHYSICAL_THEORY_BODY_BOUNDARY",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_PHYSICAL_THEORY_BODY_BOUNDARY.png",
        "RECONSTRUCTION",
        "Make the ordinary physical hypothesis tactile through skin response, a real sensor and opaque aluminum.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_THEORY_INFORMATION": (
        "KZ_MYSTIC_THEORY_INFORMATION_REFLECTION",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_THEORY_INFORMATION_REFLECTION.png",
        "INNER_HYPOTHESIS",
        "Turn the information hypothesis into a restrained reflection that seems spatially ahead of its source.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_TIME_AS_ACTIVE_IDEA": (
        "KZ_MYSTIC_TIME_ACTIVE_AFTERIMAGE",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_TIME_ACTIVE_AFTERIMAGE.png",
        "INNER_HYPOTHESIS",
        "Carry Kozyrev's idea forward as delayed light bands inside a materially real chamber.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_THREE_STREAMS_COLLAPSE": (
        "KZ_MYSTIC_THREE_STORIES_COLLAPSE",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_THREE_STORIES_COLLAPSE.png",
        "INNER_HYPOTHESIS",
        "Let three distinct material traces converge on the same chair instead of collapsing text labels.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_STREAM_RESEARCHERS": (
        "KZ_RESEARCHERS_NIGHT_LAB",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_RESEARCHERS_NIGHT_LAB.png",
        "RECONSTRUCTION",
        "Show a clearly reconstructed late-1990s research practice when the experiments are named; identities remain established by the preceding authentic pair.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_THREE_STREAMS_SEPARATED": (
        "KZ_MYSTIC_SEPARATE_THREADS",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_SEPARATE_THREADS.png",
        "INNER_HYPOTHESIS",
        "Separate condensation, reflection and sensor trace across three physical layers without a diagram.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_WHY_DIRECTION": (
        "KZ_MYSTIC_DIRECTION_REFLECTION",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_DIRECTION_REFLECTION.png",
        "INNER_HYPOTHESIS",
        "Pose direction as a displaced traveling reflection across curved aluminum.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_WHY_MOON": (
        "KZ_MYSTIC_LUNAR_REFLECTION",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_LUNAR_REFLECTION.png",
        "INNER_HYPOTHESIS",
        "Pose the lunar condition through one plausible exterior light reflection, not celestial spectacle.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_MEASURABLE_NOT_TIME_TRAVEL": (
        "KZ_MYSTIC_MEASURABLE_NOT_TRAVEL",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_MEASURABLE_NOT_TRAVEL.png",
        "RECONSTRUCTION",
        "Ground the distinction in an ordinary analog bodily measurement beside a curved aluminum sample.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_EXTRAORDINARY_POSSIBILITY": (
        "KZ_MYSTIC_EXTRAORDINARY_POSSIBILITY",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_EXTRAORDINARY_POSSIBILITY.png",
        "INNER_HYPOTHESIS",
        "Let an impossible-seeming chair reflection embody the possibility while remaining explicitly hypothetical in metadata and narration.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_UNKNOWN_INFORMATION": (
        "KZ_CLIP_INFORMATION_BEFORE_REVEAL",
        "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_INFORMATION_BEFORE_REVEAL.mp4",
        "INNER_HYPOTHESIS",
        "Progressively organize reflected light before the sealed target is revealed; movement carries the perception process.",
        "PROGRESSIVE_MOTION",
    ),
    "KZ_CARD_THEORIES_FORCED_APART": (
        "KZ_MYSTIC_THEORIES_FORCED_APART",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_THEORIES_FORCED_APART.png",
        "INNER_HYPOTHESIS",
        "Force the explanations apart as distinct heat, light and sensor traces across one real chamber gap.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_MISSING_EXPERIMENT": (
        "KZ_CLIP_MISSING_EXPERIMENT_VOID",
        "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_MISSING_EXPERIMENT_VOID.mp4",
        "RECONSTRUCTION",
        "Let the lab visibly power down toward an empty results tray so the missing experiment becomes an experience, not a title card.",
        "PROGRESSIVE_MOTION",
    ),
    "KZ_CARD_DECISIVE_INFORMATION_QUESTION": (
        "KZ_MYSTIC_DECISIVE_INFORMATION_QUESTION",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_DECISIVE_INFORMATION_QUESTION.png",
        "INNER_HYPOTHESIS",
        "Stage the decisive question across observer, participant and sealed target without claiming an answer.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_RESULT_STILL_MISSING": (
        "KZ_MYSTIC_RESULT_STILL_MISSING",
        "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_RESULT_STILL_MISSING.png",
        "RECONSTRUCTION",
        "Show the absent chair, unplugged sensor and dark final chamber layer as the missing result.",
        "STATIC_OR_NEAR_STATIC",
    ),
    "KZ_CARD_THREE_OBSERVERS_THREE_TIMES": (
        "KZ_CLIP_THREE_OBSERVERS_TRANSITION",
        "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_THREE_OBSERVERS_TRANSITION.mp4",
        "INNER_HYPOTHESIS",
        "Move one practical reflection through three empty observer positions for an EP01-only closing promise that does not pre-use Gateway imagery.",
        "PROGRESSIVE_MOTION",
    ),
}

PATENT_OLD = {
    "KZ_SRC_PATENT_AUTHORITY_FULL",
    "KZ_SRC_PATENT_NUMBER_CROP",
    "KZ_SRC_PATENT_DATES_CROP",
    "KZ_SRC_PATENT_INVENTORS_CROP",
    "KZ_SRC_PATENT_DRAWINGS",
}
PATENT_NEW = (
    "KZ_CLIP_PATENT_EVIDENCE_DECONSTRUCTION",
    "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PATENT_EVIDENCE_DECONSTRUCTION.mp4",
    "ORIGINAL_DOCUMENT",
    "Keep the verified original patent on screen as one continuous progressive proof beat, sequentially revealing number, dates, inventors and drawings.",
    "PROGRESSIVE_MOTION",
)


def replace_row(row: dict[str, str]) -> bool:
    old = row["visual_state_id"]
    replacement = PATENT_NEW if old in PATENT_OLD else REPLACEMENTS.get(old)
    if replacement is None:
        return False
    new, path, mode, action, motion = replacement
    row["visual_state_id"] = new
    row["selected_asset_id"] = new
    row["selected_file_path"] = path
    row["visual_mode_internal"] = mode
    row["visual_action"] = action
    row["motion_class"] = motion
    row["visible_mode_badge"] = "NO"
    row["allowed_context_line"] = "NO"
    return True


def main() -> int:
    with CUE.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    cue_changed = sum(replace_row(row) for row in rows)
    with CUE.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    required = json.loads(REQUIRED.read_text(encoding="utf-8"))
    required_changed = 0
    cue_by_id = {row["cue_id"]: row for row in rows}
    for family in required.values():
        modes: list[str] = []
        for state in family.get("states", []):
            old = state.get("state_id", "")
            replacement = PATENT_NEW if old in PATENT_OLD else REPLACEMENTS.get(old)
            if replacement:
                new, path, _mode, action, motion = replacement
                state["state_id"] = new
                state["selected_file_path"] = path
                state["visual_action"] = action
                state["motion_class"] = motion
                state["content_sha256"] = "PENDING_FINALIZER"
                required_changed += 1
            cue = cue_by_id.get(state.get("cue_id", ""))
            if cue and cue["visual_mode_internal"] not in modes:
                modes.append(cue["visual_mode_internal"])
        family["visual_modes_internal"] = modes
        family["visible_mode_badge"] = "NO"
    REQUIRED.write_text(json.dumps(required, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    expected = len(REPLACEMENTS) + len(PATENT_OLD)
    if cue_changed != expected or required_changed != expected:
        raise RuntimeError(f"Expected {expected} cue/required replacements; got cue={cue_changed}, required={required_changed}")
    print(json.dumps({"cue_replacements": cue_changed, "required_replacements": required_changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
