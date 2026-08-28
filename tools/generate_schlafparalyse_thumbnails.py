#!/usr/bin/env python3
"""Thumbnail-Vorlagen fuer EP06-EP08 erzeugen.

Der Prompt steht je Episode in
`PRODUCTION_SUMMARY/<Episode>/THUMBNAIL_ENDCARD_V4.md`, Abschnitt
"Generation prompt", und wird von dort woertlich uebernommen.

Ergaenzt wird nur ein Textverbot: die Vorlage bekommt die Titelzeile spaeter im
Schnitt, und ein Modell, das selbst Schrift ins Bild setzt, macht die Flaeche
dafuer unbrauchbar. Bei den EP06-Stills hatte genau das mehrfach zugeschlagen.

    python tools/generate_schlafparalyse_thumbnails.py --list
    python tools/generate_schlafparalyse_thumbnails.py EP06 EP08
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

EPISODES = {
    "EP06": dict(dir="EP06_SCHLAFPARALYSE_V4",
                 style="IMAGE_GENERATION_KIT/02_ASSETS/STYLE_CINEMATIC_EP06.png"),
    "EP07": dict(dir="EP07_SCHLAFPARALYSE_V4",
                 style="IMAGE_GENERATION_KIT/02_ASSETS/STYLE_CINEMATIC_EP07.png"),
    "EP08": dict(dir="EP08_SCHLAFPARALYSE_V4",
                 style="IMAGE_GENERATION_KIT/02_ASSETS/STYLE_CINEMATIC_EP08.png"),
}

NO_TEXT = (
    "ABSOLUTELY CRITICAL: the image must contain no text, lettering, captions, "
    "titles, numbers, labels, signage or watermarks of any kind, in any language. "
    "The negative space is reserved for a title that is added later in the edit - "
    "leave it genuinely empty. Any lettering the model draws makes the frame "
    "unusable."
)


def spec_prompt(ep: str) -> str:
    doc = ROOT / "PRODUCTION_SUMMARY" / EPISODES[ep]["dir"] / "THUMBNAIL_ENDCARD_V4.md"
    text = doc.read_text(encoding="utf-8")
    block = text.split("### Generation prompt")[1].split("##")[0]
    prompt = next(line.strip() for line in block.splitlines() if line.strip())
    return f"{prompt}\n\n{NO_TEXT}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("episodes", nargs="*", default=[])
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    targets = args.episodes or list(EPISODES)
    if args.list:
        for ep in targets:
            print(f"\n=== {ep} ===\n{spec_prompt(ep)[:400]} ...")
        return 0

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT ist nicht gesetzt.")

    done = failed = 0
    for ep in targets:
        cfg = EPISODES[ep]
        episode = ROOT / "06_PRODUCTION" / cfg["dir"]
        out_dir = episode / "thumbnail"
        out_dir.mkdir(parents=True, exist_ok=True)
        base.ASSETS = episode
        base.OUTPUT = out_dir
        job = {
            "kind": "MAIN",
            "output_filename": f"{ep}_THUMB_BASE.png",
            "refs": [cfg["style"]],
            "prompt": spec_prompt(ep),
        }
        if not (episode / cfg["style"]).is_file():
            print(f"{ep}: Stilreferenz fehlt ({cfg['style']}) - ohne Referenz")
            job["refs"] = []
        if (out_dir / job["output_filename"]).exists() and not args.overwrite:
            print(f"{ep}: SKIP (vorhanden)")
            done += 1
            continue
        for attempt, wait in enumerate((0, 90, 240, 480), 1):
            if wait:
                time.sleep(wait)
            try:
                r = base.generate(job, project, "global", args.overwrite, attempts=1)
                print(f"{ep}: {r['status']} {r.get('width')}x{r.get('height')} "
                      f"-> {out_dir.relative_to(ROOT)}/{job['output_filename']}")
                done += 1
                break
            except Exception as exc:
                if attempt == 4:
                    print(f"{ep}: FEHLER {str(exc)[:150]}")
                    failed += 1
    print(f"\nfertig={done} fehlgeschlagen={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
