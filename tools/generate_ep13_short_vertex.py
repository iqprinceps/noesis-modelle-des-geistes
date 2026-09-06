#!/usr/bin/env python3
"""Vertical stills for the EP13 teaser short.

The short is a separate film, not a trimmed episode, so it gets its own pictures
in 9:16 rather than crops of the 16:9 ones. A crop of a wide frame puts the
subject in the middle of a tall box and throws away most of the composition; a
frame built tall can use the height, which is the only thing a phone gives you.

The same picture set serves the English and the German short, because both
scripts were written to the same fourteen beats. Only the narration differs.

The identity rules from the episode still apply: named historical figures appear
only in real photographs and are never generated, and the man in white is never
identifiable.
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
OUT = ROOT / "tmp" / "imagegen" / "ep13_short_vertical"

VERTICAL_LOCK = """Production constraints: VERTICAL 9:16 frame, 2K, built for a phone
held upright. Compose for height: let the subject run up or down the frame, stack
foreground, middle and distance vertically, and put the point of interest away from
the exact centre. The top and bottom eighth of the frame may carry interface, so
nothing essential sits there. Photographic, real materials, real light. No text, no
lettering, no captions, no watermark, no logo, no border, no vignette, no tilt-shift,
no split screen, no collage."""

REGISTER_A = """VISUAL REGISTER A, HISTORICAL. A naturalistic photograph of a real
place or a real object: correct period materials, weight, wear and imperfection.
Available light with a clear direction. Full tonal range with real shadow. Never
glossy, never a product shot, never a render."""

REGISTER_B = """VISUAL REGISTER B, VISION. Something remembered rather than
photographed. Desaturated and cool, close to monochrome, with one warm ember accent.
Full tonal range from deep shadow to light, with real texture everywhere: stone
grain, dust in the air, smoke, cloth. Every frame has a subject with mass. Never a
pale field with a small mark on it."""

BISHOP = """THE MAN IN WHITE. He wears a plain white cassock, has SHORT GREY
CLOSE-CROPPED HAIR and NO BEARD, and his face is NEVER readable: turned away, bowed
into shadow, or lost to distance. No mitre, no crozier, no pectoral cross, no
insignia. He must NOT read as a depiction of Jesus Christ: no long hair, no halo, no
bare feet, no outstretched arms."""


def job(name, prompt, register=REGISTER_A, bishop=False):
    reg = VERTICAL_LOCK + "\n\n" + register + ("\n\n" + BISHOP if bishop else "")
    return {"name": name, "text": reg + "\n\nSCENE.\n" + prompt}


JOBS = [
    job("SH01_CROWN_TALL.png", (
        "A jewelled gold crown standing upright on a dark altar cloth, photographed from "
        "slightly below so it rises through the middle of a tall frame. Pearls, small "
        "stones and worked gold catch a single warm light from the left. Deep shadow above "
        "and below it. Among the arches near the top of the crown sits one small dull grey "
        "metal object that does not belong with the jewels.")),

    job("SH02_BULLET_MACRO.png", (
        "Extreme close macro, vertical, of a single spent lead projectile lying on dark "
        "velvet, filling the upper half of a tall frame with the cloth falling away into "
        "shadow below it. The metal is dull, scratched and slightly deformed. Hard raking "
        "light from one side picks out every mark on it.")),

    job("SH03_SQUARE_CROWD_1981.png", (
        "A dense crowd in a large European square on a bright spring afternoon in 1981, "
        "photographed from within the crowd at head height in a tall vertical frame, so "
        "faces fill the lower two thirds and the sky and colonnade rise above them. Ordinary "
        "people of every age in period clothing, looking past the camera at something out of "
        "frame. Warm daylight. No banner, no flag, no lettering, no famous face.")),

    job("SH04_HOSPITAL_WINDOW.png", (
        "A tall narrow hospital window in 1981, seen from inside a dim room, with pale "
        "daylight coming through it and falling down a bare wall onto the corner of a bed. "
        "Period fittings, worn paint, a drip stand in shadow. Nobody in the frame. The frame "
        "reads from the bright window at the top down into darkness at the bottom.")),

    job("SH05_ENVELOPE_UPRIGHT.png", (
        "A large aged envelope standing upright and leaning against a dark stone wall, "
        "photographed straight on in a tall frame, lit warmly from one side. It carries "
        "several small lines of dark fountain pen writing, steeply foreshortened and soft, "
        "and is closed with a thick dark red wax seal. Deep shadow above and below.")),

    job("SH06_TWO_CHAIRS_EMPTY.png", (
        "Two plain wooden chairs facing each other in a tall bare stone room, seen from "
        "above and to the side so the floor runs up through the frame. Nobody is sitting in "
        "them. Cold light from a high window falls between them onto worn flagstones. Dust "
        "hangs in the beam.")),

    job("SH07_HAND_WRITING_1944.png", (
        "A woman's hand writing with a pencil on a sheet of paper on a plain wooden table, "
        "seen from directly above in a tall frame so the forearm enters from the bottom and "
        "the sheet fills the middle. Mid-1940s sleeve. The writing on the page is dense and "
        "unreadable. Warm lamplight from the left. No face in frame.")),

    job("SH08_ARCHIVE_SHAFT.png", (
        "A very tall archive shelf photographed from below, boxes and bound volumes "
        "receding upward into darkness, with one work lamp low on the left throwing light "
        "across the nearest spines. The frame reads from the lit boxes at the bottom up into "
        "black. No lettering on any box.")),

    job("SH09_MAN_ALONE_THINKING.png", (
        "One ordinary man in his sixties sits alone on a low stone step in a vast dim "
        "interior, photographed close in a tall frame so his head and shoulders fill the "
        "upper half and the steps fall away below him. He leans forward with his forearms on "
        "his knees, looking down and away, entirely absorbed. His face is clearly visible in "
        "three-quarter view, lined and still. Plain dark clothing. He is an unnamed private "
        "individual, not a portrait of anyone.")),

    job("SH10_FIGURE_IN_WHITE_TALL.png", register=REGISTER_B, bishop=True, prompt=(
        "A man in a plain white cassock stands far off at the bottom of a tall frame, seen "
        "from behind, on cracked pale stone. Above and beyond him the haze rises and fills "
        "most of the frame, with the faint mass of a ruined skyline just discernible in it "
        "and shafts of cold light coming down through the dust. One small warm ember burns "
        "on the ground near him.")),

    job("SH11_CROWN_EMBER_VISION.png", register=REGISTER_B, prompt=(
        "The silhouette of a jewelled crown in a dark interior, rim lit and standing upright "
        "in the lower half of a tall frame, its arches picked out against blackness. From the "
        "point where the arches meet, one small warm ember burns, and thin smoke rises from it "
        "up through the empty top of the frame. No face, no figure, no lettering.")),

    job("SH12_PILGRIM_CANDLES_TALL.png", (
        "A tall rack of burning devotional candles at night, photographed close so the "
        "flames run from the bottom of the frame to the top in receding rows. One ordinary "
        "person stands at the left edge, lit warmly from below, watching them. Their face is "
        "visible. Quiet and undramatic. No clergy, no statue, no text.")),
    # --- second teaser: the silence ---
    job("SB01_SAFE_DOOR_TALL.png", (
        "A heavy steel archive door standing shut in a tall stone doorway, photographed "
        "straight on so it fills the middle of a tall frame with worn stone above and below "
        "it. A brass handle and an old lock plate catch a single hard light from the left. "
        "The metal is scratched and cold. Nobody in frame, no lettering.")),

    job("SB02_WOMAN_AT_WINDOW.png", (
        "A woman in her fifties in plain mid-twentieth-century clothing stands at a tall "
        "narrow window in a bare room, seen from behind and slightly to the side, small at "
        "the bottom of a tall frame with the window and the wall rising above her. Grey "
        "daylight. Her face is not visible. She is an unnamed private individual.")),

    job("SB03_CALENDAR_YEARS.png", (
        "A thick block of loose paper calendar pages stacked and curling on a dark wooden "
        "shelf, photographed close from slightly above in a tall frame so the stack fills the "
        "lower half and the shelf recedes upward into shadow. The printed dates are soft and "
        "unreadable. Dust on the top sheet. Warm low light from one side.")),

    job("SB04_TELEPHONE_UNANSWERED.png", (
        "A black bakelite telephone from the 1950s sitting alone on a bare wooden desk, "
        "photographed from above and slightly to the side in a tall frame, with the desk "
        "surface running away up the frame into darkness. The handset rests in its cradle. "
        "Cold daylight from the left. Nobody in frame.")),

    job("SB05_LOCKED_DOOR_CORRIDOR.png", (
        "A long institutional corridor in a tall vertical frame, seen from the floor looking "
        "down its length, with identical closed doors receding away and one bare bulb "
        "burning near the far end. Terrazzo floor, worn paint. Nobody in frame, no signage.")),

    job("SB06_NEWSPAPERS_PILED.png", (
        "A tall unsteady stack of folded old newspapers on a stone floor, photographed from "
        "low down so the stack rises through most of the frame against a dark wall. The "
        "print on the visible pages is dense and unreadable. One hard light from the right "
        "rakes across the paper edges.")),

    job("SB07_CROWD_WAITING_TALL.png", (
        "A crowd of ordinary people waiting outside on a grey day, photographed from within "
        "them at head height in a tall frame so faces fill the lower two thirds and an "
        "overcast sky rises above. They are looking in the same direction at something out "
        "of frame, patient rather than excited. Mid-twentieth-century clothing. No banner, "
        "no lettering, no famous face.")),

    job("SB08_ENVELOPE_IN_DARK.png", (
        "A single sealed envelope lying flat in a shallow open document box on a dark table, "
        "photographed from directly above in a tall frame so the box fills the middle and "
        "the table falls into blackness above and below. One narrow shaft of light crosses "
        "the envelope diagonally. Dark red wax seal, small unreadable writing.")),

    job("SB09_EMPTY_CHAIR_QUESTION.png", (
        "One plain wooden chair standing alone in a large empty room, photographed from a "
        "low angle in a tall frame so the chair sits in the lower third and the bare wall "
        "and high window rise above it. Cold daylight falls across the floor toward the "
        "chair. Nobody in frame.")),
]


def render(job_spec, outdir):
    """Reuse the episode generator's transport, which already resolves the
    secondary Vertex profile and retries. Rebuilding the token call here silently
    fell back to the default account and every request came back 401."""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT not set; start via run_with_vertex_secondary.ps1")
    url = ("https://aiplatform.googleapis.com/v1/projects/" + project +
           "/locations/" + LOCATION + "/publishers/google/models/" + MODEL +
           ":generateContent")
    payload = {"contents": [{"role": "user", "parts": [{"text": job_spec["text"]}]}],
               "generationConfig": {"responseModalities": ["IMAGE"],
                                    "imageConfig": {"aspectRatio": "9:16",
                                                    "imageSize": "2K"}}}
    resp = post_json(url, payload)
    for part in resp["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            data = base64.b64decode(part["inlineData"]["data"])
            (outdir / job_spec["name"]).write_bytes(data)
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
        print("GEN " + j["name"], flush=True)
        try:
            n = render(j, outdir)
            print(f"OK  {j['name']}  {n} bytes", flush=True)
        except Exception as exc:
            print("FAIL " + j["name"] + ": " + str(exc)[:300], flush=True)


if __name__ == "__main__":
    main()
