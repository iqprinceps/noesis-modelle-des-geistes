#!/usr/bin/env python3
"""Cached EP01 still generation through Vertex Nano Banana Pro.

The script keeps prompt lineage beside every image, never overwrites accepted
finals unless --force is supplied, limits concurrency to two jobs, and retries
transient failures with exponential backoff.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image


MODEL = "gemini-3-pro-image"
ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP01_KOZYREV"
JOBS_PATH = EP / "04_ASSETS" / "GENERATION_JOBS.json"
OUT = EP / "04_ASSETS" / "GENERATED" / "NANO_BANANA_PRO"
META = EP / "04_ASSETS" / "METADATA"
ANCHOR = OUT / "KZ_EN_HERO01.png"
PATENT_SPIRAL = EP / "04_SOURCES" / "RENDERS" / "PATENT" / "RU2122446C1_FIG3_SPIRAL_UPRIGHT.png"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def endpoint(project: str) -> str:
    return (
        f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/global/"
        f"publishers/google/models/{MODEL}:generateContent"
    )


def load() -> tuple[dict, list[dict]]:
    data = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    return data["geometry_lock"], data["still_jobs"]


def prompt_for(job: dict, geometry: dict) -> str:
    taxonomy = "photorealistic-natural"
    if job["class"] in {"model", "concept"}:
        taxonomy = "scientific-educational"
    if job["class"] == "target":
        taxonomy = "photorealistic-natural"
    lines = [
            f"Use case: {taxonomy}",
            "Asset type: evidence-driven mystery documentary still",
            f"Primary request: {job['prompt']}",
            "Style/medium: high-end factual documentary photography with realistic optics, material grain, and natural midtones",
            "Composition/framing: single finished frame; preserve subject scale and usable edit margins",
            "Constraints: no captions, labels, subtitles, logos, signatures, watermarks, invented readable text, fake archive marks, or interface text; anatomically natural people and hands; historically plausible props; the image is a reconstruction base and must never look like authenticated archive",
        ]
    if job["class"] == "target":
        lines.extend(
            [
                "Controlled-test requirement: this is a standalone target photograph only. Show no laboratory, chamber, apparatus, workshop, camera operator, frame, screen, card, envelope, or surrounding test context.",
                "Avoid: collage, display mockup, border, futuristic styling, fantasy art, crushed blacks, extra focal subjects.",
            ]
        )
    else:
        lines.extend(
            [
                f"Geometry lock: {geometry['description']}",
                f"Visual continuity: {geometry['palette']}",
                "Avoid: futuristic chamber, nautilus shell, copper coil, glass pod, laser, aura, meditation pose, fantasy game art, generic esoteric stock imagery, crushed blacks, duplicated limbs, warped panel geometry",
            ]
        )
    return "\n".join(lines)


def image_part(path: Path) -> dict:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return {
        "inlineData": {
            "mimeType": mime,
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


def decode_image(data: dict) -> tuple[bytes, str]:
    notes: list[str] = []
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"]), " ".join(notes).strip()
            if part.get("text"):
                notes.append(part["text"])
    raise RuntimeError("No image returned: " + json.dumps(data.get("promptFeedback", data))[:1600])


def destination(job: dict, mode: str) -> Path:
    suffix = "_preview" if mode == "preview" else ""
    return OUT / f"{job['id']}{suffix}.png"


def generate_one(job: dict, geometry: dict, project: str, mode: str, force: bool) -> dict:
    dest = destination(job, mode)
    meta = META / f"{job['id']}_{mode}.json"
    if dest.exists() and meta.exists() and not force:
        with Image.open(dest) as im:
            return {"id": job["id"], "status": "CACHED", "size": list(im.size), "path": str(dest)}

    parts = [{"text": prompt_for(job, geometry)}]
    if job["id"] == "KZ_EN_HERO01":
        if not PATENT_SPIRAL.exists():
            raise FileNotFoundError(f"Patent geometry reference missing: {PATENT_SPIRAL}")
        parts.append(image_part(PATENT_SPIRAL))
        parts[0]["text"] += (
            "\nInput images: Image 1 is original patent figure 3 and is a geometry reference only. "
            "Translate its one continuous open spiral wall into a plausible full-scale apparatus. "
            "Do not copy the page, callout numbers, margins, lettering, or drawing style."
        )
    # All later chamber images inherit the accepted anchor. Targets do not.
    elif job["class"] != "target":
        if not ANCHOR.exists():
            raise FileNotFoundError(f"Accepted geometry anchor missing: {ANCHOR}")
        parts.append(image_part(ANCHOR))
        parts[0]["text"] += (
            "\nInput images: Image 1 is the accepted geometry and material reference only. "
            "Preserve its exact panel count, spiral opening, platform, scale, aluminum finish, and documentary grade; "
            "change only the requested camera, action, or configuration."
        )

    payload = {
        "contents": [{"role": "USER", "parts": parts}],
        "generationConfig": {
            "candidateCount": 1,
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": job.get("aspect", "16:9"),
                "imageSize": "1K" if mode == "preview" else "2K",
            },
        },
    }
    prompt_hash = sha256_bytes(parts[0]["text"].encode("utf-8"))
    last_error: Exception | None = None
    for attempt in range(1, 5):
        try:
            response = requests.post(
                endpoint(project),
                headers={"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"},
                json=payload,
                timeout=480,
            )
            if response.status_code >= 400:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1400]}")
            image_bytes, response_text = decode_image(response.json())
            OUT.mkdir(parents=True, exist_ok=True)
            META.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(image_bytes)
            with Image.open(dest) as im:
                width, height = im.size
                im.verify()
            record = {
                "asset_id": job["id"],
                "status": "GENERATED",
                "provider": "Google Vertex AI",
                "model": MODEL,
                "provider_seed": "unsupported",
                "mode": mode,
                "image_size_request": "1K" if mode == "preview" else "2K",
                "aspect_ratio": job.get("aspect", "16:9"),
                "geometry_lock": geometry["id"],
                "prompt": parts[0]["text"],
                "prompt_sha256": prompt_hash,
                "reference_images": ([str(PATENT_SPIRAL)] if job["id"] == "KZ_EN_HERO01" else [str(ANCHOR)]) if len(parts) > 1 else [],
                "created_utc": utc_now(),
                "attempt": attempt,
                "response_text": response_text,
                "output": str(dest),
                "output_sha256": sha256_bytes(image_bytes),
                "width": width,
                "height": height,
                "bytes": len(image_bytes),
            }
            meta.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return {"id": job["id"], "status": "GENERATED", "size": [width, height], "path": str(dest)}
        except Exception as exc:  # continue after transient API failures
            last_error = exc
            if attempt < 4:
                time.sleep(min(45, 3 * (2 ** (attempt - 1))))
    raise RuntimeError(f"{job['id']} failed after 4 attempts: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", help="Comma-separated asset IDs; default is all")
    parser.add_argument("--mode", choices=["preview", "final"], default="final")
    parser.add_argument("--max-workers", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    geometry, jobs = load()
    selected = {x.strip() for x in args.ids.split(",")} if args.ids else None
    jobs = [j for j in jobs if selected is None or j["id"] in selected]
    if not jobs:
        raise SystemExit("No matching jobs")
    workers = max(1, min(2, args.max_workers))
    print(f"model={MODEL} mode={args.mode} jobs={len(jobs)} workers={workers}", flush=True)
    failures: list[dict] = []
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(generate_one, j, geometry, project, args.mode, args.force): j for j in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(json.dumps(result, ensure_ascii=False), flush=True)
            except Exception as exc:
                failures.append({"id": job["id"], "error": str(exc)})
                print(json.dumps(failures[-1], ensure_ascii=False), flush=True)
    log = {
        "run_utc": utc_now(),
        "mode": args.mode,
        "results": sorted(results, key=lambda x: x["id"]),
        "failures": failures,
    }
    META.mkdir(parents=True, exist_ok=True)
    (META / f"vertex_run_{args.mode}.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
