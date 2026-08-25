#!/usr/bin/env python3
"""EP08 - die beiden noch fehlenden Stills IMG033 und IMG036 erzeugen.

Der Sync-Plan fuehrt genau zwei Cues als `GENERATION_REQUIRED`. Die Prompts
stehen in `POST_PLAN/EP08_MISSING_ASSETS_AND_PROMPTS.md`, Abschnitt C, der
gemeinsame Negativ-Lock in Abschnitt D.

Modell, Bildgroesse, Referenzrollen und Guardrail kommen unveraendert aus
`tools/generate_ep08_vertex.py`, damit die beiden Nachzuegler stilistisch
zur bestehenden Serie passen.

    python tools/generate_ep08_supplement.py [--overwrite]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_ep08_vertex as base  # noqa: E402

NEGATIVE = (
    "Hard constraints: no crushed blacks, no generic horror ghost, no repeated person in bed, "
    "no neon cyberpunk room, no glowing skin, no fake document text, no title typography, no logos, "
    "no watermark, no extra limbs, and no literal claim that a supernatural entity is objectively present."
)

JOBS = [
    {
        "kind": "MAIN",
        "output_filename": "IMG033_CULTURAL_TEMPLATE_PRELOAD.png",
        "refs": [
            "STYLE_CONCEPTUAL_EP08.png",
            "IMG007_NAME_STABILIZES_SHAPE.png",
            "IMG027_GLOBAL_VISUAL_MEMORY.png",
        ],
        "prompt": (
            "Create a luminous 16:9 conceptual documentary still about a cultural image becoming "
            "available before a later perception. In a spacious museum-like signal chamber, unrelated "
            "archival fragments, soft charcoal marks and network traces pass through translucent memory "
            "planes; one simple hat-brim contour remains only as a faint latent possibility at the far "
            "edge, never a literal person. No bedroom, bed, ghost, horror creature, readable interface "
            "or text. Deep indigo balanced by warm amber pools and pearl highlights, lifted midtones, "
            "visible shadow detail, tactile glass and paper, sophisticated scientific-poetic realism. "
            "No captions, logos, signatures or watermark.\n\n" + NEGATIVE
        ),
    },
    {
        "kind": "MAIN",
        "output_filename": "IMG036_TRILOGY_THRESHOLD.png",
        "refs": [
            "STYLE_CINEMATIC_EP08.png",
            "IMG029_THREE_EPISODE_MOTIF_TABLE.png",
            "IMG030_BRAIN_EXPERIENCE_STORY_EXPECTATION_BASE.png",
        ],
        "prompt": (
            "Create a premium luminous 16:9 closing documentary still synthesizing body, experience, "
            "story and expectation as four connected physical spaces. A sleeping-body signal chamber "
            "opens into an ambiguous perception gallery, then into an archive of cultural masks, then "
            "into a bright network horizon that loops back toward a new human silhouette. No literal "
            "monster, bedroom, bed, occult diagram or readable text. The circular relation must be "
            "visually clear without arrows or labels. Warm amber practical light, cool indigo depth, "
            "pearl highlights, subtle grain, mystical but intellectually grounded and not gloomy. "
            "No logos, signatures or watermark.\n\n"
            # Der erste Versuch hat die vier Raeume mit eingebrannten englischen
            # Kapitaelchen beschriftet. Das verletzt den Negativ-Lock und waere
            # in einer deutschen Folge ohnehin unbrauchbar.
            "ABSOLUTELY CRITICAL: the image must contain zero text of any kind. No captions, no titles, "
            "no section labels, no room names, no legends, no annotations, no lettering on walls, floors, "
            "screens or objects, in any language. The four spaces must be distinguishable purely through "
            "architecture, lighting and content. If you are tempted to label a zone, leave it unlabelled.\n\n"
            + NEGATIVE
        ),
    },
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT ist nicht gesetzt.")
    location = "global"

    # Stilreferenzen liegen in 02_ASSETS, die bereits erzeugten IMG-Motive in
    # 03_GENERATED_OUTPUT. Fehlende Referenzen sofort melden statt still
    # weiterzulaufen - ohne sie waere der Stil nicht anschlussfaehig.
    for job in JOBS:
        for ref in job["refs"]:
            if (base.ASSETS / ref).is_file():
                continue
            found = next(base.OUTPUT.rglob(ref), None)
            if found is None:
                raise SystemExit(f"Referenz fehlt: {ref}")
            # request_parts() loest ueber base.ASSETS auf; relativen Pfad setzen.
            job["refs"][job["refs"].index(ref)] = os.path.relpath(found, base.ASSETS)

    print(f"Model={base.MODEL} project={project} location={location} jobs={len(JOBS)}")
    for job in JOBS:
        result = base.generate(job, project, location, args.overwrite)
        print(f"{result['status']:10} {base.final_filename(job)}  "
              f"{result.get('width')}x{result.get('height')}  {result.get('bytes', 0):,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
