#!/usr/bin/env python3
"""Generate 96 native 9:16 stills for the six Schlafparalyse Shorts, V4.

Against the V2 asset set this changes three things:

* 16 motifs per Short instead of 7, so the beat-cut edit gets a genuinely new
  image on almost every cut rather than a re-framing of the same picture.
* A per-Short continuity clause. V2 changed protagonist almost every shot in
  SP06A and SP06B, which read as a stock-photo slideshow; V4 pins one cast and
  one location per Short.
* Explicit shot sizes in every scene (wide / medium / close / insert), so the
  edit has real grammar instead of seven equally framed tableaus.

The STYLE block is carried over unchanged from the V2 generator. It encodes the
failure modes that were paid for once already: rotated rooms, inset cards,
letterboxing, cropped heads, invented typography.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
MODEL = "gemini-3-pro-image"
GCLOUD = Path(r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")

STYLE = """Generate exactly one finished native vertical 9:16 documentary still in 2K.
This is a portrait composition created for a phone screen from the beginning, never a landscape image placed inside a portrait canvas. Fill the entire frame with real scene content from edge to edge. No black bars, no letterboxing, no picture-in-picture, no inset card, no blurred duplicate background, no split screen and no triptych.
NOESIS visual language: photorealistic investigative documentary, deep graphite shadows with visible detail, restrained tungsten practical light, cold moonlight where appropriate, realistic optics, subtle 35mm grain, sober and credible rather than sensational horror. One dominant visual idea that reads instantly on a phone. Keep the main subject and any head or hands inside the central safe 76 percent of the frame. Natural anatomy, complete heads, plausible hands and fingers, no duplicated limbs.
Absolutely no captions, labels, readable writing, pseudo-writing, numbers, logos, UI, watermarks or decorative typography. Avoid crushed blacks, glowing eyes, demons, gore, fantasy spectacle, Dutch angles, fisheye distortion and artificial horror poses.
Gravity must be correct and the camera must be level. The floor meets the bottom edge of the frame and the ceiling meets the top edge. Standing people have their heads toward the top of the frame; people lying in bed are shown either from directly above with the bed running top to bottom, or from the side with the mattress horizontal. Never rotate the room, never tip the horizon, never place a bed or a person sideways along the frame.
The picture is the scene itself, never a picture of a picture. Do not draw a phone, tablet, laptop, monitor, television, camera viewfinder, bezel, notch, device body, passepartout, poster, print, postcard, polaroid, window mullion or decorative border around the scene or around any part of it. No double exposure, no overlapping duplicate copies of the subject, no montage, no collage, no reflection that duplicates the whole frame."""

CAST = {
    "SP06A_ATEM":
        "Continuity: the same woman, early thirties, dark shoulder-length hair, plain charcoal long-sleeve shirt, no jewellery and no make-up. The same modest city bedroom at night with one window on the left, a low wooden nightstand and a warm bedside lamp, unless a scene explicitly names another room.",
    "SP06B_RUECKENLAGE":
        "Continuity: the same man, late twenties, short dark hair, light grey t-shirt. The same small attic bedroom with a sloped ceiling, one skylight and a plain wooden bed frame, unless a scene explicitly names another room.",
    "SP07A_ALBTRAUMWORT":
        "Continuity: the same bearded man, thirties, coarse undyed linen shirt, in the same historically plausible early medieval northern European timber sleeping room with a low wool-covered bed, one small shuttered window and a single candle, unless a scene explicitly names another room or period.",
    "SP07B_SALEM_ZEUGE":
        "Continuity: the same woman, thirties, plain dark colonial New England dress with a white linen coif, and the same 1692 colonial timber house interior with whitewashed plaster, a plank floor and a heavy panelled door, unless a scene explicitly names the courtroom.",
    "SP08A_HAT_MAN_HUT":
        "Continuity: the same man, thirties, dark work jacket and knitted cap, in the same plain apartment bedroom with a doorway to an unlit hallway, unless a scene explicitly names another room. The shadow figure is always an ordinary cast shadow with a brimmed-hat silhouette, never a rendered creature and never with visible eyes.",
    "SP08B_UNSICHTBARE_PERSON":
        "Continuity: the same woman, thirties, olive fleece pullover, in the same 2000s-era European neurological examination room with pale institutional walls, a bookshelf, a examination chair and one tall window, unless a scene explicitly names another room.",
}

SCENES = {
    "SP06A_ATEM": [
        "WIDE, overhead portrait view straight down onto the bed: she lies flat on her back at night, fully clothed above the covers, eyes wide open and completely still. Whole body from head to feet inside the frame, both hands visible beside her. Nothing else in the room moves.",
        "CLOSE, side view level with the pillow: her face in profile, eyes open, jaw tight, controlled fear rather than screaming. Warm lamp light on one cheek, cold window light on the other.",
        "INSERT, macro from low bedside height: only the blanket over her chest, a shallow but unmistakable rise. Shallow depth of field, the rest of the room falling into graphite darkness.",
        "MEDIUM, from the foot of the bed: the whole quiet room around her, curtain edge lifted slightly by moving air, lamp steady. She is small in frame and motionless.",
        "A classroom anatomical torso model made of painted plaster and resin, the kind used in biology teaching, standing UPRIGHT on a wooden table in a dim room and photographed straight on with a level camera. The chest is open to show the ribcage and the dome-shaped diaphragm muscle beneath the lungs, which catches a single warm practical light while the rest falls away into shadow. The model stands vertical on its base: not lying down, not tipped, not rotated. Real object photography with visible material texture, no arrows, no labels, no glow, no writing.",
        "INSERT, macro: her open hand lying on the sheet, fingers slack and completely still, skin texture and sheet weave sharp, the arm disappearing into darkness.",
        "CLOSE from above: her neck and one shoulder, muscles visibly slack, head tipped slightly back into the pillow, hair spread. Restraint, not distress.",
        "WIDE, sleep laboratory at night: the same woman lying calmly in a clinical bed with small non-invasive sensor pads on her temples and chest, cables tidy, no technician present, all monitor screens dark and blank.",
        "INSERT, macro against the dark window: the very edge of a curtain lifting and falling in a slow rhythm, backlit by cold moonlight. Proof that air is moving, no person in frame.",
        "MEDIUM, three-quarter from bedside: she is awake and frightened, chest visibly shallow, one hand half-curled. The bedside lamp throws a hard rim of light along her arm.",
        "CLOSE portrait of her face on the pillow seen from slightly above, filling the whole tall frame from forehead to chin: pupils wide, a first deliberate slow exhale beginning, fear starting to organise into concentration. Scene content reaches all four edges; no letterbox band, no dark strip along any edge, no cinematic crop bars.",
        "INSERT, extreme macro: one single fingertip against the dark sheet, sharply lit, everything else out of focus. The one small thing she can still control.",
        "CLOSE, side view: the same fingertip has moved a few millimetres, the hand no longer frozen, the sheet slightly disturbed around it.",
        "MEDIUM, from the doorway: she sits up on the edge of the bed in the blue-grey light before dawn, both feet on the floor, shoulders dropped, breathing normally.",
        "WIDE, morning: the same bedroom in flat daylight, curtains open, bed unmade but empty, everything ordinary and unthreatening. No person in frame.",
        "MEDIUM, daylight: the same woman stands at the window with a mug, calm and unremarkable, seen from behind and slightly to the side. Sober, everyday ending.",
    ],
    "SP06B_RUECKENLAGE": [
        "WIDE, overhead portrait view straight down onto the bed, the long axis of the bed running from the top of the frame to the bottom: he lies flat on his back, head in the upper third, feet toward the lower third, both hands visible. Moonlight from the skylight crosses him.",
        "CLOSE, from the pillow: his face from the side, awake, eyes open, completely still, one hand near his chest. Cold skylight above, no lamp.",
        "MEDIUM, side view of the whole bed at mattress height: supine posture readable, chin slightly raised, throat line exposed. Documentary distance, no medical labels.",
        "INSERT, macro: the hollow of his throat and the top of his chest, breathing shallow and audible in the image only through posture. Very shallow depth of field.",
        "WIDE, a plain room used as a physical study: eight identical small unmarked beds arranged in even rows seen from above, more of the miniature sleepers lying on their backs than on their sides. Real miniature-set photography, no percentages, no diagram, no writing.",
        "MEDIUM, the same attic bedroom empty at night: two soft translucent bands of moonlight overlap above the empty mattress. No person, no poster, no screen, no interface, walls vertical and floor at the bottom.",
        "INSERT, still life on the nightstand: an unmarked analog alarm clock with blank face, no readable numbers, beside a glass of water, lit only by the skylight.",
        "WIDE, the same man asleep at an obviously wrong hour: harsh afternoon light through the skylight, clothes still on, one shoe off, sleep taken at the wrong time rather than chosen.",
        "MEDIUM, an airport gate at night seen through glass: the same man asleep upright in a waiting chair, jacket as a pillow, no readable signage anywhere in frame.",
        "INSERT, macro: a packed travel bag half open on the floor of the attic room, moonlight across it, the bed unmade behind and out of focus.",
        "CLOSE from above: his face at the moment between sleeping and waking, eyelids moving, expression unresolved. Neither clearly asleep nor clearly awake.",
        "WIDE, overhead: the same man now sleeping comfortably on his side, knees slightly drawn, one hand under the pillow, complete head and hands visible, spine in a natural line.",
        "MEDIUM, side view: a supportive pillow placed deliberately behind his back to keep him off his spine, bedding tidy, a practical and unmagical arrangement.",
        "INSERT, macro: a hand switching off the bedside lamp, the room dropping to moonlight only, fingers anatomically clean.",
        "WIDE, early morning: the same attic room in flat grey daylight, bed slept in and empty, skylight showing pale sky. No person.",
        "MEDIUM, morning: the same man stands under the skylight stretching, unremarkable and rested, seen three-quarter from behind. Calm practical ending.",
    ],
    "SP07A_ALBTRAUMWORT": [
        "WIDE, camera standing at the foot of the bed at chest height and perfectly level, the plank floor along the bottom edge and the timber wall rising vertically behind: he lies on his back under a heavy wool blanket with his head on the pillow at the far end, feet toward the camera. A candle gutters on a low stool beside him and the small shuttered window is closed. Whole body in frame, complete head, both hands at his sides. The room is upright as a person standing in it would see it: the bed is never turned sideways along the frame and the camera is never rotated.",
        "CLOSE, from beside the bed: his face, eyes open, beard, the exact expression of someone awake who cannot move. Candlelight from below, no monster in frame.",
        "INSERT, macro: a dark human-shaped pressure impression sunk into the wool blanket over his chest, the weave compressed. Nothing above it, no creature, no boot.",
        "MEDIUM, from the foot of the bed: the whole room, and on the timber wall behind him an ambiguous human-shaped shadow that never resolves into a figure. Cast shadow only.",
        "CLOSE on his hands: fingers gripping the blanket edge, tendons visible, knuckles pale, the only sign of effort in an otherwise motionless body.",
        "MEDIUM, a modest carved wooden shelf beside the bed holding three small worn household figures of related night-visitor traditions, candlelit. No runes, no letters, no map, archaeological realism.",
        "INSERT, macro: a single small carved horse token lying on the plank floor, deliberately set aside and slightly out of the light. The blanket and the pressure shadow dominate behind it, out of focus.",
        "WIDE, a second historically plausible timber room in another house, same period: a different sleeper under the same kind of pressure shadow. The tradition is not one person's story.",
        "MEDIUM, a third variation, a low stone-walled room with a straw mattress, same motif of the ambiguous chest shadow. Same century, different place, same account.",
        "CLOSE, candle flame guttering as if something passed, held in sharp focus with the dark room behind. Restrained and physical, no supernatural glow.",
        "WIDE, an archive-like interior in one continuous photographic space: the old wool blanket and one carved token in the foreground on a table, and through an open doorway far behind, a plain modern bedroom lit by a phone screen. One room, no collage, no split screen.",
        "MEDIUM, the modern bedroom at night: a present-day sleeper on their back in the same posture as the medieval man, duvet instead of wool, streetlight instead of candle. The pose rhymes exactly.",
        "INSERT, macro on the modern duvet: the same human-shaped pressure impression over the chest, in modern bedding. The motif survives the change of century.",
        "CLOSE, the modern sleeper's face, eyes open, awake and unable to move, the same expression as the medieval close-up. Cold street light.",
        "MEDIUM, the modern bedroom window at night with a faint ambiguous reflection in the glass that only suggests the old shadow shape. Restrained, non-supernatural.",
        "WIDE, dawn in the modern bedroom, empty and ordinary, grey light, bed unmade. The word outlived the explanation. No person.",
    ],
    "SP07B_SALEM_ZEUGE": [
        "WIDE, camera standing beside the bed at chest height and perfectly level, the plank floor running along the bottom edge and the whitewashed wall rising vertically behind: she lies awake on the bed, fully dressed, her head on the pillow to the left and her body extending to the right, so the mattress sits horizontally across the lower half of the frame. Complete head and both hands visible. A faint ambiguous human-shaped patch of moonlight stands near the closed panelled door behind her. The room is upright as a person standing in it would see it: the bed is never turned to run up and down the frame and the camera is never rotated or placed on the ceiling.",
        "CLOSE, from the bedside: her face, eyes open and fixed on the door, coif framing her face, one candle low and guttering.",
        "INSERT, macro: the heavy iron latch of the door, firmly closed and undisturbed, dust motes in the moonlight. The door was locked.",
        "MEDIUM, the empty colonial bedroom photographed upright from the doorway: plank floor at the bottom, whitewashed wall rising, the corner of the bed entering only along the lower edge, faint human-shaped moonlight beside the door. No person, no writing, no frames on the wall.",
        "CLOSE, her hands gripping the edge of the bedding, knuckles pale, plain sleeves, no jewellery. Fear held still.",
        "MEDIUM, morning in the same house: she sits at a plain table telling a neighbour woman what happened, both fully clothed with complete heads and hands, blank paper untouched between them, hard daylight from a small window.",
        "WIDE, the meeting-house room used as a court: a magistrate at a raised desk, plain benches, tall windows, several plainly dressed colonial figures seated. Historically plausible 1692 New England clothing, no modern suits, no readable documents.",
        "MEDIUM, across the courtroom table: the magistrate leaning toward the witness, a lantern between them, both in period dress, complete heads and hands, the paper on the table entirely blank.",
        "CLOSE, the witness standing to speak, one hand raised, her face lit from a high window. Ordinary conviction rather than hysteria.",
        "INSERT, macro: a magistrate's hands placing a blank sheet beside a plain wax seal and an inkwell on the worn courtroom table. No text anywhere.",
        "MEDIUM, the accused woman standing alone before the bench in plain period dress, complete head and hands, back partly to camera, the room dim around her.",
        "INSERT, macro: a plain brass balance scale on the courtroom table, one pan holding a small wax seal, the other holding nothing at all. Candlelight, no writing.",
        "CLOSE, the magistrate's face in half shadow, considering, neither villain nor hero. Sober historical portraiture.",
        "MEDIUM, the courtroom benches from behind the last row: the assembled townspeople as a mass of dark period silhouettes facing the bench, faces indistinct, one high window pouring light.",
        "WIDE, the same courtroom completely empty afterwards, daylight flat and grey, one chair left out of place, the bench abandoned. No person.",
        "MEDIUM, the colonial bedroom by day, empty, the door standing open now, ordinary and unremarkable. The room where it started, drained of threat.",
    ],
    "SP08A_HAT_MAN_HUT": [
        "WIDE, the apartment bedroom at night from the foot of the bed: the man stands with his back to camera facing the unlit hallway doorway, and on the wall beside the doorway falls a tall shadow with a clear brimmed-hat silhouette. Cast shadow only, no rendered figure, no eyes.",
        "CLOSE, his face in profile lit only by the hallway light, looking toward the doorway, unsure rather than terrified.",
        "MEDIUM, the doorway itself: darkness beyond, and only a hat-brim silhouette suggested at the top of the frame by the way the light falls. Ambiguous by construction.",
        "INSERT, macro: a real felt hat hanging on a coat hook in the hall, ordinary and mundane, throwing a much larger shadow onto the wall behind it.",
        "WIDE, camera at mattress height beside the bed and perfectly level, the mattress running horizontally across the lower half of the frame and the wall rising vertically behind it: he lies on his back, awake, head on the pillow toward the left, and a tall hat-brimmed shadow falls on the upright wall in the far corner. Room upright, never seen from above, never rotated.",
        "CLOSE, a single portrait of his face on the pillow lit from one side, eyes open and fixed on something out of frame. One face only, filling the frame naturally, no reflection and no second image anywhere.",
        "MEDIUM, a bare concrete stairwell wall at night: a tall human shadow with a brimmed hat cast across it by a doorway behind, nobody visible casting it.",
        "INSERT, macro on a desk under a lamp: a plain shoebox and books arranged so their combined shadow accidentally forms a brimmed-hat silhouette on the wall. The brain's pattern completion, shown physically.",
        "MEDIUM, a formless dark column of shadow on a plain wall with no hat at all: shapeless, unreadable, not yet a person. The control image.",
        "MEDIUM, the same wall and the same column of shadow now with a brim added at the top: instantly a person, instantly facing a direction. Identical framing to the previous shot.",
        "WIDE, four hands of different people laying five plain unmarked photographic prints on a worn wooden table, each print showing the same brimmed-hat shadow silhouette. No writing, no numbers, no logos on the prints.",
        "MEDIUM, a home desk at night: a man at a microphone in front of a dark monitor, window streaked with rain, bookshelves behind. All screens off and blank, no readable interface.",
        "INSERT, macro: a rain-streaked dark window at night in which several overlapping faint reflections of the same hat silhouette repeat. Repetition as the point.",
        "MEDIUM, a plain wall with the same hat silhouette repeated four times at slightly different scales by overlapping light sources. Physical light effect, not a graphic.",
        "WIDE, the bedroom at dawn, empty, the coat and hat on the hook throwing an entirely ordinary small shadow. The figure dissolved into furniture. No person.",
        "MEDIUM, the same man sitting on the edge of his bed in flat morning light, looking at the hallway doorway, which is now simply a doorway. Calm, unresolved, honest ending.",
    ],
    "SP08B_UNSICHTBARE_PERSON": [
        "WIDE, the neurological examination room: she sits upright in the examination chair, fully clothed, hands in her lap, small non-invasive electrode pads at her left temple, complete head above torso and feet on the floor. Institutional daylight, all screens dark and blank.",
        "CLOSE, her face three-quarter: calm, attentive, mid-examination, a faint blue indicator light from equipment out of frame catching one side.",
        "MEDIUM, from behind and slightly above her chair: the empty pale wall behind her, nothing there, the room quiet. The absence before the effect.",
        "MEDIUM, identical framing to the previous shot, now with a soft second human-shaped shadow on the wall directly behind her chair. Cast shadow only, no rendered person.",
        "CLOSE, her face turning slightly as if to look over her shoulder, expression puzzled rather than frightened.",
        "WIDE, the same room: she sits with her right hand raised, and the shadow behind her holds the same posture exactly, mirrored. Anatomically consistent, no glow.",
        "CLOSE on her raised hand alone against the pale wall, and the shadow hand behind it in the same position. The copy is the point.",
        "A classroom anatomical model of a human head made of painted plaster, the kind used in biology teaching, standing UPRIGHT on its base on a dark table and photographed from the left side with a level camera. One quarter of the skull is cut away to show the brain beneath, and the area just above and behind the ear catches a single warm practical light while the rest falls into shadow. This is an inanimate teaching model on a table, not a living person: no real face, no skin, no clothing, no hair, nobody from the previous scenes. Real object photography with visible plaster texture, no labels, no arrows, no glow.",
        "INSERT, macro: three thin electrode cables running to a plain unmarked grey instrument box, indicator lights small and dim, no readable display.",
        "MEDIUM, a laboratory bench with an articulated wooden anatomical mannequin standing under a work lamp, its shadow on the wall much more human than the mannequin itself.",
        "CLOSE, the mannequin's blank wooden face beside its own convincing shadow, shallow depth of field. What the brain fills in.",
        "MEDIUM, the same woman seated, now with two overlapping shadows behind her at slightly different angles, both matching her posture. Two body models, one body.",
        "CLOSE, her face lit from one side, listening to something behind her that is not there, eyes not focused on anything in frame.",
        "WIDE, the examination room from the doorway: she sits alone, the wall behind her now entirely plain, the effect switched off. Same framing as the beginning.",
        "MEDIUM, the empty examination chair after the session, a soft remaining shadow on the wall that is no longer person-shaped, equipment dark. No person.",
        "WIDE, a plain hospital corridor with one figure walking away from camera into flat daylight, complete body, unremarkable. Open ending, no threat.",
    ],
}


class Pacer:
    """Serialise request starts.

    Measured on this project: firing six requests at once returns 429 for five
    of them within 0.2 s and completes exactly one in 38 s. The per-project
    image quota allows a single concurrent generation, so any parallelism buys
    nothing and only burns the retry budget. Run with --workers 1; the lock is
    kept so a higher worker count degrades to serial instead of to 429 storms.
    """

    def __init__(self, gap: float) -> None:
        self.gap = gap
        self.lock = threading.Lock()

    def __enter__(self) -> "Pacer":
        self.lock.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        if self.gap:
            time.sleep(self.gap)
        self.lock.release()


# A short cooldown after every request. The limit is not purely a concurrency
# cap: even a strictly serial run collects the occasional 429, so the quota has
# a time component too. Waiting a few seconds between generations is far cheaper
# than exhausting a retry budget.
PACER = Pacer(8.0)


def token() -> str:
    result = subprocess.run(
        [str(GCLOUD), "auth", "application-default", "print-access-token"],
        check=True, capture_output=True, text=True, timeout=90,
    )
    return result.stdout.strip()


class Token:
    """Refreshable access token.

    gcloud application-default tokens expire after about an hour. A full run of
    96 images at roughly 90 s each takes longer than that, so fetching once at
    startup makes every request after the expiry fail with 401 — which is how
    the first full run lost its last twenty images.
    """

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.value = token()
        self.stamp = time.monotonic()

    def get(self) -> str:
        with self.lock:
            # Refresh well before the hour is up rather than waiting for a 401.
            if time.monotonic() - self.stamp > 1800:
                self.value, self.stamp = token(), time.monotonic()
            return self.value

    def refresh(self) -> str:
        with self.lock:
            self.value, self.stamp = token(), time.monotonic()
            return self.value


def jobs() -> list[dict]:
    return [
        {"job": short, "number": index, "name": "%s_%02d" % (short, index), "prompt": prompt}
        for short, prompts in SCENES.items()
        for index, prompt in enumerate(prompts, 1)
    ]


def endpoint(project: str) -> str:
    return (
        "https://aiplatform.googleapis.com/v1/projects/%s/locations/global/"
        "publishers/google/models/%s:generateContent" % (project, MODEL)
    )


def generate(item: dict, project: str, access: "Token", overwrite: bool) -> tuple[str, str]:
    out_dir = PROD / item["job"] / "assets_v4"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / ("SHOT%02d.png" % item["number"])
    if target.is_file() and not overwrite:
        with Image.open(target) as image:
            return item["name"], "skip %dx%d" % (image.width, image.height)
    prompt = STYLE + "\n\n" + CAST[item["job"]] + "\n\nScene: " + item["prompt"]
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "candidateCount": 1,
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "9:16", "imageSize": "2K"},
        },
    }
    data = json.dumps(payload).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(1, 13):
        try:
            with PACER:
                request = urllib.request.Request(
                    endpoint(project), data=data,
                    headers={"Authorization": "Bearer " + access.get(),
                             "Content-Type": "application/json"},
                )
                response = json.load(urllib.request.urlopen(request, timeout=420))
            parts = response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            inline = next(
                (part.get("inlineData") or part.get("inline_data")
                 for part in parts if part.get("inlineData") or part.get("inline_data")),
                None,
            )
            if not inline or not inline.get("data"):
                raise RuntimeError("no image data returned")
            target.write_bytes(base64.b64decode(inline["data"]))
            with Image.open(target) as image:
                width, height = image.size
                image.verify()
            if height <= width:
                raise RuntimeError("not portrait: %dx%d" % (width, height))
            return item["name"], "ok %dx%d" % (width, height)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 401:
                # Expired token, not a rejected prompt: mint a new one and retry.
                access.refresh()
                continue
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 403:
                break
            # 429 is the shared per-project image quota, not a bad prompt, so it
            # is worth waiting out properly instead of burning the retry budget.
            # A 429 comes back in a fraction of a second and just means another
            # generation is in flight, so a short wait is enough.
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                time.sleep(min(30, 6 * attempt))
            else:
                time.sleep(min(30, 3 * attempt))
    return item["name"], "FAILED %s" % last_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="substring filter")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    selected = [item for item in jobs() if not args.only or args.only in item["name"]]
    if not selected:
        raise SystemExit("No matching jobs")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    access = Token()
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(generate, item, project, access, args.overwrite) for item in selected]
        for count, future in enumerate(as_completed(futures), 1):
            name, status = future.result()
            print("[%02d/%02d] %-24s %s" % (count, len(selected), status, name), flush=True)
            if status.startswith("FAILED"):
                failures.append((name, status))
    if failures:
        print("FAILURES: %d" % len(failures), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
