# EP06 — Audio / Stems Plan

**Status:** PRODUCTION LOCK  
**Voice:** George / ElevenLabs multilingual v2 / speed 1.06

## Voice
- Voice ID: `JBFqnCBsd6RMkjVDRZzb`
- stability `0.58` / similarity `0.80` / style `0.08` / speed `1.06` / speaker boost `true`
- 8 source stems under `voice/source/`
- raw outputs under `voice/raw_stems/`
- normalize VO to about `-18 LUFS integrated`, `<= -2 dBTP`
- final VO master: `EP06_SCHLAFPARALYSE_V4_VO_MASTER.wav`
- 48 kHz mono PCM24 working master

## Music stems
No licensed third-party music is required. Build the bed from project-owned synthesis.

Required:
- `EP06_MX_LOW.wav` — low foundation; keep narration clear
- `EP06_MX_HARMONIC.wav` — sparse audible texture for phone speakers
- `EP06_MX_NOISE.wav` — restrained room/noise layer
- `EP06_MX_MASTER.wav` — premix before VO ducking

Relative act energy:
- S1: `0.90`
- S2: `0.72`
- S3: `0.60`
- S4: `0.72`
- S5: `0.84`
- S6: `0.88`
- S7: `1.00`
- S8: `0.66`

Normal narration bed around `-30 LUFS`; smooth ducking; no pumping. Let music rise only in deliberate pauses/reveals.

## SFX / atmosphere
- `EP06_SFX_BEDROOM_ROOMTONE.wav` — sehr leiser dunkler Schlafzimmer-Raumton, keine Horror-Drohne
- `EP06_SFX_FOOTSTEPS_DISTANT.wav` — 2–3 glaubwürdige, trockene Schritte; nur punktuell S1/S6
- `EP06_SFX_MATTRESS_WEIGHT.wav` — dezentes Stoff-/Matratzenknarzen, kein Jump-Scare
- `EP06_SFX_SLEEP_LAB.wav` — klinischer Raumton, Lüftung/Kabel/Monitor sehr subtil
- `EP06_SFX_EEG_MOTION.wav` — kleine technische Ticks für REM-/EEG-Grafik; keine Sci-Fi-Beepfolge
- `EP06_SFX_BREATH_BODY.wav` — zurückhaltende Atem-/Körpertextur, niemals Atemnot dramatisieren

Forbidden across the trilogy:
- trailer booms / jump scares
- reversed choir / generic occult drones
- cyberpunk neon-sonic language
- branded phone/radio/UI sounds
- SFX that imply a supernatural entity is objectively present

## Final mix
- stereo 48 kHz AAC 320 kbps delivery audio
- integrated loudness `-14 LUFS +/- 0.5`
- true peak `<= -0.8 dBTP`
- dialogue remains foreground

## Export stems
Deliver separately: VO master, LOW, HARMONIC, NOISE and every required SFX file above. Final mix is derived from stems, not baked into VO.
