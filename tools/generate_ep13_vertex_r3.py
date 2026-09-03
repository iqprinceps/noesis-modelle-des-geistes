#!/usr/bin/env python3
"""EP13 round 3: fill the beats the first two rounds left unserved.

Derived from the forced alignment, not estimated. The episode has 115 spoken
beats over 7:55 of narration. Rounds one and two produced the vision sequence,
the object states and the acted beats; this pass covers what the beat map shows
still uncovered, mostly the waiting section, the attack, the three readings and
the handoff into EP14.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import REGISTER_A, REGISTER_B, run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r3"

JOBS = [
    # ---- the waiting: what grew into the empty space -----------------------
    {"name": "EP13_H16_NEWSPAPER_STACK.png", "register": REGISTER_A, "prompt": (
        "A tall untidy stack of folded mid-twentieth-century newspapers on a wooden floor, "
        "photographed close from a low angle so the stack rises past the top of the frame. "
        "The paper is yellowed and softened at the folds. All headlines and body text are "
        "turned away, creased shut or out of focus, so no word is readable anywhere. Cool "
        "grey daylight from one side. No photographs visible on any front page, no colour "
        "print, no modern paper.")},
    {"name": "EP13_H17_EMPTY_PEWS.png", "register": REGISTER_A, "prompt": (
        "The interior of a large plain church seen down the central aisle, completely empty, "
        "every pew unoccupied. Cold grey light falls from high windows onto stone. No altar "
        "detail in focus, no statues in frame, no candles lit, no decoration, no crucifix "
        "large in shot, no people. The scale is institutional and the mood is waiting rather "
        "than worship.")},
    {"name": "EP13_H18_LOCKED_DOOR.png", "register": REGISTER_A, "prompt": (
        "A heavy old wooden door, closed, seen straight on and filling most of the frame, "
        "with a plain iron lock plate and a keyhole at its centre. Worn paint, deep grain, "
        "one long scratch. No handle turning, no key, no hand, no sign, no lettering, no "
        "number. Cool light from the left. The frame reads as something kept shut.")},
    {"name": "EP13_H19_PAPERS_ON_DESK_NIGHT.png", "register": REGISTER_A, "prompt": (
        "A desk at night lit only by a single lamp, with loose sheets of paper spread across "
        "it and a chair pushed back. The writing on every sheet is illegible grey texture "
        "with no formed letters. The room beyond the lamp falls away into soft darkness that "
        "still holds detail. No person, no clock, no religious object, no readable text.")},
    # ---- the attack --------------------------------------------------------
    {"name": "EP13_H20_CROWD_TURNING.png", "register": REGISTER_A, "prompt": (
        "A crowd in a large open square in 1981 caught at the instant of alarm: heads and "
        "shoulders turning sharply in one direction, some arms rising, bodies twisting. Shot "
        "from within the crowd at shoulder height and from behind, so not one face is "
        "visible or identifiable. Slight motion blur on the nearest figures only. Period "
        "1981 clothing. No weapon, no violence, no blood, no vehicle, no uniform, no injured "
        "person, no identifiable architecture.")},
    {"name": "EP13_H21_EMPTY_SQUARE_AFTER.png", "register": REGISTER_A, "prompt": (
        "A large paved public square, empty, photographed low and close to the stones in the "
        "late afternoon. A few small ordinary objects lie abandoned on the paving: a dropped "
        "hat, a single shoe, a folded paper. Long shadows across worn granite setts. Nobody "
        "present, no barriers, no vehicles, no blood, no police, no identifiable building in "
        "frame.")},
    {"name": "EP13_H22_SURGICAL_LIGHT.png", "register": REGISTER_A, "prompt": (
        "An operating theatre lamp of the early 1980s seen from directly beneath, switched "
        "on, its cluster of round reflectors filling the upper frame against a plain pale "
        "ceiling. Cool clinical light. No patient, no table, no staff, no instruments, no "
        "blood, no body part in frame. Period-correct equipment, worn enamel and chrome.")},
    # ---- the hospital and the reading --------------------------------------
    {"name": "EP13_H23_WINDOW_AFTERNOON.png", "register": REGISTER_A, "prompt": (
        "A plain hospital window seen from inside a quiet room in 1981, late afternoon light "
        "coming through it and falling in a hard rectangle onto a bare wall. Simple metal "
        "frame, a thin curtain half drawn, an ordinary view of trees and sky beyond, out of "
        "focus. No person, no bed in frame, no equipment, no lettering.")},
    {"name": "EP13_H24_HAND_ON_ENVELOPE.png", "register": REGISTER_A, "prompt": (
        "One hand resting flat and still on top of a closed envelope on a bedside table, "
        "not yet opening it. Framed close, from the side, so only the hand, the sleeve cuff "
        "and the envelope are visible: no face, no bed, no room. The envelope is blank with "
        "no address, no stamp and no writing. Warm low afternoon light from one side, a soft "
        "shadow under the hand. Stillness before a decision.")},
    # ---- the three readings ------------------------------------------------
    {"name": "EP13_H25_PRESS_MICROPHONES.png", "register": REGISTER_A, "prompt": (
        "A cluster of old broadcast microphones on a plain lectern, photographed close and "
        "slightly from below, nobody standing behind them. The microphones are mismatched, "
        "metal, of the late twentieth century, with cables falling away. All station badges "
        "and lettering are turned away, blurred or absent so nothing is readable. Neutral "
        "daylight, plain background. No person, no crowd, no logo, no text.")},
    {"name": "EP13_H26_INTERVIEW_CHAIRS.png", "register": REGISTER_A, "prompt": (
        "Two simple wooden chairs facing each other in an otherwise bare room, close "
        "together, both empty. Plain wall, plain floor, one window off frame casting soft "
        "light between them. Nothing else at all: no table, no recorder, no papers, no "
        "person, no religious object. The frame reads as a conversation that has happened or "
        "is about to.")},
    {"name": "EP13_H27_ARCHIVE_LEDGER.png", "register": REGISTER_A, "prompt": (
        "A large open institutional ledger on a desk, photographed from above at a slight "
        "angle, its ruled columns filled with illegible handwritten entries that form no "
        "readable letter or word in any language. A ribbon marker lies across the gutter. "
        "Warm lamp light from the right. No person, no pen, no date visible, no printed "
        "heading.")},
    # ---- crown payoff and devotion -----------------------------------------
    {"name": "EP13_H28_GOLD_UNDER_GLASS.png", "register": REGISTER_A, "prompt": (
        "An ornate gold object resting on dark velvet inside a museum vitrine, seen through "
        "the glass at a slight angle so one soft reflection crosses the frame. The object is "
        "cropped so its overall shape is never legible and it cannot be identified as any "
        "particular thing: only gold surface, tiny set stones and velvet. Warm museum "
        "spotlight, deep shadow beyond the case. No label, no card, no lettering, no "
        "visitor, no reflection of a person.")},
    {"name": "EP13_H29_CANDLE_WALL.png", "register": REGISTER_A, "prompt": (
        "A long open-air rack of burning devotional candles at night, photographed close "
        "along its length so the flames recede into darkness. Wax has run and pooled. Warm "
        "flame light is the only source. No people, no faces, no hands, no building, no "
        "statue, no religious figure in frame, no text.")},
    {"name": "EP13_H30_FIELD_1917.png", "register": REGISTER_A, "prompt": (
        "A bare stony upland pasture in Portugal on an overcast day in the early twentieth "
        "century, photographed wide and low. Thin grass, scattered rocks, a few sheep far "
        "off, a dry-stone wall running away to the left. Nobody present. Plain, poor, "
        "unremarkable country. No village, no church, no tree of significance, no shrine, no "
        "modern object of any kind.")},
    # ---- the form and the handoff to EP14 ----------------------------------
    {"name": "EP13_H31_PARCHMENT_COLUMNS.png", "register": REGISTER_A, "prompt": (
        "A very wide sheet of aged parchment photographed at a steep raking angle from one "
        "side, so it recedes sharply and the surface catches the light. It carries many "
        "columns of ink marks left by many different hands. CRITICAL: these marks are pure "
        "abstract pen gesture, loops, dashes, flourishes and trailing strokes, with NO "
        "letterforms whatsoever: no a, no e, no ascenders, no descenders, nothing that could "
        "be mistaken for a letter, a name or a word in any language or script. They must "
        "read as the trace of writing rather than as writing. Very shallow depth of field so "
        "only a narrow band is sharp. Cool raking light, strong parchment grain.")},
    {"name": "EP13_H32_SEALS_ON_CORD.png", "register": REGISTER_A, "prompt": (
        "A close view along a row of many wax seals hanging on short cords from the bottom "
        "edge of a parchment, each seal closed inside a small tin case, receding into "
        "shallow focus so the row seems to continue past the frame. The cases are dull "
        "metal, dented and tarnished. No device, crest, letter or symbol is legible on any "
        "seal. Cool raking light, dark neutral background. Nothing else in frame.")},
    {"name": "EP13_H33_CRATES_MOUNTAIN_ROAD.png", "register": REGISTER_A, "prompt": (
        "A line of heavy wooden crates roped onto horse-drawn carts on a narrow stone "
        "mountain road in the early nineteenth century, seen from behind and slightly above "
        "as the convoy moves away into mist. Bare rock and snow patches on the slopes. The "
        "crates are plain, unmarked, with no lettering, no stencil and no crest. Cold "
        "overcast light. No faces visible, no soldiers in frame, no flags.")},
    {"name": "EP13_H34_WASTE_PAPER_WEIGHED.png", "register": REGISTER_A, "prompt": (
        "Bundles of old documents tied with coarse string, stacked on the pan of a large "
        "cast-iron balance scale in a bare storeroom. The paper is creased and dirty at the "
        "edges and all writing on it is illegible grey texture with no formed letters. The "
        "scale's beam and weights are visible. Cold light from a high window. No person, no "
        "face, no number readable on the weights, no signage.")},
    # ---- vision register: connective and the three readings ----------------
    {"name": "EP13_V10_MARTYRS_LINE.png", "register": REGISTER_B, "prompt": (
        "An immensely long line of very small figures walking away from the camera across "
        "empty pale ground, stretching from the foreground into white distance until the "
        "line dissolves. The figures are tiny silhouettes at true scale, indistinct, no "
        "faces, no readable clothing, no banners, no order or uniform. Bone-white and grey "
        "with one faint warm accent far off to one side. No horizon, no architecture.")},
    {"name": "EP13_V11_THREE_EMBERS.png", "register": REGISTER_B, "prompt": (
        "Three small warm embers suspended at different depths in vast pale bone-white "
        "emptiness, well separated from one another, each with its own soft falloff into "
        "the white. Nothing else at all in the frame: no figure, no ground, no horizon, no "
        "architecture, no smoke. The embers are the only colour. Enormous quiet space "
        "between and around them.")},
    {"name": "EP13_V12_SWORD_ALONE.png", "register": REGISTER_B, "prompt": (
        "A straight sword suspended alone in vast pale bone-white emptiness, angled across "
        "the frame, with fire running along the blade and thin filaments of flame reaching "
        "outward into the white. No figure holds it, no hand, no arm. No ground, no horizon, "
        "no architecture. The burning blade is the only colour in the image.")},
    {"name": "EP13_V13_PAGE_DISSOLVING.png", "register": REGISTER_B, "prompt": (
        "A single sheet of pale paper suspended in bone-white emptiness, its edges losing "
        "definition and dissolving into the surrounding white so that it is impossible to "
        "say where the page stops. Any marking on it is the faintest grey texture with no "
        "formed letter. One faint warm accent behind it. No hand, no table, no ground, no "
        "horizon, no shadow cast on anything.")},
    {"name": "EP13_V14_DOORWAY_LIGHT.png", "register": REGISTER_B, "prompt": (
        "A tall narrow opening standing alone in vast pale bone-white emptiness, with even "
        "brighter light coming through it, so it reads as a threshold with nothing built "
        "around it. No wall, no frame, no hinges, no door leaf, no architecture attached. No "
        "figure, no ground, no horizon. One faint warm accent beyond the opening.")},
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--outdir", default=str(OUT))
    args = ap.parse_args()
    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    picks = [j for j in JOBS if not args.only or any(f.strip() in j["name"] for f in args.only.split(","))]
    print(str(len(picks)) + " job(s) -> " + str(outdir), flush=True)
    for job in picks:
        try:
            run(job, outdir)
        except Exception as exc:
            print("FAIL " + job["name"] + ": " + str(exc)[:200], flush=True)


if __name__ == "__main__":
    main()
