# EP04A — Production Commands

Run from repository root. Creative counts and timings follow `01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md`.

## 1. Verify / download archive

```bash
python 03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/download_ep04ab_assets.py --dry-run --only EP04A
python 03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/download_ep04ab_assets.py --only EP04A --green-only
```

Add YELLOW assets only after their listed rights/ShareAlike/jurisdiction review.

## 2. Generate image coverage

Use, in story order:

```text
PRODUCTION_SUMMARY/EP04A_JUNG_KUNDALINI_V5/NANOBANANA_PROMPTS_V5_S1_S3.md
PRODUCTION_SUMMARY/EP04A_JUNG_KUNDALINI_V5/NANOBANANA_PROMPTS_V5_S4_S6.md
PRODUCTION_SUMMARY/EP04A_JUNG_KUNDALINI_V5/NANOBANANA_PROMPTS_V5_S7_S8.md
```

The current `44 MAIN + 8 RESERVE` set is a prepared coverage pool, never a quota. Generate/select only what the final cut actually needs.

## 3. Generate raw VO

```bash
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP04A_JUNG_KUNDALINI_V5/voice/voice_batch.json --execute
```

## 4. Build VO master + alignment

```bash
python tools/ep04ab_voice.py EP04A all
```

## 5. Build project-owned audio stems

```bash
python tools/ep04ab_audio_render.py EP04A
```

The delivered stems are trimmed to the actual VO-master length. Any endscreen/atmospheric continuation is chosen in the edit, not baked as a fixed duration.

## 6. Edit

Canonical cue map:

```text
PRODUCTION_SUMMARY/EP04A_JUNG_KUNDALINI_V5/VISUAL_CUE_SHEET_V5_FINAL.csv
```

Motion rules:

```text
PRODUCTION_SUMMARY/EP04A_JUNG_KUNDALINI_V5/MOTION_GRAPHICS_V5.md
```

Timing follows the actual VO master/alignment. Do not back-fill a target runtime, shot count or uniform hold duration into the edit.

## 7. Captions / delivery

Build captions from the forced-alignment JSON using the clean transcript. Technical delivery follows the global NOESIS delivery spec; creative duration remains whatever this episode needs.
