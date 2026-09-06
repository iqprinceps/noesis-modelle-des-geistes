#!/usr/bin/env python3
"""EP14 image generation: the 1530 letter, the archive, and what was lost.

Three registers, described in 03_VISUALS/VISUAL_PLAN.md. A is naturalistic
photography of real places and objects, B is conservation-grade document
photography, C is absence.

The object at the centre of this episode has no free image anywhere: the 1530
letter survives publicly only as a commercial facsimile. It is therefore
reconstructed from its documented description, and the description is specific
enough that this is reconstruction rather than invention: 91.5 by 46 cm of
parchment, 83 signatures in 13 columns, 81 seals each in its own tin skippet on a
red silk cord, and 4 positions where a skippet was expected and never arrived.

Constraints inherited from EP13, each of them the fix for something that went
wrong there: no named historical figure is ever generated, no writing surface is
left blank, writing is present but never resolves into a readable word, and
ordinary people have visible faces.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import LOCATION, MODEL, post_json  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "imagegen" / "ep14"

GLOBAL = """Production constraints: horizontal cinematic 16:9 frame at 2K.
Photographic, real materials, real light, real imperfection. Full tonal range with
true shadow and no crushed blacks. NO text overlay, NO caption, NO watermark, NO
logo, NO border, NO vignette, NO tilt-shift, NO diorama or model look, NO split
screen, NO collage, NO modern object in a historical frame."""

INK = """WRITING. Every writing surface in frame carries ink and is never blank: a
period hand in iron gall brown or black, or period type, dense enough to fill the
writing area, with margins and natural variation. It must resolve into NO readable
word in any language, no name, no date, no legible heading. Keep written lines
small in the frame, let focus fall off along them, and never render an English
word anywhere in the picture."""

FACES = """PEOPLE. Anyone in frame is an ordinary unnamed person of the period,
with a visible, lit, anatomically clean face and something to do with their hands.
Never a portrait of any real or named individual."""

A = """REGISTER A, HISTORICAL. A naturalistic photograph of a real place or object.
Correct period materials, weight and wear. Available light with one clear
direction. Never glossy, never a product shot, never a render."""

B = """REGISTER B, DOCUMENT. Conservation photography: the object lit by even
raking light that reveals surface, laid on a neutral dark ground, colour accurate,
shallow depth of field. The material is the subject, so parchment fibre, wax
grain, tin, silk and ink must all read as themselves. No hands unless the scene
says so, no studio gloss, no dramatic spotlight."""

C = """REGISTER C, LOSS. What is no longer there. Cool and low in contrast, wide,
under-populated, with air and distance in the frame. Empty shelving, dust
outlines, bare boards, a road. Quiet and ordinary rather than gothic or ruined:
this register shows that most of the past disappears for dull reasons, not
dramatic ones."""


def job(name, prompt, reg=A, ink=False, faces=False):
    parts = [GLOBAL, reg]
    if ink:
        parts.append(INK)
    if faces:
        parts.append(FACES)
    return {"name": name, "text": "\n\n".join(parts) + "\n\nSCENE.\n" + prompt}


JOBS = [
    # ---------------------------------------------------------------- the object
    job("D01_LETTER_WHOLE_SHEET.png", reg=B, ink=True, prompt=(
        "One enormous single sheet of parchment, MUCH WIDER THAN TALL, laid flat and "
        "photographed from directly overhead so it fills the frame edge to edge in a long "
        "horizontal band. Its width is roughly twice its height. Across the whole width run "
        "THIRTEEN separate narrow vertical columns of short handwritten entries, evenly spaced "
        "with clear gaps of blank parchment between the columns, each column a stack of about "
        "six separate signatures in a different hand. Below all thirteen columns the parchment "
        "is folded once across its entire width, and along the whole length of that fold hangs "
        "a dense row of small round metal cases on short red cord loops, running off both sides "
        "of the frame. Even raking light. The parchment is creased and cockled.")),

    job("D02_SEAL_ROW_SIDE.png", reg=B, prompt=(
        "A long row of small round metal cases hanging side by side from a red silk cord, "
        "photographed from the side and slightly below against a dark neutral ground, so the "
        "row recedes across the frame and the cord is visibly under their weight. Each case is "
        "dull tin, hand-formed, tarnished unevenly, about the size of a large coin, and each "
        "hangs from its own short loop of cord. They touch and overlap slightly. Raking light "
        "from the left picks out the rim of every case.")),

    job("D03_SKIPPET_OPEN_MACRO.png", reg=B, prompt=(
        "Extreme close macro of one small round tin case lying open on a dark neutral surface, "
        "its lid tilted back on a short hinge of cord. Inside sits a disc of dark red wax with "
        "an impressed device on it, worn smooth in places and chipped at one edge. The tin is "
        "scratched and dull. The wax shows the fibres of the cord embedded in its back. Hard "
        "raking light from one side. No lettering of any kind is legible on the wax.")),

    job("D04_EMPTY_POSITION.png", reg=B, prompt=(
        "Close on a section of the folded lower edge of a large parchment, photographed "
        "straight on against a dark ground. Along it hang small round tin cases on short cord "
        "loops, but at the centre of the frame one loop of red silk cord hangs with nothing on "
        "the end of it: the cord is there, cut and knotted, and the case that belonged on it "
        "is absent. The parchment above shows the punched hole the cord passes through.")),

    job("D05_SIGNATURE_COLUMNS.png", reg=B, ink=True, prompt=(
        "Two narrow vertical columns of short handwritten entries on parchment, photographed "
        "from a very steep raking angle almost along the surface, so the sheet runs away from "
        "the camera and the writing is strongly foreshortened and compressed. Depth of field is "
        "extremely shallow: one band across the middle of the frame is nearly sharp and "
        "everything nearer and further dissolves. The entries are short, stacked one under "
        "another with gaps between them, each in a different hand, several with a looping "
        "flourish. Nothing is a paragraph. The strokes read as handwriting and as nothing else: "
        "no entry can be resolved into letters that spell a word or a name, in any language. "
        "Hard low light across the parchment fibre."
        " Absolutely no legible personal name anywhere in the frame.")),

    job("D06_CORD_THROUGH_FOLD.png", reg=B, prompt=(
        "Macro of a red silk cord passing through a punched hole in the folded edge of a thick "
        "parchment, photographed from the side against a dark ground. The silk is frayed and "
        "faded to a dull red, the fibres visible where it has worn. The parchment is thick, "
        "cream, slightly translucent at the fold. Hard low light.")),

    # ---------------------------------------------------------------- 1530 world
    job("H01_SEALING_TABLE_1530.png", ink=True, faces=True, prompt=(
        "A long trestle table in a stone hall in 1530, seen from one end, with three clerks in "
        "period clothing working along it. One holds a sheet flat, one is pressing a seal into "
        "wax, and one is threading cord through a punched parchment edge. Small tin cases are "
        "laid out in a row on the boards beside them. Their faces are visible and lit by cold "
        "light from a high window. Wooden bowls of wax, a brazier, a knife.")),

    job("H02_LORDS_ASSEMBLY.png", faces=True, prompt=(
        "A crowded panelled chamber in 1530, seen from the side at head height, with perhaps "
        "twenty men in heavy period robes standing and sitting in groups, mid-argument. Several "
        "faces are clearly visible and lit by cold light from tall windows on the left. Their "
        "clothing is rich but worn, fur-trimmed, dark. Nobody wears a crown or a mitre. No "
        "throne, no altar, no lettering, no heraldic banner.")),

    job("H03_COURIER_LEAVES.png", faces=True, prompt=(
        "A rider in heavy 1530s travelling clothes mounting a horse in a cobbled courtyard at "
        "dawn, a flat leather document case strapped across his back. His face is visible, "
        "turned back over his shoulder. A servant holds the bridle. Cold blue morning light, "
        "breath visible. Stone buildings behind. No banner, no crest, no lettering.")),

    job("H04_POPE_DESK_REFUSAL.png", prompt=(
        "A heavy carved writing desk in a Renaissance study, photographed from the side in warm "
        "light from a tall window. On it lies a large folded parchment with a red cord and metal "
        "cases spilling over the edge of the desk. An empty high-backed chair is pushed back "
        "from it. Nobody is in the room. Fresco fragments and dark panelling behind.")),

    # ---------------------------------------------------------------- the archive
    job("H10_READING_ROOM.png", faces=True, prompt=(
        "A long archive reading room, seen down its length, with perhaps six researchers at "
        "individual desks under green-shaded lamps, each with a bound volume open in front of "
        "them. Two faces are visible in three-quarter view, concentrating. Tall shelving of "
        "uniform boxes runs up both walls. Cold daylight from high windows mixes with the warm "
        "lamps. Quiet and ordinary. No signage, no lettering.")),

    job("H11_CALL_SLIP.png", ink=True, prompt=(
        "A small handwritten paper slip lying on a wooden counter beside a brass bell and a "
        "wire basket, photographed from above at a slight angle in warm light. The slip carries "
        "a few short handwritten lines and a stamped mark, none of it readable. The counter is "
        "worn smooth. A pencil lies across the corner of the slip.")),

    job("H12_CATALOGUE_DRAWER.png", ink=True, prompt=(
        "A wooden card catalogue drawer pulled fully open, photographed from above and slightly "
        "in front, packed tight with upright index cards. The cards are typed and handwritten, "
        "yellowed, with tabbed dividers standing above them. One card is lifted slightly proud "
        "of the rest. Warm lamplight from the left. No readable text on any card.")),

    job("H13_SHELVING_KILOMETRES.png", prompt=(
        "A very long aisle between tall metal archive shelving, photographed straight down its "
        "length so it converges into the distance, both sides packed with uniform grey document "
        "boxes. Strip lighting overhead throws even cool light. Concrete floor. Nobody in "
        "frame. No lettering on any box.")),

    job("H14_HANDS_ON_REGISTER.png", ink=True, prompt=(
        "Two hands in white cotton conservation gloves turning the page of a very large bound "
        "register on a padded book cradle, photographed from above in even light. The open "
        "pages are dense with a close period hand in brown ink. A foam wedge supports the "
        "spine. The paper is cockled and edge-worn. No face in frame.")),

    job("H15_OLD_HANDS_CLOSE.png", ink=True, prompt=(
        "Macro of a page of sixteenth-century administrative handwriting, photographed at a "
        "steep angle so the lines recede and only the nearest are close to sharp. Abbreviation "
        "marks, superscript strokes and a marginal annotation in a second hand are visible as "
        "shapes. The paper is laid, ribbed, foxed at the edge. Raking light.")),

    # ---------------------------------------------------------------- 1810
    job("H20_CRATES_PACKED.png", faces=True, prompt=(
        "A high stone hall in 1810 filled with wooden packing crates in rows, some open and "
        "half-filled with bound volumes and bundles of parchment. Four men in period working "
        "clothes are lifting and packing; two faces are visible and lit. Straw on the floor, "
        "hammers, coils of rope. Cold daylight from high windows. No lettering on the crates.")),

    job("H21_CONVOY_ROAD.png", prompt=(
        "A line of heavy horse-drawn carts loaded with roped wooden crates, photographed from "
        "the roadside at a distance on a grey day in 1810, strung out along an unmade road that "
        "curves away between bare fields. The carts are small in a wide landscape. Mud, ruts, "
        "a driver walking beside the lead horse. Flat overcast light. No banner, no uniform "
        "insignia.")),

    job("H22_ALPINE_PASS.png", prompt=(
        "A narrow road cut into a steep alpine hillside under low cloud, with a short line of "
        "loaded carts working up it, seen from above and behind so the drop falls away below "
        "them. Snow in the shadowed hollows, bare rock, thin trees. The carts are small against "
        "the scale of the pass. Cold flat light, no sun.")),

    job("H23_PARIS_UNLOADING.png", faces=True, prompt=(
        "Crates being unloaded from carts into the courtyard of a large eighteenth-century "
        "Paris mansion, seen from one corner of the courtyard. Six men are working, three faces "
        "visible and lit. The crates are stacked unevenly on the cobbles. Tall shuttered windows "
        "and a stone arcade behind. Grey daylight. No lettering, no flag.")),

    # ---------------------------------------------------------------- the loss
    job("L01_SHELVES_WITH_GAPS.png", reg=C, prompt=(
        "A wall of old wooden archive shelving photographed straight on, most of it full of "
        "uniform boxes and bundles, but with several conspicuous empty stretches where "
        "something stood for a long time: the boards there are clean rectangles inside a film "
        "of dust. Cold even light from the left. Nobody in frame.")),

    job("L02_DUST_OUTLINE.png", reg=C, prompt=(
        "Close on a bare wooden shelf photographed from above at a shallow angle, empty except "
        "for the sharp dust outline of a large rectangular object that stood there for decades. "
        "The wood inside the outline is lighter. A few fragments of straw and a broken cord "
        "remain. Cold raking light.")),

    job("L03_SCALES_PAPER.png", reg=C, ink=True, prompt=(
        "A large iron balance scale on a stone floor with a stack of loose parchment sheets "
        "piled in one pan and iron weights in the other, photographed from the side in cold "
        "light from a high window. The parchment is written on and worn. The room behind is "
        "bare and out of focus. Nobody in frame.")),

    job("L04_GROCER_WRAPPING.png", reg=C, ink=True, faces=True, prompt=(
        "A shopkeeper in early nineteenth-century working clothes wrapping goods on a counter "
        "in a small Paris shop, using a sheet of old written parchment as packing paper. His "
        "face is visible and entirely unremarkable, concentrating on the job. More sheets are "
        "stacked under the counter. Warm dim interior light, shelves of jars behind. Nothing in "
        "the frame suggests he knows what the paper is.")),

    job("L05_EMPTY_CART_RETURNING.png", reg=C, prompt=(
        "A single empty horse-drawn cart on an unmade road in flat country, photographed from "
        "behind at a distance as it moves away, its bed bare except for loose straw and a coil "
        "of rope. Grey sky, wide horizon, no other traffic. The frame is mostly road and sky.")),

    job("L06_BURNT_EDGE.png", reg=C, ink=True, prompt=(
        "A charred bundle of written parchment sheets lying on a cold stone floor, photographed "
        "from above. The outer sheets are burnt away at one corner and the char has stopped, "
        "leaving the inner sheets legible as writing but scorched brown at the edge. Ash "
        "around it. No flame, no glow, nothing burning now.")),

    # ---------------------------------------------------------------- the bunker
    job("H30_BUNKER_STAIR.png", prompt=(
        "A wide flight of plain concrete steps running down from a bright doorway into a lit "
        "basement level, photographed from the top of the flight so the steps themselves fill "
        "the lower two thirds of the frame and converge downward. A tubular steel handrail runs "
        "down the left wall. At the bottom a heavy grey door stands open onto an evenly lit "
        "corridor. Daylight behind the camera, fluorescent light below. Clean, functional and "
        "entirely unmysterious.")),

    job("H31_CLIMATE_GAUGE.png", prompt=(
        "A wall-mounted temperature and humidity recorder in a plain concrete corridor, "
        "photographed close and straight on, its paper drum turning behind glass with a faint "
        "ink trace on it. Cool even light. The corridor recedes out of focus behind. No "
        "readable numbers on the dial.")),

    job("H32_ROLLING_STACKS.png", prompt=(
        "Compact rolling archive shelving in an underground room, photographed from one end "
        "with one bay wound open to make a single narrow aisle between two solid walls of "
        "boxes. Steel handwheels on the ends. Even cool light, concrete floor, no windows. "
        "Nobody in frame.")),

    # ---------------------------------------------------------------- digital
    job("H40_SCANNING_RIG.png", faces=True, prompt=(
        "A book scanning cradle in a bright workroom with a large bound volume open on it under "
        "two soft lights and an overhead camera arm. A technician in a plain shirt is "
        "positioning the page with a gloved hand, face visible in three-quarter view. Cables, a "
        "colour chart, a monitor turned away from camera. Clean and workmanlike.")),

    job("H41_SERVER_AISLE.png", prompt=(
        "A narrow aisle between two racks of storage servers, photographed straight down its "
        "length, with small indicator lights along both sides and cable runs overhead. Cool "
        "light, dark floor, nobody in frame. No branding, no readable label.")),

    job("H42_ONE_PAGE_MISSED.png", reg=C, ink=True, prompt=(
        "A single written page lying flat and alone on a wide empty table under one cold "
        "overhead light, photographed from directly above so the table extends far beyond it on "
        "every side. The page is entirely ordinary and densely written. Nothing else is in the "
        "frame.")),
]


def render(spec, outdir):
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT not set; use run_with_vertex_secondary.ps1")
    url = ("https://aiplatform.googleapis.com/v1/projects/" + project +
           "/locations/" + LOCATION + "/publishers/google/models/" + MODEL +
           ":generateContent")
    payload = {"contents": [{"role": "user", "parts": [{"text": spec["text"]}]}],
               "generationConfig": {"responseModalities": ["IMAGE"],
                                    "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}}}
    resp = post_json(url, payload)
    for part in resp["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            data = base64.b64decode(part["inlineData"]["data"])
            (outdir / spec["name"]).write_bytes(data)
            return len(data)
    raise RuntimeError("no image returned")


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
        if (outdir / j["name"]).is_file():
            print("SKIP " + j["name"], flush=True)
            continue
        print("GEN " + j["name"], flush=True)
        try:
            n = render(j, outdir)
            print(f"OK  {j['name']}  {n} bytes", flush=True)
        except Exception as exc:
            print("FAIL " + j["name"] + ": " + str(exc)[:250], flush=True)


if __name__ == "__main__":
    main()
