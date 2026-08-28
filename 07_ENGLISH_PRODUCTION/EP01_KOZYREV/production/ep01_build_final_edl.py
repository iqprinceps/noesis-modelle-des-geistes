#!/usr/bin/env python3
"""Build the continuous, frame-conform EP01 EDL and diagnose visual-mode clusters."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
CUE = EP / "06_TIMELINE" / "EP01_EN_VISUAL_CUE_SHEET.csv"
EDL = EP / "06_TIMELINE" / "EP01_EN_FINAL_EDL.csv"
QA = EP / "05_QA" / "MODE_CLUSTER_QA.json"
MANUAL_REVIEW = EP / "05_QA" / "MODE_CLUSTER_MANUAL_REVIEW.json"
MASTER_DURATION = 434.632
FPS = 25


def classify(state: str, mode: str) -> str:
    if state.startswith("KZ_DOC_") or state.startswith("KZ_FIG_PATENT_"):
        return "DOCUMENT_EVIDENCE"
    if state == "KZ_DATA_PATENT_FILING_ANCHOR":
        return "CONTEMPORARY_CONTEXT"
    if state in {"KZ_FILM_ALUMINUM_SURFACE_MACRO", "KZ_CLIP_PATENT_FEATURES_RECAP"}:
        return "PHYSICAL_CHAMBER"
    if state in {"KZ_FILM_LUNAR_STORM_SESSION", "KZ_FILM_HELIOGEOPHYSICAL_CHAMBER"}:
        return "SUBJECTIVE_MYSTICAL"
    if state in {"KZ_FILM_PATENT_AUTHORITY_LIGHTTABLE", "KZ_CLIP_PATENT_VALUE_LIMITS_CONTINUOUS"}:
        return "EVIDENCE_PROCESS"
    if state == "KZ_CLIP_FIELD_CONCENTRATION_PROPOSAL":
        return "EXPLANATORY_GRAPHIC"
    if state.startswith("KZ_CLIP_") or state.startswith("KZ_EN_REC") or state.startswith("KZ_EN_HERO") or state == "KZ_HERO01_REFLECTION_STATE":
        if any(token in state for token in ("INTERNAL_TIME", "DISTANT_IMAGE", "EMPTY_SPIRAL", "INFORMATION_BEFORE", "MISSING_EXPERIMENT", "THREE_OBSERVERS")):
            return "SUBJECTIVE_MYSTICAL"
        if "PATENT_EVIDENCE" in state:
            return "DOCUMENT_EVIDENCE"
        return "PHYSICAL_CHAMBER"
    if state.startswith("KZ_HISTORY_") or "KOZYREV" in state or "INVENTOR_PAIR" in state or "KAZNACHEEV_TROFIMOV_PAIR" in state:
        return "PERSON_HISTORY"
    if state.startswith("KZ_TARGET0") or state == "KZ_TARGET_MATCH_LIGHTHOUSE":
        return "TARGET_IMAGE"
    if state.startswith("KZ_TARGET_GRID") or state.startswith("KZ_PROTOCOL") or state.startswith("KZ_REPLICATION"):
        return "EXPERIMENT_PROTOCOL"
    if state == "KZ_RANDOM_TARGET_SEALED_VAULT":
        return "EXPERIMENT_PROTOCOL"
    if state.startswith("KZ_MAP_"):
        return "MAP_HANDOFF"
    if state.startswith("KZ_SRC_"):
        return "DOCUMENT_EVIDENCE"
    if state in {"KZ_PHYSICAL_PANEL_SCALE", "KZ_PHYSICAL_PANEL_ARRAY", "KZ_SENSORY_HAND_ON_ALUMINUM", "KZ_SUBJECTIVE_REPORT_HAND", "KZ_PSYCHOLOGY_ISOLATION_BODY", "KZ_PHYSICAL_MEASUREMENT_CLOSEUP"}:
        return "PHYSICAL_CHAMBER"
    if state == "KZ_OBSERVER_DISTANCE_REFLECTION":
        return "SUBJECTIVE_MYSTICAL"
    if state.startswith("KZ_MYSTIC_"):
        return "SUBJECTIVE_MYSTICAL"
    if state in {"KZ_PHYSICAL_THEORY_BODY_BOUNDARY", "KZ_RESEARCHERS_NIGHT_LAB"}:
        return "PHYSICAL_CHAMBER"
    if state == "KZ_ONLINE_PATENT_AUTHORITY":
        return "CONTEMPORARY_CONTEXT"
    if state == "KZ_PATENT_PROVENANCE_DESK":
        return "EVIDENCE_PROCESS"
    if state == "KZ_EMPTY_RESULT_TRAY":
        return "PHYSICAL_EVIDENCE"
    if mode == "INNER_HYPOTHESIS":
        return "SUBJECTIVE_MYSTICAL"
    return "EXPLANATORY_GRAPHIC"


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    with CUE.open(encoding="utf-8-sig", newline="") as handle:
        cues = list(csv.DictReader(handle))
    raw_runs = []
    for cue in cues:
        if not raw_runs or raw_runs[-1]["visual_state_id"] != cue["visual_state_id"]:
            raw_runs.append({
                "visual_state_id": cue["visual_state_id"],
                "primary_asset_id": cue["primary_asset_id"],
                "visual_mode_internal": cue["visual_mode_internal"],
                "selected_file_path": cue["selected_file_path"],
                "first_cue": cue["cue_id"],
                "last_cue": cue["cue_id"],
                "first_voice_start": float(cue["start_seconds"]),
                "last_voice_end": float(cue["end_seconds"]),
                "viewer_function": cue["viewer_function"],
                "motion_class": cue["motion_class"],
                "long_hold_reason": cue.get("long_hold_reason", ""),
            })
        else:
            raw_runs[-1]["last_cue"] = cue["cue_id"]
            raw_runs[-1]["last_voice_end"] = float(cue["end_seconds"])

    rows = []
    for index, run in enumerate(raw_runs):
        if index == 0:
            start = 0.0
        else:
            start = (raw_runs[index - 1]["last_voice_end"] + run["first_voice_start"]) / 2.0
        if index == len(raw_runs) - 1:
            end = MASTER_DURATION
        else:
            end = (run["last_voice_end"] + raw_runs[index + 1]["first_voice_start"]) / 2.0
        start_frame = round(start * FPS)
        end_frame = round(end * FPS)
        if end_frame <= start_frame:
            end_frame = start_frame + 1
        conform_start = start_frame / FPS
        conform_end = end_frame / FPS
        category = classify(run["visual_state_id"], run["visual_mode_internal"])
        rows.append({
            "event": f"KZ-EDL-{index + 1:03d}",
            "record_in_seconds": f"{conform_start:.3f}",
            "record_out_seconds": f"{conform_end:.3f}",
            "duration_seconds": f"{conform_end - conform_start:.3f}",
            "record_in_frame": start_frame,
            "record_out_frame": end_frame,
            "visual_state_id": run["visual_state_id"],
            "primary_asset_id": run["primary_asset_id"],
            "semantic_mode": category,
            "internal_mode": run["visual_mode_internal"],
            "motion_class": run["motion_class"],
            "selected_file_path": run["selected_file_path"],
            "first_cue": run["first_cue"],
            "last_cue": run["last_cue"],
            "viewer_function": run["viewer_function"],
            "long_hold_reason": run["long_hold_reason"],
        })

    fields = list(rows[0].keys())
    write_csv(EDL, fields, rows)

    clusters = []
    for row in rows:
        if not clusters or clusters[-1]["semantic_mode"] != row["semantic_mode"]:
            clusters.append({
                "semantic_mode": row["semantic_mode"],
                "first_event": row["event"],
                "last_event": row["event"],
                "start_seconds": float(row["record_in_seconds"]),
                "end_seconds": float(row["record_out_seconds"]),
                "events": [row["event"]],
                "states": [row["visual_state_id"]],
            })
        else:
            clusters[-1]["last_event"] = row["event"]
            clusters[-1]["end_seconds"] = float(row["record_out_seconds"])
            clusters[-1]["events"].append(row["event"])
            clusters[-1]["states"].append(row["visual_state_id"])
    for cluster in clusters:
        cluster["duration_seconds"] = round(cluster["end_seconds"] - cluster["start_seconds"], 3)
        cluster["event_count"] = len(cluster["events"])
        threshold = 14.0 if cluster["semantic_mode"] in {"DOCUMENT_EVIDENCE", "EXPLANATORY_GRAPHIC"} else 20.0
        cluster["review_required"] = cluster["duration_seconds"] >= threshold or cluster["event_count"] >= 4

    manual = json.loads(MANUAL_REVIEW.read_text(encoding="utf-8")) if MANUAL_REVIEW.exists() else {}
    for cluster in clusters:
        key = f'{cluster["semantic_mode"]}:{cluster["first_event"]}:{cluster["last_event"]}'
        verdict = manual.get(key, {})
        cluster["manual_review"] = verdict.get("status", "NOT_REQUIRED" if not cluster["review_required"] else "REQUIRED")
        cluster["manual_review_reason"] = verdict.get("reason", "")
        cluster["unresolved_review"] = cluster["review_required"] and cluster["manual_review"] != "PASS_VIEWER_LED"

    long_events = [row for row in rows if float(row["duration_seconds"]) >= 8.0]
    unresolved = [cluster for cluster in clusters if cluster["unresolved_review"]]
    accepted = [cluster for cluster in clusters if cluster["review_required"] and not cluster["unresolved_review"]]
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "REVIEW_REQUIRED" if unresolved else "PASS",
        "fps": FPS,
        "master_duration_seconds": MASTER_DURATION,
        "event_count": len(rows),
        "semantic_mode_counts": dict(Counter(row["semantic_mode"] for row in rows)),
        "clusters": clusters,
        "clusters_requiring_review": unresolved,
        "clusters_reviewed_and_accepted": accepted,
        "events_at_or_above_8_seconds": long_events,
        "note": "Cluster thresholds are diagnostic. Viewer review, semantic development and actual movement determine acceptance.",
    }
    QA.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "events": len(rows),
        "status": report["status"],
        "review_clusters": len(report["clusters_requiring_review"]),
        "long_events": len(long_events),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
