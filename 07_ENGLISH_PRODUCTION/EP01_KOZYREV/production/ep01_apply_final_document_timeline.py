#!/usr/bin/env python3
"""Apply the final viewer-led document decisions to EP01's canonical cue timeline.

This pass only writes planning/timeline metadata. It does not generate media or render.
"""

from __future__ import annotations

import csv
import json
from collections import OrderedDict
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
CUE = EP / "06_TIMELINE" / "EP01_EN_VISUAL_CUE_SHEET.csv"
REQUIRED = EP / "06_TIMELINE" / "EP01_EN_REQUIRED_ASSET_SET.json"


def decision(state, path, mode, action, motion="STATIC_OR_NEAR_STATIC", reason=""):
    return {
        "state": state,
        "path": path,
        "mode": mode,
        "action": action,
        "motion": motion,
        "reason": reason,
    }


DECISIONS = {
    "KZ-CUE-002": decision(
        "KZ_DATA_PATENT_FILING_ANCHOR",
        "04_ASSETS/GENERATED/FINAL_DOCUMENT_TIMELINE/KZ_DATA_PATENT_FILING_ANCHOR.png",
        "DATA_SOURCE_ANCHOR",
        "Ground the hook in verified filing data while the preceding physical chamber remains in memory; no pseudo-document text.",
    ),
    "KZ-CUE-003": decision(
        "KZ_DOC_002", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_002.png",
        "ORIGINAL_DOCUMENT", "Hold the complete verified clinical-title block statically with its genuine phrase highlighted.",
    ),
    "KZ-CUE-010": decision(
        "KZ_FIG_PATENT_CYLINDER", "04_ASSETS/GENERATED/FINAL_DOCUMENT_TIMELINE/KZ_FIG_PATENT_CYLINDER.png",
        "ORIGINAL_TECHNICAL_FIGURE", "Show the correct patent page and enlarged Figure 2 as a technical illustration, not a textual quote.",
    ),
    "KZ-CUE-011": decision(
        "KZ_MODEL_CLOCKWISE_SPIRAL", "04_ASSETS/GENERATED/FINAL_DOCUMENT_TIMELINE/KZ_MODEL_CLOCKWISE_SPIRAL.png",
        "EXPLANATORY_MODEL", "Translate clockwise direction into a unique clean geometry state because the original figure does not encode direction.",
    ),
    "KZ-CUE-013": decision(
        "KZ_FIG_PATENT_MOTORIZED_PLATFORM", "04_ASSETS/GENERATED/FINAL_DOCUMENT_TIMELINE/KZ_FIG_PATENT_MOTORIZED_PLATFORM.png",
        "ORIGINAL_TECHNICAL_FIGURE", "Show authentic patent Figure 4 at the motorized-platform statement; this avoids a repeated abstract-page visual mode.",
    ),
    "KZ-CUE-015": decision(
        "KZ_FILM_LUNAR_STORM_SESSION", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/FINAL_DOCUMENT_REPAIR/KZ_FILM_LUNAR_STORM_SESSION.png",
        "CLAIM_VISUALIZATION", "Visualize the explicitly attributed lunar/storm operating claim as an ambiguous physical night session, not an unreadable scan.",
    ),
    "KZ-CUE-027": decision(
        "KZ_DOC_028", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_028.png",
        "ORIGINAL_DOCUMENT", "Use the complete English abstract block naming cells, people, plants and information as the correct source passage.",
    ),
    "KZ-CUE-035": decision(
        "KZ_FILM_ALUMINUM_SURFACE_MACRO", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/FINAL_DOCUMENT_REPAIR/KZ_FILM_ALUMINUM_SURFACE_MACRO.png",
        "PHYSICAL_DETAIL", "Show physically distinct ground and smoother aluminum surface treatment without overstating the translated abstract.",
    ),
    "KZ-CUE-036": decision(
        "KZ_DOC_032", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_032.png",
        "ORIGINAL_DOCUMENT", "Hold a mobile-readable recomposition of the complete verified focus-distance sentence.",
    ),
    "KZ-CUE-041": decision(
        "KZ_MYSTIC_LUNAR_REFLECTION", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_LUNAR_REFLECTION.png",
        "SUBJECTIVE_HYPOTHESIS", "Begin one continuous lunar/geomagnetic question image with physically ambiguous chamber reflections.",
    ),
    "KZ-CUE-042": decision(
        "KZ_MYSTIC_LUNAR_REFLECTION", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_LUNAR_REFLECTION.png",
        "SUBJECTIVE_HYPOTHESIS", "Continue the same uninterrupted question state; no later return.",
    ),
    "KZ-CUE-043": decision(
        "KZ_CLIP_FIELD_CONCENTRATION_PROPOSAL", "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_FIELD_CONCENTRATION_PROPOSAL.mp4",
        "CLAIM_VISUALIZATION", "Begin a progressive field-concentration model as the explicitly attributed inventors' answer; do not use identity metadata as proof.",
        "PROGRESSIVE_MOTION", "One continuous 9.20-second proposal sequence adds field paths and convergence instead of holding a static graphic.",
    ),
    "KZ-CUE-044": decision(
        "KZ_CLIP_FIELD_CONCENTRATION_PROPOSAL", "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_FIELD_CONCENTRATION_PROPOSAL.mp4",
        "CLAIM_VISUALIZATION", "Continue the same model while the proposed body-associated field concentration is stated.",
        "PROGRESSIVE_MOTION", "Continuous evolving clip; no restart.",
    ),
    "KZ-CUE-045": decision(
        "KZ_FILM_HELIOGEOPHYSICAL_CHAMBER", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/FINAL_DOCUMENT_REPAIR/KZ_FILM_HELIOGEOPHYSICAL_CHAMBER.png",
        "CLAIM_VISUALIZATION", "Visualize the attributed environmental claim with a plausible chamber, dawn light and an analog field instrument.",
    ),
    "KZ-CUE-046": decision(
        "KZ_CARD_PATENT_RECORDS_CLAIM", "04_ASSETS/GENERATED/DETERMINISTIC/KZ_CARD_PATENT_RECORDS_CLAIM.png",
        "EPISTEMIC_GRAPHIC", "Start one concise continuous claim-versus-result distinction; no document is asked to prove itself.",
    ),
    "KZ-CUE-047": decision(
        "KZ_CARD_PATENT_RECORDS_CLAIM", "04_ASSETS/GENERATED/DETERMINISTIC/KZ_CARD_PATENT_RECORDS_CLAIM.png",
        "EPISTEMIC_GRAPHIC", "Continue the same claim-state without a cut or later reuse.",
    ),
    "KZ-CUE-049": decision(
        "KZ_DOC_013", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_013.png",
        "ORIGINAL_DOCUMENT", "Use the complete Kaznacheev/Trofimov 2008 author/title block as the departure from medicine.",
    ),
    "KZ-CUE-050": decision(
        "KZ_DOC_014", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_014.png",
        "ORIGINAL_DOCUMENT", "Use the complete 2006 author/title block with the genuine modeled-Kozyrev-space phrase.",
    ),
    "KZ-CUE-051": decision(
        "KZ_MYSTIC_INTERNAL_TIME_REFRACTION", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/EXPERIENTIAL_UPGRADE/KZ_MYSTIC_INTERNAL_TIME_REFRACTION.png",
        "SUBJECTIVE_HYPOTHESIS", "Represent the attributed time interpretation as a first-person metal-room perception, never as a fabricated quotation.",
    ),
    "KZ-CUE-091": decision(
        "KZ_DOC_016", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_016.png",
        "ORIGINAL_DOCUMENT", "Show the authentic patent-office line and full page context as the real-patent anchor.",
    ),
    "KZ-CUE-092": decision(
        "KZ_DOC_029", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_029.png",
        "ORIGINAL_DOCUMENT", "Show the complete authors' English abstract with genuine information-transmission and unusual-optical-effects phrases highlighted.",
    ),
    "KZ-CUE-096": decision(
        "KZ_FILM_PATENT_AUTHORITY_LIGHTTABLE", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/FINAL_DOCUMENT_REPAIR/KZ_FILM_PATENT_AUTHORITY_LIGHTTABLE.png",
        "INTERPRETIVE_FILMIC", "Set up the authority trap as a filmic light-table metaphor with no readable synthetic document.",
    ),
    "KZ-CUE-097": decision(
        "KZ_FILM_PATENT_AUTHORITY_LIGHTTABLE", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/FINAL_DOCUMENT_REPAIR/KZ_FILM_PATENT_AUTHORITY_LIGHTTABLE.png",
        "INTERPRETIVE_FILMIC", "Continue the same uninterrupted authority image through the verdict line.",
    ),
    "KZ-CUE-098": decision(
        "KZ_DOC_030", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_030.png",
        "ORIGINAL_DOCUMENT", "Begin one static authentic metadata composite containing the complete number, date and inventor fields.",
    ),
    "KZ-CUE-099": decision(
        "KZ_DOC_030", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_030.png",
        "ORIGINAL_DOCUMENT", "Continue the same static metadata composite; complete application/publication lines remain visible.",
    ),
    "KZ-CUE-100": decision(
        "KZ_DOC_030", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_030.png",
        "ORIGINAL_DOCUMENT", "Continue the same static metadata composite; complete inventor lines remain visible.",
    ),
    "KZ-CUE-101": decision(
        "KZ_FIG_PATENT_DRAWING_FIG3", "04_ASSETS/GENERATED/FINAL_DOCUMENT_TIMELINE/KZ_FIG_PATENT_DRAWING_FIG3.png",
        "ORIGINAL_TECHNICAL_FIGURE", "Show the previously unused authentic Figure 3 spiral page, distinct from the earlier motorized-platform figure.",
    ),
    "KZ-CUE-105": decision(
        "KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS", "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS.mp4",
        "EVIDENCE_PROCESS", "Begin a progressive evidence-desk-to-empty-result sequence explaining what a patent can establish.",
        "PROGRESSIVE_MOTION", "A 13.96-second continuous sequence is justified by three visible phases: scope card, provenance desk, then empty empirical result.",
    ),
    "KZ-CUE-106": decision(
        "KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS", "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS.mp4",
        "EVIDENCE_PROCESS", "Continue to the empty result state while the narration states the evidentiary limit.",
        "PROGRESSIVE_MOTION", "Continuous evolving clip; no restart.",
    ),
    "KZ-CUE-107": decision(
        "KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS", "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS.mp4",
        "EVIDENCE_PROCESS", "End on the patent's documentary value without returning to a document card.",
        "PROGRESSIVE_MOTION", "Continuous evolving clip; no restart.",
    ),
    "KZ-CUE-108": decision(
        "KZ_DOC_031", "04_ASSETS/GENERATED/DOCUMENT_EVIDENCE/KZ_DOC_031.png",
        "ORIGINAL_DOCUMENT", "Hold a distinct mobile-readable composition of the complete dimensions/material sentence.",
    ),
    "KZ-CUE-112": decision(
        "KZ_CLIP_PATENT_FEATURES_RECAP", "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PATENT_FEATURES_RECAP.mp4",
        "PHYSICAL_RECAP", "Begin a new mechanical chamber insert with a progressive focal-distance overlay.",
        "PROGRESSIVE_MOTION",
    ),
    "KZ-CUE-113": decision(
        "KZ_CLIP_PATENT_FEATURES_RECAP", "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PATENT_FEATURES_RECAP.mp4",
        "PHYSICAL_RECAP", "Continue the same clip with direction indication; no document return.",
        "PROGRESSIVE_MOTION",
    ),
    "KZ-CUE-114": decision(
        "KZ_CLIP_PATENT_FEATURES_RECAP", "04_ASSETS/CLIPS/LOCAL_PROGRESSIVE/KZ_CLIP_PATENT_FEATURES_RECAP.mp4",
        "PHYSICAL_RECAP", "Finish the same clip at the physical drive/rotation state.",
        "PROGRESSIVE_MOTION",
    ),
    "KZ-CUE-117": decision(
        "KZ_EN_REC18_EMPTY_CHAMBER_A", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/CHAMBER_STATES/KZ_EN_REC18_EMPTY_CHAMBER_A.png",
        "PHYSICAL_CHAMBER", "Continue the immediately preceding empty-chamber payoff as one uninterrupted physical state; the patent has already been established by authentic evidence.",
    ),
    "KZ-CUE-118": decision(
        "KZ_MYSTIC_CLAIMS_TRIAD", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/FINAL_DOCUMENT_REPAIR/KZ_MYSTIC_CLAIMS_TRIAD.png",
        "SUBJECTIVE_HYPOTHESIS", "Show perception, distant information and temporal ambiguity as three unresolved chamber reflections, not as a source quote.",
    ),
    "KZ-CUE-119": decision(
        "KZ_MYSTIC_INTENSE_EXPERIENCE_HISTORY", "04_ASSETS/GENERATED/NATIVE_IMAGEGEN/FINAL_DOCUMENT_REPAIR/KZ_MYSTIC_INTENSE_EXPERIENCE_HISTORY.png",
        "SUBJECTIVE_HYPOTHESIS", "Use a unique body-boundary experience image for the historical report beat; no fake phrase or horror figure.",
    ),
}


def main() -> int:
    with CUE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = list(rows[0])
    seen = set()
    for row in rows:
        item = DECISIONS.get(row["cue_id"])
        if not item:
            continue
        seen.add(row["cue_id"])
        row["visual_state_id"] = item["state"]
        row["selected_asset_id"] = item["state"]
        row["selected_file_path"] = item["path"]
        row["visual_mode_internal"] = item["mode"]
        row["visual_action"] = item["action"]
        row["motion_class"] = item["motion"]
        row["long_hold_reason"] = item["reason"]
        row["visible_mode_badge"] = "NO"
        row["allowed_context_line"] = ""
        row["asset_status"] = "READY" if (EP / item["path"]).is_file() else "PLANNED_POST_TIMELINE_QA"
        row["selection_status"] = "FINAL_DECISION"
    missing = sorted(set(DECISIONS) - seen)
    if missing:
        raise RuntimeError(f"Cue IDs not found: {missing}")
    with CUE.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        writer.writerows(rows)

    families = OrderedDict()
    for row in rows:
        family = row["primary_asset_id"]
        payload = families.setdefault(family, {
            "status": "READY", "visual_modes_internal": [], "visible_mode_badge": "NO",
            "viewer_functions": [], "first_start_seconds": float(row["start_seconds"]),
            "last_end_seconds": float(row["end_seconds"]), "states": [],
        })
        if row["visual_mode_internal"] not in payload["visual_modes_internal"]:
            payload["visual_modes_internal"].append(row["visual_mode_internal"])
        if row["viewer_function"] not in payload["viewer_functions"]:
            payload["viewer_functions"].append(row["viewer_function"])
        payload["last_end_seconds"] = float(row["end_seconds"])
        ready = (EP / row["selected_file_path"]).is_file()
        if not ready:
            payload["status"] = "PLANNED_POST_TIMELINE_QA"
        payload["states"].append({
            "cue_id": row["cue_id"], "state_id": row["visual_state_id"],
            "component_status": "SELECTED_READY" if ready else "PLANNED_POST_TIMELINE_QA",
            "start_seconds": float(row["start_seconds"]), "end_seconds": float(row["end_seconds"]),
            "visual_action": row["visual_action"], "motion_class": row["motion_class"],
            "long_hold_reason": row["long_hold_reason"], "selected_file_path": row["selected_file_path"],
            "series_usage": "EP01_ONLY",
        })
    REQUIRED.write_text(json.dumps(families, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated_cues": len(seen), "cue_rows": len(rows), "families": len(families)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
