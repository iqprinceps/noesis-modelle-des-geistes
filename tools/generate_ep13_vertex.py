#!/usr/bin/env python3
"""Generate the EP13 Vatican I reconstruction images with Vertex AI (Nano Banana Pro).

Two visual registers, deliberately incompatible so the viewer can never mistake
the reported vision for a record of an event:

  A  HISTORICAL  naturalistic colour, practical light, tactile material, grounded camera
  B  VISION      near-monochrome, luminous overexposure, one ember accent, no horizon

Outputs land in a QA directory. Nothing is copied into the episode folder by this
script; that is the production QA pass, per the render-economy preflight gate in
07_ENGLISH_PRODUCTION/00_GLOBAL/VISUAL_RETENTION_STANDARD.md.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import subprocess
import time
import urllib.error
import urllib.request
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw"
MODEL = "gemini-3-pro-image"
LOCATION = "global"

GLOBAL_LOCK = """Production constraints: horizontal cinematic 16:9 frame at 2K.
This is documentary reconstruction for a factual film, not horror-poster art and not
fantasy illustration. Any human body must have plausible anatomy: one head, two arms,
two hands, two legs, natural joints and fingers, no duplicate limbs, no merged bodies,
no extra people. Do not add logos, captions, watermarks, interface words, invented
handwriting, fake labels, random symbols or any legible generated text. No modern
objects in historical rooms. No CGI sheen, no plastic skin, no lens flare gimmicks.
Preserve empty negative space for editor-added cards.
NO VIGNETTE. Do not darken the frame corners or edges. Do not add a border, a frame,
letterboxing or any poster treatment. Brightness stays even to the very edge of frame.
NO TILT-SHIFT and no miniature or scale-model look: focus is consistent across the
frame and the top and bottom bands are never artificially blurred."""

REGISTER_A = """VISUAL REGISTER A, HISTORICAL. Naturalistic colour with restrained
saturation. Light comes from plausible practical sources in the room. Shadow detail
stays readable and nothing is crushed to pure black. Materials are tactile: paper fibre,
cloth weave, worn wood, aged metal. Camera is grounded and static, normal lens, no
wide-angle distortion. The frame must look photographed, never painted and never
luminous."""

REGISTER_B = """VISUAL REGISTER B, VISION. This is a reported inner vision, not an
event and not a photograph. Near-monochrome, desaturated to cool bone-white and pale
grey, with exactly one warm ember accent. Highlights bloom past detail so bright areas
lose their edges. No sky horizon line and no ground plane anchor: space is ambiguous.
Human figures are small in the frame, seen at distance, never with a readable face.
Everything is at true full scale with real architectural mass and real distance: never
a diorama, never a model, never toy-like proportions. This register must never look
grainy, sepia, period-photographic, archival, or like a painting hanging in a museum.
It must read as something remembered, not something recorded."""

JOBS = [
    {
        "name": "EP13_V01_ANGEL_SWORD.png",
        "register": REGISTER_B,
        "prompt": (
            "A tall standing figure at distance holding a straight sword raised, the blade "
            "carrying fire along its length. The flames spread outward into the pale field "
            "as if they could take hold of everything, then thin and fail near the frame "
            "edges. The figure is a silhouette of light with no readable face, no wings "
            "rendered as feathered costume, no armour detail, no religious iconography "
            "props. The ember accent is the burning blade alone. Vast empty pale space "
            "around and above the figure. Nothing beneath the figure suggests a floor."
        ),
    },
    {
        "name": "EP13_V03_RUINED_CITY.png",
        "register": REGISTER_B,
        "prompt": (
            "A large city, half of it in ruins, at true full scale. The camera stands in "
            "the empty street at human eye level, so the standing walls rise well above the "
            "viewer and the distance recedes for many blocks. Broken roof lines, hollow "
            "window openings, collapsed upper storeys, a few surviving towers. Architecture "
            "is generic and unplaceable: no recognisable landmark, no dome, no identifiable "
            "skyline, no signage. Everything is bleached toward bone-white with the deepest "
            "tones only a mid grey. One single small warm ember glow sits far down the "
            "street. A very small solitary figure in white walks away from the camera in the "
            "middle distance, seen only from behind, no face, no detail, no vestments "
            "readable. Sharp architectural edges, real stone mass, no softness gimmick. No "
            "smoke plumes, no fire spectacle, no vehicles, no crowds."
        ),
    },
    {
        "name": "EP13_V02_FIGURE_IN_WHITE.png",
        "register": REGISTER_B,
        "prompt": (
            "One very small solitary figure in a long plain white robe, standing still, seen "
            "entirely from behind, FAR AWAY: the whole figure occupies less than one tenth "
            "of the frame height and sits low in a vast pale emptiness. No face, no profile, "
            "no visible hair, no visible skin, no neck, no hands: the head is only a pale "
            "shape and the body dissolves into the light at its edges. The robe is undefined "
            "cloth with no collar, no seams, no embroidery, no mitre, no crozier, no "
            "pectoral cross and no insignia of any kind. Nothing identifies a rank, a period "
            "or a person. Bone-white space all around with no floor, no wall and no horizon. "
            "One faint warm accent far beyond the figure. This must read as a remembered "
            "shape, never as a photograph of a man."
        ),
    },
    {
        "name": "EP13_V04_THE_WAY.png",
        "register": REGISTER_B,
        "prompt": (
            "A wide empty road of pale dust receding into bleached distance. Along both "
            "verges lie low still shapes covered entirely by pale cloth, small and far away, "
            "reading only as covered forms. Absolutely no visible body, no limb, no face, no "
            "skin, no blood, no wound, no distress detail of any kind: only cloth and "
            "silence. The shapes grow smaller and less distinct with distance. Bone-white "
            "and pale grey. One faint warm accent at the far end of the road. Restraint and "
            "quiet, not spectacle. No vehicles, no rubble, no soldiers, no onlookers."
        ),
    },
    {
        "name": "EP13_V06_THE_FALL.png",
        "register": REGISTER_B,
        "prompt": (
            "A full-frame view of a bare pale summit that fills the lower half of the image, "
            "with the rough timber cross standing at its highest point on the right. Left of "
            "the cross, a single small white figure is caught mid-fall, tilted backward, "
            "already close to the ground. Further left and slightly below, a compact group "
            "of small dark silhouettes stands with long weapons raised toward the figure. "
            "Thin pale streaks cross the air between them. Everything is distant silhouette "
            "at true scale, no face anywhere, no uniform detail, no insignia, no visible "
            "impact, no blood, no wound and no violence detail. Bone-white and grey with one "
            "faint warm accent low on the slope. The image must fill the entire 16:9 frame "
            "edge to edge with NO black bars at top or bottom and no letterboxing."
        ),
    },
    {
        "name": "EP13_H01_ENVELOPE_SEALED.png",
        "register": REGISTER_A,
        "prompt": (
            "One closed envelope of aged paper lying alone on a plain dark wooden surface, "
            "photographed from directly above. The flap is closed and secured with a plain "
            "disc of dark red sealing wax bearing no readable device, no crest, no letters "
            "and no symbol. The envelope carries no address, no stamp, no writing of any "
            "kind: its face is completely blank. Soft warm practical light from one side "
            "gives the paper visible fibre and a faint shadow. Nothing else in frame. "
            "Generous empty wood around the envelope for an editor-added card."
        ),
    },
    {
        "name": "EP13_H04_ARCHIVE_STORE.png",
        "register": REGISTER_A,
        "prompt": (
            "A quiet institutional archive storeroom in the late 1950s, seen down a narrow "
            "aisle between tall wooden shelving. The shelves hold uniform bound volumes and "
            "plain document boxes with blank spines and no readable labels. Halfway along "
            "the aisle a single small envelope lies flat on an otherwise empty shelf at "
            "chest height, slightly separate from everything around it. Cool daylight from a "
            "high window at the far end, one warm practical lamp nearer the camera. Worn "
            "wood, dust in the air, tiled or stone floor. No people, no ladders, no signage, "
            "no religious decoration, no modern equipment."
        ),
    },
    {
        "name": "EP13_V05_MOUNTAIN_CROSS.png",
        "register": REGISTER_B,
        "prompt": (
            "A steep bare mountain rising out of pale ambiguous space, seen from below and "
            "at a distance so its full height is felt. At the summit stands a large cross "
            "made of rough-hewn tree trunks with the bark still on them, plainly built, no "
            "ornament, no figure on it. A thin line of very small figures climbs the slope "
            "toward it, tiny against the mass of the mountain, no faces, no readable "
            "clothing, no procession banners. Bone-white and pale grey throughout, with one "
            "faint warm accent low on the slope. Real geological scale and weight. No sky "
            "horizon line, no clouds rendered as scenery, no sunburst, no rays of light."
        ),
    },
    {
        "name": "EP13_H02_SHEET_TWENTYFIVE_LINES.png",
        "register": REGISTER_A,
        "prompt": (
            "A single small sheet of aged writing paper lying on a plain dark wooden table, "
            "photographed from slightly above and to one side. The sheet carries roughly "
            "twenty-five short lines of handwriting in dark ink. CRITICAL: the writing must "
            "be completely illegible at every scale, rendered as the rhythm and grey texture "
            "of handwriting only, with no formed letters, no readable words, no alphabet of "
            "any language, no signature. Shallow depth of field so the ink texture softens "
            "away from the focus point. The paper has a soft horizontal fold line and gentle "
            "age toning at the edges. Nothing else on the table. Warm low practical light "
            "from the left. No hands, no pen, no envelope, no decoration."
        ),
    },
    {
        "name": "EP13_H03_HOSPITAL_ROOM_1981.png",
        "register": REGISTER_A,
        "prompt": (
            "A plain hospital room in 1981 seen from the foot of the bed, late afternoon. "
            "The bed is occupied but the patient is out of frame beyond the near edge or "
            "turned entirely away, so no face and no identity are visible. On the small side "
            "table beside the bed lies one closed envelope, and nothing else. Period-correct "
            "1981 clinical furniture: enamelled metal bed frame, folded pale blanket, simple "
            "chair, plain wall. Warm daylight through a window at the left, practical lamp "
            "off. Quiet, ordinary, undramatic. No medical equipment spectacle, no monitors, "
            "no drip stands crowding the frame, no religious objects, no clergy, no "
            "recognisable person, no crowd, no flowers."
        ),
    },
]


_token_cache: dict[str, Any] = {}


def access_token() -> str:
    now = time.time()
    if _token_cache.get("expires", 0) > now + 60:
        return str(_token_cache["value"])
    done = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        capture_output=True, text=True, shell=True, timeout=90)
    value = done.stdout.strip()
    if not value:
        raise RuntimeError("no ADC token: run tools/run_with_vertex_secondary.ps1 -Check")
    _token_cache.update(value=value, expires=now + 3300)
    return value


def post_json(url: str, payload: dict[str, Any], retries: int = 8) -> dict[str, Any]:
    waits = [10, 20, 30, 45, 60, 90, 120]
    for attempt in range(retries):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + access_token(),
                     "Content-Type": "application/json; charset=utf-8"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=420) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:600]
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                wait = waits[min(attempt, len(waits) - 1)]
                print("  retry HTTP " + str(exc.code) + " in " + str(wait) + "s", flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError("HTTP " + str(exc.code) + ": " + body) from None
        except Exception:
            if attempt >= retries - 1:
                raise
            time.sleep(waits[min(attempt, len(waits) - 1)])
    raise RuntimeError("generation failed after retries")


def run(job: dict[str, Any], outdir: pathlib.Path) -> pathlib.Path:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT not set; start via run_with_vertex_secondary.ps1")
    url = ("https://aiplatform.googleapis.com/v1/projects/" + project +
           "/locations/" + LOCATION + "/publishers/google/models/" + MODEL + ":generateContent")
    text = GLOBAL_LOCK + "\n\n" + job["register"] + "\n\nSCENE:\n" + job["prompt"]
    payload = {"contents": [{"role": "user", "parts": [{"text": text}]}],
               "generationConfig": {"responseModalities": ["IMAGE"],
                                    "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}}}
    print("GEN " + job["name"], flush=True)
    resp = post_json(url, payload)
    images = []
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                images.append(base64.b64decode(inline["data"]))
    if not images:
        finish = (resp.get("candidates") or [{}])[0].get("finishReason", "unknown")
        raise RuntimeError("no image for " + job["name"] + " (finishReason=" + str(finish) + ")")
    dest = outdir / job["name"]
    dest.write_bytes(images[0])
    print("OK  " + dest.name + "  " + str(dest.stat().st_size) + " bytes", flush=True)
    return dest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma separated name fragments")
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
