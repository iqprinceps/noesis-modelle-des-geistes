#!/usr/bin/env python3
"""Cached Vertex preview/final still generation for EP02_EN."""

from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import hashlib
import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "07_ENGLISH_PRODUCTION" / "EP02_GATEWAY"
PREVIEW = EP / "03_VISUALS" / "GENERATED" / "PREVIEWS"
FINAL = EP / "03_VISUALS" / "GENERATED" / "STILLS"
LOG = EP / "03_VISUALS" / "GENERATED" / "VERTEX_GENERATION_LOG.jsonl"
LOCATION = "global"
MODELS = {"preview": "gemini-2.5-flash-image", "final": "gemini-3-pro-image"}

GLOBAL = """Use case: historical-scene / photorealistic-natural.
Asset type: 16:9 documentary still for EP02 The Gateway Process.
The viewer-facing frame carries no production-category badge. Reconstruction is
communicated by a consistent restrained visual grammar and editor context only at
the first block entry. Early-1980s materials, natural anatomy, readable midtones,
one cool institutional source and at most one muted warm practical. Tactile 35mm
grain, no glossy stock-photo finish. No logos, captions, watermarks, invented
documents, readable generated text, insignia close-ups, duplicate people, extra
limbs, modern devices, neon brains, portals, occult symbols, or fantasy effects.
Leave space for editor-added factual typography where requested."""

JOBS = [
    {
        "id": "GW_EN_STILL01_MCDONNELL_REPORT_V2",
        "prompt": "1983 U.S. Army intelligence office at Fort Meade. Camera is directly behind a seated male lieutenant colonel: only the back of his head, shoulders, forearms, and hands are visible, absolutely no face, cheek, profile, reflection, portrait, or identity detail. He assesses a thick report at a metal desk. Olive drab service uniform is period-plausible but insignia are soft and not a focal point. Every page is blank or fully out of focus with zero visible letters. Calm procedural action, venetian-blind daylight, locked documentary composition.",
    },
    {
        "id": "GW_EN_STILL02_BENTOV_OSCILLATOR_OBJECT_V4",
        "prompt": "Object-only late-1970s mechanical workbench, with no person, hands, body, portrait, or reflection anywhere. A carefully built pendulum-and-spring apparatus sits beside purely mechanical tools and analog needle meters turned partly away. No digital displays, LED readouts, screens, or numeric scales face the camera. Bentov's authentic portrait is shown separately at introduction; this is only a labeled reconstruction of the physical oscillator idea. Worn wood and brass; all papers blank with zero letters or numbers; practical task lighting; coherent apparatus geometry.",
    },
    {
        "id": "GW_EN_STILL03_TEN_DIGIT_PARTICIPANT_V2",
        "prompt": "Controlled early-1980s consciousness experiment room. One anonymous adult participant reclines with headphones while a plain opaque unmarked envelope and an inactive ten-position display box sit across the room. The envelope is completely blank: no seal word, letters, numbers, logo, stamp, handwriting, or symbols. No digits are visible; editor adds the actual sequence. A technician's empty chair emphasizes that nobody present knows the target. Clinical, restrained, plausible geometry, no paranormal effect.",
    },
    {
        "id": "GW_EN_STILL04_REPORTS_SIDE_BY_SIDE_V2",
        "prompt": "Top-down evidence-table photograph: three blank ruled observer sheets lie side by side, each showing only one simple geometric pencil sketch—circle, angular outline, curved edge—with absolutely no words, letters, numbers, pseudo-writing, signatures, stamps, or labels. A completely blank face-down target card sits above them. Editor overlays exact comparison marks later. Cool institutional desk light, one amber reflection, rigorous chain-of-custody feeling, no hands.",
    },
    {
        "id": "GW_EN_STILL05_THREE_OBSERVERS_V2",
        "prompt": "Wide conceptual documentary tableau of three anonymous adult observers in three separate but visually connected early-1980s rooms, each seated at a plain desk with headphones and a closed blank report folder. The full frame contains zero words, letters, numbers, captions, explanatory copy, labels, title blocks, interface text, or logos. No split-screen border. Subtle differences in practical light and clock-shadow direction distinguish present, immediate past, and immediate future without readable clocks or fantasy effects. Target remains hidden. All three bodies anatomically correct and clearly separate.",
    },
    {
        "id": "GW_EN_FILMIC06_MONROE_RADIO_STUDIO",
        "prompt": "Late-1950s American radio control room at night. An anonymous broadcasting executive is seen only from behind, one hand on a large rotary console control while reel-to-reel tape machines and a studio microphone sit beyond glass. No face or asserted likeness. Warm vacuum-tube glow against blue-black shadows, tactile knobs and braided cable, cinematic 35mm realism, one decisive human action, all dials too oblique to read.",
    },
    {
        "id": "GW_EN_FILMIC07_MONROE_LAB_BUILDER",
        "prompt": "Early-1970s private acoustics laboratory in Virginia. Anonymous older male engineer shown from shoulder level down, sleeves rolled, connecting two headphone channels to a reel-to-reel deck and analogue oscillator. Natural hands and physically plausible cabling. The scene communicates methodical construction rather than mysticism; dark wood, brushed aluminium, one amber task lamp, no readable markings.",
    },
    {
        "id": "GW_EN_FILMIC08_GATEWAY_TRAINING_SESSION",
        "prompt": "Early-1980s guided-listening training room, three anonymous adults reclining in separate simple booths with padded headphones, eyes closed, while a technician behind glass advances a reel-to-reel tape. Calm bodily stillness, practical institutional materials, deep spatial composition, quiet anticipation. No faces dominate, no supernatural effect, no readable controls or paperwork.",
    },
    {
        "id": "GW_EN_FILMIC09_BENTOV_CATHETER_BENCH",
        "prompt": "Late-1960s biomedical inventor's workshop. Object-focused close photograph of a flexible steerable catheter prototype curving under mechanical tension beside a small brass joystick linkage and precision hand tools. No person or medical procedure. White polymer tubing, stainless guide wires, worn green cutting mat, period-correct analogue workspace, exact plausible geometry, no text.",
    },
    {
        "id": "GW_EN_FILMIC10_BODY_OSCILLATION_TEST",
        "prompt": "Late-1970s physiology experiment seen in restrained profile: anonymous adult lies still on a narrow cot while a mechanical displacement sensor lightly contacts the upper chest and records tiny rhythmic movement on analogue paper. Entire body remains anatomically natural; the apparatus, cable and paper feed are physically coherent. Clinical darkness, soft side light, no readable scale or medical claim.",
    },
    {
        "id": "GW_EN_FILMIC11_LEFT_EAR_HEADPHONE_MACRO",
        "prompt": "Extreme cinematic macro of the left side of an anonymous listener wearing heavy 1970s studio headphones. Fingertips settle the ear cup; coiled cable leads into darkness. Real skin pores, worn vinyl, brushed metal and shallow depth of field. One cool reflection and a faint amber practical, no face identity, no text, no waveform graphics.",
    },
    {
        "id": "GW_EN_FILMIC12_RIGHT_EAR_HEADPHONE_MACRO",
        "prompt": "Distinct reverse-angle extreme macro of the right ear under a different 1970s headphone cup, seen through the arc of the headband with the second cable channel in sharp focus. Natural skin and hair, old foam and oxidized metal, soft blue institutional light. Not a mirrored duplicate of another shot; no text or waveform graphics.",
    },
    {
        "id": "GW_EN_FILMIC13_AUDITORY_PROCESSING_PROFILE",
        "prompt": "Anonymous listener in near-profile inside a dark acoustics booth, both ears enclosed by headphones. Reflected bands from two hidden analogue oscillators fall across the booth walls and meet behind the head without becoming a literal brain graphic. Human breathing and subtle posture implied, sophisticated documentary photography, no text or mystical symbols.",
    },
    {
        "id": "GW_EN_FILMIC14_ALTERED_STATE_LISTENER",
        "prompt": "Close documentary portrait without identifiable likeness: anonymous adult reclining with headphones, eyes closed, one hand relaxed open beside a tape remote. The room stays physically real while a very subtle double reflection appears only in the observation glass. Intimate, quiet, ambiguous, early-1980s materials, no glowing aura, no text.",
    },
    {
        "id": "GW_EN_FILMIC15_COLD_WAR_CORRIDOR",
        "prompt": "Long early-1980s military research corridor after hours, anonymous uniformed figure walking away toward a single lit testing room. Cable trunks, acoustic doors and paper file carts establish an institution willing to test unusual ideas. Restrained geometry and sodium-vapour ambience, no readable signs, no insignia close-up, no horror figure.",
    },
    {
        "id": "GW_EN_FILMIC16_FOCUS10_BODY_ASLEEP",
        "prompt": "Anonymous participant viewed from foot of a simple listening cot, body fully relaxed under a light blanket while alert eyes remain barely open beneath large headphones. The observation room is dim and materially ordinary, with a single pulse lamp reflected in glass. Mind awake, body asleep conveyed through posture only; no text or supernatural effect.",
    },
    {
        "id": "GW_EN_FILMIC17_FOCUS_DIFFICULTY",
        "prompt": "Tense but restrained close view of an anonymous participant attempting a deep listening exercise: hands grip the cot edge slightly, brow visible only in partial silhouette, headphones and cable physically grounded. Most surrounding booths beyond glass are empty and dark. Human effort and rarity, not failure spectacle; no text or paranormal effect.",
    },
    {
        "id": "GW_EN_FILMIC18_FEWER_PARTICIPANTS",
        "prompt": "Wide early-1980s training room after a session: a long arc of empty reclining chairs and disconnected headphones recedes into darkness, while one anonymous participant remains seated at the far end under a small pool of light. Quiet visual metaphor for very few reaching the state, no numbers, labels, or interface graphics.",
    },
    {
        "id": "GW_EN_FILMIC19_PARTIAL_DIGIT_NOTES",
        "prompt": "Top-down evidentiary photograph of an early-1980s laboratory desk after a blind digit trial. Ten blank physical tiles sit in a row; four have been turned over to reveal only simple cyan light, not digits. A separate sealed target envelope remains face down and unmarked. Human presence implied by a chair shadow, no hands, no readable writing.",
    },
    {
        "id": "GW_EN_FILMIC20_AUTHORIZATION_HAND",
        "prompt": "Early-1980s Army office close-up: an anonymous officer's natural hand hovers above an unsigned authorization sheet beside a closed file, then hesitates. The paper is deliberately blank and angled away; a fountain pen casts a long shadow across the desk. Human decision under institutional pressure, cinematic restraint, no readable text or badge.",
    },
    {
        "id": "GW_EN_FILMIC21_H_TRIAL_OVERHEAD",
        "prompt": "High overhead cinematic view of three separate early-1980s listening booths arranged around one sealed central target chamber. Three anonymous observers lie or sit with headphones; narrow pools of light reach toward the centre but do not touch. Physically plausible architecture, deep shadows, no labels, clocks, diagrams, split-screen borders or supernatural glow.",
    },
    {
        "id": "GW_EN_FILMIC22_MODERN_EEG_LAB",
        "prompt": "Contemporary independent auditory neuroscience lab, documentary realism. Anonymous participant wears research headphones and a sparse EEG cap while a researcher seen from behind checks raw traces on an out-of-focus monitor. Clean but not glossy, daylight mixed with cool screen light, scientifically plausible electrodes, no readable interface or branding.",
    },
    {
        "id": "GW_EN_FILMIC23_NO_DATASET_EMPTY_LAB",
        "prompt": "Empty early-1980s experiment room after everyone has left. Headphones rest on a cot, a ten-position display is dark, and an open metal data drawer is visibly empty. One blank sheet lies under a cold fluorescent tube. The absence of a controlled dataset is communicated through physical absence, not text; austere cinematic framing.",
    },
    {
        "id": "GW_EN_FILMIC24_THREE_INPUTS_STILL_LIFE",
        "prompt": "Moody evidence still life on one large early-1980s desk: a reel-to-reel headphone system, a brass mechanical oscillator model, and three blank witness sketch sheets occupy three clearly separated pools of light. At the far edge, an Army file folder waits in shadow. Coherent scale and period materials, no readable text, no floating graphics.",
    },
    {
        "id": "GW_EN_FILMIC25_COLD_WAR_DESPERATION",
        "prompt": "Early-1980s operations room in a tense late-night lull: empty radar consoles, paper plotting table, cigarette smoke in projector light, and one anonymous exhausted analyst leaning forward with face hidden in hands. Historically plausible equipment, restrained Cold War unease, no readable screens, no sensational weapons imagery.",
    },
    {
        "id": "GW_EN_FILMIC26_REPORT_UNDER_LAMP",
        "prompt": "A thick authentic-looking but completely unreadable government file under a single desk lamp in an otherwise dark office. Its pages are held by a brass clip; beside it sit headphones, a mechanical pointer and an empty chair. The composition feels like evidence that survived its theory, tactile 35mm photography, no visible words, seals, labels or invented official marks.",
    },
    {
        "id": "GW_EN_FILMIC27_ANONYMOUS_OPERATOR",
        "prompt": "Late-1980s experimental lab seen through observation glass: one anonymous operator sits alone before a physical random-event apparatus and rows of small unlit indicator lamps. The person is tiny in frame and unidentifiable; the machinery dominates. Quiet quantitative mystery, realistic cables and metal, no readable numbers or text.",
    },
]


_token: tuple[str, float] | None = None
_lock = threading.Lock()


def token() -> str:
    global _token
    with _lock:
        if _token and _token[1] > time.time() + 60:
            return _token[0]
        p = subprocess.run(["gcloud", "auth", "application-default", "print-access-token"], capture_output=True, text=True, shell=True, timeout=60)
        value = p.stdout.strip()
        if not value:
            raise RuntimeError("Vertex ADC token unavailable")
        _token = (value, time.time() + 3300)
        return value


def project() -> str:
    value = os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    if not value:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set")
    return value


def post(url: str, payload: dict, retries: int = 7) -> dict:
    waits = [4, 8, 15, 30, 60, 90]
    for attempt in range(retries):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=420) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")[:800]
            if exc.code == 429 and any(marker in body.casefold() for marker in ("resource_exhausted", "credit", "billing", "quota")):
                raise RuntimeError(f"HTTP 429 non-retryable capacity/credit blocker: {body}") from None
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(waits[min(attempt, len(waits) - 1)])
                continue
            raise RuntimeError(f"HTTP {exc.code}: {body}") from None


def generate(job: dict, mode: str) -> Path:
    out_dir = PREVIEW if mode == "preview" else FINAL
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{job['id']}_{mode.upper()}.png"
    meta = out.with_suffix(".json")
    if out.is_file() and meta.is_file():
        print(f"SKIP {out.name}", flush=True)
        return out
    model = MODELS[mode]
    prompt = f"{GLOBAL}\n\nPrimary request: {job['prompt']}"
    url = f"https://aiplatform.googleapis.com/v1/projects/{project()}/locations/{LOCATION}/publishers/google/models/{model}:generateContent"
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9", "imageSize": "1K" if mode == "preview" else "2K"}}}
    started = time.time()
    response = post(url, payload)
    images = []
    for cand in response.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                images.append(base64.b64decode(inline["data"]))
    if not images:
        raise RuntimeError(f"no image returned for {job['id']}")
    out.write_bytes(images[0])
    record = {"asset_id": job["id"], "mode": mode, "provider": "Vertex AI", "model": model, "location": LOCATION, "seed": None, "prompt": prompt, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "output": str(out.resolve()), "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest(), "seconds": round(time.time() - started, 3), "cache_rule": "skip when PNG and metadata both exist"}
    meta.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    with _lock:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    print(f"OK {out.name}", flush=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preview", "final"], required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=2)
    args = ap.parse_args()
    selected = JOBS
    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        selected = [j for j in JOBS if j["id"] in wanted]
    failures = []
    with cf.ThreadPoolExecutor(max_workers=max(1, min(args.jobs, 2))) as pool:
        futures = {pool.submit(generate, job, args.mode): job for job in selected}
        for fut in cf.as_completed(futures):
            try:
                fut.result()
            except Exception as exc:
                failures.append((futures[fut]["id"], str(exc)))
                print(f"FAIL {failures[-1][0]}: {failures[-1][1]}", flush=True)
    if failures:
        raise SystemExit(json.dumps(failures, indent=2))


if __name__ == "__main__":
    main()
