#!/usr/bin/env python3
"""EP13 clip round 2.

Lesson from round 1: Veo adds a camera move on wide establishing shots however
firmly the prompt forbids it, but holds a locked frame on close work where a
single element moves. This batch is therefore weighted toward hands, objects and
one nearly abstract vision state, plus two wide shots that are worth one attempt
because the beat is temporal in the script.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_ep13_veo as base  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

JOBS = [
    {
        "output": "EP13_CLIP03_WRITING.mp4",
        "start": ("r2", "EP13_H05_WRITING_HAND_1944.png"),
        "person": "allow_adult",
        "prompt": (
            "Six seconds beginning exactly from the supplied frame. LOCKED-OFF TRIPOD MACRO: "
            "the camera is completely frozen, the table edge and the paper stay at identical "
            "pixel positions in the first and last frame. The only movement is the writing "
            "hand: the pencil advances slowly along one line, the fingers adjust their grip "
            "once, and a short new stretch of illegible grey marking appears behind the "
            "pencil tip. The marking never forms a letter or a readable word in any language. "
            "The second hand holding the paper steady does not move. No face enters the "
            "frame, no arm above the elbow, no new object, no page turn, no lighting change."
        ),
    },
    {
        "output": "EP13_CLIP04_SEALING.mp4",
        "start": ("r2", "EP13_H07_SEALING_WAX.png"),
        "person": "allow_adult",
        "prompt": (
            "Six seconds beginning exactly from the supplied frame. LOCKED-OFF TRIPOD MACRO: "
            "the camera does not move at all and the envelope stays at an identical pixel "
            "position throughout. The only movement is the hand: it presses the metal seal "
            "down firmly into the soft red wax, holds it still for a beat, then lifts it "
            "slowly and cleanly away, leaving a smooth blank impression with no device, no "
            "crest, no letters and no symbol. A faint sheen of heat leaves the wax as it "
            "sets. No face, no second hand, no new object, no smoke, no lighting change."
        ),
    },
    {
        "output": "EP13_CLIP05_EMBER.mp4",
        "start": ("r2", "EP13_V07_EMBER_ALONE.png"),
        "person": "dont_allow",
        "prompt": (
            "Six seconds beginning exactly from the supplied frame. The camera is completely "
            "static. The single warm ember suspended in the pale bone-white emptiness "
            "breathes very slowly: it brightens almost imperceptibly, then dims and contracts "
            "until it is a faint point, close to going out but never quite gone. The white "
            "field around it stays perfectly even and never darkens, never gains texture and "
            "never develops cloud. Absolutely nothing else appears: no figure, no smoke, no "
            "sparks, no architecture, no ground."
        ),
    },
    {
        "output": "EP13_CLIP06_THE_CLIMB.mp4",
        "start": ("r2", "EP13_V09_THE_CLIMB.png"),
        "person": "allow_adult",
        "prompt": (
            "Six seconds beginning exactly from the supplied frame. LOCKED-OFF TRIPOD SHOT: "
            "the camera does not move one millimetre and every rock feature stays at an "
            "identical pixel position from first frame to last. The only movement is the long "
            "thin line of very small figures, who climb slowly upward along the slope, each "
            "one advancing a short distance, the line staying unbroken and evenly spaced. No "
            "face ever becomes visible, no figure grows larger, no new figure joins. The "
            "slope, the rock texture and the pale air are completely static. No dolly, no "
            "push, no drift, no parallax, no weather, no dust storm."
        ),
    },
    {
        "output": "EP13_CLIP07_THE_FALL.mp4",
        "start": ("v3", "EP13_V06_THE_FALL.png"),
        "person": "allow_adult",
        "prompt": (
            "Six seconds beginning exactly from the supplied frame. LOCKED-OFF TRIPOD SHOT: "
            "the camera is frozen and the summit, the cross and the horizon stay at identical "
            "pixel positions throughout. The small white figure completes its backward fall "
            "slowly and comes to rest on the pale ground, and then does not move again. The "
            "group of dark silhouettes lowers its raised weapons once and then stands still. "
            "The thin pale streaks in the air fade out. No face anywhere, no impact detail, "
            "no blood, no wound, no violence detail, no new figure, no camera move, no "
            "zoom. The last two seconds are almost completely still."
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
