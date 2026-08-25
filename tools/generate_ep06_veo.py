#!/usr/bin/env python3
"""Generate four transformative EP06 image-to-video inserts with Vertex AI Veo 3.1."""

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
OUTPUT = (
    ROOT
    / "06_PRODUCTION"
    / "EP06_SCHLAFPARALYSE_V4"
    / "IMAGE_GENERATION_KIT"
    / "03_GENERATED_OUTPUT"
    / "NanoBanana_2K_Series"
)
GCLOUD = Path(r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")

CLIPS = [
    {
        "filename": "CLIP001_SOUL_BODY_OFFSET.mp4",
        "start": "IMG011_WAKE_BODY_LAG.png",
        "person": "allow_adult",
        "prompt": "Six-second transformative conceptual science-documentary clip beginning exactly from the supplied temporal-layer frame. Lock the camera completely. The single anonymous walking figure's three translucent timing layers separate farther apart: the warm awareness layer advances one measured step, the cool dense body layer remains delayed, and a thin silver layer between them stretches like elastic time. At the midpoint the delayed layers catch up in one smooth pulse and fuse back into a single anatomically correct adult figure. The curtains respond with one subtle pressure wave and the floor reflections follow the moving layers accurately. This is a subjective visualization of wake-body timing, not evidence of a literal soul leaving the body. No new person, no face close-up, no clone remaining at the end, no text, logo, camera motion, flicker, random morphing or audio. Keep bright dawn midtones and visible detail.",
        "position": "S3, subjektive Visualisierung: Bewusstsein vor Koerperreaktion",
    },
    {
        "filename": "CLIP002_REM_SIGNAL_GATE.mp4",
        "start": "IMG003_HAND_WILL_NOT_MOVE.png",
        "person": "allow_adult",
        "prompt": "Six-second transformative neuroscience visualization beginning exactly from the supplied hand-and-forearm frame. Camera locked. A warm motor-command pulse travels visibly from the forearm toward the fingers, reaches the luminous REM inhibition gate at the wrist, compresses against it and branches sideways into harmless fading filaments; the real hand and all five fingers remain anatomically still. After a short pause the gate softens, one final pulse crosses, and the index finger makes a tiny deliberate movement of only a few millimeters. This is an illustrative scientific metaphor for REM atonia, not a literal recording of neural activity. No extra fingers, no deformation, no detached limb, no text, label, logo, camera move, flicker, random morphing or audio. Preserve bright readable blue and amber detail.",
        "position": "S3-S4, wissenschaftliche Visualisierung: REM-Motorhemmung",
    },
    {
        "filename": "CLIP003_OLD_HAG_THRESHOLD.mp4",
        "start": "SHOT04_EMPTY_BEDROOM_SHADOWS.png",
        "person": "allow_adult",
        "prompt": "Six-second transformative oral-history visualization beginning exactly from the supplied Newfoundland rocking-chair archive frame. Camera locked. Atlantic light crosses the floor, the empty chair rocks twice by itself, and loose quilt fibers rise gently from the chair back. The fibers and sea mist briefly assemble at the open doorway into an ambiguous faceless elderly-woman-shaped outline made entirely of textile and fog; it takes one slow step toward the threshold, then unravels back into the quilt as the tape reels turn. Keep the outline poetic and culturally contextual, never a literal supernatural claim and never a grotesque monster. No detailed face, no attack, no bed, no jump scare, no text, logo, camera movement, chaotic morphing or audio. Bright readable coastal midtones throughout.",
        "position": "S2/S7, subjektive Folklore-Visualisierung: Old-Hag-Schwelle",
    },
    {
        "filename": "CLIP004_PRESENCE_GEOMETRY.mp4",
        "start": "IMG028_PRESENCE_BEFORE_FORM.png",
        "person": "dont_allow",
        "prompt": "Six-second transformative perception visualization beginning exactly from the supplied translucent museum corridor. Camera locked. A pressure ripple travels through the hanging fabric planes although no wind source exists; reflections and drifting dust bend around one moving region of empty space. The region crosses the corridor, briefly aligns the curtains and floor light into the readable geometry of shoulders and a head without creating a solid being, then the alignment collapses into ordinary separate curtains and reflections. The final second is clearly an empty architecture again. This visualizes perceptual completion and sensed presence, not a recorded entity. No person, face, opaque ghost, monster, black silhouette, text, logo, camera motion, random object morphing or audio. Preserve luminous pearl-blue exposure and warm threshold light.",
        "position": "S5-S6, wissenschaftliche Visualisierung: Praesenzgeometrie",
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


def endpoint(project: str, method: str) -> str:
    return (
        f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/"
        f"publishers/google/models/{MODEL}:{method}"
    )


def post(project: str, method: str, payload: dict, retries: int = 8) -> dict:
    waits = [10, 20, 30, 45, 60, 90, 120]
    for attempt in range(retries):
        response = requests.post(
            endpoint(project, method),
            headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
            json=payload,
            timeout=300,
        )
        if response.status_code < 400:
            return response.json()
        if response.status_code in {429, 500, 502, 503, 504} and attempt < retries - 1:
            delay = waits[min(attempt, len(waits) - 1)]
            print(f"HTTP {response.status_code}; retry in {delay}s", flush=True)
            time.sleep(delay)
            continue
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1600]}")
    raise RuntimeError("request exhausted retries")


def submit(clip: dict, project: str) -> str:
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
            "enhancePrompt": True,
            "generateAudio": False,
            "negativePrompt": "text, subtitles, captions, labels, logos, watermark, detailed faces, extra people, duplicate bodies, gore, grotesque monster, demon, jump scare, random morphing, broken anatomy, extra fingers, camera pan, camera push, camera pull, zoom, handheld shake, rapid strobe, extreme darkness, crushed shadows, audio",
            "personGeneration": clip["person"],
            "resizeMode": "crop",
            "resolution": "1080p",
            "sampleCount": 1,
        },
    }
    data = post(project, "predictLongRunning", payload)
    if not data.get("name"):
        raise RuntimeError(f"No operation name: {json.dumps(data)[:1600]}")
    return data["name"]


def poll(operation: str, project: str, timeout_seconds: int = 1800) -> dict:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        data = post(project, "fetchPredictOperation", {"operationName": operation})
        if data.get("done"):
            return data
        print("  waiting...", flush=True)
        time.sleep(15)
    raise TimeoutError(operation)


def save(clip: dict, operation: dict) -> Path:
    if operation.get("error"):
        raise RuntimeError(json.dumps(operation["error"], ensure_ascii=False))
    videos = (operation.get("response") or {}).get("videos") or []
    if not videos or not videos[0].get("bytesBase64Encoded"):
        raise RuntimeError(f"No inline video: {json.dumps(operation)[:1600]}")
    destination = OUTPUT / clip["filename"]
    destination.write_bytes(base64.b64decode(videos[0]["bytesBase64Encoded"]))
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clips", default="1,2,3,4")
    args = parser.parse_args()
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    selected = {int(value.strip()) for value in args.clips.split(",") if value.strip()}
    failures = []
    for index, clip in enumerate(CLIPS, 1):
        if index not in selected:
            continue
        destination = OUTPUT / clip["filename"]
        if destination.is_file() and destination.stat().st_size > 100_000:
            print(f"SKIP {destination.name}", flush=True)
            continue
        print(f"{clip['filename']} <- {clip['start']}", flush=True)
        try:
            operation = submit(clip, project)
            print(f"  submitted {operation}", flush=True)
            destination = save(clip, poll(operation, project))
            print(f"  saved {destination} ({destination.stat().st_size} bytes)", flush=True)
        except Exception as exc:  # noqa: BLE001
            failures.append({"clip": clip["filename"], "error": str(exc)})
            print(f"  FAILED {exc}", flush=True)
    if failures:
        print(json.dumps({"failures": failures}, ensure_ascii=False, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
