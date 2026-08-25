#!/usr/bin/env python3
"""Generate EP08 stills through Vertex AI Gemini 3 Pro Image (Nano Banana Pro)."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import mimetypes
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from PIL import Image


MODEL = "gemini-3-pro-image"
ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT"
ASSETS = KIT / "02_ASSETS"
OUTPUT = KIT / "03_GENERATED_OUTPUT"
QUEUE = KIT / "GENERATION_QUEUE.csv"


def access_token() -> str:
    gcloud = os.environ.get(
        "GCLOUD_CMD",
        r"C:\Users\iQPrinceps\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
    )
    result = subprocess.run(
        [gcloud, "auth", "application-default", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def mime_type(path: Path) -> str:
    guessed = mimetypes.guess_type(path.name)[0]
    if guessed == "image/svg+xml":
        raise ValueError(f"SVG is not supported as a Gemini image input: {path}")
    return guessed or "application/octet-stream"


def image_part(path: Path) -> dict:
    return {
        "inlineData": {
            "mimeType": mime_type(path),
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


def read_prompt(source: Path, filename: str) -> str:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    for index, line in enumerate(lines):
        if line.strip().rstrip() != filename:
            continue
        for prompt_index in range(index + 1, min(index + 8, len(lines))):
            if lines[prompt_index].strip().startswith("Prompt:"):
                for body_index in range(prompt_index + 1, len(lines)):
                    body = lines[body_index].strip()
                    if body:
                        return body
        break
    raise ValueError(f"Prompt body not found for {filename} in {source}")


def load_jobs() -> list[dict]:
    with QUEUE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    jobs = []
    for row in rows:
        if row["kind"] not in {"MAIN", "RESERVE"}:
            continue
        source = KIT / Path(row["prompt_source"])
        refs = [item.strip() for item in row["references"].split(";") if item.strip() and item.strip() != "Keine"]
        jobs.append(
            {
                **row,
                "order": int(row["order"]),
                "source": source,
                "refs": refs,
                "prompt": read_prompt(source, row["output_filename"]),
            }
        )
    return jobs


def request_parts(job: dict) -> list[dict]:
    roles = []
    parts = []
    for number, ref in enumerate(job["refs"], start=1):
        path = ASSETS / ref
        if not path.is_file():
            raise FileNotFoundError(path)
        if ref.startswith("STYLE_"):
            role = "style, color, lighting, texture and documentary tone only; do not copy its layout or subjects"
        elif "Art_Bell" in ref:
            role = "identity reference for Art Bell only; preserve recognizable adult facial identity without copying pose or background"
        else:
            role = "factual visual reference only"
        roles.append(f"Reference image {number} ({ref}): {role}.")
        parts.append(image_part(path))

    guardrail = (
        "Generate exactly one finished 2K landscape documentary still in 16:9. "
        "The supplied images are references, not edit targets. "
        "Follow the requested scene and all negative constraints literally. "
        "Do not add captions, labels, subtitles, logos, signatures, watermarks, invented interface words, "
        "or decorative typography. Keep people anatomically natural, with correct hands and no duplicated limbs. "
        "Use lifted natural midtones and visible shadow detail suitable for YouTube viewing; avoid crushed blacks "
        "and a uniformly bleak grade."
    )
    text = "\n".join(roles + [guardrail, "", job["prompt"]])
    return [{"text": text}, *parts]


def endpoint(project: str, location: str) -> str:
    return (
        f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/"
        f"publishers/google/models/{MODEL}:generateContent"
    )


def generate(job: dict, project: str, location: str, overwrite: bool, attempts: int = 4) -> dict:
    destination = OUTPUT / final_filename(job)
    if destination.exists() and not overwrite:
        with Image.open(destination) as image:
            return {"status": "SKIPPED", "width": image.width, "height": image.height, "bytes": destination.stat().st_size}

    payload = {
        "contents": [{"role": "USER", "parts": request_parts(job)}],
        "generationConfig": {
            "candidateCount": 1,
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"},
        },
    }
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.post(
                endpoint(project, location),
                headers={"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"},
                json=payload,
                timeout=420,
            )
            if response.status_code >= 400:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1200]}")
            data = response.json()
            image_bytes = None
            response_text = []
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    inline = part.get("inlineData") or part.get("inline_data")
                    if inline and inline.get("data"):
                        image_bytes = base64.b64decode(inline["data"])
                        break
                    if part.get("text"):
                        response_text.append(part["text"])
                if image_bytes:
                    break
            if not image_bytes:
                feedback = json.dumps(data.get("promptFeedback", data), ensure_ascii=False)[:1600]
                raise RuntimeError(f"No image returned. Response: {feedback}")
            OUTPUT.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(image_bytes)
            with Image.open(destination) as image:
                width, height = image.size
                image.verify()
            return {
                "status": "GENERATED",
                "width": width,
                "height": height,
                "bytes": destination.stat().st_size,
                "response_text": " ".join(response_text).strip(),
            }
        except Exception as exc:  # noqa: BLE001 - CLI reports per-job failure and retries
            last_error = exc
            if attempt < attempts:
                time.sleep(min(30, 4 * attempt))
    raise RuntimeError(f"Generation failed after {attempts} attempts: {last_error}")


def final_filename(job: dict) -> str:
    source = job["output_filename"]
    if job["kind"] == "MAIN":
        return source.removeprefix("EP08_")
    if job["kind"] == "RESERVE":
        stem = Path(source).stem.removeprefix("EP08_RSV")
        number, _, description = stem.partition("_")
        return f"SHOT{int(number):02d}_{description}.png"
    return source.removeprefix("EP08_")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", help="Comma-separated queue orders, e.g. 4,5,6")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--model-info", action="store_true")
    parser.add_argument("--dump-json", action="store_true", help="Print selected jobs for the built-in fallback")
    args = parser.parse_args()

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    if location != "global":
        print(f"Forcing global location for {MODEL} (configured value was {location})", file=sys.stderr)
        location = "global"

    selected = None
    if args.orders:
        selected = {int(item.strip()) for item in args.orders.split(",") if item.strip()}
    jobs = [job for job in load_jobs() if selected is None or job["order"] in selected]
    if not jobs:
        raise SystemExit("No matching MAIN/RESERVE jobs")

    if args.dump_json:
        print(
            json.dumps(
                [
                    {
                        "order": job["order"],
                        "filename": final_filename(job),
                        "prompt": request_parts(job)[0]["text"],
                        "references": [str(ASSETS / ref) for ref in job["refs"]],
                    }
                    for job in jobs
                ],
                ensure_ascii=False,
            )
        )
        return 0

    print(f"Model={MODEL} project={project} location={location} jobs={len(jobs)}")
    failures = []
    for index, job in enumerate(jobs, start=1):
        name = final_filename(job)
        print(f"[{index}/{len(jobs)}] {name}", flush=True)
        try:
            result = generate(job, project, location, args.overwrite)
            print(f"  {result['status']} {result['width']}x{result['height']} {result['bytes']} bytes", flush=True)
        except Exception as exc:  # noqa: BLE001 - continue batch and summarize failures
            failures.append({"order": job["order"], "filename": name, "error": str(exc)})
            print(f"  FAILED {exc}", file=sys.stderr, flush=True)

    if failures:
        print(json.dumps({"failures": failures}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
