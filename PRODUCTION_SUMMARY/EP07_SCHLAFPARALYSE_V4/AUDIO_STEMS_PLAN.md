# EP07 — Audio / Stems Plan

**Status:** PRODUCTION LOCK  
**Voice:** George / ElevenLabs multilingual v2 / speed 1.06

## Voice
- Voice ID: `JBFqnCBsd6RMkjVDRZzb`
- stability `0.58` / similarity `0.80` / style `0.08` / speed `1.06` / speaker boost `true`
- 8 source stems under `voice/source/`
- raw outputs under `voice/raw_stems/`
- normalize VO to about `-18 LUFS integrated`, `<= -2 dBTP`
- final VO master: `EP07_SCHLAFPARALYSE_V4_VO_MASTER.wav`
- 48 kHz mono PCM24 working master

## Music stems
No licensed third-party music is required. Build the bed from project-owned synthesis.

Required:
- `EP07_MX_LOW.wav` — low foundation; keep narration clear
- `EP07_MX_HARMONIC.wav` — sparse audible texture for phone speakers
- `EP07_MX_NOISE.wav` — restrained room/noise layer
- `EP07_MX_MASTER.wav` — premix before VO ducking

Relative act energy:
- S1: `0.92`
- S2: `0.72`
- S3: `0.66`
- S4: `0.82`
- S5: `0.72`
- S6: `0.88`
- S7: `1.00`
- S8: `0.70`

Normal narration bed around `-30 LUFS`; smooth ducking; no pumping. Let music rise only in deliberate pauses/reveals.

## SFX / atmosphere
- `EP07_SFX_SALEM_ROOMTONE.wav` — kleiner Holzraum, Stoff, ferne Bewegung; keine Hexenfilm-Kulisse
- `EP07_SFX_PAPER_INK.wav` — Papier, Feder, trockene Seitenbewegung für Originalakten
- `EP07_SFX_WOOD_BED.wav` — sehr dezentes Holz-/Bettgeräusch für Coman-Rekonstruktion
- `EP07_SFX_COURT_MURMUR.wav` — kurzer niedriger Raum-Murmur, nicht dramatisch aufladen
- `EP07_SFX_MAP_MOTION.wav` — kleine neutrale Ticks/Swishes für Kulturkarte
- `EP07_SFX_MEDIA_HANDOFF.wav` — subtile Radio-/Leitungstextur für Übergang zu EP08

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
