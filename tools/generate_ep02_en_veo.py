#!/usr/bin/env python3
"""Generate the four viewer-justified EP02 image-to-video inserts with Vertex Veo.

The runner is resumable: operation IDs are persisted, completed files are cached,
and no more than two jobs are active at once.
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
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
STARTS = EP / "03_VISUALS" / "GENERATED" / "INNER"
OUTPUTS = EP / "03_VISUALS" / "CLIPS"
STATE_DIR = EP / "03_VISUALS" / "METADATA" / "VEO"
STATE_FILE = STATE_DIR / "operations.json"
MODEL = "veo-3.1-generate-001"
LOCATION = "global"
MAX_ACTIVE = 2

NEGATIVE = (
    "captions, title, labels, letters, numbers, readable text, logo, watermark, mode badge, "
    "new person, changed anatomy, distorted body, duplicated limbs, monster, ghost face, "
    "generic occult symbols, zodiac, chakra, crystal, glowing orb, energy beam, jump scare, "
    "camera shake, fast motion, simple zoom, Ken Burns effect, crushed blacks, audio"
)

JOBS = [
    {
        "output": "GW_EN_CLIP03_MONROE_EXIT.mp4",
        "start": "GW_EN_INNER01_MONROE_EXIT_NATIVE.png",
        "person": "allow_adult",
        "use": "Monroe introduction: clearly subjective out-of-body experience, not archival fact",
        "prompt": (
            "Six-second clearly subjective visualisation beginning exactly from the supplied 1970s laboratory image. "
            "Keep the resting adult body, cot and listening equipment anatomically stable. The elevated first-person "
            "viewpoint rises only a little farther while the room gains real spatial parallax; the cable and headphone "
            "remain physically connected below. A soft double boundary around the cot separates once, then settles, "
            "communicating the reported sensation of leaving the body without showing a spirit, monster or literal proof. "
            "Slow controlled motion, restrained amber and blue-grey light, tactile period materials, no text."
        ),
    },
    {
        "output": "GW_EN_CLIP05_CROSSING.mp4",
        "start": "GW_EN_INNER02_ACOUSTICS_COSMOLOGY_NATIVE.png",
        "person": "disallow",
        "use": "McDonnell's conceptual transition from acoustics to cosmology",
        "prompt": (
            "Six-second conceptual transformation beginning exactly from the supplied acoustic-to-cosmology image. "
            "At left, one precise analogue sound wave travels through the tangible paper-and-brass apparatus. As it "
            "crosses the central threshold, the same waveform folds continuously into a deep impossible lattice of "
            "curved spacetime planes on the right. Make the transformation legible as one chain of reasoning, not an "
            "explosion or magic portal. Real material depth, slow lateral parallax, stable geometry, no symbols or text."
        ),
    },
    {
        "output": "GW_EN_CLIP06_FOCUS_WHEEL.mp4",
        "start": "GW_EN_INNER03_FOCUS_WHEEL_NATIVE.png",
        "person": "disallow",
        "use": "Focus-level model: attention decouples from ordinary time sequence",
        "prompt": (
            "Six-second abstract explanatory motion beginning exactly from the supplied brass time-wheel image. The "
            "central anonymous figure stays stable while the outer engraved rings rotate at different slow rates. "
            "Several translucent phase echoes move around the circumference, briefly align across nonadjacent positions, "
            "then separate again. The hub remains calm as ordinary clock order loosens at the rim. Sophisticated mechanical "
            "motion, shallow orbital camera arc, no face, no numerals, no clock text, no supernatural iconography."
        ),
    },
    {
        "output": "GW_EN_CLIP09_NONPHYSICAL_DOCTRINE.mp4",
        "start": "GW_EN_INNER04_NONPHYSICAL_PRESENCE_NATIVE.png",
        "person": "disallow",
        "use": "Recommendation J: doctrine for encounters framed as nonphysical presences",
        "prompt": (
            "Six-second restrained military-threshold visualisation beginning exactly from the supplied 1980s perimeter "
            "image. Keep the empty corridor, fence geometry and analogue surveillance materials stable. A responsive "
            "negative-space pressure crosses the threshold: dust, hanging cable and reflected light each react in sequence, "
            "suggesting an unseen presence without forming a body or face. The distortion approaches the guarded boundary, "
            "pauses, then recedes. This is an ambiguous conceptual image, not documentary evidence. No text or creature."
        ),
    },
]

_token: tuple[str, float] | None = None


def access_token() -> str:
    global _token
    now = time.time()
    if _token and _token[1] > now + 60:
        return _token[0]
    completed = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        capture_output=True,
        text=True,
        shell=True,
        timeout=60,
    )
    value = completed.stdout.strip()
    if not value:
        raise RuntimeError("No ADC access token")
    _token = (value, now + 3300)
    return value


def project_id() -> str:
    value = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not value:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set")
    return value


def endpoint(method: str) -> str:
    return (
        f"https://aiplatform.googleapis.com/v1/projects/{project_id()}"
        f"/locations/{LOCATION}/publishers/google/models/{MODEL}:{method}"
    )


def post(url: str, payload: dict[str, Any], retries: int = 7) -> dict[str, Any]:
    waits = [10, 20, 30, 45, 60, 90]
    for attempt in range(retries):
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:1200]
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                delay = waits[min(attempt, len(waits) - 1)]
                print(f"HTTP {exc.code}; retry in {delay}s", flush=True)
                time.sleep(delay)
                continue
            raise RuntimeError(f"HTTP {exc.code}: {body}") from None
    raise RuntimeError("request exhausted retries")


def submit(job: dict[str, str]) -> str:
    start_path = STARTS / job["start"]
    payload = {
        "instances": [{
            "prompt": job["prompt"],
            "image": {
                "bytesBase64Encoded": base64.b64encode(start_path.read_bytes()).decode("ascii"),
                "mimeType": "image/png",
            },
        }],
        "parameters": {
            "aspectRatio": "16:9",
            "durationSeconds": 6,
            "enhancePrompt": True,
            "generateAudio": False,
            "negativePrompt": NEGATIVE,
            "personGeneration": job["person"],
            "resolution": "1080p",
            "sampleCount": 1,
        },
    }
    response = post(endpoint("predictLongRunning"), payload)
    if not response.get("name"):
        raise RuntimeError(f"No operation name: {response}")
    return str(response["name"])


def poll(operation: str) -> dict[str, Any]:
    return post(endpoint("fetchPredictOperation"), {"operationName": operation})


def save_video(job: dict[str, str], response: dict[str, Any]) -> pathlib.Path:
    videos = (response.get("response") or {}).get("videos") or []
    if not videos:
        raise RuntimeError(f"No videos in response: {json.dumps(response)[:1500]}")
    item = videos[0].get("video", videos[0])
    output = OUTPUTS / job["output"]
    encoded = item.get("bytesBase64Encoded") or item.get("videoBytes")
    if encoded:
        output.write_bytes(base64.b64decode(encoded))
    elif (uri := item.get("gcsUri") or item.get("uri")) and str(uri).startswith("gs://"):
        subprocess.run(["gcloud", "storage", "cp", str(uri), str(output)], check=True, shell=True)
    else:
        raise RuntimeError(f"Video response contains neither bytes nor GCS URI: {item}")
    return output


def write_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="")
    parser.add_argument("--poll-seconds", type=int, default=20)
    args = parser.parse_args()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.is_file() else {}
    chosen = [j for j in JOBS if not args.only or j["output"] == args.only]
    pending = [j for j in chosen if not (OUTPUTS / j["output"]).is_file()]
    while pending:
        active = [j for j in pending if state.get(j["output"], {}).get("operation")]
        for job in pending:
            if len(active) >= MAX_ACTIVE:
                break
            record = state.setdefault(job["output"], {})
            if not record.get("operation"):
                print(f"SUBMIT {job['output']} <- {job['start']}", flush=True)
                record.update(
                    operation=submit(job), start=job["start"], prompt=job["prompt"],
                    negative_prompt=NEGATIVE, use=job["use"], provider="Vertex AI",
                    model=MODEL, duration_seconds=6, resolution="1080p", seed=None,
                )
                write_state(state)
                active.append(job)
        completed: list[dict[str, str]] = []
        for job in active:
            response = poll(state[job["output"]]["operation"])
            if response.get("done"):
                if response.get("error"):
                    raise RuntimeError(f"{job['output']}: {response['error']}")
                output = save_video(job, response)
                state[job["output"]].update(done=True, output=str(output), bytes=output.stat().st_size)
                write_state(state)
                completed.append(job)
                print(f"OK {output.name} {output.stat().st_size} bytes", flush=True)
            else:
                print(f"WAIT {job['output']}", flush=True)
        pending = [j for j in pending if j not in completed]
        if pending:
            time.sleep(max(10, args.poll_seconds))


if __name__ == "__main__":
    main()
