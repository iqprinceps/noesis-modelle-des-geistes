#!/usr/bin/env python3
"""Generate the EP07 visual-diversity replacement batch with Vertex NanoBanana Pro."""

from __future__ import annotations

import argparse
import base64
import pathlib

from ep07_vertex_generate import ASSETS, LOCATION, MODEL, post_json, project_id


ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "tmp" / "imagegen" / "ep07_diversity_raw"

LOCK = """Create a premium horizontal 16:9 German documentary frame at 2K. The visual language is
deep, mystical and intellectually complex, but epistemically cautious: museum-grade source handling,
layered material depth, restrained chiaroscuro, graphite, aged paper, quiet indigo, amber practical
light, translucent thresholds and subtle film grain. Keep lifted midtones, visible shadow detail and
clear focal hierarchy on an ordinary phone screen. This replacement must contain no bed, no bedroom,
no sleeping or reclining person, and no generic horror ghost. No glowing eyes, fantasy magic, occult
proof, fake genealogy, demon caricature, CGI sheen, cyberpunk neon, captions, labels, logos, watermark,
invented handwriting or readable generated text. Human anatomy must be natural. Blank zones are for
later editor typography. Any supplied historical source remains a separate photographed source object;
do not redraw, rewrite, animate or merge its contents into invented history."""

JOBS = [
    {
        "name": "IMG003_PRIVATE_NIGHT_TO_COURT.png",
        "refs": ["STYLE_ARCHIVE_EP07.png", "@COMAN", "EP07_Witchcraft_at_Salem_Village_1876.jpg"],
        "prompt": """Build an archival constellation about a private perception entering collective judgment.
Place a tall authentic testimony object in a museum-dark vertical plane, while a separate nineteenth-century
Salem courtroom engraving appears as a distant secondary source fragment. Between them use an empty witness
rail, quill shadow, folded docket shapes and many soft human shadows converging toward the evidence. The visual
argument is transformation through institutions and group interpretation, not a supernatural event and not
proof that one testimony caused a conviction. No domestic reconstruction.""",
    },
    {
        "name": "IMG007_MARA_INCUBUS_KANASHIBARI_BASE.png",
        "refs": ["STYLE_CONCEPTUAL_EP07.png", "EP07_Jinn_from_Ali_manuscript.png", "EP07_Kunisada_The_Ghost.jpg", "EP07_Yoshitoshi_Shoki.jpg"],
        "prompt": """Create a sophisticated cultural-form-wandering triptych using three authentic historical
source images as separate, clearly bounded paper objects. Connect them only through threshold motifs: an arched
door shadow, a patterned manuscript border and a shoji-like lattice rhythm that repeat without becoming the
same symbol. Suggest that cultures give different forms to fear, pressure and sensed presence; do not equate
the jinn manuscript, Japanese ghost imagery or guardian imagery with one universal being. Preserve generous
blank negative space for later labels. No direct lineage arrows and no copied figure outside its source panel.""",
    },
    {
        "name": "IMG010_RITUAL_RESPONSE_TABLE.png",
        "refs": ["STYLE_CINEMATIC_EP07.png"],
        "prompt": """Create an overhead museum-documentary still life of ordinary protective and religious
responses arranged around an intentionally empty center on a worn historical table: one closed prayer book,
simple wooden cross, unlit beeswax candle beside a small natural flame, folded linen, plain water bowl, iron key
and household cord. A window-lattice shadow crosses the surface like a threshold. It must feel used, practical
and human, never an occult altar. Keep every page closed or unreadable and the composition materially rich.""",
    },
    {
        "name": "IMG012_EXPERIENCE_BEFORE_STORY.png",
        "refs": ["STYLE_CONCEPTUAL_EP07.png"],
        "prompt": """Create an abstract tactile documentary composition in which immediate bodily experience
exists before explanation: a life-size embossed eye, ribcage pressure contour and motionless hand impression
emerge from layered graphite, linen and translucent vellum. Far behind a clear visual boundary sits a sealed
stack of generic books that has not yet touched the body layer. The sensed presence is only a change in negative
space, not a figure. Make the materials physically believable and luminous enough to read.""",
    },
    {
        "name": "IMG013_BODY_TO_STORY_FLOW_BASE.png",
        "refs": ["STYLE_CONCEPTUAL_EP07.png"],
        "prompt": """Create a left-to-right sculptural documentary sequence with no text: first a pressure
imprint across folded linen and an awake eye fragment; second a graphite handprint beside a blank recording reel;
third a small oral-history circle seen as warm silhouettes around a table. Bind the stages with one continuous
paper fiber and changing light, not arrows or mystical energy. The result should feel like a museum installation
about sensation becoming testimony and shared narrative.""",
    },
    {
        "name": "IMG014_TWO_PEOPLE_SAME_BODY_DIFFERENT_MODEL.png",
        "refs": ["STYLE_CONCEPTUAL_EP07.png"],
        "prompt": """Create a balanced conceptual diptych of two anonymous adults shown upright in matching
three-quarter profile silhouettes, each holding the same tense shoulder-and-hand posture. Their internal body
geometry is represented by the same subtle embossed pressure contour. Around one silhouette are neutral sleep-
laboratory materials; around the other are restrained household, oral-history and religious materials. Neither
side is presented as superior or as proof. Use translucent vellum layers and realistic material shadows.""",
    },
    {
        "name": "IMG015_EXPERIENCE_CULTURE_DECISION_BASE.png",
        "refs": ["STYLE_CONCEPTUAL_EP07.png"],
        "prompt": """Create a deep, elegant decision-card base without text or a literal split-screen. In the
foreground, macro fragments of an awake eye, skin texture, fingertips and a pressure crease represent immediate
experience. Behind and around them, translucent family-photo edges, blank book spines, woven ornament and oral-
history silhouettes represent cultural interpretation. Let the two material systems interpenetrate without one
erasing the other. No versus symbol, no brain diagram and no supernatural entity.""",
    },
    {
        "name": "IMG017_FEAR_SLEEP_FEEDBACK_LOOP_BASE.png",
        "refs": ["STYLE_CONCEPTUAL_EP07.png"],
        "prompt": """Create a circular conceptual documentary composition with four materially distinct stations:
an open eye aperture surrounded by pressure contours; a daylight figure sitting upright with tense shoulders;
a fractured clock-shadow and folded dark fabric suggesting disrupted rest; and a returning ring of ambiguous
negative space. Connect them with repeated shadow direction and paper fibers, not arrows or energy. This is one
plausible fear-and-sleep feedback model, not universal causality. Keep every station readable and non-horrific.""",
    },
    {
        "name": "IMG018_STORY_BECOMES_BODY.png",
        "refs": ["STYLE_CONCEPTUAL_EP07.png"],
        "prompt": """Create a poetic but sober museum-scale composition where a warm oral-history circle at one
edge emits no words, only concentric relief ripples in translucent paper. The ripples gradually become the embossed
geometry of ribs, throat, eye line and still hands at the other edge. A dark threshold shape gains weight without
ever becoming a creature. The frame should suggest that interpretation can influence fear and later sensation,
while preserving uncertainty and avoiding literal mind control.""",
    },
    {
        "name": "IMG019_SALEM_LOOP_RETURN.png",
        "refs": ["STYLE_ARCHIVE_EP07.png", "@COMAN", "EP07_Bridget_Bishop_lithograph.jpg", "EP07_Witchcraft_at_Salem_Village_1876.jpg"],
        "prompt": """Create a sober closing evidence-room composition: the authentic Coman testimony and Bridget
Bishop lithograph remain separate source objects on two museum mounts; a third distant Salem courtroom engraving
is visible as context. At the center is an empty witness rail under neutral light, surrounded by overlapping but
faceless crowd shadows. Show experience, interpretation and collective accusation intersecting without a guilt
stamp, causal arrow or supernatural proof. The central void must be visually powerful and leave space for narration.""",
    },
    {
        "name": "SHOT01_SALEM_EMPTY_BED.png",
        "refs": ["STYLE_CINEMATIC_EP07.png", "EP07_Salem_Village_Parsonage_Foundation.jpg"],
        "prompt": """Create a quiet reserve reconstruction of an empty Salem threshold at first dawn: rough timber
doorframe opening toward pale outdoor light, an extinguished candle on a plain stool, a hanging linen edge and a
few historically plausible floorboards. Let the supplied parsonage-foundation photograph inform only the austere
material reality and geography, not become a literal rebuilt ruin. The threshold should feel psychologically open,
ordinary and unresolved. No person, body, furniture for sleeping or supernatural residue.""",
    },
    {
        "name": "SHOT02_MANY_NAMES_PAPER_LAYERS.png",
        "refs": ["STYLE_CONCEPTUAL_EP07.png", "EP07_Jinn_from_Ali_manuscript.png", "EP07_Kunisada_The_Ghost.jpg"],
        "prompt": """Create a restrained reserve base of translucent paper and cloth layers suspended across one
constant doorway-shadow geometry. Each layer contains a different non-readable material vocabulary: northern
woodgrain, manuscript ornament, Japanese print texture and modern graphite, with large blank zones for editor-added
names. Keep the authentic source fragments small and separate, never claiming they depict the same being. The
underlying threshold remains constant while surface interpretation changes.""",
    },
]


def ref_path(name: str) -> pathlib.Path:
    if name == "@COMAN":
        return ROOT / "tmp" / "pdfs" / "ep07" / "Richard_Coman_page1.png"
    return ASSETS / name


def role(name: str, index: int) -> str:
    if name.startswith("STYLE_"):
        return f"Image {index}: style reference only; use its palette, material depth and readable lighting, never its scene."
    return f"Image {index}: authentic historical source; keep it as a separate photographed object and do not redraw or rewrite it."


def generate(job: dict[str, object], overwrite: bool = False) -> pathlib.Path:
    RAW.mkdir(parents=True, exist_ok=True)
    output = RAW / str(job["name"])
    if output.is_file() and not overwrite:
        print(f"SKIP {output.name}", flush=True)
        return output
    refs = [str(value) for value in job["refs"]]
    parts: list[dict[str, object]] = []
    roles: list[str] = []
    for index, ref_name in enumerate(refs, 1):
        path = ref_path(ref_name)
        if not path.is_file():
            raise FileNotFoundError(path)
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        parts.append({"inlineData": {"mimeType": mime, "data": base64.b64encode(path.read_bytes()).decode("ascii")}})
        roles.append(role(ref_name, index))
    prompt = "Input images:\n" + "\n".join(roles) + f"\n\nPrimary request:\n{job['prompt']}\n\n{LOCK}"
    parts.append({"text": prompt})
    url = (
        f"https://aiplatform.googleapis.com/v1/projects/{project_id()}"
        f"/locations/{LOCATION}/publishers/google/models/{MODEL}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}},
    }
    print(f"GEN {output.name} refs={len(refs)}", flush=True)
    response = post_json(url, payload)
    for candidate in response.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                output.write_bytes(base64.b64decode(inline["data"]))
                print(f"OK {output.name} {output.stat().st_size}", flush=True)
                return output
    raise RuntimeError(f"No image returned for {output.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    selected = [job for job in JOBS if not args.only or job["name"] == args.only]
    for job in selected:
        generate(job, args.overwrite)


if __name__ == "__main__":
    main()
