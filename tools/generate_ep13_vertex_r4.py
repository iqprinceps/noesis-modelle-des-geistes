#!/usr/bin/env python3
"""EP13 round 4: the three abstract stretches the assignment ran dry on.

Assigning states to the 115 beats exposed exactly where the set was thin, and it
was not the narrative sections. It was the waiting (beats 22 to 35), the three
readings (73 to 85) and the closing statement of form (96 to 105), where the
script argues rather than recounts and there is no object to photograph.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import REGISTER_A, REGISTER_B, run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r4"

JOBS = [
    # ---- the waiting, beats 22 to 35 ---------------------------------------
    {"name": "EP13_H35_SAFE_DOOR.png", "register": REGISTER_A, "prompt": (
        "The closed door of an old institutional strongroom, heavy painted steel with a "
        "brass dial and a long lever handle, photographed straight on and filling the frame. "
        "Chipped paint, worn metal, a faint scuff arc where the handle swings. No lettering, "
        "no maker's plate, no numbers on the dial, no hand, no person. Cool even light.")},
    {"name": "EP13_H36_KEY_RING.png", "register": REGISTER_A, "prompt": (
        "A heavy iron ring of old keys hanging from a nail on a plain plaster wall, "
        "photographed close from slightly below. The keys are of different ages, dark and "
        "worn smooth at the bows. One casts a long shadow. No tag, no label, no lettering, "
        "no hand, no door in frame. Warm low light from one side.")},
    {"name": "EP13_H37_CORRIDOR_DOORS.png", "register": REGISTER_A, "prompt": (
        "A long institutional corridor of closed identical wooden doors receding into "
        "shallow focus, photographed down its length in cold daylight. Stone or terrazzo "
        "floor, plain walls, no signage, no numbers, no nameplates, no people. Early to "
        "middle twentieth century. Every door is shut.")},
    {"name": "EP13_H38_EMPTY_CHAIR_LAMP.png", "register": REGISTER_A, "prompt": (
        "A single empty upright chair beside a small side table with a switched-on lamp, in "
        "an otherwise bare room at night. The lamp throws a warm pool onto the floor and the "
        "rest of the room falls away into readable darkness. Nothing on the table. No "
        "person, no book, no papers, no religious object, no clock.")},
    {"name": "EP13_H39_CALENDAR_PAGES.png", "register": REGISTER_A, "prompt": (
        "A thick block of tear-off calendar pages on a desk, most of the block still "
        "unturned, photographed close from the side so the stacked edges fill the frame and "
        "the top sheet curls slightly. Every printed date and word is out of focus, turned "
        "away or too small to resolve, so nothing is readable. Warm side light. No hand, no "
        "pen, no wall, no other object.")},
    {"name": "EP13_H40_DUST_IN_LIGHT.png", "register": REGISTER_A, "prompt": (
        "A shaft of daylight cutting diagonally across a dim interior, with fine dust "
        "drifting through it. The room around it is barely described: a suggestion of wall "
        "and floor, nothing identifiable. No furniture, no person, no window frame visible, "
        "no object. Time passing, and nothing happening.")},
    # ---- the three readings, beats 73 to 85 --------------------------------
    {"name": "EP13_H41_THREE_CHAIRS_ANGLES.png", "register": REGISTER_A, "prompt": (
        "Three plain wooden chairs standing apart from one another in a large bare room, "
        "each turned to face a different direction, all empty. Even daylight, plain floor, "
        "plain walls, deep space around them. Nothing else in frame: no table, no papers, no "
        "person, no decoration.")},
    {"name": "EP13_H42_PRINTED_COLUMN.png", "register": REGISTER_A, "prompt": (
        "A close view of a printed book page held open under warm light, shot at a shallow "
        "angle so only a narrow band across the middle is sharp and the rest falls away. The "
        "printed lines are grey texture with no formed letters and no readable word in any "
        "language. Fine paper grain, a soft gutter shadow. No hand, no cover, no page "
        "number, no heading.")},
    {"name": "EP13_H43_PHOTOGRAPHERS_BACKS.png", "register": REGISTER_A, "prompt": (
        "A row of press photographers seen entirely from behind, standing shoulder to "
        "shoulder with cameras raised, in the late twentieth century. No face is visible. "
        "The subject they are pointing at is out of frame and never shown. Neutral outdoor "
        "daylight, plain background. No logo, no press badge, no lettering, no flash, no "
        "crowd beyond them.")},
    {"name": "EP13_H44_MIRROR_ROOM.png", "register": REGISTER_A, "prompt": (
        "An old plain mirror on the wall of a bare room, reflecting only the empty opposite "
        "wall and a doorway, with nobody in the reflection. The mirror glass is slightly "
        "clouded at the edges and the frame is simple dark wood. Cool daylight. No person "
        "anywhere in frame or reflection, no furniture, no object, no religious image.")},
    # ---- the statement of form, beats 96 to 105 ---------------------------
    {"name": "EP13_H45_OBJECT_LINE.png", "register": REGISTER_A, "prompt": (
        "Four ordinary objects laid out in a row on a plain dark surface, evenly spaced, "
        "photographed from directly above in cool even light: a folded sheet of paper, a "
        "small closed box, a rolled document tied with cord, and a plain bound volume. All "
        "are blank and unmarked, with no writing, no label, no title and no crest anywhere. "
        "Generous empty surface between and around them. Nothing else in frame.")},
    {"name": "EP13_H46_SHELF_OF_BOXES.png", "register": REGISTER_A, "prompt": (
        "A single long shelf carrying a row of identical plain document boxes, photographed "
        "straight on so the row fills the frame horizontally. The boxes are worn card and "
        "cloth, all closed, with no label, no lettering, no number and no crest on any of "
        "them. Even cool light, faint dust. Nothing else in frame.")},
    {"name": "EP13_H47_HANDS_HANDING_OVER.png", "register": REGISTER_A, "prompt": (
        "Two pairs of hands at the moment one passes a closed envelope to the other across a "
        "plain table, the envelope held by both at once. Framed close from the side so no "
        "face, no head and no upper body are visible, only forearms in plain dark sleeves. "
        "The envelope is blank. Warm practical light from one side. Nothing else in frame.")},
    # ---- vision register: connective for the argument sections ------------
    {"name": "EP13_V15_TWO_FIGURES_APART.png", "register": REGISTER_B, "prompt": (
        "Two very small figures standing far apart from one another in vast pale bone-white "
        "emptiness, both seen from behind, both facing the same distant point. Neither has a "
        "readable face or any detail. The space between them is the subject. One faint warm "
        "accent far beyond them both. The emptiness around them is smooth and even with no "
        "cloud, no mist bank, no vapour, no ground plane and no horizon line anywhere: the "
        "figures are simply in white space. The image fills the entire 16:9 frame edge to "
        "edge with NO black bars at top or bottom and no letterboxing.")},
    {"name": "EP13_V16_SAME_SHAPE_THREE.png", "register": REGISTER_B, "prompt": (
        "One identical pale shape repeated three times across an empty bone-white field, "
        "each repetition lit slightly differently so it reads as the same form seen under "
        "three different lights. The shape is simple and unidentifiable, not a figure, not a "
        "letter, not an object anyone could name. One faint warm accent beside the middle "
        "one. No ground, no horizon.")},
    {"name": "EP13_V17_LIGHT_THROUGH_PAPER.png", "register": REGISTER_B, "prompt": (
        "Strong light coming from behind a single sheet of pale paper so the sheet glows and "
        "its fibre structure shows through, filling most of the frame. No writing at all on "
        "the sheet, not even texture that could read as text. One faint warm accent behind "
        "it. No hand, no edge of a room, no ground, no horizon.")},
    {"name": "EP13_V18_EMBER_GOING_OUT.png", "register": REGISTER_B, "prompt": (
        "A single warm ember in vast pale bone-white emptiness, very small and almost spent, "
        "reduced nearly to a point with only the faintest halo left around it. Nothing else "
        "in the frame at all. Enormous quiet space. The image reads as the last moment "
        "before something stops.")},
    {"name": "EP13_V19_OPEN_FIELD_WAITING.png", "register": REGISTER_B, "prompt": (
        "Completely empty pale bone-white space with the faintest suggestion of depth, and "
        "nothing in it whatsoever: no figure, no ember, no object, no architecture, no "
        "horizon, no ground plane. Only a very subtle tonal drift across the frame and an "
        "organic irregularity in the surface so it never reads as a flat digital fill.")},
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
