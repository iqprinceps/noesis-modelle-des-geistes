#!/usr/bin/env python3
"""Generate four transformative EP07 image-to-video inserts with Vertex AI Veo 3.1."""

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
SERIES = (
    ROOT
    / "06_PRODUCTION"
    / "EP07_SCHLAFPARALYSE_V4"
    / "IMAGE_GENERATION_KIT"
    / "03_GENERATED_OUTPUT"
    / "NanoBanana_Pro_2K_Series"
)
STATE_DIR = ROOT / "tmp" / "video" / "ep07_veo_transformative_v3"
STATE_FILE = STATE_DIR / "operations.json"
MODEL = "veo-3.1-generate-001"
LOCATION = "global"

NEGATIVE = (
    "Ken Burns effect, mere camera push, mere dolly, mere zoom, camera shake, fast motion, "
    "morphing architecture, warped objects, object duplication, new people, literal monster, "
    "glowing eyes, jump scare, changed historical artwork, changed document, altered handwriting, "
    "new text, captions, labels, logos, watermark, readable interface text, flicker artifact, "
    "extreme darkness, crushed shadows, audio"
)

JOBS = [
    {
        "output": "CLIP001_CULTURAL_MASKS.mp4",
        "start": "IMG015_EXPERIENCE_CULTURE_DECISION_BASE.png",
        "person": "disallow",
        "prompt": (
            "Six-second KULTURELLE VISUALISIERUNG beginning exactly from the supplied frame, with genuine "
            "internal transformation rather than a camera move. Keep the awake eye, skin, fingertips and all "
            "human anatomy stable and natural. The surrounding translucent family-photo edges, woven ornament, "
            "blank book planes and oral-history silhouettes rise into three-dimensional depth and slide past one "
            "another. Their empty cut-outs successively form three different mask-like threshold silhouettes—" 
            "arched, manuscript-ornamental and shoji-angular—without ever becoming faces or one universal being. "
            "The forms overlap for a brief shared pressure contour, then resolve back into visibly distinct cultural "
            "layers. Gentle orbital parallax only supports the transformation. No bed, bedroom, new person, literal "
            "creature, readable text, duplicated anatomy or historical-document claim. Readable indigo and warm-paper midtones."
        ),
        "use": "S3-S4: verschiedene kulturelle Formen um denselben Grenzzustand, ohne Gleichsetzung",
    },
    {
        "output": "CLIP002_NIGHTMARE_PRESSURE.mp4",
        "start": "IMG012_EXPERIENCE_BEFORE_STORY.png",
        "person": "disallow",
        "prompt": (
            "Six-second SUBJECTIVE VISUALISIERUNG beginning exactly from the supplied tactile frame. Create one "
            "clear, meaningful pressure event within the materials: a broad invisible weight travels slowly over "
            "the linen, compressing the embossed rib contour while fine graphite dust flows outward in concentric "
            "waves. The embossed open eye remains awake and follows the pressure only through a tiny change of "
            "highlight; the hand impression tries once to lift from the vellum but remains pinned. At peak pressure "
            "the negative space briefly resembles a crouched threshold shape, never a literal body or creature, "
            "then releases and leaves the material subtly altered. Locked composition with real material parallax, "
            "no bed, bedroom, living person, horror face, glowing effect, text or simple zoom. Keep shadow detail."
        ),
        "use": "S1-S2: subjektive Körpererfahrung von Druck, Wachheit und Bewegungsunfähigkeit",
    },
    {
        "output": "CLIP003_SALEM_PUBLIC_TRANSFORMATION.mp4",
        "start": "IMG003_PRIVATE_NIGHT_TO_COURT.png",
        "person": "disallow",
        "prompt": (
            "Six-second KULTURELLE VISUALISIERUNG beginning exactly from the supplied archival composition. "
            "PIXEL-LOCK THE CAMERA AND BOTH ARCHIVE PANELS. The authentic Richard Coman testimony page at left and "
            "the Salem courtroom engraving at right are static photographic source objects. They remain in the "
            "exact same screen coordinates, scale and appearance for all 144 frames. Do not animate, redraw, rewrite, "
            "morph, crop, replace, enlarge, open or alter a single mark inside them. Transform only the empty constructed "
            "foreground below and between those panels. One private quill-shadow leaves the testimony "
            "mount and crosses the empty witness rail; as it crosses, it branches into many faceless public shadows "
            "that converge around the rail, turning an isolated perception into collective accusation. At the final "
            "beat the shadows separate again, leaving the rail empty and the sources untouched. Camera completely "
            "locked; depth comes only from moving foreground shadows, never a zoom or parallax. No spectral creature, moving source figures, invented "
            "writing, labels, guilt stamp, text or crushed blacks."
        ),
        "use": "S1-S2/S8: private Erfahrung wird durch Institution und Öffentlichkeit umgeformt",
    },
    {
        "output": "CLIP004_FEEDBACK_ENTITY.mp4",
        "start": "IMG017_FEAR_SLEEP_FEEDBACK_LOOP_BASE.png",
        "person": "disallow",
        "prompt": (
            "Six-second SUBJECTIVE FEEDBACK-MODEL beginning exactly from the supplied conceptual frame. The four "
            "stations remain materially recognizable while the model becomes alive: the eye aperture opens, its "
            "shadow flows along the circular graphite fibers toward the tense upright silhouette; the broken clock "
            "shadow accelerates, then the folded dark cloth rises as pressure. Those accumulated shadows detach as "
            "one ambiguous negative-space entity and travel once around the loop, growing denser at each station. "
            "Before it becomes a literal being, the open eye interrupts the circuit and the entity dissolves back "
            "into separate paper shadows. A slight camera arc reveals real layer depth; this is one possible model, "
            "not universal causality. No bed, monster, glowing eyes, new person, arrows, energy beam, text or flat zoom."
        ),
        "use": "S7-S8: Angst–Schlaf–Deutung als sich selbst verstärkender Kreislauf",
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


def post(url: str, payload: dict[str, Any], retries: int = 8) -> dict[str, Any]:
    waits = [10, 20, 30, 45, 60, 90, 120]
    for attempt in range(retries):
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token()}",
                "Content-Type": "application/json; charset=utf-8",
            },
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


def read_state() -> dict[str, Any]:
    if STATE_FILE.is_file():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def write_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def submit(job: dict[str, str]) -> str:
    start_path = SERIES / job["start"]
    if not start_path.is_file():
        raise FileNotFoundError(start_path)
    payload = {
        "instances": [
            {
                "prompt": job["prompt"],
                "image": {
                    "bytesBase64Encoded": base64.b64encode(start_path.read_bytes()).decode("ascii"),
                    "mimeType": "image/png",
                },
            }
        ],
        "parameters": {
            "aspectRatio": "16:9",
            "durationSeconds": 6,
            "enhancePrompt": job.get("enhance", True),
            "generateAudio": False,
            "negativePrompt": NEGATIVE,
            "personGeneration": job["person"],
            "resolution": "1080p",
            "sampleCount": 1,
        },
    }
    response = post(endpoint("predictLongRunning"), payload)
    operation = response.get("name")
    if not operation:
        raise RuntimeError(f"No operation name: {response}")
    return str(operation)


def poll(operation: str) -> dict[str, Any]:
    return post(endpoint("fetchPredictOperation"), {"operationName": operation})


def save_video(job: dict[str, str], response: dict[str, Any]) -> pathlib.Path:
    body = response.get("response") or {}
    videos = body.get("videos") or body.get("generatedVideos") or []
    if not videos:
        raise RuntimeError(f"No videos in response: {json.dumps(response)[:1500]}")
    item = videos[0]
    if "video" in item and isinstance(item["video"], dict):
        item = item["video"]
    encoded = item.get("bytesBase64Encoded") or item.get("videoBytes") or item.get("bytes_base64_encoded")
    output = SERIES / job["output"]
    if encoded:
        output.write_bytes(base64.b64decode(encoded))
        return output
    uri = item.get("gcsUri") or item.get("uri")
    if uri and str(uri).startswith("gs://"):
        subprocess.run(["gcloud", "storage", "cp", str(uri), str(output)], check=True, shell=True)
        return output
    raise RuntimeError(f"Video response contains neither bytes nor GCS URI: {item}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="")
    parser.add_argument("--poll-seconds", type=int, default=20)
    args = parser.parse_args()
    chosen = [job for job in JOBS if not args.only or job["output"] == args.only]
    if not chosen:
        raise SystemExit("No matching job")

    state = read_state()
    for job in chosen:
        output = SERIES / job["output"]
        if output.is_file() and output.stat().st_size > 100_000:
            print(f"SKIP complete {output.name}", flush=True)
            continue
        record = state.setdefault(job["output"], {})
        if not record.get("operation"):
            print(f"SUBMIT {job['output']} <- {job['start']}", flush=True)
            record.update(
                operation=submit(job),
                start=job["start"],
                prompt=job["prompt"],
                use=job["use"],
                duration=6,
                resolution="1080p",
            )
            write_state(state)
            print(f"OP {record['operation']}", flush=True)

    pending = [job for job in chosen if not (SERIES / job["output"]).is_file()]
    while pending:
        for job in list(pending):
            record = state[job["output"]]
            response = poll(record["operation"])
            if response.get("done"):
                if response.get("error"):
                    raise RuntimeError(f"{job['output']}: {response['error']}")
                output = save_video(job, response)
                record.update(done=True, output=str(output), bytes=output.stat().st_size)
                write_state(state)
                pending.remove(job)
                print(f"OK {output.name} {output.stat().st_size} bytes", flush=True)
            else:
                print(f"WAIT {job['output']}", flush=True)
        if pending:
            time.sleep(max(10, args.poll_seconds))


if __name__ == "__main__":
    main()
