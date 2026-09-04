#!/usr/bin/env python3
"""EP13 round 9: bring the rest of the vision act into the round 8 language.

Round 8 rebuilt the seven vision states that were a pale field with an ember on
it. That left the act split: seven frames with depth, texture and bodies, and ten
still in the old bone-white treatment. A register that changes halfway through is
worse than a weak register applied consistently, so the remaining ten follow.

Two of them change more than their tone.

V03 was an aerial ruined city, and the new V15 is now also a ruined city seen
from above. Two of those, forty-four seconds apart, is a repeat. The line under
V03 is "He walks through a large city, half of it in ruins. He passes bodies on
the way", which is a street at his shoulder rather than a vista. It becomes that.

V05, V06 and V08 are the mountain sequence and had nobody climbing it. The text
says he climbs with other bishops, priests and lay people, and that they are
killed with him. Those people belong in the frames.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex_r6 import run_with_refs  # noqa: E402
from generate_ep13_vertex_r8 import BISHOP, FACES, REGISTER_B2  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r9"

NO_GORE = (" No blood, no wounds, no gore, no dismemberment, no distorted or "
           "screaming faces, no weapons pointed at the camera.")


def job(name, prompt, faces=True, bishop=False):
    reg = REGISTER_B2 + ("\n\n" + FACES if faces else "") + ("\n\n" + BISHOP if bishop else "")
    return {"name": name, "register": reg, "refs": [], "prompt": prompt}


JOBS = [
    job("EP13_V03_RUINED_STREET.png", faces=False, bishop=True, prompt=(
        "Street level in a bombed-out city street, the camera a few metres behind and to one "
        "side of a man in a white robe who is walking away from us down the middle of the "
        "road. Rubble and broken masonry heaped along both sides, gutted facades rising into "
        "smoke on the left and right, the street receding into haze ahead. Along the edges of "
        "the road lie still shapes covered over with dust-grey cloth. His robe is filthy at "
        "the hem and moves as he walks. Cold light comes down between the buildings and "
        "catches the dust. One small warm ember burns in the rubble to one side." + NO_GORE)),

    job("EP13_V05_THE_CLIMB.png", faces=True, bishop=True, prompt=(
        "A steep bare mountainside of dark broken rock, seen from below and to the side. A "
        "line of perhaps fifteen people climbs it in single file, strung out across the "
        "slope: men and women in plain robes and simple dark clothing, bent into the climb, "
        "hands on the rock, real effort in their bodies. Two or three of the nearest faces "
        "are visible and lit, tired and set. Near the front of the line one figure wears a "
        "plain white robe, seen from behind. At the summit far above, a great rough timber "
        "cross stands against a sky full of moving cloud. Cold raking light, dust and thin "
        "cloud drifting across the slope, one warm ember low among the rocks.")),

    job("EP13_V06_THE_FALL.png", faces=True, bishop=True, prompt=(
        "The summit of a mountain at the foot of a great rough timber cross. In the centre of "
        "the frame an ELDERLY man with SHORT GREY CLOSE-CROPPED HAIR and NO BEARD, wearing a "
        "plain white cassock, has just been struck and is going down: his knees buckling, one "
        "hand reaching for the rock. He is seen from BEHIND AND SLIGHTLY ABOVE so that the "
        "back of his grey head is toward the camera and his face cannot be seen at all. "
        "Around and behind him eight other climbers are falling and recoiling, two of their "
        "faces visible and lit with real shock. At the edge of the frame, distant and in "
        "silhouette against the cloud, a rank of dark figures stands with raised arms. Cold "
        "hard light, dust thrown up from the rock, one warm ember on the ground near him." + NO_GORE)),

    job("EP13_V08_EMPTY_SUMMIT.png", faces=False, prompt=(
        "The same mountain summit afterwards, from a low angle a few metres away. The great "
        "rough timber cross stands alone against drifting cloud. The rock around its base is "
        "scattered with abandoned things: a fallen staff, a shoe, cloth caught between "
        "stones, a book face down with its pages moving in the wind. Nobody is there. The "
        "light has gone flat and grey and the cloud has come down over the slope below, so "
        "the mountain ends in nothing. One warm ember burns out among the stones." + NO_GORE)),

    job("EP13_V10_MARTYRS_LINE.png", faces=True, prompt=(
        "An immense column of people walking slowly away from the camera across a broad "
        "plain of dark wet ground, the line narrowing into the distance until it disappears "
        "into haze: hundreds of figures, close together, unhurried. In the near foreground "
        "three or four of them are close enough that their faces are visible in profile, "
        "ordinary people of different ages, calm rather than frightened. Their clothing spans "
        "many centuries, plain and worn. Low cloud presses down. Small warm embers are "
        "scattered along the length of the line into the distance, one for each of many.")),

    job("EP13_V12_SWORD_ALONE.png", faces=False, prompt=(
        "A straight sword held upright, filling most of the frame, burning fiercely along the "
        "whole length of the blade. Every detail of the steel is visible under the flame: "
        "hammer marks, a worn edge, heat colouring the metal. The fire throws hard warm light "
        "onto drifting smoke around it and dies away into deep darkness at the frame edges. A "
        "hand and forearm hold the grip at the very bottom of the frame, in shadow. No face, "
        "no wings, no armour, no religious iconography, no lettering.")),

    job("EP13_V13_PAGE_DISSOLVING.png", faces=False, prompt=(
        "A single sheet of old handwritten paper standing upright in mid-air in a dark stone "
        "interior, lit from behind so the fibres of the paper glow. Its lower half is intact "
        "and detailed, with visible creases and soft unreadable handwriting; its upper half is "
        "coming apart into drifting fragments and sparks that rise and scatter into the dark. "
        "Deep shadow all around, dust suspended in the backlight, one warm ember among the "
        "rising fragments. No hand, no face, no legible text.")),

    job("EP13_V14_DOORWAY_LIGHT.png", faces=False, prompt=(
        "A tall narrow doorway standing open at the end of a long dark stone corridor, seen "
        "straight on from thirty metres away. Hard light pours through the opening and lies "
        "in a long bright wedge down the corridor floor, catching every worn flagstone and "
        "the dust hanging in the air. The corridor walls are heavy stone, damp and textured, "
        "falling into blackness at the frame edges. Whatever is beyond the doorway is lost in "
        "the brightness. One small warm ember burns on the floor partway down. No person, no "
        "furniture, no lettering.")),

    job("EP13_V17_LIGHT_THROUGH_PAPER.png", faces=False, prompt=(
        "A folded sheet of old paper stands propped upright on a dark wooden table in a dim "
        "stone room, filling the middle of the frame, with a bright lamp burning directly "
        "behind it. The light drives through the paper and turns it into a glowing panel in "
        "which the fibres, the laid lines and a watermark all become visible, and the writing "
        "on the far side shows through as soft reversed marks that cannot be read. The fold "
        "runs down the sheet as a hard dark seam. Everything around it falls into deep shadow, "
        "with dust drifting through the beam. No hand, no person, no legible text.")),

    job("EP13_V21_CROWN_SHAPE_DISSOLVE.png", faces=False, prompt=(
        "The silhouette of a jewelled crown, seen almost edge on in a dark interior, its "
        "arches and finial picked out in hard rim light against blackness. The metal is real "
        "and detailed where the light strikes it, and the rest of the form dissolves into "
        "drifting smoke and dark. Inside the arches, at the point where they meet, a single "
        "small warm ember burns, brighter than anything else in the frame. Dust hangs in the "
        "light. No face, no figure, no head wearing it, no lettering.")),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--outdir", default=str(OUT))
    a = ap.parse_args()
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    picks = [j for j in JOBS if not a.only or any(f.strip() in j["name"] for f in a.only.split(","))]
    print(f"{len(picks)} job(s) -> {outdir}", flush=True)
    for j in picks:
        try:
            run_with_refs(j, outdir)
        except Exception as exc:
            print("FAIL " + j["name"] + ": " + str(exc)[:300], flush=True)


if __name__ == "__main__":
    main()
