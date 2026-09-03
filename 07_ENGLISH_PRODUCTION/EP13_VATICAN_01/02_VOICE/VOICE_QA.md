# EP13_EN — Voice QA

Produced 2026-09-03 with `tools/produce_ep13_en_voice.py`, adapted from the
pipeline that produced the published EP05 master.

## Master

| | |
|---|---|
| Narrator | George, ElevenLabs `JBFqnCBsd6RMkjVDRZzb` |
| Model | `eleven_multilingual_v2` |
| Profile | EP05_EN candidate A reused: stability 0.61, similarity 0.82, style 0.06, speed 1.0, speaker boost on |
| Seed | 260827 |
| Stems | 8, concatenated with 0.34 s gaps |
| Duration | **8:08** narration only |
| Loudness | −18.06 LUFS integrated, true peak −2.00 dBTP, LRA 2.2 |
| File | `MASTER/EP13_EN_VO_MASTER.wav`, 48 kHz mono, 24 bit |

The delivery profile was reused rather than re-auditioned. Same narrator, same
channel, and EP05's brief, intimate and restrained, is close to EP13's calm and
immediate. **The aesthetic judgement on the read is the channel owner's**, since
it cannot be settled by measurement.

## Rate correction

The narration runs at **166 words per minute**, not the 148 used in the planning
tables. Both figures are correct for different things: 148 came from finished
videos and therefore absorbs music beds, act pauses and the end-screen window,
while 166 is the raw read.

For EP13 the gap is about one minute. Narration is 8:08 and the finished cut
should land near 9:00 once card holds and the end-screen window are added. The
series runtime table in `VATICAN_SERIES_RETENTION_ARCHITECTURE.md` was built
against finished-video rates and still stands, but it should be re-checked
against each master as it is produced rather than trusted forward.

## Content QA

Independent pass with `scribe_v2`: the master is transcribed blind and the
transcript is diffed against the canonical script, so an error in the read shows
up as a mismatch rather than relying on listening.

Sequence similarity **0.985999**, 15 deviations, automated status `REVIEW`
because the gate wants 0.992 and at most four.

All fifteen are orthographic normalisation by the transcriber, not speech errors:

| Deviation | Count | What it is |
|---|---:|---|
| `thirteenth` → `13th`, `third` → `3rd`, `eighteenth` → `18th` | 6 | ordinals written as digits |
| `eighty three` → `83`, `eighty one` → `81`, `five hundred` → `500` | 4 | numbers written as digits |
| `the twenty third` → `xxiii`, `the sixth` → `vi` | 2 | spoken ordinals written back as roman numerals |
| `saint` → `st` | 1 | abbreviation |
| `lay people` → `laypeople` | 1 | compounding |
| `recognises` → `recognizes`, `travelled` → `traveled` | 2 | transcriber uses US spelling |

**Human verdict: PASS.** Zero speech errors. The automated `REVIEW` status is the
gate reacting to transcriber orthography, and the gate is right to flag rather
than guess.

## One real error, found and fixed

The first master read **John XXIII as "John the Thirteenth"**. The forced-alignment
transcript showed `John XIII`, which is how the mistake surfaced: a pope's name
read wrong by ten numerals.

Fixed by spelling the ordinals out in the voice script, `John the Twenty-Third`
and `Paul the Sixth`, and regenerating. The transcript now returns `John XXIII`,
which confirms the correct reading. The pronunciation sheet already required this
delivery; the script simply had not been written to enforce it.

**Rule for the remaining episodes: never leave a roman numeral in a voice script.**
EP14 through EP17 must be swept for `Clement VII`, `Paul V`, `Henry VIII`,
`Alfonso V`, `Eugene IV`, `Pius IV`, `Paul IV` and `Canon 1172` before their
masters are generated.

## Alignment

`ALIGNMENT/EP13_EN_VO_ALIGNMENT.json`, word-level timings from the ElevenLabs
forced-alignment endpoint against the canonical script and the master hash. This
is the timing spine for the cue sheet: every one of the 88 visual states binds to
a spoken word range, not to an estimate.
