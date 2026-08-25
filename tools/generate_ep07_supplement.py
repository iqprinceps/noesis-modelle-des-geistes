#!/usr/bin/env python3
"""EP07 - die fehlenden Bildmotive IMG024 bis IMG060 erzeugen.

`EP07_MISSING_ASSETS_AND_PROMPTS.md`, Prioritaet C, fuehrt die Motive als
Tabelle: Dateiname, Stilreferenz und ein deutscher **Promptkern**. Der Kern
beschreibt praezise, was das Bild leisten soll - er ist aber kein fertiger
Generierungsprompt.

Dieses Skript baut daraus den vollstaendigen Auftrag: Bildfunktion, globale
Bildregeln der Folge und der gemeinsame Negativ-Lock. Der deutsche Kern bleibt
woertlich erhalten und wird nicht uebersetzt oder umgedeutet - er ist die
redaktionelle Vorgabe, nicht eine Anregung.

    python tools/generate_ep07_supplement.py --list
    python tools/generate_ep07_supplement.py --only IMG024,IMG025
    python tools/generate_ep07_supplement.py
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_ep08_vertex as base  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EPISODE = ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4"
KIT = EPISODE / "IMAGE_GENERATION_KIT"
ASSETS = KIT / "02_ASSETS"
OUTPUT = KIT / "03_GENERATED_OUTPUT" / "NanoBanana_Pro_2K_Series"
DOC = EPISODE / "EP07_MISSING_ASSETS_AND_PROMPTS.md"

STYLE_FOR = {
    "CINEMATIC": "STYLE_CINEMATIC_EP07.png",
    "CONCEPTUAL": "STYLE_CONCEPTUAL_EP07.png",
    "ARCHIVE": "STYLE_ARCHIVE_EP07.png",
}

# Woertlich aus dem Kopf der Promptdatei.
GLOBAL_RULES = (
    "Global rules for this episode: horizontal 16:9, 2K. Mystical and deep but with "
    "readable midtones - no large areas collapsing into black. No generated readable "
    "text, no invented script, no logos, no watermarks. No generic horror monster, no "
    "glowing eyes, no fantasy magic, no aurora colours indoors. Historical documents, "
    "artworks and research pages are never rebuilt by AI - real sources are cut in "
    "separately as static originals, so do not depict any specific historical document "
    "or painting. Show a bed or bedroom only where the narration genuinely needs the "
    "physical starting state; this batch works mostly away from the bed. Calm "
    "composition with a real foreground, middle ground and background; do not rely on "
    "a later aggressive camera move."
)

NEGATIVE = (
    "Hard constraints: no crushed blacks, no lettering of any kind in any language, "
    "no captions, no labels, no arrows, no diagram or HUD look, no watermark, no logo, "
    "no signature, no extra limbs, no distorted hands, and no image that asserts a "
    "supernatural being is objectively present."
)


def parse_table() -> list[dict]:
    text = DOC.read_text(encoding="utf-8")
    section = text.split("## Priorität C")[1].split("## Kartenstatus")[0]
    jobs = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or "Datei" in line[:12]:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or not cells[0].startswith("`"):
            continue
        filename = cells[0].strip("`")
        style = cells[1].strip()
        core = cells[2].strip()
        prompt = (
            f"Create one finished 16:9 documentary still at 2K for a German documentary "
            f"series on sleep paralysis and its cultural history.\n\n"
            f"Required content and function of this image (this is the editorial "
            f"instruction, follow it literally):\n{core}\n\n"
            f"{GLOBAL_RULES}\n\n{NEGATIVE}"
        )
        jobs.append({"key": filename.split("_")[0], "output_filename": filename,
                     "prompt": prompt, "kind": "MAIN",
                     "refs": [STYLE_FOR.get(style, STYLE_FOR["CONCEPTUAL"])],
                     "style": style})
    return jobs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    jobs = parse_table()
    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        jobs = [j for j in jobs if j["key"] in wanted or j["output_filename"] in wanted]
    if args.list:
        for job in jobs:
            print(f"  {job['key']:8s} {job['output_filename']:50s} {job['style']}")
        print(f"\n{len(jobs)} Motive")
        return 0

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT ist nicht gesetzt.")

    base.ASSETS = ASSETS
    base.OUTPUT = OUTPUT
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for job in jobs:
        for ref in job["refs"]:
            if not (ASSETS / ref).is_file():
                raise SystemExit(f"Stilreferenz fehlt: {ASSETS / ref}")

    print(f"Model={base.MODEL} project={project} jobs={len(jobs)}", flush=True)
    done = failed = 0
    for index, job in enumerate(jobs, 1):
        if (OUTPUT / job["output_filename"]).exists() and not args.overwrite:
            print(f"  [{index:2d}/{len(jobs)}] SKIP      {job['output_filename']}", flush=True)
            done += 1
            continue
        for attempt, wait in enumerate((0, 60, 150, 300, 480), 1):
            if wait:
                time.sleep(wait)
            try:
                result = base.generate(job, project, "global", args.overwrite, attempts=1)
                print(f"  [{index:2d}/{len(jobs)}] {result['status']:9s} "
                      f"{job['output_filename']:50s} "
                      f"{result.get('width')}x{result.get('height')}", flush=True)
                done += 1
                break
            except Exception as exc:
                if attempt == 5:
                    print(f"  [{index:2d}/{len(jobs)}] FEHLER    {job['output_filename']}: "
                          f"{str(exc)[:110]}", flush=True)
                    failed += 1
    print(f"\nfertig={done} fehlgeschlagen={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
