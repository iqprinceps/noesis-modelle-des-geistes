#!/usr/bin/env python3
"""EP01A Die Spiegel — Bildgenerierung (Vertex AI / NanoBanana).

Abgeleitet von `tools/gateway_image_gen.py`. Die Vorlage bleibt unveraendert.

Der Style Key regelt nur noch Handwerk: Filmlook, Material, Licht aus echten
Quellen, kein Leuchten an Menschen, kein Text im Bild.

Die Farbe steht in `AKT_FARBE` und wechselt mit dem Akt. Ein erster Durchgang
hatte eine einzige Palette global im Style Key — dadurch lief die komplette
Folge im selben Tuerkiston und wirkte monoton. Der Farbbogen geht jetzt von
warmem Wolframlicht im Institut ueber kaltes Metall in der Werkstatt bis zur
gesaettigten Farbexplosion im Visionsakt und einem stillen Archivton am Ende.

    python tools/spg_image_gen.py generate <name> "<prompt>" --model flash \
        --aspect 16:9 --resolution 2k
    python tools/spg_image_gen.py all [--model flash] [--jobs 6] [--only NAME,NAME]
    python tools/spg_image_gen.py missing
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import json
import pathlib
import subprocess
import sys
import threading
import time
from typing import Any

import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL" / "visuals" / "generated"
REF_DIR = ROOT / "06_PRODUCTION" / "EP01A_SPIEGEL" / "visuals" / "references"

# --------------------------------------------------------------- Style Key
# Wortgleich abgeleitet aus 06_PRODUCTION/EP01_KOZYREV_V2/VISUAL_SPEC.md.
STYLE_KEY = """Visual style: Late-1980s Soviet scientific documentary photography, shot on
colour film with visible grain. Warm tungsten practical light played against cold arctic
daylight. Polished aluminium surfaces carrying coloured reflections. Deep shadows, but
every frame keeps at least one light source with real colour inside it. Materials:
bakelite, enamel paint, brass switches, paper rolls, plywood, frost. Photographic, not
rendered: no high gloss, no CGI sheen, no atmospheric fog machine.

All colour in the frame comes from light sources that are physically present in the
scene: lamps, windows, instrument panels, fire, sky. Colour is never a wash, a filter or
a tint laid over the whole picture, and it never glows out of a person, a hand or a face.
The image must read as colour photography, never as a monochrome or near-monochrome frame.

Aurora and saturated colour belong to the sky and to the open air. Inside a room they
appear only through a window or an open door, as a pale wash on the glass and on the
wall beside it. They never lie across a table, a sheet of paper, a hand or a face as
bands of magenta, cyan or green — an interior is lit by its own bulbs and by daylight,
and by nothing else. This is the single clearest sign of a generated picture.

The frame contains no writing of any kind. No colour names, no colour codes, no numbers,
no letters, no labels, no annotations anywhere in the image, not even faintly in a corner.

Mood: cold, remote, physically real. Siberia and the polar sea. The viewer should feel
they are looking at a place that exists, photographed by someone who was allowed in."""

NEGATIVE = """greyscale, monochrome, desaturated or washed-out colour, a uniform blue cast over
the whole frame, lens flare, bokeh overlays, particle or dust overlays, glowing auras around
people, modern flat-panel screens, modern clothing or eyewear, invented Cyrillic or Russian
lettering, readable text of any kind, watermarks, logos, captions, stock-photo styling,
HDR look, fantasy or sci-fi styling, plastic CGI surfaces"""

# Farbbogen ueber die Folge. Vorher stand eine einzige Palette global im
# Style Key — dadurch war jedes Bild im selben Tuerkiston und der Film wirkte
# monoton. Die Farbe gehoert zur Dramaturgie, nicht zur Marke.
AKT_FARBE = {
    # Nur Farbe, keine Szene. Eine Raumbeschreibung hier zwingt dem Modell
    # sonst ein Labor in jedes abstrakte Motiv — der Prompt entscheidet, ob
    # ueberhaupt ein Raum vorkommt.
    "S1": ("Near-black ground. Where colour appears it is luminous green, violet and "
           "magenta, soft-edged and weightless, plus one warm amber source if the scene "
           "calls for it. Nothing is tinted; the darkness stays neutral."),
    "S2": ("Soviet institute interior, winter. Warm tungsten and olive-green enamel "
           "inside, hard cold blue-white daylight through the windows. Amber desk lamps, "
           "cream paint, brown linoleum. No aurora, no green sky, no teal cast."),
    "S3": ("Workshop and drawing office. Brushed aluminium, cold steel grey, oiled "
           "machinery, copper and brass fittings catching a warm work lamp. Restrained "
           "and technical. No aurora, no green."),
    "S4": ("Polished aluminium interior. Cool silver and steel with a single warm "
           "reflection travelling across the curved surface. One faint hint of green "
           "deep in the reflection, nothing more."),
    "S5": ("The most colourful passage of the film. Saturated magenta, cyan, gold, "
           "deep violet and blood red against pure black. Rich and strange, like a "
           "colour organ. Where a person appears they are lit by ordinary light and "
           "never glow. No room, no walls and no equipment unless the prompt asks "
           "for them."),
    "S6": ("Arctic night at Dikson. Deep polar blue snow, green and faintly violet "
           "aurora across the sky, warm yellow window light and orange sodium lamps from "
           "the station buildings. Wide, cold, enormous."),
    "S7": ("Two worlds in one act. Sender side, outdoors in the arctic: cold blue snow "
           "under aurora. Receiver side, indoors: a warm domestic kitchen at night lit "
           "only by a yellow bulb — wooden table, white paper, no aurora and no coloured "
           "light anywhere in the room. The contrast between the two is the point."),
    "S8": ("Quiet ending. Dusty warm archive light, faded cream paper, aged brass, "
           "muted olive and brown. Softly lit, low contrast, almost nostalgic. "
           "No aurora, no strong green."),
}


def akt_farbe(akt: str) -> str:
    return AKT_FARBE.get(akt, "")


# Geometrie der Anlage. Wird an jeden Prompt gehaengt, der die Spiegel zeigt.
# Die vorhandenen EP01-Bilder zeigen die Konstruktion teilweise falsch; das
# Patent ist eindeutig (VISUAL_SPEC "Die Spiegel korrekt darstellen").
SPIEGEL = """Construction, exactly as specified and with no deviation: curved rectangular
sheets of polished aluminium alloy, each about 2.8 metres tall and 1.2 metres wide, standing
upright on the floor. Between four and ten such sheets are set side by side so their curves
form an OPEN vertical cylinder, or a spiral with one clearly visible vertical gap wide enough
for a person to walk through. The inner face is mirror-polished, the outer face is matte.
The structure is open to the ceiling — there is no lid, no dome, no cone, no funnel, no tube,
no capsule and no hood. A single person sits upright in the centre on a plain metal chair,
fully clothed, hands resting on the thighs, eyes open or closed, with nothing attached to the
body: no helmet, no cap, no electrodes, no cables, no wires, no sensors, no headphones.
Optionally a low motorised turntable with a visible gear ring under the whole structure."""


MODELLE = {
    "pro": ("gemini-3-pro-image", "global"),
    "flash": ("gemini-2.5-flash-image", "global"),
}


def die(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(2)


_token_cache: dict[str, Any] = {}
_token_lock = threading.Lock()


def token() -> str:
    now = time.time()
    with _token_lock:
        if _token_cache.get("exp", 0) > now + 60:
            return _token_cache["val"]
        try:
            out = subprocess.run(
                ["gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True, text=True, shell=True, timeout=60)
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
         retries: int = 12) -> dict[str, Any]:
    # Das Kontingent ist der Engpass, nicht die Rechenzeit. Lieber lange
    # warten als einen Job verlieren — ein fehlendes Motiv kostet spaeter
    # eine Wiederholung im Schnitt.
    wait_times = [15, 30, 45, 60, 90, 120, 150, 180, 210, 240, 300]
    for attempt in range(retries):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {token()}",
                     "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:400]
            if e.code in (429, 500, 503, 504) and attempt < retries - 1:
                w = wait_times[min(attempt, len(wait_times) - 1)]
                print(f"  Kontingent ({e.code}), warte {w}s "
                      f"[Versuch {attempt + 2}/{retries}]", flush=True)
                time.sleep(w)
                continue
            raise RuntimeError(f"HTTP {e.code}: {body}") from None
        except Exception:
            if attempt >= retries - 1:
                raise
            time.sleep(wait_times[min(attempt, len(wait_times) - 1)])
    raise RuntimeError("Failed after all retries")


def load_reference(ref_name: str) -> str | None:
    for ext in (".png", ".jpg", ".jpeg"):
        p = REF_DIR / f"{ref_name}{ext}"
        if p.exists():
            return base64.b64encode(p.read_bytes()).decode()
    return None


def generate_image(prompt: str, output_name: str, modell: str = "flash",
                   aspect: str = "16:9", resolution: str = "2k",
                   reference: str | None = None,
                   nachtrag: str = "") -> pathlib.Path:
    model_id, loc = MODELLE[modell]
    host = "aiplatform" if loc == "global" else f"{loc}-aiplatform"
    url = (f"https://{host}.googleapis.com/v1/projects/{project()}"
           f"/locations/{loc}/publishers/google/models/{model_id}:generateContent")

    parts: list[dict[str, Any]] = []
    ref_data = load_reference(reference) if reference else None
    if ref_data:
        parts.append({"inlineData": {"mimeType": "image/png", "data": ref_data}})

    voll = f"{STYLE_KEY}\n\n{prompt}"
    if nachtrag:
        voll += f"\n\n{nachtrag}"
    if ref_data:
        voll += ("\n\nUse the supplied photograph only as the ground truth for the shape and "
                 "proportions of the construction. Match the colour palette named above, not "
                 "the colour of the reference.")
    voll += f"\n\nDo not include: {NEGATIVE}"

    parts.append({"text": voll})
    payload = {"contents": [{"role": "user", "parts": parts}],
               "generationConfig": {"responseModalities": ["IMAGE"],
                                    "imageConfig": {"aspectRatio": aspect,
                                                    "imageSize": resolution.upper()}}}

    r = post(url, payload)
    images: list[bytes] = []
    for cand in r.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                images.append(base64.b64decode(inline["data"]))
    if not images:
        fr = (r.get("candidates") or [{}])[0].get("finishReason", "?")
        raise RuntimeError(f"kein Bild zurueck (finishReason={fr})")

    OUT.mkdir(parents=True, exist_ok=True)
    output_path = OUT / f"{output_name}.png"
    output_path.write_bytes(images[0])
    return output_path


# --------------------------------------------------------------------- Jobs
# Schwerpunkt nach VISUAL_SPEC: das Phaenomen, nicht die Dokumente.
# "M" markiert Motive, an die die Spiegel-Geometrie angehaengt wird.

# Welches Bild in welchem Akt zuerst laeuft. Bestimmt seine Farbwelt.
AKT_VON_BILD = {
    "spg_akademgorodok_winter": "S2",
    "spg_anlage_heute_leer": "S8",
    "spg_besucher_heute": "S8",
    "spg_blaetterstapel": "S2",
    "spg_brennpunkt": "S3",
    "spg_dikson_funkstation": "S2",
    "spg_dikson_hafen": "S6",
    "spg_drehplattform": "S3",
    "spg_empfaenger_kuechentisch": "S5",
    "spg_farbflaechen": "S1",
    "spg_geburtsort_norden": "S5",
    "spg_gesicht_aus_farbe": "S1",
    "spg_haende_kribbeln": "S5",
    "spg_innenflaeche_detail": "S2",
    "spg_institut_flur": "S2",
    "spg_institut_treppe": "S2",
    "spg_kabel_im_eis": "S6",
    "spg_kabeltrommel_schnee": "S6",
    "spg_kaznacheev_labor": "S2",
    "spg_kindheitsszene": "S5",
    "spg_kompass_dreht": "S5",
    "spg_kozyrev_raum_leer": "S1",
    "spg_kurzwelle_empfaenger": "S2",
    "spg_labor_nachbau_leer": "S5",
    "spg_lagerwerkstatt": "S8",
    "spg_landschaft_aus_licht": "S1",
    "spg_leerer_stuhl": "S5",
    "spg_licht_geht_aus": "S1",
    "spg_magnetfeld_schwach": "S4",
    "spg_mikroskop_makro": "S2",
    "spg_montagehalle": "S6",
    "spg_nordlicht_ueber_masten": "S6",
    "spg_notizbuch_zeit": "S2",
    "spg_patentmappe": "S8",
    "spg_platte_profil": "S3",
    "spg_protokollblatt_makro": "S1",
    "spg_protokollstapel": "S1",
    "spg_pulkowo_nacht": "S8",
    "spg_quarzglas_kulturen": "S2",
    "spg_ringe": "S1",
    "spg_schimmern_rand": "S1",
    "spg_schleifen_hand": "S3",
    "spg_schreibtisch_rechenschieber": "S8",
    "spg_sender_symbol": "S7",
    "spg_sitzung_weit": "S1",
    "spg_spalt_schliesst": "S1",
    "spg_spirale_im_schnee": "S2",
    "spg_spirale_oben": "S4",
    "spg_stille_ohr": "S1",
    "spg_stuhl_detail": "S1",
    "spg_taiga_birken": "S2",
    "spg_teleskop_mond": "S8",
    "spg_trofimov_aufzeichnungen": "S2",
    "spg_tuer_geht_auf": "S1",
    "spg_uhr_gleichzeitig": "S5",
    "spg_unbehagen": "S5",
    "spg_verladung_polarkreis": "S6",
    "spg_waage_kreisel": "S8",
    "spg_waerme_gesicht": "S5",
    "spg_weite_wasser": "S2",
    "spg_werkstatt_platten": "S2",
    "spg_zeichnung_wird_bau": "S3",
    "spg_zeitungsseite": "S7",
    "spg_zifferblatt": "S1",
    "spg_zimmer_fenster": "S1",
}


def J(id_, prompt, spiegel=False, aspect="16:9", akt=""):
    return {"id": id_, "prompt": prompt, "spiegel": spiegel, "aspect": aspect,
            "akt": akt or AKT_VON_BILD.get(id_, "")}


JOBS = [
    # ---------------------------------------------- Akt 1: die Sitzung
    J("spg_sitzung_weit",
      "Wide interior shot of a windowless laboratory hall with a bare concrete floor and "
      "a low painted ceiling. In the centre stands the construction, lit from one copper-warm "
      "work lamp clamped to a wall bracket at the left edge of frame, its light raking across "
      "the polished aluminium so the metal glows warm ochre on one side and cold aurora green "
      "on the other. A man in his forties in a plain dark wool sweater sits inside on the "
      "chair, seen through the entry gap, small in the frame. Deep shadow fills the corners.",
      spiegel=True),
    J("spg_spalt_schliesst",
      "Close three-quarter view of the vertical entry gap of the aluminium spiral seen from "
      "outside, roughly 40 centimetres wide, the polished inner faces on both sides catching "
      "a thin aurora-green line of reflected light down their whole height. Through the gap, "
      "half visible, the shoulder and knee of a seated person and the leg of a plain metal "
      "chair. A hand at the edge of frame is about to push the last curved sheet closed. "
      "Copper-warm lamp light from behind the camera, cold blue shadow inside.",
      spiegel=True),
    J("spg_licht_geht_aus",
      "The same laboratory hall an instant after the lamps were switched off. Almost total "
      "darkness in deep arctic night blue; only the faintest aluminium highlight survives as "
      "a thin vertical rim along the curved sheets, and a single copper-orange pilot lamp "
      "glows low on the far wall. The silhouette of the seated figure is barely separable "
      "from the dark. Heavy film grain.",
      spiegel=True),
    J("spg_schimmern_rand",
      "A nearly black frame in deep arctic night blue, filling the whole image, with no object, "
      "no room, no wall and no opening visible anywhere. Only at the extreme left and right "
      "edges of the frame a faint formless aurora-green shimmer has begun, soft, uneven, "
      "without outline, like the first stage of a visual afterimage in complete darkness. A "
      "trace of copper warmth low in the frame. Heavy colour-film grain, no geometry of any "
      "kind, no tube, no ring, no circle."),
    J("spg_farbflaechen",
      "Abstract but photographic: large soft drifting fields of colour seen in complete "
      "darkness. Broad aurora-green and deep teal planes overlapping with a slow copper-orange "
      "band and a violet edge, out of focus, no hard outline, no object. The look of pressure "
      "phosphenes photographed on grainy colour film. Black arctic-blue ground under everything."),
    J("spg_ringe",
      "Concentric rings of coloured light seen in total darkness, seven or eight of them, "
      "sliding into and through one another off-centre. Aurora green and deep teal for the "
      "outer rings, copper orange for the innermost, a violet fringe where two rings cross. "
      "Soft edges, uneven brightness, heavy colour-film grain, black arctic-blue ground. "
      "No object, no room, no person."),
    J("spg_landschaft_aus_licht",
      "A wide landscape assembling itself out of light rather than being lit: a flat expanse "
      "of water meeting a low horizon, the whole scene built from aurora-green and copper "
      "luminous bands that have not yet resolved into ground, so the shoreline dissolves into "
      "coloured striations at both edges of frame. Violet sky above, arctic-blue water below. "
      "Beautiful and unresolved, photographic grain, no people, no buildings."),
    J("spg_zimmer_fenster",
      "An unfamiliar room seen as if remembered rather than observed: a plain interior with "
      "a single tall window, the wall surfaces breaking down into soft aurora-green and violet "
      "colour fields towards the edges of frame while the window itself stays sharp and pours "
      "copper-warm light onto a bare wooden floor. No furniture is fully formed. Arctic-blue "
      "shadow, colour-film grain, nobody present."),
    J("spg_gesicht_aus_farbe",
      "A human face coalescing out of colour in complete darkness — the features assembled "
      "from overlapping aurora-green and copper luminous patches with violet in the shadow "
      "side, recognisable as a face for only a moment, dissolving back into colour fields at "
      "the jaw and hairline. Frontal, calm, eyes indicated rather than drawn. Black "
      "arctic-blue ground, heavy grain. Not a portrait, not a painting."),
    J("spg_zifferblatt",
      "Macro photograph of the enamel dial of an old Soviet mechanical wall clock in near "
      "darkness. The minute and hour hands have lost their direction: both are captured "
      "mid-sweep as smeared copper-orange arcs running the wrong way around the dial, one "
      "doubled back on itself. The dial face is aluminium cream, the numerals are plain "
      "batons, the ground behind is arctic night blue, and an aurora-green reflection lies "
      "across the glass. Grain, no readable writing."),
    J("spg_tuer_geht_auf",
      "View from inside the darkened aluminium construction towards the entry gap as it is "
      "opened from outside. A hard wedge of copper-warm corridor light cuts into the black "
      "interior and strikes the polished inner face, throwing a long aurora-green reflection "
      "down the metal. The silhouette of a standing person fills the gap. The seated figure "
      "in the foreground is still in shadow, head turning towards the light.",
      spiegel=True),
    J("spg_protokollstapel",
      "A tall stack of handwritten protocol sheets on a scratched wooden desk in a dim "
      "office, photographed from a low three-quarter angle so the stack fills the left of "
      "frame. The paper is warm cream, the topmost sheets carry loose pencil handwriting and "
      "small hand-drawn shapes, deliberately illegible. One warm desk lamp lights the stack "
      "from the right and is the only light in the room; behind it the office falls into "
      "brown darkness, with cold grey daylight just visible at a distant window. No coloured "
      "light and no floating lights anywhere in the frame. Film grain."),

    # ------------------------------------- Akt 2: Nowosibirsk und die Menschen
    J("spg_akademgorodok_winter",
      "Wide winter exterior of Akademgorodok, the Siberian science town, late 1980s: five "
      "storey concrete apartment slabs standing among bare birch trunks in deep snow, blue "
      "hour, minus thirty degrees. Copper-warm light in a scattering of windows against "
      "arctic-blue snow and violet sky, a faint aurora-green band low over the treeline. "
      "Photographic, grainy, no people, no cars, no signage."),
    J("spg_institut_flur",
      "A long institute corridor in a Soviet research building at night: linoleum floor, "
      "enamel-painted walls in pale aluminium cream to shoulder height and arctic blue above, "
      "a row of tall doors, one of them standing open with copper-warm light spilling out "
      "across the floor. An aurora-green fluorescent tube glows at the far end. Deep "
      "perspective, grain, nobody in frame, no readable lettering."),
    J("spg_kaznacheev_labor",
      "Editorial reconstruction photographed STRICTLY FROM BEHIND, half-length: an older man "
      "in a white lab coat over a dark suit stands with his back fully to the camera at a "
      "laboratory bench in a late-1980s Soviet institute, head bowed over a binocular "
      "microscope. Only the back of his head, shoulders and coat are visible; no part of his "
      "face, not even in profile, and no reflection of it anywhere. Bakelite instrument "
      "housings, brass switches, enamel trays and paper rolls on the bench. A copper-warm "
      "bench lamp lights the microscope and the bench; the room behind is arctic blue with an "
      "aurora-green cast from a window."),
    J("spg_quarzglas_kulturen",
      "Macro photograph of two round glass tissue-culture vessels standing face to face on a "
      "dark laboratory bench, separated by an upright pane of quartz glass held in a simple "
      "aluminium frame. The culture medium in the left vessel is a clouded copper amber, in "
      "the right a clear aurora green. A single hard light from behind the quartz makes the "
      "pane's edge glow. Arctic-blue background, shallow but honest depth, film grain."),
    J("spg_trofimov_aufzeichnungen",
      "Editorial reconstruction, three-quarter from behind: a man in his forties in a dark "
      "polo-neck sits at a desk in a dim institute office, writing in a large ruled ledger "
      "under a copper-warm articulated lamp. His face is turned away and not identifiable. "
      "Beside the ledger lie a slide rule, a stack of protocol sheets and a black bakelite "
      "telephone. Arctic-blue room behind, aurora-green light from a corridor door left ajar. "
      "Film grain."),
    J("spg_werkstatt_platten",
      "Institute workshop, late 1980s: two large curved sheets of aluminium alloy about "
      "2.8 metres tall lean against a steel frame while a third lies across trestles being "
      "polished by hand. The polished faces throw long aurora-green and copper reflections "
      "across the workshop wall. Tools, a bucket, cloths, sawdust on the floor. A single "
      "high window gives cold arctic-blue daylight against the copper-warm work lamp. Only "
      "hands and forearms of a worker visible at the edge of frame. Grain."),

    # --------------------------------------------- Akt 3: die Maschine, Patent
    J("spg_zeichnung_wird_bau",
      "A single wide frame split by an invisible vertical seam. The LEFT half is a technical "
      "drawing in fine copper-brown ink on warm cream paper: an elevation view of six tall "
      "narrow rectangular plates standing side by side in a row, each drawn as a slightly "
      "curved upright panel about 2.8 metres tall, with plain dimension lines above them. The "
      "RIGHT half is a photograph of exactly the same six plates built and standing upright on "
      "a workshop floor in polished aluminium, forming an open cylinder with a gap, "
      "aurora-green reflections down the metal and a copper-warm lamp at their foot. Same "
      "height and same spacing in both halves. Arctic-blue ground, film grain, nothing "
      "readable, no sculpture, no pinwheel, no spiral ornament."),
    J("spg_innenflaeche_detail",
      "Extreme close-up of the ground and polished inner face of a curved aluminium alloy "
      "sheet, filling the whole frame. Fine concentric grinding marks catch the light; a "
      "broad aurora-green reflection sweeps diagonally across the surface with a copper-orange "
      "highlight along the curved edge and arctic-blue shadow at the bottom of frame. The "
      "metal has real scratches and slight waviness. Heavy film grain."),
    J("spg_drehplattform",
      "Low three-quarter close-up of the base of the construction: a heavy low motorised "
      "turntable of welded steel with an exposed toothed gear ring and a small electric motor "
      "with a bakelite terminal box bolted to the floor beside it. The lowest 60 centimetres "
      "of two curved aluminium sheets rise from the platform edge, their polished faces "
      "reflecting the copper-warm work lamp and an aurora-green glow. Concrete floor, cable "
      "run in a steel conduit. Arctic-blue shadow, grain."),
    J("spg_spirale_oben",
      "Looking straight down from the ceiling onto the construction: six curved aluminium "
      "sheets form an open spiral with one clear entry gap, the polished inner faces reading "
      "as a bright aluminium ribbon against the arctic-blue concrete floor. In the exact "
      "centre stands a plain metal chair, empty. An aurora-green reflection runs around the "
      "inner curve and a copper-warm lamp pool lies across the floor at the gap. Nothing "
      "covers the top. Grain, no people.",
      spiegel=True),
    J("spg_brennpunkt",
      "Physical demonstration photographed in a dark room: a single curved polished aluminium "
      "sheet stands upright, and a fan of thin light rays strikes its inner face and converges "
      "to a bright focus point roughly half a metre in front of the metal, marked by a thin "
      "aluminium rod on a stand. The rays are aurora green, the focus flares copper orange, "
      "the room behind is arctic night blue. Practical, laboratory-looking, film grain, no "
      "diagrams, no text."),
    J("spg_patentmappe",
      "A grey card folder tied with cotton tape lying open on a desk under a copper-warm lamp, "
      "showing two pages of a typed technical specification on cream paper with a fine ink "
      "line drawing of a curved-plate construction on the right-hand page. Photographed "
      "straight down, slightly off-square. Aurora-green daylight from a window falls across "
      "the upper left of the desk; arctic-blue shadow at the lower edge. The typing and "
      "handwriting are present but not readable. Film grain."),

    # ------------------------------------------- Akt 4: der Kozyrev-Raum
    J("spg_magnetfeld_schwach",
      "Photographic laboratory demonstration of a weakened magnetic field: iron filings on a "
      "sheet of cream paper laid on a dark bench, arranged in field lines by a bar magnet at "
      "the frame edge — but towards the centre of the paper the lines thin out and break "
      "apart into an empty patch. Lit hard from the side so the filings cast long shadows. "
      "Aurora-green reflected light on the paper, copper-warm lamp at the right edge, "
      "arctic-blue surround. Macro, grain, no text."),
    J("spg_kozyrev_raum_leer",
      "The construction standing empty in a completely dark hall, photographed from a low "
      "wide angle. The only light is a cold aurora-green glow that appears to come from "
      "inside the open spiral itself, spilling out through the entry gap onto the concrete "
      "floor and up the polished inner faces; a single copper-orange pilot lamp burns on the "
      "far wall. The empty metal chair is visible through the gap. Deep arctic-blue shadow "
      "everywhere else, heavy grain.",
      spiegel=True),
    # Kein Leuchten an der Hand. Genau das las sich sofort als KI-Effekt.
    # Das Kribbeln wird ueber Haltung und Licht erzaehlt, nicht ueber Glow.
    J("spg_haende_kribbeln",
      "Extreme close-up of the hands of a seated person resting on the thighs of dark wool "
      "trousers in a very dark room. The fingers are slightly splayed and tensed, as if "
      "something is happening in them. A single hard practical lamp far to the left rakes "
      "across the skin so the knuckles and tendons catch the light and the rest falls into "
      "black. Ordinary skin, visible pores and hair, short unmanicured nails, a plain "
      "wedding band. Straight photography with a long lens, heavy colour-film grain. The "
      "hands emit no light of their own and have no outline, rim, halo or coloured edge."),

    # ------------------------------------------ Akt 6 und 7: Aurora Borealis
    J("spg_dikson_funkstation",
      "Wide exterior at polar night: a low weathered radio station building of timber and "
      "corrugated iron on the flat snow shore of the Arctic Ocean, two guyed lattice antenna "
      "masts beside it, sea ice reaching to the horizon. Copper-warm light in two windows and "
      "over the door; a broad aurora-green and violet auroral band stands in the arctic-blue "
      "sky above the masts and lays a faint green sheen on the snow. Photographic, grainy, "
      "no people, no readable signage."),
    J("spg_nordlicht_ueber_masten",
      "Looking almost straight up from the base of a steel lattice antenna mast into a full "
      "auroral display: vertical curtains of aurora green shading to deep teal at the top "
      "with violet fringes, folded and rayed, filling the arctic-blue polar sky. The mast and "
      "its guy wires read as black aluminium-edged silhouettes against the light. Long "
      "exposure look, real star field, heavy colour-film grain."),
    J("spg_spirale_im_schnee",
      "The aluminium construction erected outdoors on packed snow at polar night, guyed with "
      "thin steel cables pegged into the ice. Six curved polished sheets form an open spiral "
      "with a visible entry gap; frost has settled on the matte outer faces while the polished "
      "inner faces mirror the aurora-green sky. A green and violet auroral band stands "
      "overhead; a copper-warm portable lamp on a tripod lights the snow at the entry gap. "
      "Wide, low angle, grain, no people.",
      spiegel=True),
    J("spg_kabel_im_eis",
      "Close low shot of two heavy rubber-sheathed cables running out of a snowdrift across "
      "bare blue-green sea ice towards the base of an aluminium plate, frozen into the "
      "surface, with fresh frost crystals on the sheathing. Aurora-green light from the sky "
      "reflects off the ice, a copper-warm lamp glow enters from the upper right, arctic-blue "
      "shadow in the drift. Sharp, cold, film grain."),
    J("spg_sender_symbol",
      "A woman in her thirties in a heavy dark sweater sits upright on a plain metal chair in "
      "the centre of the open aluminium spiral, eyes closed, hands flat on her thighs, "
      "concentrating. Nothing is attached to her. On a small stand directly in front of her, "
      "at eye height, stands a plain white card with a single simple black triangle drawn on "
      "it. One copper-warm lamp lights her face from the left; the polished sheets behind "
      "throw aurora-green reflections. Arctic-blue shadow, grain.",
      spiegel=True),
    J("spg_empfaenger_kuechentisch",
      "A domestic kitchen table at night, photographed from a high three-quarter angle: a "
      "sheet of squared paper, a wooden pencil lying across it, a hand mid-stroke having just "
      "drawn a single simple triangle, a glass of tea in a metal holder and a small mechanical "
      "alarm clock beside them. A copper-warm ceiling lamp lights the table; the window behind "
      "is arctic blue with a faint aurora-green glow. Worn oilcloth, film grain, no readable "
      "writing."),
    J("spg_kurzwelle_empfaenger",
      "Close three-quarter photograph of a Soviet short-wave receiver from the late 1980s on "
      "a desk: bakelite case, an illuminated tuning dial glowing copper amber, brass toggle "
      "switches, a fabric speaker grille, an aluminium-cased microphone on a stand beside it. "
      "The dial light is the warm source; cold aurora-green light comes from a window at the "
      "left. Arctic-blue shadow, grain, no readable lettering on the dial."),
    J("spg_blaetterstapel",
      "Overhead photograph of thirty or forty collected sheets of paper spread and overlapping "
      "across a dark wooden table, each carrying a single simple pencil drawing — circles, "
      "crosses, triangles — in different hands, some sure, some hesitant. The paper is warm "
      "cream, the table arctic blue in shadow. A copper-warm lamp lights the centre of the "
      "spread, an aurora-green cast falls across the upper edge. Film grain, no readable "
      "writing, only the simple shapes."),
    J("spg_verladung_polarkreis",
      "Daytime arctic exterior under a low sun: five large flat rectangular aluminium sheets, "
      "each about 2.8 metres long, lying FLAT and stacked one on top of another, roped down "
      "onto a wooden sledge and the open bed of a truck beside a small ice-bound harbour. The "
      "sheets are flat panels, not rolled and not formed into any tube or cylinder. Men in "
      "heavy dark parkas, seen from behind, handle the ropes. The polished top sheet catches "
      "the low copper-orange sun and an aurora-green reflection from the ice. Arctic-blue sea "
      "ice and violet sky. Documentary wide shot, film grain, no faces, no lettering."),

    # -------------------------------------------------- Akt 8: was bleibt
    J("spg_anlage_heute_leer",
      "A present-day version of the same hall, empty and quiet: the aluminium construction "
      "still standing, dust on the matte outer faces, the polished inner faces dulled but "
      "still throwing a soft aurora-green reflection. Cold daylight falls from a high window "
      "in an arctic-blue shaft across the concrete floor; one copper-warm bulb still burns on "
      "the far wall. The plain metal chair stands in the centre, empty. Wide, still, film "
      "grain, no people.",
      spiegel=True),
    J("spg_leerer_stuhl",
      "A plain metal chair standing alone in the exact centre of the dark open aluminium "
      "spiral, photographed at seated eye height through the entry gap. The chair is lit by a "
      "single narrow copper-warm beam from above; the curved polished sheets around it are "
      "visible only as aurora-green vertical highlights in the arctic-blue dark. Nothing "
      "else in frame. Grain.",
      spiegel=True),
    J("spg_labor_nachbau_leer",
      "A plain university laboratory at night, empty: bare benches, a trolley, stacked "
      "steel stools, a roll of aluminium sheet standing unopened against the wall under a "
      "dust cover. Cold grey moonlight through the windows, one warm desk lamp left burning "
      "over an empty bench, everything else in shadow. No coloured light of any kind, no "
      "illuminated signs, no indicator lamps. Wide, still, film grain, no people, no flat "
      "screens, no readable lettering."),
    J("spg_teleskop_mond",
      "A large 1950s Soviet refracting telescope inside its dome at night, seen from below "
      "and behind, the tube raised towards an open shutter through which a cold aluminium "
      "moon is visible. The dome interior is arctic blue; a copper-warm work lamp lights the "
      "brass drive gears and the observer's ladder; an aurora-green glow enters through the "
      "shutter slit. No people, film grain."),
    J("spg_schreibtisch_rechenschieber",
      "Editorial reconstruction from behind, half-length: a man in a dark jacket sits at a "
      "desk in a 1960s observatory office, working over sheets of calculation with a slide "
      "rule; his face is not visible. A copper-warm desk lamp, a brass inkwell, a stack of "
      "journals and a dark window showing arctic-blue night with a faint aurora-green band. "
      "Film grain, no readable writing."),

    # ------------------------------------------------------------ zweite Serie
    # Ziel: mindestens 85 Einzelbilder in der Timeline ohne Wiederholung ueber
    # vier — dafuer braucht jeder Akt mehr eigene Motive.
    J("spg_stuhl_detail",
      "Close low photograph of a plain welded metal chair standing on a concrete floor, seen "
      "against the curved polished aluminium wall behind it about a metre away. The metal of "
      "the chair is worn to bare steel at the seat edge. A copper-warm lamp lights it from the "
      "left, an aurora-green reflection runs down the aluminium behind. Arctic-blue shadow, "
      "film grain, nobody present."),
    J("spg_stille_ohr",
      "Very close photograph of the side of a person's head and ear in near darkness, seen "
      "from behind and slightly above, hair and the collar of a dark wool sweater visible. A "
      "thin warm amber rim of light traces the ear and jaw; everything else is black. Nothing "
      "is attached to the head — no headphones, no electrodes, no cables. No coloured light "
      "on the skin. Long lens, heavy grain."),
    J("spg_protokollblatt_makro",
      "Macro photograph of a single sheet of squared paper on a dark desk, filled with dense "
      "handwriting in blue-black ink and a small hand-drawn diagram of concentric circles in "
      "the margin, deliberately illegible. The paper is warm cream under one warm desk lamp "
      "that is the only light in the frame; the desk falls into brown shadow at every edge. "
      "No coloured light, no floating lights, no out-of-focus coloured spots anywhere. "
      "Shallow angle, film grain."),
    J("spg_taiga_birken",
      "Siberian taiga in deep winter at blue hour: dense bare birch trunks in snow, receding "
      "into arctic-blue haze, a low violet sky visible between the crowns and a faint "
      "aurora-green band above the treeline. One distant copper-warm window light glows far "
      "back among the trunks. Cold, still, film grain, no people, no path."),
    J("spg_institut_treppe",
      "A stairwell in a Soviet research institute at night: terrazzo steps, a heavy iron "
      "handrail painted aluminium cream, walls in arctic blue enamel, a tall window on the "
      "half landing showing snow outside. One copper-warm bulb burns over the landing, an "
      "aurora-green fluorescent glows on the floor above. Looking up the well, film grain, "
      "nobody in frame, no lettering."),
    J("spg_mikroskop_makro",
      "Macro three-quarter photograph of the head and stage of a heavy 1970s laboratory "
      "microscope in black crackle enamel with brass focus knobs, a glass slide clipped on "
      "the stage. The substage lamp throws a warm copper cone up through the slide; an "
      "aurora-green reflection sits on the black enamel body. Arctic-blue laboratory darkness "
      "behind, film grain, no lettering."),
    J("spg_platte_profil",
      "A single curved aluminium alloy sheet about 2.8 metres tall standing upright on a "
      "workshop floor, photographed from the side so its curve reads clearly as an arc in "
      "profile, with a wooden support brace behind it. The polished inner face catches an "
      "aurora-green reflection along its whole height, the matte outer face is warm aluminium "
      "cream, and a copper-warm work lamp stands at its foot. Arctic-blue workshop behind, "
      "film grain, no people."),
    J("spg_schleifen_hand",
      "Close photograph of two bare hands working a polishing block across the inner face of "
      "a large curved aluminium sheet, fine metal dust in the air catching the light. The "
      "polished area to the left of the block is mirror-bright with an aurora-green "
      "reflection, the unpolished area to the right is dull warm aluminium. Copper-warm work "
      "lamp from the upper right, arctic-blue shadow, heavy film grain, no face."),
    J("spg_montagehalle",
      "A high institute assembly hall with steel roof trusses, photographed wide: eight large "
      "curved aluminium sheets stand in a row along one wall waiting to be erected, a chain "
      "hoist hangs from a girder, a wooden crate and coils of cable on the floor. Cold "
      "arctic-blue daylight falls from high windows, one copper-warm lamp burns near the "
      "crate, aurora-green reflections run down the sheets. Grain, no people."),
    J("spg_kompass_dreht",
      "Macro photograph of a brass marine compass on a dark bench in a dim room, its card "
      "caught mid-swing and blurred so no bearing can be read. Copper-warm lamp light rakes "
      "the brass rim, an aurora-green reflection crosses the domed glass, the ground behind "
      "is arctic night blue. Film grain, no readable markings."),
    J("spg_unbehagen",
      "Close photograph of a seated man's face and shoulder in near darkness, three-quarter "
      "from the side, jaw set and eyes open, clearly uneasy. The only light is a narrow "
      "aurora-green reflection from a polished metal surface just out of frame and a distant "
      "copper-warm glow behind his shoulder. Arctic-blue dark, nothing attached to his head, "
      "heavy grain."),
    J("spg_kindheitsszene",
      "One single continuous photograph — no grid, no panels, no split screen. A remembered "
      "summer afternoon surfacing out of blackness: a low wooden fence, a strip of long grass "
      "and the corner of a village house, all of it built from soft gold and amber light that "
      "dissolves into black at every edge. Nothing is fully sharp except one sunlit patch of "
      "grass. No electric light, no screens, no signage, no people, no aurora and no magenta "
      "or cyan anywhere. Very soft focus, heavy grain."),
    J("spg_weite_wasser",
      "A wide flat expanse of still water meeting a low horizon under a broad aurora-green "
      "and violet sky, photographed as if from ground level. A band of copper-orange light "
      "lies along the horizon and repeats as a broken reflection on the water. Arctic-blue "
      "foreground. Empty, silent, film grain, no boats, no people, no land features."),
    J("spg_waerme_gesicht",
      "Close photograph of a seated woman's face in near total darkness, eyes closed, calm, "
      "lit by a single warm tungsten lamp standing just out of frame to the left, so that one "
      "side of the face is modelled and the other falls away into black. Visible pores, a "
      "loose strand of hair, a woollen collar. Nothing attached to her head. No coloured light "
      "of any kind on the skin and no glow coming out of her. Long lens, heavy film grain."),
    J("spg_geburtsort_norden",
      "Two horizons in one frame, split by an invisible vertical seam: on the left an arctic "
      "coast under an aurora-green sky with sea ice; on the right a warm southern steppe under "
      "a copper-orange evening sky with dry grass. Both halves in the same grainy colour film, "
      "same low camera height, arctic-blue shadow along the seam. No people, no buildings, no "
      "lettering."),
    J("spg_dikson_hafen",
      "A small ice-bound arctic harbour at low polar light: a wooden pier, a rusted crane, a "
      "single ship frozen in beside it, snow on every horizontal surface. Copper-orange low "
      "sun on the crane arm and the ship's aluminium superstructure, arctic-blue ice, violet "
      "sky with a faint aurora-green band. Wide documentary shot, film grain, no people, no "
      "readable markings."),
    J("spg_kabeltrommel_schnee",
      "A large wooden cable drum half buried in a snowdrift beside a low arctic building at "
      "night, heavy cable still wound on it, frost on the timber. A copper-warm lamp over the "
      "building door lights one side; the snow reads arctic blue with an aurora-green sheen "
      "from the sky. Close wide angle, film grain, no people, no lettering."),
    J("spg_zeitungsseite",
      "Macro photograph at a shallow angle of a folded newspaper page on a wooden table, the "
      "columns of type reduced to grey texture by the angle and the shallow focus, with one "
      "small hand-drawn circle in pencil in the middle of a column. Copper-warm lamp from the "
      "left, an aurora-green cast from a window on the right, arctic-blue shadow. Warm cream "
      "newsprint, film grain, nothing readable."),
    J("spg_uhr_gleichzeitig",
      "Three small mechanical alarm clocks of different makes standing in a row on a dark "
      "wooden shelf, all showing the same time, photographed straight on. Their cream enamel "
      "dials catch one warm tungsten lamp from the left; brass cases, worn nickel bezels, a "
      "little dust. The wall behind is plain and unlit. No coloured light anywhere in the "
      "picture. Film grain, plain baton numerals, no brand lettering."),
    J("spg_besucher_heute",
      "A present-day visitor, seen from behind, standing at the entry gap of the aluminium "
      "construction in a quiet hall and looking in. Plain dark coat, no modern branding "
      "visible. Cold arctic-blue daylight from a high window, one copper-warm lamp inside "
      "throwing an aurora-green reflection off the polished sheets onto the floor at the gap. "
      "Wide, still, film grain.",
      spiegel=True),
    J("spg_pulkowo_nacht",
      "A nineteenth-century observatory building on a low hill under a winter night sky, its "
      "dome open a slit, snow on the roofs and the drive. One single window on the ground "
      "floor burns copper-warm; everything else is arctic blue, with a faint aurora-green band "
      "and a full star field above the dome. Wide, still, film grain, no people, no lettering."),
    J("spg_lagerwerkstatt",
      "Editorial reconstruction, from behind and in poor light: a man in a padded jacket "
      "works at a rough wooden bench in a cold barrack workshop, filing a small metal part "
      "under a single weak copper-warm bulb on a cord. His face is not visible. Frost on the "
      "small window, arctic-blue light coming through it, an aurora-green cast on the far "
      "wall. Heavy film grain, no uniforms, no barbed wire, no violence."),
    J("spg_notizbuch_zeit",
      "Macro photograph of an open notebook on a desk, the left page filled with a hand-drawn "
      "curve and columns of figures in pencil, deliberately illegible, a fountain pen lying "
      "across it. Warm cream paper under a copper-warm lamp, aurora-green reflection along the "
      "metal pen barrel, arctic-blue shadow at the gutter. Shallow angle, film grain."),
    J("spg_waage_kreisel",
      "A precision beam balance in a glass case and a heavy brass gyroscope on a wooden "
      "laboratory bench, photographed in three-quarter view. The brass and aluminium catch a "
      "copper-warm lamp from the right; the glass case reflects an aurora-green window light. "
      "Arctic-blue room behind, dust visible on the bench, film grain, no lettering, no people."),

    # ------------------------------------------------------------------
    # Nachtrag: Motive gegen die Wiederholungen im selben Akt. Der erste
    # Durchgang hatte 19 Stellen, an denen dasselbe Bild innerhalb eines
    # Akts mehrfach lief — global unauffaellig, im Erleben eine Doppelung.
    # ------------------------------------------------------------------
    J("spg_kaznacheev_schreibt", akt="S2", prompt=(
      "A man in his late fifties in a white lab coat writing in a hardbound ledger at a "
      "desk in a Soviet institute office, seen from the side. Fountain pen, ink bottle, a "
      "stack of buff folders, a green banker's lamp. Bookshelves of bound journals behind "
      "him. He is absorbed and does not look up. Winter daylight from a tall window at the "
      "left. Documentary photograph, no text legible anywhere.")),
    J("spg_institut_aussen_winter", akt="S2", prompt=(
      "Exterior of a low 1970s Soviet research institute in deep winter, four storeys, "
      "cream render with olive-painted window frames, snow banked against the wall, birch "
      "trees bare in front. A few windows lit warm yellow in the blue afternoon. Tyre ruts "
      "in packed snow. Wide, still, documentary.")),
    J("spg_petrischalen", akt="S2", prompt=(
      "Close-up of a row of glass petri dishes and culture flasks on a scratched enamel "
      "tray in a 1960s laboratory, warm lamp light from the upper left catching the glass "
      "rims and the meniscus of the liquid inside. Cork stoppers, a steel loop, a burner. "
      "Shallow depth of field, colour film grain.")),
    J("spg_kolben_allein", akt="S2", prompt=(
      "A single sealed glass culture flask standing alone on a dark laboratory bench, lit "
      "from behind so the cloudy liquid inside glows amber against a black background. "
      "Dust on the glass. Nothing else in frame. Macro, quiet, ominous.")),
    J("spg_journalregal", akt="S2", prompt=(
      "A wall of bound laboratory journals and box files on grey metal shelving in an "
      "institute corridor, receding into shadow, lit by one bare bulb. Worn spines, "
      "handwritten labels too small to read. Documentary, warm dusty light.")),
    J("spg_hand_am_notizbuch", akt="S2", prompt=(
      "Overhead close-up of a hand writing a column of figures in a squared notebook on a "
      "wooden desk, sleeve of a lab coat, a slide rule and a cup of tea beside it. Warm "
      "desk lamp light. The writing is not legible. Straight photography, grain.")),

    J("spg_vision_bandmuster", akt="S5", prompt=(
      "Wide horizontal bands of saturated colour drifting across complete darkness — deep "
      "magenta above, cyan and gold beneath, edges soft and unresolved, no object and no "
      "geometry. Photographed on grainy colour film. The look of a colour field seen with "
      "closed eyes.")),
    J("spg_vision_wasserlinie", akt="S5", prompt=(
      "A wide flat horizon of water rendered entirely in light against blackness: a violet "
      "sky band over a gold band over a dark cyan band, nothing else, no shore, no sky "
      "detail, no stars. Soft and luminous, heavy grain. It should read as a remembered "
      "landscape rather than a photograph of one.")),
    J("spg_vision_innenraum", akt="S5", prompt=(
      "The interior of an unfamiliar room appearing out of darkness: the corner of a "
      "ceiling, part of a doorframe and a window, sketched in deep red and gold light, the "
      "rest swallowed by black. Perspective slightly wrong, as if remembered. No furniture "
      "detail, no text, grainy colour film.")),
    J("spg_zeiger_trennen", akt="S5", prompt=(
      "Macro of the two hands of an old enamel clock face, photographed so they appear to "
      "be drifting apart in opposite directions with visible motion blur, the dial itself "
      "sharp behind them. Warm brass and cream enamel under one warm lamp, the rest of the "
      "frame black. No coloured light and no reflection across the glass. Numerals present "
      "but out of focus and unreadable.")),
    J("spg_waerme_haut", akt="S5", prompt=(
      "Extreme close-up of the side of a face in near darkness: cheekbone, temple and the "
      "edge of a closed eye, raked by one warm amber light from below left so only that "
      "band of skin is visible. Visible pores and fine hair, a faint sheen of sweat. The "
      "skin emits no light of its own. Long lens, heavy grain.")),

    J("spg_aurora_ueber_eis", akt="S6", prompt=(
      "Wide arctic seascape at night: pack ice to the horizon under a huge green and "
      "violet aurora arc, the ice picking up the colour, a band of deep blue open water. "
      "No buildings, no people. Enormous and empty. Long exposure on colour film.")),
    J("spg_kisten_entladen", akt="S6", prompt=(
      "Men in heavy fur-lined coats unloading long wooden crates from a tracked vehicle "
      "onto snow at polar night, lit by the vehicle's yellow work lamps and a hand torch. "
      "Breath visible. Seen from a distance, faces not readable. Documentary, cold blue "
      "surround against warm lamp pools.")),

    J("spg_kreis_gezeichnet", akt="S7", prompt=(
      "Overhead macro of a single circle drawn in soft pencil on a sheet of cheap ruled "
      "paper on a wooden kitchen table, the graphite catching a warm bulb overhead. Slight "
      "wobble in the line. Nothing else on the page. Shallow depth, warm domestic light.")),
    J("spg_kreuz_gezeichnet", akt="S7", prompt=(
      "Overhead macro of a simple cross drawn in blue ballpoint on a torn-off sheet of "
      "squared paper lying on an oilcloth-covered table, one corner lifting. Warm evening "
      "lamp light from the right, deep shadow at the edges. No other marks.")),
    J("spg_empfaenger_zweiter", akt="S7", prompt=(
      "A woman in her sixties sitting alone at a small table in a modest apartment at "
      "night, a sheet of paper and a pencil in front of her, hands still, eyes closed, a "
      "wall clock behind her. One warm bulb overhead, cold blue night at the window. "
      "Documentary, unposed, no glow of any kind.")),
    J("spg_kurzwelle_detail", akt="S7", prompt=(
      "Macro of the tuning dial of a 1980s shortwave receiver: illuminated glass scale, "
      "amber backlight, a brass pointer, bakelite knobs worn smooth, a fabric speaker "
      "grille out of focus behind. The scale markings are present but unreadable. Warm "
      "and tactile, film grain.")),
    J("spg_blaetter_ausgebreitet", akt="S7", prompt=(
      "Dozens of small sheets of paper with simple pencil shapes on them, spread out "
      "overlapping across a large table under one hanging lamp, photographed from above at "
      "a slight angle. Some sheets creased, some torn from notebooks. The shapes are "
      "visible as marks but no writing is legible. Warm pool of light, dark edges.")),

    J("spg_anlage_heute_besuch", akt="S8", prompt=(
      "The construction standing in a plain modern room with a painted concrete floor, "
      "photographed in flat daylight from a doorway, entirely ordinary and slightly "
      "shabby, a radiator and a folding chair against the wall. Nothing mysterious about "
      "it. Documentary, low contrast, dusty warm light."), spiegel=True),
    J("spg_patentmappe_offen", akt="S8", prompt=(
      "An open cardboard document folder on a desk with tied fabric ribbons, holding a "
      "thick set of typewritten pages and technical drawings, photographed from above in "
      "warm archive light. Aged cream paper, a rubber stamp impression, paperclip rust "
      "marks. The text is present but not legible.")),
    J("spg_pulkowo_kuppel", akt="S8", prompt=(
      "The dome of a nineteenth-century observatory at dusk seen from below against a "
      "violet and amber sky, the shutter partly open, bare trees at the edge of frame, "
      "snow on the roof. Quiet and elegiac. Colour film, fine grain.")),

    J("spg_glasscheibe_durchblick", akt="S2", prompt=(
      "Macro photograph looking straight through a thick polished quartz plate clamped "
      "upright in a brass stand on a laboratory bench; a sealed culture flask stands on "
      "each side of it, one clouded and one clear, both slightly distorted by the glass. "
      "Backlit by a single warm lamp so the edge of the plate glows. 1960s laboratory, "
      "dust, scratches, colour film grain. No text.")),
    J("spg_zwei_blaetter_vergleich", akt="S7", prompt=(
      "Two small sheets of paper lying side by side on a dark desk under one warm lamp, "
      "each bearing the same simple pencil shape drawn by a different hand, one firmer and "
      "one hesitant. Photographed from directly above, the rest of the desk in shadow. "
      "Creased paper, soft graphite, shallow depth of field. No writing, no numbers.")),

    # ------------------------------------------------------------------
    # Zweiter Nachtrag. Auf dem Kontaktbogen des ersten Durchgangs lag in
    # mehreren Innenraumbildern Polarlichtfarbe als Magenta- und Cyanband
    # ueber Tisch, Hand und Gesicht. Genau daran erkennt man ein erzeugtes
    # Bild sofort. Diese Motive ersetzen die betroffenen Aufnahmen; die
    # Regel dazu steht jetzt im Style Key.
    # ------------------------------------------------------------------
    J("spg_farbflaechen_rein", akt="S1", prompt=(
      "Pure fields of colour against complete blackness, nothing else in the frame: a "
      "broad magenta band above, a cyan one beneath it, a thin seam of gold between them, "
      "all soft-edged and slowly dissolving. No object, no room, no horizon, no geometry, "
      "no figure. Photographed on grainy colour film, slightly out of focus. It should "
      "look like colour seen behind closed eyes.")),
    J("spg_gesicht_lichtspur", akt="S1", prompt=(
      "A human face barely forming out of darkness, drawn only by faint bands of violet "
      "and gold light that suggest a brow, a cheek and the line of a mouth; everything "
      "else is black. No skin texture, no eyes rendered in detail, no shoulders, no room. "
      "Heavy grain, very soft focus, unsettling and incomplete. The light describes the "
      "face from outside; nothing shines out of it.")),
    J("spg_haende_ruhig", akt="S5", prompt=(
      "Close-up of a pair of adult hands resting palm-down on the knees of coarse woollen "
      "trousers, lit by one warm tungsten lamp from the left. Veins, knuckles, a worn "
      "wedding ring, a faint tremor caught as motion blur in one fingertip. The rest of "
      "the room is black. Ordinary lamp light only — no coloured light of any kind on the "
      "skin. Long lens, shallow depth, colour film grain.")),
    J("spg_kuechentisch_warm", akt="S5", prompt=(
      "A scrubbed wooden kitchen table at night photographed from a low angle: a sheet of "
      "ruled paper, a blunt pencil, a glass of tea in a metal holder, a small alarm clock. "
      "One bare yellow bulb hangs above and is the only light in the picture; the corners "
      "of the room fall away into brown darkness. Frost on the window pane in the "
      "background, dark blue night behind it. Quiet, domestic, documentary.")),
    J("spg_wohnung_empfang", akt="S7", prompt=(
      "A man in his forties sitting alone at a table in a small Soviet apartment at night, "
      "shot from across the room. Warm yellow bulb overhead, patterned wallpaper, a "
      "sideboard, a radio. He holds a pencil over a blank sheet, eyes closed, head "
      "slightly bowed. Through the window behind him a faint green aurora is visible in "
      "the night sky and on the glass only — it does not reach into the room. Unposed, "
      "documentary, colour film grain.")),

    J("spg_farbwellen", akt="S5", prompt=(
      "One single continuous photograph filling the entire frame edge to edge — not a "
      "grid, not a collage, not panels, no borders, no split screen. The photograph shows "
      "nothing but colour: a deep red wave rolling into gold across the lower half and a "
      "cold violet crest above it, everything else black. There is no object, no room, no "
      "window, no horizon, no person and no equipment anywhere in the picture. Extremely "
      "soft focus, heavy colour film grain.")),
    J("spg_gesichter_im_dunkeln", akt="S5", prompt=(
      "A tight head-and-shoulders portrait of a middle-aged man in near-total darkness, "
      "facing the camera with his eyes closed. A single narrow edge of warm amber light "
      "runs down the right side of his forehead, nose and jaw; the entire left half of the "
      "face and everything around him is black. Ordinary lamp light only — no coloured "
      "light on the skin, no aurora, no glow coming out of him. No background detail, no "
      "equipment, no window. One single continuous photograph, no grid and no panels. "
      "Long lens, shallow depth of field, heavy colour film grain.")),
    J("spg_dreieck_gezeichnet", akt="S7", prompt=(
      "Overhead macro of a single triangle drawn in soft pencil on a sheet of cheap ruled "
      "paper on a wooden kitchen table, the graphite catching a warm bulb overhead. The "
      "three strokes are slightly uneven and one corner does not quite close. Nothing "
      "else on the page. Shallow depth of field, warm domestic light, no coloured light.")),
    J("spg_sender_im_spiegel", akt="S7", prompt=(
      "A woman in her thirties sitting upright on a plain metal chair at the centre of the "
      "construction, seen from the front at a distance, a small card with one simple "
      "pencilled shape resting on her knee. Her eyes are closed and her hands are still. "
      "One work lamp clamped to the wall behind the camera is the only light; the polished "
      "plates carry its warm reflection and a faint cold daylight from a high window. No "
      "aurora, no coloured light in the room. Unposed, documentary, colour film grain."),
      spiegel=True),
]


def bauen(job: dict, modell: str, resolution: str) -> tuple[str, str]:
    try:
        # Farbe kommt aus dem Akt, nicht aus dem Style Key. Vorher stand eine
        # einzige Palette global — dadurch lief die ganze Folge im selben
        # Tuerkiston und wirkte monoton.
        farbe = akt_farbe(job.get("akt", ""))
        prompt = job["prompt"]
        if farbe:
            prompt = f"{prompt}\n\nColour direction for this passage: {farbe}"
        zusatz = [SPIEGEL] if job.get("spiegel") else []
        if farbe:
            zusatz.append("The colour direction above overrides any colour named "
                          "earlier in this prompt.")
        p = generate_image(prompt, job["id"], modell, job.get("aspect", "16:9"),
                           resolution, job.get("ref"),
                           nachtrag="\n\n".join(zusatz))
        return job["id"], f"ok {p.name}"
    except Exception as e:  # noqa: BLE001
        return job["id"], f"FEHLER {e}"


def generate_all(modell="flash", resolution="2k", jobs=6, only=None, force=False):
    todo = [j for j in JOBS if (not only or j["id"] in only)]
    if not force:
        todo = [j for j in todo if not (OUT / f"{j['id']}.png").exists()]
    if not todo:
        print("nichts zu tun")
        return
    print(f"{len(todo)} Motive, Modell {modell}, {jobs} parallel\n")
    with cf.ThreadPoolExecutor(max_workers=jobs) as ex:
        for name, msg in ex.map(lambda j: bauen(j, modell, resolution), todo):
            print(f"  {name:<32} {msg}", flush=True)
    fehlt = [j["id"] for j in JOBS if not (OUT / f"{j['id']}.png").exists()]
    print(f"\n{len(JOBS) - len(fehlt)}/{len(JOBS)} vorhanden -> {OUT}")
    if fehlt:
        print("fehlt: " + ", ".join(fehlt))


def main():
    parser = argparse.ArgumentParser(description="EP01A Die Spiegel — Bildgenerierung")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate")
    gen.add_argument("name")
    gen.add_argument("prompt")
    gen.add_argument("--model", choices=["pro", "flash"], default="flash")
    gen.add_argument("--ref")
    gen.add_argument("--aspect", default="16:9")
    gen.add_argument("--resolution", default="2k", choices=["1k", "2k", "4k"])
    gen.add_argument("--spiegel", action="store_true",
                     help="Geometrievorgabe der Anlage anhaengen")

    al = sub.add_parser("all")
    al.add_argument("--model", choices=["pro", "flash"], default="flash")
    al.add_argument("--resolution", default="2k", choices=["1k", "2k", "4k"])
    al.add_argument("--jobs", type=int, default=6)
    al.add_argument("--only", default="")
    al.add_argument("--force", action="store_true")

    sub.add_parser("missing")

    args = parser.parse_args()
    if args.command == "generate":
        p = generate_image(args.prompt, args.name, args.model, args.aspect,
                           args.resolution, args.ref,
                           nachtrag=SPIEGEL if args.spiegel else "")
        print(f"  {p}")
    elif args.command == "all":
        generate_all(args.model, args.resolution, args.jobs,
                     set(x for x in args.only.split(",") if x), args.force)
    elif args.command == "missing":
        for j in JOBS:
            if not (OUT / f"{j['id']}.png").exists():
                print(j["id"])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
