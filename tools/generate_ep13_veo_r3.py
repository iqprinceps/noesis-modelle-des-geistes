#!/usr/bin/env python3
"""EP13 clip round 3: action first.

Round 2 over-corrected. Long camera-lock sentences and inline prohibition lists
suppressed the action along with the camera, producing one clip that was a
brightness change on a static frame and one that jiggled for four seconds and
then jump-cut. The prohibitions belong in negativePrompt, not in the prompt.

Rule for this round: one short camera sentence, then a three-beat physical
action written with verbs. Every clip must have something that visibly starts,
happens and finishes.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_ep13_veo as base  # noqa: E402

JOBS = [
    {
        "output": "EP13_CLIP04_SEALING.mp4",
        "start": ("r2", "EP13_H07_SEALING_WAX.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera. A hand seals a letter, in three clear stages over six "
            "seconds. First the hand pushes the metal seal firmly straight down into the "
            "soft red wax, and the wax spreads and squeezes out slightly around the rim as "
            "it takes the pressure. Then the hand stops and holds the seal pressed down, "
            "completely motionless, while the wax cools and its surface loses its wet shine. "
            "Finally the hand lifts the seal straight up and away, slowly, with a faint pull "
            "as the metal separates from the setting wax, and carries it up out of the top "
            "of the frame, leaving the sealed envelope alone in the shot. The envelope stays "
            "exactly where it is on the table the whole time and never shifts, slides or "
            "changes position or angle."
        ),
    },
    {
        "output": "EP13_CLIP08_SETTING_THE_METAL.mp4",
        "start": ("r2b", "EP13_H15_SETTING_THE_METAL.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked macro camera on a bench. The gold object is clamped tight in a "
            "vice and physically cannot move, rotate, tilt or shift: it is bolted in place "
            "and every highlight on it stays exactly where it is for all six seconds. The "
            "ONLY thing that moves in the entire frame is the pair of steel tweezers and the "
            "small dull grey lump they hold. Over six seconds the tweezers descend the last "
            "short distance, press the grey lump down into the shallow recess in the gold, "
            "release it there, and withdraw straight up out of the top of the frame, leaving "
            "the dull grey metal seated in the bright gold. Nothing else in the image changes "
            "at all."
        ),
    },
    {
        "output": "EP13_CLIP09_PUTTING_IT_AWAY.mp4",
        "start": ("r2", "EP13_H10_BOX_RETURNED.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera looking down at a table. Two hands put a document away, in "
            "three clear stages over six seconds. First the hands lower the closed envelope "
            "the last short distance into the cloth-lined wooden box and let it settle flat "
            "on the bottom. Then the fingers press it down once at the corner, flattening it, "
            "and withdraw. Finally one hand reaches across, takes the wooden lid lying "
            "beside the box, swings it over and lowers it onto the box, closing it, and the "
            "hands lift away out of frame. The box itself never moves on the table."
        ),
    },
    {
        "output": "EP13_CLIP10_THE_WAY.mp4",
        "start": ("v2", "EP13_V04_THE_WAY.png"),
        "person": "dont_allow",
        "prompt": (
            "Static locked camera. Wind moves along an empty pale road over six seconds. The "
            "loose edges and folds of the pale cloths covering the low shapes at the roadside "
            "lift, ripple and settle again in an uneven gust, nearest ones first and then the "
            "ones further away, so the movement travels down the road away from the camera. "
            "Fine pale dust lifts off the road surface and drifts low across it in the same "
            "direction. The covered shapes underneath never move, never change outline and "
            "are never uncovered. The road, the light and the distance stay exactly as they "
            "are."
        ),
    },
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    base.JOBS = [j for j in JOBS if not args.only or args.only in j["output"]]
    sys.argv = [sys.argv[0]]
    base.main()


if __name__ == "__main__":
    main()
