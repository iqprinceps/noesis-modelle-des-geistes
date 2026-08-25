#!/usr/bin/env python3
"""Generate selected EP08 image-to-video clips through Vertex AI Veo 3.1."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
from pathlib import Path

import requests


MODEL = "veo-3.1-generate-001"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT"
GCLOUD = Path(r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")

CLIPS = [
    {
        "filename": "CLIP001_RADIO_MICROPHONE_PUSH.mp4",
        "start": "SHOT01_RADIO_MICROPHONE_MACRO.png",
        "prompt": "A restrained six-second documentary insert. Preserve the start frame exactly. Very slow cinematic push toward the vintage broadcast microphone. Only tiny amber console indicators fluctuate naturally and the loose headphone cable settles by a few millimeters. No people enter. No new objects, text, labels or logos. Stable geometry, realistic optics, no dramatic movement, no camera shake, no audio.",
        "position": "S1–S2, Art-Bell-/Radiostudio-Übergang",
    },
    {
        "filename": "CLIP002_MESSAGE_ROOM_GLIDE.mp4",
        "start": "IMG002_4500_MESSAGES_MATERIAL.png",
        "prompt": "A restrained six-second early-2000s documentary insert. Preserve every paper stack, CRT, radio console and object from the start frame. Execute an extremely slow lateral camera glide. Only one or two loose paper corners move subtly from room air and equipment indicators flicker naturally. Do not reveal or create readable writing. No people, no new messages, no text, labels, logos, morphing or object duplication, no audio.",
        "position": "S1–S2, Reaktion auf 4.500 Nachrichten",
    },
    {
        "filename": "CLIP003_BRIGHT_BLINDS_DRIFT.mp4",
        "start": "SHOT03_BRIGHT_BLINDS.png",
        "prompt": "A quiet six-second documentary bedroom insert. Preserve the empty room, bed, blinds and exact lighting design. Locked camera with an almost imperceptible slow push. Exterior light through the blinds changes only slightly and a few dust particles drift in the beam. No person, silhouette, alien, new object, text, logo or supernatural effect. Stable geometry, no flicker artifacts, no audio.",
        "position": "S3–S4, Licht-/Erinnerungsübergang",
    },
    {
        "filename": "CLIP004_FINAL_BEDROOM_GLOW.mp4",
        "start": "IMG032_FINAL_EMPTY_BEDROOM_SCREEN_GLOW.png",
        "prompt": "A quiet six-second final documentary shot. Preserve the empty bedroom, chair, doorway, bed and all object geometry from the start frame. Very slow controlled dolly forward. The off-frame screen glow breathes almost imperceptibly and soft dawn-night ambient light remains natural. No person or silhouette appears, no object moves independently, no text, logo, face, paranormal residue, morphing or camera shake, no audio.",
        "position": "S7–S8, ruhiger Schluss vor Endcard",
    },
]


def token() -> str:
    result = subprocess.run(
        [str(GCLOUD), "auth", "application-default", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def model_url(project: str, location: str, method: str) -> str:
    host = "aiplatform.googleapis.com" if location == "global" else f"{location}-aiplatform.googleapis.com"
    return (
        f"https://{host}/v1/projects/{project}/locations/{location}/publishers/google/"
        f"models/{MODEL}:{method}"
    )


def headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {token()}", "Content-Type": "application/json"}


def submit(clip: dict, project: str, location: str) -> str:
    start = OUTPUT / clip["start"]
    payload = {
        "instances": [
            {
                "prompt": clip["prompt"],
                "image": {
                    "bytesBase64Encoded": base64.b64encode(start.read_bytes()).decode("ascii"),
                    "mimeType": "image/png",
                },
            }
        ],
        "parameters": {
            "aspectRatio": "16:9",
            "durationSeconds": 6,
            "generateAudio": False,
            "negativePrompt": "text, subtitles, captions, labels, logos, watermark, faces, new people, object morphing, duplicated objects, camera shake, rapid movement, horror effects",
            "personGeneration": clip.get("personGeneration", "dont_allow"),
            "resizeMode": "crop",
            "resolution": "1080p",
            "sampleCount": 1,
        },
    }
    response = requests.post(
        model_url(project, location, "predictLongRunning"),
        headers=headers(),
        json=payload,
        timeout=180,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1600]}")
    data = response.json()
    if not data.get("name"):
        raise RuntimeError(f"No operation name: {json.dumps(data)[:1600]}")
    return data["name"]


def poll(operation: str, project: str, location: str, timeout_seconds: int = 1800) -> dict:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        response = requests.post(
            model_url(project, location, "fetchPredictOperation"),
            headers=headers(),
            json={"operationName": operation},
            timeout=180,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Poll HTTP {response.status_code}: {response.text[:1600]}")
        data = response.json()
        if data.get("done"):
            return data
        print("  waiting...", flush=True)
        time.sleep(15)
    raise TimeoutError(f"Timed out: {operation}")


def save_video(clip: dict, operation: dict) -> Path:
    if operation.get("error"):
        raise RuntimeError(json.dumps(operation["error"], ensure_ascii=False))
    response = operation.get("response", {})
    videos = response.get("videos", [])
    if not videos:
        reasons = response.get("raiMediaFilteredReasons", response)
        raise RuntimeError(f"No video returned: {json.dumps(reasons, ensure_ascii=False)[:1600]}")
    encoded = videos[0].get("bytesBase64Encoded")
    if not encoded:
        raise RuntimeError(f"Inline video bytes missing: {json.dumps(videos[0])[:1600]}")
    destination = OUTPUT / clip["filename"]
    destination.write_bytes(base64.b64decode(encoded))
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clips", default="1,2,3,4", help="Comma-separated clip numbers")
    args = parser.parse_args()

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    location = "global"
    selected = {int(item.strip()) for item in args.clips.split(",") if item.strip()}
    failures = []
    for index, clip in enumerate(CLIPS, start=1):
        if index not in selected:
            continue
        print(f"{clip['filename']} from {clip['start']}", flush=True)
        try:
            operation_name = submit(clip, project, location)
            print(f"  submitted {operation_name}", flush=True)
            operation = poll(operation_name, project, location)
            destination = save_video(clip, operation)
            print(f"  saved {destination} ({destination.stat().st_size} bytes)", flush=True)
        except Exception as exc:  # noqa: BLE001 - continue selected jobs and report all failures
            failures.append({"clip": clip["filename"], "error": str(exc)})
            print(f"  FAILED {exc}", flush=True)
    if failures:
        print(json.dumps({"failures": failures}, ensure_ascii=False, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
