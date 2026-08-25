#!/usr/bin/env python3
"""EP06 - die fehlenden Stills erzeugen: IMG033-IMG045 und die SHOT-Companions.

Zwei Quellen fuer die Prompts:

* `VOICE_EP06/MISSING_ASSETS_AND_PROMPTS.md`, Abschnitt B - dreizehn
  ausformulierte Prompts fuer IMG033 bis IMG045.
* `VOICE_EP06/SEMANTIC_DERIVATIVE_BATCH.md` - die Companions mit Methode
  `NEW_IMAGEGEN_COMPANION`. Dort steht nur ein generischer Ausfuehrungshinweis;
  der eigentliche Auftrag ist der **neue semantische Anker**. Er wird hier nach
  vorn gezogen, sonst entstuende bloss eine Variante des Basisbilds.

Modell und Bildkonfiguration kommen aus `tools/generate_ep08_vertex.py`, die
globalen Bildregeln aus dem Kopf der EP06-Promptdatei.

    python tools/generate_ep06_supplement.py --list
    python tools/generate_ep06_supplement.py --only IMG033,SHOT09
    python tools/generate_ep06_supplement.py
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
EPISODE = ROOT / "06_PRODUCTION" / "EP06_SCHLAFPARALYSE_V4"
KIT = EPISODE / "IMAGE_GENERATION_KIT"
ASSETS = KIT / "02_ASSETS"
OUTPUT = KIT / "03_GENERATED_OUTPUT" / "NanoBanana_2K_Series"
PROMPTS = EPISODE / "VOICE_EP06" / "MISSING_ASSETS_AND_PROMPTS.md"
BATCH = EPISODE / "VOICE_EP06" / "SEMANTIC_DERIVATIVE_BATCH.md"

# Aus dem Kopf von MISSING_ASSETS_AND_PROMPTS.md. Gilt fuer jeden Prompt.
GLOBAL_RULES = (
    "Global constraints for this series: 16:9 at 2560x1440, sRGB, clear midtone "
    "separation and nothing crushed into black. Calm NOESIS palette of night blue, "
    "warm lamp light, paper and desaturated coastal tones; no cyberpunk neon. "
    "No lettering, logos, watermarks or invented measurement curves of any kind. "
    "No generic ghost figure, no monster, no demonic face. Scientific images are "
    "illustrative metaphors, never presented as actual recordings of a named study. "
    "Show a bed or bedroom only when the stated anchor genuinely requires it."
)

STYLE_FOR = {
    "CINEMATIC": "STYLE_CINEMATIC_EP06.png",
    "CONCEPTUAL": "STYLE_CONCEPTUAL_EP06.png",
    "SCIENCE": "STYLE_SCIENCE_EP06.png",
}

# Welche Stilreferenz je Motiv. Rekonstruktion -> cinematic, subjektive
# Wahrnehmung -> conceptual, Koerper und Labor -> science.
STYLE_MAP = {
    "IMG033": "CINEMATIC", "IMG034": "CINEMATIC", "IMG035": "CONCEPTUAL",
    "IMG036": "CINEMATIC", "IMG037": "CONCEPTUAL", "IMG038": "SCIENCE",
    "IMG039": "SCIENCE", "IMG040": "SCIENCE", "IMG041": "SCIENCE",
    "IMG042": "CONCEPTUAL", "IMG043": "CONCEPTUAL", "IMG044": "CINEMATIC",
    "IMG045": "CINEMATIC",
    "SHOT09": "CINEMATIC", "SHOT10": "CINEMATIC", "SHOT12": "CONCEPTUAL",
    "SHOT14": "CONCEPTUAL", "SHOT19": "CONCEPTUAL", "SHOT22": "CONCEPTUAL",
    "SHOT23": "CONCEPTUAL", "SHOT25": "CONCEPTUAL", "SHOT26": "SCIENCE",
    "SHOT27": "CONCEPTUAL", "SHOT28": "CONCEPTUAL", "SHOT30": "CONCEPTUAL",
    "SHOT31": "CINEMATIC", "SHOT32": "CONCEPTUAL", "SHOT33": "CINEMATIC",
    "SHOT37": "SCIENCE",
}


def parse_img_prompts() -> list[dict]:
    text = PROMPTS.read_text(encoding="utf-8")
    section = text.split("## B. Bildgenerierungs-Batch")[1].split("## C.")[0]
    jobs = []
    for block in re.split(r"\n### ", section)[1:]:
        name = block.split("`")[1]
        body = "\n".join(block.split("\n")[1:]).strip()
        # Erster nichtleerer Absatz ist der Prompt.
        prompt = next((p.strip() for p in body.split("\n\n") if p.strip()), "")
        jobs.append({"key": name.split("_")[0], "output_filename": name,
                     "prompt": prompt, "kind": "MAIN"})
    return jobs


def parse_companion_prompts() -> list[dict]:
    text = BATCH.read_text(encoding="utf-8")
    jobs = []
    for block in re.split(r"\n### ", text)[1:]:
        name = block.split("`")[1]
        if "NEW_IMAGEGEN_COMPANION" not in block:
            continue
        anchor = re.search(r"New semantic anchor: (.+)", block)
        take = re.search(r"Take/act: `([^`]+)` / `([^`]+)`", block)
        base_ref = re.search(r"Base reference: `([^`]+)`", block)
        anchor_text = anchor.group(1).strip() if anchor else ""
        act = take.group(2) if take else ""
        base_name = Path(base_ref.group(1)).name if base_ref else ""
        prompt = (
            f"Create a distinct 16:9 editorial documentary still, 2560x1440, for act {act} of "
            f"a German documentary on sleep paralysis. The idea the image has to carry, "
            f"expressed only through objects, space and light: {anchor_text}.\n\n"
            f"This image is a companion to an existing shot ({base_name}); it must share the "
            f"series palette and material world but must NOT repeat its composition. Change "
            f"the framing, the scale, the arrangement of objects, the background and the "
            f"lighting direction. A closer or wider view of the same picture is a failure - "
            f"the viewer has to receive new information, not the same information again.\n\n"
            # Erster Durchlauf: das Modell hat den deutschen Anker woertlich auf
            # Zettel, Karteikarten und Bildschirme geschrieben - bei zwei Motiven
            # sogar als erfundene Messkurve mit Studientitel. Beides verletzt die
            # globalen Bildregeln und den Claims-Lock der Folge.
            f"ABSOLUTELY CRITICAL - the idea above is a DESCRIPTION FOR YOU, never something "
            f"to write into the picture. The image must contain zero readable text in any "
            f"language: nothing written on paper, notes, cards, labels, book pages, screens, "
            f"blackboards or walls. Any paper or handwriting that appears must be far enough "
            f"away, blurred or oblique that no word can be read. Do not invent measurement "
            f"traces, EEG or EMG curves, charts, study titles, dates or readouts - a fabricated "
            f"scientific graphic would be a false document. Convey the idea through what is "
            f"physically in the room, not through captions."
        )
        jobs.append({"key": name.split("_")[0], "output_filename": name,
                     "prompt": prompt, "kind": "MAIN"})
    return jobs


def build_jobs() -> list[dict]:
    jobs = parse_img_prompts() + parse_companion_prompts()
    seen: set[str] = set()
    unique = []
    for job in jobs:
        if job["output_filename"] in seen:
            continue
        seen.add(job["output_filename"])
        style = STYLE_FOR[STYLE_MAP.get(job["key"], "CONCEPTUAL")]
        job["refs"] = [style]
        job["prompt"] = f"{job['prompt']}\n\n{GLOBAL_RULES}"
        unique.append(job)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Kommaliste von Praefixen, z. B. IMG033,SHOT09")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    jobs = build_jobs()
    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        jobs = [j for j in jobs if j["key"] in wanted or j["output_filename"] in wanted]
    if args.list:
        for job in jobs:
            print(f"  {job['key']:8s} {job['output_filename']:52s} "
                  f"{STYLE_MAP.get(job['key'], 'CONCEPTUAL')}")
        print(f"\n{len(jobs)} Motive")
        return 0

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT ist nicht gesetzt.")

    # Auf die EP06-Ablage umbiegen; das Basismodul zeigt auf EP08.
    base.ASSETS = ASSETS
    base.OUTPUT = OUTPUT
    OUTPUT.mkdir(parents=True, exist_ok=True)

    print(f"Model={base.MODEL} project={project} jobs={len(jobs)}")
    done = failed = 0
    for index, job in enumerate(jobs, 1):
        target = OUTPUT / job["output_filename"]
        if target.exists() and not args.overwrite:
            print(f"  [{index:2d}/{len(jobs)}] SKIP      {job['output_filename']}")
            done += 1
            continue
        # Vertex drosselt bei laengeren Serien; lieber langsam durchlaufen als
        # nach der Haelfte mit 429 abbrechen.
        for attempt, wait in enumerate((0, 60, 150, 300, 480), 1):
            if wait:
                time.sleep(wait)
            try:
                result = base.generate(job, project, "global", args.overwrite, attempts=1)
                print(f"  [{index:2d}/{len(jobs)}] {result['status']:9s} "
                      f"{job['output_filename']:52s} {result.get('width')}x{result.get('height')}")
                done += 1
                break
            except Exception as exc:
                if attempt == 5:
                    print(f"  [{index:2d}/{len(jobs)}] FEHLER    {job['output_filename']}: "
                          f"{str(exc)[:110]}")
                    failed += 1
    print(f"\nfertig={done} fehlgeschlagen={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
