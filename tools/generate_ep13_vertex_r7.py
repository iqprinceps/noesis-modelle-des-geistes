#!/usr/bin/env python3
"""EP13 round 7: one replacement for a CC BY-SA still.

EP13-X02 sat on a museum photograph of the Fiat Campagnola under the line "John
Paul II is moving slowly through the crowd in an open car". The photograph is CC
BY-SA, and Ken Burns makes the film Adapted Material, which would drag the whole
film under ShareAlike. Commons has exactly one clean photograph of that vehicle
and the cut already uses it elsewhere.

So the beat is reconstructed instead. The vehicle carries the frame and the crowd
surrounds it, which also keeps this state distinct from the two crowd states on
either side of it. No likeness of John Paul II is synthesised: the occupants are
turned away and too far back to read.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import REGISTER_A  # noqa: E402
from generate_ep13_vertex_r6 import run_with_refs  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r7"

JOBS = [
    {"name": "EP13_P15_OPEN_CAR_IN_CROWD.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "A small white open-topped four-wheel-drive parade vehicle moving at walking pace "
         "through a dense crowd in a large paved European square on a bright spring afternoon "
         "in 1981. The vehicle fills the middle of the frame, seen from within the crowd at "
         "head height from behind and slightly to one side. Two occupants stand in the back "
         "of it, both turned away from the camera and far enough back that no face is visible "
         "and no one is identifiable. Around and in front of the vehicle, ordinary people of "
         "every age press close: a dozen faces visible in the foreground and mid-ground, "
         "turned toward the vehicle, some raising a hand, some lifting a small child, some "
         "shading their eyes. Period 1981 clothing and hairstyles. Warm low afternoon "
         "daylight from the left, long soft shadows across the paving. Documentary "
         "photograph, plain and unstaged. No weapon, no violence, no alarm, no uniform, no "
         "flag or banner with an emblem, no lettering, no logo, no religious dress, no "
         "identifiable building, no famous face.")},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(OUT))
    a = ap.parse_args()
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"{len(JOBS)} job(s) -> {outdir}", flush=True)
    for job in JOBS:
        try:
            run_with_refs(job, outdir)
        except Exception as exc:
            print("FAIL " + job["name"] + ": " + str(exc)[:300], flush=True)


if __name__ == "__main__":
    main()
