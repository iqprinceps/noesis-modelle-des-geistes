# EP05 V5 — Production Commands

Run from repository root.

## 1. Voice raw stems

```bash
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/voice/voice_batch_v4.json --execute
```

## 2. VO master + forced alignment

```bash
python tools/ep05_voice.py all
```

Outputs under:
`PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/voice/`

## 3. Project-owned music + SFX working stems

```bash
python tools/ep05_audio_stems.py
```

Outputs under:
`PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/audio/stems/`

The audio generator reads the real finished VO stem durations, so the music/SFX stems inherit the actual episode length rather than a hard target runtime.

## 4. Image generation

Manual NanoBanana batches, in order:

1. `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/NANOBANANA_PROMPTS_V5_S1_S2.md`
2. `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/NANOBANANA_PROMPTS_V5_S3_S4.md`
3. `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/NANOBANANA_PROMPTS_V5_S5_S6.md`
4. `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/NANOBANANA_PROMPTS_V5_S7_S8.md`

Each block already contains filename, references and full prompt.

## 5. Edit

Use forced alignment + `VISUAL_CUE_SHEET.csv` for text anchors. Build motion per `MOTION_GRAPHICS_V5.md` and mix per `AUDIO_STEMS_PLAN.md`.

## 6. Final delivery

- 1920×1080 / 30 fps
- H.264 High / yuv420p TV range
- AAC 48 kHz stereo 320 kbps
- -14 LUFS +/-0.5
- TP <= -0.8 dBTP
- SRT <=84 chars/block
- 20 s endcard
