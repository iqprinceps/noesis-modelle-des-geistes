# EP05 Jung & Pauli V5 — Production Guide

**Status:** READY FOR PRODUCTION INPUTS  
**Episode source:** `03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/DREHBUCH.md`  
**Production transcript:** `07_VOICE_SCRIPT_CLEAN_V4.txt`  
**Timing rule:** no hard target runtime. Voice cadence and concentration determine the final duration; visuals follow text anchors.

---

## What is already prepared

### Editorial
- final V4 script / voice-authenticity lock
- 8-act retention structure
- viewer CTA `ZUFALL / ZEICHEN`
- EP06 handoff
- scientific/claim guardrails

### Image package
- `NANOBANANA_GUIDE_V5.md`
- `NANOBANANA_PROMPTS_V5_S1_S2.md`
- `NANOBANANA_PROMPTS_V5_S3_S4.md`
- `NANOBANANA_PROMPTS_V5_S5_S6.md`
- `NANOBANANA_PROMPTS_V5_S7_S8.md`
- total **64 MAIN + 8 RESERVE** complete prompts
- each image has exact filename, exact reference list and complete prompt
- `SOURCE_ASSET_DOWNLOAD_MAP_V5.md` with exact local source names
- `VISUAL_CUE_SHEET.csv` for story/text anchors
- `MOTION_GRAPHICS_V5.md` for explanatory graphics

### Voice package
- one clean master transcript
- 8 complete source stems
- `voice_batch_v4.json`
- George / multilingual v2 settings locked to NOESIS production standard
- `tools/ep05_voice.py` for normalization, VO master and forced alignment

### Audio package
- `AUDIO_STEMS_PLAN.md`
- music stem names and character
- SFX stem names and specific usage rules
- final loudness / true-peak targets

### Delivery
- thumbnail concept + full thumbnail prompt
- 20 s endcard specification
- export targets and QA below

---

# Production sequence

## 1. Download and archive original sources

Use:
`03_EPISODEN/TYPE_B/EP05_JUNG_PAULI/SOURCE_ASSET_DOWNLOAD_MAP_V5.md`

Download the six required references with **exact local filenames**:
- `SRC01_Wolfgang_Pauli_1924.jpg`
- `SRC03_Solvay_Conference_1927.jpg`
- `SRC05_Carl_Gustav_Jung_Portrait.jpg`
- `SRC06_ETH_Zuerich_Historical.jpg`
- `SRC07_Johannes_Kepler_Portrait.jpg`
- `SRC08_Cetonia_Aurata_Species.jpg`

Save the source page / license information next to them.

**Do not block production waiting for Jung–Pauli letter scans or a 1952 book scan.** Both have safe editorial fallbacks. A real scan enters the cut only after reproduction rights are explicitly cleared.

## 2. Style references

Use the existing EP05 style reference package:
`NANOBANANA_STYLE_REFERENZEN.md`

Required:
- `STYLE_CINEMATIC.png`
- `STYLE_CONCEPTUAL.png`
- `STYLE_INFOGRAPHIC.png` only if needed; most explanatory cards should be built in edit

Do not regenerate the style masters if the already approved files are available.

## 3. Generate images

Follow `NANOBANANA_GUIDE_V5.md`.

Recommended batch order:
1. S1–S2
2. S3–S4
3. S5–S6
4. S7–S8
5. reserves only where visual repetition or a weak generated frame creates a gap

The 64 MAIN images are a coverage pool, not a mandate to use every frame.

### Visual selection target
Combine:
- real archive/originals
- generated coverage frames
- motion/cards
- 3–5 small motion clips / animated graphics

Final target from NOESIS standard:
- ~140–155 shots
- average shot roughly 3.5–4.5 s
- no single still > 9 s
- >=85 unique visual motifs
- no visual repeat inside the same act
- max repeated use of a motif <=4 total
- AI/reconstruction <=65% where sufficient archival material exists

These are QA guardrails, **not reasons to stretch or shorten the narration**.

## 4. Generate voice stems

From repository root:

```bash
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/voice/voice_batch_v4.json --execute
```

Expected output:
`PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/voice/raw_stems/`

Before full batch, do a short pronunciation test for:
- C. G. Jung
- ETH Zürich
- Wolfgang Pauli
- Erna Rosenbaum
- J. B. Rhine
- Johannes Kepler
- Synchronizität

Do not insert phonetic spelling unless a real audible problem is confirmed.

## 5. Build VO master + alignment

```bash
python tools/ep05_voice.py all
```

Outputs:
- normalized PCM voice stems
- `EP05_JUNG_PAULI_V4_VO_MASTER.wav`
- forced-alignment JSON against `07_VOICE_SCRIPT_CLEAN_V4.txt`

The alignment is the time source for:
- subtitles
- visual cue anchors
- chapter boundaries

Do not type fixed timestamps back into the cue sheet before this exists.

## 6. Music / SFX

Follow `AUDIO_STEMS_PLAN.md`.

Required audio deliverables:
- VO master
- 3 music stems: LOW / HARMONIC / NOISE
- world-clock SFX
- paper/letter SFX
- beetle-window SFX
- phone notification
- room tones
- sleep-paralysis handoff

Music is self-synthesized / project-owned; no third-party music is required.

## 7. Motion and graphics

Build the cards from `MOTION_GRAPHICS_V5.md`.

Priority motions:
- `400`
- Patient → Briefpartner
- Inneres / Äußeres
- Eng / Weit
- Treffer / Nicht-Treffer
- `ZUFALL / ZEICHEN`
- Quantum Trap
- 1952 double reveal
- Ursache / Bedeutung

Graphics use German display text. Historical document wording remains original only when actually present on a real source.

## 8. Timeline / edit

Use `VISUAL_CUE_SHEET.csv` as **text-anchor story map**, not as a 37-shot timeline.

Each cue is a beat. Within a beat, choose 2–5 archive/generated/detail/motion views as needed to stay under the still-duration ceiling and maintain visual novelty.

### Edit rhythm
- Hook: world clock can breathe, but change crop/detail before it becomes static
- Pauli reveal: hard transition from dream to real portrait / Solvay world
- biography: no suicide reconstruction
- beetle: hold the small window event; do not score it like horror
- S5: keep diagrams concise, avoid lecture feeling
- S6: let CTA breathe
- S7: strongest document/graphic reveal of episode
- S8: slow down slightly, return to world clock, then dark bedroom handoff

### Source lines
Use two-line lower-left captions where useful:
1. German descriptor
2. source / license / reconstruction designation

Generated historical scenes: mark `Rekonstruktion` at first appearance when ambiguity with archive is possible.

## 9. Subtitles

Generate from final forced alignment.

- SRT
- blocks <=84 characters
- normal German spelling from clean transcript
- do not subtitle editorial labels that are not spoken unless required for accessibility

## 10. Endcard

Use `THUMBNAIL_ENDCARD_V5.md`.

- exactly 20 s
- next episode: Schlafparalyse I
- CTA: `ZUFALL ODER ZEICHEN?`
- reserve YouTube endscreen zones

## 11. Thumbnail

Primary concept: Pauli + world clock.

Run readability test at 246 px width before lock.

## 12. Final export

- 1920×1080
- 30 fps
- H.264 High
- yuv420p / TV range
- AAC stereo, 48 kHz, 320 kbps
- integrated loudness `-14 LUFS +/-0.5`
- true peak `<= -0.8 dBTP`

## 13. Technical QA

Check at minimum:
- no missing/black/broken segment
- yuv420p, no yuvj range switches
- every still <=9 s
- no same visual repeated in same act
- generated interior faces free of neon/cyan-magenta spill
- no fake archival document
- no quantum visualization implying synchronicity is proven physics
- captions aligned and <=84 chars/block
- endcard 20 s
- thumbnail legible at mobile size
- source/attribution list complete

---

# What is not pre-generated by this package

The package is **production ready**, not already rendered. The following are runtime outputs:
- 8 ElevenLabs MP3 voice files
- normalized VO WAV master
- alignment JSON
- 64 MAIN / optional 8 reserve generated images
- music and SFX WAV stems
- final timeline, rendered video, SRT, chapter timestamps, thumbnail render

No creative or structural decision is still required to start those jobs. Any replacement decision after generation is normal QA, not missing preproduction.