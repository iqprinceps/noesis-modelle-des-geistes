#!/usr/bin/env python3
"""EP06 - die sechs zusaetzlichen Transformationsclips CLIP005 bis CLIP010.

Vorgabe aus `VOICE_EP06/MISSING_ASSETS_AND_PROMPTS.md`, Abschnitt D:
1920x1080, 24 fps, sechs Sekunden, ohne Ton, Kamera fest. Die Bewegung muss
Gegenstand, Zustand oder Bedeutung veraendern - ein blosser Push, Parallax oder
Ken Burns ist ausdruecklich unzulaessig.

Modell, Endpunkt und Negativprompt kommen unveraendert aus
`tools/generate_ep06_veo.py`, damit die sechs Nachzuegler zu den vier bereits
freigegebenen Clips passen.

Startframes sind vorhandene, freigegebene Stills derselben Folge. Wo der Plan
"ein neues Companion" verlangt, aber keines existiert, wird der thematisch
richtige Still genutzt und der Prompt so gefuehrt, dass der Clip sich vom
bereits bestehenden Clip aus demselben Still unterscheidet.

    python tools/generate_ep06_veo_supplement.py --list
    python tools/generate_ep06_veo_supplement.py
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_ep06_veo as base  # noqa: E402

CLIPS = [
    {
        "filename": "CLIP005_MOTOR_FREEZE.mp4",
        # Derselbe Ausgangsstill wie CLIP002. Dort loest sich die Hemmung am
        # Ende und ein Finger bewegt sich; hier bleibt sie bestehen. Zwei
        # verschiedene Aussagen, zwei verschiedene Akte.
        "start": "IMG003_HAND_WILL_NOT_MOVE.png",
        "person": "allow_adult",
        "prompt": (
            "Six-second transformative science-documentary clip beginning exactly from the "
            "supplied hand-and-forearm frame. Lock the camera completely; nothing pans, "
            "pushes or drifts. A warm motor impulse becomes visible in the upper forearm and "
            "travels toward the fingers. Partway down it meets a translucent inhibition "
            "boundary, presses against it, spreads sideways along the boundary and disperses "
            "into fading filaments. The real hand and all five fingers stay completely and "
            "visibly still for the entire six seconds - the impulse never crosses and no "
            "finger moves at any point. The room stays ordinary and unchanged. This is an "
            "illustrative metaphor for REM atonia, not a recording of neural activity. No "
            "pain, no distress, no glowing skin, no supernatural force, no extra fingers, no "
            "deformation, no text, label, logo, camera motion, flicker or audio. Keep bright "
            "readable blue and amber midtones."
        ),
        "position": "S3, Motorik bleibt blockiert",
    },
    {
        "filename": "CLIP006_THREE_FAMILIES.mp4",
        "start": "SHOT37_ERLEBNISFAMILIEN.png",
        "person": "dont_allow",
        "prompt": (
            "Six-second transformative documentary clip beginning exactly from the supplied "
            "frame. Camera absolutely locked. Three ordinary object environments replace one "
            "another in sequence, each fully superseding the previous state. First, doorway "
            "and coat-stand cues quietly organise into the implied outline of a presence "
            "without any figure appearing. Second, folded fabric and bedding compress "
            "downward as if under weight, expressing chest pressure. Third, chair, lamp and "
            "floor lose their stable orientation and tilt coherently, expressing vestibular "
            "displacement. Each state is made only of real objects and their shadows. No "
            "monster, no literal attack, no person, no labels, no montage of beds, no camera "
            "drift, no text, logo or audio. Preserve bright readable midtones throughout."
        ),
        "position": "S4, drei Erlebnisfamilien",
    },
    {
        "filename": "CLIP007_INTERRUPTION_CYCLE.mp4",
        "start": "IMG040_INTERRUPTION_PROTOCOL_OBJECTS.png",
        "person": "dont_allow",
        "prompt": (
            "Six-second transformative documentary clip beginning exactly from the supplied "
            "early-1990s laboratory table. Camera completely locked. The analog clock hands "
            "advance smoothly. A small blank protocol marker slides from its sleep position "
            "across the table to a one-hour wake interval position, pauses, and then returns "
            "to rest beside the prepared sensors. The objects themselves perform the whole "
            "sequence; nothing else in the room changes. No readable text, no numerals "
            "appearing, no patient, no person, no fabricated chart or measurement trace, no "
            "futuristic interface, no camera motion, no logo and no audio. Warm lamp light "
            "and cool room shadows stay bright and readable."
        ),
        "position": "S5, Unterbrechungsprotokoll",
    },
    {
        "filename": "CLIP008_SIX_EPISODES_SIGNAL.mp4",
        "start": "IMG041_SIX_EPISODES_MARKERS.png",
        "person": "dont_allow",
        "prompt": (
            "Six-second transformative documentary clip beginning exactly from the supplied "
            "fixed evidence table. Camera locked. Six distinct warm markers illuminate one "
            "after another, each in response to one short measurement pulse travelling along "
            "the connected cable. After the sixth marker the sequence stops and the remaining "
            "unused positions on the table stay dark and empty. The final count must be "
            "exactly six illuminated markers. No numerals, no text, no labels, no celebratory "
            "effect, no particles or sparkles, no camera movement, no logo and no audio. Calm "
            "documentary lighting with visible shadow detail."
        ),
        "position": "S5, sechs dokumentierte Episoden",
    },
    {
        "filename": "CLIP009_REALNESS_CAUSE_SPLIT.mp4",
        "start": "IMG043_PRESENCE_BEFORE_IMAGE.png",
        "person": "dont_allow",
        # Erster Versuch: die Formulierung "measurable timing structure" liess
        # Veo eine EKG-artige Kurve mit beschrifteten Achsen rendern - eine
        # erfundene Messaufzeichnung mit lesbaren Zahlen. Die Ordnung wird
        # deshalb rein als physisches Material beschrieben.
        "prompt": (
            "Six-second transformative conceptual clip beginning exactly from the supplied "
            "frame. Camera locked. One vivid subjective form of pressure and presence "
            "separates cleanly into two synchronised halves that then hold side by side. The "
            "left half becomes calm physical order: evenly spaced translucent fabric panels "
            "and regular folds, like something that can be counted and measured by hand. The "
            "right half stays an unresolved open threshold of soft empty air. Neither half "
            "fades, dominates or cancels the other - both remain fully visible at the end.\n\n"
            "ABSOLUTELY CRITICAL: this clip must contain no chart, no graph, no waveform, no "
            "ECG or EEG trace, no oscilloscope line, no grid, no axis, no ruler, no scale "
            "markings, no numerals and no readable text of any kind. Order is shown only "
            "through the spacing and rhythm of real physical objects, never through a "
            "diagram or a screen. A fabricated measurement readout would be a false document.\n\n"
            "No claim about a soul, no external entity, no figure, no balance or scales "
            "imagery, no arrows, no neon, no camera motion and no audio. Luminous, readable "
            "midtones."
        ),
        "position": "S6, Wirklichkeit und Ursache",
    },
    {
        "filename": "CLIP010_SHADOW_COMPLETION.mp4",
        "start": "SHOT28_SCHATTEN_WIRD_SCHULTER.png",
        "person": "dont_allow",
        "prompt": (
            "Six-second transformative perception clip beginning exactly from the supplied "
            "bright interior with chair, curtain and door edge. Camera absolutely locked. The "
            "real shadows cast by these ordinary objects drift slowly into alignment until "
            "they briefly suggest the outline of a shoulder and upper arm. The suggestion "
            "holds for about one second, then the shadows separate again into clearly "
            "ordinary, unrelated object shadows. No person ever enters, no figure becomes "
            "solid, no dark apparition, no monster, no face. Daylight stays bright and the "
            "midtones readable at all times - nothing sinks into black. No text, logo, camera "
            "movement or audio."
        ),
        "position": "S7, Schattenvervollstaendigung",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--only", help="Kommaliste, z. B. CLIP007,CLIP008")
    args = parser.parse_args()

    clips = CLIPS
    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        clips = [c for c in clips if c["filename"].split("_")[0] in wanted
                 or c["filename"] in wanted]

    if args.list:
        for c in clips:
            start = base.OUTPUT / c["start"]
            mark = "OK " if start.is_file() else "FEHLT"
            print(f"  {mark} {c['filename']:34s} <- {c['start']:44s} {c['position']}")
        print(f"\n{len(clips)} Clips")
        return 0

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise SystemExit("GOOGLE_CLOUD_PROJECT ist nicht gesetzt.")

    missing = [c for c in clips if not (base.OUTPUT / c["start"]).is_file()]
    if missing:
        raise SystemExit("Startframe fehlt: " +
                         ", ".join(c["start"] for c in missing))

    print(f"Model={base.MODEL} project={project} clips={len(clips)}", flush=True)
    done = failed = 0
    for index, clip in enumerate(clips, 1):
        target = base.OUTPUT / clip["filename"]
        if target.is_file():
            print(f"  [{index}/{len(clips)}] SKIP      {clip['filename']}", flush=True)
            done += 1
            continue
        # Veo meldet regelmaessig Ueberlast (code 8) oder liefert eine fertige
        # Operation ohne Video zurueck. Beides ist transient; ohne Wiederholung
        # bleiben sonst zufaellig einzelne Clips liegen.
        for attempt, wait in enumerate((0, 90, 240, 480, 900), 1):
            if wait:
                print(f"  [{index}/{len(clips)}] warte {wait}s und wiederhole ...",
                      flush=True)
                time.sleep(wait)
            try:
                print(f"  [{index}/{len(clips)}] sende     {clip['filename']} "
                      f"(Versuch {attempt}) ...", flush=True)
                operation = base.submit(clip, project)
                result = base.poll(operation, project)
                path = base.save(clip, result)
                print(f"  [{index}/{len(clips)}] FERTIG    {path.name} "
                      f"({path.stat().st_size:,} bytes)", flush=True)
                done += 1
                break
            except Exception as exc:
                if attempt == 5:
                    print(f"  [{index}/{len(clips)}] FEHLER    {clip['filename']}: "
                          f"{str(exc)[:200]}", flush=True)
                    failed += 1
    print(f"\nfertig={done} fehlgeschlagen={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
