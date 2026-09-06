#!/usr/bin/env python3
"""Vertical clips for the two EP13 teasers.

Four clips, two per teaser, generated at 9:16 rather than cropped from the
episode's wide ones. Each starts from one of the vertical stills so the clip and
the frames around it belong to the same photograph.

Round 3's rule from the episode still applies: one short camera sentence, then a
three-beat physical action written with verbs, and every prohibition in
negativePrompt where it cannot crowd out the action.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_ep13_veo as base  # noqa: E402

JOBS = [
    {
        "output": "SHORT_CLIP01_CROWN_PUSH.mp4",
        "start": ("ep13_short_vertical", "SH01_CROWN_TALL.png"),
        "person": "dont_allow",
        "prompt": (
            "Static locked camera on a jewelled crown standing on dark cloth. Nothing moves "
            "except the light. Over six seconds a single warm light source travels slowly "
            "from the left side of the crown around toward the front, so highlights wake up "
            "one after another across the pearls and the worked gold, the shadows behind the "
            "arches swing round with it, and the small dull grey object among the arches "
            "stays dark while everything around it brightens. The crown itself never moves, "
            "rotates or shifts position."
        ),
    },
    {
        "output": "SHORT_CLIP02_ENVELOPE_LIFTED.mp4",
        "start": ("ep13_short_vertical", "SH05_ENVELOPE_UPRIGHT.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera. A sealed envelope leans against a dark stone wall. Over "
            "six seconds one hand completes a single action in three stages. First the hand "
            "enters from the bottom of the frame and closes on the lower edge of the "
            "envelope. Then it lifts the envelope clear of the wall and holds it upright and "
            "still, so the wax seal catches the light. Finally the hand turns it a few "
            "degrees toward the camera and stops. The wall behind never moves."
        ),
    },
    {
        "output": "SHORT_CLIP03_DOOR_CLOSING.mp4",
        "start": ("ep13_short_vertical", "SB01_SAFE_DOOR_TALL.png"),
        "person": "allow_adult",
        "prompt": (
            "Static locked camera on a heavy steel archive door standing slightly ajar in a "
            "stone doorway. Over six seconds the door completes one movement in three "
            "stages. First it begins to swing shut, slowly, with weight. Then the gap of warm "
            "light from inside narrows to a thin line as the door comes across it. Finally "
            "the door meets the frame and stops dead, and the light is gone. The camera and "
            "the stone doorway never move."
        ),
    },
    {
        "output": "SHORT_CLIP04_DUST_IN_SHAFT.mp4",
        "start": ("ep13_short_vertical", "SB08_ENVELOPE_IN_DARK.png"),
        "person": "dont_allow",
        "prompt": (
            "Static locked camera looking straight down at a sealed envelope lying in a "
            "shallow open box on a dark table, with one narrow shaft of light across it. "
            "Nothing in the scene moves except the air. Over six seconds dust drifts slowly "
            "through the shaft of light, turning and catching the beam, and the edge of the "
            "shaft creeps a few millimetres across the envelope as the light outside shifts. "
            "The envelope, the box and the table never move at all."
        ),
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    picks = [j for j in JOBS if not a.only or a.only in j["output"]]
    base.JOBS = picks
    base.ASPECT = "9:16"
    # the short stills live beside the episode ones, not inside them
    base.SRC = pathlib.Path(base.SRC).parent
    base.main()


if __name__ == "__main__":
    main()
