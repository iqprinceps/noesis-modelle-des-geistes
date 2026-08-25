#!/usr/bin/env python3
"""Generate the eight targeted EP08 diversity replacements through Vertex Nano Banana Pro."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import time
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT"
MODEL = "gemini-3-pro-image"

JOBS = {
    "IMG003_SHADOW_DOORWAY_GENERIC.png": """A luminous conceptual documentary still about a recurring nocturnal intruder archetype before it has a name: a vast museum-like archive corridor seen straight on, hundreds of translucent human recollection fragments suspended in layers like glass negatives, their unrelated dark vertical gaps loosely aligning into one ambiguous doorway-shaped absence at the center. No literal person, no bedroom, no ghost. The central absence should feel discovered by pattern recognition, not supernatural. Cool indigo archive depth balanced by warm amber practical pools and pearl highlights, clear readable midtones, subtle grain, tactile glass and paper, sophisticated poetic realism, 16:9.""",
    "IMG007_NAME_STABILIZES_SHAPE.png": """Conceptual documentary image of language stabilizing an ambiguous perception: many soft charcoal smudges, radio-wave traces and forum-thumbnail rectangles orbit through a bright archival signal chamber; as they move toward the center they gradually align into a crisp but purely geometric hat-and-shoulder negative-space icon made only from intersecting light planes. No literal man, no bedroom, no readable words or invented symbols. Elegant cyan, ivory and amber light, mystic but analytical, generous shadow detail, high visual depth, 16:9.""",
    "IMG008_INTRUDER_OVERLAP_BASE.png": """Scientific-poetic visualization of three different sleep-paralysis intruder reports overlapping: three translucent spatial maps—doorframe geometry, human peripheral-vision field and acoustic pressure rings—intersect in a luminous dark-blue gallery, producing one shared humanoid-shaped absence only where the layers overlap. It is an optical negative space, not a creature. No bed, no bedroom, no horror ghost, no text. Warm brass accents, pale cyan contours, visible midtones, complex layered documentary art direction, 16:9.""",
    "IMG010_GREY_FORM_AMBIGUOUS.png": """A restrained conceptual still about an ambiguous 'grey' form created by the brain: a pearl-grey ovoid volume floats within a large black-box perception laboratory, assembled from fog, peripheral blur, binocular field arcs and fragmented facial-recognition grids; it never resolves into an alien or a face. Small warm observation lights and a luminous horizon keep the frame readable. No bedroom, no UFO, no extraterrestrial cliché, no text, no logos. Museum-installation realism, subtle grain, deep indigo and silver palette, 16:9.""",
    "IMG017_HAT_MAN_FOOT_OF_BED.png": """The Hat Man treated as a cultural negative symbol rather than a man in a room: a monumental typology wall in a bright dim museum archive holds dozens of differently shaped hat brims and shoulder contours cut from translucent smoked glass; viewed together, the empty wall between them forms one imposing human-shaped void. No literal person, no bedroom, no horror apparition, no readable labels. Amber edge light, cool slate depth, lifted midtones, tactile materials, poetic documentary photography, 16:9.""",
    "IMG019_HAT_MAN_AS_ROOM_GEOMETRY.png": """Abstract architectural geometry explaining how ordinary cues create the Hat Man: freestanding doorframe, coat-hook, lampshade and window-blind planes are separated across a spacious luminous studio; a single warm side light projects their unrelated shadows so they almost—but not quite—assemble into a hat-brim silhouette on a translucent screen. No person, no bed, no bedroom, no supernatural entity, no text. Precise gallery-installation photography, clear midtones, amber and indigo, 16:9.""",
    "IMG021_MULTIPLE_CAUSES_SAME_SILHOUETTE.png": """A sophisticated causal convergence diagram rendered as a physical museum installation: five distinct streams—body-pressure ripples, doorway geometry, peripheral blur, remembered sketches and network signal pulses—travel through translucent sculptural channels and converge into the same central hat-shaped negative space, then separate again. No literal man, no bedroom, no captions or invented writing. Luminous pearl, cyan and amber against deep blue, readable shadows, scientific yet mystical, 16:9 documentary realism.""",
    "IMG031_HAT_MAN_DISSOLVES_INTO_PIXELS.png": """Final conceptual transformation: the culturally shared hat-shaped negative-space icon dissolves into thousands of luminous archive tiles, radio wavelets, memory fragments and network nodes that flow outward into a vast bright signal cosmos. The icon is purely geometric and already breaking apart, not a literal person. No bedroom, no horror ghost, no binary text, no logos. Deep indigo with warm amber and electric cyan, luminous threshold feeling, complex but serene, lifted midtones, cinematic 16:9.""",
}

GUARDRAIL = """Create exactly one 2K 16:9 landscape documentary still. No captions, labels, subtitles, logos, signatures, watermarks, readable interface text, or invented writing. No malformed anatomy. Keep natural lifted midtones and visible shadow detail for YouTube; mysterious but not depressing or crushed-black. """


def token() -> str:
    gcloud = os.environ.get("GCLOUD_CMD", r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")
    return subprocess.run([gcloud, "auth", "application-default", "print-access-token"], check=True, capture_output=True, text=True).stdout.strip()


def endpoint(project: str) -> str:
    return f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/publishers/google/models/{MODEL}:generateContent"


def main() -> int:
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    failures = []
    for i, (name, prompt) in enumerate(JOBS.items(), 1):
        print(f"[{i}/{len(JOBS)}] {name}", flush=True)
        payload = {"contents": [{"role": "USER", "parts": [{"text": GUARDRAIL + prompt}]}], "generationConfig": {"candidateCount": 1, "responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}}}
        try:
            response = requests.post(endpoint(project), headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"}, json=payload, timeout=420)
            if response.status_code >= 400:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text[:700]}")
            image_bytes = None
            for candidate in response.json().get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    inline = part.get("inlineData") or part.get("inline_data")
                    if inline and inline.get("data"):
                        image_bytes = base64.b64decode(inline["data"])
                        break
            if not image_bytes:
                raise RuntimeError("No image returned")
            temp = OUTPUT / (Path(name).stem + "_REDESIGN.png")
            temp.write_bytes(image_bytes)
            with Image.open(temp) as img:
                print(f"  {img.width}x{img.height} {temp.stat().st_size} bytes", flush=True)
        except Exception as exc:
            failures.append((name, str(exc)))
            print(f"  FAILED {exc}", flush=True)
        time.sleep(1)
    if failures:
        print(json.dumps(failures, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
