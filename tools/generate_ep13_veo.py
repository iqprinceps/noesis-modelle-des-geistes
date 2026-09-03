#!/usr/bin/env python3
"""EP13 image-to-video inserts with Vertex AI Veo 3.1.

Motion is only used where it carries meaning the still cannot: the flames that
appear to set the world alight and then go out, and the figure walking away down
the ruined street. Everything else in EP13 stays a still with editor-side motion.
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
SRC = ROOT / "tmp" / "imagegen" / "ep13_vertex_raw"
OUT = ROOT / "tmp" / "video" / "ep13_veo"
MODEL = "veo-3.1-generate-001"
LOCATION = "global"

NEGATIVE = (
    "camera shake, fast motion, whip pan, zoom burst, morphing architecture, warped "
    "geometry, object duplication, new people appearing, face becoming visible, readable "
    "face, literal monster, glowing eyes, jump scare, horror lighting, new text, captions, "
    "labels, logos, watermark, subtitles, vignette, darkened corners, letterboxing, black "
    "bars, tilt-shift, miniature look, colour saturation shift, sepia, film grain, "
    "flicker, strobe, audio, speech, music, explosion, fireball, blast, smoke cloud, "
    "smoke plume, billowing smoke, pyrotechnics, ember shower, sparks, dolly, tracking shot, "
    "camera push in, camera pull back, crane move, parallax, changing perspective"
)

JOBS = [
    {
        "output": "EP13_CLIP01_FLAMES_FAIL.mp4",
        "start": ("v2", "EP13_V01_ANGEL_SWORD.png"),
        "person": "allow_adult",
        "prompt": (
            "Six seconds beginning exactly from the supplied frame. LOCKED-OFF TRIPOD SHOT: "
            "the camera position, angle and focal length are frozen for the entire six "
            "seconds and the framing is identical in the first and last frame. The figure "
            "and the sword stay completely still: no step, no turn, no gesture, no head "
            "movement, and the face never becomes visible. Only the fire changes, and it "
            "changes as thin filaments, never as volume. In the first half, fine threads of "
            "flame run off the blade and stretch outward across the pale field like burning "
            "hairline cracks, reaching far but staying thin and transparent. In the second "
            "half those threads cool, lose colour and retract until only a faint ember sits "
            "at the blade. Absolutely no fireball, no explosion, no billowing smoke cloud, "
            "no dark plume, no puff, no sparks. The pale field stays bone-white, evenly lit "
            "to every frame edge, and never darkens."
        ),
    },
    {
        "output": "EP13_CLIP02_WALKING_AWAY.mp4",
        "start": ("v2", "EP13_V03_RUINED_CITY.png"),
        "person": "allow_adult",
        "prompt": (
            "Six seconds beginning exactly from the supplied frame. LOCKED-OFF TRIPOD SHOT: "
            "the camera does not move one millimetre. Its position, angle and focal length "
            "are frozen, so every wall, arch, window and piece of rubble stays at exactly "
            "the same pixel position from the first frame to the last. The ONLY thing that "
            "moves in the entire frame is the small white figure, who walks slowly further "
            "away down the street and becomes gradually smaller, always seen from behind, "
            "never turning, face never visible. Everything else is completely static. Fine "
            "pale dust hangs almost motionless. The single warm ember far down the street "
            "pulses almost imperceptibly. No dolly, no push, no drift, no parallax, no "
            "perspective change, no new people, no vehicles, no birds, no collapsing walls."
        ),
    },
]

_token: dict[str, Any] = {}


def access_token() -> str:
    now = time.time()
    if _token.get("expires", 0) > now + 60:
        return str(_token["value"])
    done = subprocess.run(["gcloud", "auth", "application-default", "print-access-token"],
                          capture_output=True, text=True, shell=True, timeout=90)
    v = done.stdout.strip()
    if not v:
        raise RuntimeError("no ADC token")
    _token.update(value=v, expires=now + 3300)
    return v


def endpoint(verb: str) -> str:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT not set")
    return ("https://aiplatform.googleapis.com/v1/projects/" + project + "/locations/" +
            LOCATION + "/publishers/google/models/" + MODEL + ":" + verb)


def post(url: str, payload: dict[str, Any], retries: int = 6) -> dict[str, Any]:
    for attempt in range(retries):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + access_token(),
                     "Content-Type": "application/json; charset=utf-8"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=420) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:600]
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError("HTTP " + str(e.code) + ": " + body) from None
        except Exception:
            if attempt >= retries - 1:
                raise
            time.sleep(15)
    raise RuntimeError("request failed")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    picks = [j for j in JOBS if not args.only or args.only in j["output"]]

    ops = []
    for job in picks:
        sub, name = job["start"]
        start = SRC / sub / name
        if not start.is_file():
            print("MISSING " + str(start), flush=True)
            continue
        payload = {
            "instances": [{"prompt": job["prompt"],
                           "image": {"bytesBase64Encoded": base64.b64encode(start.read_bytes()).decode("ascii"),
                                     "mimeType": "image/png"}}],
            "parameters": {"aspectRatio": "16:9", "durationSeconds": 6, "enhancePrompt": True,
                           "generateAudio": False, "negativePrompt": NEGATIVE,
                           "personGeneration": job["person"], "resolution": "1080p",
                           "sampleCount": 1},
        }
        resp = post(endpoint("predictLongRunning"), payload)
        op = resp.get("name")
        if not op:
            print("FAIL submit " + job["output"] + ": " + json.dumps(resp)[:300], flush=True)
            continue
        print("SUBMIT " + job["output"], flush=True)
        ops.append((job, op))

    for job, op in ops:
        for _ in range(80):
            time.sleep(15)
            st = post(endpoint("fetchPredictOperation"), {"operationName": op})
            if not st.get("done"):
                continue
            if st.get("error"):
                print("FAIL " + job["output"] + ": " + json.dumps(st["error"])[:300], flush=True)
                break
            body = st.get("response") or {}
            vids = body.get("videos") or body.get("generatedVideos") or []
            if not vids:
                print("FAIL " + job["output"] + " no video: " + json.dumps(st)[:400], flush=True)
                break
            item = vids[0]
            if isinstance(item.get("video"), dict):
                item = item["video"]
            enc = item.get("bytesBase64Encoded") or item.get("videoBytes")
            if not enc:
                print("FAIL " + job["output"] + " no bytes: " + json.dumps(item)[:300], flush=True)
                break
            dest = OUT / job["output"]
            dest.write_bytes(base64.b64decode(enc))
            print("OK  " + dest.name + "  " + str(dest.stat().st_size) + " bytes", flush=True)
            break
        else:
            print("TIMEOUT " + job["output"], flush=True)


if __name__ == "__main__":
    main()
