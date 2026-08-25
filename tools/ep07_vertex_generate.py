#!/usr/bin/env python3
"""Generate the complete EP07 sleep-paralysis image batch with Vertex AI.

Outputs are written to a temporary QA directory first. Approved files are copied
to the episode output folder by the production QA pass, never directly by this
generator.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import csv
import json
import os
import pathlib
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT"
PROMPTS = KIT / "01_PROMPTS"
ASSETS = KIT / "02_ASSETS"
RAW = ROOT / "tmp" / "imagegen" / "ep07_vertex_raw"
PDF_RENDERS = ROOT / "tmp" / "pdfs" / "ep07"
QUEUE = KIT / "GENERATION_QUEUE.csv"

MODEL = "gemini-3-pro-image"
LOCATION = "global"

GLOBAL_LOCK = """Production constraints: horizontal cinematic 16:9 frame at 2K.
This is a documentary visual, not horror-poster art. Keep natural lifted midtones,
readable shadow detail, and at least one warm or neutral practical-light anchor.
Never crush large areas into black and never use a uniformly bleak color grade.
Any human body must have plausible anatomy: one head, two arms, two hands, two legs,
natural joints and fingers, with no duplicate limbs, merged bodies or extra people.
Keep each bed, room and object spatially coherent. Do not add logos, captions,
watermarks, interface words, invented handwriting, fake labels, random symbols or
legible generated text. Existing writing inside a supplied archival source image may
remain only as unchanged photographic texture. No split-screen borders unless the
prompt explicitly requests panels. No glowing supernatural being, jump-scare face,
fantasy effects, excessive fog, CGI sheen, plastic skin or modern objects in historical
rooms. Preserve empty negative space intended for editor-added labels."""


_token_cache: dict[str, Any] = {}
_token_lock = threading.Lock()


def access_token() -> str:
    now = time.time()
    with _token_lock:
        if _token_cache.get("expires", 0) > now + 60:
            return str(_token_cache["value"])
        completed = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            shell=True,
            timeout=60,
        )
        value = completed.stdout.strip()
        if not value:
            raise RuntimeError("No ADC access token; run gcloud auth application-default login")
        _token_cache.update(value=value, expires=now + 3300)
        return value


def project_id() -> str:
    value = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not value:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set")
    return value


def post_json(url: str, payload: dict[str, Any], retries: int = 10) -> dict[str, Any]:
    waits = [10, 20, 30, 45, 60, 90, 120, 150, 180]
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
            with urllib.request.urlopen(request, timeout=420) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:800]
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                wait = waits[min(attempt, len(waits) - 1)]
                print(f"  retry HTTP {exc.code} in {wait}s ({attempt + 2}/{retries})", flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {exc.code}: {body}") from None
        except Exception:
            if attempt >= retries - 1:
                raise
            wait = waits[min(attempt, len(waits) - 1)]
            print(f"  transport retry in {wait}s ({attempt + 2}/{retries})", flush=True)
            time.sleep(wait)
    raise RuntimeError("generation failed after retries")


def parse_prompt_documents() -> dict[str, str]:
    found: dict[str, str] = {}
    pattern = re.compile(
        r"(?ms)^(EP07_(?:IMG\d{3}|RSV\d{2})_[^\r\n]+\.png)\s*\r?\n"
        r"Referenz:\s*[^\r\n]+\s*\r?\nPrompt:\s*\r?\n"
        r"(.+?)(?=\r?\n\r?\n(?:EP07_(?:IMG\d{3}|RSV\d{2})_|---)|\Z)"
    )
    for path in sorted(PROMPTS.glob("NANOBANANA_PROMPTS_V4_*.md")):
        for original_name, prompt in pattern.findall(path.read_text(encoding="utf-8")):
            found[original_name] = prompt.strip()
    return found


def final_name(original_name: str) -> str:
    image_match = re.match(r"EP07_(IMG\d{3}_.+)", original_name)
    if image_match:
        return image_match.group(1)
    reserve_match = re.match(r"EP07_RSV(\d{2})_(.+)", original_name)
    if reserve_match:
        return f"SHOT{reserve_match.group(1)}_{reserve_match.group(2)}"
    raise ValueError(original_name)


def reference_path(name: str) -> pathlib.Path:
    if name == "EP07_Richard_Coman_Testimony_v_Bridget_Bishop_1692.pdf":
        return PDF_RENDERS / "Richard_Coman_page1.png"
    if name == "EP07_Bridget_Bishop_Examination_1692.pdf":
        return PDF_RENDERS / "Bridget_Bishop_page1.png"
    return ASSETS / name


def load_jobs() -> list[dict[str, Any]]:
    prompts = parse_prompt_documents()
    jobs: list[dict[str, Any]] = []
    with QUEUE.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["kind"] == "STYLE_MASTER":
                continue
            original_name = row["output_filename"]
            if original_name not in prompts:
                raise RuntimeError(f"prompt missing for {original_name}")
            refs = [item.strip() for item in row["references"].split(";") if item.strip() and item.strip() != "Keine"]
            ref_paths = [reference_path(name) for name in refs]
            missing = [str(path) for path in ref_paths if not path.is_file()]
            if missing:
                raise RuntimeError(f"missing references for {original_name}: {missing}")
            jobs.append(
                {
                    "order": int(row["order"]),
                    "kind": row["kind"],
                    "original_name": original_name,
                    "output_name": final_name(original_name),
                    "prompt": prompts[original_name],
                    "reference_names": refs,
                    "reference_paths": ref_paths,
                }
            )
    return jobs


def mime_type(path: pathlib.Path) -> str:
    return "image/png" if path.suffix.lower() == ".png" else "image/jpeg"


def role_for_reference(name: str, index: int) -> str:
    if name.startswith("STYLE_"):
        return (
            f"Image {index} is a style reference only. Match its restrained documentary palette, "
            "natural lighting, texture and tonal readability. Do not copy its people, room, objects or composition."
        )
    return (
        f"Image {index} is an authentic historical source object. If the prompt calls for it, preserve its "
        "content, crop proportions, material edges and visible marks faithfully as a photographed insert. "
        "Do not redraw, rewrite, beautify, animate or invent detail inside it."
    )


def generate(job: dict[str, Any], overwrite: bool = False) -> pathlib.Path:
    RAW.mkdir(parents=True, exist_ok=True)
    output = RAW / job["output_name"]
    if output.is_file() and not overwrite:
        print(f"SKIP {output.name}", flush=True)
        return output

    parts: list[dict[str, Any]] = []
    roles: list[str] = []
    for index, (name, path) in enumerate(zip(job["reference_names"], job["reference_paths"]), start=1):
        parts.append(
            {
                "inlineData": {
                    "mimeType": mime_type(path),
                    "data": base64.b64encode(path.read_bytes()).decode("ascii"),
                }
            }
        )
        roles.append(role_for_reference(name, index))

    prompt = (
        "Use case: historical-scene / conceptual documentary still\n"
        "Asset type: German YouTube documentary episode shot\n"
        + ("Input images:\n" + "\n".join(roles) + "\n" if roles else "")
        + f"Primary request:\n{job['prompt']}\n\n{GLOBAL_LOCK}"
    )
    parts.append({"text": prompt})

    url = (
        f"https://aiplatform.googleapis.com/v1/projects/{project_id()}"
        f"/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"},
        },
    }
    print(f"GEN {job['output_name']} ({len(parts) - 1} refs)", flush=True)
    response = post_json(url, payload)
    images: list[bytes] = []
    for candidate in response.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                images.append(base64.b64decode(inline["data"]))
    if not images:
        finish = (response.get("candidates") or [{}])[0].get("finishReason", "unknown")
        raise RuntimeError(f"no image returned for {job['output_name']} (finishReason={finish})")
    output.write_bytes(images[0])
    print(f"OK  {output.name} {output.stat().st_size} bytes", flush=True)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--only", default="", help="comma-separated output filenames or IMG/SHOT prefixes")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    jobs = load_jobs()
    if args.only:
        wanted = {item.strip() for item in args.only.split(",") if item.strip()}
        jobs = [job for job in jobs if job["output_name"] in wanted or pathlib.Path(job["output_name"]).stem in wanted]
    if args.list:
        for job in jobs:
            print(f"{job['order']:02d} {job['kind']:7s} {job['output_name']} refs={len(job['reference_paths'])}")
        return
    if not jobs:
        raise SystemExit("no matching jobs")

    failures: list[tuple[str, str]] = []
    with cf.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        future_map = {pool.submit(generate, job, args.overwrite): job for job in jobs}
        for future in cf.as_completed(future_map):
            job = future_map[future]
            try:
                future.result()
            except Exception as exc:
                failures.append((job["output_name"], str(exc)))
                print(f"FAIL {job['output_name']}: {exc}", flush=True)
    if failures:
        print(json.dumps(failures, ensure_ascii=False, indent=2), flush=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
