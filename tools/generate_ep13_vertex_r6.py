#!/usr/bin/env python3
"""EP13 round 6: put people back in.

Rounds one to five applied a rule that was correct for named historical figures
and wrong for everyone else. The bishop in white must stay unidentifiable, no
likeness of John Paul II, Lucia, John XXIII, Paul VI, Sodano or Agca may be
synthesised, and Lucia's hand must not be imitated. Those are real constraints.

They were then generalised into a blanket ban on human presence, written as "no
face" eighteen times and "no person" twelve times across 54 prompts, which left
an episode of empty rooms. This pass replaces the worst of that.

The line that actually applies:

  named historical figure  -> their real photograph only, never generated
  the bishop in white      -> stays unidentifiable, the reveal depends on it
  everyone else            -> ordinary people with visible faces

Supplied reference images are used for period clothing, room and light only. The
prompt says so explicitly, and no face from a reference is ever reproduced.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_ep13_vertex import (GLOBAL_LOCK, LOCATION, MODEL, REGISTER_A,  # noqa: E402
                                  REGISTER_B, post_json)

ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP13_VATICAN_01"
AUTH = EP / "03_VISUALS" / "ASSETS" / "SELECTED" / "AUTHENTIC"
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw" / "r6"

PEOPLE = """PEOPLE IN THIS FRAME. Ordinary people are present and their faces are
visible, lit and in focus unless the scene note says otherwise. They are unnamed
private individuals of the period, not portraits of anyone. Give them real
period-plausible clothing, posture and expression, and let them be doing
something rather than posing. Faces must be anatomically clean: two eyes, correct
ears, natural teeth if visible, no melted or duplicated features, no extra
fingers. Do NOT reproduce the face of any person from a supplied reference image;
references are for period clothing, room, materials and light only."""

REF_NOTE = """A reference image is supplied. Use it ONLY for period accuracy:
clothing cut and fabric, room fittings, light quality and the general look of the
era. Do not copy its composition, do not reproduce any face, figure or document
from it, and do not treat it as the scene."""


def refs(*names):
    out = []
    for n in names:
        p = AUTH / n
        if p.is_file():
            out.append(p)
    return out


JOBS = [
    {"name": "EP13_P01_NURSE_BEDSIDE_1981.png", "register": REGISTER_A,
     "refs": refs("EP13_Popemobile_assassination_attempt_John_Paul_II_13_may_1981_Vatican_13_j.jpg"),
     "prompt": (
         "A nurse in a 1981 hospital uniform stands at the foot of a bed in a plain "
         "hospital room, checking a chart, her face visible in three-quarter view and lit by "
         "the window. The bed is occupied but the patient is turned fully away and out of "
         "focus, so no patient face and no identity are visible. Warm late-afternoon light "
         "from a window on the left. Period-correct 1981 fittings. The nurse is an unnamed "
         "private individual, not a portrait of anyone.")},
    {"name": "EP13_P02_ARCHIVIST_AT_WORK.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "An archivist in late 1950s clothing stands in a narrow aisle between tall archive "
         "shelves, lifting a document box down with both hands, glancing at it. His face is "
         "visible in profile and clearly lit by a work lamp. Cool daylight from a high "
         "window far down the aisle. Worn wood, uniform boxes with blank spines, dust in the "
         "air. An unnamed clerk, not a portrait of anyone, no clerical dress, no insignia.")},
    {"name": "EP13_P03_CROWD_FACES_1981.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "A dense crowd waiting in a large European square on a bright spring afternoon in "
         "1981, photographed at head height from within the crowd, so a dozen faces are "
         "clearly visible and in focus, looking past the camera at something out of frame. "
         "Ordinary people of every age, period 1981 clothing and hairstyles, some smiling, "
         "some shading their eyes. Warm daylight. No banners, no flags with emblems, no "
         "uniforms, no identifiable architecture, no religious imagery, no famous face.")},
    {"name": "EP13_P04_CROWD_ALARM_FACES.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "The same kind of 1981 crowd at the instant of alarm: faces turning sharply toward "
         "something out of frame, mouths open, hands rising to cover mouths, eyes wide. "
         "Several faces clearly visible and in focus in the middle ground. Genuine shock, "
         "not horror-film grimacing. Period 1981 clothing. No weapon, no violence, no blood, "
         "no injury, no vehicle, no uniform, no identifiable building, no famous face.")},
    {"name": "EP13_P05_CONGREGATION_WAITING.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "A sparse congregation seated in the pews of a large plain church, perhaps twenty "
         "people spread across many empty rows, several faces visible and lit by cold light "
         "from high windows. They are waiting rather than praying: some looking ahead, one "
         "checking a watch, one leaning to speak to a neighbour. Mid-twentieth-century "
         "clothing. No clergy in frame, no altar detail, no statues, no famous face.")},
    {"name": "EP13_P06_TWO_MEN_TALKING.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "Two men in plain mid-twentieth-century suits sit facing each other on simple "
         "wooden chairs in a bare room, mid-conversation, one leaning forward and speaking, "
         "the other listening with his hands folded. Both faces are visible and lit by soft "
         "daylight from one side. No table, no papers, no recorder, no religious dress, no "
         "insignia. Unnamed private individuals, not portraits of anyone.")},
    {"name": "EP13_P07_PILGRIMS_CANDLES.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "Three or four ordinary pilgrims standing at a long outdoor rack of burning "
         "devotional candles at night, one lighting a candle, another watching the flames. "
         "Their faces are lit warmly from below by the candlelight and are clearly visible. "
         "Plain modern-but-timeless coats. Quiet and undramatic. No clergy, no statue in "
         "frame, no religious figure, no text, no famous face.")},
    {"name": "EP13_P08_SHEPHERD_CHILDREN_DISTANT.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "Two rural children in poor early-twentieth-century Portuguese country clothing sit "
         "on a stone wall in a bare upland pasture with a few sheep behind them, on an "
         "overcast day. They are seen at a middle distance, small in a wide landscape, faces "
         "turned toward each other in conversation rather than toward the camera, so they "
         "read as anonymous country children and not as a portrait of anyone. Plain, poor, "
         "unremarkable. No village, no church, no shrine, no modern object.")},
    {"name": "EP13_P09_CLERK_CARRYING_BOX.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "A man in a dark late-1950s overcoat walks away down a long institutional corridor "
         "carrying a flat document box under one arm, glancing back over his shoulder so his "
         "face is visible and lit. Terrazzo floor, closed identical doors, cold daylight from "
         "a window at the far end. No signage, no lettering, no clerical collar, no insignia, "
         "no famous face.")},
    {"name": "EP13_P10_PRESS_1981.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "A group of press photographers and reporters in 1981 crowded together outdoors, "
         "several faces clearly visible, one lowering his camera to write in a notebook, "
         "another calling out. Their equipment is period-correct for 1981: boxy 35mm SLR "
         "bodies with short lenses, no long white telephoto lenses, no digital screens. "
         "Neutral daylight. No logo, no press badge lettering, no famous face.")},
    {"name": "EP13_P11_HANDOVER_TWO_MEN.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "Two men in plain dark mid-twentieth-century clothing at the moment one hands a "
         "closed envelope to the other across a table, both faces visible, both looking at "
         "the envelope rather than at each other. The envelope is blank. Warm practical light "
         "from one side. A quiet formal transfer. No clerical dress, no insignia, no ring, "
         "no crucifix, no famous face.")},
    {"name": "EP13_P12_WOMAN_WRITING_ROOM.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "A young woman in plain dark 1940s clothing sits writing at a bare wooden table in a "
         "spare whitewashed room, seen from the side at a middle distance so the room and her "
         "posture carry the frame. Her face is visible in profile, lowered toward the paper, "
         "concentrating. The writing on the sheet is illegible grey texture with no formed "
         "letters. Cool daylight from a window. She is an unnamed private individual and not "
         "a portrait of anyone. No habit, no veil, no religious object, no crucifix.")},
    {"name": "EP13_P13_DOCTORS_CORRIDOR.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "Two doctors in 1981 European hospital dress stand talking quietly in a corridor: "
         "long white cotton coats over shirt and tie, no blue scrubs, no modern lanyard, no "
         "ID badge, no plastic clogs. One holds a cardboard folder. Both faces visible and "
         "lit by overhead fluorescent light. "
         "Pale green walls, scuffed linoleum, closed doors. Their expressions are tired and "
         "ordinary, not alarmed. No patient, no trolley in use, no blood, no urgency, no "
         "signage, no famous face.")},
    {"name": "EP13_P14_MAN_ALONE_PEW.png", "register": REGISTER_A, "refs": [],
     "prompt": (
         "One middle-aged man sits alone in an empty church pew, elbows on his knees, hands "
         "clasped, looking down at the floor rather than at any altar. His face is visible in "
         "three-quarter view, lit softly from a high window. Plain mid-century clothing. The "
         "rows around him are completely empty. No clergy, no statue, no candles, no "
         "religious image in frame, no famous face.")},
]


def run_with_refs(job, outdir):
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT not set")
    url = ("https://aiplatform.googleapis.com/v1/projects/" + project + "/locations/" +
           LOCATION + "/publishers/google/models/" + MODEL + ":generateContent")
    text = GLOBAL_LOCK + "\n\n" + job["register"] + "\n\n" + PEOPLE
    if job.get("refs"):
        text += "\n\n" + REF_NOTE
    text += "\n\nSCENE:\n" + job["prompt"]
    parts = [{"text": text}]
    for p in job.get("refs", []):
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        parts.append({"inlineData": {"mimeType": mime,
                                     "data": base64.b64encode(p.read_bytes()).decode("ascii")}})
    payload = {"contents": [{"role": "user", "parts": parts}],
               "generationConfig": {"responseModalities": ["IMAGE"],
                                    "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}}}
    print("GEN " + job["name"] + (f" ({len(job.get('refs', []))} ref)" if job.get("refs") else ""), flush=True)
    resp = post_json(url, payload)
    images = []
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                images.append(base64.b64decode(inline["data"]))
    if not images:
        finish = (resp.get("candidates") or [{}])[0].get("finishReason", "unknown")
        raise RuntimeError("no image (finishReason=" + str(finish) + ")")
    dest = outdir / job["name"]
    dest.write_bytes(images[0])
    print("OK  " + dest.name + "  " + str(dest.stat().st_size) + " bytes", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--outdir", default=str(OUT))
    a = ap.parse_args()
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    picks = [j for j in JOBS if not a.only or any(f.strip() in j["name"] for f in a.only.split(","))]
    print(str(len(picks)) + " job(s) -> " + str(outdir), flush=True)
    for job in picks:
        try:
            run_with_refs(job, outdir)
        except Exception as exc:
            print("FAIL " + job["name"] + ": " + str(exc)[:200], flush=True)


if __name__ == "__main__":
    main()
