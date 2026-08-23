#!/usr/bin/env python3
"""Gateway Image Generation — NanoBanana Pro (Vertex AI) Integration.

Generates cohesive visuals for the Gateway documentary using:
- Reference images for consistent style
- Style key matching the documentary look
- Semantic prompts based on script content
"""

from __future__ import annotations

import argparse
import base64
import json
import pathlib
import subprocess
import sys
import time
from typing import Any

import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V5" / "visuals" / "generated"
REF_DIR = ROOT / "06_PRODUCTION" / "EP02_GATEWAY_V5" / "visuals" / "references"
BATCH_DIR = ROOT / "tools" / "gateway_batches"

# Gateway Style Key — cohesive documentary look
STYLE_KEY = """Visual style: Cold, clinical documentary aesthetic. Desaturated colors with
subtle blue-grey tint. Film grain texture. High contrast shadows. Institutional lighting
reminiscent of 1980s government facilities. Clean composition with negative space.
No decorative elements. Professional archival quality.

Color palette: Deep navy (#041114), cold grey (#2a3a3f), muted cyan (#5bd2d3),
off-white (#eeebe0), gold accent (#e0ae47) used sparingly for emphasis.

Mood: Authoritative, measured, slightly unsettling. The viewer should feel they are
looking at evidence, not entertainment."""

NEGATIVE = """No warm colors, no saturated tones, no cheerful atmosphere, no modern UI elements,
no watermarks, no text overlays, no logos, no stock photo aesthetics, no Instagram filters,
no HDR, no lens flare, no bokeh, no shallow depth of field, no artistic interpretation,
no fantasy elements, no sci-fi aesthetics"""

# Model configuration
MODELLE = {
    "pro": ("gemini-3-pro-image", "global"),
    "flash": ("gemini-2.5-flash-image", "global"),
}

PREISE = {
    "gemini-3-pro-image": {"1k": 0.134, "2k": 0.134, "4k": 0.24},
    "gemini-2.5-flash-image": {"1k": 0.039, "2k": 0.039, "4k": 0.039},
}


def die(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(2)


# --------------------------------------------------------------------------- #
# Authentication
# --------------------------------------------------------------------------- #

_token_cache: dict[str, Any] = {}


def token() -> str:
    now = time.time()
    if _token_cache.get("exp", 0) > now + 60:
        return _token_cache["val"]
    try:
        out = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, shell=True, timeout=60,
        )
    except Exception as exc:
        die(f"gcloud not available: {exc}")
    tok = out.stdout.strip()
    if not tok:
        die("No ADC token. Run 'gcloud auth application-default login' first.")
    _token_cache.update(val=tok, exp=now + 3300)
    return tok


def project() -> str:
    import os
    p = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not p:
        die("GOOGLE_CLOUD_PROJECT is not set.")
    return p


def post(url: str, payload: dict[str, Any], timeout: int = 300,
         retries: int = 6) -> dict[str, Any]:
    """POST with retry on 429 and 5xx."""
    wait_times = [20, 40, 80, 160, 300]
    for attempt in range(retries):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:400]
            is_last = attempt >= retries - 1
            if e.code in (429, 500, 503, 504) and not is_last:
                w = wait_times[min(attempt, len(wait_times) - 1)]
                print(f"  Quota reached ({e.code}). Waiting {w}s [attempt {attempt + 2}/{retries}]",
                      flush=True)
                time.sleep(w)
                continue
            raise RuntimeError(f"HTTP {e.code}: {body}") from None
        except Exception:
            if attempt >= retries - 1:
                raise
            time.sleep(wait_times[min(attempt, len(wait_times) - 1)])
    raise RuntimeError("Failed after all retries")


# --------------------------------------------------------------------------- #
# Reference images
# --------------------------------------------------------------------------- #

def load_reference(ref_name: str) -> str | None:
    """Load a reference image and return base64 encoded."""
    ref_path = REF_DIR / f"{ref_name}.png"
    if not ref_path.exists():
        # Try jpg
        ref_path = REF_DIR / f"{ref_name}.jpg"
    if not ref_path.exists():
        return None
    return base64.b64encode(ref_path.read_bytes()).decode()


def save_reference(name: str, image_bytes: bytes):
    """Save an image as a reference for future generations."""
    REF_DIR.mkdir(parents=True, exist_ok=True)
    (REF_DIR / f"{name}.png").write_bytes(image_bytes)
    print(f"  Saved reference: {name}.png")


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #

def generate_image(prompt: str, output_name: str, modell: str = "flash",
                   aspect: str = "16:9", resolution: str = "2k",
                   reference: str | None = None) -> pathlib.Path:
    """Generate a single image with the Gateway style."""
    model_id, loc = MODELLE[modell]
    host = "aiplatform" if loc == "global" else f"{loc}-aiplatform"
    url = (f"https://{host}.googleapis.com/v1/projects/{project()}"
           f"/locations/{loc}/publishers/google/models/{model_id}:generateContent")

    parts: list[dict[str, Any]] = []

    # Add reference image if provided
    if reference:
        ref_data = load_reference(reference)
        if ref_data:
            parts.append({"inlineData": {"mimeType": "image/png", "data": ref_data}})
            prompt = (f"{STYLE_KEY}\n\n{prompt}\n\n"
                      "Match the supplied reference image exactly in lighting, grain, "
                      "colour temperature, contrast and lens character. Change only what "
                      "the instruction above describes.\n\n"
                      f"Do not include: {NEGATIVE}")
        else:
            prompt = f"{STYLE_KEY}\n\n{prompt}\n\nDo not include: {NEGATIVE}"
    else:
        prompt = f"{STYLE_KEY}\n\n{prompt}\n\nDo not include: {NEGATIVE}"

    parts.append({"text": prompt})

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect,
                "imageSize": resolution.upper(),
            },
        },
    }

    r = post(url, payload)
    images: list[bytes] = []
    for cand in r.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                images.append(base64.b64decode(inline["data"]))
    if not images:
        fr = (r.get("candidates") or [{}])[0].get("finishReason", "?")
        raise RuntimeError(f"No image returned (finishReason={fr})")

    OUT.mkdir(parents=True, exist_ok=True)
    output_path = OUT / f"{output_name}.png"
    output_path.write_bytes(images[0])
    print(f"  Generated: {output_name}.png")
    return output_path


# --------------------------------------------------------------------------- #
# Gateway-specific generation jobs
# --------------------------------------------------------------------------- #

GATEWAY_JOBS = [
    # Consciousness and field visualizations
    {
        "id": "gw_consciousness_field",
        "prompt": "Abstract visualization of a consciousness field. Concentric rings of energy "
                  "emanating from a central point, suggesting information access beyond normal "
                  "space-time. Dark background with subtle blue-cyan energy patterns. "
                  "Scientific diagram aesthetic, not mystical.",
        "ref": "exhibit_4c",  # Use existing exhibit as style reference
    },
    {
        "id": "gw_time_wheel",
        "prompt": "Abstract representation of time as a wheel with spokes. Each spoke represents "
                  "a different point in time - past, present, future. Central hub glowing with "
                  "gold accent. Clean geometric design suggesting navigation through time. "
                  "Dark navy background.",
        "ref": "exhibit_5",
    },
    {
        "id": "gw_binaural_processing",
        "prompt": "Visualization of binaural beat processing in the brain. Two waveforms entering "
                  "from left and right, converging in the center to create a third perceived "
                  "frequency. Scientific illustration style with clean lines and subtle glow effects.",
        "ref": "figure_1",
    },
    {
        "id": "gw_holographic_barrier",
        "prompt": "Abstract representation of a holographic barrier or protective field. "
                  "Geometric patterns forming a semi-transparent shield. Suggests mental "
                  "defense mechanisms. Clean, institutional aesthetic.",
        "ref": "exhibit_3",
    },
    {
        "id": "gw_information_flow",
        "prompt": "Visualization of information flow between consciousness states. Abstract "
                  "data streams moving through different focus levels. Clean diagram aesthetic "
                  "with subtle energy patterns. Dark background with cyan and gold accents.",
        "ref": "exhibit_1a",
    },
    {
        "id": "gw_focus_transition",
        "prompt": "Abstract representation of transitioning between focus states. Concentric "
                  "circles representing Focus 10, 12, 15, 21. Each ring slightly different "
                  "in character. Smooth transition between states. Scientific diagram style.",
        "ref": "exhibit_4a",
    },
    {
        "id": "gw_observer_protocol",
        "prompt": "Visualization of the three-observer protocol. Three distinct viewing "
                  "positions around a central target. Each position represents a different "
                  "time perspective. Clean geometric diagram with subtle depth.",
        "ref": "exhibit_1b",
    },
    {
        "id": "gw_evidence_gap",
        "prompt": "Abstract visualization of the evidence gap between small auditory effects "
                  "and extraordinary claims. A scale or balance showing the disparity. "
                  "Clean, clinical diagram aesthetic.",
        "ref": "exhibit_4c",
    },
]


def create_references():
    """Create reference images from existing assets."""
    REF_DIR.mkdir(parents=True, exist_ok=True)

    # Map existing exhibits as references
    source_map = {
        "exhibit_1a": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_002_Exhibit_1A.png",
        "exhibit_1b": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_003_Exhibit_1B.png",
        "exhibit_1c": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_004_Exhibit_1C.png",
        "exhibit_2": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_005_Exhibit_2.png",
        "exhibit_3": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_006_Exhibit_3.png",
        "exhibit_4a": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_007_Exhibit_4A.png",
        "exhibit_4b": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_008_Exhibit_4B.png",
        "exhibit_4c": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_009_Exhibit_4C.png",
        "exhibit_5": ROOT / "04_ASSETS" / "02_CURATED" / "EP02_GATEWAY" / "APPROVED" / "GW_010_Exhibit_5.png",
        "figure_1": ROOT / "06_PRODUCTION" / "Gateway_Production" / "Assets_Research_Luna" / "GW_IMG_002_PMC7082494_Figure1_Binaural_vs_Monaural.jpg",
    }

    for name, source in source_map.items():
        target = REF_DIR / f"{name}.png"
        if not target.exists() and source.exists():
            import shutil
            shutil.copy2(source, target)
            print(f"  Reference: {name}.png")


def generate_all(modell: str = "flash", resolution: str = "2k"):
    """Generate all Gateway visuals."""
    print("Creating references...")
    create_references()

    print(f"\nGenerating {len(GATEWAY_JOBS)} images with {modell} model...")
    for job in GATEWAY_JOBS:
        try:
            generate_image(
                prompt=job["prompt"],
                output_name=job["id"],
                modell=modell,
                reference=job.get("ref"),
                resolution=resolution,
            )
        except Exception as e:
            print(f"  Failed: {job['id']}: {e}")

    print(f"\nDone! Generated images in {OUT}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Gateway Image Generation")
    sub = parser.add_subparsers(dest="command")

    # Generate command
    gen = sub.add_parser("generate", help="Generate a single image")
    gen.add_argument("name", help="Output filename (without extension)")
    gen.add_argument("prompt", help="Image prompt")
    gen.add_argument("--model", choices=["pro", "flash"], default="flash")
    gen.add_argument("--ref", help="Reference image name")
    gen.add_argument("--aspect", default="16:9")
    gen.add_argument("--resolution", default="2k", choices=["1k", "2k", "4k"])

    # Generate all
    all_cmd = sub.add_parser("all", help="Generate all Gateway visuals")
    all_cmd.add_argument("--model", choices=["pro", "flash"], default="flash")
    all_cmd.add_argument("--resolution", default="2k", choices=["1k", "2k", "4k"])

    # Create references
    sub.add_parser("refs", help="Create reference images from existing assets")

    args = parser.parse_args()

    if args.command == "generate":
        generate_image(args.prompt, args.name, args.model, args.aspect, args.resolution, args.ref)
    elif args.command == "all":
        generate_all(args.model, args.resolution)
    elif args.command == "refs":
        create_references()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
