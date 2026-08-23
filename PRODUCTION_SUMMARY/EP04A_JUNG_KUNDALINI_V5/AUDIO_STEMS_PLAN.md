# EP04A — Audio / Stems Plan V5

**Principle:** the soundtrack must make the boundary between historical reality and inner imagery audible without turning the episode into horror or meditation music.

## Voice

- 12 performance-oriented source stems
- George, episode-specific starting profile in `voice/voice_batch.json`
- each raw stem normalized to approximately `-18 LUFS` / `<= -2 dBTP` for the working VO master
- per-stem pause suggestions come from `voice/voice_timing.json`; they are starting points and may move after listening
- no scene is stretched to a target minute

## Project-owned music stems

### `EP04A_MX_GROUND.wav`
Low, organic foundation. Slow pressure rather than a beat. Stronger when the story enters 1913 and the cave; thinner in archive/document sections.

### `EP04A_MX_AIR_METAL.wav`
Sparse upper-mid resonances, soft metal/glass partials and air between 700–2600 Hz so the score remains audible on phones. This carries mystery without a constant low drone.

### `EP04A_MX_PULSE.wav`
A restrained irregular pulse used selectively when the story becomes structured: seminar, map, historical movement. It should disappear completely around the two-second smartphone pause.

### `EP04A_MX_MASTER.wav`
Premix of the three music layers before VO ducking. Do not bake SFX into it.

## SFX / atmosphere stems

### `EP04A_SFX_INNER_WATER.wav`
Non-naturalistic but believable dark-water movement for flood/cave transitions. Never a loud disaster wave.

### `EP04A_SFX_CAVE_RESONANCE.wav`
Sparse mineral/metal resonances and long room decay for the inner landscape. No voices with intelligible words.

### `EP04A_SFX_ARCHIVE_ROOM.wav`
Dry room tone for seminar/clinic/archive reality resets.

### `EP04A_SFX_PAPER_PROJECTOR.wav`
Paper edges, page handling, subtle mechanical projection/slide texture where real source material appears.

### `EP04A_SFX_BODY_MICRO.wav`
Very restrained breath, cloth, chair and finger-contact textures in Manipura/Anahata and the viewer experiment. No heartbeat cliché unless the actual edit genuinely needs one short beat.

### `EP04A_SFX_PHONE_PAUSE.wav`
Room-tone stem specifically shaped so the two-second non-action can become almost empty without dropping into digital silence. No branded phone notification.

### `EP04A_SFX_PAULI_HANDOFF.wav`
One short dry tonal/mechanical impulse for the Pauli reveal. It should feel like the story changes domain, not like a trailer sting.

## Scene behavior

- S1: tension from air/metal + sparse ground; source reveal stays intelligible.
- S2: reality train/clinic dry; inner flood opens low-frequency space.
- S3: the most spacious inner-world sound; do not over-score Philemon.
- S4: hard dry reset to seminar; pulse can appear.
- S5: body textures replace large cinematic sound.
- S6: score gradually thins; around `du schreibst zwei Sekunden lang nichts` use room/body micro only.
- S7: dry investigative pulse + paper mechanics; history is a reveal, not a climax boom.
- S8: return to air/water residue, then cut cleaner for Pauli.

## Mix / delivery

Technical delivery remains fixed even though dramaturgic timing is flexible:
- final integrated loudness: `-14 LUFS +/-0.5`
- final true peak: `<= -0.8 dBTP`
- 48 kHz stereo final audio
- dialogue is always foreground
- music bed typically lives around the familiar NOESIS low level under narration, but automate by ear rather than chasing one number
