#!/usr/bin/env python3
"""EP13 round 2: the acted beats the first pass did not cover.

Round 1 built the vision sequence and four object states. This pass covers the
human actions the script names and the still set cannot yet show: the writing,
the sealing, the carrying, the reading and resealing by popes, the square, the
setting of the projectile into the crown, plus vision connective tissue.

Same two registers and the same global lock as generate_ep13_vertex.py.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import REGISTER_A, REGISTER_B, run  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r2"

JOBS = [
    {
        "name": "EP13_H05_WRITING_HAND_1944.png",
        "register": REGISTER_A,
        "prompt": (
            "A young woman's hands writing with a plain wooden pencil on a small sheet of "
            "paper, on a bare wooden table in a spare room in the early 1940s. Framed from "
            "above and behind the hands so no face, no head and no upper body are visible. "
            "The sleeves are plain dark cloth. The writing under the pencil is illegible "
            "grey texture with no formed letters and no readable word in any language. Cool "
            "daylight from a window off frame left, one deep shadow under the wrist. Nothing "
            "else on the table but the sheet and the pencil. No religious objects, no "
            "crucifix, no habit, no veil, no decoration, no book."
        ),
    },
    {
        "name": "EP13_H06_FOLDING_SHEET.png",
        "register": REGISTER_A,
        "prompt": (
            "ONE SINGLE LOOSE SHEET of aged paper, definitely not a book and definitely not "
            "bound, lying on a dark wooden table with its lower half already folded up over "
            "its upper half. Two slim younger hands press the new crease flat with the "
            "fingertips, caught mid-gesture. Framed close from above; no face, no head, no "
            "arms above the elbow. The sheet has exactly two visible surfaces, the folded "
            "flap and the part beneath it, with a single sharp crease between them. Any "
            "visible writing is illegible grey texture with no formed letters. Plain dark "
            "sleeves. Warm practical light from one side, strong paper fibre. Nothing else "
            "in frame: no book, no spine, no pages, no second sheet, no pen, no envelope."
        ),
    },
    {
        "name": "EP13_H07_SEALING_WAX.png",
        "register": REGISTER_A,
        "prompt": (
            "A close view of one hand pressing a plain metal seal into a fresh disc of dark "
            "red wax on the closed flap of an aged envelope, on a dark wooden table. The wax "
            "is still glossy at the edge. The seal face carries no device, no crest, no "
            "letters and no symbol, and the envelope is otherwise completely blank. Framed "
            "close so only the hand, the seal, the wax and the envelope corner are visible: "
            "no face, no room. Warm low practical light, one small highlight on the wax."
        ),
    },
    {
        "name": "EP13_H08_ENVELOPE_CARRIED.png",
        "register": REGISTER_A,
        "prompt": (
            "A man's gloved hands holding a small closed envelope flat against a dark coat, "
            "as if carrying it somewhere and not letting go. Framed from the chest down so "
            "no face and no head are visible. Late 1950s clothing: dark wool overcoat, plain "
            "leather gloves. Cool overcast daylight, shallow depth of field so the background "
            "is an unreadable soft grey. The envelope is blank with no address, no stamp and "
            "no writing. No clerical collar, no religious insignia, no vehicle, no luggage."
        ),
    },
    {
        "name": "EP13_H09_READING_ALONE.png",
        "register": REGISTER_A,
        "prompt": (
            "An older man in plain dark clothing sits alone at a desk in a quiet study, seen "
            "from behind and to one side so that no face, no profile and no identity are "
            "visible. He holds one single sheet of paper up in both hands and is reading it. "
            "The room is sparse: a desk, a lamp with a warm bulb, heavy curtains, dark wood. "
            "The paper catches the lamp light and its writing is illegible grey texture. "
            "Late 1950s or early 1960s. No white cassock, no skullcap, no ring, no crucifix, "
            "no religious insignia, no portrait on the wall, no other person."
        ),
    },
    {
        "name": "EP13_H10_BOX_RETURNED.png",
        "register": REGISTER_A,
        "prompt": (
            "A pair of hands lowering one closed envelope back into a plain wooden document "
            "box lined with faded cloth, on a table in a quiet room. The lid is open beside "
            "the box. Framed from above, close, no face and no upper body visible. The box "
            "has no label, no lettering and no crest. Cool daylight with one warm practical "
            "lamp. Worn wood, dust, stillness. The gesture reads as putting something away "
            "rather than taking it out."
        ),
    },
    {
        "name": "EP13_H11_DESK_AFTER_READING.png",
        "register": REGISTER_A,
        "prompt": (
            "An empty desk in a quiet study, photographed straight on, nobody present. On it "
            "sit one closed envelope, one pair of reading glasses folded, and a lamp still "
            "switched on. The chair is pushed back and empty. Late afternoon light through a "
            "tall window at the left. Dark wood, worn leather chair, plain walls. The frame "
            "reads as a decision that has just been taken and a room somebody has left. No "
            "papers scattered, no books, no religious objects, no person."
        ),
    },
    {
        "name": "EP13_H12_SQUARE_CROWD_1981.png",
        "register": REGISTER_A,
        "prompt": (
            "A dense crowd in a large European public square on a bright spring afternoon in "
            "1981, seen from behind and among the people at shoulder height, so that the "
            "camera looks past heads and raised arms toward an open middle distance. Period "
            "clothing and hairstyles of 1981. Nobody in frame is identifiable: all faces are "
            "turned away from the camera. No vehicle visible, no barriers, no uniforms, no "
            "banners, no flags with emblems, no architecture that identifies a specific "
            "place, no religious imagery. Warm daylight, ordinary and expectant."
        ),
    },
    {
        "name": "EP13_H13_CORRIDOR_1981.png",
        "register": REGISTER_A,
        "prompt": (
            "An empty hospital corridor in 1981, photographed straight down its length. Pale "
            "green painted walls, a scuffed linoleum floor, a row of closed doors, one "
            "trolley parked against a wall far down. Fluorescent tubes overhead and daylight "
            "from a window at the far end. Nobody is present. Period-correct 1981 fittings, "
            "worn and ordinary. No signage, no lettering on doors, no medical equipment "
            "spectacle, no blood, no urgency, no people."
        ),
    },
    {
        "name": "EP13_H14_TWO_ENVELOPES.png",
        "register": REGISTER_A,
        "prompt": (
            "Two closed envelopes lying side by side on a plain table, photographed from "
            "directly above. One is visibly older, with age toning and a soft fold; the other "
            "is newer and cleaner. Both are completely blank: no address, no stamp, no "
            "writing, no marking of any kind. Warm even practical light, soft shadows beneath "
            "each envelope, generous empty table around them for an editor-added card. "
            "Nothing else in frame."
        ),
    },
    {
        "name": "EP13_H15_SETTING_THE_METAL.png",
        "register": REGISTER_A,
        "prompt": (
            "An extreme close macro on a jeweller's bench: a pair of fine steel tweezers held "
            "by one hand lowers a small dull lead-grey lump of metal, deformed and clearly "
            "not a gemstone, into a shallow prepared recess surrounded by polished gold and "
            "tiny set stones. Only the tweezers, the grey lump, the gold surface and part of "
            "one hand are in frame. No second hand, no complete object, no silhouette that "
            "identifies what the gold piece is, no room, no face, no tools scattered in "
            "frame. Warm intense bench light with the gold brightly specular and the grey "
            "metal deliberately dead and matte against it. Very shallow depth of field."
        ),
    },
    {
        "name": "EP13_V07_EMBER_ALONE.png",
        "register": REGISTER_B,
        "prompt": (
            "A single small warm ember suspended alone in vast pale bone-white emptiness, "
            "slightly below and right of centre, its glow falling off quickly into the white. "
            "Nothing else in the frame at all: no figure, no architecture, no ground, no "
            "horizon, no smoke. The ember is the only colour in the image. Enormous quiet "
            "negative space around it."
        ),
    },
    {
        "name": "EP13_V08_EMPTY_SUMMIT.png",
        "register": REGISTER_B,
        "prompt": (
            "The bare pale summit of a mountain with the rough timber cross standing at its "
            "highest point, seen from the same distance as before, and now completely empty: "
            "no figures anywhere, no soldiers, no fallen shape, no marks on the ground. Only "
            "the cross, the stone and the pale air. One very faint warm accent low on the "
            "slope. Bone-white and grey, true geological scale, evenly lit to every frame "
            "edge. The image reads as afterwards."
        ),
    },
    {
        "name": "EP13_V09_THE_CLIMB.png",
        "register": REGISTER_B,
        "prompt": (
            "A steep pale slope filling most of the frame, with a long thin line of very "
            "small figures climbing it in single file toward the upper right, where the "
            "ground disappears into white. The figures are tiny silhouettes at true scale, "
            "no faces, no readable clothing, no banners, no procession objects, spaced "
            "unevenly as real people climbing. Bone-white and grey with one faint warm accent "
            "low on the slope. No summit visible, no cross visible, no horizon."
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
