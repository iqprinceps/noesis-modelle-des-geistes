#!/usr/bin/env python3
"""Generate 42 native 9:16 stills for the six Schlafparalyse Shorts."""
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
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
MODEL = "gemini-3-pro-image"
GCLOUD = Path(r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")

STYLE = """Generate exactly one finished native vertical 9:16 documentary still in 2K.
This is a portrait composition created for a phone screen from the beginning, never a landscape image placed inside a portrait canvas. Fill the entire frame with real scene content from edge to edge. No black bars, no letterboxing, no picture-in-picture, no inset card, no blurred duplicate background, no split screen and no triptych.
NOESIS visual language: photorealistic investigative documentary, deep graphite shadows with visible detail, restrained tungsten practical light, cold moonlight where appropriate, realistic optics, subtle 35mm grain, sober and credible rather than sensational horror. One dominant visual idea that reads instantly on a phone. Keep the main subject and any head or hands inside the central safe 76 percent of the frame. Natural anatomy, complete heads, plausible hands and fingers, no duplicated limbs.
Absolutely no captions, labels, readable writing, pseudo-writing, numbers, logos, UI, watermarks or decorative typography. Avoid crushed blacks, glowing eyes, demons, gore, fantasy spectacle, Dutch angles, fisheye distortion and artificial horror poses."""

SCENES = {
    "SP06A_ATEM": [
        "Night bedroom, overhead portrait view of a fully clothed adult lying on the back, awake but unable to move; subtle tension in the chest while a curtain edge and a small breath condensation cue show air is still moving; complete head and both hands visible, no attacker.",
        "Intimate three-quarter portrait view from bedside level: fully clothed adult during sleep paralysis, chest rises slightly under the blanket, face frightened but not screaming; a warm bedside lamp and cold moonlight reveal the breathing rhythm, complete head and one relaxed hand visible.",
        "Upright front-facing scientific portrait in an upright clinical room: a standing neutral anatomical torso from head to hips, with lungs and diaphragm visible through a restrained translucent overlay. Camera held normally upright, ceiling at top and floor at bottom, body vertical, never sideways or rotated. No labels or arrows, realistic proportions.",
        "Vertical sleep-laboratory scene: fully clothed adult resting with external noninvasive sensors while posture muscles are visually quiet and the diaphragm remains the clear active center; technician absent, complete head and hands, no readable monitor interface.",
        "A real upright studio portrait with floor clearly at the bottom and wall vertical: fully clothed adult seated normally on a chair, head above torso, feet below, hands resting naturally. A subtle continuous ribbon follows the chest's breathing path while soft panic ripples remain on the wall behind. No rotation, no sideways room, no mystical aura.",
        "Close but complete portrait composition of a fully clothed adult in bed deliberately focusing on one visible fingertip while slowly exhaling; head intact in the upper third, hand anatomically correct in the lower third, tension beginning to release.",
        "Quiet dawn bedroom after the episode: same fully clothed adult sitting safely on the edge of the bed, breathing normally, both feet grounded and hands resting naturally, full head visible, early grey-blue light, calm evidence-based ending.",
    ],
    "SP06B_RUECKENLAGE": [
        "True vertical overhead bedroom composition with the long axis of the bed running from the top of the portrait frame to the bottom. A fully clothed adult lies flat on the back in the same vertical direction: complete head near the upper third, feet toward the lower third, both hands visible and natural. The viewer never needs to rotate the phone. Moonlight crosses the bed, no shadow figure, no writing or screen content.",
        "Portrait side view of a complete bed and sleeper in supine position, shoulders and airway alignment readable without medical labels; restrained moonlight, realistic bedding, full head and hands, no distress spectacle.",
        "Text-free documentary visualization of many small neutral bed silhouettes arranged vertically, with more sleepers shown on their backs than on their sides; physical miniature-set realism, no percentages, labels or diagrams, mobile-readable composition.",
        "Vertical still life about unstable sleep timing: unmarked analog clock, crescent moon through a window, packed travel bag and rumpled bed connected naturally in one real room; no numbers or writing, no floating infographic objects.",
        "An empty real bedroom photographed upright with a level camera: the floor is visibly along the bottom edge, the ceiling is visibly at the top, and one unoccupied horizontal bed is centered. Two soft translucent vertical bands of moonlight overlap above the mattress to suggest REM sleep and waking briefly overlapping. No person, posters, frames, books, writing, phone, screen, interface, inset, border or picture-in-picture. Normal gravity and vertical walls.",
        "True vertical overhead view of the same fully clothed adult sleeping comfortably on the side, complete head and both hands visible near the pillow, natural spine position, warm-cool balanced bedroom light.",
        "Morning routine in a real bedroom: adult opens curtains after a full night's sleep, bed behind prepared for side sleeping with a supportive pillow, complete body and head, calm practical mood, no clocks with readable numbers.",
    ],
    "SP07A_ALBTRAUMWORT": [
        "Historically plausible early medieval northern European timber bedroom at night, true portrait composition; fully clothed adult sleeper from head to feet, subtle dark pressure impression on the blanket, candlelight and moonlight, complete head and hands, no monster.",
        "Upright early-medieval bedroom with gravity correct, floor at bottom, ceiling at top and bed horizontal across the lower half. A dark footprint-like pressure impression appears on the wool blanket above the sleeper's chest; complete face and one hand visible. Camera level, never rotated or sideways, no giant boot, no creature.",
        "A portrait-oriented old northern European room containing three modest carved household tokens suggesting related night-visitor traditions, arranged on a wooden shelf beside a bed; no letters, runes or maps, candlelit archaeological realism.",
        "Historically plausible bedside scene with a small carved horse token deliberately set aside on the floor while the real focus is an ambiguous human-shaped night pressure shadow across the blanket; complete sleeper head and hands, no crossed-out graphic.",
        "Sober medieval reconstruction of a fully clothed sleeper awake beneath a dark human-sized pressure shadow that never resolves into a creature; timber walls, moonlit window, complete anatomy, documentary distance.",
        "Vertical generational transition in one physical archive room: an old wool blanket and carved night-visitor token in the foreground, a modern bedroom visible through an open doorway behind; no collage, no text, one continuous photographic space.",
        "Modern bedroom at night, fully clothed adult asleep with a soft dream-cloud reflection in the window containing only the old shadow-pressure motif; true vertical frame filled by the room, complete head and hands, restrained and non-supernatural.",
    ],
    "SP07B_SALEM_ZEUGE": [
        "Salem 1692 colonial bedroom photographed upright with floor at bottom, ceiling at top, vertical door and horizontal bed. Fully clothed adult woman lies naturally across the bed, awake, with complete head and hands; locked wooden door visible behind and a faint human-shaped light near it. Never rotate the room or camera.",
        "Empty Salem-era colonial bedroom photographed upright with a level camera. Wooden floorboards run across the bottom, vertical walls rise upward, and the ceiling is at the top. A tall vertical wooden door with a simple iron latch is firmly closed in the center; the corner of a horizontal bed enters only along the lower edge. Faint ambiguous human-shaped moonlight falls beside the door. No person, furniture on walls, writing, papers, frames, posters, labels or rotated room.",
        "Historically plausible colonial witness speaking quietly to a magistrate across a wooden table, both adults fully clothed with complete heads and hands, blank paper between them, vertical courtroom composition, no readable writing.",
        "Portrait close-up of complete magistrate hands placing a blank testimony sheet beside a plain wax seal on a courtroom table; witness and court blurred vertically behind, no text, no fake archive content.",
        "Salem-era colonial courtroom in true vertical framing, a fully clothed accused adult woman standing before seated magistrates, all visible heads complete, restrained faces, no execution imagery, no occult symbols.",
        "Physical brass evidence scale in a true vertical Salem-era colonial courtroom, one side holding a plain cracked wax seal and the other side empty. Behind it are only empty rough wooden benches, timber walls and simple period candle lamps. No people, suits, modern furniture, text or documents; clear private-experience-versus-public-proof metaphor.",
        "Empty colonial courtroom after proceedings, tall portrait perspective toward a single witness chair and closed door, morning light revealing dust, no people and no documents with writing, sober historical ending.",
    ],
    "SP08A_HAT_MAN_HUT": [
        "True vertical modern bedroom doorway at night; a vague tall shadow column stands in the door while a separate simple brimmed-hat shadow falls on the adjacent wall, fully clothed adult observer seen safely from behind with complete head and hands, no face in shadow.",
        "Portrait bedside viewpoint of a dark doorway where the ambiguous column and detached brimmed-hat shape nearly align; complete adult hand visible on the blanket foreground, no glowing eyes, no monster, realistic low light.",
        "Vertical conceptual reconstruction of the brimmed-hat shadow settling onto the top of the vague column, making it instantly readable as a person; one continuous physical wall and doorway, no split screen, no UI or labels.",
        "Text-free perception experiment as a real studio set: simple geometric shadow edges cast by ordinary household objects combine into a recognizable hat-wearing silhouette on a tall wall; portrait framing, practical lights visible, no supernatural claim.",
        "Several complete anatomically correct hands pass blank physical photo cards vertically down a table, each card showing only the same simple hat-shadow silhouette; no writing, no interfaces, tactile documentary realism.",
        "Portrait media room with unmarked podcast microphone, blank phone screen and dark monitor, the hat-shadow silhouette repeated only as reflected shapes in the glass; no text, logos or readable UI, complete seated listener head and hands.",
        "Quiet vertical bedroom at dawn where the hat-like shadow dissolves naturally back into the geometry of a coat rack and doorframe; no person in the shadow, full scene content edge to edge, evidence-boundary ending.",
    ],
    "SP08B_UNSICHTBARE_PERSON": [
        "Mid-2000s neurological evaluation room in true vertical framing, fully clothed adult female patient seated safely, complete head and both hands, small noninvasive conceptual light marker near the left temporoparietal side, soft human-shaped shadow immediately behind.",
        "Portrait side view of the same fully clothed patient and chair, a second translucent body outline directly behind copying her seated posture; complete head and hands, sober clinical reconstruction, no needles or surgery.",
        "Upright clinical portrait with floor at bottom and ceiling at top: fully clothed female patient sits normally vertical in a chair, complete face in upper third and both hands visible. One hand lifts slightly; a soft shadow-double on the wall mirrors the same hand position. Camera level, no rotation, no sideways room.",
        "Text-free scientific portrait visualization of a complete neutral human body with three subtle spatial rings around torso and head, a second body outline offset behind by a few centimeters; dark clinical space, no equations or labels.",
        "A physical anatomical mannequin in a vertical laboratory room casts two slightly misaligned but plausible human shadows, illustrating body-space-self mismatch; no people, no text, stable realistic geometry.",
        "Upright clinical room with floor down, ceiling up and camera level. Fully clothed female patient sits normally vertical in a chair, complete head above torso, feet below and hands natural. A second translucent body outline directly behind aligns and merges back into her posture. Never sideways or rotated, no mystical glow.",
        "Empty neurological evaluation chair in a tall quiet clinic room after the test, soft remaining shadow on the wall no longer person-shaped, equipment screens dark and blank, no text, sober open-question ending.",
    ],
}


def token() -> str:
    result = subprocess.run(
        [str(GCLOUD), "auth", "application-default", "print-access-token"],
        check=True, capture_output=True, text=True, timeout=90,
    )
    return result.stdout.strip()


def jobs() -> list[dict]:
    return [
        {"job": short, "number": index, "name": f"{short}_{index:02d}", "prompt": prompt}
        for short, prompts in SCENES.items()
        for index, prompt in enumerate(prompts, 1)
    ]


def endpoint(project: str) -> str:
    return (
        f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/"
        f"publishers/google/models/{MODEL}:generateContent"
    )


def generate(item: dict, project: str, access: str, overwrite: bool) -> tuple[str, str]:
    out_dir = PROD / item["job"] / "assets_vertical_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"SHOT{item['number']:02d}.png"
    if target.is_file() and not overwrite:
        with Image.open(target) as image:
            return item["name"], f"skip {image.width}x{image.height}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": STYLE + "\n\nScene: " + item["prompt"]}]}],
        "generationConfig": {
            "candidateCount": 1,
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "9:16", "imageSize": "2K"},
        },
    }
    data = json.dumps(payload).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            request = urllib.request.Request(
                endpoint(project), data=data,
                headers={"Authorization": "Bearer " + access, "Content-Type": "application/json"},
            )
            response = json.load(urllib.request.urlopen(request, timeout=420))
            parts = response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            inline = next((part.get("inlineData") or part.get("inline_data") for part in parts if part.get("inlineData") or part.get("inline_data")), None)
            if not inline or not inline.get("data"):
                raise RuntimeError("no image data returned")
            target.write_bytes(base64.b64decode(inline["data"]))
            with Image.open(target) as image:
                width, height = image.size
                image.verify()
            if height <= width:
                raise RuntimeError(f"not portrait: {width}x{height}")
            return item["name"], f"ok {width}x{height}"
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code in {401, 403}:
                break
            time.sleep(min(30, 3 * attempt))
    return item["name"], f"FAILED {last_error}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="substring filter")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    selected = [item for item in jobs() if not args.only or args.only in item["name"]]
    if not selected:
        raise SystemExit("No matching jobs")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    access = token()
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(generate, item, project, access, args.overwrite) for item in selected]
        for count, future in enumerate(as_completed(futures), 1):
            name, status = future.result()
            print(f"[{count:02d}/{len(selected):02d}] {status:24s} {name}", flush=True)
            if status.startswith("FAILED"):
                failures.append((name, status))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
