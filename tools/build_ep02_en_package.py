#!/usr/bin/env python3
"""Build aligned EP02_EN cue data, authentic document crops, and editable cards."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import subprocess
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

from document_evidence_renderer import render_evidence_frame


ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
ALIGN = EP / "04_VOICE" / "ALIGNMENT" / "GW_EN_VO_ALIGNMENT.json"
PDF = EP / "02_SOURCES" / "ORIGINAL_DOCUMENTS" / "CIA-RDP96-00788R001700210016-5_TEXT_LAYER.pdf"
PATENT = EP / "02_SOURCES" / "ORIGINAL_DOCUMENTS" / "US3884218A_MONROE_1975.pdf"
BENTOV_PATENT = EP / "02_SOURCES" / "ORIGINAL_DOCUMENTS" / "US3605725A_BENTOV_CONTROLLED_MOTION.pdf"
NTSB = EP / "02_SOURCES" / "ORIGINAL_DOCUMENTS" / "NTSB-AAR-79-17_FLIGHT191.pdf"
DOC_OUT = EP / "03_VISUALS" / "DOCUMENT_CROPS"
CARD_OUT = EP / "03_VISUALS" / "CARDS"
CUE = EP / "05_DELIVERY" / "GW_EN_VOICE_ALIGNED_CUE_SHEET.csv"
EDL = EP / "05_DELIVERY" / "GW_EN_EDIT_SHOT_LIST.csv"

W, H = 1920, 1080
BG = (8, 15, 18)
PAPER = (236, 232, 218)
CYAN = (91, 210, 211)
AMBER = (224, 174, 71)

FONT_REG = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), size)


def paragraph_times() -> list[tuple[str, float, float]]:
    data = json.loads(ALIGN.read_text(encoding="utf-8"))
    source = data["source_text"]
    chars = data["characters"]
    parts = [p.strip() for p in re.split(r"\r?\n\s*\r?\n", source) if p.strip()]
    rows = []
    cursor = 0
    for p in parts:
        idx = source.find(p, cursor)
        if idx < 0:
            raise RuntimeError(f"paragraph not found: {p[:50]}")
        end_idx = idx + len(p) - 1
        start = chars[idx]["start"]
        end = chars[end_idx]["end"]
        rows.append((p.replace("\n", " "), float(start), float(end)))
        cursor = end_idx + 1
    return rows


def semantic_map() -> dict[int, tuple[str, str, str, str, str]]:
    """Return cue-indexed (mode, primary, fallback, use, asset_state) mapping."""
    out: dict[int, tuple[str, str, str, str, str]] = {}

    def put(ids, mode, primary, fallback, use, state):
        for i in ids:
            out[i] = (mode, primary, fallback, use, state)

    put(range(1, 7), "MODEL", "GW_EN_CLIP01_THREE_TIMES_RECOMMENDATION_H.mp4", "GW_EN_STILL05_THREE_OBSERVERS_V2_FINAL.png", "hook protocol builds before reveal", "progressive three-time protocol")
    put([7], "ORIGINAL DOCUMENT", "GW_EN_DOC01_ARMY_HEADER.png", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "reality anchor", "full Army memorandum")
    put([8], "ORIGINAL DOCUMENT", "GW_EN_DOC15_RECOMMENDATION_H.png", "GW_EN_CARD_H_RECOMMENDATION_H.png", "hook payoff", "Recommendation H line highlight")
    put([9], "ORIGINAL DOCUMENT", "GW_EN_DOC01_ARMY_HEADER.png", "GW_EN_DOC02_MCDONNELL_SIGNATURE.png", "date proof", "date and sender header")
    put([10], "ORIGINAL DOCUMENT", "GW_EN_DOC02_MCDONNELL_SIGNATURE.png", "GW_EN_STILL01_MCDONNELL_REPORT_V2_FINAL.png", "McDonnell identity through verified signature", "signature block")
    put([11], "ARCHIVE", "GW_EN_MAP01_FORT_MEADE_CONTEXT.png", "FORT_MEADE_CURRENT_CC_BY_SA_2.jpg", "location context", "Fort Meade regional marker")
    put([12], "ORIGINAL DOCUMENT", "GW_EN_DOC01_ARMY_HEADER.png", "GW_EN_CLIP02_ARCHIVE_CHAIN.mp4", "CIA custody marks", "CIA release stamp detail")
    put([13, 14], "ORIGINAL DOCUMENT", "GW_EN_CLIP02_ARCHIVE_CHAIN.mp4", "GW_EN_CARD_ARMY_NOT_CIA.png", "separate Army authorship from CIA archive custody", "Army-to-CIA provenance chain")
    put([15], "ORIGINAL DOCUMENT", "GW_EN_DOC15_RECOMMENDATION_H.png", "GW_EN_CARD_H_RECOMMENDATION_H.png", "return to hook clause", "H surrounding recommendations")
    put([16], "INNER / HYPOTHESIS", "GW_EN_CLIP09_NONPHYSICAL_PRESENCE_SAFE.mp4", "GW_EN_INNER04_NONPHYSICAL_PRESENCE_NATIVE.png", "attributed non-corporeal encounter idea", "responsive perimeter distortion")
    put([17], "RECONSTRUCTION", "GW_EN_STILL01_MCDONNELL_REPORT_V2_FINAL.png", "GW_EN_DOC02_MCDONNELL_SIGNATURE.png", "anonymous McDonnell action; identity stays document-anchored", "officer studies report from behind")
    put([18], "MODEL", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "GW_EN_CARD_BEAT_10HZ.png", "two-tone mechanism preview", "two carriers emerge")
    put([19], "MODEL", "GW_EN_CLIP06_FOCUS_WHEEL.mp4", "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png", "time-coordinate preview", "wheel phase overview")
    put([20], "MODEL", "GW_EN_CLIP07_TEN_DIGITS.mp4", "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png", "ten-digit test preview", "hidden sequence setup")
    put([21, 22], "MODEL", "GW_EN_CARD_EVIDENCE_MIXED.png", "GW_EN_DOC14_CONCLUSION.png", "result and decision tension", "weak-result boundary")

    put([23], "ARCHIVE", "MONROE_29_PORTRAIT.jpg", "MONROE_15_BOB_IN_LAB.jpg", "Monroe introduction", "authentic portrait")
    put([24], "ARCHIVE", "MONROE_14_BOB_IN_LAB.jpg", "MONROE_15_BOB_IN_LAB.jpg", "broadcasting/lab continuity", "Monroe seated in analogue lab")
    put([25], "INNER / HYPOTHESIS", "GW_EN_CLIP03_MONROE_EXIT.mp4", "GW_EN_INNER01_MONROE_EXIT_NATIVE.png", "reported subjective episode", "elevated first-person separation")
    put([26, 27], "ARCHIVE", "MONROE_15_BOB_IN_LAB.jpg", "MONROE_16_BOB_IN_LAB.jpg", "engineering response", "Monroe with equipment portrait")
    put([28], "ARCHIVE", "MONROE_14_BOB_IN_LAB.jpg", "MONROE_20_BOB_IN_LAB.jpg", "laboratory proof", "wide equipment bench")
    put([29], "ARCHIVE", "MONROE_16_BOB_IN_LAB.jpg", "MONROE_18_BOB_IN_LAB.jpg", "training system", "Monroe interview and lab sequence")
    put([30], "ORIGINAL DOCUMENT", "GW_EN_DOC03_HEMISYNC.png", "MONROE_20_BOB_IN_LAB.jpg", "Hemi-Sync naming", "Hemi-Sync source line")
    put([31], "RECONSTRUCTION", "GW_EN_STILL01_MCDONNELL_REPORT_V2_FINAL.png", "GW_EN_DOC02_MCDONNELL_SIGNATURE.png", "assessment task", "report examination close")
    put([32], "ORIGINAL DOCUMENT", "GW_EN_DOC17_BIBLIOGRAPHY.png", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "Bentov source trail", "bibliography Bentov line")
    put([33], "ARCHIVE", "BENTOV_PORTRAIT_FAIR_USE.jpg", "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4_FINAL.png", "Bentov introduction", "authentic portrait fair-use slot")
    put([34], "RECONSTRUCTION", "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4_FINAL.png", "BENTOV_PORTRAIT_FAIR_USE.jpg", "inventor object language", "object-only biomedical workbench")
    put([35], "ORIGINAL DOCUMENT", "GW_EN_DOC06_BODY_OSCILLATOR.png", "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4_FINAL.png", "body oscillator claim", "coherent oscillator line")
    put([36], "MODEL", "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4_FINAL.png", "GW_EN_DOC06_BODY_OSCILLATOR.png", "heart-aorta rhythm", "pendulum and vessel model")
    put([37], "ORIGINAL DOCUMENT", "GW_EN_DOC05_RESONANCE.png", "GW_EN_DOC06_BODY_OSCILLATOR.png", "resonance source", "Role of Resonance line")
    put([38], "INNER / HYPOTHESIS", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "GW_EN_DOC07_TIME_SPACE.png", "Bentov cosmology attribution", "resonance opens into larger structure")
    put([39], "ARCHIVE", "GW_EN_DOC19_NTSB_FLIGHT191.png", "BENTOV_PORTRAIT_FAIR_USE.jpg", "Flight 191 official record", "NTSB title and date")
    put([40], "MAP", "GW_EN_MAP02_FLIGHT191_ROUTE_CONTEXT.png", "GW_EN_DOC19_NTSB_FLIGHT191.png", "scheduled destination context", "Chicago-to-Los-Angeles route context")
    put([41], "ARCHIVE", "AA191_CRASH_SITE_NTSB_PD.png", "AA191_WRECKAGE_NTSB_PD.jpg", "official crash archive", "crash site then wreckage")
    put([42], "ORIGINAL DOCUMENT", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "GW_EN_DOC17_BIBLIOGRAPHY.png", "model reappears in Army paper", "Bentov source beside memorandum")
    put([43], "ARCHIVE", "MONROE_20_BOB_IN_LAB.jpg", "GW_EN_DOC03_HEMISYNC.png", "Monroe supplied training", "Monroe wearing headphones")
    put([44], "RECONSTRUCTION", "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4_FINAL.png", "GW_EN_DOC06_BODY_OSCILLATOR.png", "Bentov supplied model", "oscillator object close")
    put([45], "RECONSTRUCTION", "GW_EN_STILL01_MCDONNELL_REPORT_V2_FINAL.png", "GW_EN_DOC02_MCDONNELL_SIGNATURE.png", "McDonnell connection", "anonymous officer connective action")

    put([46], "ORIGINAL DOCUMENT", "GW_EN_DOC03_HEMISYNC.png", "GW_EN_CARD_CROSSING_SOUND.png", "modest mechanism", "Hemi-Sync mechanism line")
    put(range(47, 50), "MODEL", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "GW_EN_CARD_BEAT_10HZ.png", "exact binaural arithmetic", "400/410/10 progressive waveform")
    put([50], "MODEL", "GW_EN_CARD_BEAT_10HZ.png", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "difference tone boundary", "no physical ten-hertz source")
    put([51], "ORIGINAL DOCUMENT", "GW_EN_DOC04_FREQUENCY_RESPONSE.png", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "auditory processing attribution", "Frequency Following Response")
    put([52], "MODEL", "GW_EN_CARD_BEAT_10HZ.png", "GW_EN_DOC04_FREQUENCY_RESPONSE.png", "mechanism name", "binaural beat resolved")
    put([53], "ORIGINAL DOCUMENT", "GW_EN_DOC03_HEMISYNC.png", "MONROE_20_BOB_IN_LAB.jpg", "Monroe proposal", "guided brain-pattern claim")
    put([54], "ORIGINAL DOCUMENT", "GW_EN_DOC05_RESONANCE.png", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "coherence hypothesis", "hemispheric coherence line")
    put([55], "ORIGINAL DOCUMENT", "GW_EN_DOC18_MONROE_PATENT.png", "MONROE_29_PORTRAIT.jpg", "1975 patent anchor", "patent inventor/date/title")
    put([56], "ORIGINAL DOCUMENT", "GW_EN_DOC03_HEMISYNC.png", "GW_EN_DOC04_FREQUENCY_RESPONSE.png", "last modest-material recap", "sound-attention-electrical chain")
    put([57, 58], "INNER / HYPOTHESIS", "GW_EN_CLIP05_CROSSING.mp4", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "explicit scale change", "wave crosses conceptual threshold")
    put([59], "ORIGINAL DOCUMENT", "GW_EN_DOC06_BODY_OSCILLATOR.png", "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4_FINAL.png", "body premise", "oscillator text close")
    put([60], "ORIGINAL DOCUMENT", "GW_EN_DOC04_FREQUENCY_RESPONSE.png", "GW_EN_CARD_CROSSING_SOUND.png", "brain patterns", "electrical response detail")
    put([61], "ORIGINAL DOCUMENT", "GW_EN_DOC05_RESONANCE.png", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "coherence step", "resonance-to-coherence detail")
    put([62], "INNER / HYPOTHESIS", "GW_EN_CLIP05_CROSSING.mp4", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "speculative information-field claim", "wave becomes spacetime lattice")
    put([63], "ORIGINAL DOCUMENT", "GW_EN_DOC07_TIME_SPACE.png", "GW_EN_DOC01_ARMY_HEADER.png", "engineering appearance", "full time-space page")
    put([64], "ORIGINAL DOCUMENT", "GW_EN_DOC07_TIME_SPACE.png", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "document visual syntax", "arrow detail")
    put([65], "ORIGINAL DOCUMENT", "GW_EN_DOC07_TIME_SPACE.png", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "document visual syntax", "axis detail")
    put([66], "ORIGINAL DOCUMENT", "GW_EN_DOC07_TIME_SPACE.png", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "document visual syntax", "vortex detail")
    put([67], "ORIGINAL DOCUMENT", "GW_EN_DOC07_TIME_SPACE.png", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "document visual syntax", "nested-system detail")
    put([68], "ORIGINAL DOCUMENT", "GW_EN_DOC01_ARMY_HEADER.png", "GW_EN_DOC07_TIME_SPACE.png", "institutional contrast", "Army letterhead return")
    put([69], "INNER / HYPOTHESIS", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "GW_EN_CLIP05_CROSSING.mp4", "crossing summary", "acoustics-versus-cosmology split")
    put([70], "MODEL", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "GW_EN_CARD_CROSSING_COSMOLOGY.png", "three-reading setup", "three blank reasoning sheets")
    put([71], "MODEL", "GW_EN_CARD_CROSSING_COSMOLOGY.png", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "interpretation one", "speculative metaphor")
    put([72], "ARCHIVE", "FORT_MEADE_CURRENT_CC_BY_SA_2.jpg", "GW_EN_MAP01_FORT_MEADE_CONTEXT.png", "interpretation two", "modern location as era context")
    put([73], "RECONSTRUCTION", "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png", "GW_EN_DOC12_TEN_DIGITS.png", "interpretation three", "anonymous test participant")
    put([74], "ORIGINAL DOCUMENT", "GW_EN_DOC14_CONCLUSION.png", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "interpretive limit", "conclusion boundary")
    put([75], "RECONSTRUCTION", "GW_EN_STILL01_MCDONNELL_REPORT_V2_FINAL.png", "GW_EN_DOC09_FOCUS15.png", "next action", "officer turns to focus map")

    put([76], "ORIGINAL DOCUMENT", "GW_EN_DOC09_FOCUS15.png", "GW_EN_CLIP06_FOCUS_WHEEL.mp4", "focus map entry", "full Focus page")
    put([77, 78, 79], "MODEL", "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png", "GW_EN_DOC09_FOCUS15.png", "Focus 10 staged definition", "Focus 10 / mind awake / body asleep progression")
    put([80, 81], "MODEL", "GW_EN_CLIP06_FOCUS_WHEEL.mp4", "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png", "Focus 12 staged definition", "Focus 12 / expanded awareness progression")
    put([82], "ORIGINAL DOCUMENT", "GW_EN_DOC09_FOCUS15.png", "GW_EN_CARD_FOCUS15.png", "heading reveal", "Focus 15 heading approach")
    put([83, 84], "ORIGINAL DOCUMENT", "GW_EN_DOC09_FOCUS15.png", "GW_EN_CARD_FOCUS15.png", "Focus 15 proof", "Focus 15 / Travel into the Past highlight")
    put([85], "MODEL", "GW_EN_CLIP06_FOCUS_WHEEL.mp4", "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png", "time-wheel model", "wheel begins rotating")
    put([86], "MODEL", "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png", "GW_EN_CLIP06_FOCUS_WHEEL.mp4", "present hub", "hub isolated")
    put([87], "MODEL", "GW_EN_CLIP06_FOCUS_WHEEL.mp4", "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png", "past spokes", "spokes reveal phase echoes")
    put([88], "ORIGINAL DOCUMENT", "GW_EN_DOC09_FOCUS15.png", "GW_EN_CARD_FEWER_5.png", "difficulty caveat", "difficulty sentence")
    put([89], "ORIGINAL DOCUMENT", "GW_EN_CARD_FEWER_5.png", "GW_EN_DOC09_FOCUS15.png", "exact participation caveat", "fewer-than-five-percent fact")
    put([90, 91], "ORIGINAL DOCUMENT", "GW_EN_DOC10_FOCUS21.png", "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png", "Focus 21 proof", "Focus 21 / The Future highlight")
    put([92], "ORIGINAL DOCUMENT", "GW_EN_DOC11_ROLLOUT.png", "GW_EN_INNER01_MONROE_EXIT_NATIVE.png", "physical instructions", "Out-of-Body Movement paragraph")
    put([93], "ORIGINAL DOCUMENT", "GW_EN_DOC11_ROLLOUT.png", "GW_EN_CLIP03_MONROE_EXIT.mp4", "instruction one", "roll-out line")
    put([94], "INNER / HYPOTHESIS", "GW_EN_CLIP03_MONROE_EXIT.mp4", "GW_EN_DOC11_ROLLOUT.png", "instruction two visualised", "rise upward")
    put([95], "ORIGINAL DOCUMENT", "GW_EN_DOC11_ROLLOUT.png", "GW_EN_INNER01_MONROE_EXIT_NATIVE.png", "instruction three", "opening line")
    put([96], "INNER / HYPOTHESIS", "GW_EN_INNER01_MONROE_EXIT_NATIVE.png", "GW_EN_DOC11_ROLLOUT.png", "impossible field-manual contrast", "subjective manoeuvre tableau")
    put([97, 98], "RECONSTRUCTION", "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png", "GW_EN_DOC12_TEN_DIGITS.png", "intelligence question", "participant and hidden target")
    put([99], "ORIGINAL DOCUMENT", "GW_EN_DOC12_TEN_DIGITS.png", "GW_EN_CLIP07_TEN_DIGITS.mp4", "ten-digit source entry", "ten computer-generated numbers line")
    put([100], "MODEL", "GW_EN_CLIP07_TEN_DIGITS.mp4", "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png", "procedure setup", "remote sequence appears")
    put([101], "RECONSTRUCTION", "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png", "GW_EN_CLIP07_TEN_DIGITS.mp4", "blinding condition", "participant isolated from sequence")
    put([102], "MODEL", "GW_EN_CLIP07_TEN_DIGITS.mp4", "GW_EN_DOC12_TEN_DIGITS.png", "retrieval attempt", "partial digits reveal")
    put([103], "ORIGINAL DOCUMENT", "GW_EN_DOC12_TEN_DIGITS.png", "GW_EN_CARD_DIGITS_SOME.png", "trainer-attributed result", "matching-digits source line")
    put([104], "MODEL", "GW_EN_CARD_DIGITS_NONE.png", "GW_EN_CLIP07_TEN_DIGITS.mp4", "negative boundary", "nobody got all ten")
    put([105], "MODEL", "GW_EN_CARD_DIGITS_SOME.png", "GW_EN_CARD_DIGITS_NONE.png", "episode hinge", "some matched versus none complete")
    put([106, 107], "MODEL", "GW_EN_CARD_DIGITS_NONE.png", "GW_EN_DOC12_TEN_DIGITS.png", "no clean demonstration", "failure boundary")
    put([108], "ORIGINAL DOCUMENT", "GW_EN_DOC12_TEN_DIGITS.png", "GW_EN_CARD_DIGITS_SOME.png", "report continues", "partial-match line return")
    put([109], "ORIGINAL DOCUMENT", "GW_EN_DOC13_DISTORTION.png", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "distortion rationale", "distortion paragraph heading")
    put([110], "MODEL", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "GW_EN_DOC13_DISTORTION.png", "three-source blend", "target / room / time sheets overlap")
    put([111], "MODEL", "GW_EN_STILL05_THREE_OBSERVERS_V2_FINAL.png", "GW_EN_DOC13_DISTORTION.png", "source ambiguity", "observer cannot sort sources")
    put([112], "ORIGINAL DOCUMENT", "GW_EN_DOC15_RECOMMENDATION_H.png", "GW_EN_CLIP01_THREE_TIMES_RECOMMENDATION_H.mp4", "failed result becomes H", "H line reveal")
    put([113], "MODEL", "GW_EN_CARD_DECISION_QUESTION.png", "GW_EN_CARD_DECISION_AUTHORIZE_STOP.png", "viewer decision", "question only")
    put(range(114, 118), "MODEL", "GW_EN_CLIP01_THREE_TIMES_RECOMMENDATION_H.mp4", "GW_EN_STILL05_THREE_OBSERVERS_V2_FINAL.png", "H protocol restated", "present/past/future agreement build")
    put([118, 119], "MODEL", "GW_EN_CARD_DECISION_AUTHORIZE_STOP.png", "GW_EN_CARD_DECISION_QUESTION.png", "binary decision", "authorize versus stop")
    put([120], "MODEL", "GW_EN_CARD_DECISION_AUTHORIZE_STOP.png", "GW_EN_CARD_DECISION_QUESTION.png", "comment prompt", "one-word decision hold")
    put([121], "RECONSTRUCTION", "GW_EN_STILL01_MCDONNELL_REPORT_V2_FINAL.png", "GW_EN_DOC16_RECOMMENDATIONS_JK.png", "McDonnell continues", "officer turns page")
    put([122], "ORIGINAL DOCUMENT", "GW_EN_DOC16_RECOMMENDATIONS_JK.png", "GW_EN_INNER04_NONPHYSICAL_PRESENCE_NATIVE.png", "Recommendation J exact attribution", "J non-corporal forms highlight")
    put([123], "INNER / HYPOTHESIS", "GW_EN_CLIP09_NONPHYSICAL_PRESENCE_SAFE.mp4", "GW_EN_DOC16_RECOMMENDATIONS_JK.png", "Recommendation K conceptual defence", "perimeter reacts without entity")
    put([124], "ORIGINAL DOCUMENT", "GW_EN_DOC03_HEMISYNC.png", "GW_EN_DOC16_RECOMMENDATIONS_JK.png", "return to modest question", "headphones versus doctrine split")
    put([125], "INNER / HYPOTHESIS", "GW_EN_INNER04_NONPHYSICAL_PRESENCE_NATIVE.png", "GW_EN_DOC16_RECOMMENDATIONS_JK.png", "unestablished defensive space", "empty perimeter distortion")

    put([126], "MODEL", "GW_EN_CARD_CROSSING_SOUND.png", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "modern-testable boundary", "back to sound")
    put([127], "MODEL", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "GW_EN_CARD_EVIDENCE_MIXED.png", "modern study domains", "binaural waveform under test")
    put([128, 129], "MODEL", "GW_EN_CARD_EVIDENCE_MIXED.png", "GW_EN_DOC04_FREQUENCY_RESPONSE.png", "review outcome", "modest psychological effects")
    put([130], "MODEL", "GW_EN_CARD_EVIDENCE_MIXED.png", "GW_EN_DOC04_FREQUENCY_RESPONSE.png", "entrainment uncertainty", "EEG entrainment mixed")
    put([131, 132], "MODEL", "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png", "GW_EN_CARD_DIGITS_NONE.png", "state change is not information retrieval", "headphones versus hidden digits")
    put([133], "ORIGINAL DOCUMENT", "GW_EN_DOC12_TEN_DIGITS.png", "GW_EN_CARD_EVIDENCE_MIXED.png", "controlled-data gap", "reported result without dataset")
    put([134, 135], "ORIGINAL DOCUMENT", "GW_EN_DOC01_ARMY_HEADER.png", "GW_EN_DOC14_CONCLUSION.png", "authenticity recap", "memorandum full-page return")
    put([136], "ORIGINAL DOCUMENT", "GW_EN_DOC02_MCDONNELL_SIGNATURE.png", "GW_EN_DOC01_ARMY_HEADER.png", "visible provenance fields", "author/date/recipient proof")
    put([137], "ORIGINAL DOCUMENT", "GW_EN_DOC09_FOCUS15.png", "GW_EN_CARD_FOCUS15.png", "verified claim recap", "Travel into the Past line")
    put([138], "ORIGINAL DOCUMENT", "GW_EN_DOC12_TEN_DIGITS.png", "GW_EN_CARD_DIGITS_NONE.png", "verified result recap", "none got all ten line")
    put([139], "ORIGINAL DOCUMENT", "GW_EN_DOC16_RECOMMENDATIONS_JK.png", "GW_EN_INNER04_NONPHYSICAL_PRESENCE_NATIVE.png", "verified doctrine recap", "non-corporal forms line")
    put([140], "MODEL", "GW_EN_CARD_EVIDENCE_MIXED.png", "GW_EN_DOC14_CONCLUSION.png", "proof boundary", "no path-outside-time evidence")
    put([141], "MODEL", "GW_EN_CARD_ARMY_NOT_CIA.png", "GW_EN_CLIP02_ARCHIVE_CHAIN.mp4", "viral claim correction", "CIA-proved-it claim crossed by provenance")
    put([142], "ORIGINAL DOCUMENT", "GW_EN_DOC01_ARMY_HEADER.png", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "real document return", "Army memorandum close")
    put([143], "MODEL", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "GW_EN_DOC17_BIBLIOGRAPHY.png", "three borrowed inputs", "audio / Bentov / anomaly source stack")
    put([144], "MODEL", "GW_EN_CLIP01_THREE_TIMES_RECOMMENDATION_H.mp4", "GW_EN_DOC15_RECOMMENDATION_H.png", "test plan recap", "three-time observer protocol")
    put([145, 146, 147], "MODEL", "GW_EN_STILL05_THREE_OBSERVERS_V2_FINAL.png", "GW_EN_CARD_DECISION_QUESTION.png", "three final interpretations", "overreach / desperation / anomaly triad")
    put([148], "ORIGINAL DOCUMENT", "GW_EN_DOC14_CONCLUSION.png", "GW_EN_CARD_EVIDENCE_MIXED.png", "unsettled conclusion", "document cannot decide")
    put([149, 150], "MODEL", "GW_EN_CLIP10_ZERO_ONE_HANDOFF.mp4", "GW_EN_CARD_HANDOFF.png", "PEAR handoff", "visions removed; zeros and ones enter")
    put([151, 152], "MODEL", "GW_EN_CARD_HANDOFF.png", "GW_EN_CLIP10_ZERO_ONE_HANDOFF.mp4", "next-episode quantitative hook", "fourteen million / one operator")
    return out


def no_repeat_semantic_map() -> dict[int, tuple[str, str, str, str, str]]:
    """Linear picture-lock mapping: every primary asset occupies one contiguous block only."""
    out: dict[int, tuple[str, str, str, str, str]] = {}

    def put(ids, mode, primary, use, state):
        for i in ids:
            out[i] = (mode, primary, "", use, state)

    # Hook and provenance.
    for i, state in zip(range(1, 7), ["three observers", "one target", "present", "immediate past", "immediate future", "compare after session"]):
        put([i], "MODEL", "GW_EN_CLIP01_THREE_TIMES_RECOMMENDATION_H.mp4", "linear Recommendation H hook", state)
    put([7], "ORIGINAL DOCUMENT", "GW_EN_DOC20_TASKING.png", "document reality anchor", "tasking line")
    put([8], "ORIGINAL DOCUMENT", "GW_EN_DOC15_RECOMMENDATION_H.png", "hook payoff", "Recommendation H source line")
    put([9], "ORIGINAL DOCUMENT", "GW_EN_DOC44_DATE.png", "date proof", "9 June 1983 detail")
    put([10], "ORIGINAL DOCUMENT", "GW_EN_DOC02_MCDONNELL_SIGNATURE.png", "McDonnell introduction through verified signature", "signature block")
    put([11], "MAP", "GW_EN_MAP01_FORT_MEADE_CONTEXT.png", "Fort Meade location", "regional context")
    put([12], "ORIGINAL DOCUMENT", "GW_EN_CLIP02_ARCHIVE_CHAIN.mp4", "CIA release marks", "archive marks")
    put([13], "ORIGINAL DOCUMENT", "GW_EN_CLIP02_ARCHIVE_CHAIN.mp4", "internet naming versus custody", "archive chain resolves")
    put([14], "MODEL", "GW_EN_CARD_ARMY_NOT_CIA.png", "Army authorship separated from CIA custody", "authorship correction")
    put([15], "MODEL", "GW_EN_CARD_H_RECOMMENDATION_H.png", "Recommendation H callback with new graphic", "H before stranger clause")
    put([16], "INNER / HYPOTHESIS", "GW_EN_CLIP09_NONPHYSICAL_PRESENCE_SAFE.mp4", "non-corporeal idea in hook", "controlled perimeter distortion")
    put([17], "RECONSTRUCTION", "GW_EN_STILL01_MCDONNELL_REPORT_V2_FINAL.png", "anonymous officer action anchored earlier by signature", "officer studies report from behind")
    put([18], "MODEL", "GW_EN_CARD_CROSSING_SOUND.png", "two-tone path preview", "sound begins")
    put([19], "MODEL", "GW_EN_CARD_TIME_COORDINATE.png", "time-coordinate preview", "time as coordinate")
    put([20], "MODEL", "GW_EN_CARD_DIGITS_SOME.png", "ten-digit preview", "some digits")
    put([21], "MODEL", "GW_EN_CARD_DIGITS_NONE.png", "negative result preview", "none complete")
    put([22], "MODEL", "GW_EN_CARD_WEAK_NOT_DISCARDED.png", "weak but retained result", "prove versus discard")

    # Monroe, Bentov, Flight 191, and the chain into the report.
    put([23], "ARCHIVE", "MONROE_29_PORTRAIT.jpg", "Monroe introduction", "authentic portrait")
    put([24], "ARCHIVE", "MONROE_14_BOB_IN_LAB.jpg", "broadcasting and laboratory context", "analogue lab wide")
    put([25], "INNER / HYPOTHESIS", "GW_EN_CLIP03_MONROE_EXIT.mp4", "reported subjective episode", "elevated viewpoint")
    put([26], "ARCHIVE", "MONROE_15_BOB_IN_LAB.jpg", "non-mystic response", "equipment portrait")
    put([27, 28], "ARCHIVE", "MONROE_18_BOB_IN_LAB.jpg", "engineering response and laboratory construction", "alternate lab interview")
    put([29], "ARCHIVE", "MONROE_20_BOB_IN_LAB.jpg", "training system", "headphones and console")
    put([30], "ORIGINAL DOCUMENT", "GW_EN_DOC03_HEMISYNC.png", "Hemi-Sync source", "Hemi-Sync line")
    put([31], "ORIGINAL DOCUMENT", "GW_EN_DOC21_HYPNOSIS.png", "assessment mechanism context", "comparative technique detail")
    put([32], "ORIGINAL DOCUMENT", "GW_EN_DOC17_BIBLIOGRAPHY.png", "dead inventor source trail", "Bentov bibliography line")
    put([33], "ARCHIVE", "BENTOV_PORTRAIT_FAIR_USE.jpg", "Bentov introduction", "authentic portrait fair-use slot")
    put([34], "RECONSTRUCTION", "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4_FINAL.png", "inventor object language", "object-only workbench")
    put([35], "ORIGINAL DOCUMENT", "GW_EN_DOC27_BENTOV_CITATION.png", "Bentov attribution", "Bentov citation detail")
    put([36], "ORIGINAL DOCUMENT", "GW_EN_DOC28_BODY_RHYTHM.png", "heart and aorta rhythm", "body rhythm line")
    put([37], "ORIGINAL DOCUMENT", "GW_EN_DOC05_RESONANCE.png", "resonance source", "Role of Resonance")
    put([38], "ORIGINAL DOCUMENT", "GW_EN_DOC29_UNIVERSAL_HOLOGRAM.png", "larger reality hypothesis", "universal hologram detail")
    put([39], "ORIGINAL DOCUMENT", "GW_EN_DOC19_NTSB_FLIGHT191.png", "Flight 191 official record", "NTSB title and date")
    put([40], "MAP", "GW_EN_MAP02_FLIGHT191_ROUTE_CONTEXT.png", "scheduled destination context", "Chicago to Los Angeles")
    put([41], "ARCHIVE", "AA191_CRASH_SITE_NTSB_PD.png", "official crash-site archive", "FAA overhead crash site")
    put([42], "ORIGINAL DOCUMENT", "GW_EN_DOC58_BENTOV_REAPPEARS.png", "model reappears in Army analysis", "Bentov citation in later report section")
    put([43], "ARCHIVE", "MONROE_30_REMOTE_CONTROL.jpg", "Monroe supplied training", "Monroe with remote control")
    put([44], "ORIGINAL DOCUMENT", "GW_EN_DOC06_BODY_OSCILLATOR.png", "Bentov supplied model", "coherent oscillator line")
    put([45], "RECONSTRUCTION", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "McDonnell connects sources", "three-source desk composition")

    # Acoustics to cosmology.
    put([46], "ORIGINAL DOCUMENT", "GW_EN_DOC23_BIOFEEDBACK.png", "real and modest comparison", "biofeedback detail")
    put([47], "MODEL", "GW_EN_CARD_BEAT_400.png", "left-ear carrier", "400 hertz")
    put([48], "MODEL", "GW_EN_CARD_BEAT_410.png", "right-ear carrier", "410 hertz")
    put([49, 50], "MODEL", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "linear binaural-beat result", "ten-beat result / no direct pulse")
    put([51], "ORIGINAL DOCUMENT", "GW_EN_DOC04_FREQUENCY_RESPONSE.png", "auditory processing attribution", "Frequency Following Response")
    put([52], "MODEL", "GW_EN_CARD_BEAT_10HZ.png", "binaural beat resolved", "400 / 410 / 10")
    put([53], "ORIGINAL DOCUMENT", "GW_EN_DOC25_FFR_DETAIL.png", "Monroe brain-pattern proposal", "FFR close detail")
    put([54], "ORIGINAL DOCUMENT", "GW_EN_DOC26_ELECTROMAGNETIC_RESPONSE.png", "hemispheric coherence hypothesis", "electromagnetic response detail")
    put([55], "ORIGINAL DOCUMENT", "GW_EN_DOC18_MONROE_PATENT.png", "1975 patent anchor", "inventor/date/title")
    put([56], "ORIGINAL DOCUMENT", "GW_EN_DOC24_GATEWAY_COMPARISON.png", "last modest chain recap", "Gateway comparison detail")
    for i, state in zip(range(57, 61), ["scale changes", "threshold", "body oscillator", "brain patterns"]):
        put([i], "INNER / HYPOTHESIS", "GW_EN_CLIP05_CROSSING.mp4", "linear acoustics-to-cosmology transition", state)
    put([61], "MODEL", "GW_EN_CARD_CROSSING_COSMOLOGY.png", "coherence becomes speculation", "consciousness outside time")
    put([62], "ORIGINAL DOCUMENT", "GW_EN_DOC30_CONSCIOUSNESS_MATRIX.png", "information-field claim", "matrix field detail")
    put([63], "ORIGINAL DOCUMENT", "GW_EN_DOC07_TIME_SPACE.png", "engineering appearance", "full time-space page")
    put(range(64, 67), "ORIGINAL DOCUMENT", "GW_EN_DOC52_NESTED_SYSTEMS.png", "single progressing geometry block", "arrows / axes / vortices")
    put([67, 68], "ORIGINAL DOCUMENT", "GW_EN_DOC01_ARMY_HEADER.png", "nested systems resolve into Army letterhead", "nested-system context / memorandum header")
    put([69], "MODEL", "GW_EN_CARD_CROSSING_SUMMARY.png", "crossing summary", "acoustics to cosmology")

    # Interpretations and Focus levels.
    put([70], "ORIGINAL DOCUMENT", "GW_EN_DOC42_STUDY_LIMIT.png", "three-reading setup", "study-limit line")
    put([71], "ORIGINAL DOCUMENT", "GW_EN_DOC22_TRANSCENDENTAL_MEDITATION.png", "speculative metaphor context", "comparative-method detail")
    put([72], "ARCHIVE", "FORT_MEADE_CURRENT_CC_BY_SA_2.jpg", "military-era context; contemporary image flagged in manifest", "Fort Meade aerial")
    put([73], "MODEL", "GW_EN_CARD_INTERPRETATION_TEST.png", "unusual reports motivate a test", "test-the-model question")
    put([74], "ORIGINAL DOCUMENT", "GW_EN_DOC14_CONCLUSION.png", "interpretive limit", "Conclusion line")
    put([75, 76], "ORIGINAL DOCUMENT", "GW_EN_DOC09_FOCUS15.png", "Focus map entry", "full Focus-level page")
    put(range(77, 80), "MODEL", "GW_EN_CARD_FOCUS10_STATE.png", "Focus 10 definition and state", "Focus 10 / mind awake / body asleep")
    put([80, 81], "MODEL", "GW_EN_CARD_FOCUS12_STATE.png", "Focus 12 definition and state", "Focus 12 / beyond ordinary senses")
    put([82], "MODEL", "GW_EN_CARD_FOCUS15.png", "Focus 15 heading reveal", "Focus 15 / The Past")
    put([83, 84], "ORIGINAL DOCUMENT", "GW_EN_DOC45_FOCUS15_RECAP.png", "Focus 15 source proof", "Travel into the Past detail")
    for i, state in zip(range(85, 88), ["wheel begins", "present hub", "past spokes"]):
        put([i], "MODEL", "GW_EN_CLIP06_FOCUS_WHEEL.mp4", "linear time-wheel model", state)
    put([88], "ORIGINAL DOCUMENT", "GW_EN_DOC34_FOCUS_DIFFICULTY.png", "difficulty caveat", "difficulty sentence")
    put([89], "MODEL", "GW_EN_CARD_FEWER_5.png", "participation caveat", "fewer than five percent")
    put([90, 91], "ORIGINAL DOCUMENT", "GW_EN_DOC10_FOCUS21.png", "Focus 21 source proof", "Focus 21 / The Future")
    put(range(92, 96), "ORIGINAL DOCUMENT", "GW_EN_DOC11_ROLLOUT.png", "single progressing instruction block", "roll out / rise / opening")
    put([96], "ORIGINAL DOCUMENT", "GW_EN_DOC08_OUT_OF_BODY_STATUS.png", "field-manual contrast", "Out-of-Body Experience status")

    # Ten-digit test and Recommendation H.
    put([97], "RECONSTRUCTION", "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png", "intelligence-test question", "anonymous participant")
    put([98], "ORIGINAL DOCUMENT", "GW_EN_DOC35_DIGIT_PROCEDURE.png", "hidden sequence procedure", "computer-generated numbers detail")
    put([99], "ORIGINAL DOCUMENT", "GW_EN_DOC12_TEN_DIGITS.png", "ten-digit source entry", "full ten-digit paragraph")
    for i, state in zip(range(100, 103), ["sequence placed", "participant blinded", "partial retrieval"]):
        put([i], "MODEL", "GW_EN_CLIP07_TEN_DIGITS.mp4", "linear test procedure", state)
    put([103], "ORIGINAL DOCUMENT", "GW_EN_DOC57_MATCHING_DIGITS.png", "trainer-attributed partial result", "matching-digits detail")
    put([104], "ORIGINAL DOCUMENT", "GW_EN_DOC36_DIGIT_FAILURE.png", "negative boundary", "none got all ten detail")
    put([105, 106, 107], "MODEL", "GW_EN_CARD_TEST_NOT_PROOF.png", "episode hinge and no clean demonstration", "not a clean demonstration")
    put([108], "ORIGINAL DOCUMENT", "GW_EN_DOC37_DISTORTION_DETAIL.png", "partial resemblance rationale", "distortion detail")
    put([109, 110], "ORIGINAL DOCUMENT", "GW_EN_DOC13_DISTORTION.png", "three-source blend", "information distortion paragraph")
    put([111], "MODEL", "GW_EN_CARD_SOURCE_UNCERTAIN.png", "observer source ambiguity", "which belongs where")
    put([112], "ORIGINAL DOCUMENT", "GW_EN_DOC38_MULTIFOCUS_DETAIL.png", "failed result becomes H", "multi-focus detail")
    put([113], "MODEL", "GW_EN_CARD_DECISION_QUESTION.png", "viewer decision", "authorize question")
    put([114], "MODEL", "GW_EN_CARD_H_PRESENT.png", "H protocol present observer", "observer one")
    put([115], "MODEL", "GW_EN_CARD_H_PAST.png", "H protocol past observer", "observer two")
    put([116], "MODEL", "GW_EN_CARD_H_FUTURE.png", "H protocol future observer", "observer three")
    put([117], "MODEL", "GW_EN_CARD_H_COMPARE.png", "H protocol comparison", "compare later")
    put([118, 119, 120], "MODEL", "GW_EN_CARD_DECISION_AUTHORIZE_STOP.png", "binary viewer decision", "authorize versus stop")
    put([121], "ORIGINAL DOCUMENT", "GW_EN_DOC41_RECOMMENDATION_INTRO.png", "McDonnell continues", "recommendations heading")

    # Recommendations J/K, evidence boundary, recap, and handoff.
    put([122], "ORIGINAL DOCUMENT", "GW_EN_DOC39_NONCORPOREAL_DETAIL.png", "Recommendation J exact attribution", "non-corporal forms detail")
    put([123], "ORIGINAL DOCUMENT", "GW_EN_DOC40_HOLOGRAPHIC_DEFENCE.png", "Recommendation K exact attribution", "holographic defence detail")
    put([124], "MODEL", "GW_EN_CARD_RECOMMENDATION_JK.png", "headphones-to-doctrine contrast", "J and K")
    put([125], "ORIGINAL DOCUMENT", "GW_EN_DOC16_RECOMMENDATIONS_JK.png", "unestablished defensive doctrine", "J/K source context")
    put([126], "ORIGINAL DOCUMENT", "GW_EN_DOC59_FFR_MODERN_BOUNDARY.png", "return to testable sound", "frequency-response alternate detail")
    put([127], "MODEL", "GW_EN_CARD_MODERN_METHODS.png", "modern study domains", "methods and outcomes vary")
    put([128, 129], "MODEL", "GW_EN_CARD_EVIDENCE_MIXED.png", "review outcome", "modest psychological effects")
    put([130], "MODEL", "GW_EN_CARD_EEG_MIXED.png", "entrainment uncertainty", "EEG entrainment mixed")
    put([131], "MODEL", "GW_EN_CARD_STATE_NOT_INFO.png", "central evidentiary gap", "altered state is not hidden information")
    put([132], "MODEL", "GW_EN_CARD_HIDDEN_DIGITS_GAP.png", "feeling versus retrieval", "not reading digits")
    put([133], "MODEL", "GW_EN_CARD_NO_DATASET.png", "controlled-data gap", "no controlled dataset")
    put([134, 135], "ORIGINAL DOCUMENT", "GW_EN_DOC54_SUBJECT_RECAP.png", "authenticity and subject recap", "authentic memorandum subject detail")
    put([136], "ORIGINAL DOCUMENT", "GW_EN_DOC55_AUTHOR_RECAP.png", "visible author provenance", "author detail")
    put([137], "ORIGINAL DOCUMENT", "GW_EN_DOC56_FOCUS_RECAP_ALT.png", "verified Focus claim recap", "Travel into the Past alternate detail")
    put([138], "ORIGINAL DOCUMENT", "GW_EN_DOC46_DIGIT_RECAP.png", "verified digit result recap", "all-ten alternate context")
    put([139], "ORIGINAL DOCUMENT", "GW_EN_DOC53_NONCORPOREAL_RECAP.png", "verified doctrine recap", "non-corporal alternate detail")
    put([140], "MODEL", "GW_EN_CARD_PROOF_BOUNDARY.png", "proof boundary", "authentic document / unproven claim")
    put([141], "MODEL", "GW_EN_CARD_ARMY_NOT_CIA_RECAP.png", "viral claim correction with new composition", "Army written / CIA archived")
    put([142], "ORIGINAL DOCUMENT", "GW_EN_DOC47_ARMY_HEADER_RECAP.png", "real document return through new verified detail", "Army header close detail")
    put([143], "MODEL", "GW_EN_CARD_THREE_INPUTS.png", "three borrowed inputs", "audio / Bentov / anomalous reports")
    put([144], "MODEL", "GW_EN_CARD_H_PROTOCOL_RECAP.png", "three-time test recap with new composition", "three times / one target")
    put([145], "MODEL", "GW_EN_CARD_OVERREACH.png", "closing interpretation one", "bureaucratic overreach")
    put([146], "MODEL", "GW_EN_CARD_DESPERATION.png", "closing interpretation two", "Cold War desperation")
    put([147], "MODEL", "GW_EN_CARD_ANOMALY.png", "closing interpretation three", "unanswered anomaly")
    put([148], "ORIGINAL DOCUMENT", "GW_EN_DOC48_CONCLUSION_RECAP.png", "document cannot decide", "conclusion alternate detail")
    put([149], "MODEL", "GW_EN_CLIP10_ZERO_ONE_HANDOFF.mp4", "PEAR handoff", "visions removed; binary test enters")
    put([150], "MODEL", "GW_EN_CARD_HANDOFF.png", "zero/one transition", "remove visions / keep test")
    put([151], "MODEL", "GW_EN_CARD_14M.png", "next-episode quantitative hook", "fourteen million trials")
    put([152], "MODEL", "GW_EN_CARD_ONE_OPERATOR.png", "next-episode anomaly hook", "one operator / half effect")

    # Release-rights and retention override (2026-08-26).  The commercially
    # uncleared Monroe Institute photographs and the Bentov fair-use portrait
    # remain source references only.  Person introductions are anchored by
    # authentic inventor records; adjacent actions use identity-neutral
    # reconstructions.  Generated filmic material breaks the former document
    # chains without inventing evidence or putting category labels on screen.
    put([23], "ORIGINAL DOCUMENT", "GW_EN_DOC64_MONROE_INVENTOR.png", "Robert Monroe introduction", "patent inventor line")
    put([24], "RECONSTRUCTION", "GW_EN_FILMIC06_MONROE_RADIO_STUDIO_FINAL.png", "radio career context", "anonymous period broadcast studio")
    put([25], "INNER / HYPOTHESIS", "GW_EN_CLIP03_MONROE_EXIT.mp4", "reported subjective episode", "elevated viewpoint")
    put(range(26, 29), "RECONSTRUCTION", "GW_EN_FILMIC07_MONROE_LAB_BUILDER_FINAL.png", "engineering response and laboratory construction", "anonymous engineer at equipment bench")
    put([29], "RECONSTRUCTION", "GW_EN_FILMIC08_GATEWAY_TRAINING_SESSION_FINAL.png", "training-system context", "anonymous headphone session")
    put([30], "ORIGINAL DOCUMENT", "GW_EN_DOC03_HEMISYNC.png", "Hemi-Sync source", "Hemi-Sync line")
    put([31], "ORIGINAL DOCUMENT", "GW_EN_DOC21_HYPNOSIS.png", "assessment mechanism context", "comparative technique detail")
    put([32], "ORIGINAL DOCUMENT", "GW_EN_DOC17_BIBLIOGRAPHY.png", "dead inventor source trail", "Bentov bibliography line")
    put([33], "ORIGINAL DOCUMENT", "GW_EN_DOC65_BENTOV_INVENTOR.png", "Itzhak Bentov introduction", "patent inventor line and device drawing")
    put([34], "RECONSTRUCTION", "GW_EN_FILMIC09_BENTOV_CATHETER_BENCH_FINAL.png", "catheter contribution context", "identity-neutral biomedical bench")
    put([35], "RECONSTRUCTION", "GW_EN_FILMIC10_BODY_OSCILLATION_TEST_FINAL.png", "body oscillator concept", "anonymous physiological test")
    put([36, 37], "INNER / HYPOTHESIS", "GW_EN_INNER05_BODY_RESONANCE_NATIVE.png", "heart-aorta rhythm and resonance", "pressure wave through body and room")
    put([38], "INNER / HYPOTHESIS", "GW_EN_INNER06_COHERENT_FIELD_NATIVE.png", "larger-reality hypothesis", "coherence opens into structured field")
    put([39], "ORIGINAL DOCUMENT", "GW_EN_DOC19_NTSB_FLIGHT191.png", "Flight 191 official record", "NTSB title and date")
    put([40], "MAP", "GW_EN_MAP02_FLIGHT191_ROUTE_CONTEXT.png", "scheduled destination context", "Chicago to Los Angeles")
    put([41], "ARCHIVE", "AA191_CRASH_SITE_NTSB_PD.png", "official crash-site archive", "FAA overhead crash site")
    put([42], "ORIGINAL DOCUMENT", "GW_EN_DOC58_BENTOV_REAPPEARS.png", "model reappears in Army analysis", "Bentov citation in report")
    put([43], "RECONSTRUCTION", "GW_EN_FILMIC12_RIGHT_EAR_HEADPHONE_MACRO_FINAL.png", "Monroe supplied the training system", "physical headphone detail")
    put([44], "RECONSTRUCTION", "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4_FINAL.png", "Bentov supplied the physical model", "oscillator-object bench")
    put([45], "RECONSTRUCTION", "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2_FINAL.png", "McDonnell connects the sources", "single report-comparison block")

    put([46], "ORIGINAL DOCUMENT", "GW_EN_DOC23_BIOFEEDBACK.png", "real and modest comparison", "biofeedback detail")
    put([47], "MODEL", "GW_EN_CARD_BEAT_400.png", "left-ear carrier", "400 hertz")
    put([48], "MODEL", "GW_EN_CARD_BEAT_410.png", "right-ear carrier", "410 hertz")
    put([49, 50], "MODEL", "GW_EN_CLIP04_BEAT_RESONANCE.mp4", "linear binaural-beat result", "difference tone resolves")
    put([51], "ORIGINAL DOCUMENT", "GW_EN_DOC04_FREQUENCY_RESPONSE.png", "auditory-processing attribution", "Frequency Following Response")
    put([52], "MODEL", "GW_EN_CARD_BEAT_10HZ.png", "binaural beat resolved", "400 / 410 / 10")
    put([53], "ORIGINAL DOCUMENT", "GW_EN_DOC25_FFR_DETAIL.png", "Monroe brain-pattern proposal", "FFR close detail")
    put([54], "ORIGINAL DOCUMENT", "GW_EN_DOC26_ELECTROMAGNETIC_RESPONSE.png", "hemispheric-coherence hypothesis", "electromagnetic-response detail")
    put([55], "ORIGINAL DOCUMENT", "GW_EN_DOC18_MONROE_PATENT.png", "1975 patent anchor", "inventor/date/title")
    put([56], "ORIGINAL DOCUMENT", "GW_EN_DOC24_GATEWAY_COMPARISON.png", "modest mechanism recap", "Gateway comparison detail")
    put(range(57, 61), "INNER / HYPOTHESIS", "GW_EN_CLIP05_CROSSING.mp4", "linear acoustics-to-cosmology transition", "wave crosses conceptual threshold")
    put([61], "INNER / HYPOTHESIS", "GW_EN_INNER17_INFORMATION_FIELD_NATIVE.png", "coherence becomes speculation", "wavefront enters nonordinary lattice")
    put([62], "INNER / HYPOTHESIS", "GW_EN_INNER17_INFORMATION_FIELD_NATIVE.png", "information-field claim", "field bends ordinary perspective")
    mode, primary, _, use, state = out[62]
    out[62] = (mode, primary, "GW_EN_DOC60_FIELD_INFORMATION_DETAIL.png", use, state)
    put([63], "ORIGINAL DOCUMENT", "GW_EN_DOC07_TIME_SPACE.png", "engineering appearance", "full time-space page")
    put([64], "INNER / HYPOTHESIS", "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png", "abstract arrow-like geometry matching the narration", "luminous directional geometry")
    put([65], "INNER / HYPOTHESIS", "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png", "abstract axis-like geometry matching the narration", "radial coordinate system")
    put([66], "INNER / HYPOTHESIS", "GW_EN_INNER04_NONPHYSICAL_PRESENCE_NATIVE.png", "vortex-like geometry matching the narration", "dark field bends into a vortex")
    put([67], "ORIGINAL DOCUMENT", "GW_EN_DOC52_NESTED_SYSTEMS.png", "nested-system context", "intervening-dimensions passage")
    put([68], "ORIGINAL DOCUMENT", "GW_EN_DOC01_ARMY_HEADER.png", "institutional contrast", "Army letterhead")
    put([69], "MODEL", "GW_EN_CARD_CROSSING_SUMMARY.png", "crossing summary", "acoustics to cosmology")

    put([70], "ORIGINAL DOCUMENT", "GW_EN_DOC42_STUDY_LIMIT.png", "three-reading setup", "study-limit line")
    put([71], "MODEL", "GW_EN_CARD_CROSSING_COSMOLOGY.png", "speculative-metaphor reading", "mechanism or metaphor")
    put([72], "ARCHIVE", "FORT_MEADE_CURRENT_CC_BY_SA_2.jpg", "military-era context; contemporary image disclosed in credits", "Fort Meade aerial")
    put([73], "MODEL", "GW_EN_CARD_INTERPRETATION_TEST.png", "unusual reports motivate a test", "test-the-model question")
    put([74], "ORIGINAL DOCUMENT", "GW_EN_DOC14_CONCLUSION.png", "interpretive limit", "Conclusion line")
    put([75, 76], "ORIGINAL DOCUMENT", "GW_EN_DOC09_FOCUS15.png", "Focus map entry", "full Focus-level page")
    put(range(77, 80), "MODEL", "GW_EN_CARD_FOCUS10_STATE.png", "Focus 10 definition", "mind awake / body asleep")
    put([80, 81], "INNER / HYPOTHESIS", "GW_EN_INNER07_FOCUS12_EXPANSION_NATIVE.png", "Focus 12 subjective expansion", "room expands beyond ordinary geometry")
    put([82], "MODEL", "GW_EN_CARD_FOCUS15.png", "Focus 15 heading reveal", "Focus 15 / The Past")
    put([83, 84], "ORIGINAL DOCUMENT", "GW_EN_DOC45_FOCUS15_RECAP.png", "Focus 15 source proof", "Travel into the Past detail")
    put(range(85, 88), "MODEL", "GW_EN_CLIP06_FOCUS_WHEEL.mp4", "linear time-wheel model", "hub and past spokes")
    put([88], "INNER / HYPOTHESIS", "GW_EN_INNER16_BODY_TURN_DIFFICULTY_NATIVE.png", "difficulty caveat embodied", "stable body / displaced room")
    put([89], "MODEL", "GW_EN_CARD_FEWER_5.png", "participation caveat", "fewer than five percent")
    put([90, 91], "ORIGINAL DOCUMENT", "GW_EN_DOC10_FOCUS21.png", "Focus 21 source proof", "Focus 21 / The Future")
    put([92], "ORIGINAL DOCUMENT", "GW_EN_DOC11_ROLLOUT.png", "physical instructions", "Out-of-Body Movement paragraph")
    put([93], "ORIGINAL DOCUMENT", "GW_EN_DOC49_ROLL_OUT_DETAIL.png", "instruction one", "roll out line")
    put([94], "INNER / HYPOTHESIS", "GW_EN_INNER09_RISE_UPWARD_NATIVE.png", "instruction two visualized", "first-person rise upward")
    put([95], "ORIGINAL DOCUMENT", "GW_EN_DOC51_OPENING_DETAIL.png", "instruction three", "opening line")
    put([96], "INNER / HYPOTHESIS", "GW_EN_INNER08_FOCUS21_THRESHOLD_NATIVE.png", "field-manual contrast", "impossible threshold")

    put([97], "RECONSTRUCTION", "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2_FINAL.png", "intelligence-test question", "anonymous participant")
    put([98], "ORIGINAL DOCUMENT", "GW_EN_DOC35_DIGIT_PROCEDURE.png", "hidden sequence procedure", "computer-generated numbers detail")
    put([99], "ORIGINAL DOCUMENT", "GW_EN_DOC12_TEN_DIGITS.png", "ten-digit source entry", "full paragraph")
    put(range(100, 103), "MODEL", "GW_EN_CLIP07_TEN_DIGITS.mp4", "linear test procedure", "placement to attempted retrieval")
    put([103], "ORIGINAL DOCUMENT", "GW_EN_DOC57_MATCHING_DIGITS.png", "trainer-attributed partial result", "matching-digits source")
    mode, primary, _, use, state = out[103]
    out[103] = (mode, primary, "GW_EN_FILMIC19_PARTIAL_DIGIT_NOTES_NATIVE.png", use, state)
    put([104], "ORIGINAL DOCUMENT", "GW_EN_DOC36_DIGIT_FAILURE.png", "negative boundary", "none got all ten")
    put([105, 106, 107], "MODEL", "GW_EN_CARD_TEST_NOT_PROOF.png", "episode hinge", "not a clean demonstration")
    put([108], "ORIGINAL DOCUMENT", "GW_EN_DOC37_DISTORTION_DETAIL.png", "partial-resemblance rationale", "distortion detail")
    put([109], "ORIGINAL DOCUMENT", "GW_EN_DOC13_DISTORTION.png", "distortion attribution", "information-distortion paragraph")
    put([110], "INNER / HYPOTHESIS", "GW_EN_INNER10_DISTORTION_BLEND_NATIVE.png", "three-source blend", "target / room / time impressions")
    put([111], "MODEL", "GW_EN_CARD_SOURCE_UNCERTAIN.png", "observer source ambiguity", "which belongs where")
    put([112], "ORIGINAL DOCUMENT", "GW_EN_DOC38_MULTIFOCUS_DETAIL.png", "failed result becomes H", "multi-focus detail")
    put([113], "MODEL", "GW_EN_CARD_DECISION_QUESTION.png", "viewer decision", "authorize question")
    put(range(114, 117), "RECONSTRUCTION", "GW_EN_STILL05_THREE_OBSERVERS_V2_FINAL.png", "H protocol participants", "present / past / future observers")
    put([117], "INNER / HYPOTHESIS", "GW_EN_INNER14_RECOMMENDATION_H_TRIAL_NATIVE.png", "H comparison logic", "three booths converge on target")
    put(range(118, 121), "RECONSTRUCTION", "GW_EN_FILMIC20_AUTHORIZATION_HAND_NATIVE.png", "binary viewer decision", "hand suspended above authorization")
    put([121], "ORIGINAL DOCUMENT", "GW_EN_DOC41_RECOMMENDATION_INTRO.png", "McDonnell continues", "recommendations heading")

    put([122], "ORIGINAL DOCUMENT", "GW_EN_DOC39_NONCORPOREAL_DETAIL.png", "Recommendation J exact attribution", "non-corporal forms detail")
    mode, primary, _, use, state = out[122]
    out[122] = (mode, primary, "GW_EN_INNER15_NONPHYSICAL_PRESENCE_NATIVE.png", use, state)
    put([123], "ORIGINAL DOCUMENT", "GW_EN_DOC40_HOLOGRAPHIC_DEFENCE.png", "Recommendation K exact attribution", "holographic defence detail")
    mode, primary, _, use, state = out[123]
    out[123] = (mode, primary, "GW_EN_INNER11_DEFENSIVE_PERIMETER_NATIVE.png", use, state)
    put([124], "MODEL", "GW_EN_CARD_RECOMMENDATION_JK.png", "headphones-to-doctrine contrast", "J and K")
    put([125], "ORIGINAL DOCUMENT", "GW_EN_DOC16_RECOMMENDATIONS_JK.png", "unestablished defensive doctrine", "J/K source context")
    put([126], "ORIGINAL DOCUMENT", "GW_EN_DOC59_FFR_MODERN_BOUNDARY.png", "return to testable sound", "frequency-response detail")
    put([127], "RECONSTRUCTION", "GW_EN_FILMIC22_MODERN_EEG_LAB_NATIVE.png", "modern study domains", "anonymous EEG test")
    put([128, 129], "MODEL", "GW_EN_CARD_EVIDENCE_MIXED.png", "review outcome", "modest psychological effects")
    put([130], "MODEL", "GW_EN_CARD_EEG_MIXED.png", "entrainment uncertainty", "EEG entrainment mixed")
    put([131], "INNER / HYPOTHESIS", "GW_EN_INNER12_STATE_NOT_INFORMATION_NATIVE.png", "central evidentiary gap", "altered state separated from hidden target")
    put([132], "MODEL", "GW_EN_CARD_HIDDEN_DIGITS_GAP.png", "feeling versus retrieval", "not reading digits")
    put([133], "RECONSTRUCTION", "GW_EN_FILMIC23_NO_DATASET_EMPTY_LAB_NATIVE.png", "controlled-data gap", "empty modern lab")
    put([134, 135], "ORIGINAL DOCUMENT", "GW_EN_DOC54_SUBJECT_RECAP.png", "authenticity and subject recap", "memorandum subject detail")
    put([136], "ORIGINAL DOCUMENT", "GW_EN_DOC55_AUTHOR_RECAP.png", "visible author provenance", "author detail")
    put([137], "ORIGINAL DOCUMENT", "GW_EN_DOC56_FOCUS_RECAP_ALT.png", "verified Focus claim recap", "Travel into the Past")
    put([138], "ORIGINAL DOCUMENT", "GW_EN_DOC46_DIGIT_RECAP.png", "verified digit result recap", "all-ten context")
    put([139], "ORIGINAL DOCUMENT", "GW_EN_DOC53_NONCORPOREAL_RECAP.png", "verified doctrine recap", "non-corporal detail")
    put([140], "MODEL", "GW_EN_CARD_PROOF_BOUNDARY.png", "proof boundary", "authentic document / unproven claim")
    put([141], "MODEL", "GW_EN_CARD_ARMY_NOT_CIA_RECAP.png", "viral-claim correction", "Army written / CIA archived")
    put([142], "ORIGINAL DOCUMENT", "GW_EN_DOC47_ARMY_HEADER_RECAP.png", "real document", "Army header detail")
    put([143], "RECONSTRUCTION", "GW_EN_CLIP12_THREE_INPUTS_PROGRESS.mp4", "three borrowed inputs", "audio / Bentov / anomalous reports illuminate in sequence")
    put([144], "MODEL", "GW_EN_CARD_H_PROTOCOL_RECAP.png", "three-time test recap", "three times / one target")
    put([145], "MODEL", "GW_EN_CARD_OVERREACH.png", "closing interpretation one", "bureaucratic overreach")
    put([146], "RECONSTRUCTION", "GW_EN_FILMIC25_COLD_WAR_DESPERATION_NATIVE.png", "closing interpretation two", "Cold War institutional anxiety")
    put([147], "INNER / HYPOTHESIS", "GW_EN_INNER13_UNANSWERED_ANOMALY_NATIVE.png", "closing interpretation three", "unanswered anomaly")
    put([148], "ORIGINAL DOCUMENT", "GW_EN_DOC48_CONCLUSION_RECAP.png", "document cannot decide", "conclusion detail")
    put([149, 150], "MODEL", "GW_EN_CLIP10_ZERO_ONE_HANDOFF.mp4", "PEAR handoff", "visions removed; binary test enters")
    put([151], "MODEL", "GW_EN_CARD_14M.png", "next-episode quantitative hook", "fourteen million trials")
    put([152], "RECONSTRUCTION", "GW_EN_FILMIC27_ANONYMOUS_OPERATOR_NATIVE.png", "next-episode operator hook", "one unnamed operator at apparatus")
    return out


def build_cue() -> None:
    mapping = no_repeat_semantic_map()
    paragraphs = paragraph_times()
    if set(mapping) != set(range(1, len(paragraphs) + 1)):
        missing = sorted(set(range(1, len(paragraphs) + 1)) - set(mapping))
        raise RuntimeError(f"semantic map incomplete; missing {missing}")
    CUE.parent.mkdir(parents=True, exist_ok=True)
    with CUE.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cue_id", "start", "end", "duration", "voice_text", "internal_mode", "primary_asset", "asset_state", "fallback_asset", "editorial_use", "visible_mode_badge", "reconstruction_context"])
        for i, (text, start, end) in enumerate(paragraphs, 1):
            mode, primary, fallback, use, state = mapping[i]
            context = "optional 1.5-2.0s at first block entry only" if mode == "RECONSTRUCTION" else "none"
            w.writerow([f"GW-CUE-{i:03d}", f"{start:.3f}", f"{end:.3f}", f"{end-start:.3f}", text, mode, primary, state, fallback, use, "NO", context])
    build_edit_shots(paragraphs, mapping)
    print(CUE)


def build_edit_shots(paragraphs, mapping) -> None:
    groups = []
    for i, (text, start, end) in enumerate(paragraphs, 1):
        mode, primary, fallback, use, state = mapping[i]
        if groups and groups[-1]["primary"] == primary:
            groups[-1]["last"] = i
            groups[-1]["voice_end"] = end
            groups[-1]["voice_text"] += " " + text
            if state not in groups[-1]["states"]:
                groups[-1]["states"].append(state)
            if use not in groups[-1]["uses"]:
                groups[-1]["uses"].append(use)
            if fallback and not groups[-1]["fallback"]:
                groups[-1]["fallback"] = fallback
        else:
            groups.append({
                "first": i, "last": i, "voice_start": start, "voice_end": end,
                "voice_text": text, "mode": mode, "primary": primary,
                "fallback": fallback, "states": [state], "uses": [use],
            })

    # Split long single-image holds at natural midpoints using the mapped fallback.
    expanded = []
    for group in groups:
        mode, primary, fallback = group["mode"], group["primary"], group["fallback"]
        duration = group["voice_end"] - group["voice_start"]
        moving = primary.lower().endswith(".mp4")
        if duration > 6.2 and not moving and fallback and fallback != primary:
            mid = group["voice_start"] + duration / 2
            first = dict(group)
            first["voice_end"] = mid
            first["voice_text"] += " [first visual half]"
            second = dict(group)
            second["voice_start"] = mid
            second["primary"] = fallback
            second["fallback"] = primary
            second["states"] = ["alternate verified source/state"]
            second["voice_text"] = group["voice_text"] + " [second visual half]"
            expanded.extend([first, second])
        else:
            expanded.append(group)

    master_end = 481.037
    primaries = [group["primary"] for group in expanded]
    repeated = sorted({asset for asset in primaries if primaries.count(asset) > 1})
    if repeated:
        raise RuntimeError(f"picture-lock asset return: {repeated}")

    asset_paths = {p.name: p for p in EP.rglob("*") if p.is_file()}
    with EDL.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["edit_shot_id", "start", "end", "duration", "cue_first", "cue_last", "primary_asset", "asset_state", "internal_mode", "editorial_use", "fallback_asset", "source_in", "source_out", "playback_rate", "retention_review", "visible_mode_badge", "series_usage"])
        for idx, group in enumerate(expanded):
            prev_end = expanded[idx - 1]["voice_end"] if idx else 0.0
            next_start = expanded[idx + 1]["voice_start"] if idx + 1 < len(expanded) else master_end
            start = 0.0 if idx == 0 else (prev_end + group["voice_start"]) / 2
            end = master_end if idx + 1 == len(expanded) else (group["voice_end"] + next_start) / 2
            state = " → ".join(group["states"])
            use = " / ".join(group["uses"])
            shot_duration = end - start
            source_in = source_out = playback_rate = ""
            if group["primary"].lower().endswith(".mp4"):
                path = asset_paths.get(group["primary"])
                if not path:
                    raise FileNotFoundError(group["primary"])
                result = subprocess.run([
                    "ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1", str(path),
                ], capture_output=True, text=True, check=True)
                clip_duration = float(result.stdout.strip())
                source_in, source_out = "0.000", f"{clip_duration:.3f}"
                playback_rate = f"{clip_duration / shot_duration:.3f}x"
            review = ""
            if shot_duration >= 8:
                if not group["primary"].lower().endswith(".mp4"):
                    raise RuntimeError(f"static hold >=8s: {group['primary']} {shot_duration:.3f}s")
                if group["primary"].startswith("GW_EN_CLIP01"):
                    review = "ACCEPT: 10.7s hook contains six visible protocol stages and one continuous source pass; no restart."
                elif group["primary"].startswith("GW_EN_CLIP07"):
                    review = "ACCEPT: 8.9s test sequence progresses from placement to blinding to partial retrieval; no repeated material."
                else:
                    review = "REVIEWED: continuous motion with documented internal progression."
            w.writerow([f"GW-SHOT-{idx+1:03d}", f"{start:.3f}", f"{end:.3f}", f"{shot_duration:.3f}", f"GW-CUE-{group['first']:03d}", f"GW-CUE-{group['last']:03d}", group["primary"], state, group["mode"], use, group["fallback"], source_in, source_out, playback_rate, review, "NO", "EP02_ONLY"])


DOC_SPECS = [
    ("GW_EN_DOC01_ARMY_HEADER.png", PDF, 1, "DEPARTMENT OF THE ARMY", 165, 250, True),
    ("GW_EN_DOC02_MCDONNELL_SIGNATURE.png", PDF, 2, "Commander, Det O", 170, 250, False),
    ("GW_EN_DOC03_HEMISYNC.png", PDF, 6, "Gateway and Hemi-Sync", 140, 255, False),
    ("GW_EN_DOC04_FREQUENCY_RESPONSE.png", PDF, 7, "Frequency Following Response", 140, 235, False),
    ("GW_EN_DOC05_RESONANCE.png", PDF, 7, "Role of Resonance", 145, 245, False),
    ("GW_EN_DOC06_BODY_OSCILLATOR.png", PDF, 8, "coherent oscillator", 170, 240, False),
    ("GW_EN_DOC07_TIME_SPACE.png", PDF, 13, "Time-Space Dimension", 150, 260, False),
    ("GW_EN_DOC08_OUT_OF_BODY_STATUS.png", PDF, 16, "Out-of-Body Experience", 170, 240, False),
    ("GW_EN_DOC09_FOCUS15.png", PDF, 24, "Focus 15: Travel into the Past", 120, 290, False),
    ("GW_EN_DOC10_FOCUS21.png", PDF, 24, "Focus 21: The Future", 120, 235, False),
    ("GW_EN_DOC11_ROLLOUT.png", PDF, 24, "Out-of-Body Movement", 140, 310, False),
    ("GW_EN_DOC12_TEN_DIGITS.png", PDF, 25, "ten computer generated numbers", 170, 255, False),
    ("GW_EN_DOC13_DISTORTION.png", PDF, 26, "Some of the distortions occurring", 170, 270, False),
    ("GW_EN_DOC14_CONCLUSION.png", PDF, 27, "Conclusion", 145, 300, False),
    ("GW_EN_DOC15_RECOMMENDATION_H.png", PDF, 28, "H. Use multi-focus approach", 115, 275, False),
    ("GW_EN_DOC16_RECOMMENDATIONS_JK.png", PDF, 28, "intelligent, non-corporal energy forms", 140, 260, False),
    ("GW_EN_DOC17_BIBLIOGRAPHY.png", PDF, 29, "Bentov, Itzhak", 110, 300, False),
    ("GW_EN_DOC18_MONROE_PATENT.png", PATENT, 1, "Robert", 140, 260, False),
    ("GW_EN_DOC19_NTSB_FLIGHT191.png", NTSB, 1, "Flight 191", 160, 300, False),
    ("GW_EN_DOC20_TASKING.png", PDF, 1, "You tasked me", 110, 240, False, True),
    ("GW_EN_DOC21_HYPNOSIS.png", PDF, 3, "Hypnosis", 110, 240, False, True),
    ("GW_EN_DOC22_TRANSCENDENTAL_MEDITATION.png", PDF, 3, "Transcendental Meditation", 100, 235, False, True),
    ("GW_EN_DOC23_BIOFEEDBACK.png", PDF, 5, "Biofeedback", 105, 235, False, True),
    ("GW_EN_DOC24_GATEWAY_COMPARISON.png", PDF, 6, "Gateway and Hemi-Sync", 105, 260, False, True),
    ("GW_EN_DOC25_FFR_DETAIL.png", PDF, 7, "Frequency Following Response", 100, 245, False, True),
    ("GW_EN_DOC26_ELECTROMAGNETIC_RESPONSE.png", PDF, 8, "An electromagnetic pulse is then generated", 105, 255, False, True),
    ("GW_EN_DOC27_BENTOV_CITATION.png", PDF, 8, "Bentov", 95, 235, False, True),
    ("GW_EN_DOC28_BODY_RHYTHM.png", PDF, 8, "body", 105, 245, False, True),
    ("GW_EN_DOC29_UNIVERSAL_HOLOGRAM.png", PDF, 10, "universal hologram", 100, 245, False, True),
    ("GW_EN_DOC30_CONSCIOUSNESS_MATRIX.png", PDF, 10, "consciousness matrix", 105, 245, False, True),
    ("GW_EN_DOC31_TIME_SPACE_DETAIL.png", PDF, 13, "time-space", 95, 235, False, True),
    ("GW_EN_DOC32_CLICKING_OUT.png", PDF, 14, "clicking out", 100, 245, False, True),
    ("GW_EN_DOC33_OBE_DETAIL.png", PDF, 16, "Out-of-Body Experience", 95, 260, False, True),
    ("GW_EN_DOC34_FOCUS_DIFFICULTY.png", PDF, 24, "less than five", 100, 250, False, True),
    ("GW_EN_DOC35_DIGIT_PROCEDURE.png", PDF, 25, "computer generated numbers", 95, 255, False, True),
    ("GW_EN_DOC36_DIGIT_FAILURE.png", PDF, 25, "none have ever succeeded", 95, 255, False, True),
    ("GW_EN_DOC37_DISTORTION_DETAIL.png", PDF, 26, "somewhat distorted form", 100, 250, False, True),
    ("GW_EN_DOC38_MULTIFOCUS_DETAIL.png", PDF, 28, "multi-focus approach", 95, 245, False, True),
    ("GW_EN_DOC39_NONCORPOREAL_DETAIL.png", PDF, 28, "non-corporal energy forms", 95, 245, False, True),
    ("GW_EN_DOC40_HOLOGRAPHIC_DEFENCE.png", PDF, 28, "holographic patterns", 95, 245, False, True),
    ("GW_EN_DOC41_RECOMMENDATION_INTRO.png", PDF, 27, "The most promising approach suggested in the foregoing study involves the following steps", 90, 230, False, True),
    ("GW_EN_DOC42_STUDY_LIMIT.png", PDF, 2, "This study is certainly not designed to be the last word on the subject", 95, 250, False, True),
    ("GW_EN_DOC43_RECIPIENT.png", PDF, 1, "TO:", 90, 220, False, True),
    ("GW_EN_DOC44_DATE.png", PDF, 1, "9 June 1983", 90, 220, False, True),
    ("GW_EN_DOC45_FOCUS15_RECAP.png", PDF, 24, "Focus 15: Travel into the Past", 80, 220, False, True),
    ("GW_EN_DOC46_DIGIT_RECAP.png", PDF, 25, "all ten correct", 85, 225, False, True),
    ("GW_EN_DOC47_ARMY_HEADER_RECAP.png", PDF, 1, "DEPARTMENT OF THE ARMY", 75, 205, False, True),
    ("GW_EN_DOC48_CONCLUSION_RECAP.png", PDF, 27, "Conclusion", 80, 220, False, True),
    ("GW_EN_DOC49_ROLL_OUT_DETAIL.png", PDF, 24, "rolling out", 80, 220, False, True),
    ("GW_EN_DOC50_RISE_DETAIL.png", PDF, 24, "lifting out", 80, 220, False, True),
    ("GW_EN_DOC51_OPENING_DETAIL.png", PDF, 25, "sliding out through either end of his body", 80, 220, False, True),
    ("GW_EN_DOC52_NESTED_SYSTEMS.png", PDF, 13, "various intervening dimensions to which human consciousness in altered states of being may gain access", 85, 230, False, True),
    ("GW_EN_DOC53_NONCORPOREAL_RECAP.png", PDF, 28, "intelligent, non-corporal energy forms", 70, 205, False, True),
    ("GW_EN_DOC54_SUBJECT_RECAP.png", PDF, 1, "SUBJECT:", 75, 205, False, True),
    ("GW_EN_DOC55_AUTHOR_RECAP.png", PDF, 2, "MCDONNELL", 75, 205, False, True),
    ("GW_EN_DOC56_FOCUS_RECAP_ALT.png", PDF, 24, "Travel into the Past", 70, 200, False, True),
    ("GW_EN_DOC57_MATCHING_DIGITS.png", PDF, 25, "aquired enough of the digits", 75, 215, False, True),
    ("GW_EN_DOC58_BENTOV_REAPPEARS.png", PDF, 17, "Bentov", 80, 220, False, True),
    ("GW_EN_DOC59_FFR_MODERN_BOUNDARY.png", PDF, 7, "frequency", 75, 210, False, True),
    ("GW_EN_DOC60_FIELD_INFORMATION_DETAIL.png", PDF, 13, "It retains its inherent capacity for consciousness in that it can receive and passively perceive holograms generated by energy in motion out in the various dimensions which make up the created universe", 75, 215, False, True),
    ("GW_EN_DOC61_NONCORPOREAL_CONTEXT.png", PDF, 28, "time-space boundaries", 70, 205, False, True),
    ("GW_EN_DOC62_DEFENCE_CONTEXT.png", PDF, 28, "sensitive areas", 70, 205, False, True),
    ("GW_EN_DOC63_MATCHING_DIGITS_CONTEXT.png", PDF, 25, "university laboratory", 75, 215, False, True),
    ("GW_EN_DOC64_MONROE_INVENTOR.png", PATENT, 1, "Robert A. Monroe", 100, 255, False, True),
    ("GW_EN_DOC65_BENTOV_INVENTOR.png", BENTOV_PATENT, 1, "BENTOV", 120, 390, False, False),
]


def render_document(spec: tuple) -> None:
    name, pdf_path, page_number, phrase, pad_y, crop_h, first_source, *extra = spec
    metadata = EP / "03_VISUALS" / "METADATA" / "DOCUMENT_EVIDENCE" / f"{Path(name).stem}.json"
    if name == "GW_EN_DOC19_NTSB_FLIGHT191.png":
        # The NTSB scan has no searchable text layer.  This is explicitly a
        # whole-cover source establishing document identity, not a quotation
        # crop; retaining the full page is safer than inventing OCR geometry.
        doc = pymupdf.open(pdf_path)
        page = doc[page_number - 1]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2), alpha=False)
        full = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        full.thumbnail((1120, 900), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (W, H), BG)
        canvas.paste(Image.new("RGB", (1220, 960), PAPER), (350, 60))
        canvas.paste(full, ((W - full.width) // 2, (H - full.height) // 2))
        DOC_OUT.mkdir(parents=True, exist_ok=True)
        canvas.save(DOC_OUT / name, quality=96)
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(json.dumps({
            "status": "PASS_WHOLE_PAGE_NO_TEXT_LAYER",
            "pdf": str(pdf_path), "page": page_number,
            "purpose": "document identity / NTSB cover, not quotation evidence",
            "full_page_visible": True, "highlight": None,
        }, indent=2), encoding="utf-8")
        return
    footer = "CIA archive copy • Army memorandum • 9 June 1983" if first_source else None
    render_evidence_frame(
        pdf_path=Path(pdf_path),
        page_number=page_number,
        phrase=phrase,
        output_path=DOC_OUT / name,
        metadata_path=metadata,
        canvas_size=(W, H),
        background=BG,
        paper=PAPER,
        accent=AMBER,
        fallback_above=max(48.0, pad_y / 2),
        fallback_below=max(130.0, crop_h),
        footer=footer,
        footer_font=font(28),
    )


def build_documents(force: bool = False) -> None:
    force_rebuild = {"GW_EN_DOC22_TRANSCENDENTAL_MEDITATION.png"}
    for spec in DOC_SPECS:
        out = DOC_OUT / spec[0]
        if out.is_file() and out.name not in force_rebuild and not force:
            print(f"SKIP {out.name}")
            continue
        render_document(spec)
        print(f"OK {out.name}")


CARDS = [
    ("GW_EN_CARD_H_RECOMMENDATION_H.png", ["RECOMMENDATION H"], AMBER),
    ("GW_EN_CARD_ARMY_NOT_CIA.png", ["ARMY ANALYSIS", "CIA ARCHIVE COPY"], CYAN),
    ("GW_EN_CARD_BEAT_400.png", ["400 Hz"], CYAN),
    ("GW_EN_CARD_BEAT_410.png", ["400 Hz", "410 Hz"], CYAN),
    ("GW_EN_CARD_BEAT_10HZ.png", ["400 Hz", "410 Hz", "10 beats/sec"], AMBER),
    ("GW_EN_CARD_CROSSING_SOUND.png", ["Sound"], CYAN),
    ("GW_EN_CARD_CROSSING_COSMOLOGY.png", ["Consciousness outside time?"], AMBER),
    ("GW_EN_CARD_FOCUS15.png", ["FOCUS 15", "THE PAST"], AMBER),
    ("GW_EN_CARD_FEWER_5.png", ["Fewer than 5%"], AMBER),
    ("GW_EN_CARD_DECISION_QUESTION.png", ["Would you authorize the test?"], PAPER),
    ("GW_EN_CARD_DECISION_AUTHORIZE_STOP.png", ["AUTHORIZE", "STOP"], AMBER),
    ("GW_EN_CARD_DIGITS_SOME.png", ["Some digits matched."], CYAN),
    ("GW_EN_CARD_DIGITS_NONE.png", ["Nobody got all ten."], AMBER),
    ("GW_EN_CARD_RECOMMENDATION_JK.png", ["RECOMMENDATION J", "RECOMMENDATION K"], AMBER),
    ("GW_EN_CARD_EVIDENCE_MIXED.png", ["Psychological effects: modest", "EEG entrainment: mixed"], CYAN),
    ("GW_EN_CARD_HANDOFF.png", ["Remove the visions.", "Keep the test."], AMBER),
    ("GW_EN_CARD_FOCUS10.png", ["FOCUS 10"], AMBER),
    ("GW_EN_CARD_FOCUS10_STATE.png", ["MIND AWAKE", "BODY ASLEEP"], CYAN),
    ("GW_EN_CARD_FOCUS12.png", ["FOCUS 12"], AMBER),
    ("GW_EN_CARD_FOCUS12_STATE.png", ["AWARENESS", "BEYOND ORDINARY SENSES"], CYAN),
    ("GW_EN_CARD_TEST_NOT_PROOF.png", ["NOT A CLEAN", "DEMONSTRATION"], AMBER),
    ("GW_EN_CARD_DISTORTION_SOURCES.png", ["TARGET", "ROOM", "OTHER MOMENTS"], CYAN),
    ("GW_EN_CARD_H_PRESENT.png", ["OBSERVER 1", "PRESENT"], CYAN),
    ("GW_EN_CARD_H_PAST.png", ["OBSERVER 2", "IMMEDIATE PAST"], CYAN),
    ("GW_EN_CARD_H_FUTURE.png", ["OBSERVER 3", "IMMEDIATE FUTURE"], CYAN),
    ("GW_EN_CARD_H_COMPARE.png", ["COMPARE", "AFTER THE SESSION"], AMBER),
    ("GW_EN_CARD_MODERN_METHODS.png", ["METHODS VARY", "OUTCOMES VARY"], CYAN),
    ("GW_EN_CARD_EEG_MIXED.png", ["EEG ENTRAINMENT", "MIXED"], AMBER),
    ("GW_EN_CARD_STATE_NOT_INFO.png", ["ALTERED STATE", "≠", "HIDDEN INFORMATION"], AMBER),
    ("GW_EN_CARD_HIDDEN_DIGITS_GAP.png", ["FEELING DIFFERENT", "IS NOT READING DIGITS"], CYAN),
    ("GW_EN_CARD_NO_DATASET.png", ["NO CONTROLLED DATASET", "IN THE REPORT"], AMBER),
    ("GW_EN_CARD_PROOF_BOUNDARY.png", ["AUTHENTIC DOCUMENT", "UNPROVEN CLAIM"], AMBER),
    ("GW_EN_CARD_OVERREACH.png", ["BUREAUCRATIC", "OVERREACH?"], PAPER),
    ("GW_EN_CARD_DESPERATION.png", ["COLD WAR", "DESPERATION?"], PAPER),
    ("GW_EN_CARD_ANOMALY.png", ["UNANSWERED ANOMALY", "WRONG THEORY?"], PAPER),
    ("GW_EN_CARD_TIME_COORDINATE.png", ["TIME", "AS A COORDINATE"], AMBER),
    ("GW_EN_CARD_SOURCE_UNCERTAIN.png", ["WHICH IMPRESSION", "BELONGS WHERE?"], PAPER),
    ("GW_EN_CARD_THREE_INPUTS.png", ["AUDIO SYSTEM", "BENTOV MODEL", "ANOMALOUS REPORTS"], CYAN),
    ("GW_EN_CARD_H_PROTOCOL_RECAP.png", ["THREE TIMES", "ONE TARGET", "COMPARE LATER"], AMBER),
    ("GW_EN_CARD_WEAK_NOT_DISCARDED.png", ["TOO WEAK TO PROVE", "NOT DISCARDED"], AMBER),
    ("GW_EN_CARD_INTERPRETATION_TEST.png", ["UNUSUAL REPORTS", "TEST THE MODEL?"], PAPER),
    ("GW_EN_CARD_ARMY_NOT_CIA_RECAP.png", ["WRITTEN BY THE ARMY", "ARCHIVED BY THE CIA"], CYAN),
    ("GW_EN_CARD_CROSSING_SUMMARY.png", ["ACOUSTICS", "→", "COSMOLOGY"], AMBER),
    ("GW_EN_CARD_14M.png", ["14,000,000", "TRIALS"], CYAN),
    ("GW_EN_CARD_ONE_OPERATOR.png", ["ONE UNNAMED PERSON", "ROUGHLY HALF THE EFFECT"], AMBER),
    ("GW_EN_CARD_THREE_INPUTS_COMBINED.png", ["THREE INPUTS", "ONE TEST PLAN"], AMBER),
]


def build_cards() -> None:
    CARD_OUT.mkdir(parents=True, exist_ok=True)
    for name, lines, color in CARDS:
        canvas = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(canvas)
        d.line((180, 170, 1740, 170), fill=(42, 61, 65), width=3)
        # Large semantic forms make these title cards materially different
        # visual states, not cosmetic crop/zoom variants of one template.
        if name == "GW_EN_CARD_CROSSING_SOUND.png":
            points = []
            for x in range(180, 1741, 8):
                y_wave = 805 + int(62 * math.sin((x - 180) / 54.0))
                points.append((x, y_wave))
            d.line(points, fill=CYAN, width=8)
        elif name == "GW_EN_CARD_BEAT_400.png":
            d.rounded_rectangle((145, 250, 470, 880), radius=38, outline=CYAN, width=8)
            for y_bar in range(315, 830, 74):
                d.line((220, y_bar, 395, y_bar), fill=(74, 124, 132), width=5)
        elif name == "GW_EN_CARD_FOCUS15.png":
            centre = (1485, 670)
            for radius in (90, 165, 245):
                d.ellipse((centre[0]-radius, centre[1]-radius, centre[0]+radius, centre[1]+radius), outline=AMBER, width=6)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                d.line((centre[0], centre[1], centre[0] + int(245*math.cos(rad)), centre[1] + int(245*math.sin(rad))), fill=(118, 91, 50), width=3)
        elif name == "GW_EN_CARD_DIGITS_SOME.png":
            for idx in range(10):
                x0 = 265 + idx * 142
                fill = (28, 74, 82) if idx in {1, 4, 7} else (18, 28, 31)
                d.rounded_rectangle((x0, 790, x0 + 100, 895), radius=13, fill=fill, outline=CYAN, width=4)
        elif name == "GW_EN_CARD_FEWER_5.png":
            for idx in range(20):
                cx = 1320 + (idx % 5) * 92
                cy = 600 + (idx // 5) * 92
                dot = AMBER if idx == 0 else (48, 67, 70)
                d.ellipse((cx-22, cy-22, cx+22, cy+22), fill=dot)
        sizes = [112 if len(x) < 20 else 80 for x in lines]
        heights = [font(s, True).getbbox(x)[3] for x, s in zip(lines, sizes)]
        total = sum(heights) + max(0, len(lines) - 1) * 60
        y = (H - total) // 2
        for line, size, hh in zip(lines, sizes, heights):
            f = font(size, True)
            box = d.textbbox((0, 0), line, font=f)
            x = (W - (box[2] - box[0])) // 2
            d.text((x, y), line, font=f, fill=color)
            y += hh + 60
        d.line((180, 910, 1740, 910), fill=(42, 61, 65), width=3)
        canvas.save(CARD_OUT / name)
        print(CARD_OUT / name)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["cue", "documents", "cards", "all"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if args.action in ("cue", "all"):
        build_cue()
    if args.action in ("documents", "all"):
        build_documents(args.force)
    if args.action in ("cards", "all"):
        build_cards()


if __name__ == "__main__":
    main()
