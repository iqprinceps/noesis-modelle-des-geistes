#!/usr/bin/env python3
"""EP03 PEAR — Bildmotive, 2K.

Abgeleitet von `tools/spg_image_gen.py`; die Vorlage bleibt unveraendert.
Uebernommen ist alles, was dort schmerzhaft gelernt wurde:

* Farbe steht je Akt, nicht global. Eine einzige Palette ueber die ganze
  Folge macht sie monoton — das war der erste Befund an EP01A.
* Kein Leuchten, das aus Haut kommt.
* Keine Farbbaender im Innenraum ohne Quelle im Bild. Bei EP01A trugen elf
  Motive diese Signatur, und genau daran war sofort zu sehen, dass die
  Bilder erzeugt sind.
* Abstrakte Motive brauchen eine harte Absage an Raum und Objekt, sonst
  setzt der Style Key eine Szene dagegen.
* Gesichter sind erlaubt und oft richtig. Verboten ist nur, was ein Gesicht
  kaputtmacht.

Die Welt ist eine andere als bei EP01A: amerikanische Universitaet,
neunzehnhundertneunundsiebzig bis zweitausendsieben. Kein Polarlicht, kein
Sibirien. Leuchtstoffroehren, Backstein, Efeu, beiger Kunststoff, gruener
Bildschirmphosphor, Endlospapier.

    python tools/pear_image_gen.py fehlend
    python tools/pear_image_gen.py alle [--jobs 3]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "06_PRODUCTION" / "EP03_PEAR" / "visuals" / "generated"

_spec = importlib.util.spec_from_file_location("spg_image_gen",
                                               ROOT / "tools" / "spg_image_gen.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


STYLE_KEY = """Visual style: American university documentary photography, 1979 to 2007,
shot on colour film with visible grain. Institutional interiors lit by their own fixtures:
fluorescent tubes with a faint green cast, incandescent desk lamps, daylight through
window blinds. Materials: painted cinder block, grey steel furniture, oak panelling, beige
moulded plastic, ribbon cable, tractor-feed paper, red LED seven-segment digits, green CRT
phosphor. Deep shadow is allowed; every frame keeps at least one light source that is
physically present in the picture.

All colour comes from those sources. Colour is never a wash, a filter or a tint laid over
the frame, and it never glows out of a person, a hand or a face. There are no bands or
patches of magenta, cyan or green lying across a desk, a sheet of paper or skin — that is
the single clearest sign of a generated picture.

The frame contains no writing of any kind. No labels, no signage, no numbers on paper, no
lettering anywhere, not even faintly in a corner. Where a display or a counter appears, it
shows only indistinct glowing segments.

Mood: quiet, institutional, slightly worn. A serious place where something unusual is
being done carefully. The viewer should feel they are looking at a room that existed."""

NEGATIVE = """greyscale, monochrome, washed-out colour, a uniform blue or teal cast over the
whole frame, lens flare, bokeh overlays, particle or dust overlays, glowing auras around
people, holograms, floating interfaces, modern flat-panel screens, smartphones, modern
clothing or eyewear, readable text of any kind, watermarks, logos, captions, stock-photo
styling, HDR look, sci-fi styling, plastic CGI surfaces, collage, grid, split screen"""

AKT_FARBE = {
    "S1": ("Basement room at night. Near darkness, one incandescent desk lamp making a "
           "small warm pool, and the red glow of LED digits. Painted concrete, grey steel. "
           "Everything outside the lamp falls to black."),
    "S2": ("American academic interiors of the late seventies. Oak, brass, worn leather, "
           "cream paint, autumn daylight through tall windows. Warm and settled. No "
           "fluorescent green, no cold cast."),
    "S3": ("Electronics workbench. Grey metal, solder, green circuit board, bright bench "
           "lamp throwing hard shadows, oscilloscope glow. Technical and close. "
           "Restrained colour."),
    "S4": ("The laboratory itself. Cool fluorescent overhead, clear acrylic, white "
           "polystyrene, pale institutional walls. Even, shadowless, slightly clinical. "
           "One warm desk lamp allowed as contrast."),
    "S5": ("Almost nothing. Deep black with a single thin amber or pale line. No room, no "
           "object, no person unless the prompt asks for one. Very high contrast."),
    "S6": ("Paper and daylight. Cream continuous-feed printout, pencil, grey overcast "
           "light through a window, brown desk. Sober, unglamorous, a little tired."),
    "S7": ("Two countries. American side: the same basement fluorescent. German side: a "
           "nineteen-nineties European institute — beech veneer, white walls, grey carpet, "
           "flat daylight. The contrast between the two rooms is the point."),
    "S8": ("An ending. Late afternoon light through dusty glass, cardboard boxes, bare "
           "shelves, warm brown and faded cream. Low contrast, quiet, elegiac."),
}
# Referenzen dieser Folge. Fuer Dunne liegt ein Foto unter CC BY 4.0 vor
# (JAEX-Nachruf 2022, 276x250 px) — zu klein zum Zeigen, aber gross genug als
# Vorlage. Die Lizenz erlaubt Bearbeitungen ausdruecklich; Namensnennung steht
# in den Bildnachweisen. Fuer Jahn existiert weltweit kein freies Foto, seine
# Motive entstehen aus der Textbeschreibung.
gen.REF_DIR = ROOT / "06_PRODUCTION" / "EP03_PEAR" / "visuals" / "references"
gen.AKT_FARBE = AKT_FARBE
gen.STYLE_KEY = STYLE_KEY
gen.NEGATIVE = NEGATIVE

# Fuer rein abstrakte Motive: der Style Key will einen Raum, der Prompt nicht.
KASKADE = """Construction, exactly as specified: a single tall apparatus roughly three metres
high and just under two metres wide, BUILT INTO the dark wood panelling of the wall so its
frame is flush with the woodwork. It is far taller than a standing adult — the top edge is
near the ceiling. Behind one continuous sheet of clear acrylic it has three zones stacked
vertically: at the top a funnel holding several thousand small white spheres; in the middle
a dense regular diamond grid of several hundred short dark pins; at the bottom a row of
nineteen narrow vertical collecting channels separated by thin dividers, in which the
spheres pile up to form a smooth mound, highest in the middle and falling away to both
sides. A narrow belt conveyor runs up one side to return the spheres to the funnel. It is
NOT a small cabinet, NOT a box on a bench and NOT a piece of tabletop equipment."""

KEIN_RAUM = ("One single continuous photograph filling the whole frame — not a grid, not a "
             "collage, no panels, no borders, no split screen. There is no room, no wall, "
             "no window, no lamp, no furniture, no person and no horizon anywhere in this "
             "picture. ")


def J(id_, prompt, akt="", ref=None, kaskade=False):
    if kaskade:
        prompt = prompt + chr(10) + chr(10) + KASKADE
    j = {"id": id_, "prompt": prompt, "akt": akt, "aspect": "16:9"}
    if ref:
        j["ref"] = ref
    return j


JOBS = [
    J("pe_v2_03_pilot_cockpit", akt="", prompt=(
      "This picture is NOT set in a laboratory, an office or any institutional interior. "
      "There are no laboratory benches, no fluorescent ceiling tubes, no desk lamp, no "
      "instrument racks and no cinder-block walls anywhere in the frame. Tight view inside "
      "the cockpit of a nineteen-seventies fighter aircraft, seen from just behind and to "
      "the right of the pilot's shoulder. He wears a helmet with the visor up and an oxygen "
      "mask hanging loose at one side; his gloved hand rests on the control column. The "
      "instrument panel fills the lower frame with round analogue dials and warning lights. "
      "Through the canopy: bright hazy daylight and a horizon. The light in the cockpit "
      "comes from that daylight and from the panel's own small lamps, nothing else. Shot on "
      "colour film, visible grain, documentary.")),
    J("pe_v2_02_mcdonnell_werk", akt="", prompt=(
      "This picture is NOT set in a laboratory, an office or any institutional interior. "
      "There are no laboratory benches, no fluorescent ceiling tubes, no desk lamp, no "
      "instrument racks and no cinder-block walls anywhere in the frame. A vast aircraft "
      "assembly hall in the nineteen-seventies: two military jets in bare metal on the line, "
      "gantries and scaffolding around them, overhead cranes in the roof structure, cable "
      "looms hanging from open panels. Daylight floods in through a wall of high industrial "
      "windows at the far end. A handful of workers are small against the scale. Wide, "
      "documentary, colour film grain.")),
    J("pe_v2_17_drei_labore", akt="", prompt=(
      "There are no laboratory benches, no fluorescent ceiling tubes, no desk lamp, no "
      "instrument racks and no cinder-block walls anywhere in the frame. One single "
      "continuous photograph — not a grid, not a collage, no panels, no borders. Three "
      "identical small grey instrument boxes stand in a row on a long white bench, each "
      "connected by an identical cable to an identical beige computer, the three sets spaced "
      "evenly and photographed straight on. Flat even daylight from a window out of frame, "
      "no shadows, clinical and deliberate. No text on any panel. The repetition is the "
      "subject.")),
    J("pe_v2_26_netz_knoten", akt="", prompt=(
      "One single continuous photograph filling the whole frame — not a grid, not a collage, "
      "no panels, no borders. Against pure black, several dozen small pale points of light "
      "are scattered unevenly, a few of them joined by very faint thin lines. There is no "
      "map, no coastline, no landmass, no globe, no grid and no text — only the points and "
      "the faint lines. Soft focus, heavy grain, very high contrast.")),
    J("pe_v2_27_generator_modern", akt="", prompt=(
      "This picture is NOT set in a laboratory, an office or any institutional interior. "
      "There are no laboratory benches, no fluorescent ceiling tubes, no desk lamp, no "
      "instrument racks and no cinder-block walls anywhere in the frame. Extreme macro of a "
      "small modern electronic module the size of a matchbox lying on a plain dark surface: "
      "a black circuit board with a USB connector at one end and two small indicator LEDs "
      "lit, a thin cable running out of frame. One hard light from the side, everything else "
      "black. No markings on the board. Very shallow depth of field, grain.")),
    J("pe_v2_19_telefon_nacht", akt="", prompt=(
      "A man in shirtsleeves sitting at a desk late at night with a telephone handset held "
      "to his ear, seen from across a dim room, a spread of continuous-feed printout in "
      "front of him. He is listening, not speaking; his free hand has stopped moving on the "
      "page. Only one desk lamp is lit and the window behind him is black. Warm tungsten "
      "against cold glass, 50 mm, heavy grain, documentary.")),
    J("pe_v2_06_geist_still", akt="", prompt=(
      "One single continuous photograph filling the whole frame — not a grid, not a collage, "
      "no panels, no borders. Against near-total blackness, the edge of a human head is "
      "barely suggested in profile by a thin rim of warm amber light along the brow and "
      "temple; everything else is black. No eyes, no features, no shoulders, no room, no "
      "equipment, no coloured light. Extremely soft focus, heavy grain, quiet.")),
    J("pe_v2_05_baseline_glatt", akt="", prompt=(
      "One single continuous photograph filling the whole frame — not a grid, not a collage, "
      "no panels, no borders. Against pure black, one thin pale line runs almost perfectly "
      "horizontally from edge to edge, trembling only very slightly. Nothing else is in the "
      "frame — no axes, no grid, no screen, no room, no numbers. Soft focus, heavy grain, "
      "very high contrast.")),
    # ================================================== S1  Der Raum, die Kiste
    J("pe_thumb_held", akt="S1", prompt=(
      "Vertical-thirds composition for a thumbnail. A man seen from behind and slightly "
      "above, sitting on a plain wooden chair at a grey steel desk in a dark basement room, "
      "shoulders relaxed, facing a small grey instrument box on the desk. The box's red "
      "seven-segment display is the brightest thing in the picture and throws a red glow "
      "onto the desk and onto his hands. One warm desk lamp at the far left. The whole left "
      "third of the frame is deep shadow and almost empty. Dark wood panelling behind, a "
      "red painted door just visible at the edge. The face is not visible. Cinematic wide "
      "angle, shot on colour film with visible grain and slight halation. No text, no "
      "signage, no lettering anywhere.")),
    J("pe_a01_keller_weit", akt="S1", prompt=(
      "Wide view of a small windowless basement room in a university engineering building: "
      "painted cinder-block walls, exposed pipes and ductwork along the ceiling, a grey "
      "steel desk against the far wall, one wooden chair. A single incandescent desk lamp "
      "is the only light. Bare concrete floor, a coil of cable in the corner. Empty, quiet, "
      "documentary.")),
    J("pe_a02_kiste_detail", akt="S1", prompt=(
      "Close three-quarter view of a plain grey-painted steel instrument enclosure about the "
      "size of a shoebox standing on a desk, with a small recessed window showing glowing "
      "red seven-segment digits, two toggle switches and a coaxial socket. The digits are "
      "bright but their shapes are indistinct. Warm desk lamp from the left, black behind. "
      "Film grain, shallow depth of field.")),
    J("pe_a03_ziffern_makro", akt="S1", prompt=(
      "Extreme macro of red seven-segment LED digits behind a smoked plastic window, so "
      "close that the individual light segments and the plastic texture are visible and no "
      "number can be read. Everything around them is black. Deep red glow, heavy grain.")),
    J("pe_a04_person_ruecken", akt="S1", prompt=(
      "Seen from directly behind: a man in a checked shirt sitting on a plain wooden chair "
      "at a grey steel desk, facing a small grey instrument box whose red display is the "
      "only colour in the room. His shoulders have dropped and his head is tilted very "
      "slightly down — the posture of someone who has been doing the same thing for several "
      "hours and has stopped expecting anything to happen. The room is not clinical: dark "
      "wood panelling on the walls, a red painted door, a worn red-orange couch against one "
      "wall with a heap of soft toys piled on it, a rag rug on the floor. It looks like "
      "somebody's basement den with laboratory equipment moved into it. One desk lamp off to "
      "the left, everything else dark. Shot on Kodachrome with a 50 mm lens at f2, available "
      "light only, visible grain. Documentary, patient, unremarkable.")),
    J("pe_a05_gesicht_konzentration", akt="S1", prompt=(
      "Close portrait of a man in his thirties in a plain shirt, sitting in near darkness, "
      "eyes closed. This is not strain — his brow is smooth, his jaw unclenched, his lips "
      "slightly parted. He looks like someone who has been told that trying harder makes it "
      "worse and is deliberately letting go. A warm desk lamp from below left models one "
      "side of the face; the other falls to black. A faint red glow from a display sits in "
      "the background and does not touch his skin. 85 mm lens wide open, colour negative "
      "film, visible grain, no retouching.")),
    J("pe_a06_hand_am_tisch", akt="S1", prompt=(
      "Macro of an adult hand lying still and open on a scratched grey steel desktop beside "
      "a coiled cable and a spiral notebook, lit by one warm desk lamp from the upper left. "
      "The rest of the desk falls into darkness. Nothing is being touched. Shallow depth, "
      "heavy grain.")),
    J("pe_a07_zaehler_laeuft", akt="S1", prompt=(
      "Macro of a mechanical counter unit with rotating numbered drums, mounted in a grey "
      "metal panel, photographed mid-rotation so the digits are blurred and unreadable. "
      "Brass and black enamel, worn edges. One warm lamp from the right, black surround."), ),
    J("pe_a08_papierstreifen", akt="S1", prompt=(
      "Close overhead view of a narrow strip of continuous printer paper spilling from a "
      "machine onto a desk, densely covered in rows of small printed marks that read as "
      "texture and not as numbers. One desk lamp, warm cream paper against dark wood. "
      "Shallow depth of field, film grain.")),
    J("pe_a09_kurve_millimeter", akt="S1", prompt=(
      "Close overhead macro of a hand-drawn line climbing gently across squared graph paper, "
      "drawn in pencil, the paper slightly creased and taped at one corner. One warm lamp "
      "from the left; the desk beyond falls into shadow. No numbers, no axis labels, no "
      "writing of any kind. Shallow depth, grain.")),
    J("pe_a10_ausdruckstapel", akt="S1", prompt=(
      "A tall stack of fan-folded continuous-feed computer printout on a desk in a dim "
      "office, the perforated edge strips still attached, photographed from a low "
      "three-quarter angle. Cream paper, faint printed texture, no legible characters. One "
      "warm desk lamp from the right, brown darkness behind. Film grain.")),
    J("pe_a11_kellerflur", akt="S1", prompt=(
      "A long basement corridor in a nineteen-sixties university building: painted "
      "cinder-block walls, overhead pipes and conduit, a row of fluorescent fixtures with a "
      "faint green cast receding into the distance, grey painted floor, a few closed doors. "
      "Nobody in the corridor. Wide, cold, institutional.")),
    J("pe_a12_tuer_keller", akt="S1", prompt=(
      "A plain painted metal door at the end of a basement corridor, slightly ajar, warm "
      "light spilling out through the gap into the cold fluorescent corridor. A steel frame, "
      "a worn kick plate, a small blank card holder beside the handle with no card in it. No "
      "text anywhere. High contrast, documentary.")),
    J("pe_a13_schreibtisch_dekan", akt="S2", prompt=(
      "A large oak desk in a panelled university office, seen at an angle in late afternoon "
      "light through a tall window: a green-shaded banker's lamp, a leather blotter, a rack "
      "of pipes, stacked folders, a rotary telephone. Nobody in the room. Warm, settled, "
      "unmistakably academic.")),

    # ============================================== S2  Der Mann, die Bedingung
    J("pe_b01_jahn_portraet", akt="S2", prompt=(
      "A tall, lean, almost gaunt American man with narrow shoulders and no fullness in the "
      "face; a long narrow head with a high strongly receding forehead; prominent cheekbones "
      "and a narrow angular jaw; deep vertical furrows running down from the cheekbones and "
      "hollow cheeks, so the face looks carved; thin straight hair, grey to silver, combed "
      "flat back against the skull with a very high hairline; large ears that stand "
      "noticeably away from the head; deep-set eyes under straight horizontal brows, heavy "
      "upper lids, a direct and friendly gaze; a long straight nose; a wide mouth with thin "
      "lips. He wears no spectacles at all. Clean shaven. He is forty-nine years old and it "
      "is 1979. A formal faculty portrait made in his own office: he sits half-turned "
      "towards the camera in a grey-brown Prince-of-Wales check tweed jacket, white "
      "button-down shirt and a patterned tie with a tie clip, one hand resting on the desk. "
      "Composed and unhurried, a listener rather than a performer, with a restrained "
      "slightly crooked smile that shows the upper teeth. Bookshelves behind him fall out of "
      "focus. Warm window light from the left, a green-shaded desk lamp lit at the edge of "
      "frame. Colour negative film of the period, 105 mm lens, slightly faded dye, visible "
      "grain.")),
    J("pe_b02_jahn_schreibtisch", akt="S2", prompt=(
      "A tall, lean, almost gaunt American man with narrow shoulders and no fullness in the "
      "face; a long narrow head with a high strongly receding forehead; prominent cheekbones "
      "and a narrow angular jaw; deep vertical furrows running down from the cheekbones and "
      "hollow cheeks, so the face looks carved; thin straight hair, grey to silver, combed "
      "flat back against the skull with a very high hairline; large ears that stand "
      "noticeably away from the head; deep-set eyes under straight horizontal brows, heavy "
      "upper lids, a direct and friendly gaze; a long straight nose; a wide mouth with thin "
      "lips. He wears no spectacles at all. Clean shaven. He is in his early fifties. Seen "
      "from across his panelled office, half-turned away from the camera, writing on a legal "
      "pad at a large oak desk covered in journals and folders. He is absorbed and has not "
      "noticed the photographer. Late afternoon light through venetian blinds lays warm "
      "stripes across the desk and across his sleeve; a green-shaded banker's lamp is lit. "
      "Unposed, a colleague's snapshot rather than a portrait. 35 mm, available light, "
      "colour film grain.")),
    J("pe_b03_vakuumkammer", akt="S2", prompt=(
      "A large cylindrical steel vacuum chamber in a university propulsion laboratory of the "
      "nineteen-seventies, port windows with heavy bolted flanges, thick cables and hoses "
      "running to a control rack, a wheeled staircase beside it. Cool overhead light, one "
      "warm lamp at a workbench in the foreground. Industrial, serious, nobody in frame.")),
    J("pe_b04_triebwerk_pruefstand", akt="S2", prompt=(
      "Close view of an experimental electric thruster on a test stand inside a laboratory: "
      "a small ring of copper coils and a machined electrode assembly on an aluminium mount, "
      "surrounded by instrumentation cables. Hard workshop lighting, metal and copper "
      "tones, no plasma discharge visible. Technical documentary photograph.")),
    J("pe_b05_buchruecken", akt="S2", prompt=(
      "Macro of a row of hardback academic books standing on a shelf, seen at a slight "
      "angle, cloth spines in dark blue and oxblood with blank gold-blocked panels where "
      "titles would be. No lettering at all. Warm lamplight from the left, dust in the air. "
      "Shallow depth of field.")),
    J("pe_b06_fakultaetssitzung", akt="S2", prompt=(
      "A faculty meeting room in a nineteen-seventies American university: a long polished "
      "table, a dozen empty wooden chairs pushed in at angles, water glasses and folders "
      "left behind, tall windows with half-drawn blinds. Late daylight, warm wood, nobody in "
      "the room. Wide and still.")),
    J("pe_b07_studentenarbeit", akt="S2", prompt=(
      "Overhead close view of a slim typewritten student report lying open on a desk beside "
      "a slide rule and a mug, the pages showing dense typed text as texture with no legible "
      "words, one page carrying a small hand-drawn circuit sketch in pencil. Warm desk lamp, "
      "brown desk falling into shadow. Film grain.")),
    J("pe_b08_notizbuch_offen", akt="S2", prompt=(
      "Overhead macro of a hard-backed laboratory notebook open on a desk, both pages filled "
      "with handwriting and small sketches rendered as marks with no legible words, a "
      "fountain pen lying in the gutter. One warm lamp from the right, dark wood around. "
      "Shallow depth of field, grain.")),
    J("pe_b09_hoersaal_leer", akt="S2", prompt=(
      "An empty tiered lecture hall in an older American engineering building: fixed wooden "
      "benches, sliding blackboards wiped clean, a lectern, tall windows down one side. "
      "Flat afternoon daylight, dust in the air, nobody present. Wide, quiet.")),
    J("pe_b10_dunne_portraet", akt="S2", ref="dunne_1982", prompt=(
      "An American woman with long dark brown slightly wavy hair worn loose with a centre "
      "parting, strong dark brows, an open warm face, no spectacles, almost no make-up and "
      "no conspicuous jewellery. She is in her late thirties and it is about 1982. "
      "Documentary portrait at her desk in an institutional office: a white "
      "broderie-anglaise blouse, folders and a coffee cup in front of her, one hand still "
      "resting on a page she was reading. She looks straight at the camera with a direct, "
      "warm, faintly challenging expression — someone who has been asked the same sceptical "
      "question many times and has stopped being annoyed by it. Daylight from a window at "
      "the right, fluorescent overhead. Colour negative film of the period, visible grain.")),
    J("pe_b11_dunne_am_ordner", akt="S2", ref="dunne_1982", prompt=(
      "An American woman with long dark brown slightly wavy hair worn loose with a centre "
      "parting, strong dark brows, an open warm face, no spectacles, almost no make-up and "
      "no conspicuous jewellery. She is in her forties. She stands at an open grey steel "
      "filing cabinet, pulling a thick folder from a drawer, half-turned away from the "
      "camera, her other hand steadying two more folders against her hip. Everyday "
      "competence, mid-motion, nothing posed. Fluorescent overhead light with a faint green "
      "cast, one warm desk lamp behind. 35 mm, available light, grain.")),
    J("pe_b12_vereinbarung_blatt", akt="S2", prompt=(
      "Overhead macro of a single typewritten sheet of headed paper lying on a desk, held "
      "flat by a hand at one corner, the typed text present as texture but no word legible "
      "and the letterhead blank. A fountain pen beside it. Warm lamp from the left, dark "
      "wood, deep shadow at the edges. Shallow depth, grain.")),
    J("pe_b13_efeu_backstein", akt="S2", prompt=(
      "A brick facade of an older American university building covered in ivy, tall windows "
      "with stone surrounds, autumn light raking across it from the left, a few fallen "
      "leaves on the path below. No people, no signage. Warm brick, gold leaves, deep blue "
      "shadow. Documentary.")),

    J("pe_b14_jahn_entscheidung", akt="S2", prompt=(
      "A tall, lean, almost gaunt American man with narrow shoulders and no fullness in the "
      "face; a long narrow head with a high strongly receding forehead; prominent cheekbones "
      "and a narrow angular jaw; deep vertical furrows running down from the cheekbones and "
      "hollow cheeks, so the face looks carved; thin straight hair, grey to silver, combed "
      "flat back against the skull with a very high hairline; large ears that stand "
      "noticeably away from the head; deep-set eyes under straight horizontal brows, heavy "
      "upper lids, a direct and friendly gaze; a long straight nose; a wide mouth with thin "
      "lips. He wears no spectacles at all. Clean shaven. He is forty-nine. He stands alone "
      "at the window of his office at dusk with his back half to the camera, hands in his "
      "trouser pockets, looking out over the campus. The tweed jacket hangs over the chair "
      "behind him, his shirtsleeves are rolled. On the desk behind him lies a thin "
      "typewritten student report, open. This is the evening he decides to do something that "
      "could cost him his standing. Warm low sun on one side of his face, the room behind "
      "him unlit. 50 mm, backlit, heavy grain, quiet.")),
    J("pe_b15_jahn_alt", akt="S8", prompt=(
      "A tall, lean, almost gaunt American man with narrow shoulders and no fullness in the "
      "face; a long narrow head with a high strongly receding forehead; prominent cheekbones "
      "and a narrow angular jaw; deep vertical furrows running down from the cheekbones and "
      "hollow cheeks, so the face looks carved; thin straight hair, grey to silver, combed "
      "flat back against the skull with a very high hairline; large ears that stand "
      "noticeably away from the head; deep-set eyes under straight horizontal brows, heavy "
      "upper lids, a direct and friendly gaze; a long straight nose; a wide mouth with thin "
      "lips. He wears no spectacles at all. Clean shaven. He is seventy-six and it is 2007. "
      "He sits on a plain chair in a half-emptied laboratory, cardboard boxes behind him, "
      "elbows on his knees and hands loosely clasped, looking down and slightly away. The "
      "hair is fully silver now, the face more hollow, but the posture is unbowed. He is "
      "neither bitter nor triumphant — he has simply finished. Late afternoon light through "
      "a dusty high window. 50 mm, available light, colour negative, visible grain.")),
    J("pe_b16_dunne_kugelwand", akt="S4", ref="kaskade_geometrie", kaskade=True, prompt=(
      "An American woman in her forties with long dark brown slightly wavy hair worn loose "
      "with a centre parting, strong dark brows, an open warm face and no spectacles, "
      "wearing a white blouse. She stands at the foot of the apparatus, small against it, "
      "one hand resting on its frame, head tilted back to watch the spheres falling through "
      "the pin field high above her. Her expression is plain attention — she has watched "
      "this ten thousand times and still watches. One ceiling fixture and a desk lamp. 35 "
      "mm, documentary, film grain.")),
    # ================================================= S3  Die Maschine
    J("pe_c01_werkbank", akt="S3", prompt=(
      "An electronics workbench in a university laboratory: a soldering iron in its stand, a "
      "green circuit board held in a small vice, spools of solder, cutters, a coffee tin of "
      "resistors, an oscilloscope at the back with a faint trace on its screen. One bright "
      "articulated bench lamp throws hard shadows. Nobody in frame. Technical, close.")),
    J("pe_c02_platine_makro", akt="S3", prompt=(
      "Extreme macro of a green printed circuit board, hand-soldered, with through-hole "
      "resistors, a small metal-can transistor and a row of integrated circuits in sockets, "
      "solder joints bright under a bench lamp. The board markings are visible as shapes but "
      "no character is legible. Shallow depth of field, hard light, film grain.")),
    J("pe_c03_rauschdiode", akt="S3", prompt=(
      "Extreme macro of a small glass-bodied semiconductor diode with wire leads, held "
      "upright in a pair of tweezers against a black background, lit hard from one side so "
      "the glass body glows and the internal structure is visible as a dark silhouette. "
      "Nothing else in frame. Very shallow depth of field, heavy grain.")),
    J("pe_c04_oszilloskop_rauschen", akt="S3", prompt=(
      "Close view of the round screen of an analogue oscilloscope showing a dense band of "
      "random noise as a bright green trace against the graticule, photographed straight on "
      "in a darkened room. The instrument's beige housing and worn knobs are just visible "
      "around the screen. No text on the panel. Green phosphor glow, grain.")),
    J("pe_c05_schaltung_zeichnung", akt="S3", prompt=(
      "Overhead view of a hand-drawn circuit diagram on a large sheet of tracing paper "
      "pinned to a drawing board, drawn in fine ink with a straight edge, showing boxes and "
      "connecting lines. The shapes are clear but carry no labels or numbers. One "
      "drafting lamp from the upper left, the board's green surface visible at the edges. "
      "Slight angle, film grain.")),
    J("pe_c06_kiste_offen", akt="S3", prompt=(
      "A grey steel instrument enclosure standing open on a workbench with its lid removed, "
      "showing a hand-wired interior: a circuit board on standoffs, a small transformer, a "
      "bundle of coloured ribbon cable, a socket on the rear panel. Bench lamp from above, "
      "hard shadows inside the box. Technical documentary, nobody in frame.")),
    J("pe_c07_kabel_bundel", akt="S3", prompt=(
      "Macro of a thick bundle of coloured ribbon and hookup wire laced together with waxed "
      "cord, running along the back of a grey equipment rack. Warm lamp raking from the "
      "left, dust visible. Shallow depth of field, heavy grain.")),
    J("pe_c08_geraet_reihe", akt="S3", prompt=(
      "A row of identical grey instrument boxes standing side by side on a shelf in a "
      "laboratory, each with a small dark display window and two switches, cables coiled "
      "beside them. Even fluorescent light from above, one warm lamp at the left end. "
      "Orderly, institutional, no text on any panel.")),
    J("pe_c09_patent_mappe", akt="S3", prompt=(
      "An open cardboard document folder on a desk with a thick set of typewritten pages and "
      "technical drawings inside, photographed from above in warm lamplight. Aged cream "
      "paper, a rubber stamp impression, paperclip rust marks. The text is present as "
      "texture but nothing is legible. Dark wood at the edges.")),

    # ================================================== S4  Der Ablauf
    J("pe_d01_labor_weit", akt="S4", prompt=(
      "Wide view of the laboratory room in a university basement. The room is not clinical: "
      "dark wood panelling on the walls, a red painted door, a worn red-orange couch against "
      "one wall with a heap of soft toys piled on it, a rag rug on the floor. It looks like "
      "somebody's basement den with laboratory equipment moved into it. Two grey steel desks "
      "with instruments stand among it, a wheeled chair, shelves of boxed equipment, and a "
      "tall clear-acrylic apparatus built into the panelling at the right. One ceiling "
      "fixture and two desk lamps. Nobody in frame. The contrast between the domestic "
      "furniture and the equipment is the point. 28 mm, available light, grain.")),
    J("pe_d02_sitzung_seitlich", akt="S4", prompt=(
      "A woman in her fifties in a cardigan sitting upright on a plain chair at a desk, "
      "photographed from the side at a distance. Her hands rest loosely in her lap, her eyes "
      "are closed, and there is the faintest amusement at the corner of her mouth — she "
      "finds the situation slightly absurd and is doing it properly anyway. A small grey "
      "instrument box in front of her, a clipboard beside it. The room is not clinical: dark "
      "wood panelling on the walls, a red painted door, a worn red-orange couch against one "
      "wall with a heap of soft toys piled on it, a rag rug on the floor. It looks like "
      "somebody's basement den with laboratory equipment moved into it. One warm lamp and a "
      "little daylight. Unposed, caught mid-session, 35 mm colour film, grain.")),
    J("pe_d03_zettel_absicht", akt="S4", prompt=(
      "Overhead macro of a small pre-printed form lying on a desk with three empty tick "
      "boxes in a column and a pencil resting beside it. The boxes are clear; there is no "
      "printed text anywhere on the form. One warm lamp from the left, grey desktop, "
      "shallow depth of field.")),
    J("pe_d04_uhr_wand", akt="S4", prompt=(
      "A plain institutional wall clock with a white face and black hands mounted on a pale "
      "painted cinder-block wall, photographed slightly from below. The numerals are absent "
      "from the dial. Flat fluorescent light, a conduit running past the clock. Sparse and "
      "cold.")),
    J("pe_d05_kugelwand_weit", akt="S4", ref="kaskade_geometrie", kaskade=True, prompt=(
      "Wide frontal view of the apparatus standing against the panelled laboratory wall, "
      "photographed from a few metres back so its full height is in frame from floor to top. "
      "A plain wooden chair stands in front of it, giving the scale — the apparatus is "
      "roughly twice the height of the chair-and-person. Even overhead light, the white "
      "spheres bright behind the acrylic. Nobody in frame. Documentary, 28 mm, film grain.")),
    J("pe_d06_kugeln_fallen", akt="S4", ref="kaskade_geometrie", kaskade=True, prompt=(
      "Close view through the clear acrylic of the middle zone only: hundreds of small white "
      "spheres cascading downward through the dense diamond grid of dark pins, many blurred "
      "by motion, bouncing on complex paths. The frame is filled by the pin field; the "
      "funnel above and the channels below are cut off. Cool overhead light catching the "
      "acrylic and the spheres. High shutter speed, dense, chaotic, mechanical.")),
    J("pe_d07_faecher_unten", akt="S4", ref="kaskade_geometrie", kaskade=True, prompt=(
      "Close frontal view of the bottom zone only: nineteen narrow vertical collecting "
      "channels behind clear acrylic, separated by thin dividers, partly filled with small "
      "white spheres so their levels form one smooth mound, highest in the middle and "
      "falling away evenly to both sides. The frame is filled by the channels; the pin field "
      "above is cut off at the top edge. Even light. No numbers, no scale markings.")),
    J("pe_d08_pendel_quarz", akt="S4", prompt=(
      "A slender pendulum hanging in a laboratory: a polished transparent sphere the size of "
      "a plum at the end of a thin clear rod, suspended from a machined bracket on a stand. "
      "The sphere catches one bright lamp and throws a small caustic on the bench below. "
      "Dark background, shallow depth of field, technical.")),
    J("pe_d09_springbrunnen", akt="S4", prompt=(
      "A small indoor water fountain apparatus in a laboratory, a column of water rising and "
      "breaking into droplets above a shallow basin, lit hard from one side so the droplets "
      "are frozen against a dark background. An aluminium frame and a pump hose visible at "
      "the edge. No coloured light. Macro, high shutter speed, grain.")),
    J("pe_d10_kopfhoerer_tisch", akt="S4", prompt=(
      "Macro of a pair of nineteen-eighties over-ear headphones lying on a grey steel desk "
      "beside a small cassette player, the coiled cable trailing off the edge. Worn foam "
      "pads, beige plastic. One warm desk lamp from the right, dark surround, shallow "
      "depth.")),
    J("pe_d11_protokollbuch", akt="S4", prompt=(
      "Overhead view of a large ruled laboratory logbook open on a desk, its columns filled "
      "with handwritten entries rendered as marks with no legible words, a ruler and a "
      "pencil lying across it. Fluorescent light from above with one warm lamp at the "
      "corner. Cream paper, grey desk.")),
    J("pe_d12_stuhl_leer_labor", akt="S4", prompt=(
      "A single empty wooden chair standing on a rag rug facing a desk with a grey "
      "instrument box on it, photographed straight on from a distance. The room is not "
      "clinical: dark wood panelling on the walls, a red painted door, a worn red-orange "
      "couch against one wall with a heap of soft toys piled on it, a rag rug on the floor. "
      "It looks like somebody's basement den with laboratory equipment moved into it. One "
      "lamp lit, the room otherwise unoccupied. Still, plain, slightly melancholy. 35 mm, "
      "grain.")),

    # =================================================== S5  Die Zahl
    J("pe_e01_linie_steigt", akt="S5", prompt=(
      KEIN_RAUM +
      "The photograph shows a single thin pale amber line against pure black, entering at "
      "the lower left and climbing very slightly and unevenly to the right, jittering as it "
      "goes but never returning to its starting height. Nothing else is in the frame. Soft "
      "focus, heavy grain, very high contrast.")),
    J("pe_e02_muenzen_flug", akt="S5", prompt=(
      "Dozens of small metal coins frozen in mid-air against a completely black background, "
      "tumbling at different angles, lit hard from one side so their edges flash and their "
      "faces stay dark and unreadable. No hand, no table, no room. High shutter speed, "
      "shallow depth of field, heavy grain.")),
    J("pe_e03_null_eins_strom", akt="S5", prompt=(
      KEIN_RAUM +
      "The photograph shows a dense stream of tiny pale marks against pure black, arranged "
      "in long horizontal rows that recede and blur towards the edges of the frame, reading "
      "as pure texture. No character is identifiable as a letter or a number. Soft focus at "
      "the margins, heavy grain.")),
    J("pe_e04_waage_zunge", akt="S5", prompt=(
      "Extreme macro of the pointer of an old analytical balance resting almost exactly on "
      "its centre mark, the scale behind it out of focus and carrying no numbers. Polished "
      "brass and white enamel, one hard lamp from the left, black surround. Very shallow "
      "depth of field.")),
    J("pe_e05_sandkorn", akt="S5", prompt=(
      "Extreme macro of a single grain of sand lying alone on a vast smooth dark surface, "
      "lit from one side so it casts a long shadow. The surface recedes out of focus in "
      "every direction. Nothing else in frame. Shallow depth, heavy grain."), ),

    # ================================================== S6  Die Kritik
    J("pe_f01_endlospapier_boden", akt="S6", prompt=(
      "A long ribbon of fan-folded continuous printer paper spilling from a desk onto the "
      "floor of an office and running towards the camera, its perforated edges catching grey "
      "daylight from a window. The printed rows read as texture with no legible characters. "
      "Overcast light, brown carpet, film grain.")),
    J("pe_f02_bleistift_korrektur", akt="S6", prompt=(
      "Overhead macro of a hand holding a pencil above a printed table on continuous-feed "
      "paper, one row circled in pencil, the rest of the page reading as texture with no "
      "legible characters. Grey daylight from a window at the left, wooden desk. Shallow "
      "depth of field.")),
    J("pe_f03_zwei_stapel", akt="S6", prompt=(
      "Two stacks of paper of very different heights standing side by side on a desk, "
      "photographed from a low angle against a plain wall so the difference in height is "
      "obvious. Cream paper, grey overcast daylight from the right. No writing visible on "
      "any page. Plain, sober.")),
    J("pe_f04_fenster_regen", akt="S6", prompt=(
      "A tall office window streaked with rain, seen from inside, the campus outside "
      "reduced to soft grey and green shapes. A radiator below the sill, a mug on the ledge. "
      "Flat overcast light, no lamp lit. Muted, tired.")),
    J("pe_f05_ordnerwand", akt="S6", prompt=(
      "A wall of grey and buff box files on metal shelving in an institutional storeroom, "
      "receding into shadow, lit by one bare overhead fluorescent tube. Worn spines with "
      "blank label holders, no lettering anywhere. Documentary, dusty, cold light.")),
    J("pe_f06_person_am_stapel", akt="S6", prompt=(
      "A man in his forties in shirtsleeves with his tie loosened, standing at a desk with "
      "both hands flat on a thick stack of continuous-feed printout, head down, reading a "
      "page near the top. His weight is on his arms. This is the hundredth hour of checking "
      "the same kind of page, looking for the mistake that would explain everything. Grey "
      "overcast daylight from a window at the left, fluorescent overhead. His face is partly "
      "turned away. 35 mm, available light, grain.")),
    J("pe_f07_einzelner_stuhl_reihe", akt="S6", prompt=(
      "A long row of identical empty chairs against a pale institutional wall, with one "
      "chair pulled out of line and turned slightly towards the camera. Flat fluorescent "
      "light, grey linoleum floor. Plain, slightly unsettling, nobody present.")),
    J("pe_f08_taschenrechner", akt="S6", prompt=(
      "Macro of an early-eighties desktop calculator with a small glowing red display and "
      "large beige keys, standing on a printout-covered desk, a hand just leaving the frame. "
      "The display shows indistinct glowing segments. One warm lamp from the right, shallow "
      "depth of field.")),

    # ================================================== S7  Die Probe
    J("pe_g01_institut_freiburg", akt="S7", prompt=(
      "Exterior of a modest nineteen-nineties German research institute building: three "
      "storeys, white render, grey window frames, a low hedge and a gravel path, bicycles "
      "leaning against a rack. Flat overcast daylight, bare trees. No signage, no lettering. "
      "Documentary, plain.")),
    J("pe_g02_labor_deutsch", akt="S7", prompt=(
      "A small European research laboratory of the nineteen-nineties: beech-veneer desks, "
      "white walls, grey carpet tiles, a beige computer tower and a CRT monitor showing a "
      "blank green screen, a grey instrument box beside it. Flat daylight through a large "
      "window with vertical blinds. Nobody in frame. Clean, ordinary, institutional.")),
    J("pe_g03_drei_geraete", akt="S7", prompt=(
      "Three identical small grey instrument boxes standing in a row on a white bench, each "
      "with a dark display window, connected by identical cables to three identical beige "
      "computers. Even daylight, no shadows, clinical and deliberate. No text on any panel.")),
    J("pe_g04_protokoll_unterschrift", akt="S7", prompt=(
      "Overhead macro of a hand signing at the foot of a typewritten agreement on a desk, "
      "the fountain pen mid-stroke, the typed text above reading as texture with nothing "
      "legible and the signature itself an indistinct flourish. Warm lamp from the left, "
      "dark wood, shallow depth of field.")),
    J("pe_g05_versand_kiste", akt="S7", prompt=(
      "A wooden shipping crate standing open on a laboratory floor, packing straw and foam "
      "inside, a grey instrument box half-lifted out of it by two hands. Fluorescent "
      "overhead light, concrete floor, a clipboard lying on the crate lid. No labels, no "
      "writing.")),
    J("pe_g06_telefonat_nacht", akt="S7", prompt=(
      "A man sitting alone at a desk late at night, a telephone handset held to his ear with "
      "one shoulder, both hands flat on a printout spread in front of him, seen from across "
      "a dim office. He is not speaking — he is listening, and his free hand has stopped "
      "moving on the page. Only the desk lamp is lit; the window behind him is black. This "
      "is the call in which the result is read out. 50 mm, warm tungsten against cold glass, "
      "heavy grain.")),
    J("pe_g08_flaches_ergebnis", akt="S7", prompt=(
      KEIN_RAUM +
      "The photograph shows a single thin pale line against pure black running almost "
      "horizontally across the whole frame, trembling very slightly up and down but never "
      "departing from its level. Nothing else in the frame. Soft focus, heavy grain.")),
    J("pe_g09_veroeffentlichung", akt="S7", prompt=(
      "Overhead view of an academic journal lying open on a desk, two columns of small print "
      "reading as texture with no legible words, a simple line graph occupying the upper "
      "half of one page. Grey daylight from the left, a pencil lying across the gutter. "
      "Plain, sober, film grain.")),
    J("pe_g10_labor_weiterarbeit", akt="S7", prompt=(
      "The American basement laboratory again, seen from the doorway, lit and in use: papers "
      "spread on both desks, a chair pushed back, the instrument running with its red "
      "display lit, a coat over the back of a chair. Nobody in frame. Fluorescent overhead "
      "with one warm desk lamp. Documentary.")),

    # ================================================= S8  Was bleibt
    J("pe_h01_kisten_packen", akt="S8", prompt=(
      "Cardboard boxes stacked and part-filled on the floor of a laboratory being cleared "
      "out, equipment wrapped in bubble film, a roll of tape on a chair, shelves half empty "
      "behind. Late afternoon light through a high dusty window. Nobody in frame. Quiet, "
      "elegiac.")),
    J("pe_h02_leerer_raum", akt="S8", prompt=(
      "The basement room completely empty: bare painted walls with pale rectangles where "
      "shelving stood, cable stubs hanging from a conduit, a swept concrete floor, one "
      "fluorescent tube lit. Wide, flat, final. Nobody in frame.")),
    J("pe_h03_archivkarton", akt="S8", prompt=(
      "A row of grey archive boxes on a metal shelf in a storeroom, their lids tied with "
      "cotton tape, blank label holders on the fronts. One overhead fluorescent tube, dust "
      "on the upper surfaces. No lettering anywhere. Documentary, cool light.")),
    J("pe_h04_datentraeger", akt="S8", prompt=(
      "Macro of a stack of nine-track magnetic tape reels in their plastic cases lying on a "
      "shelf, the tape visible through the hub windows, blank label areas on the sides. Warm "
      "lamp from the left, grey shelf, dust. Shallow depth of field."), ),
    J("pe_h05_fenster_abend", akt="S8", prompt=(
      "A tall university window seen from inside an empty room at dusk, the campus outside "
      "reduced to silhouettes and a few lit windows, the glass dusty and streaked. No lamp "
      "lit inside. Warm sky against a dark interior. Quiet, final.")),
    J("pe_h06_grabstein_schlicht", akt="S8", prompt=(
      "A plain granite headstone in an American cemetery in autumn, seen from the front at "
      "a slight angle, fallen leaves at its base, bare branches above. The inscribed face is "
      "turned just far enough that no lettering can be read. Soft overcast light, muted "
      "browns and greys. Respectful, still.")),
    J("pe_h07_schreibtisch_leer", akt="S8", prompt=(
      "An empty oak desk in a panelled office at the end of the day: the blotter removed, a "
      "clean rectangle in the dust where a lamp stood, one forgotten paperclip. Late warm "
      "light through a tall window. Nobody in the room. Melancholy, still.")),
    J("pe_h08_netz_weltkarte", akt="S8", prompt=(
      KEIN_RAUM +
      "The photograph shows several dozen small pale points of light scattered unevenly "
      "across pure black, a few of them joined by very faint thin lines. There is no map, no "
      "coastline, no landmass, no grid and no text — only the points and the faint lines. "
      "Soft focus, heavy grain, very high contrast.")),
    J("pe_h09_serverraum_klein", akt="S8", prompt=(
      "A small modern equipment room with a single half-populated server rack, a tangle of "
      "network cables, and the steady glow of indicator lights along the front panels, "
      "photographed in a darkened room. Cool light from the rack itself, concrete floor. "
      "Nobody in frame. No text, no logos.")),
    J("pe_h10_generator_heute", akt="S8", prompt=(
      "Macro of a small modern electronic module the size of a matchbox on a desk, a plain "
      "black circuit board with a USB connector and two indicator LEDs lit, a thin cable "
      "running off frame. Hard lamp from one side, black surround, very shallow depth of "
      "field. No markings on the board.")),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("befehl", choices=("alle", "fehlend", "zaehlen"))
    ap.add_argument("--modell", default="pro", choices=("pro", "flash"))
    ap.add_argument("--aufloesung", default="2k", choices=("1k", "2k", "4k"))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--nur", default="")
    ap.add_argument("--neu", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    gen.OUT = OUT

    if args.befehl == "zaehlen":
        from collections import Counter
        c = Counter(j["akt"] for j in JOBS)
        for a in sorted(c):
            print(f"  {a}  {c[a]:2d} Motive")
        print(f"  gesamt {len(JOBS)}")
        return

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

    print(f"{len(offen)} Motive, Modell {args.modell}, {args.aufloesung}, "
          f"{args.jobs} parallel\n")
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for name, status in pool.map(
                lambda j: gen.bauen(j, args.modell, args.aufloesung), offen):
            print(f"  {name:28s} {status}", flush=True)

    da = sum(1 for j in JOBS if (OUT / f"{j['id']}.png").exists())
    print(f"\n{da}/{len(JOBS)} vorhanden -> {OUT}")


if __name__ == "__main__":
    main()
