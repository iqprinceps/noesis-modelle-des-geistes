#!/usr/bin/env python3
"""Create the exact forced-alignment EDL, cue sheet, subtitles and rights register."""

from __future__ import annotations

import bisect
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


EP = Path(__file__).resolve().parents[1]
ALIGN = EP / "02_VOICE" / "ALIGNMENT" / "EP06_EN_FORCED_ALIGNMENT.json"
MASTER = EP / "02_VOICE" / "MASTER" / "EP06_EN_VO_MASTER.wav"
EDIT = EP / "04_EDIT"
SUB = EP / "07_SUBTITLES"
ASSETS = EP / "03_VISUALS" / "ASSETS"


SECTIONS = [
    (
        "S1_SALEM_PRIVATE_TO_PUBLIC", "In 1692", "Look closely at Coman's sequence",
        [
            "GENERATED/IMG001_SALEM_BEDROOM_COMAN_RECON.png",
            "GENERATED/IMG002_COMAN_TRIES_TO_WAKE_WIFE.png",
            "CARDS/EVIDENCE_COMAN_FULL_CONTEXT.png",
            "CARDS/EVIDENCE_COMAN_PRESSURE.png",
            "CARDS/EVIDENCE_COMAN_SPEAK_STIR.png",
            "GENERATED/IMG003_PRIVATE_NIGHT_TO_COURT.png",
            "ORIGINAL/SRC_EP07_Bridget_Bishop_execution_archive_scan_full_scan.png",
            "GENERATED/IMG004_BRIDGET_BISHOP_COURT_CONTEXT_RECON.png",
            "ORIGINAL/SRC_EP07_Salem_Village_1692_map_Upham_1866_full_map.png",
            "ORIGINAL/SRC_EP07_Proctors_Ledge_Memorial_full_context.png",
            "GENERATED/IMG050_PRIVATE_TO_PUBLIC_NETWORK.png",
            "CLIPS/CLIP003_SALEM_PUBLIC_TRANSFORMATION.mp4",
            "GENERATED/SHOT03_CASSETTE_NOTEBOOK_MACRO.png",
        ],
    ),
    (
        "S2_PATTERN_AND_FOLKLORE", "Look closely at Coman's sequence", "Perhaps the story begins",
        [
            "GENERATED/IMG033_AWAKE_BRAIN_BODY_LOCK.png",
            "GENERATED/IMG006_SAME_MECHANIC_DIFFERENT_ROOMS.png",
            "GENERATED/IMG005_NIGHTMARE_MOTIF_ROOM_BASE.png",
            "GENERATED/IMG026_SHARED_MECHANIC_RELIEF.png",
            "GENERATED/IMG025_MANY_ORIGINS_ARCHIVE_TABLE.png",
            "ORIGINAL/SRC_EP07_Fuseli_The_Nightmare_1781_full_painting.png",
            "ORIGINAL/SRC_EP07_Fuseli_The_Nightmare_1781_woman_detail.png",
            "ORIGINAL/SRC_EP07_Fuseli_The_Nightmare_1781_incubus_detail.png",
            "ORIGINAL/SRC_EP07_Fuseli_The_Nightmare_1781_horse_detail.png",
            "GENERATED/IMG024_NIGHTMARE_PRINT_WORKSHOP.png",
            "CLIPS/CLIP002_NIGHTMARE_PRESSURE.mp4",
            "GENERATED/IMG007_MARA_INCUBUS_KANASHIBARI_BASE.png",
            "ORIGINAL/SRC_EP07_Jinn_from_Ali_manuscript_full_manuscript.png",
            "ORIGINAL/SRC_EP07_Kunisada_The_Ghost_full_print.png",
            "GENERATED/IMG027_KANASHIBARI_THRESHOLD.png",
            "GENERATED/IMG028_NEWFOUNDLAND_ORAL_HISTORY.png",
        ],
    ),
    (
        "S3_CULTURE_AND_ACTION", "Perhaps the story begins", "The simplest modern answer",
        [
            "ORIGINAL/SRC_EP07_Abildgaard_Nightmare_1800_full_painting.png",
            "ORIGINAL/SRC_EP07_Queen_of_the_Night_Burney_Relief_full_object.png",
            "GENERATED/IMG008_BURNEY_RELIEF_SOURCE_ROOM.png",
            "GENERATED/IMG009_MEDIEVAL_BEDROOM_EXPLANATION.png",
            "GENERATED/IMG029_HOUSEHOLD_EXPLANATION_CHOICES.png",
            "GENERATED/IMG030_RITUAL_AS_PRACTICAL_RESPONSE.png",
            "GENERATED/IMG010_RITUAL_RESPONSE_TABLE.png",
            "ORIGINAL/SRC_EP07_Malleus_1494_Bull_Innocent_VIII_Wellcome_full_page.png",
            "ORIGINAL/SRC_EP07_Examination_of_a_Witch_Matteson_1853_full_painting_later_depiction.png",
            "ORIGINAL/SRC_EP07_Trial_George_Jacobs_Salem_LOC_full_later_depiction.png",
        ],
    ),
    (
        "S4_HUFFORD_REVERSAL", "The simplest modern answer", "Imagine two people waking",
        [
            "GENERATED/IMG031_HUFFORD_FIELD_INTERVIEW.png",
            "CARDS/CARD_DAVID_HUFFORD_WORK.png",
            "GENERATED/IMG011_HUFFORD_FIELD_NOTES_RECON.png",
            "GENERATED/IMG032_UNNAMED_FIRST_EPISODE.png",
            "GENERATED/IMG043_FIRST_EPISODE_BODY_TRACE.png",
            "GENERATED/IMG012_EXPERIENCE_BEFORE_STORY.png",
            "CLIPS/CLIP001_CULTURAL_MASKS.mp4",
            "GENERATED/IMG013_BODY_TO_STORY_FLOW_BASE.png",
            "GENERATED/IMG044_SAME_BODY_TWO_INTERPRETATIONS.png",
            "GENERATED/IMG049_DECISION_LAYERS_HOLD.png",
        ],
    ),
    (
        "S5_TWO_NIGHTS_AND_STUDY", "Imagine two people waking", "Association is not a one-way spell",
        [
            "GENERATED/IMG014_TWO_PEOPLE_SAME_BODY_DIFFERENT_MODEL.png",
            "GENERATED/IMG034_TWO_EXPECTATIONS_THRESHOLD.png",
            "GENERATED/IMG015_EXPERIENCE_CULTURE_DECISION_BASE.png",
            "CARDS/CARD_JALAL_HINTON_PAPER.png",
            "GENERATED/IMG035_EGYPT_INTERVIEW_CONTEXT.png",
            "MAPS/ORIG_ORIG_EGYPT_MAP_PD_full_map.png",
            "CARDS/CARD_STUDY_SCOPE.png",
            "GENERATED/IMG036_DENMARK_INTERVIEW_CONTEXT.png",
            "MAPS/ORIG_ORIG_DENMARK_MAP_PD_full_map.png",
            "CARDS/CARD_STUDY_RESULTS.png",
            "CARDS/CARD_STUDY_ASSOCIATION.png",
        ],
    ),
    (
        "S6_FEEDBACK_LOOP", "Association is not a one-way spell", "So return to Richard Coman",
        [
            "ORIGINAL/SRC_EP07_REM_Polysomnography_30sec_full_trace.png",
            "ORIGINAL/SRC_EP07_Sleep_Studies_NHLBI_Polysomnography_full_photo.png",
            "GENERATED/IMG045_EXPECTATION_ENTERS_BODY.png",
            "GENERATED/IMG046_RAW_MATERIAL_TO_FORM.png",
            "CLIPS/CLIP004_FEEDBACK_ENTITY.mp4",
            "GENERATED/IMG017_FEAR_SLEEP_FEEDBACK_LOOP_BASE.png",
            "GENERATED/IMG047_CULTURE_FEEDBACK_BRAID.png",
            "GENERATED/IMG018_STORY_BECOMES_BODY.png",
            "GENERATED/IMG048_STORY_BODY_RETURN.png",
            "GENERATED/IMG052_QUESTION_BETWEEN_MODELS.png",
        ],
    ),
    (
        "S7_RETURN_AND_SYNTHESIS", "So return to Richard Coman", "Which carries more power",
        [
            "GENERATED/IMG053_PRESSURE_PRESENCE_RELIEF.png",
            "GENERATED/IMG038_BODY_CULTURE_BRAID.png",
            "GENERATED/IMG055_CULTURAL_FORM_SETTLES.png",
            "GENERATED/IMG056_PRESSURE_AS_MEMORY_RELIEF.png",
            "GENERATED/SHOT02_MANY_NAMES_PAPER_LAYERS.png",
            "GENERATED/IMG039_GENERATIONS_OF_NIGHT_STORIES.png",
            "GENERATED/IMG057_PUBLIC_MEMORY_SHADOWS.png",
            "GENERATED/IMG061_ONE_BODY_THREE_STORIES.png",
        ],
    ),
    (
        "S8_INTERACTION", "Which carries more power", "Because the body may open the door",
        ["CARDS/CARD_EXPERIENCE_OR_STORY.png"],
    ),
    (
        "S9_FINAL_IMAGE", "Because the body may open the door", None,
        ["GENERATED/IMG060_WORD_LAYERS_CTA_BG.png", "GENERATED/SHOT04_FUSELI_TO_SCREEN_TRANSITION.png"],
    ),
]


def tc(sec: float, srt: bool = False) -> str:
    ms = round(sec * 1000)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{',' if srt else '.'}{milli:03d}"


def load() -> tuple[dict, list[dict], str]:
    data = json.loads(ALIGN.read_text(encoding="utf-8"))
    words = [w for w in data["words"] if w["text"].strip()]
    return data, words, data["source_text"]


def audio_duration() -> float:
    value = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(MASTER),
    ], text=True).strip()
    return float(value)


def phrase_time(data: dict, source: str, phrase: str) -> float:
    idx = source.casefold().find(phrase.casefold())
    if idx < 0:
        raise ValueError(f"phrase not found: {phrase}")
    return float(data["characters"][idx]["start"])


def words_in(words: list[dict], start: float, end: float, limit: int = 12) -> str:
    chosen = [w["text"] for w in words if float(w["start"]) >= start - .001 and float(w["start"]) < end - .001]
    text = " ".join(chosen[:limit])
    return text + (" …" if len(chosen) > limit else "")


def provenance(asset: str) -> tuple[str, str]:
    if asset.startswith("ORIGINAL/"):
        name = Path(asset).name
        if "NHLBI" in name:
            return "ORIGINAL_SOURCE", "NHLBI public domain"
        if "Proctors" in name:
            return "ORIGINAL_SOURCE", "CC BY-SA 4.0; attribution in register"
        if "Queen_of_the_Night" in name:
            return "ORIGINAL_SOURCE", "CC0/PD project source"
        return "ORIGINAL_SOURCE", "public domain project source"
    if asset.startswith("MAPS/"):
        return "VIEWER_MAP", "public-domain location map rebuild"
    if asset.startswith("CLIPS/"):
        return "GENERATED_CLIP", "internally generated for German EP07; approved main version"
    if asset.startswith("CARDS/EVIDENCE"):
        return "DOCUMENT_DERIVATIVE", "PD Salem document with English transcription overlay"
    if asset.startswith("CARDS/"):
        return "ENGLISH_GRAPHIC", "new in-house graphic from cited primary/scholarly data"
    return "GENERATED_STILL", "internally generated for German EP07; no authentic-portrait claim"


def build_edl() -> list[dict]:
    data, words, source = load()
    word_starts = [float(w["start"]) for w in words]
    master_end = round(audio_duration(), 3)
    shots: list[dict] = []
    seen: set[str] = set()
    for section_index, (section, start_phrase, end_phrase, assets) in enumerate(SECTIONS):
        start = 0.0 if section_index == 0 else phrase_time(data, source, start_phrase)
        end = phrase_time(data, source, end_phrase) if end_phrase else master_end
        bounds = [start]
        for i in range(1, len(assets)):
            target = start + (end - start) * i / len(assets)
            pos = bisect.bisect_left(word_starts, target)
            candidates = word_starts[max(0, pos - 1):min(len(word_starts), pos + 2)]
            snap = min(candidates, key=lambda x: abs(x - target))
            if snap <= bounds[-1] + .4:
                snap = target
            bounds.append(round(snap, 3))
        bounds.append(end)
        for i, asset in enumerate(assets):
            if asset in seen:
                raise RuntimeError(f"asset repeated: {asset}")
            seen.add(asset)
            path = ASSETS / asset
            if not path.exists():
                raise FileNotFoundError(path)
            shot_start, shot_end = round(bounds[i], 3), round(bounds[i + 1], 3)
            kind, rights = provenance(asset)
            is_clip = path.suffix.lower() == ".mp4"
            static = asset.startswith("CARDS/") or asset.startswith("MAPS/") or asset.startswith("ORIGINAL/")
            shots.append({
                "shot_id": f"SP2_{len(shots)+1:03d}", "section": section,
                "start": shot_start, "end": shot_end, "duration": round(shot_end - shot_start, 3),
                "start_tc": tc(shot_start), "end_tc": tc(shot_end),
                "asset": asset.replace("/", "\\"), "asset_abs": str(path.resolve()),
                "asset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "kind": kind, "rights": rights, "voice_beat": words_in(words, shot_start, shot_end),
                "treatment": "MCI 24→30 fps + retime + cadence QA" if is_clip else ("static evidence/viewer frame" if static else "shared 8K supersampled eased motion"),
                "x_bias": round(.28 + ((len(shots) * 37) % 44) / 100, 2),
                "y_bias": round(.32 + ((len(shots) * 29) % 36) / 100, 2),
                "zoom": round(.012 + ((len(shots) * 11) % 16) / 1000, 3),
            })
    if shots[0]["start"] > .01 or abs(shots[-1]["end"] - master_end) > .01:
        raise RuntimeError("EDL does not cover master")
    EDIT.mkdir(parents=True, exist_ok=True)
    (EDIT / "VISUAL_EDL.json").write_text(json.dumps({"episode": "EP06_EN", "voice_duration": master_end, "shot_count": len(shots), "shots": shots}, indent=2) + "\n", encoding="utf-8")
    with (EDIT / "CUE_SHEET.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields = ["shot_id", "section", "start_tc", "end_tc", "duration", "voice_beat", "asset", "kind", "rights", "treatment", "asset_sha256"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(shots)
    max_hold = max(s["duration"] for s in shots)
    over8 = [s for s in shots if s["duration"] > 8.0]
    lines = [
        "# Fine Edit Plan — Forced-Alignment Lock", "",
        f"- Voice master: `{MASTER.name}` · {master_end:.3f} s · 48 kHz mono source", f"- Picture: 1920×1080p30", f"- Exact states: {len(shots)}", f"- Longest state: {max_hold:.3f} s", f"- States over 8 s: {len(over8)} (all reviewed below)",
        "- No asset path repeats. Document detail states are continuous, never returns.",
        "- Generated 24 fps clips are motion-interpolated to 30 fps and individually retimed to their exact voice windows.", "",
        "## Review states over eight seconds", "",
    ]
    lines += [f"- `{s['shot_id']}` {s['start_tc']}–{s['end_tc']} · {s['duration']:.3f} s · `{s['asset']}` · {s['voice_beat']}" for s in over8] or ["- None."]
    lines += ["", "## Section boundaries", ""]
    for section, *_ in SECTIONS:
        subset = [s for s in shots if s["section"] == section]
        lines.append(f"- `{section}`: {subset[0]['start_tc']}–{subset[-1]['end_tc']} · {len(subset)} states")
    (EDIT / "FINE_EDIT_PLAN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return shots


def build_subtitles() -> None:
    _, words, _ = load()
    cues: list[tuple[float, float, str]] = []
    current: list[dict] = []
    for word in words:
        current.append(word)
        text = " ".join(w["text"] for w in current)
        dur = float(current[-1]["end"]) - float(current[0]["start"])
        terminal = bool(re.search(r"[.!?][\"']?$", current[-1]["text"]))
        if (terminal and len(current) >= 3) or len(current) >= 7 or len(text) >= 42 or dur >= 3.8:
            cues.append((float(current[0]["start"]), float(current[-1]["end"]), text))
            current = []
    if current:
        cues.append((float(current[0]["start"]), float(current[-1]["end"]), " ".join(w["text"] for w in current)))
    SUB.mkdir(parents=True, exist_ok=True)
    srt = []
    vtt = ["WEBVTT", ""]
    def wrap_caption(value: str) -> str:
        parts = value.split()
        if len(value) <= 34:
            return value
        best = min(range(1, len(parts)), key=lambda i: abs(len(" ".join(parts[:i])) - len(" ".join(parts[i:]))))
        return " ".join(parts[:best]) + "\n" + " ".join(parts[best:])

    wrapped = []
    for i, (start, end, text) in enumerate(cues, 1):
        end = max(end, start + .9)
        display = wrap_caption(text)
        wrapped.append(display)
        srt += [str(i), f"{tc(start, True)} --> {tc(end, True)}", display, ""]
        vtt += [f"{tc(start)} --> {tc(end)}", display, ""]
    (SUB / "EP06_EN.srt").write_text("\n".join(srt), encoding="utf-8")
    (SUB / "EP06_EN.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (SUB / "SUBTITLE_QA.json").write_text(json.dumps({"cue_count": len(cues), "max_total_characters": max(len(x.replace("\n", " ")) for x in wrapped), "max_line_characters": max(max(len(line) for line in x.splitlines()) for x in wrapped), "max_words": max(len(x[2].split()) for x in cues), "source": "ElevenLabs forced alignment against canonical script"}, indent=2) + "\n", encoding="utf-8")


def build_rights(shots: list[dict]) -> None:
    path = EP / "03_VISUALS" / "SOURCE_RIGHTS_AND_REUSE_REGISTER.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        fields = ["shot_id", "asset", "kind", "rights", "asset_sha256", "voice_beat", "start_tc", "end_tc"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(shots)


def main() -> None:
    shots = build_edl()
    build_subtitles()
    build_rights(shots)
    print(json.dumps({"shots": len(shots), "start": shots[0]["start_tc"], "end": shots[-1]["end_tc"], "max_hold": max(s["duration"] for s in shots)}, indent=2))


if __name__ == "__main__":
    main()
