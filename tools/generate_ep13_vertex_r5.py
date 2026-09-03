#!/usr/bin/env python3
"""EP13 round 5: the closing statement of form and the EP14 handoff.

Building the cue sheet exposed that beats 97 to 115 had no honest coverage. The
draft assignment there leaned on five near-identical chapel photographs and on
renamed repeats of states already used earlier, which is exactly the repeat the
standard forbids. These are the episode's closing argument and its handoff, so
they get their own material.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import REGISTER_A, REGISTER_B, run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r5"

JOBS = [
    # ---- the form, beats 97 to 105 -----------------------------------------
    {"name": "EP13_H48_PAGE_BECOMES_OBJECT.png", "register": REGISTER_A, "prompt": (
        "A single folded sheet of aged paper lying beside an open empty envelope on a plain "
        "dark surface, photographed from directly above, as if the sheet is about to go in. "
        "Both are completely blank with no writing, no address and no marking of any kind. "
        "Warm even light, soft shadows beneath each, generous empty surface around them. "
        "Nothing else in frame.")},
    {"name": "EP13_H49_BOX_ON_SHELF_ALONE.png", "register": REGISTER_A, "prompt": (
        "One closed plain document box standing alone on a long empty wooden shelf, "
        "photographed straight on so the emptiness of the shelf on both sides dominates the "
        "frame. The box is worn card and cloth with no label, no lettering and no crest. "
        "Cool even light, faint dust on the shelf. Nothing else in frame.")},
    {"name": "EP13_H50_THREE_READERS_TABLE.png", "register": REGISTER_A, "prompt": (
        "A plain table seen from directly above with three identical sheets of paper laid "
        "out side by side, each turned to a slightly different angle. All three are blank "
        "with no writing of any kind. Even cool light, soft shadows under each sheet, plenty "
        "of bare table around them. No hands, no person, no pen, no envelope.")},
    {"name": "EP13_H51_FIVE_FORMS_ROW.png", "register": REGISTER_A, "prompt": (
        "Five ordinary objects laid out in a single evenly spaced row on a plain dark "
        "surface, photographed from directly above in cool even light: a closed envelope, a "
        "plain document box, a rolled document tied with cord, a bound volume, and a small "
        "closed wooden case. All are blank and unmarked, with no writing, label, title or "
        "crest anywhere. Generous empty surface between them. Nothing else in frame.")},
    {"name": "EP13_H52_ENVELOPE_ALONE_WIDE.png", "register": REGISTER_A, "prompt": (
        "One small closed envelope lying alone in the centre of a very large empty dark "
        "table, photographed from above and far enough back that the envelope is small in "
        "the frame and the bare surface surrounds it on all sides. Blank, no address, no "
        "stamp, no seal. One soft light from the side gives it a thin shadow. Nothing else "
        "in frame at all.")},
    # ---- the EP14 handoff, beats 106 to 115 --------------------------------
    {"name": "EP13_H53_WIDE_PARCHMENT_EDGE.png", "register": REGISTER_A, "prompt": (
        "The lower edge of a very wide sheet of aged parchment, photographed straight on and "
        "close, so the edge runs the full width of the frame with dark empty space beneath "
        "it. Short cords hang from the edge at regular intervals, some carrying small dull "
        "metal cases and a few positions empty. Cool raking light. No writing visible, no "
        "device or symbol on any case, nothing else in frame.")},
    {"name": "EP13_H54_SEAL_SINGLE_MACRO.png", "register": REGISTER_A, "prompt": (
        "One wax seal inside a small dented tin case, hanging on a short cord, photographed "
        "in extreme close macro against a dark neutral background with the rest of the row "
        "falling far out of focus behind it. The wax is dark and scuffed and carries no "
        "readable device, crest, letter or symbol. Cool raking light picks out the dents in "
        "the metal. Nothing else in frame.")},
    {"name": "EP13_H55_CART_WHEEL_MUD.png", "register": REGISTER_A, "prompt": (
        "A heavy wooden cart wheel stopped in deep frozen mud on a mountain track, "
        "photographed low and close so the wheel fills much of the frame and the road "
        "recedes behind it into mist. Iron tyre, worn spokes, ice in the ruts. Early "
        "nineteenth century. No person, no horse's head in frame, no crate visible, no "
        "lettering.")},
    {"name": "EP13_H56_EMPTY_SHELVES_GAPS.png", "register": REGISTER_A, "prompt": (
        "Tall archive shelving photographed straight on, where whole sections stand empty "
        "and only scattered bundles of documents remain, so the gaps read as loss rather "
        "than as storage. Worn wood, dust lines on the empty boards showing where things "
        "used to sit. Cold light from one side. No person, no label, no lettering, no ladder.")},
    {"name": "EP13_H57_SCALE_PAN_EMPTY.png", "register": REGISTER_A, "prompt": (
        "The empty pan of a large cast-iron balance scale in a bare storeroom, photographed "
        "close from slightly above, with the brass weights standing beside it and a few loose "
        "scraps of torn paper caught on the pan's rim. Cold light from a high window. No "
        "person, no bundles, no readable number on any weight, no signage.")},
    # ---- vision register: the closing loop ---------------------------------
    {"name": "EP13_V20_FIVE_EMBERS_LINE.png", "register": REGISTER_B, "prompt": (
        "Five small warm embers arranged in a slow curve across vast pale bone-white "
        "emptiness, each at a different depth so the curve recedes, each with its own soft "
        "falloff. Nothing else in the frame at all: no figure, no object, no ground, no "
        "horizon, no architecture. The embers are the only colour. Enormous quiet space.")},
    {"name": "EP13_V21_CROWN_SHAPE_DISSOLVE.png", "register": REGISTER_B, "prompt": (
        "A simple pale ring shape suspended in bone-white emptiness, its outline losing "
        "definition and dissolving into the surrounding white so it is impossible to say "
        "where it stops. One small warm ember sits caught inside the ring. Nothing else in "
        "the frame: no figure, no ground, no horizon, no ornament, no gemstone, no metal "
        "texture, nothing that identifies it as any particular object.")},
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
