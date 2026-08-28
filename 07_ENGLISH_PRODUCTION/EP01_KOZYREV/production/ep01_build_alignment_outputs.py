#!/usr/bin/env python3
"""Build paragraph timing, subtitles and an evidence-aware EP01 visual cue sheet."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV"
SCRIPT = EP / "01_SCRIPT" / "VOICE_SCRIPT_EN.txt"
ALIGN = EP / "02_VOICE" / "alignment" / "EP01_EN_KOZYREV_alignment.json"
OUT = EP / "06_TIMELINE"


def timecode(seconds: float, vtt: bool = False) -> str:
    millis = round(seconds * 1000)
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    sep = "." if vtt else ","
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{sep}{ms:03d}"


def classify(text: str, index: int) -> tuple[str, str, str, str, str]:
    lower = text.casefold()
    # mode, primary, fallback, status, rationale
    if index == 1:
        return "RECONSTRUCTION", "KZ_CLIP01_CHAMBER_MEMORY", "KZ_EN_HERO01", "NEEDS_CLIP", "Immediate impossible object and rotation question"
    if "in 1996" in lower or "clinical title" in lower:
        return "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_HOOK", "KZ_CARD_PATENT_METADATA", "SOURCE_READY", "Early verified patent/date/title anchor"
    if "same structure is called" in lower:
        return "EXPLANATORY_MODEL", "KZ_CARD_MEDICAL_TO_TIME_MACHINE", "KZ_SRC_PATENT_HOOK", "NEEDS_CARD", "Name/meaning contradiction"
    if "kozyrev died" in lower or "thirteen years later" in lower:
        return "ARCHIVE", "KZ_CARD_1983_1996", "KZ_SRC_KOZYREV_1959", "NEEDS_CARD", "Biography/filing contradiction"
    if "never built" in lower or "man whose name" in lower:
        return "ARCHIVE", "KZ_SRC_KOZYREV_1959", "KZ_CARD_1983_1996", "SOURCE_READY", "Correct identity and no-construction boundary"
    if "clockwise spiral" in lower or "counterclockwise spiral" in lower or "form a cylinder" in lower:
        return "ORIGINAL_DOCUMENT", "KZ_CLIP02_PATENT_ASSEMBLY", "KZ_SRC_PATENT_FIGURES", "NEEDS_CLIP", "Patent configurations and direction"
    if "motorized platform" in lower or "and it can rotate" in lower:
        return "RECONSTRUCTION", "KZ_EN_HERO01", "KZ_SRC_PATENT_FIG4", "READY", "Accepted anchor contains the visible motor/platform; no extra still needed"
    if "person sat" in lower or "participant" in lower and "chamber" in lower:
        return "RECONSTRUCTION", "KZ_EN_REC01_ENTERING", "KZ_EN_HERO01", "READY", "Accepted entry reconstruction provides human scale without a redundant seated still"
    if "new moon" in lower or "full moon" in lower or "geomagnetic" in lower or "heliogeophysical" in lower:
        return "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_CONDITIONS", "KZ_MAP_HELIOGEOPHYSICAL_CONTEXT", "SOURCE_READY", "Inventor-attributed conditions"
    if "which story" in lower or "strange form of isolation" in lower or "physical environment" in lower or "information itself" in lower:
        return "EXPLANATORY_MODEL", "KZ_CARD_THREE_THEORIES", "KZ_CLIP05_THREE_THEORIES", "NEEDS_CARD", "Sets three competing interpretations"
    if "nikolai alexandrovich" in lower or "soviet astronomer" in lower:
        return "ARCHIVE", "KZ_SRC_KOZYREV_1959", "KZ_MAP_PULKOVO_TO_NOVOSIBIRSK", "SOURCE_READY", "Authentic person identity"
    if "time was not merely" in lower or "act physically" in lower or "measurable traces" in lower:
        return "INNER_HYPOTHESIS", "KZ_INNER01_INTERNAL_TIME", "KZ_SRC_KOZYREV_1959", "NEEDS_NATIVE_IMAGEGEN", "Make Kozyrev's speculative time idea tangible"
    if "kaznacheev and trofimov" in lower and ("moved" in lower or "studied" in lower):
        return "ARCHIVE", "KZ_SRC_KAZNACHEEV_TROFIMOV_IDENTITIES", "KZ_SRC_PATENT_INVENTORS", "SOURCE_READY", "Authentic identities at name beat"
    if "three separate stories" in lower or "collapsed into one label" in lower or "documents separate" in lower:
        return "EXPLANATORY_MODEL", "KZ_CARD_THREE_STREAMS", "KZ_SRC_PATENT_INVENTORS", "NEEDS_CARD", "Separate theory researchers and apparatus"
    if "two point eight" in lower or "fifty centimeters" in lower or "between four and ten" in lower or "ground or polished" in lower:
        return "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_DIMENSIONS", "KZ_EN_HERO02", "SOURCE_READY", "Verified patent dimensions/material"
    if "focus" in lower or "surround the participant" in lower:
        return "EXPLANATORY_MODEL", "KZ_CARD_SCALE_FOCUS", "KZ_SRC_PATENT_DIMENSIONS", "NEEDS_CARD", "Explain scale/focus without claiming an effect"
    if "inventors' answer" in lower or "proposed that" in lower or "patent records a claim" in lower or "does not prove" in lower:
        return "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_CLAIMS", "KZ_CARD_PATENT_NOT_PROOF", "SOURCE_READY", "Attribute claim and evidence boundary"
    if "later publications" in lower or "modeled kozyrev space" in lower:
        return "ORIGINAL_DOCUMENT", "KZ_SRC_2006_2008_PUBLICATIONS", "KZ_SRC_TROFIMOV_2018", "SOURCE_READY", "Researchers' own later publications"
    if "altered internal time" in lower:
        return "INNER_HYPOTHESIS", "KZ_CLIP03_INTERNAL_TIME", "KZ_INNER01_INTERNAL_TIME", "NEEDS_CLIP", "Subjective temporal discontinuity"
    if "distant information" in lower or "remote objects" in lower or "other moments" in lower:
        return "INNER_HYPOTHESIS", "KZ_INNER02_DISTANT_IMAGE", "KZ_SRC_2006_2008_PUBLICATIONS", "NEEDS_NATIVE_IMAGEGEN", "Fractured distant-image metaphor tied to attributed claim"
    if "three ways" in lower or "first is psychological" in lower or "second possibility" in lower or "third is" in lower:
        return "EXPLANATORY_MODEL", "KZ_CLIP05_THREE_THEORIES", "KZ_CARD_THREE_THEORIES", "NEEDS_CLIP", "Progressive theory fork"
    if "isolation" in lower or "expectation" in lower or "unusual acoustics" in lower or "powerful state" in lower:
        return "RECONSTRUCTION", "KZ_EN_REC01_ENTERING", "KZ_EN_HERO01", "READY", "Use accepted neutral entry and controlled crop rather than another chamber reconstruction"
    if "sound" in lower or "temperature" in lower or "electromagnetic conditions" in lower or "measurable" in lower:
        return "EXPLANATORY_MODEL", "KZ_CARD_PHYSICAL_VARIABLES", "KZ_EN_HERO02", "NEEDS_CARD", "Ordinary measurable physical variables"
    if "four sealed target" in lower or "lighthouse" in lower or "violin" in lower or "burning car" in lower or "white horse" in lower or "choose to hide" in lower:
        return "EXPLANATORY_MODEL", "KZ_CLIP07_BLIND_TARGET_TEST", "KZ_TARGET_GRID", "NEEDS_CLIP", "Viewer target choice and fixed four-image set"
    if "computer randomly" in lower or "nobody present" in lower or "speaks or draws" in lower or "independent judges" in lower or "rules fixed" in lower:
        return "EXPLANATORY_MODEL", "KZ_CLIP07_BLIND_TARGET_TEST", "KZ_CARD_BLIND_PROTOCOL", "NEEDS_CLIP", "Blinded test procedure"
    if "another laboratory" in lower or "independent replication" in lower or "independent result" in lower or "replication" in lower:
        return "EXPLANATORY_MODEL", "KZ_CLIP08_REPLICATION_CHAIN", "KZ_CARD_MISSING_RESULT", "NEEDS_CLIP", "Replication is the decisive missing link"
    if "tower" in lower or "one resemblance" in lower or "chance" in lower or "interpretation after" in lower:
        return "EXPLANATORY_MODEL", "KZ_CARD_MATCH_VS_CHANCE", "KZ_TARGET_GRID", "NEEDS_CARD", "Prevents post-hoc matching from reading as success"
    if "sources behind" in lower or "real patent" in lower or "publications" in lower:
        return "ORIGINAL_DOCUMENT", "KZ_SRC_EVIDENCE_STACK", "KZ_SRC_PATENT_HOOK", "SOURCE_READY", "Return to the documented record"
    if "government number" in lower or "dates" in lower or "inventors" in lower or "language of authority" in lower or "patented means proven" in lower:
        return "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_HOOK", "KZ_CARD_PATENT_NOT_PROOF", "SOURCE_READY", "Patent-authority trap"
    if "patent can show" in lower or "does not certify" in lower:
        return "EXPLANATORY_MODEL", "KZ_CARD_PATENT_NOT_PROOF", "KZ_SRC_PATENT_CLAIMS", "NEEDS_CARD", "Legal document versus empirical validation"
    if any(word in lower for word in ["aluminum alloys", "polished surfaces", "fasteners", "focal distance", "the invisible acquired screws"]):
        return "RECONSTRUCTION", "KZ_EN_HERO02", "KZ_SRC_PATENT_FIGURES", "READY", "Accepted panel detail already shows material seams and fasteners"
    if "what remains" in lower or "patented chamber is documented" in lower or "central claim remains unconfirmed" in lower:
        return "RECONSTRUCTION", "KZ_EN_REC18_EMPTY_CHAMBER", "KZ_EN_HERO01", "NEEDS_GENERATION", "Sober factual residue"
    if "simplest decisive test" in lower or "part we cannot see" in lower or "larger than the experiment" in lower:
        return "INNER_HYPOTHESIS", "KZ_CLIP09_EMPTY_SPIRAL", "KZ_EN_REC18_EMPTY_CHAMBER", "NEEDS_CLIP", "Unresolved empty-room payoff"
    if "fort meade" in lower or "army officer" in lower or "next file" in lower:
        return "EXPLANATORY_MODEL", "KZ_MAP_FORT_MEADE_HANDOFF", "KZ_CARD_MISSING_RESULT", "NEEDS_MAP", "Episode-two geographic/protocol handoff"
    return "RECONSTRUCTION", "KZ_EN_HERO01", "KZ_SRC_PATENT_FIGURES", "READY", "Chamber continuity coverage"


# Recovery rebuild: explicit viewer-first storyboard assignments.  The former
# keyword classifier remains above only for provenance; production output uses
# this complete cue map so generic chamber coverage cannot silently swallow a
# named person, source, procedure or theory beat.
STORYBOARD: dict[int, tuple[str, str, str, str, str]] = {}


def add_storyboard(
    cues: list[int], mode: str, asset: str, fallback: str, status: str, function: str
) -> None:
    for cue in cues:
        if cue in STORYBOARD:
            raise RuntimeError(f"Duplicate storyboard assignment for cue {cue}")
        STORYBOARD[cue] = (mode, asset, fallback, status, function)


add_storyboard([1], "RECONSTRUCTION", "KZ_CLIP_ROTATION_HOOK", "KZ_EN_HERO01", "CLIP_CANDIDATE_STORYBOARDED", "Open on the physical rotation question; 2.02-second concrete motion beat")
add_storyboard([2], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_COVER_DATE", "KZ_CARD_PATENT_METADATA", "NEEDS_SOURCE_COMPOSITE", "Verified 1996 filing anchor before the legend expands")
add_storyboard([3], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_TITLE_CROP", "KZ_SRC_PATENT_COVER_DATE", "NEEDS_SOURCE_COMPOSITE", "Reveal the clinical title as an exact document crop")
add_storyboard([4], "EXPLANATORY_MODEL", "KZ_CARD_MEDICAL_TO_TIME_MACHINE", "KZ_SRC_PATENT_TITLE_CROP", "NEEDS_DETERMINISTIC_BUILD", "Make the medical-device versus time-machine escalation legible")
add_storyboard([5], "ARCHIVE", "KZ_SRC_KOZYREV_PORTRAIT_1983", "KZ_SRC_KOZYREV_1959", "NEEDS_SOURCE_COMPOSITE", "Show Kozyrev at the death-date biography beat")
add_storyboard([6], "ARCHIVE", "KZ_SRC_INVENTOR_PAIR_1996", "KZ_SRC_PATENT_INVENTORS", "NEEDS_SOURCE_COMPOSITE", "Show Kaznacheev and Trofimov when the later filing is named")
add_storyboard([7, 8], "EXPLANATORY_MODEL", "KZ_CARD_1983_1996_CONTRADICTION", "KZ_SRC_KOZYREV_PORTRAIT_1983", "NEEDS_DETERMINISTIC_BUILD", "Resolve the thirteen-year contradiction without implying Kozyrev built the device")
add_storyboard([9], "RECONSTRUCTION", "KZ_EN_HERO01", "KZ_SRC_PATENT_FIG3_CW", "READY_CANDIDATE", "Return once to the accepted chamber geometry for the second contradiction")
add_storyboard([10], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_FIG2_CYLINDER", "KZ_SRC_PATENT_DRAWINGS", "NEEDS_SOURCE_COMPOSITE", "Match the cylinder configuration claim to the patent figure")
add_storyboard([11], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_FIG3_CW", "KZ_SRC_PATENT_DRAWINGS", "NEEDS_SOURCE_COMPOSITE", "Match clockwise spiral wording to the patent geometry")
add_storyboard([12], "EXPLANATORY_MODEL", "KZ_MODEL_PATENT_FIG3_CCW", "KZ_SRC_PATENT_FIG3_CW", "NEEDS_DETERMINISTIC_BUILD", "Mirror the verified geometry as an explicitly explanatory counterclockwise state")
add_storyboard([13], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_FIG4_ROTATION", "KZ_EN_HERO01", "NEEDS_SOURCE_COMPOSITE", "Show the motorized patent configuration at the rotation claim")
add_storyboard([14], "RECONSTRUCTION", "KZ_EN_REC01_ENTERING", "KZ_EN_HERO01", "READY_CANDIDATE", "Human scale and entry, with no meditation or effect claim")
add_storyboard([15], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_LUNAR_GEOMAGNETIC", "KZ_SRC_PATENT_COVER_DATE", "NEEDS_SOURCE_COMPOSITE", "Attribute moon and storm conditions to the patent text")
add_storyboard([16], "EXPLANATORY_MODEL", "KZ_CARD_THREE_THEORIES_OPEN", "KZ_EN_HERO01", "NEEDS_DETERMINISTIC_BUILD", "Open the three-way interpretive fork")
add_storyboard([17], "EXPLANATORY_MODEL", "KZ_CARD_THEORY_ISOLATION", "KZ_CARD_THREE_THEORIES_OPEN", "NEEDS_DETERMINISTIC_BUILD", "First competing explanation: isolation")
add_storyboard([18], "EXPLANATORY_MODEL", "KZ_CARD_THEORY_PHYSICAL", "KZ_CARD_THREE_THEORIES_OPEN", "NEEDS_DETERMINISTIC_BUILD", "Second competing explanation: ordinary physical change")
add_storyboard([19], "EXPLANATORY_MODEL", "KZ_CARD_THEORY_INFORMATION", "KZ_CARD_THREE_THEORIES_OPEN", "NEEDS_DETERMINISTIC_BUILD", "Third competing explanation: information access")
add_storyboard([20], "ARCHIVE", "KZ_SRC_KOZYREV_PORTRAIT_FULL", "KZ_SRC_KOZYREV_1959", "NEEDS_SOURCE_COMPOSITE", "Reintroduce the correctly identified man before biography")
add_storyboard([21], "ARCHIVE", "KZ_SRC_KOZYREV_BIOGRAPHY", "KZ_SRC_KOZYREV_PORTRAIT_FULL", "NEEDS_SOURCE_COMPOSITE", "Hold the authentic portrait with concise astronomer attribution")
add_storyboard([22], "EXPLANATORY_MODEL", "KZ_CARD_TIME_AS_ACTIVE_IDEA", "KZ_SRC_KOZYREV_BIOGRAPHY", "NEEDS_DETERMINISTIC_BUILD", "Shift from person to the specific speculative idea")
add_storyboard([23], "INNER_HYPOTHESIS", "KZ_INNER01_INTERNAL_TIME_A", "KZ_CARD_TIME_AS_ACTIVE_IDEA", "NEEDS_NATIVE_IMAGEGEN", "Turn time-as-more-than-coordinate into an episode-specific subjective image")
add_storyboard([24], "INNER_HYPOTHESIS", "KZ_INNER01_INTERNAL_TIME_B", "KZ_INNER01_INTERNAL_TIME_A", "NEEDS_NATIVE_IMAGEGEN", "Escalate to time acting physically without presenting proof")
add_storyboard([25], "INNER_HYPOTHESIS", "KZ_INNER01_INTERNAL_TIME_C", "KZ_INNER01_INTERNAL_TIME_B", "NEEDS_NATIVE_IMAGEGEN", "Land on the possibility of measurable traces")
add_storyboard([26], "ARCHIVE", "KZ_SRC_KAZNACHEEV_TROFIMOV_PAIR", "KZ_SRC_INVENTOR_PAIR_1996", "NEEDS_SOURCE_COMPOSITE", "Show both later researchers at their first research-history beat")
add_storyboard([27], "ARCHIVE", "KZ_SRC_RESEARCHERS_AND_PUBLICATIONS", "KZ_SRC_KAZNACHEEV_TROFIMOV_PAIR", "NEEDS_SOURCE_COMPOSITE", "Connect the named researchers to their documented work, not a generic chamber")
add_storyboard([28], "EXPLANATORY_MODEL", "KZ_CARD_THREE_STREAMS_COLLAPSE", "KZ_SRC_RESEARCHERS_AND_PUBLICATIONS", "NEEDS_DETERMINISTIC_BUILD", "Visualize the online collapse of three distinct histories")
add_storyboard([29], "EXPLANATORY_MODEL", "KZ_CARD_STREAM_KOZYREV_TIME", "KZ_SRC_KOZYREV_BIOGRAPHY", "NEEDS_DETERMINISTIC_BUILD", "Identify stream one: Kozyrev's time theory")
add_storyboard([30], "EXPLANATORY_MODEL", "KZ_CARD_STREAM_RESEARCHERS", "KZ_SRC_KAZNACHEEV_TROFIMOV_PAIR", "NEEDS_DETERMINISTIC_BUILD", "Identify stream two: later experiments")
add_storyboard([31], "EXPLANATORY_MODEL", "KZ_CARD_STREAM_PATENT", "KZ_SRC_PATENT_COVER_DATE", "NEEDS_DETERMINISTIC_BUILD", "Identify stream three: the aluminum medical patent")
add_storyboard([32], "EXPLANATORY_MODEL", "KZ_CARD_THREE_STREAMS_SEPARATED", "KZ_CARD_THREE_STREAMS_COLLAPSE", "NEEDS_DETERMINISTIC_BUILD", "Restore the documentary separation between the three streams")
add_storyboard([33], "RECONSTRUCTION", "KZ_EN_HERO01", "KZ_SRC_PATENT_DRAWINGS", "READY_CANDIDATE", "Brief geometry return before exact apparatus specifications")
add_storyboard([34], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_HEIGHT", "KZ_SRC_PATENT_DIMENSIONS", "NEEDS_SOURCE_COMPOSITE", "Show the 2.8-metre limit where it is spoken")
add_storyboard([35], "RECONSTRUCTION", "KZ_EN_HERO02_SURFACE", "KZ_EN_HERO02", "NEEDS_DETERMINISTIC_BUILD", "Macro crop of the accepted aluminum surface at the polished-surface beat")
add_storyboard([36], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_FOCUS", "KZ_SRC_PATENT_DIMENSIONS", "NEEDS_SOURCE_COMPOSITE", "Show the proposed fifty-centimetre focus in the patent")
add_storyboard([37], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_PANEL_COUNT", "KZ_SRC_PATENT_DIMENSIONS", "NEEDS_SOURCE_COMPOSITE", "Show the four-to-ten panel range")
add_storyboard([38], "EXPLANATORY_MODEL", "KZ_MODEL_DIRECTION_COMPARE", "KZ_SRC_PATENT_FIG3_CW", "NEEDS_DETERMINISTIC_BUILD", "Compare clockwise and counterclockwise geometry without faking a source page")
add_storyboard([39], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_FIG4_ROTATION", "KZ_EN_HERO01", "NEEDS_SOURCE_COMPOSITE", "Return to the verified rotation drawing")
add_storyboard([40], "EXPLANATORY_MODEL", "KZ_CARD_WHY_DIRECTION", "KZ_MODEL_DIRECTION_COMPARE", "NEEDS_DETERMINISTIC_BUILD", "Turn direction into a clear unresolved question")
add_storyboard([41], "EXPLANATORY_MODEL", "KZ_CARD_WHY_MOON", "KZ_SRC_PATENT_LUNAR_GEOMAGNETIC", "NEEDS_DETERMINISTIC_BUILD", "Turn lunar timing into a clear unresolved question")
add_storyboard([42], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_GEOMAGNETIC", "KZ_SRC_PATENT_LUNAR_GEOMAGNETIC", "NEEDS_SOURCE_COMPOSITE", "Match geomagnetic wording to its original source")
add_storyboard([43], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_INVENTOR_CLAIM", "KZ_SRC_PATENT_INVENTORS", "NEEDS_SOURCE_COMPOSITE", "Frame the next explanation explicitly as the inventors' answer")
add_storyboard([44], "EXPLANATORY_MODEL", "KZ_MODEL_FIELD_CONCENTRATION", "KZ_SRC_PATENT_INVENTOR_CLAIM", "NEEDS_DETERMINISTIC_BUILD", "Explain the claimed field-concentration mechanism without validating it")
add_storyboard([45], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_HELIOGEOPHYSICAL", "KZ_SRC_PATENT_GEOMAGNETIC", "NEEDS_SOURCE_COMPOSITE", "Show the exact heliogeophysical attribution")
add_storyboard([46], "ARCHIVE", "KZ_SRC_INVENTOR_PAIR_CLAIMS", "KZ_SRC_KAZNACHEEV_TROFIMOV_PAIR", "NEEDS_SOURCE_COMPOSITE", "Put the claims back beside the people who made them")
add_storyboard([47], "EXPLANATORY_MODEL", "KZ_CARD_PATENT_RECORDS_CLAIM", "KZ_SRC_PATENT_INVENTOR_CLAIM", "NEEDS_DETERMINISTIC_BUILD", "Define what a patent records")
add_storyboard([48], "EXPLANATORY_MODEL", "KZ_CARD_CLAIM_NOT_PROOF", "KZ_SRC_PATENT_INVENTOR_CLAIM", "NEEDS_DETERMINISTIC_BUILD", "Hold the evidence boundary: claim is not proof")
add_storyboard([49], "ARCHIVE", "KZ_SRC_RESEARCHERS_LATER_WORK", "KZ_SRC_KAZNACHEEV_TROFIMOV_PAIR", "NEEDS_SOURCE_COMPOSITE", "Return to both researchers as the story leaves medicine")
add_storyboard([50], "ORIGINAL_DOCUMENT", "KZ_SRC_2006_MODELED_SPACE", "KZ_SRC_2006_2008_PUBLICATIONS", "NEEDS_SOURCE_COMPOSITE", "Show their modeled-Kozyrev-space publication")
add_storyboard([51], "INNER_HYPOTHESIS", "KZ_INNER01_INTERNAL_TIME_C", "KZ_SRC_2006_MODELED_SPACE", "NEEDS_NATIVE_IMAGEGEN", "Reconnect the later altered-time claim to the established internal-time motif")
add_storyboard([52], "INNER_HYPOTHESIS", "KZ_INNER02_DISTANT_IMAGE_A", "KZ_SRC_2006_MODELED_SPACE", "NEEDS_NATIVE_IMAGEGEN", "Make distant information perceptible only as a fractured reflection")
add_storyboard([53], "INNER_HYPOTHESIS", "KZ_INNER02_DISTANT_IMAGE_B", "KZ_INNER02_DISTANT_IMAGE_A", "NEEDS_NATIVE_IMAGEGEN", "Escalate the attributed remote-object claim without a portal or proof cue")
add_storyboard([54], "RECONSTRUCTION", "KZ_HERO01_REFLECTION_STATE", "KZ_EN_HERO01", "NEEDS_DETERMINISTIC_BUILD", "Return to the metal reflector with a distinct slow reflective motion state")
add_storyboard([55], "RECONSTRUCTION", "KZ_EN_REC02_SEATED_NEUTRAL", "KZ_EN_REC01_ENTERING", "NEEDS_GENERATION", "Place a neutral participant inside for the experience question")
add_storyboard([56], "EXPLANATORY_MODEL", "KZ_CARD_THEORY_FORK_RETURN", "KZ_CARD_THREE_THEORIES_OPEN", "NEEDS_DETERMINISTIC_BUILD", "Re-open the three explanations before testing them")
add_storyboard([57], "EXPLANATORY_MODEL", "KZ_CARD_THEORY_ISOLATION_ACTIVE", "KZ_CARD_THEORY_ISOLATION", "NEEDS_DETERMINISTIC_BUILD", "Activate the psychological branch")
add_storyboard([58], "RECONSTRUCTION", "KZ_EN_REC02_SEATED_ISOLATION", "KZ_EN_REC02_SEATED_NEUTRAL", "NEEDS_GENERATION", "Show isolation, expectation and unusual sensory conditions without mystic effects")
add_storyboard([59], "EXPLANATORY_MODEL", "KZ_CARD_EXPERIENCE_NOT_INFORMATION", "KZ_CARD_THEORY_ISOLATION_ACTIVE", "NEEDS_DETERMINISTIC_BUILD", "Separate genuine experience from external information")
add_storyboard([60], "EXPLANATORY_MODEL", "KZ_CARD_THEORY_PHYSICAL_ACTIVE", "KZ_CARD_THEORY_PHYSICAL", "NEEDS_DETERMINISTIC_BUILD", "Activate the ordinary physical branch")
add_storyboard([61], "EXPLANATORY_MODEL", "KZ_MODEL_ORDINARY_VARIABLES", "KZ_EN_HERO02", "NEEDS_DETERMINISTIC_BUILD", "Map sound, temperature, reflections and body sensing onto physical details")
add_storyboard([62, 88], "EXPLANATORY_MODEL", "KZ_CARD_PHYSICAL_VARIABLES", "KZ_MODEL_ORDINARY_VARIABLES", "NEEDS_DETERMINISTIC_BUILD", "Keep the measurable ordinary variables available at both logic beats")
add_storyboard([63], "EXPLANATORY_MODEL", "KZ_CARD_MEASURABLE_NOT_TIME_TRAVEL", "KZ_CARD_PHYSICAL_VARIABLES", "NEEDS_DETERMINISTIC_BUILD", "Explicitly separate measurement from time travel")
add_storyboard([64], "EXPLANATORY_MODEL", "KZ_CARD_THEORY_INFORMATION_ACTIVE", "KZ_CARD_THEORY_INFORMATION", "NEEDS_DETERMINISTIC_BUILD", "Activate the proponents' extraordinary branch")
add_storyboard([65], "INNER_HYPOTHESIS", "KZ_INNER02_DISTANT_IMAGE_C", "KZ_INNER02_DISTANT_IMAGE_B", "NEEDS_NATIVE_IMAGEGEN", "Visualize information across distance/time as subjective reflection")
add_storyboard([66], "EXPLANATORY_MODEL", "KZ_CARD_EXTRAORDINARY_POSSIBILITY", "KZ_INNER02_DISTANT_IMAGE_C", "NEEDS_DETERMINISTIC_BUILD", "Name the extraordinary possibility without endorsing it")
add_storyboard([67], "EXPLANATORY_MODEL", "KZ_CARD_CLEAN_TEST", "KZ_CARD_EXTRAORDINARY_POSSIBILITY", "NEEDS_DETERMINISTIC_BUILD", "Pivot from mystery to a decisive test")
add_storyboard([68], "EXPLANATORY_MODEL", "KZ_CARD_FEELING_NOT_TEST", "KZ_EN_REC02_SEATED_NEUTRAL", "NEEDS_DETERMINISTIC_BUILD", "Reject subjective feeling as the decisive outcome")
add_storyboard([69], "EXPLANATORY_MODEL", "KZ_CARD_UNKNOWN_INFORMATION", "KZ_CARD_CLEAN_TEST", "NEEDS_DETERMINISTIC_BUILD", "Define the target outcome: information not already knowable")
add_storyboard([70], "EXPLANATORY_MODEL", "KZ_TARGET_GRID_SEALED", "KZ_CARD_CLEAN_TEST", "NEEDS_DETERMINISTIC_BUILD", "Introduce four fixed sealed targets")
add_storyboard([71], "EXPLANATORY_MODEL", "KZ_TARGET01_LIGHTHOUSE", "KZ_TARGET_GRID_SEALED", "NEEDS_GENERATION", "Show the lighthouse target exactly when named")
add_storyboard([72], "EXPLANATORY_MODEL", "KZ_TARGET02_VIOLIN", "KZ_TARGET_GRID_SEALED", "NEEDS_GENERATION", "Show the violin target exactly when named")
add_storyboard([73], "EXPLANATORY_MODEL", "KZ_TARGET03_BURNING_CAR", "KZ_TARGET_GRID_SEALED", "NEEDS_GENERATION", "Show the burning-car target exactly when named")
add_storyboard([74], "EXPLANATORY_MODEL", "KZ_TARGET04_WHITE_HORSE", "KZ_TARGET_GRID_SEALED", "NEEDS_GENERATION", "Show the horse target exactly when named")
add_storyboard([75], "EXPLANATORY_MODEL", "KZ_TARGET_GRID_CHOOSE", "KZ_TARGET_GRID_SEALED", "NEEDS_DETERMINISTIC_BUILD", "Invite a viewer choice while all four targets remain visible")
add_storyboard([76], "EXPLANATORY_MODEL", "KZ_TARGET_GRID_HOLD", "KZ_TARGET_GRID_CHOOSE", "NEEDS_DETERMINISTIC_BUILD", "Preserve the choice for the later reveal")
add_storyboard([77], "EXPLANATORY_MODEL", "KZ_PROTOCOL_RANDOM_SELECTION", "KZ_TARGET_GRID_HOLD", "NEEDS_DETERMINISTIC_BUILD", "Show selection occurring only after chamber entry")
add_storyboard([78], "EXPLANATORY_MODEL", "KZ_PROTOCOL_DOUBLE_BLIND", "KZ_PROTOCOL_RANDOM_SELECTION", "NEEDS_DETERMINISTIC_BUILD", "Make the nobody-knows condition unmistakable")
add_storyboard([79], "RECONSTRUCTION", "KZ_EN_REC03_PARTICIPANT_REPORT", "KZ_PROTOCOL_DOUBLE_BLIND", "NEEDS_GENERATION", "Show speech/drawing before target reveal")
add_storyboard([80], "EXPLANATORY_MODEL", "KZ_PROTOCOL_JUDGING", "KZ_EN_REC03_PARTICIPANT_REPORT", "NEEDS_DETERMINISTIC_BUILD", "Show independent pre-registered comparison against all four targets")
add_storyboard([81], "EXPLANATORY_MODEL", "KZ_REPLICATION_CHAIN_LAB2", "KZ_PROTOCOL_JUDGING", "NEEDS_DETERMINISTIC_BUILD", "Extend the procedure into a second laboratory")
add_storyboard([82], "EXPLANATORY_MODEL", "KZ_TARGET_MATCH_LIGHTHOUSE", "KZ_TARGET01_LIGHTHOUSE", "NEEDS_DETERMINISTIC_BUILD", "Show why tower/red/ice resembles the lighthouse")
add_storyboard([83], "EXPLANATORY_MODEL", "KZ_CARD_ONE_MATCH_CHANCE", "KZ_TARGET_MATCH_LIGHTHOUSE", "NEEDS_DETERMINISTIC_BUILD", "Downgrade one resemblance to a chance-compatible observation")
add_storyboard([84], "EXPLANATORY_MODEL", "KZ_CARD_POSTHOC_INTERPRETATION", "KZ_CARD_ONE_MATCH_CHANCE", "NEEDS_DETERMINISTIC_BUILD", "Expose interpretation after the answer is known")
add_storyboard([85], "EXPLANATORY_MODEL", "KZ_REPLICATION_REPEATED_BLIND", "KZ_PROTOCOL_JUDGING", "NEEDS_DETERMINISTIC_BUILD", "Show the repeated blinded pattern that would matter")
add_storyboard([86], "EXPLANATORY_MODEL", "KZ_CARD_THEORIES_FORCED_APART", "KZ_CARD_THEORY_FORK_RETURN", "NEEDS_DETERMINISTIC_BUILD", "Separate the predictions of all three explanations")
add_storyboard([87], "EXPLANATORY_MODEL", "KZ_CARD_PSYCHOLOGY_PREDICTION", "KZ_CARD_THEORY_ISOLATION_ACTIVE", "NEEDS_DETERMINISTIC_BUILD", "Psychology predicts an intense state, not target access")
add_storyboard([89], "EXPLANATORY_MODEL", "KZ_CARD_RANDOM_TARGET_BOUNDARY", "KZ_TARGET_GRID_SEALED", "NEEDS_DETERMINISTIC_BUILD", "Show that neither ordinary branch predicts a random hidden image")
add_storyboard([90], "EXPLANATORY_MODEL", "KZ_CARD_MISSING_EXPERIMENT", "KZ_REPLICATION_REPEATED_BLIND", "NEEDS_DETERMINISTIC_BUILD", "Make the missing controlled experiment the central absence")
add_storyboard([91], "ORIGINAL_DOCUMENT", "KZ_SRC_EVIDENCE_PATENT", "KZ_SRC_PATENT_COVER_DATE", "NEEDS_SOURCE_COMPOSITE", "Return to the real patent in the source stack")
add_storyboard([92], "ORIGINAL_DOCUMENT", "KZ_SRC_EVIDENCE_PUBLICATIONS", "KZ_SRC_2006_MODELED_SPACE", "NEEDS_SOURCE_COMPOSITE", "Return to the researchers' extraordinary-effect publications")
add_storyboard([93], "EXPLANATORY_MODEL", "KZ_REPLICATION_CHAIN_MISSING", "KZ_SRC_EVIDENCE_PUBLICATIONS", "NEEDS_DETERMINISTIC_BUILD", "Show the broken independent-replication chain")
add_storyboard([94], "EXPLANATORY_MODEL", "KZ_CARD_APPARATUS_NOT_EVIDENCE", "KZ_EN_HERO01", "NEEDS_DETERMINISTIC_BUILD", "Separate the documented apparatus from missing empirical evidence")
add_storyboard([95], "EXPLANATORY_MODEL", "KZ_CARD_INDEPENDENT_RESULT", "KZ_REPLICATION_CHAIN_MISSING", "NEEDS_DETERMINISTIC_BUILD", "Name the independent result as the missing link")
add_storyboard([96], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_AUTHORITY_TRAP", "KZ_SRC_PATENT_COVER_DATE", "NEEDS_SOURCE_COMPOSITE", "Set up the final patent-authority trap")
add_storyboard([97], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_AUTHORITY_FULL", "KZ_SRC_PATENT_AUTHORITY_TRAP", "NEEDS_SOURCE_COMPOSITE", "Let the formal page resemble a verdict before deconstruction")
add_storyboard([98], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_NUMBER_CROP", "KZ_SRC_PATENT_AUTHORITY_FULL", "NEEDS_SOURCE_COMPOSITE", "Isolate the government number")
add_storyboard([99], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_DATES_CROP", "KZ_SRC_PATENT_AUTHORITY_FULL", "NEEDS_SOURCE_COMPOSITE", "Isolate the dates")
add_storyboard([100], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_INVENTORS_CROP", "KZ_SRC_PATENT_AUTHORITY_FULL", "NEEDS_SOURCE_COMPOSITE", "Isolate the inventor names")
add_storyboard([101], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_DRAWINGS", "KZ_SRC_PATENT_AUTHORITY_FULL", "NEEDS_SOURCE_COMPOSITE", "Isolate the technical drawings")
add_storyboard([102], "EXPLANATORY_MODEL", "KZ_CARD_LANGUAGE_OF_AUTHORITY", "KZ_SRC_PATENT_AUTHORITY_FULL", "NEEDS_DETERMINISTIC_BUILD", "Name why the page feels authoritative")
add_storyboard([103], "EXPLANATORY_MODEL", "KZ_CARD_PATENTED_MEANS_PROVEN", "KZ_CARD_LANGUAGE_OF_AUTHORITY", "NEEDS_DETERMINISTIC_BUILD", "Expose the online patented-means-proven inference")
add_storyboard([104], "EXPLANATORY_MODEL", "KZ_CARD_IT_DOES_NOT", "KZ_CARD_PATENTED_MEANS_PROVEN", "NEEDS_DETERMINISTIC_BUILD", "Break the false inference with a short hard stop")
add_storyboard([105], "EXPLANATORY_MODEL", "KZ_CARD_PATENT_CAN_SHOW", "KZ_SRC_PATENT_AUTHORITY_FULL", "NEEDS_DETERMINISTIC_BUILD", "List the legitimate provenance uses of a patent")
add_storyboard([106], "EXPLANATORY_MODEL", "KZ_CARD_PATENT_NOT_CERTIFY", "KZ_CARD_PATENT_CAN_SHOW", "NEEDS_DETERMINISTIC_BUILD", "State that patent status does not certify extraordinary effects")
add_storyboard([107], "ORIGINAL_DOCUMENT", "KZ_SRC_EVIDENCE_STACK", "KZ_SRC_PATENT_AUTHORITY_FULL", "NEEDS_SOURCE_COMPOSITE", "Reframe the patent as invaluable documentation, not proof")
add_storyboard([108], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_DIMENSIONS", "KZ_SRC_PATENT_HEIGHT", "NEEDS_SOURCE_COMPOSITE", "Return to the dimensions the document actually supplies")
add_storyboard([109], "RECONSTRUCTION", "KZ_EN_HERO02_ALUMINUM", "KZ_EN_HERO02", "NEEDS_DETERMINISTIC_BUILD", "Macro state for aluminum alloy")
add_storyboard([110], "RECONSTRUCTION", "KZ_EN_HERO02_POLISHED", "KZ_EN_HERO02", "NEEDS_DETERMINISTIC_BUILD", "Distinct macro state for polished surfaces")
add_storyboard([111], "RECONSTRUCTION", "KZ_EN_HERO02_FASTENERS", "KZ_EN_HERO02", "NEEDS_DETERMINISTIC_BUILD", "Distinct macro state for fasteners")
add_storyboard([112], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_FOCUS", "KZ_SRC_PATENT_DIMENSIONS", "NEEDS_SOURCE_COMPOSITE", "Return to the proposed focal distance")
add_storyboard([113], "EXPLANATORY_MODEL", "KZ_MODEL_DIRECTION_COMPARE", "KZ_SRC_PATENT_FIG3_CW", "NEEDS_DETERMINISTIC_BUILD", "Return to direction as documented geometry")
add_storyboard([114], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_FIG4_ROTATION", "KZ_EN_HERO01", "NEEDS_SOURCE_COMPOSITE", "Return to rotation as documented hardware")
add_storyboard([115], "RECONSTRUCTION", "KZ_EN_HERO02_SCREWS_PAYOFF", "KZ_EN_HERO02", "NEEDS_DETERMINISTIC_BUILD", "Pay off the line that the invisible acquired screws")
add_storyboard([116], "RECONSTRUCTION", "KZ_EN_REC18_EMPTY_CHAMBER_A", "KZ_EN_HERO01", "NEEDS_GENERATION", "Strip the legend back to an empty documented object")
add_storyboard([117], "ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_DOCUMENTED_CHAMBER", "KZ_SRC_EVIDENCE_STACK", "NEEDS_SOURCE_COMPOSITE", "Pair the empty object with the document that establishes it")
add_storyboard([118], "ARCHIVE", "KZ_SRC_KAZNACHEEV_TROFIMOV_CLAIM_HISTORY", "KZ_SRC_KAZNACHEEV_TROFIMOV_PAIR", "NEEDS_SOURCE_COMPOSITE", "Show the correct researchers beside their unusual claims")
add_storyboard([119], "ORIGINAL_DOCUMENT", "KZ_SRC_CLAIM_HISTORY_PUBLICATIONS", "KZ_SRC_EVIDENCE_PUBLICATIONS", "NEEDS_SOURCE_COMPOSITE", "Place intense-experience reports inside the project history")
add_storyboard([120], "ARCHIVE", "KZ_SRC_KOZYREV_NOT_BUILDER", "KZ_SRC_KOZYREV_PORTRAIT_1983", "NEEDS_SOURCE_COMPOSITE", "Restore Kozyrev's identity and no-builder boundary at the conclusion")
add_storyboard([121], "RECONSTRUCTION", "KZ_EN_REC18_EMPTY_CHAMBER_B", "KZ_EN_REC18_EMPTY_CHAMBER_A", "NEEDS_GENERATION", "Hold the unconfirmed central claim in an empty-room state")
add_storyboard([122], "INNER_HYPOTHESIS", "KZ_INNER02_TEST_QUESTION", "KZ_INNER02_DISTANT_IMAGE_C", "NEEDS_NATIVE_IMAGEGEN", "Bring the supernatural possibility back only as the decisive question")
add_storyboard([123], "EXPLANATORY_MODEL", "KZ_PROTOCOL_CLEAN_TEST", "KZ_CARD_CLEAN_TEST", "NEEDS_DETERMINISTIC_BUILD", "Return to the exact clean test")
add_storyboard([124], "EXPLANATORY_MODEL", "KZ_REPLICATION_CHAIN_MISSING", "KZ_CARD_INDEPENDENT_RESULT", "NEEDS_DETERMINISTIC_BUILD", "End the evidence argument on the absent independent result")
add_storyboard([125, 126], "RECONSTRUCTION", "KZ_CLIP_EMPTY_SPIRAL_PAYOFF", "KZ_EN_REC18_EMPTY_CHAMBER_B", "CLIP_CANDIDATE_STORYBOARDED", "Unresolved empty chamber payoff across the final two questions")
add_storyboard([127], "EXPLANATORY_MODEL", "KZ_MAP_NOVOSIBIRSK_TO_FORT_MEADE", "KZ_CARD_MISSING_EXPERIMENT", "NEEDS_DETERMINISTIC_BUILD", "Move the next-file handoff out of the chamber and across the map")
add_storyboard([128], "EXPLANATORY_MODEL", "KZ_MAP_FORT_MEADE_ZOOM", "KZ_MAP_NOVOSIBIRSK_TO_FORT_MEADE", "NEEDS_DETERMINISTIC_BUILD", "Land geographically on Fort Meade")
add_storyboard([129], "EXPLANATORY_MODEL", "KZ_CARD_THREE_OBSERVERS_THREE_TIMES", "KZ_MAP_FORT_MEADE_ZOOM", "NEEDS_DETERMINISTIC_BUILD", "Tease the next protocol's three-observer time structure")

# Hard picture-lock corrections: later callbacks must be genuinely new source
# details, actions or compositions.  These overrides remove every state return
# that would otherwise re-use a prior export after a visual change.
STORYBOARD[33] = ("RECONSTRUCTION", "KZ_EN_REC04_CHAMBER_REVERSE_WIDE", "", "NEEDS_GENERATION", "New reverse-angle chamber moment before the physical specifications")
STORYBOARD[35] = ("ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_POLISHED_SURFACE_TEXT", "", "NEEDS_SOURCE_COMPOSITE", "Use the patent's material wording instead of cropping the later HERO02 payoff")
STORYBOARD[39] = ("EXPLANATORY_MODEL", "KZ_MODEL_ROTATION_CUTAWAY", "", "NEEDS_DETERMINISTIC_BUILD", "Use a new cutaway state rather than returning to the earlier figure-four export")
STORYBOARD[51] = ("ORIGINAL_DOCUMENT", "KZ_SRC_2006_ALTERED_INTERNAL_TIME", "", "NEEDS_SOURCE_COMPOSITE", "Use a new publication detail; do not restart the earlier internal-time image")
STORYBOARD[65] = ("EXPLANATORY_MODEL", "KZ_MODEL_INFORMATION_ACROSS_DISTANCE", "", "NEEDS_DETERMINISTIC_BUILD", "Use a new theory diagram rather than returning to the distant-image sequence")
STORYBOARD[88] = ("EXPLANATORY_MODEL", "KZ_CARD_PHYSICAL_PREDICTION", "", "NEEDS_DETERMINISTIC_BUILD", "Use a new prediction card instead of returning to the variables card")
STORYBOARD[112] = ("ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_FOCUS_TEXT_DETAIL", "", "NEEDS_SOURCE_COMPOSITE", "Use a distinct text detail rather than returning to the earlier focus diagram")
STORYBOARD[113] = ("ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_DIRECTION_TEXT_DETAIL", "", "NEEDS_SOURCE_COMPOSITE", "Use a new verified direction detail rather than the earlier comparison model")
STORYBOARD[114] = ("ORIGINAL_DOCUMENT", "KZ_SRC_PATENT_ROTATION_TEXT_DETAIL", "", "NEEDS_SOURCE_COMPOSITE", "Use a new verified rotation detail rather than the earlier figure-four export")
STORYBOARD[120] = ("ARCHIVE", "KZ_SRC_KOZYREV_THIRD_AUTHENTIC_CONTEXT", "", "NEEDS_SOURCE_RESEARCH", "Show Kozyrev in a genuinely different authenticated context at the no-builder conclusion")
STORYBOARD[122] = ("EXPLANATORY_MODEL", "KZ_CARD_DECISIVE_INFORMATION_QUESTION", "", "NEEDS_DETERMINISTIC_BUILD", "Use a new decisive-question composition, not the earlier distant-image motif")
STORYBOARD[124] = ("EXPLANATORY_MODEL", "KZ_CARD_RESULT_STILL_MISSING", "", "NEEDS_DETERMINISTIC_BUILD", "Use a new terminal missing-result state rather than restarting the replication-chain asset")
STORYBOARD[21] = ("ARCHIVE", "KZ_SRC_KOZYREV_SECOND_AUTHENTIC_CONTEXT", "", "NEEDS_SOURCE_RESEARCH", "Continue the second authenticated Kozyrev context through the biography line")
STORYBOARD[20] = ("ARCHIVE", "KZ_SRC_KOZYREV_SECOND_AUTHENTIC_CONTEXT", "", "NEEDS_SOURCE_RESEARCH", "Use a genuinely different authenticated Kozyrev image from the earlier death-date block")
for cue in (23, 24, 25):
    STORYBOARD[cue] = ("INNER_HYPOTHESIS", "KZ_CLIP_INTERNAL_TIME_CONTINUOUS", "", "CLIP_CANDIDATE_STORYBOARDED", "One continuously evolving internal-time sequence; never restart or recycle it")
for cue in (52, 53):
    STORYBOARD[cue] = ("INNER_HYPOTHESIS", "KZ_CLIP_DISTANT_IMAGE_CONTINUOUS", "", "CLIP_CANDIDATE_STORYBOARDED", "One continuously evolving distant-image sequence; no portal, beam, badge or restart")
for cue in (109, 110, 111):
    STORYBOARD[cue] = ("RECONSTRUCTION", "KZ_EN_HERO02", "", "READY_CANDIDATE", "One continuous accepted material-detail shot across alloy, surface and fasteners")
STORYBOARD[115] = ("RECONSTRUCTION", "KZ_EN_REC05_SCREWS_MACRO", "", "NEEDS_GENERATION", "New physical macro action for the screws payoff; not a crop of HERO02")
STORYBOARD[21] = ("ARCHIVE", "KZ_SRC_KOZYREV_ASTRONOMER_CONTEXT", "", "NEEDS_SOURCE_RESEARCH", "Move from the second portrait to a different authenticated astronomy context; no long portrait hold")
STORYBOARD[58] = ("RECONSTRUCTION", "KZ_CLIP_ISOLATION_SENSORY_CONTINUOUS", "", "CLIP_CANDIDATE_STORYBOARDED", "One evolving sensory-isolation sequence with new information throughout the long sentence")

# A planned fallback that repeats an earlier picture would violate the same
# lock if substituted in the edit.  Missing primaries therefore remain honest
# missing requirements instead of silently falling back to recycled coverage.
for cue, (mode, asset, _fallback, status, function) in list(STORYBOARD.items()):
    STORYBOARD[cue] = (mode, asset, "", status, function)


if set(STORYBOARD) != set(range(1, 130)):
    missing = sorted(set(range(1, 130)) - set(STORYBOARD))
    extra = sorted(set(STORYBOARD) - set(range(1, 130)))
    raise RuntimeError(f"Storyboard coverage error; missing={missing} extra={extra}")


SEQUENCE_FAMILY_RANGES = [
    (2, 4, "KZ_SEQ_PATENT_HOOK"),
    (5, 8, "KZ_SEQ_1983_1996_CONTRADICTION"),
    (10, 13, "KZ_SEQ_PATENT_CONFIGURATIONS"),
    (16, 19, "KZ_SEQ_THREE_THEORIES_INTRO"),
    (20, 22, "KZ_SEQ_KOZYREV_BIO_IDEA"),
    (23, 25, "KZ_INNER01_INTERNAL_TIME"),
    (26, 27, "KZ_SEQ_RESEARCHER_IDENTITIES"),
    (28, 32, "KZ_SEQ_THREE_STREAMS"),
    (34, 39, "KZ_SEQ_PATENT_PHYSICAL_DESIGN"),
    (40, 42, "KZ_SEQ_PATENT_CONDITIONS_QUESTIONS"),
    (43, 48, "KZ_SEQ_PATENT_CLAIMS_BOUNDARY"),
    (49, 50, "KZ_SEQ_RESEARCHERS_LATER_WORK"),
    (52, 53, "KZ_INNER02_DISTANT_IMAGE"),
    (54, 55, "KZ_SEQ_CHAMBER_EXPERIENCE"),
    (56, 59, "KZ_SEQ_THEORY_PSYCHOLOGY"),
    (60, 63, "KZ_SEQ_THEORY_PHYSICAL"),
    (64, 69, "KZ_SEQ_THEORY_INFORMATION_TEST"),
    (70, 80, "KZ_SEQ_BLIND_TARGET_PROTOCOL"),
    (82, 84, "KZ_SEQ_MATCH_VS_CHANCE"),
    (85, 90, "KZ_SEQ_PREDICTIONS_AND_MISSING_TEST"),
    (91, 95, "KZ_SEQ_EVIDENCE_AND_REPLICATION"),
    (96, 106, "KZ_SEQ_PATENT_AUTHORITY_TRAP"),
    (107, 115, "KZ_SEQ_PATENT_PHYSICAL_PAYOFF"),
    (116, 121, "KZ_SEQ_DOCUMENTED_RESIDUE"),
    (122, 124, "KZ_SEQ_FINAL_TEST_QUESTION"),
    (125, 126, "KZ_CLIP_EMPTY_SPIRAL_PAYOFF"),
    (127, 129, "KZ_SEQ_FORT_MEADE_HANDOFF"),
]


def sequence_family(index: int, state_asset: str) -> str:
    for start, end, family in SEQUENCE_FAMILY_RANGES:
        if start <= index <= end:
            return family
    return state_asset


def visual_action(mode: str, index: int, state_asset: str) -> str:
    if mode == "ORIGINAL_DOCUMENT":
        return f"Reframe or highlight only the verified source region for state {state_asset}; preserve original page text"
    if mode == "ARCHIVE":
        return f"Use authenticated identity material for state {state_asset}; restrained crop/parallax only"
    if mode == "INNER_HYPOTHESIS":
        return f"Progress to subjective state {state_asset}; no visible category label and no proof-coded beam or portal"
    if "TARGET" in state_asset or "PROTOCOL" in state_asset or "REPLICATION" in state_asset:
        return f"Advance the controlled-test procedure to state {state_asset}; retain fixed targets and ordering"
    if mode == "EXPLANATORY_MODEL":
        return f"Progressively reveal state {state_asset}; one spoken claim at a time, no production-mode badge"
    if state_asset.startswith("KZ_EN_HERO02"):
        return f"Use a distinct physical macro crop for state {state_asset}; do not repeat the previous framing"
    return f"Use the concrete reconstruction state {state_asset}; preserve chamber geometry and change framing or action"


def motion_class(state_asset: str) -> str:
    return "PROGRESSIVE_MOTION" if state_asset.startswith("KZ_CLIP_") else "STATIC_OR_NEAR_STATIC"


LONG_HOLD_REASONS = {
    "KZ_CLIP_INTERNAL_TIME_CONTINUOUS": "The single uninterrupted sequence visibly evolves through dust, condensation and delayed reflection as the three spoken claims escalate; a camera move alone is insufficient.",
    "KZ_CLIP_ISOLATION_SENSORY_CONTINUOUS": "The participant, acoustics, light and body-orientation cues develop across the sentence; the sequence cannot be a held still or simple zoom.",
    "KZ_CLIP_EMPTY_SPIRAL_PAYOFF": "The final chamber action advances continuously from mechanical stillness to a changing reflection/shadow and unresolved darkness across two questions; it is never restarted.",
}


def main() -> int:
    data = json.loads(ALIGN.read_text(encoding="utf-8"))
    source = data["source_text"]
    starts = data["character_start_times_seconds"]
    ends = data["character_end_times_seconds"]
    paragraphs = [part.strip() for part in source.split("\n\n") if part.strip()]
    rows = []
    cursor = 0
    for index, paragraph in enumerate(paragraphs, 1):
        position = source.find(paragraph, cursor)
        if position < 0:
            raise RuntimeError(f"Paragraph not found: {paragraph[:80]}")
        last = position + len(paragraph) - 1
        start = float(starts[position])
        end = float(ends[last])
        cursor = last + 1
        mode, state_asset, fallback, status, rationale = STORYBOARD[index]
        primary = sequence_family(index, state_asset)
        rows.append(
            {
                "cue_id": f"KZ-CUE-{index:03d}",
                "start_seconds": f"{start:.3f}",
                "end_seconds": f"{end:.3f}",
                "duration_seconds": f"{end - start:.3f}",
                "voice_text": paragraph,
                "visual_mode_internal": mode,
                "primary_asset_id": primary,
                "visual_state_id": state_asset,
                "fallback_asset_id": fallback,
                "asset_status": status,
                "viewer_function": rationale,
                "visual_action": visual_action(mode, index, state_asset),
                "motion_class": motion_class(state_asset),
                "long_hold_reason": LONG_HOLD_REASONS.get(state_asset, ""),
                "visible_mode_badge": "NO",
                "allowed_context_line": "FIRST_BLOCK_ONLY_MAX_2S" if index == 1 else "NO",
            }
        )

    # Hard picture lock: an ID may span adjacent cues, but after the timeline
    # switches away it may never return.  Validate both deliverable families
    # and their concrete still/document/card/clip states.
    for field in ("primary_asset_id", "visual_state_id"):
        seen_runs: set[str] = set()
        previous = None
        returns: list[dict] = []
        for row in rows:
            value = row[field]
            if value != previous:
                if value in seen_runs:
                    returns.append({"cue_id": row["cue_id"], "asset_id": value})
                seen_runs.add(value)
                previous = value
        if returns:
            raise RuntimeError(f"Hard picture-lock return in {field}: {returns}")
    OUT.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with (OUT / "EP01_EN_VISUAL_CUE_SHEET.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    timing = {
        "source_text": source,
        "audio": data["audio"],
        "audio_sha256": data["audio_sha256"],
        "cue_count": len(rows),
        "cues": rows,
    }
    (OUT / "EP01_EN_PARAGRAPH_TIMING.json").write_text(json.dumps(timing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    srt = []
    vtt = ["WEBVTT", ""]
    for index, row in enumerate(rows, 1):
        start = float(row["start_seconds"])
        end = float(row["end_seconds"])
        srt.extend([str(index), f"{timecode(start)} --> {timecode(end)}", row["voice_text"], ""])
        vtt.extend([f"{timecode(start, True)} --> {timecode(end, True)}", row["voice_text"], ""])
    (OUT / "EP01_EN_KOZYREV.srt").write_text("\n".join(srt), encoding="utf-8")
    (OUT / "EP01_EN_KOZYREV.vtt").write_text("\n".join(vtt), encoding="utf-8")

    required = {}
    for row in rows:
        item = required.setdefault(
            row["primary_asset_id"],
            {
                "status": "READY_CANDIDATE",
                "visual_modes_internal": [],
                "visible_mode_badge": "NO",
                "viewer_functions": [],
                "first_start_seconds": float(row["start_seconds"]),
                "last_end_seconds": float(row["end_seconds"]),
                "states": [],
            },
        )
        if row["asset_status"] != "READY_CANDIDATE":
            item["status"] = "NEEDS_BUILD_OR_REVIEW"
        if row["visual_mode_internal"] not in item["visual_modes_internal"]:
            item["visual_modes_internal"].append(row["visual_mode_internal"])
        if row["viewer_function"] not in item["viewer_functions"]:
            item["viewer_functions"].append(row["viewer_function"])
        item["states"].append(
            {
                "cue_id": row["cue_id"],
                "state_id": row["visual_state_id"],
                "component_status": row["asset_status"],
                "start_seconds": float(row["start_seconds"]),
                "end_seconds": float(row["end_seconds"]),
                "visual_action": row["visual_action"],
                "motion_class": row["motion_class"],
                "long_hold_reason": row["long_hold_reason"],
            }
        )
        item["first_start_seconds"] = min(item["first_start_seconds"], float(row["start_seconds"]))
        item["last_end_seconds"] = max(item["last_end_seconds"], float(row["end_seconds"]))
    (OUT / "EP01_EN_REQUIRED_ASSET_SET.json").write_text(json.dumps(required, indent=2) + "\n", encoding="utf-8")
    print(f"cues={len(rows)} unique_primary_assets={len(required)} first={rows[0]['start_seconds']} last={rows[-1]['end_seconds']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
