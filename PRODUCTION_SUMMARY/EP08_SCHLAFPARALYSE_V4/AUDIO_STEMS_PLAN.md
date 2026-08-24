# EP08 — Audio / Stems Plan

**Status:** PRODUCTION LOCK  
**Voice:** George / ElevenLabs multilingual v2 / speed 1.06

## Voice
- Voice ID: `JBFqnCBsd6RMkjVDRZzb`
- stability `0.58` / similarity `0.80` / style `0.08` / speed `1.06` / speaker boost `true`
- 8 source stems under `voice/source/`
- raw outputs under `voice/raw_stems/`
- normalize VO to about `-18 LUFS integrated`, `<= -2 dBTP`
- final VO master: `EP08_SCHLAFPARALYSE_V4_VO_MASTER.wav`
- 48 kHz mono PCM24 working master

## Music stems
No licensed third-party music is required. Build the bed from project-owned synthesis.

Required:
- `EP08_MX_LOW.wav` — low foundation; keep narration clear
- `EP08_MX_HARMONIC.wav` — sparse audible texture for phone speakers
- `EP08_MX_NOISE.wav` — restrained room/noise layer
- `EP08_MX_MASTER.wav` — premix before VO ducking

Relative act energy:
- S1: `0.94`
- S2: `0.76`
- S3: `0.78`
- S4: `0.70`
- S5: `1.00`
- S6: `0.88`
- S7: `0.96`
- S8: `0.72`

Normal narration bed around `-30 LUFS`; smooth ducking; no pumping. Let music rise only in deliberate pauses/reveals.

## SFX / atmosphere
- `EP08_SFX_RADIO_ROOM.wav` — late-night radio room tone, analog console/air, no branded ident
- `EP08_SFX_SHORTWAVE_STATIC.wav` — kurze kontrollierte Radio-Static-Textur
- `EP08_SFX_FAX_PAPER.wav` — glaubwürdige Fax-/Papierbewegung für 4.500-Reaktionsbeat
- `EP08_SFX_CRT_ROOM.wav` — leises CRT-/PC-Raumgefühl, keine überzeichneten Modemtöne
- `EP08_SFX_FORUM_UI.wav` — neutrale kleine Interface-Ticks, keine Marken-Sounds
- `EP08_SFX_SHADOW_ROOMTONE.wav` — stiller Schlafzimmer-Raumton; Hat Man ohne Horror-Sting

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
