# EP04B — Production Commands

Run from repository root. Creative counts and timings follow `01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md`.

## 1. Verify / download archive

```bash
python 03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/download_ep04ab_assets.py --dry-run --only EP04B
python 03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/download_ep04ab_assets.py --only EP04B --green-only
```

EP04B is deliberately GREEN/archive-first. Add YELLOW only when it materially improves the episode enough to justify its rights requirements.

## 2. Generate gap-fill coverage

```text
PRODUCTION_SUMMARY/EP04B_CHAKRA_GENEALOGIE_V5/NANOBANANA_PROMPTS_V5_S1_S4.md
PRODUCTION_SUMMARY/EP04B_CHAKRA_GENEALOGIE_V5/NANOBANANA_PROMPTS_V5_S5_S8.md
```

The current `20 MAIN + 4 RESERVE` set is intentionally compact and is not a quota. Real historical source objects carry the main reveals.

## 3. Generate raw VO

```bash
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP04B_CHAKRA_GENEALOGIE_V5/voice/voice_batch.json --execute
```

## 4. Build VO master + alignment

```bash
python tools/ep04ab_voice.py EP04B all
```

## 5. Build project-owned audio stems

```bash
python tools/ep04ab_audio_render.py EP04B
```

Delivered stems end with the actual VO master. Any final map/end-screen hold is created at edit length, not template length.

## 6. Build local render manifest + timeline

Cue map:

```text
PRODUCTION_SUMMARY/EP04B_CHAKRA_GENEALOGIE_V5/VISUAL_CUE_SHEET_V5.csv
```

Motion plan:

```text
PRODUCTION_SUMMARY/EP04B_CHAKRA_GENEALOGIE_V5/MOTION_GRAPHICS_V5.md
```

Run:

```bash
python tools/noesis_render.py EP04B doctor
python tools/noesis_render.py EP04B manifest
python tools/noesis_render.py EP04B plan
```

Review `06_PRODUCTION/EP04B_CHAKRA_GENEALOGIE_V5/render_manifest.json`. A cue can contain one local source object or several sequential files. Source readability and the real Voice determine the rhythm; there is no uniform hold duration.

## 7. Render + QA

```bash
python tools/noesis_render.py EP04B all
```

The `archive` profile is deliberately drier than EP04A: controlled document pans, restrained zoom and less cinematic drift. Motion clips remain explicit local assets and are never replaced silently.

## 8. Captions / delivery

Use forced alignment against `07_VOICE_SCRIPT_CLEAN_V5.txt`. Technical delivery follows NOESIS spec; creative duration remains whatever the finished episode needs.
