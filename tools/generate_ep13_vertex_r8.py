#!/usr/bin/env python3
"""EP13 round 8: give the vision register something to look at.

Seven of the seventeen vision states were a pale field with an ember dot on it:
V02, V07, V11, V15, V18, V19, V20. Together they held about twenty-five seconds
of screen time on frames with no subject in them.

The cause is the same one that emptied the rooms in round six. REGISTER_B says
"near-monochrome bone-white", "one warm ember accent", "figures small, at
distance, never a readable face" and "no horizon, no ground plane". Those are
constraints on how substance is rendered. Read as a description of the content
itself, they produce an empty frame, and that is how they were read.

EP05's picture direction is the corrective, and it is blunt about it:

    Empty rooms are expectation only. Their immediate successor must pay off
    with movement, face, figure, pressure, trace or reveal.
    An image that does none of these does not enter the final film.

The vision text is not abstract. It has an angel with a burning sword, a city
half in ruins, bodies on the road, a steep mountain, a great cross, soldiers who
fire, and a man in white who falls and does not get up. That is a sequence of
scenes. This round renders them as scenes.

What stays: the bishop in white is never identifiable, because the reveal depends
on the viewer not being told who he is. No likeness of any named figure is
synthesised. The register stays otherworldly rather than photographic.

What changes: full tonal range instead of blown-out white, real texture and
atmosphere, bodies with weight, and faces on the people around the bishop, who
are unnamed and may be seen.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex_r6 import run_with_refs  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r8"

REGISTER_B2 = """VISUAL REGISTER B, VISION. This is a reported inner vision: something
remembered rather than something photographed. It is desaturated and cool, close to
monochrome, with one warm ember accent somewhere in the frame.

It is NOT a white void. The frame carries a full tonal range from deep shadow through
mid greys to light, with real texture everywhere: stone grain, dust hanging in the air,
smoke, cloth weave, wet ash, scratched metal. Atmosphere has structure and depth, with
layers receding into distance, so the space reads as a real place seen under strange
light. Highlights may bloom, but never so far that the subject disappears into the
paper. If the frame could be described as "pale background with a small mark on it",
it is wrong.

Every frame has a subject with mass: a body, a structure, a landform, an object at
real scale. Human figures are real human bodies with weight, posture and gesture,
never specks. Space is ambiguous rather than empty: the horizon may be lost in haze
or smoke, but there is always ground, distance and something standing in it.

Never grainy, never sepia, never period-photographic, never archival, never a painting
in a museum frame, never a diorama or model, never toy-like proportions."""

FACES = """PEOPLE IN THIS FRAME. The unnamed people in this vision are real human
beings and their faces may be seen, lit and in focus, with real expression. They are
not portraits of anyone. Faces must be anatomically clean: two eyes, correct ears,
natural proportions, no melted or duplicated features, no extra fingers."""

BISHOP = """THE MAN IN WHITE. One figure wears a plain white robe. His face is NEVER
readable: he is turned away, or his head is bowed into shadow, or distance and haze take
the features. No mitre, no crozier, no pectoral cross, no vestment ornament, no insignia
of any kind, and no resemblance to any real person living or dead.

He must NOT be painted as Jesus Christ, and the usual signals of that must all be absent.
His hair is SHORT, grey and close-cropped. He is clean shaven with NO beard and NO
moustache. No long hair, no shoulder-length hair, no parted centre hair, no halo, no
crown of thorns, no bare feet, no robe draped over one shoulder, no outstretched arms,
no wounds. He is an elderly ordinary man in a plain white cassock, and if the frame could
be mistaken for a devotional image of Christ it is wrong."""


def job(name, prompt, faces=True, bishop=False):
    reg = REGISTER_B2 + ("\n\n" + FACES if faces else "") + ("\n\n" + BISHOP if bishop else "")
    return {"name": name, "register": reg, "refs": [], "prompt": prompt}


JOBS = [
    # "Then the children see a bishop dressed in white."
    job("EP13_V02_FIGURE_IN_WHITE.png", faces=False, bishop=True, prompt=(
        "A man in a plain white robe stands alone on a broad expanse of cracked pale stone, "
        "seen from behind and slightly below, filling the middle of the frame from the waist "
        "up in the lower third and standing at a real human distance of perhaps eight metres. "
        "His robe hangs with real weight, the cloth creased and moving slightly, its hem dark "
        "with dust. Ahead of him the ground recedes into thick standing haze through which the "
        "faint mass of a ruined skyline is just discernible. Shafts of cold light come down "
        "through the haze and pick out dust in the air. One small ember of warm light burns "
        "low and far off in the murk ahead of him. Deep shadow at the frame edges.")),

    # "And the bishop in white does not survive."
    job("EP13_V18_THE_MAN_DOES_NOT_RISE.png", faces=False, bishop=True, prompt=(
        "A man in a white robe lies fallen on wet dark stone at the foot of a great rough "
        "timber cross, seen from a low angle a few metres away. His body has real weight: one "
        "arm folded beneath him, the white cloth soaked grey and clinging, spread across the "
        "stone and stained with ash and water. His head is turned fully away from the camera "
        "into deep shadow so no face is visible. He is completely still. Above and behind him "
        "the cross rises out of frame into drifting smoke. Cold light rakes across the wet "
        "stone and catches every crack in it. A single warm ember lies on the ground near his "
        "hand, small and almost out. Nobody else is in the frame. No blood, no wound, no "
        "weapon, no gore.")),

    # "Or are you looking for yourself?"  — the intimate half of the WORLD / MYSELF pair
    job("EP13_V19_LOOKING_FOR_YOURSELF.png", faces=True, prompt=(
        "One ordinary man in his fifties sits alone on a low stone step in a vast dim "
        "interior, photographed close, his upper body filling much of the frame. He is "
        "leaning forward with his forearms on his knees and his hands loosely clasped, "
        "looking down and slightly away from the camera, entirely absorbed in a thought. His "
        "face is clearly visible in three-quarter view, lit softly from one side, lined and "
        "tired and completely still: this is a man recognising something about himself, not "
        "performing an emotion. Plain dark clothing with visible fabric texture. Behind him "
        "the space falls away into layered shadow and hanging dust with a single warm ember "
        "of light far back in it. No religious dress, no insignia, no text.")),
    job("EP13_V07_THE_IMPRESSION.png", faces=True, bishop=True, prompt=(
        "Three or four ordinary people stand in the near foreground with their backs "
        "three-quarters to the camera, close enough that two of their faces are visible in "
        "profile, lit from ahead. They have stopped walking and are looking at a man in a "
        "white robe who stands twenty metres away in drifting haze, his back to them, small "
        "but unmistakably a person. On the visible faces there is the exact moment of "
        "half-recognition: not awe, not fear, a quiet uncertain knowing. Cracked pale stone "
        "underfoot, layered mist behind, cold shafts of light. A single warm ember burns on "
        "the ground between the group and the figure.")),

    # "So what would you do with that page, if you were him?"
    job("EP13_V11_THE_PAGE_IN_YOUR_HANDS.png", faces=False, prompt=(
        "First person point of view looking down at your own two hands, which hold a single "
        "sheet of old handwritten paper open in front of you. The hands and forearms fill the "
        "lower half of the frame in sharp detail: skin texture, knuckles, the tension of "
        "fingers gripping the edges of the page. The page itself is lit warm from one side and "
        "its handwriting is soft and unreadable. Beyond the hands the room falls away into a "
        "deep dim interior of stone and hanging dust, with a small warm ember of lamplight far "
        "back in it. Nobody else is present. No face, no legible text, no religious dress.")),

    # "Are you looking for the world in there?"  — the vast half of the pair
    job("EP13_V15_LOOKING_FOR_THE_WORLD.png", faces=False, prompt=(
        "An enormous ruined city seen from high on a hillside at dusk, filling the whole frame "
        "and receding for miles into smoke: broken roofs, collapsed towers, streets full of "
        "rubble, whole districts flattened, layer behind layer fading into haze. The scale is "
        "vast and the detail is real, with texture in every roof and wall. In the lower "
        "foreground, very small against it, a line of tiny human figures moves along a road, "
        "far too distant for any face. Cold blue light in the sky, and scattered across the "
        "ruins a handful of small warm embers still burning. No fire storm, no explosion, no "
        "aircraft, no military vehicle, no flag, no lettering.")),

    # "Next time: why that letter survived, and what did not."
    job("EP13_V20_WHAT_SURVIVED.png", faces=False, prompt=(
        "A very long dark refectory table running away from the camera down the centre of a "
        "vast dim stone hall, seen from one end at table height. Documents lie along it in a "
        "row: thick folded parchments, bundles tied with cord, a few with heavy wax seals, "
        "their surfaces caught in hard raking light from high windows on the left. Between "
        "them are conspicuous empty spaces on the bare wood where documents are missing, with "
        "only the pale dust outlines left behind. The row recedes into darkness at the far end "
        "of the hall. One small warm ember of lamplight burns midway down the table. No "
        "legible writing, no person, no shelving.")),
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
