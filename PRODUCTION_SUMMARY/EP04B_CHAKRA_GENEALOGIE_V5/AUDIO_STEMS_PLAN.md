# EP04B — Audio / Stems Plan V5

**Principle:** EP04B should sound like a historical object being examined layer by layer: dry, material, precise. It is less dreamlike than EP04A and should not inherit EP04A's cave/water palette.

## Voice

- 10 reveal-oriented source stems
- George with the tighter episode-specific profile in `voice/voice_batch.json`
- working VO normalization around `-18 LUFS`, true peak `<= -2 dBTP`
- per-stem gaps are starting points only; evidence chains should remain continuous when the read works better that way

## Project-owned music stems

### `EP04B_MX_DRY_PULSE.wav`
Sparse low-mid investigative pulse with irregular spacing. No trailer bass and no clock cliché.

### `EP04B_MX_PAPER_TONE.wav`
Soft filtered noise and page-like friction that can sit underneath document reveals without sounding like literal Foley every second.

### `EP04B_MX_HARMONIC_THREAD.wav`
Thin upper-mid tonal line that survives phone speakers and creates continuity while visual systems change. Less mystical than EP04A's air/metal layer.

### `EP04B_MX_MASTER.wav`
Music premix only, before VO ducking.

## SFX / atmosphere stems

### `EP04B_SFX_PAGE_PRINT.wav`
Page turns, letterpress/ink/mechanical details for Serpent Power and archival transitions.

### `EP04B_SFX_LAYER_PEEL.wav`
Very restrained paper/acetate separation sounds for the modern-map peel and final seams. No whoosh.

### `EP04B_SFX_ARCHIVE_ROOM.wav`
Quiet library/reading-room/lecture-room bed.

### `EP04B_SFX_TYPE_MOTION.wav`
Tiny dry ticks for `SECHS`, dates, names and motion labels. Avoid UI-beep aesthetics.

### `EP04B_SFX_ROUTE_PAPER.wav`
Subtle paper movement and one or two neutral transport/mechanical textures for Calcutta → London / text-travel beats.

### `EP04B_SFX_FINAL_SEAMS.wav`
Low-level acetate/paper friction and room tone for the final layered-map close. No dramatic resolution chord.

## Scene behavior

- S1: dry modern texture → sudden absence/peel when the rainbow disappears.
- S2: light archive tone; move quickly.
- S3: reduce pulse and let real historical images carry the strangeness.
- S4: paper/print/route mechanics; avoid spy-thriller coding.
- S5: clean reset; Leadbeater reveal uses plate color and voice, not supernatural sound.
- S6: pulse/thread can accumulate as layers accumulate, then thin before the second turn.
- S7: warmer harmonic thread; this is cultural explanation, not exposure.
- S8: mostly paper/room material, quiet final seam sound, then black.

## Mix / delivery

- final integrated loudness: `-14 LUFS +/-0.5`
- final true peak: `<= -0.8 dBTP`
- 48 kHz stereo final audio
- dialogue always foreground
- no fixed music intensity curve; automate by the actual final read and document reveals
