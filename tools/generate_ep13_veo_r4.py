#!/usr/bin/env python3
"""EP13 clip round 4: the two clips that were rejected on viewing.

CLIP09_PUTTING_IT_AWAY. Two faults. The box was modelled with a lid that opens
from both sides at once, which no box does, and the shot ran 7.2 s against a 6 s
clip, so the renderer looped it and the action visibly started over. The loop is
fixed in the renderer; this replaces the box.

CLIP04_SEALING. The seal came down on its edge like a coin being stood up. A seal
matrix is pressed face down, flat and parallel to the paper. This is the third
attempt at the shot, so the geometry is stated first and in plain terms, before
anything about mood.

Round 3's rule still applies: one short camera sentence, then a three-beat action
written with verbs, and every prohibition in negativePrompt rather than in the
prompt, where it crowds out the action.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_ep13_veo as base  # noqa: E402

JOBS = [
    {
        "output": "EP13_CLIP09_PUTTING_IT_AWAY.mp4",
        "start": ("r10", "EP13_H48_PAGE_BECOMES_OBJECT.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera looking down at a worn wooden table. A shallow rectangular "
            "document box sits open on it with ONE lid, hinged along its far edge only, standing "
            "up and back. Two hands complete one action in three stages over six seconds. First "
            "the hands lift the written sheet, fold it once, and lay it flat inside the box. "
            "Then the hands take the single hinged lid by its front edge and swing it forward "
            "and down until it closes flush, and the paper disappears from view. Finally both "
            "hands settle flat on the closed lid and stop moving completely. The box never "
            "moves or slides on the table."
        ),
    },
    {
        "output": "EP13_CLIP04_SEALING.mp4",
        "start": ("r2", "EP13_H07_SEALING_WAX.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked macro camera. A hand holds a round brass seal by its handle with the "
            "flat engraved FACE of the disc pointing straight DOWN at the table, parallel to it, "
            "like a stamp about to be stamped. It is never tilted, never on its edge, never "
            "rolled. Over six seconds it does one thing in three stages. First the hand lowers "
            "the seal straight down and presses the flat face squarely into the pool of soft red "
            "wax, and the wax spreads and squeezes out in a ring around the rim. Then the hand "
            "holds the seal pressed down and completely still while the wax sets and its surface "
            "loses its shine. Finally the hand lifts the seal straight up and out of the top of "
            "the frame, leaving a flat round wax impression on the envelope. The envelope stays "
            "exactly where it is throughout."
        ),
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    picks = [j for j in JOBS if not a.only or a.only in j["output"]]
    base.JOBS = picks
    base.main()


if __name__ == "__main__":
    main()
