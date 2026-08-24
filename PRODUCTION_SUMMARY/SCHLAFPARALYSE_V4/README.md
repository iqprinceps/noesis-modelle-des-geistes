# Schlafparalyse V4 — Production Handoff

Status: **READY FOR PRODUCTION INPUTS**

The trilogy has final scripts, claims locks, verified source-asset tooling, V4 image prompts, voice-source generation, ElevenLabs batch configs, audio/stem plans, motion/cue specs, thumbnail/endcard specs and export QA.

## One-time local preparation
```bash
python3 tools/prepare_schlafparalyse_production_inputs.py
```

Then follow the per-episode guides:
- `PRODUCTION_SUMMARY/EP06_SCHLAFPARALYSE_V4/PRODUCTION_GUIDE_V4.md`
- `PRODUCTION_SUMMARY/EP07_SCHLAFPARALYSE_V4/PRODUCTION_GUIDE_V4.md`
- `PRODUCTION_SUMMARY/EP08_SCHLAFPARALYSE_V4/PRODUCTION_GUIDE_V4.md`

## What “production ready” means here
All creative/structural inputs are locked. Actual voice MP3/WAVs, generated images, synthesized music/SFX stems, subtitles and final renders are runtime outputs and are intentionally created locally/API-side rather than stored in Git.
