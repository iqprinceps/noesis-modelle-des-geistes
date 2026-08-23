#!/usr/bin/env python3
"""EP01A Die Spiegel — Bildmotive fuer die beiden Shorts, Hochformat 9:16.

Nutzt den Bildgenerator der Folge (`spg_image_gen`) mit allem, was dort
inzwischen drinsteht: Style Key, Farbe je Akt, Geometrie der Anlage, und vor
allem die Regel gegen Polarlichtfarbe im Innenraum — das war die Stelle, an
der die erste Fassung der Folge sofort als erzeugt zu erkennen war.

Hochformat ist nicht Beschnitt. Ein 16:9-Bild auf 9:16 beschnitten behaelt
31 Prozent der Breite; bei einer Anlage von fast drei Metern Breite bleibt
davon nichts uebrig. Die Motive entstehen deshalb neu, mit einer Bildaufteilung
fuer das stehende Format: die Anlage in die Hoehe, der Mensch klein darin, viel
Raum ueber dem Kopf.

    python tools/spg_shorts_bilder.py fehlend
    python tools/spg_shorts_bilder.py alle [--jobs 3]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL" / "shorts" / "visuals"

_spec = importlib.util.spec_from_file_location("spg_image_gen",
                                               ROOT / "tools" / "spg_image_gen.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def J(id_, prompt, akt="", spiegel=False):
    return {"id": id_, "prompt": prompt, "akt": akt, "spiegel": spiegel,
            "aspect": "9:16"}


JOBS = [
    # =================================================== Short A: Der Stuhl
    J("sh_a01_stuhl", akt="S1", spiegel=True, prompt=(
      "Vertical composition. A plain empty steel chair stands alone on a wooden platform at "
      "the centre of the construction, photographed from chest height straight on. Nobody is "
      "in the picture and nobody is sitting on the chair. The polished plates rise on both "
      "sides and leave the frame at the top. One warm work lamp low at the left rakes across "
      "the metal. The lower third is bare concrete floor. Important: there is no coloured "
      "light source anywhere in this room, so the polished metal carries only the warm "
      "yellow of the work lamp and its own grey. No green, no magenta, no violet and no "
      "aurora on the plates, on the floor or on any surface. Cold, still, empty, "
      "documentary, colour film grain.")),
    J("sh_a02_setzen", akt="S1", spiegel=True, prompt=(
      "Vertical composition, seen from behind and slightly above: a man in a heavy dark "
      "coat lowering himself onto the steel chair inside the construction, hands on the "
      "seat edge, face not visible. The polished plates curve up past him and leave the "
      "frame at the top, making him small. One warm lamp outside the gap throws his long "
      "shadow across the platform. Documentary, grainy colour film.")),
    J("sh_a03_spalt", akt="S1", spiegel=True, prompt=(
      "Vertical close view of the narrow vertical gap between two upright curved aluminium "
      "sheets, seen from outside. The gap is about 40 centimetres wide and runs the full "
      "height of the frame from the bottom edge to the top edge. The sheets are separate "
      "standing plates, not a capsule and not a closed pod — no door, no hatch, no seal, no "
      "lid. Their polished inner faces catch one thin warm line of lamp light. Through the "
      "gap there is only blackness. Important: there is no coloured light source anywhere in "
      "this room, so the polished metal carries only the warm yellow of the work lamp and "
      "its own grey. No green, no magenta, no violet and no aurora on the plates, on the "
      "floor or on any surface. Tall, narrow, claustrophobic, heavy film grain.")),
    J("sh_a04_licht_aus", akt="S1", prompt=(
      "Vertical frame, almost entirely black. In the upper third the filament of a single "
      "bare bulb is fading down to a dull orange thread, its light no longer reaching "
      "anything. A hint of curved metal catches the last of it at the left edge. Nothing "
      "else is visible. Extreme darkness, heavy grain.")),
    J("sh_a05_schimmern", akt="S1", prompt=(
      "Vertical frame of pure blackness with the faintest possible bloom of colour "
      "entering from the outer edges — a thin violet at the top corners, a trace of green "
      "at the bottom. No object, no room, no figure, no geometry. Ninety-five percent of "
      "the frame is black. Very soft, heavy colour film grain.")),
    J("sh_a06_farbe", akt="S1", prompt=(
      "One single continuous photograph filling the whole vertical frame — not a grid, not a "
      "collage, no panels, no borders, no split screen. There is no room, no wall, no "
      "window, no lamp, no equipment, no furniture, no person and no horizon anywhere in "
      "this picture. The photograph shows nothing but colour against pure black: a broad "
      "magenta band across the middle of the frame, cyan beneath it, a thin seam of gold "
      "between them, all soft-edged and drifting. Extremely soft focus, heavy colour film "
      "grain. It should look like colour seen behind closed eyes.")),
    J("sh_a07_ringe", akt="S1", prompt=(
      "One single continuous photograph filling the whole vertical frame — not a grid, not a "
      "collage, no panels, no borders, no split screen. There is no room, no wall, no "
      "window, no lamp, no equipment, no furniture, no person and no horizon anywhere in "
      "this picture. The photograph shows nothing but faint concentric rings of light "
      "sliding into one another against pure black — violet at the outside, dull gold near "
      "the centre, every edge dissolving. The rings are not an object and not a lamp; they "
      "have no rim, no housing and no surface. Very soft focus, heavy grain, low contrast.")),
    J("sh_a08_zimmer", akt="S1", prompt=(
      "One single continuous photograph filling the whole vertical frame — not a grid, not a "
      "collage, no panels, no borders, no split screen. There is no lamp, no equipment, no "
      "furniture, no person and no horizon anywhere in this picture. Out of pure blackness "
      "the corner of an unfamiliar room is barely suggested: part of a ceiling, the edge of "
      "a doorframe and a tall window, sketched only in deep red and dull gold light. "
      "Everything else is black. The perspective is slightly wrong, as if remembered. No "
      "furniture, no people, no aurora, no magenta and no cyan anywhere. Very soft focus, "
      "heavy grain.")),
    J("sh_a09_gesicht", akt="S1", prompt=(
      "One single continuous photograph filling the whole vertical frame — not a grid, not a "
      "collage, no panels, no borders. Out of near-total blackness a man's face is lit from "
      "one side by a single warm tungsten lamp standing out of frame, so that one cheekbone, "
      "one brow and the line of the nose are modelled and everything else falls away into "
      "black. His eyes are closed. Ninety percent of the frame is black. There is no "
      "coloured light of any kind on his skin, no green, no magenta, no violet, no glow "
      "coming out of him, and no lights of any colour in the background. Long lens, shallow "
      "depth of field, heavy colour film grain.")),
    J("sh_a10_uhr", akt="S5", prompt=(
      "Vertical macro of the face of an old enamel alarm clock filling the upper half of "
      "the frame, cream dial, brass bezel, the hands blurred by motion. One warm lamp from "
      "the left is the only light; the lower half of the frame falls away into brown "
      "darkness. Numerals present but unreadable. No coloured light anywhere.")),
    J("sh_a11_tuer", akt="S1", spiegel=True, prompt=(
      "Vertical composition seen from inside a dark space looking out through a tall narrow "
      "opening as it widens: a wedge of warm yellow corridor light cutting into blackness, "
      "the silhouette of a standing person inside that wedge, no face readable. Two curved "
      "polished metal edges frame the opening left and right. Everything except the wedge of "
      "warm light is black — no indicator lamps, no coloured light, no equipment. Backlit, "
      "very high contrast, heavy grain.")),
    J("sh_a12_anlage", akt="S8", spiegel=True, prompt=(
      "Vertical wide view of the construction standing in a plain room with a painted "
      "concrete floor, photographed in flat daylight from a doorway, the plates rising "
      "through most of the frame height. Entirely ordinary and slightly shabby, a radiator "
      "and a folding chair against the wall. Nothing mysterious about it. Documentary, low "
      "contrast, dusty warm light.")),

    # ================================================= Short B: Der Versuch
    J("sh_b01_dikson", akt="S6", prompt=(
      "Vertical arctic night. In the lower third a handful of low weathered timber "
      "buildings on flat snow at the edge of a frozen sea, two windows lit warm yellow. "
      "Above them the upper two thirds of the frame is filled by an enormous green and "
      "violet aurora over a black sky. Utterly empty and cold. Long exposure, colour film "
      "grain, no people, no signage.")),
    J("sh_b02_karte", akt="S6", prompt=(
      "One single continuous photograph filling the whole vertical frame — not a grid, not a "
      "collage, no panels, no borders, no inset pictures. Overhead view of one worn paper "
      "map of northern Siberia lying flat on a wooden table under a single warm lamp, the "
      "coastline crossing the upper third, a pencil line drawn from a point far south to a "
      "point on the coast. Printed names are present as texture but not legible. Creases, a "
      "coffee ring, a brass paperweight. Warm archive light, no coloured light.")),
    J("sh_b03_verladung", akt="S6", prompt=(
      "Vertical frame: men in heavy fur-lined coats manhandling a long wooden crate down "
      "from a tracked vehicle onto deep snow at polar night, lit by the vehicle's yellow "
      "work lamps. Breath visible in the cold. Above them a green aurora fills the upper "
      "half of the sky. Faces not readable. Documentary, cold blue surround against warm "
      "lamp pools.")),
    J("sh_b04_aufbau", akt="S6", spiegel=True, prompt=(
      "Vertical composition: the construction standing outdoors on packed snow at polar "
      "night, the polished plates rising through most of the frame and catching the green "
      "of an aurora overhead, one warm portable lamp at their foot throwing a small pool "
      "of yellow on the snow. A single figure in a heavy coat stands beside it, very "
      "small. Enormous, cold, absurd. Long exposure, film grain.")),
    J("sh_b05_symbolkarte", akt="S7", prompt=(
      "Vertical overhead macro of a single small card lying on a dark wooden table under "
      "one warm bulb, bearing one simple triangle drawn in soft pencil. Slightly uneven "
      "strokes, one corner not quite closed. Nothing else on the card, nothing else in "
      "frame. Shallow depth of field, warm domestic light, no coloured light.")),
    J("sh_b06_sender", akt="S7", spiegel=True, prompt=(
      "Vertical composition: a woman in her thirties sitting upright on a plain metal "
      "chair at the centre of the construction, seen from the front at a distance, a small "
      "card resting on her knee, eyes closed, hands still. The polished plates rise on "
      "both sides out of the top of the frame. One clamped work lamp is the only light. No "
      "aurora and no coloured light inside the room. Unposed, documentary, film grain.")),
    J("sh_b07_kuechentisch", akt="S7", prompt=(
      "Vertical frame of a scrubbed wooden kitchen table at night shot from a low angle: a "
      "sheet of ruled paper, a blunt pencil, a glass of tea in a metal holder, a small "
      "alarm clock. One bare yellow bulb hangs in the upper part of the frame and is the "
      "only light; the corners fall away into brown darkness. Frost on the window behind. "
      "Quiet, domestic, documentary.")),
    J("sh_b08_empfaenger", akt="S7", prompt=(
      "Vertical frame: a man in his forties sitting alone at a table in a small Soviet "
      "apartment at night, shot from across the room, a pencil held over a blank sheet, "
      "eyes closed, head slightly bowed. Warm yellow bulb overhead, patterned wallpaper, a "
      "radio on a sideboard. Through the window behind him a faint green aurora is visible "
      "in the sky and on the glass only — it does not reach into the room. Unposed, "
      "documentary, colour film grain.")),
    J("sh_b09_kurzwelle", akt="S7", prompt=(
      "Vertical macro of the tuning dial of a 1980s shortwave receiver filling the upper "
      "half of the frame: illuminated glass scale, amber backlight, a brass pointer, "
      "bakelite knobs worn smooth. The scale markings are present but unreadable. Below it "
      "the wooden table falls into darkness. Warm and tactile, film grain.")),
    J("sh_b10_zeitung", akt="S7", prompt=(
      "Vertical overhead macro of an open newspaper page on a table under one warm lamp, "
      "the paper yellowed and slightly creased, a small boxed announcement ringed in blue "
      "ballpoint in the upper third. The print is present as texture but no word is "
      "legible. Warm pool of light, dark edges, film grain.")),
    J("sh_b11_blaetter", akt="S7", prompt=(
      "One single continuous photograph filling the whole vertical frame — not a grid, not a "
      "collage, no panels, no borders, no inset pictures, no window anywhere in the picture. "
      "Seen from above at a steep angle: dozens of small sheets of paper with simple pencil "
      "shapes on them, spread overlapping across a large wooden table under one hanging "
      "lamp, the stack of sheets receding up the frame. Some sheets creased, some torn from "
      "notebooks. The shapes read as marks; no writing is legible. One warm pool of light in "
      "the centre, dark at every edge, no coloured light. Film grain.")),
    J("sh_b12_polarlicht", akt="S6", prompt=(
      "Vertical frame almost entirely filled by a towering green and violet aurora curtain "
      "over black sky, its lower edge just touching a thin band of pack ice at the very "
      "bottom of the frame. No buildings, no people, no light source but the sky itself. "
      "Enormous and empty. Long exposure on colour film.")),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("befehl", choices=("alle", "fehlend"))
    ap.add_argument("--modell", default="pro", choices=("pro", "flash"))
    ap.add_argument("--aufloesung", default="4k", choices=("1k", "2k", "4k"))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--nur", default="")
    ap.add_argument("--neu", action="store_true", help="vorhandene ueberschreiben")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    gen.OUT = OUT                       # Motive der Shorts liegen getrennt

    if args.befehl == "fehlend":
        for j in JOBS:
            if not (OUT / f"{j['id']}.png").exists():
                print(j["id"])
        return

    nur = {x for x in args.nur.split(",") if x}
    offen = [j for j in JOBS
             if (not nur or j["id"] in nur)
             and (args.neu or not (OUT / f"{j['id']}.png").exists())]
    if not offen:
        print(f"{len(JOBS)}/{len(JOBS)} vorhanden -> {OUT}")
        return

    print(f"{len(offen)} Motive, Modell {args.modell}, {args.jobs} parallel\n")
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for name, status in pool.map(
                lambda j: gen.bauen(j, args.modell, args.aufloesung), offen):
            print(f"  {name:28s} {status}", flush=True)

    da = sum(1 for j in JOBS if (OUT / f"{j['id']}.png").exists())
    print(f"\n{da}/{len(JOBS)} vorhanden -> {OUT}")


if __name__ == "__main__":
    main()
