#!/usr/bin/env python3
"""Resume-safe EP06 image generation through Vertex AI / NanoBanana Pro.

The script reads the canonical Markdown prompt batches, embeds every named local
reference, and writes only missing 2K landscape images into the episode output
folder. Existing approved files are never overwritten unless --overwrite is set.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


KIT = Path(__file__).resolve().parent
PROMPT_DIR = KIT / "01_PROMPTS"
ASSET_DIR = KIT / "02_ASSETS"
OUTPUT_DIR = KIT / "03_GENERATED_OUTPUT" / "NanoBanana_2K_Series"
RUN_LOG = OUTPUT_DIR / "VERTEX_GENERATION_LOG.json"
MODEL = "gemini-3-pro-image"
LOCATION = "global"

PROMPT_FILES = [
    PROMPT_DIR / "NANOBANANA_CORRECTION_BATCH_S1_S2.md",
    PROMPT_DIR / "NANOBANANA_PROMPTS_V4_S3_S4.md",
    PROMPT_DIR / "NANOBANANA_PROMPTS_V4_S5_S6.md",
    PROMPT_DIR / "NANOBANANA_PROMPTS_V4_S7_S8.md",
]

_token_lock = threading.Lock()
_token_cache: tuple[str, float] | None = None


def access_token() -> str:
    global _token_cache
    with _token_lock:
        now = time.time()
        if _token_cache and _token_cache[1] > now + 120:
            return _token_cache[0]
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            shell=True,
            timeout=60,
        )
        token = result.stdout.strip()
        if result.returncode or not token:
            raise RuntimeError("Vertex ADC token unavailable")
        _token_cache = (token, now + 3300)
        return token


def normalized_name(name: str) -> str:
    if name.startswith("EP06_IMG"):
        return name.removeprefix("EP06_")
    match = re.fullmatch(r"EP06_RSV(\d{2})_(.+\.png)", name)
    if match:
        return f"SHOT{match.group(1)}_{match.group(2)}"
    return name


def parse_prompts(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(?m)^((?:EP06_)?(?:IMG\d{3}|RSV\d{2})_[^\r\n]+\.png|SHOT\d{2}_[^\r\n]+\.png)\s*\r?\n"
        r"Referenz:\s*([^\r\n]+)\s*\r?\n"
        r"Prompt:\s*\r?\n"
        r"(.+?)(?=\r?\n\r?\n(?:---|## |(?:EP06_)?(?:IMG\d{3}|RSV\d{2})_|SHOT\d{2}_)|\Z)",
        re.DOTALL,
    )
    jobs: list[dict[str, object]] = []
    for name, refs, prompt in pattern.findall(text):
        jobs.append(
            {
                "filename": normalized_name(name.strip()),
                "references": [r.strip() for r in refs.split(";") if r.strip() != "Keine"],
                "prompt": " ".join(prompt.strip().split()),
                "source": path.name,
            }
        )
    return jobs


def all_jobs() -> list[dict[str, object]]:
    jobs: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in PROMPT_FILES:
        for job in parse_prompts(path):
            filename = str(job["filename"])
            if filename in seen:
                continue
            seen.add(filename)
            jobs.append(job)
    return jobs


def post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    waits = [10, 20, 40, 80, 120]
    for attempt in range(6):
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=360) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:800]
            if exc.code in {429, 500, 503, 504} and attempt < 5:
                time.sleep(waits[min(attempt, len(waits) - 1)])
                continue
            raise RuntimeError(f"HTTP {exc.code}: {body}") from None
        except Exception:
            if attempt == 5:
                raise
            time.sleep(waits[min(attempt, len(waits) - 1)])
    raise RuntimeError("Vertex request failed after retries")


def generate(job: dict[str, object], overwrite: bool) -> dict[str, object]:
    filename = str(job["filename"])
    target = OUTPUT_DIR / filename
    if target.exists() and not overwrite:
        return {**job, "status": "SKIPPED_EXISTING", "bytes": target.stat().st_size}

    parts: list[dict[str, object]] = []
    for index, reference in enumerate(job["references"], start=1):
        ref_path = ASSET_DIR / str(reference)
        if not ref_path.is_file():
            raise FileNotFoundError(f"Missing reference: {ref_path}")
        mime = mimetypes.guess_type(ref_path.name)[0] or "image/png"
        parts.append({"text": f"Reference image {index}: {ref_path.name}. Use it only in the role stated by the prompt."})
        parts.append(
            {
                "inlineData": {
                    "mimeType": mime,
                    "data": base64.b64encode(ref_path.read_bytes()).decode("ascii"),
                }
            }
        )

    production_lock = (
        "\n\nProduction lock: Return exactly one finished horizontal 16:9 documentary frame. "
        "No collage border unless explicitly requested, no captions, no letters, no numbers, "
        "no logos, no watermark. Preserve realistic anatomy, plausible room geometry and natural "
        "materials. Keep shadow detail and midtones readable on a normal phone display. Do not "
        "introduce any person, entity, object or visual effect forbidden by the scene prompt."
    )
    parts.append({"text": str(job["prompt"]) + production_lock})

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set")
    url = (
        f"https://aiplatform.googleapis.com/v1/projects/{project}/locations/{LOCATION}/"
        f"publishers/google/models/{MODEL}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"},
        },
    }
    response = post_json(url, payload)
    image_bytes: bytes | None = None
    for candidate in response.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                image_bytes = base64.b64decode(inline["data"])
                break
    if not image_bytes:
        finish = (response.get("candidates") or [{}])[0].get("finishReason", "UNKNOWN")
        raise RuntimeError(f"No image returned; finishReason={finish}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(".png.part")
    partial.write_bytes(image_bytes)
    partial.replace(target)
    return {**job, "status": "GENERATED", "bytes": len(image_bytes)}


def write_log(results: list[dict[str, object]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "episode": "EP06",
        "model": MODEL,
        "resolution": "2K",
        "aspect_ratio": "16:9",
        "generated_at_unix": int(time.time()),
        "results": sorted(results, key=lambda item: str(item["filename"])),
    }
    RUN_LOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    jobs = all_jobs()
    if args.dry_run:
        for job in jobs:
            state = "EXISTS" if (OUTPUT_DIR / str(job["filename"])).exists() else "MISSING"
            print(f"{state:7} {job['filename']} ({', '.join(job['references']) or 'no refs'})")
        print(f"TOTAL={len(jobs)}")
        return 0

    results: list[dict[str, object]] = []
    failures = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(generate, job, args.overwrite): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"[{result['status']}] {result['filename']}", flush=True)
            except Exception as exc:
                failures += 1
                result = {**job, "status": "FAILED", "error": str(exc)}
                results.append(result)
                print(f"[FAILED] {job['filename']}: {exc}", flush=True)
            write_log(results)
    print(f"DONE jobs={len(jobs)} failures={failures}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
