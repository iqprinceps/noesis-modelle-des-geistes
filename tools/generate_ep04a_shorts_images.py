#!/usr/bin/env python3
"""Fehlende 9:16-Bilder fuer die EP04A-Shorts mit NanoBanana Pro erzeugen.

Nutzt dasselbe Modell und dieselbe Rollenlogik wie der Serien-Generator, aber
vertikal und mit einem festen Identitaetsanker, damit Jung ueber alle drei
Shorts hinweg dasselbe Gesicht behaelt.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SHORTS = ROOT / "06_PRODUCTION" / "JUNG_SERIES_V1" / "SHORTS_EP04A"
OUT = SHORTS / "images" / "generated"
REFS = SHORTS / "images" / "refs"
MODEL = "gemini-3-pro-image"

LOCK = """Generate exactly one finished vertical 9:16 documentary still, 2K.
Restrained palette, natural lifted midtones, visible shadow detail, documentary
lighting, subtle film grain. Composition must read on a phone: one clear subject,
generous headroom, nothing important in the outer 12 percent on any edge.
Absolutely no text, no lettering, no captions, no watermarks, no logos, no
pseudo-readable script anywhere in the frame. No glowing auras, no magical energy,
no fantasy spectacle, no modern objects in historical scenes."""

IDENTITY = ("Image {n} ({name}) is the identity reference for the recurring scholar. "
            "Preserve the same adult male facial identity, hair and moustache across "
            "all images. Do not copy its pose, framing or background.")
STYLE = ("Image {n} ({name}) is a style reference only. Match its restrained palette, "
         "documentary lighting and texture. Do not copy its people or composition.")
FACT = ("Image {n} ({name}) is a factual historical reference. Use only as requested; "
        "do not redraw, rewrite or beautify its content.")

JOBS = [
    # ---- SHORT 1 -------------------------------------------------------
    dict(name="S1_03_rote_sonne_unter_wasser", refs=["STYLE_CAVE.png"],
         prompt="Looking down into very dark still water inside a cave. Deep beneath the "
                "surface a dull red disc glows, distorted by the water, impossible and calm. "
                "Wet black rock at the edges. No figures. Vertical composition, the red disc "
                "sitting slightly below centre."),
    dict(name="S1_05_notizbuch_1913", refs=["STYLE_DESK.png"],
         prompt="An open notebook from around 1913 on a dark wooden desk at night, dense "
                "handwritten cursive filling both pages in brown ink, a fountain pen resting "
                "across the gutter, one small oil lamp just out of frame casting warm light "
                "from the upper left. Shot from directly above, vertical framing. The writing "
                "must be an unreadable natural cursive texture, never legible words."),
    dict(name="S1_06_jung_schreibt_nacht", refs=["IDENT_JUNG.png", "STYLE_DESK.png"],
         prompt="The scholar in a dark three-piece suit sits at a desk at night, seen from a "
                "low three-quarter angle, writing into a large notebook. He is absorbed, not "
                "posing, head lowered. A single desk lamp lights his hands and the page; the "
                "room behind falls into darkness. Vertical framing with the lamp glow in the "
                "lower third and dark wall above."),
    dict(name="S1_08_schlange_am_fuss_der_tafel", refs=["STYLE_CAVE.png"],
         prompt="Extreme close view of the lower edge of an old Indian painted chakra scroll "
                "lying on dark cloth: at the base of the diagram a small coiled serpent is "
                "painted, faded pigment, visible paper fibre and age. Shallow depth of field, "
                "the coil sharp, the rest of the scroll falling out of focus upward. Vertical "
                "framing. No readable script."),
    dict(name="S1_09_jung_warnt_seminar", refs=["IDENT_JUNG.png", "STYLE_SEMINAR.png"],
         prompt="The scholar stands in a wood-panelled 1930s seminar room addressing a seated "
                "audience, seen slightly from behind and to the side of one listener's shoulder "
                "so his face is visible but not centred like a portrait. He is mid-sentence, "
                "serious, one hand raised low in a restraining gesture. Tall windows behind him. "
                "Vertical framing."),
    dict(name="S1_12_schlange_und_karte", refs=["STYLE_CAVE.png"],
         prompt="A dark tabletop seen from directly above, vertical framing. On the lower half "
                "lies a coiled black snake on wet slate; on the upper half lies an old painted "
                "Indian scroll showing a seated figure with stacked lotus symbols. Between them "
                "a hand's width of empty dark wood. Even, cold documentary light. No text."),
    # ---- SHORT 2 -------------------------------------------------------
    dict(name="S2_06_klinik_innen", refs=["STYLE_DESK.png"],
         prompt="An empty corridor inside a Swiss psychiatric clinic around 1910: pale green "
                "tiled walls, worn linoleum, tall windows on one side throwing long cold light "
                "across the floor, a row of closed wooden doors receding into depth. No people. "
                "Vertical framing, the vanishing point slightly above centre."),
    dict(name="S2_09_geht_wieder_hinein", refs=["IDENT_JUNG.png", "STYLE_DESK.png"],
         prompt="The scholar seen from behind, in shirtsleeves and waistcoat, standing at the "
                "threshold of a dark doorway in his study at night, one hand on the frame, "
                "about to step into the darkness beyond. His face is not visible. Warm lamplight "
                "behind him, the doorway ahead almost black. Vertical framing."),
    # ---- SHORT 3 -------------------------------------------------------
    dict(name="S3_10_da_ist_wut", refs=["STYLE_CAVE.png"],
         prompt="A single candle flame on a dark table, photographed very close, the flame "
                "perfectly still and upright, deep black surrounding it, a faint warm pool of "
                "light on the wood below. Nothing else in frame. Vertical composition with the "
                "flame in the upper third."),
    dict(name="S3_12_karte_des_bewusstseins", refs=["FACT_PLATE.jpg", "STYLE_SEMINAR.png"],
         prompt="An old Indian painted chakra scroll pinned to a plain plastered wall in a "
                "1930s study, lit from one side by a desk lamp so the paper texture and pigment "
                "read clearly, deep shadow to the right. Photographed straight on, slightly from "
                "below. Vertical framing. The scroll is the factual reference; reproduce its "
                "character, do not invent readable script."),

    # ---- Nachschlag: fehlende Beats, damit keine Wiederholung noetig wird ----
    dict(name="S1_04_gestalten_im_gang", refs=["STYLE_CAVE.png"],
         prompt="Two indistinct human figures standing far back in a narrow rock passage, lit "
                "only by a faint warm glow behind them so they read as silhouettes with no "
                "discernible faces. Wet dark stone walls close on both sides. Vertical framing, "
                "the figures small in the upper middle, deep foreground shadow."),
    dict(name="S2_03_truemmer_im_wasser", refs=["STYLE_CAVE.png"],
         prompt="Storm-grey floodwater filling a valley, seen from a low hillside: broken roof "
                "beams, a cartwheel, a shutter and splintered planks drifting in the current. "
                "Heavy overcast sky. No people, no bodies. Vertical framing with the horizon "
                "high and the debris filling the lower two thirds."),
    dict(name="S2_04_leeres_abteil", refs=["STYLE_DESK.png"],
         prompt="The interior of an empty first-class railway compartment around 1913: buttoned "
                "cloth seats, a folded newspaper left behind, cold daylight through the window, "
                "the landscape outside reduced to a pale blur. Nobody in frame. Vertical framing "
                "shot along the seats."),
    dict(name="S2_08_klinik_akte", refs=["STYLE_DESK.png"],
         prompt="A physician's desk in a psychiatric clinic around 1910: a stack of case files "
                "tied with cotton tape, a brass inkwell, a stethoscope laid across the papers, "
                "cold window light from the left. Shot from a steep angle above. Vertical framing. "
                "Any writing on the files must be unreadable cursive texture."),
    dict(name="S2_12_die_gefaehrliche_frage", refs=["IDENT_JUNG.png", "STYLE_DESK.png"],
         prompt="The scholar sits motionless in a wing chair in a dark study, hands loosely "
                "folded, staring past the camera, not at it. Late evening light from one window "
                "falls across half his face. He looks like a man working something out that he "
                "does not like. Vertical framing, generous dark space above his head."),
    dict(name="S3_02_display_nur_ein_name", refs=["STYLE_DESK.png"],
         prompt="Very close view of a modern smartphone lying face up on a dark wooden table in "
                "a dim room, its screen the only light source, showing an abstract message "
                "bubble shape with no readable text at all. A hand is just entering frame from "
                "the right. Vertical framing, screen glow in the lower half."),
    dict(name="S3_05_kiefer_spannt", refs=["STYLE_DESK.png"],
         prompt="Tight side view of an adult jawline and neck in low warm light, the jaw muscle "
                "visibly tensed, the rest of the face out of frame above. Dark background. "
                "Vertical framing, skin texture and a faint sheen readable."),
    dict(name="S3_08_zwei_sekunden", refs=["STYLE_DESK.png"],
         prompt="A hand resting flat and completely still beside a face-down smartphone on a "
                "dark table, fingers relaxed rather than gripping. One soft warm light from the "
                "left. Vertical framing with a lot of empty dark table below the hand."),
    dict(name="S1_13_mann_vor_der_karte", refs=["IDENT_JUNG.png", "STYLE_SEMINAR.png"],
         prompt="The scholar seen from behind and slightly below, standing alone in a dim study "
                "facing a large old Indian painted scroll that hangs on the wall in front of him. "
                "His hands are at his sides. Only the edge of his profile catches the lamplight. "
                "The scroll is soft and out of focus. Vertical framing, his shoulders filling the "
                "lower third, dark wall above. No readable script."),
    dict(name="S3_11_ich_bin_diese_wut", refs=["STYLE_CAVE.png"],
         prompt="A dark room at night seen from a low angle: an open window, a thin curtain "
                "lifting in a draught, cold blue city light outside, warm lamplight inside. "
                "Nobody in frame. The image should feel like a held breath. Vertical framing."),
]


def token() -> str:
    gcloud = os.environ.get("GCLOUD_CMD", "gcloud")
    r = subprocess.run([gcloud, "auth", "application-default", "print-access-token"],
                       capture_output=True, text=True, shell=True, timeout=90)
    value = (r.stdout or "").strip()
    if not value:
        raise SystemExit("Kein ADC-Token. gcloud auth application-default login")
    return value


def role(name: str, n: int) -> str:
    if name.startswith("IDENT_"):
        return IDENTITY.format(n=n, name=name)
    if name.startswith("STYLE_"):
        return STYLE.format(n=n, name=name)
    return FACT.format(n=n, name=name)


def parts(job: dict) -> list[dict]:
    out, roles = [], []
    for i, name in enumerate(job["refs"], start=1):
        p = REFS / name
        if not p.is_file():
            raise SystemExit(f"Referenz fehlt: {p}")
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        out.append({"inlineData": {"mimeType": mime,
                                   "data": base64.b64encode(p.read_bytes()).decode()}})
        roles.append(role(name, i))
    out.append({"text": "\n".join([LOCK, *roles, "Scene: " + job["prompt"]])})
    return out


def generate(job: dict, tok: str, overwrite: bool) -> tuple[str, str]:
    target = OUT / f"{job['name']}.png"
    if target.is_file() and not overwrite:
        return job["name"], "skip"
    proj = os.environ["GOOGLE_CLOUD_PROJECT"]
    loc = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    url = (f"https://aiplatform.googleapis.com/v1/projects/{proj}/locations/{loc}"
           f"/publishers/google/models/{MODEL}:generateContent")
    body = {"contents": [{"role": "user", "parts": parts(job)}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"aspectRatio": "9:16", "imageSize": "2K"}}}
    data = json.dumps(body).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": "Bearer " + tok, "Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=420))
            img = [p for p in r["candidates"][0]["content"]["parts"] if "inlineData" in p]
            if not img:
                raise RuntimeError("keine Bilddaten in der Antwort")
            target.write_bytes(base64.b64decode(img[0]["inlineData"]["data"]))
            with Image.open(target) as im:
                size = im.size
            return job["name"], f"ok {size[0]}x{size[1]}"
        except Exception as exc:  # noqa: BLE001
            if attempt == 5:
                return job["name"], f"FEHLER {str(exc)[:120]}"
            time.sleep(min(2 ** attempt, 30))
    return job["name"], "FEHLER"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--only", help="Teilstring-Filter auf den Jobnamen")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [j for j in JOBS if not args.only or args.only in j["name"]]
    tok = token()
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(generate, j, tok, args.overwrite) for j in jobs]
        for f in as_completed(futs):
            name, status = f.result()
            done += 1
            print(f"[{done:02d}/{len(jobs):02d}] {status:16s} {name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
