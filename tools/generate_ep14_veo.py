#!/usr/bin/env python3
"""EP14 clips: seven moments where something is done to a document.

Every clip in this episode is an act performed on paper or on a crate, because
that is what the episode is about. Nothing is a camera move dressed up as motion.

Round 3's rule from EP13 holds: one short camera sentence, then a three-beat
physical action written with verbs, and every prohibition in negativePrompt where
it cannot crowd the action out. Each clip starts from the still it belongs beside,
so the clip and its neighbours are the same photograph.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_ep13_veo as base  # noqa: E402

JOBS = [
    {
        "output": "EP14_CLIP01_SEAL_PRESSED.mp4",
        "start": ("ep14", "D03_SKIPPET_OPEN_MACRO.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked macro camera on a small round tin case lying open on a dark surface, "
            "a pool of soft red wax inside it. Over six seconds one hand completes a single "
            "action in three stages. First the hand brings a round metal seal straight down, "
            "flat face first and parallel to the wax, and presses it in, so the wax spreads and "
            "squeezes up around the rim. Then the hand holds it pressed and completely still "
            "while the surface of the wax loses its shine. Finally the hand lifts the seal "
            "straight up and out of the top of the frame, leaving a flat impression. The tin "
            "case never moves or slides."
        ),
    },
    {
        "output": "EP14_CLIP02_CORD_THREADED.mp4",
        "start": ("ep14", "D06_CORD_THROUGH_FOLD.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera close on the folded edge of a thick parchment lying on dark "
            "cloth. Over six seconds two hands thread a red silk cord through it in three "
            "stages. First the fingers push the stiffened end of the cord into a punched hole "
            "in the fold. Then the other hand takes it on the far side and draws the cord "
            "steadily through, so a long length of red silk travels across the frame. Finally "
            "both hands pull the cord taut and stop, and the silk goes still. The parchment "
            "never shifts on the cloth."
        ),
    },
    {
        "output": "EP14_CLIP03_CRATE_CLOSED.mp4",
        "start": ("ep14", "H20_CRATES_PACKED.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera looking down into an open wooden packing crate half filled "
            "with bound volumes and straw. Over six seconds two hands close it in three stages. "
            "First the hands press a last handful of straw down over the volumes. Then they "
            "lift a rough plank lid across and lower it flat onto the crate, and the contents "
            "disappear. Finally one hand sets a nail at the corner and the other drives it down "
            "with two blows of a hammer, and everything stops. The crate never slides."
        ),
    },
    {
        "output": "EP14_CLIP04_CART_PASSES.mp4",
        "start": ("ep14", "H21_CONVOY_ROAD.png"),
        # dont_allow tripped the people filter on a start frame that already has a
        # carter walking beside the horse; the clip needs him to stay there.
        "person": "allow_adult",
        "prompt": (
            "Static locked camera at the roadside on a grey day, framing an empty stretch of "
            "muddy rutted road with bare fields behind. Over six seconds a heavy horse-drawn "
            "cart loaded with roped wooden crates enters from the left, crosses the frame at "
            "walking pace with the wheels turning in the ruts and the load rocking, and exits "
            "to the right, leaving the empty road and fresh tracks. The camera never moves and "
            "never follows the cart."
        ),
    },
    {
        "output": "EP14_CLIP05_PAGE_TURNED.mp4",
        "start": ("ep14", "H14_HANDS_ON_REGISTER.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera looking down at a large open register on a padded cradle. "
            "Over six seconds two gloved hands turn one page in three stages. First the "
            "fingertips lift the outer corner of the right-hand page clear of the block. Then "
            "the hand carries the page up and over in a slow arc, the sheet bowing under its "
            "own weight as it crosses. Finally the page settles flat on the left side and both "
            "hands smooth it down and stop. The book and the cradle never move."
        ),
    },
    {
        "output": "EP14_CLIP06_SCALE_TIPS.mp4",
        "start": ("ep14", "L03_SCALES_PAPER.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera on a large iron balance scale standing level and empty on a "
            "stone floor. Over six seconds the balance is loaded in three stages. First a pair "
            "of hands lowers a thick stack of written parchment sheets into the left pan, which "
            "sinks. Then the hands place iron weights one after another into the right pan, and "
            "the beam swings back through level and past it. Finally the hands withdraw and the "
            "beam rocks twice and settles, still. The scale itself never slides on the floor."
        ),
    },
    {
        "output": "EP14_CLIP07_WRAPPING.mp4",
        "start": ("ep14", "L04_GROCER_WRAPPING.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera on a shop counter in dim warm light, a sheet of old written "
            "parchment lying flat on it. Over six seconds a pair of hands wraps a parcel in "
            "three stages. First the hands set a small heavy item down in the middle of the "
            "sheet. Then they fold the parchment up over it from one side and then the other, "
            "creasing each fold flat with a thumb, and the writing disappears inside. Finally "
            "they tie a length of string round the parcel, pull the knot, and stop. The counter "
            "never moves."
        ),
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    picks = [j for j in JOBS if not a.only or a.only in j["output"]]
    base.JOBS = picks
    # EP14's stills live in tmp/imagegen/ep14, a sibling of the EP13 raw folders
    base.SRC = pathlib.Path(base.SRC).parent
    base.OUT = pathlib.Path(base.OUT).parent / "ep14_veo"
    base.main()


if __name__ == "__main__":
    main()
