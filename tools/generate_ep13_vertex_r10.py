#!/usr/bin/env python3
"""EP13 round 10: put writing on the paper.

Eight document states were blank. Three empty white sheets laid out on a table,
envelopes with no address on them, a page and an envelope with nothing written on
either. Blank paper does not read as a document; it reads as a placeholder, and
the episode is about a document.

The good states in the same film show what the difference is: the archive ledger,
the printed column, the parchment with its columns of hand copied text. They are
convincing because there is writing on them.

The constraint that produced the blanks is real but narrow. An earlier pass was
rejected for parchment carrying readable pseudo-names, so the prompts began
asking for no text at all. What is actually required is that nothing resolves
into readable words: ink that is plainly there, in period hand or period type,
that the eye reads as writing and cannot read as language.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import REGISTER_A  # noqa: E402
from generate_ep13_vertex_r6 import run_with_refs  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r10"

INK = """WRITING ON THE PAPER. Every sheet, envelope and document in this frame
carries real ink. Handwriting is a period fountain pen or dip pen hand in dark
brown or black, in even lines with natural variation in pressure and spacing;
typing is a period typewriter face. There is enough of it to fill the writing area
convincingly, with margins, line spacing and the odd correction or blot.

It must NOT be readable. No letterform resolves into an actual word in any
language, no name, no date, no number, no heading, no signature that reads as a
name, no stamp with legible text. At normal viewing distance the eye must say
"this is a written document" and be unable to read a single word of it. Achieve
that with slightly soft focus on the text, shallow depth of field, raking light
across the paper, and letterforms that are convincing in rhythm but not in
detail. Never leave a writing surface blank.

NO LABEL WORDS. Never render an English word anywhere in the frame, and in
particular never write out a word that appears in this instruction, such as
archive, docket, seal or address. A single large line of display handwriting will
always resolve into pseudo-words and look invented; keep written lines small
relative to the frame, break them across an oblique viewing angle, and let focus
fall off along them."""


def job(name, prompt):
    return {"name": name, "register": REGISTER_A + "\n\n" + INK, "refs": [], "prompt": prompt}


JOBS = [
    job("EP13_H50_THREE_READERS_TABLE.png", (
        "Three separate sheets of aged paper laid out side by side on a worn wooden table, "
        "seen from almost directly above in cold daylight from a window on the left. Each "
        "sheet is densely covered in a different hand: the left one a cramped upright script, "
        "the middle one a looser sloping script, the right one typed in a period typewriter "
        "face. Each has been folded and opened out again, with the creases catching the light. "
        "One has a pencil annotation in the margin. The wood grain and the paper fibre are "
        "sharp; the writing itself is slightly soft. Nothing else on the table.")),

    job("EP13_H14_TWO_ENVELOPES.png", (
        "Two envelopes overlapping on dark scratched wood, photographed from a low oblique "
        "angle close to the tabletop so both surfaces are steeply foreshortened and recede from "
        "the camera. The near one is older and yellowed with its flap opened and reclosed; the "
        "far one is paler and sealed with dark red wax. Both carry several small lines of dark "
        "fountain pen writing and a faint circular ink stamp, all of it running away from the "
        "camera at an angle and softening out of focus within a centimetre. Warm low light from "
        "the left. No line of writing is large, level or in focus.")),

    job("EP13_H48_PAGE_BECOMES_OBJECT.png", (
        "An opened sheet of handwritten paper lying beside the envelope it came out of, on a "
        "worn wooden surface, seen from above at a slight angle in warm raking light. The "
        "sheet is covered edge to edge in a close period hand with visible fold creases across "
        "it. The envelope beside it is addressed in the same hand and its flap is torn open. "
        "The relationship between the two objects is the subject of the frame.")),

    job("EP13_H52_ENVELOPE_ALONE_WIDE.png", (
        "A single sealed envelope lying alone in the centre of a very large empty wooden table, "
        "shot from a low angle close to the tabletop so the envelope stands out against the "
        "long recession of bare wood behind it. It is addressed across the middle in a heavy "
        "dark hand, carries a small archive docket in the upper corner, and is closed with a "
        "dark red wax seal. Hard light from one side throws a long shadow from it. The rest of "
        "the table is bare and falls away into shadow.")),

    job("EP13_H08_ENVELOPE_CARRIED.png", (
        "A man in a plain dark mid-twentieth-century overcoat and leather gloves holds a large "
        "sealed envelope against his chest with both hands, seen from the front from the chest "
        "down so that his head is out of frame entirely. The envelope faces the camera and is "
        "addressed across it in a strong dark hand, with a second smaller line beneath and an "
        "ink stamp in the corner. Cold overcast daylight. No face, no insignia, no badge.")),

    job("EP13_H24_HAND_ON_ENVELOPE.png", (
        "One adult hand rests flat and still on top of a large aged envelope on a worn desk, "
        "fingers spread, seen from above and slightly to the side in warm lamplight from the "
        "left. The parts of the envelope not covered by the hand show a dense address written "
        "in dark ink and an official ink stamp near the corner. The hand is doing nothing: it "
        "is simply resting there, keeping it shut. Skin texture and paper fibre both sharp.")),

    job("EP13_H01_ENVELOPE_SEALED.png", (
        "A large aged envelope on dark scratched wood, photographed close and at a steep "
        "oblique angle from one corner, so the surface runs away from the camera and the "
        "writing on it is strongly foreshortened. The thick dark red wax seal on the flap is "
        "the sharpest thing in the frame and the focus falls off quickly along the paper, so "
        "the several lines of dark fountain pen writing are legible as ink and lost as words. "
        "Warm low light rakes across the paper from the left, catching two old fold lines and "
        "the worn fibres of the edges. No line of writing is large, level or in focus.")),

    job("EP13_H19_PAPERS_ON_DESK_NIGHT.png", (
        "Half a dozen handwritten sheets spread across a dark wooden desk at night, overlapping "
        "each other, lit only by a green glass banker's lamp at the left of the frame. Every "
        "sheet is covered in a close period hand and the light falls across them so the writing "
        "is bright near the lamp and disappears into shadow at the right of the desk. A closed "
        "fountain pen lies among them. The room beyond the lamp is dark.")),
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
