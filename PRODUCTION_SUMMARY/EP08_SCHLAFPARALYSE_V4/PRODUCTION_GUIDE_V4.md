# EP08 — Production Guide V4

**Status:** READY FOR PRODUCTION INPUTS  
**Episode:** Schlafparalyse III — Der Mann mit dem Hut  
**Canonical script:** `03_EPISODEN/TYPE_B/EP08_SCHLAFPARALYSE_03/DREHBUCH.md`  
**Clean voice:** `PRODUCTION_SUMMARY/EP08_SCHLAFPARALYSE_V4/07_VOICE_SCRIPT_CLEAN_V4.txt`

## Prepared
- final voice-authentic script + claims lock
- verified asset package / downloader / rights traffic lights
- V4 Nano Banana prompt package with exact reference filenames
- clean master transcript + 8 voice source stems
- ElevenLabs batch config
- Audio/Stems Plan
- Motion Graphics spec
- Visual Cue Sheet
- Thumbnail + 20 s Endcard spec

## 1. Prepare local tree
```bash
python3 tools/prepare_schlafparalyse_production_inputs.py
```
This also unpacks the committed V4 image-prompt ZIP safely.

## 2. Download source assets
```bash
cd 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2
python3 download_schlafparalyse_assets.py
```
Review YELLOW assets before use. RED files remain research-only.

## 3. Voice generation
From repo root:
```bash
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP08_SCHLAFPARALYSE_V4/voice/voice_batch_v4.json --execute
python3 tools/schlafparalyse_voice.py EP08 all
```
Before the full batch, pronunciation-test: Art Bell, Coast to Coast AM, Heidi Hollis, John E. Mack, Susan Clancy, Richard McNally, Diphenhydramin, Rodney Ascher.

## 4. Images
Use `03_EPISODEN/TYPE_B/EP08_SCHLAFPARALYSE_03/NANOBANANA_GUIDE_V4.md` and the four S1–S8 batch files. Generate style anchors first. MAIN/RESERVE prompts are coverage, not a mandate to use every frame.

## 5. Edit targets
- 140–155 shots
- average ~3.5–4.5 s
- no still >9 s
- >=85 unique motifs
- no repeat inside same act
- 3–5 motion clips/graphics
- AI reconstruction <=65% where archival material exists
- time follows the final spoken voice, not hard act timestamps

## 6. Audio
Follow `AUDIO_STEMS_PLAN.md`. Keep dialogue dominant. Music/SFX are project-owned/runtime-generated; no third-party licensed track is required.

## 7. Subtitles
Create SRT from final forced alignment; <=84 characters/block.

## 8. Export
- 1920x1080, 30 fps
- H.264 High, yuv420p / TV range
- AAC stereo 48 kHz 320 kbps
- `-14 LUFS +/-0.5`, true peak `<= -0.8 dBTP`
- endcard exactly 20 s

## Runtime outputs intentionally not committed
- ElevenLabs MP3 stems
- normalized VO WAV/master + forced alignment JSON
- generated AI images/style anchors
- synthesized music/SFX WAV stems
- final timeline/render/SRT/thumbnail render

No creative or structural decision is required before starting these jobs. Replacement decisions after generation are normal QA.
