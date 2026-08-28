#!/usr/bin/env python3
"""Generate one restrained native-portrait Veo insert for each Schlafparalyse Short."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
MODEL = "veo-3.1-generate-001"
LOCATION = "global"
GCLOUD = Path(r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")
STATE = PROD / "VEO_VERTICAL_V2_OPERATIONS.json"

NEGATIVE = (
    "landscape frame, horizontal video inside portrait, letterboxing, pillarboxing, black bars, border, "
    "inset card, split screen, camera shake, handheld wobble, fast pan, fast zoom, random morphing, "
    "warped architecture, rotating room, tilted gravity, duplicated object, new person, extra limb, "
    "broken anatomy, changed face, text, captions, labels, logos, watermark, readable interface, audio"
)

JOBS = [
    {
        "short": "SP06A_ATEM",
        "start": "SHOT04.png",
        "person": "allow_adult",
        "prompt": (
            "Native 9:16 six-second sleep-laboratory documentary insert. Preserve the supplied adult, bed, "
            "sensors, room and upright portrait geometry exactly. Camera is completely locked. The sleeper's "
            "chest and blanket rise once by only a few millimeters with a calm breath while one tiny unmarked "
            "equipment indicator softly pulses. The face, hands, wires and every body proportion remain stable. "
            "No new motion, no zoom or pan, no medical interface, no text and no audio."
        ),
    },
    {
        "short": "SP06B_RUECKENLAGE",
        "start": "SHOT05.png",
        "person": "dont_allow",
        "prompt": (
            "Native 9:16 six-second empty-bedroom documentary insert. Preserve the upright room, horizontal bed, "
            "door and all geometry exactly. Camera completely locked. The two overlapping moonlight bands drift "
            "apart very slowly by a few centimeters, then settle; a curtain shadow changes almost imperceptibly. "
            "No person appears, no object moves, no camera motion, no text and no audio."
        ),
    },
    {
        "short": "SP07A_ALBTRAUMWORT",
        "start": "SHOT03.png",
        "person": "dont_allow",
        "prompt": (
            "Native 9:16 six-second historical-documentary insert. Preserve the upright medieval room, wooden "
            "shelf, three carved household tokens and bed geometry exactly. Locked camera. Candlelight flickers "
            "gently and the three token shadows lengthen until they briefly share one ambiguous pressure contour, "
            "then separate again. No creature or person appears, no objects morph or move, no text and no audio."
        ),
    },
    {
        "short": "SP07B_SALEM_ZEUGE",
        "start": "SHOT07.png",
        "person": "dont_allow",
        "prompt": (
            "Native 9:16 six-second empty colonial courtroom insert. Preserve the witness chair, benches, doors, "
            "windows and vertical architecture exactly. Camera completely locked. A narrow beam of morning light "
            "moves slowly across the empty witness chair while a few dust particles drift. No person enters, no "
            "furniture moves, no text, papers, camera motion or audio."
        ),
    },
    {
        "short": "SP08A_HAT_MAN_HUT",
        "start": "SHOT07.png",
        "person": "dont_allow",
        "prompt": (
            "Native 9:16 six-second perception-demonstration insert. Preserve the empty bedroom, coat rack, hat, "
            "doorframe, bed and upright geometry exactly. Camera completely locked. Dawn light shifts slowly so "
            "the hat-shaped wall shadow first reads like a figure, then visibly separates back into the ordinary "
            "coat-rack and doorframe shadows. No person, face, eyes, monster, object movement, text or audio."
        ),
    },
    {
        "short": "SP08B_UNSICHTBARE_PERSON",
        "start": "SHOT07.png",
        "person": "dont_allow",
        "prompt": (
            "Native 9:16 six-second empty-clinic documentary insert. Preserve the examination chair, lamp, blank "
            "monitors, equipment and upright room geometry exactly. Camera completely locked. The practical lamp "
            "brightness changes subtly and its ordinary chair shadow shifts a few centimeters, briefly suggesting "
            "a human presence before resolving clearly as chair geometry. No person appears, no screen content, "
            "no object morphing, text, camera motion or audio."
        ),
    },
]


def token() -> str:
    result = subprocess.run(
        [str(GCLOUD), "auth", "application-default", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.stdout.strip()


def endpoint(project: str, method: str) -> str:
    return (
        f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/{LOCATION}/"
        f"publishers/google/models/{MODEL}:{method}"
    )


def post(project: str, method: str, payload: dict, access: str, retries: int = 8) -> dict:
    waits = [10, 20, 30, 45, 60, 90, 120]
    for attempt in range(retries):
        response = requests.post(
            endpoint(project, method),
            headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json"},
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
    raise RuntimeError("request retries exhausted")


def paths(job: dict) -> tuple[Path, Path]:
    start = PROD / job["short"] / "assets_vertical_v2" / job["start"]
    output = PROD / job["short"] / "veo_vertical_v2" / "CLIP01.mp4"
    return start, output


def submit(job: dict, project: str, access: str) -> str:
    start, _ = paths(job)
    payload = {
        "instances": [
            {
                "prompt": job["prompt"],
                "image": {
                    "bytesBase64Encoded": base64.b64encode(start.read_bytes()).decode("ascii"),
                    "mimeType": "image/png",
                },
            }
        ],
        "parameters": {
            "aspectRatio": "9:16",
            "durationSeconds": 6,
            "enhancePrompt": True,
            "generateAudio": False,
            "negativePrompt": NEGATIVE,
            "personGeneration": job["person"],
            "resizeMode": "crop",
            "resolution": "1080p",
            "sampleCount": 1,
        },
    }
    response = post(project, "predictLongRunning", payload, access)
    operation = response.get("name")
    if not operation:
        raise RuntimeError(f"No operation name: {json.dumps(response)[:1600]}")
    return str(operation)


def save(job: dict, response: dict) -> Path:
    if response.get("error"):
        raise RuntimeError(json.dumps(response["error"], ensure_ascii=False))
    videos = (response.get("response") or {}).get("videos") or []
    if not videos:
        raise RuntimeError(f"No video returned: {json.dumps(response)[:1600]}")
    encoded = videos[0].get("bytesBase64Encoded")
    if not encoded:
        raise RuntimeError(f"No inline bytes: {json.dumps(videos[0])[:1000]}")
    _, output = paths(job)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(base64.b64decode(encoded))
    return output


def write_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="Comma-separated Short folder names")
    parser.add_argument("--retry", action="store_true", help="discard saved operations for selected jobs")
    args = parser.parse_args()
    selected_names = {value.strip() for value in args.only.split(",") if value.strip()}
    jobs = [job for job in JOBS if not selected_names or job["short"] in selected_names]
    if not jobs:
        raise SystemExit("No matching jobs")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    access = token()
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}
    if args.retry:
        for job in jobs:
            state.pop(job["short"], None)
        write_state(state)
    pending = []
    failures = []
    for job in jobs:
        start, output = paths(job)
        if not start.is_file():
            failures.append({"short": job["short"], "error": f"missing {start}"})
            continue
        if output.is_file() and output.stat().st_size > 100_000:
            print(f"SKIP {job['short']} existing {output.stat().st_size} bytes", flush=True)
            continue
        operation = (state.get(job["short"]) or {}).get("operation")
        try:
            if not operation:
                print(f"SUBMIT {job['short']} <- {job['start']}", flush=True)
                operation = submit(job, project, access)
                state[job["short"]] = {"operation": operation, "submitted": time.time()}
                write_state(state)
            pending.append((job, operation))
        except Exception as exc:  # noqa: BLE001
            failures.append({"short": job["short"], "error": str(exc)})
            print(f"FAILED submit {job['short']}: {exc}", flush=True)
    deadline = time.monotonic() + 1800
    while pending and time.monotonic() < deadline:
        still_pending = []
        for job, operation in pending:
            try:
                response = post(project, "fetchPredictOperation", {"operationName": operation}, access)
                if response.get("done"):
                    output = save(job, response)
                    state[job["short"]]["saved"] = str(output)
                    write_state(state)
                    print(f"SAVED {job['short']} {output.stat().st_size} bytes", flush=True)
                else:
                    still_pending.append((job, operation))
            except Exception as exc:  # noqa: BLE001
                failures.append({"short": job["short"], "error": str(exc)})
                state.pop(job["short"], None)
                write_state(state)
                print(f"FAILED poll {job['short']}: {exc}", flush=True)
        pending = still_pending
        if pending:
            print("WAIT " + ", ".join(job["short"] for job, _ in pending), flush=True)
            time.sleep(15)
    for job, _ in pending:
        failures.append({"short": job["short"], "error": "timed out"})
    if failures:
        print(json.dumps({"failures": failures}, ensure_ascii=False, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
