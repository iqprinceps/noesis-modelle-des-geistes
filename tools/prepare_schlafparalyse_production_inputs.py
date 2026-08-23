#!/usr/bin/env python3
"""Build production-ready handoff inputs for Schlafparalyse EP06-EP08.

Run from repository root:
    python3 tools/prepare_schlafparalyse_production_inputs.py

What it does:
- unpacks the committed V4 image-prompt package (via the verified helper)
- extracts the canonical spoken text from each final DREHBUCH.md
- writes one clean transcript + eight voice source stems per episode
- writes ElevenLabs batch JSON files with the locked NOESIS George settings
- writes audio/stems plans, motion-graphics specs, visual cue sheets,
  thumbnail/endcard specs, production commands and production guides

Only Python stdlib is required. Actual MP3/WAV/image/video files remain runtime
outputs and are intentionally not committed.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPE_B = ROOT / "03_EPISODEN" / "TYPE_B"
SUMMARY = ROOT / "PRODUCTION_SUMMARY"

VOICE = {
    "voice": "JBFqnCBsd6RMkjVDRZzb",
    "voice_name": "George - Warm, Captivating Storyteller",
    "model": "eleven_multilingual_v2",
    "settings": {
        "stability": 0.58,
        "similarity_boost": 0.80,
        "style": 0.08,
        "speed": 1.06,
        "use_speaker_boost": True,
    },
    "seed": 2402,
    "output_format": "mp3_44100_128",
}

EPISODES = {
    "EP06": {
        "slug": "SCHLAFPARALYSE_01",
        "source": TYPE_B / "EP06_SCHLAFPARALYSE_01" / "DREHBUCH.md",
        "summary": SUMMARY / "EP06_SCHLAFPARALYSE_V4",
        "title": "Schlafparalyse I — Du bist wach. Dein Körper nicht.",
        "stems": ["ZIMMER", "OLD_HAG", "REM_ATONIE", "DREI_FAMILIEN", "LABOR", "KOERPER_BESUCHER", "PRAESENZ", "WAS_BLEIBT"],
        "intensity": [0.90, 0.72, 0.60, 0.72, 0.84, 0.88, 1.00, 0.66],
        "sfx": [
            ("EP06_SFX_BEDROOM_ROOMTONE.wav", "sehr leiser dunkler Schlafzimmer-Raumton, keine Horror-Drohne"),
            ("EP06_SFX_FOOTSTEPS_DISTANT.wav", "2–3 glaubwürdige, trockene Schritte; nur punktuell S1/S6"),
            ("EP06_SFX_MATTRESS_WEIGHT.wav", "dezentes Stoff-/Matratzenknarzen, kein Jump-Scare"),
            ("EP06_SFX_SLEEP_LAB.wav", "klinischer Raumton, Lüftung/Kabel/Monitor sehr subtil"),
            ("EP06_SFX_EEG_MOTION.wav", "kleine technische Ticks für REM-/EEG-Grafik; keine Sci-Fi-Beepfolge"),
            ("EP06_SFX_BREATH_BODY.wav", "zurückhaltende Atem-/Körpertextur, niemals Atemnot dramatisieren"),
        ],
        "motions": [
            ("REM-Atonie", "Wachheit kommt zurück, Muskelhemmung bleibt kurz bestehen; klare 2-Layer-Timeline"),
            ("Intruder / Incubus / Vestibulär", "drei Erlebnisfamilien als drei ruhige Panels"),
            ("Takeuchi 1992", "Sleep interruption -> SOREMP/REM -> isolierte Schlafparalyse; keine Phantom-per-Knopfdruck-Darstellung"),
            ("KÖRPER / BESUCHER", "binäre CTA-Karte, 1–2 Sekunden lesbar"),
            ("Präsenz-Modell", "Alarm -> Ursache fehlt -> Wahrnehmung sucht Verursacher; Hypothese, nicht bewiesene Gesamterklärung"),
        ],
        "thumb": "dark bedroom, awake rigid person in foreground, barely implied human presence at doorway, no monster face, documentary realism, high contrast, one clear visual question: someone is here",
        "endcard": "Nächste Folge: Wer sitzt auf deiner Brust? — Als Schlafparalyse zur Hexe wurde. Frage: GEHIRN oder MUSTER?",
        "pronunciation": ["David Hufford", "Old Hag", "REM-Atonie", "J. Allan Cheyne", "Incubus", "Takeuchi"],
    },
    "EP07": {
        "slug": "SCHLAFPARALYSE_02",
        "source": TYPE_B / "EP07_SCHLAFPARALYSE_02" / "DREHBUCH.md",
        "summary": SUMMARY / "EP07_SCHLAFPARALYSE_V4",
        "title": "Schlafparalyse II — Wer sitzt auf deiner Brust?",
        "stems": ["SALEM", "NACHTMAHR", "VIELE_NAMEN", "KULTUR_WIRD_WAHR", "HUFFORD", "ERFAHRUNG_KULTUR", "AEGYPTEN_DAENEMARK", "DAEMON_LERNT"],
        "intensity": [0.92, 0.72, 0.66, 0.82, 0.72, 0.88, 1.00, 0.70],
        "sfx": [
            ("EP07_SFX_SALEM_ROOMTONE.wav", "kleiner Holzraum, Stoff, ferne Bewegung; keine Hexenfilm-Kulisse"),
            ("EP07_SFX_PAPER_INK.wav", "Papier, Feder, trockene Seitenbewegung für Originalakten"),
            ("EP07_SFX_WOOD_BED.wav", "sehr dezentes Holz-/Bettgeräusch für Coman-Rekonstruktion"),
            ("EP07_SFX_COURT_MURMUR.wav", "kurzer niedriger Raum-Murmur, nicht dramatisch aufladen"),
            ("EP07_SFX_MAP_MOTION.wav", "kleine neutrale Ticks/Swishes für Kulturkarte"),
            ("EP07_SFX_MEDIA_HANDOFF.wav", "subtile Radio-/Leitungstextur für Übergang zu EP08"),
        ],
        "motions": [
            ("Salem testimony", "echtes Dokument -> Name/Datum -> markierte Passage; keine erfundene Schrift"),
            ("Viele Namen", "Mahr/Mara, Incubus, Kanashibari, Jinn/Old Hag als Vergleich; keine direkte Abstammungslinie"),
            ("Hufford inversion", "Erfahrung kann vor kultureller Kenntnis auftreten: Erlebnis -> Erzählung"),
            ("ERFAHRUNG / KULTUR", "binäre CTA-Karte"),
            ("Ägypten / Dänemark", "Deutung/Furcht/Frequenz/Länge als reduzierte Vergleichsgrafik; Quelle sichtbar"),
            ("Feedback loop", "Erlebnis -> Deutung -> Angst/Schlaf -> nächstes Erlebnis"),
        ],
        "thumb": "1692 colonial bedroom, awake immobilized man, woman-shaped silhouette near bed, archival document texture integrated but readable text only from real source, serious historical documentary",
        "endcard": "Nächste Folge: Der Mann mit dem Hut — wie das Internet einer Halluzination ein Gesicht gibt. Frage: ERLEBNIS oder ERZÄHLUNG?",
        "pronunciation": ["Richard Coman", "Bridget Bishop", "Henry Füssli", "Kanashibari", "David Hufford", "Baland Jalal", "Devon Hinton"],
    },
    "EP08": {
        "slug": "SCHLAFPARALYSE_03",
        "source": TYPE_B / "EP08_SCHLAFPARALYSE_03" / "DREHBUCH.md",
        "summary": SUMMARY / "EP08_SCHLAFPARALYSE_V4",
        "title": "Schlafparalyse III — Der Mann mit dem Hut",
        "stems": ["4500_NACHRICHTEN", "SHADOW_PEOPLE", "ALIENS", "HARVARD", "HAT_MAN", "MUSTER_MEME", "INTERNET_ANFALL", "RUECKKOPPLUNG"],
        "intensity": [0.94, 0.76, 0.78, 0.70, 1.00, 0.88, 0.96, 0.72],
        "sfx": [
            ("EP08_SFX_RADIO_ROOM.wav", "late-night radio room tone, analog console/air, no branded ident"),
            ("EP08_SFX_SHORTWAVE_STATIC.wav", "kurze kontrollierte Radio-Static-Textur"),
            ("EP08_SFX_FAX_PAPER.wav", "glaubwürdige Fax-/Papierbewegung für 4.500-Reaktionsbeat"),
            ("EP08_SFX_CRT_ROOM.wav", "leises CRT-/PC-Raumgefühl, keine überzeichneten Modemtöne"),
            ("EP08_SFX_FORUM_UI.wav", "neutrale kleine Interface-Ticks, keine Marken-Sounds"),
            ("EP08_SFX_SHADOW_ROOMTONE.wav", "stiller Schlafzimmer-Raumton; Hat Man ohne Horror-Sting"),
        ],
        "motions": [
            ("4,500 messages", "Counter/Inbox/Fax-Reaktion, Art-Bell-Datum als früher Quellen-Reveal"),
            ("Intruder overlap", "Shadow People vs bekannte Intruder-Merkmale als Überlappung, nicht Gleichsetzung"),
            ("Abduction overlap", "Immobilität / Präsenz / Licht / Körpergefühl; explizit: erklärt nicht alle Berichte"),
            ("Memory reconstruction", "Erlebnis -> spätere Befragung/Popkultur -> rekonstruierte Erinnerung"),
            ("MUSTER / MEME", "binäre CTA-Karte"),
            ("Internet feedback", "Erfahrung -> Post -> Bild/Name -> Erwartung -> nächstes Gehirn"),
            ("Final loop", "Gehirn -> Erfahrung -> Geschichte -> Erwartung -> Gehirn, als Serien-Schlussgrafik"),
        ],
        "thumb": "tall featureless black silhouette with clear hat brim at foot of ordinary bedroom, person awake in bed, realistic darkness, no glowing eyes, no smoke, no cyberpunk neon",
        "endcard": "NOESIS — Modelle des Geistes. Frage: ETWAS DRAUSSEN oder ETWAS GEMEINSAMES IN UNS?",
        "pronunciation": ["Art Bell", "Coast to Coast AM", "Heidi Hollis", "John E. Mack", "Susan Clancy", "Richard McNally", "Diphenhydramin", "Rodney Ascher"],
    },
}


def strip_markdown(text: str) -> str:
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"(?<!\*)\*(?!\*)", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def extract_acts(path: Path) -> list[tuple[str, str, str]]:
    raw = path.read_text(encoding="utf-8")
    marker = "## Vollständiger Sprechertext"
    if marker not in raw:
        raise RuntimeError(f"speaker marker missing: {path}")
    spoken = raw.split(marker, 1)[1]
    spoken = spoken.split("\n---\n", 1)[0]
    pattern = re.compile(r"^### S([1-8]) — (.+?)\n", re.M)
    hits = list(pattern.finditer(spoken))
    if len(hits) != 8:
        raise RuntimeError(f"expected 8 acts in {path}, found {len(hits)}")
    out = []
    for i, m in enumerate(hits):
        start = m.end()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(spoken)
        out.append((f"S{m.group(1)}", m.group(2).strip(), strip_markdown(spoken[start:end])))
    return out


def write_voice(ep: str, cfg: dict, acts: list[tuple[str, str, str]]) -> None:
    prod: Path = cfg["summary"]
    srcdir = prod / "voice" / "source"
    srcdir.mkdir(parents=True, exist_ok=True)

    clean = "\n\n".join(text.strip() for _, _, text in acts).strip() + "\n"
    (prod / "07_VOICE_SCRIPT_CLEAN_V4.txt").write_text(clean, encoding="utf-8")

    stems = []
    for idx, ((sid, _title, text), short) in enumerate(zip(acts, cfg["stems"]), 1):
        stem_id = f"{ep}_V4_S{idx:02d}_{short}"
        stem_path = srcdir / f"{stem_id}.txt"
        stem_path.write_text(text, encoding="utf-8")
        stems.append({
            "id": stem_id,
            "text_file": stem_path.relative_to(ROOT).as_posix(),
        })

    batch = {
        **VOICE,
        "output_dir": (prod / "voice" / "raw_stems").relative_to(ROOT).as_posix(),
        "normalization_target": "-18 LUFS integrated, true peak <= -2 dBTP per VO stem/master",
        "master_structure": {
            "pre_roll_seconds": 0.35,
            "inter_stem_gap_seconds": 0.65,
            "tail_seconds": 2.2,
            "sample_rate_hz": 48000,
            "master_codec": "PCM 24-bit mono",
        },
        "stems": stems,
        "pronunciation_notes": [
            "Batch vom Repository-Root ausfuehren.",
            "Keine Lautschrift-Kruecken ungeprueft in den finalen Text schreiben.",
            "Vor dem Vollbatch einen kurzen Hoertest fuer Eigennamen/Fachbegriffe machen: " + ", ".join(cfg["pronunciation"]),
            "Nur die Voice-Quelle korrigieren, falls ein Begriff hoerbar falsch ausgesprochen wird; DREHBUCH.md bleibt kanonisch.",
        ],
    }
    (prod / "voice").mkdir(parents=True, exist_ok=True)
    (prod / "voice" / "voice_batch_v4.json").write_text(
        json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def audio_plan(ep: str, cfg: dict) -> str:
    sx = "\n".join(f"- `{name}` — {desc}" for name, desc in cfg["sfx"])
    curve = "\n".join(f"- S{i}: `{v:.2f}`" for i, v in enumerate(cfg["intensity"], 1))
    return f"""# {ep} — Audio / Stems Plan\n\n**Status:** PRODUCTION LOCK  \n**Voice:** George / ElevenLabs multilingual v2 / speed 1.06\n\n## Voice\n- Voice ID: `JBFqnCBsd6RMkjVDRZzb`\n- stability `0.58` / similarity `0.80` / style `0.08` / speed `1.06` / speaker boost `true`\n- 8 source stems under `voice/source/`\n- raw outputs under `voice/raw_stems/`\n- normalize VO to about `-18 LUFS integrated`, `<= -2 dBTP`\n- final VO master: `{ep}_SCHLAFPARALYSE_V4_VO_MASTER.wav`\n- 48 kHz mono PCM24 working master\n\n## Music stems\nNo licensed third-party music is required. Build the bed from project-owned synthesis.\n\nRequired:\n- `{ep}_MX_LOW.wav` — low foundation; keep narration clear\n- `{ep}_MX_HARMONIC.wav` — sparse audible texture for phone speakers\n- `{ep}_MX_NOISE.wav` — restrained room/noise layer\n- `{ep}_MX_MASTER.wav` — premix before VO ducking\n\nRelative act energy:\n{curve}\n\nNormal narration bed around `-30 LUFS`; smooth ducking; no pumping. Let music rise only in deliberate pauses/reveals.\n\n## SFX / atmosphere\n{sx}\n\nForbidden across the trilogy:\n- trailer booms / jump scares\n- reversed choir / generic occult drones\n- cyberpunk neon-sonic language\n- branded phone/radio/UI sounds\n- SFX that imply a supernatural entity is objectively present\n\n## Final mix\n- stereo 48 kHz AAC 320 kbps delivery audio\n- integrated loudness `-14 LUFS +/- 0.5`\n- true peak `<= -0.8 dBTP`\n- dialogue remains foreground\n\n## Export stems\nDeliver separately: VO master, LOW, HARMONIC, NOISE and every required SFX file above. Final mix is derived from stems, not baked into VO.\n"""


def motion_plan(ep: str, cfg: dict) -> str:
    items = "\n".join(f"## {i}. {name}\n{desc}\n" for i, (name, desc) in enumerate(cfg["motions"], 1))
    return f"""# {ep} — Motion Graphics V4\n\n**Rule:** simple, readable in 3–6 seconds, German display text, no stock-template look. Historical quotes/text only when present on the real source.\n\n{items}\n## Technical\n- 1920x1080 / 30 fps / safe margins\n- no tiny paper-like labels\n- no medical infographic overload\n- source line lower-left when a factual comparison is shown\n- all uncertainty/causality must match `CLAIMS_LOCK_V2.md`\n"""


def thumbnail_endcard(ep: str, cfg: dict) -> str:
    return f"""# {ep} — Thumbnail + Endcard V4\n\n## Thumbnail primary concept\n{cfg['thumb']}\n\n### Generation prompt\nPhotorealistic cinematic investigative-documentary YouTube thumbnail, 16:9, one dominant subject, readable at 246 px width, deep natural shadows, practical light, sober mystery, no generic cyan-magenta neon, no gore, no fake archive text, no clutter. SUBJECT: {cfg['thumb']}. Leave controlled negative space for very short title text added in edit.\n\n## Endcard\n- duration exactly `20 s`\n- spoken/visible handoff: {cfg['endcard']}\n- reserve YouTube endscreen zones\n- background may move subtly; no new factual claim\n"""


def cue_rows(acts: list[tuple[str, str, str]], cfg: dict) -> list[list[str]]:
    rows = []
    for i, (sid, title, text) in enumerate(acts, 1):
        first = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))[0][:150]
        rows.append([
            sid,
            title,
            first,
            "archive/reconstruction/motion mix",
            f"relative audio energy {cfg['intensity'][i-1]:.2f}",
            "2–5 visual changes inside beat; no still >9 s",
        ])
    return rows


def production_guide(ep: str, cfg: dict) -> str:
    prod = cfg["summary"].relative_to(ROOT).as_posix()
    episode_dir = (TYPE_B / f"{ep}_{cfg['slug']}").relative_to(ROOT).as_posix()
    return f"""# {ep} — Production Guide V4\n\n**Status:** READY FOR PRODUCTION INPUTS  \n**Episode:** {cfg['title']}  \n**Canonical script:** `{episode_dir}/DREHBUCH.md`  \n**Clean voice:** `{prod}/07_VOICE_SCRIPT_CLEAN_V4.txt`\n\n## Prepared\n- final voice-authentic script + claims lock\n- verified asset package / downloader / rights traffic lights\n- V4 Nano Banana prompt package with exact reference filenames\n- clean master transcript + 8 voice source stems\n- ElevenLabs batch config\n- Audio/Stems Plan\n- Motion Graphics spec\n- Visual Cue Sheet\n- Thumbnail + 20 s Endcard spec\n\n## 1. Prepare local tree\n```bash\npython3 tools/prepare_schlafparalyse_production_inputs.py\n```\nThis also unpacks the committed V4 image-prompt ZIP safely.\n\n## 2. Download source assets\n```bash\ncd 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2\npython3 download_schlafparalyse_assets.py\n```\nReview YELLOW assets before use. RED files remain research-only.\n\n## 3. Voice generation\nFrom repo root:\n```bash\nelevenlabs_cli.py batch --batch-file {prod}/voice/voice_batch_v4.json --execute\npython3 tools/schlafparalyse_voice.py {ep} all\n```\nBefore the full batch, pronunciation-test: {', '.join(cfg['pronunciation'])}.\n\n## 4. Images\nUse `{episode_dir}/NANOBANANA_GUIDE_V4.md` and the four S1–S8 batch files. Generate style anchors first. MAIN/RESERVE prompts are coverage, not a mandate to use every frame.\n\n## 5. Edit targets\n- 140–155 shots\n- average ~3.5–4.5 s\n- no still >9 s\n- >=85 unique motifs\n- no repeat inside same act\n- 3–5 motion clips/graphics\n- AI reconstruction <=65% where archival material exists\n- time follows the final spoken voice, not hard act timestamps\n\n## 6. Audio\nFollow `AUDIO_STEMS_PLAN.md`. Keep dialogue dominant. Music/SFX are project-owned/runtime-generated; no third-party licensed track is required.\n\n## 7. Subtitles\nCreate SRT from final forced alignment; <=84 characters/block.\n\n## 8. Export\n- 1920x1080, 30 fps\n- H.264 High, yuv420p / TV range\n- AAC stereo 48 kHz 320 kbps\n- `-14 LUFS +/-0.5`, true peak `<= -0.8 dBTP`\n- endcard exactly 20 s\n\n## Runtime outputs intentionally not committed\n- ElevenLabs MP3 stems\n- normalized VO WAV/master + forced alignment JSON\n- generated AI images/style anchors\n- synthesized music/SFX WAV stems\n- final timeline/render/SRT/thumbnail render\n\nNo creative or structural decision is required before starting these jobs. Replacement decisions after generation are normal QA.\n"""


def commands(ep: str, cfg: dict) -> str:
    prod = cfg["summary"].relative_to(ROOT).as_posix()
    return f"""# {ep} Production Commands\n\n```bash\n# once for the whole trilogy\ngit pull origin master\npython3 tools/prepare_schlafparalyse_production_inputs.py\n\n# source media\ncd 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2\npython3 download_schlafparalyse_assets.py\ncd ../../..\n\n# voice\nelevenlabs_cli.py batch --batch-file {prod}/voice/voice_batch_v4.json --execute\npython3 tools/schlafparalyse_voice.py {ep} all\n```\n"""


def build_episode(ep: str, cfg: dict) -> None:
    acts = extract_acts(cfg["source"])
    prod: Path = cfg["summary"]
    prod.mkdir(parents=True, exist_ok=True)
    write_voice(ep, cfg, acts)
    (prod / "AUDIO_STEMS_PLAN.md").write_text(audio_plan(ep, cfg), encoding="utf-8")
    (prod / "MOTION_GRAPHICS_V4.md").write_text(motion_plan(ep, cfg), encoding="utf-8")
    (prod / "THUMBNAIL_ENDCARD_V4.md").write_text(thumbnail_endcard(ep, cfg), encoding="utf-8")
    (prod / "PRODUCTION_GUIDE_V4.md").write_text(production_guide(ep, cfg), encoding="utf-8")
    (prod / "PRODUCTION_COMMANDS.md").write_text(commands(ep, cfg), encoding="utf-8")
    with (prod / "VISUAL_CUE_SHEET.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["act", "beat", "anchor_text", "visual_mode", "audio", "edit_rule"])
        w.writerows(cue_rows(acts, cfg))
    print(f"{ep}: built {prod.relative_to(ROOT)}")


def write_series_readme() -> None:
    d = SUMMARY / "SCHLAFPARALYSE_V4"
    d.mkdir(parents=True, exist_ok=True)
    text = """# Schlafparalyse V4 — Production Handoff\n\nStatus: **READY FOR PRODUCTION INPUTS**\n\nThe trilogy has final scripts, claims locks, verified source-asset tooling, V4 image prompts, voice-source generation, ElevenLabs batch configs, audio/stem plans, motion/cue specs, thumbnail/endcard specs and export QA.\n\n## One-time local preparation\n```bash\npython3 tools/prepare_schlafparalyse_production_inputs.py\n```\n\nThen follow the per-episode guides:\n- `PRODUCTION_SUMMARY/EP06_SCHLAFPARALYSE_V4/PRODUCTION_GUIDE_V4.md`\n- `PRODUCTION_SUMMARY/EP07_SCHLAFPARALYSE_V4/PRODUCTION_GUIDE_V4.md`\n- `PRODUCTION_SUMMARY/EP08_SCHLAFPARALYSE_V4/PRODUCTION_GUIDE_V4.md`\n\n## What “production ready” means here\nAll creative/structural inputs are locked. Actual voice MP3/WAVs, generated images, synthesized music/SFX stems, subtitles and final renders are runtime outputs and are intentionally created locally/API-side rather than stored in Git.\n"""
    (d / "README.md").write_text(text, encoding="utf-8")


def unpack_prompts() -> None:
    helper = ROOT / "tools" / "unpack_schlafparalyse_prompts_v4.py"
    if helper.is_file():
        subprocess.run([sys.executable, str(helper)], cwd=ROOT, check=True)


def main() -> int:
    unpack_prompts()
    for ep, cfg in EPISODES.items():
        if not cfg["source"].is_file():
            raise SystemExit(f"Missing canonical script: {cfg['source']}")
        build_episode(ep, cfg)
    write_series_readme()
    print("Schlafparalyse EP06-EP08 production inputs are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
