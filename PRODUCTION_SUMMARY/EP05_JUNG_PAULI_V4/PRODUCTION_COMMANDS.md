# EP05 V5 — Production Commands

Run from repository root. Creative render quantities follow `01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md`.

## 1. Voice raw stems

```bash
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/voice/voice_batch_v4.json --execute
```

## 2. VO master + forced alignment

```bash
python tools/ep05_voice.py all
```

Outputs under `PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/voice/`.

## 3. Project-owned music + SFX working stems

```bash
python tools/ep05_audio_stems.py
```

The audio generator reads the real finished VO stem durations, so music/SFX inherit the actual episode length rather than a target runtime.

## 4. Image generation

Manual NanoBanana batches, in order:

1. `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/NANOBANANA_PROMPTS_V5_S1_S2.md`
2. `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/NANOBANANA_PROMPTS_V5_S3_S4.md`
3. `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/NANOBANANA_PROMPTS_V5_S5_S6.md`
4. `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/NANOBANANA_PROMPTS_V5_S7_S8.md`

Each block contains filename, references and full prompt.

## 5. Local render manifest + word-aligned timeline

Canonical visual cues:

```text
03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/VISUAL_CUE_SHEET.csv
```

Run:

```bash
python tools/noesis_render.py EP05 doctor
python tools/noesis_render.py EP05 manifest
python tools/noesis_render.py EP05 plan
```

Review `06_PRODUCTION/EP05_JUNG_PAULI_V4/render_manifest.json`. One cue may map to one file or a list of files. Missing mappings fail closed; no generic filler is inserted.

## 6. Render + QA

```bash
python tools/noesis_render.py EP05 all
```

EP05 uses the `precision` camera profile: controlled movement for correspondence, diagrams, portraits and documentary evidence. Its timing remains tied to its own forced alignment and cue structure.

## 7. Final delivery

- 1920×1080 / 30 fps
- H.264 High / yuv420p TV range
- AAC 48 kHz stereo 320 kbps
- -14 LUFS +/-0.5
- TP <= -0.8 dBTP
- SRT <=84 chars/block
- endcard duration follows the episode handoff rather than a global template
