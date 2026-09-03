#!/usr/bin/env python3
"""EP13 card substrates.

The cards are not drawn primitives. Each one begins as a photographed material
surface in Register A, generated blank and with deliberate empty space, and the
typography is composited onto it afterwards at full resolution. That keeps the
cards inside the episode's own material world instead of importing a template.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import REGISTER_A, REGISTER_B, run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "cards"

JOBS = [
    {
        "name": "EP13_SUB01_PAPER_ON_WOOD.png",
        "register": REGISTER_A,
        "prompt": (
            "One completely blank sheet of aged writing paper lying flat and slightly askew "
            "on a dark worn wooden table, photographed from directly above. The sheet is "
            "entirely empty: no writing, no lines, no marks, no watermark, no printing of any "
            "kind. It occupies the left two thirds of the frame, leaving bare wood at the "
            "right. Warm low practical light from the upper left gives the paper visible "
            "fibre, a soft fold shadow and gentle age toning at the edges. Nothing else in "
            "frame at all."
        ),
    },
    {
        "name": "EP13_SUB02_PAPER_FULL.png",
        "register": REGISTER_A,
        "prompt": (
            "A single sheet of aged writing paper filling the entire frame edge to edge, "
            "photographed flat from directly above, completely blank with no writing, no "
            "ruled lines, no printing and no marks. Even soft light across the whole surface "
            "with no hotspot and no strong shadow. Visible paper fibre, faint mottling, one "
            "soft horizontal crease across the lower third, slight warm age toning toward "
            "the corners. Nothing else in frame."
        ),
    },
    {
        "name": "EP13_SUB03_DARK_WOOD.png",
        "register": REGISTER_A,
        "prompt": (
            "A dark worn wooden table surface filling the entire frame, photographed from "
            "directly above, completely empty. Deep grain, old scratches, a few small nicks "
            "and a faint ring stain toward one corner. Warm raking light from the left so the "
            "grain catches and the right side falls into soft shadow while staying readable. "
            "No object of any kind, no paper, no tool, no text."
        ),
    },
    {
        "name": "EP13_SUB04_PALE_FIELD.png",
        "register": REGISTER_B,
        "prompt": (
            "An empty pale bone-white field filling the entire frame, with the faintest "
            "possible tonal drift from slightly cooler at the top to slightly warmer at the "
            "bottom. Absolutely nothing in it: no figure, no ember, no architecture, no "
            "ground, no horizon, no smoke, no object. Perfectly even and calm, evenly lit to "
            "every frame edge, no vignette. The surface has an extremely subtle organic "
            "irregularity so it never reads as a flat digital colour fill."
        ),
    },
    {
        "name": "EP13_SUB05_ENVELOPE_BLANK.png",
        "register": REGISTER_A,
        "prompt": (
            "One closed blank envelope of aged paper lying flat on dark wood, photographed "
            "from directly above and positioned low in the lower left of the frame, leaving "
            "the whole upper right area as empty dark wood. The envelope carries no address, "
            "no stamp, no seal and no writing of any kind. Warm low practical light from the "
            "left. Nothing else in frame."
        ),
    },
    {
        "name": "EP13_SUB06_PAPER_LAID.png",
        "register": REGISTER_A,
        "prompt": (
            "A sheet of laid writing paper filling the entire frame edge to edge, "
            "photographed flat from directly above, completely blank with no writing, no "
            "ruled lines and no marks. It is cooler and greyer than cream, with a visible "
            "laid chain-line texture running vertically and a slightly rough deckle edge "
            "just entering the frame at the top. Even diffuse light from the right, no "
            "hotspot. Faint foxing spots in two places. Nothing else in frame."
        ),
    },
    {
        "name": "EP13_SUB07_PAPER_WARM.png",
        "register": REGISTER_A,
        "prompt": (
            "A heavier sheet of warm ivory paper filling the entire frame edge to edge, "
            "photographed flat from directly above, completely blank with no writing, no "
            "ruled lines and no marks. Slightly darker and warmer than the other sheets, "
            "with a soft vertical crease left of centre and gentle browning along the bottom "
            "edge. Raking light from the upper left so the crease casts a faint shadow. "
            "Nothing else in frame."
        ),
    },
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
