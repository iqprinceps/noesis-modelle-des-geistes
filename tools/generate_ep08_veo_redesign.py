#!/usr/bin/env python3
"""Generate four meaningful-motion EP08 clips from approved conceptual start frames."""

from __future__ import annotations

import concurrent.futures
import json
import os
from pathlib import Path

from generate_ep08_veo import poll, save_video, submit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4" / "IMAGE_GENERATION_KIT" / "03_GENERATED_OUTPUT"

CLIPS = [
    {
        "filename": "CLIP001_RADIO_NETWORK_ENTITY.mp4",
        "start": "IMG002_4500_MESSAGES_MATERIAL.png",
        "prompt": "Six-second MEDIA-MODEL concept shot with genuine internal transformation, preserving the radio studio, paper stacks, CRT and all physical geometry. Visible but elegant amber radio-wave pulses leave the microphone and travel through the paper stacks; each pulse activates a few blank CRT/forum-window rectangles in depth. Separate soft shadow fragments appear only on different papers and screens, then align across those disconnected surfaces into one ambiguous standing silhouette for a brief beat before breaking apart again. Slow lateral camera parallax, not a flat zoom. No living creature, no new person, no readable text, logos, labels, object duplication, paper warping, horror effect or audio.",
        "position": "S1–S2, Radio → Nachrichten → Forum → kollektive Form",
    },
    {
        "filename": "CLIP002_SHADOW_DETACHES.mp4",
        "start": "SHOT05_HAT_SHADOW_EMPTY_ROOM.png",
        "prompt": "Six-second SUBJECTIVE shot with one physically clear impossible event. Preserve the exact empty room, coat rack, hat, lamp, wall, bed and light source. First the hat-and-coat shadow behaves normally. Then only the shadow edge quietly detaches from the coat rack against the light logic, glides independently across the wall and through the visible doorway threshold, pauses, and snaps softly back onto the real object shadow by the final moment. The coat rack and every physical object remain completely still. Locked camera with tiny natural breathing, not Ken Burns. No person, creature, extra shadow, object morphing, text, logo, flicker, jump scare or audio.",
        "position": "S3–S4, subjektiver Moment: Schatten widerspricht kurz der Lichtlogik",
    },
    {
        "filename": "CLIP003_MEMORY_RECONSTRUCTION.mp4",
        "start": "IMG014_MEMORY_RECONSTRUCTION_LAYERS.png",
        "prompt": "Six-second SUBJECTIVE memory-reconstruction shot with visible reassembly. Preserve the same adult person, face identity, room fragments and translucent photographic panes. The panes slide, rotate and reorder in real three-dimensional depth: window, face profile, bed edge and shadow fragment first contradict each other, then briefly reconstruct a coherent room-and-body memory. Only at the peak alignment does a simple hat-brim edge emerge from the overlap of two panes; it is an optical reconstruction, never a new person. The layers then separate slightly again. Slow camera arc with parallax. No facial mutation, duplicated anatomy, new people, text, logo, supernatural glow, abrupt morphing or audio.",
        "position": "S3–S4, Erinnerung wird sichtbar rekonstruiert und erwartet die Hutkante",
        "personGeneration": "allow_adult",
    },
    {
        "filename": "CLIP004_COLLECTIVE_IMAGE_LOOP.mp4",
        "start": "IMG020_HAT_MAN_REPORT_VARIATIONS.png",
        "prompt": "Six-second MEDIA-MODEL loop with genuine convergence and dispersal. Preserve the tabletop, papers, charcoal medium and warm practical light. The many visibly different hand-drawn silhouettes lift as separate translucent charcoal layers just above their papers and drift toward the center. Their differing hats, shoulders and proportions briefly converge into one shared Hat-Man-shaped negative-space contour, hold for half a second, then scatter outward into a loose network of distinct report fragments and settle near their original sheets. Gentle overhead camera orbit with parallax, not a flat zoom. No literal man, no living drawings, no readable writing, new papers, logos, hands, horror face, geometry melt or audio.",
        "position": "S5–S8, viele Berichte konvergieren zur Meme-Form und zerstreuen sich wieder",
        "personGeneration": "allow_adult",
    },
]


def produce(clip: dict, project: str) -> dict:
    destination = OUTPUT / clip["filename"]
    if destination.is_file():
        return {"file": destination.name, "bytes": destination.stat().st_size, "status": "EXISTING"}
    operation_name = submit(clip, project, "global")
    operation = poll(operation_name, project, "global")
    destination = save_video(clip, operation)
    return {"file": destination.name, "bytes": destination.stat().st_size, "operation": operation_name}


def main() -> int:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT is not set")
    failures = []
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(produce, clip, project): clip for clip in CLIPS}
        for future in concurrent.futures.as_completed(futures):
            clip = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(json.dumps(result), flush=True)
            except Exception as exc:  # noqa: BLE001
                failures.append({"file": clip["filename"], "error": str(exc)})
                print(json.dumps(failures[-1]), flush=True)
    print(json.dumps({"results": results, "failures": failures}, indent=2), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
