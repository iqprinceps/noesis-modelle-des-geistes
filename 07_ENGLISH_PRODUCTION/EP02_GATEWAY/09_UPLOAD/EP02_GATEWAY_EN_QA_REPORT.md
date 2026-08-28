# EP02_EN Production QA Report

QA date: 2026-08-26  
Editorial status: PASS  
Publication status: CONDITIONAL — restricted archive portraits require clearance

## Voice, script, and alignment

- Canonical English script: `../01_SCRIPT/VOICE_SCRIPT_EN.txt`; every substantive
  revision is recorded in `../01_SCRIPT/SCRIPT_CHANGELOG.md`.
- Recommendation H arrives in the planned hook at approximately 13.74 seconds.
- Two identical-excerpt auditions were made. Candidate A (George,
  `eleven_multilingual_v2`, stability 0.58, similarity 0.80, style 0.08,
  speed 1.06) was selected. Candidate B remains audition-only.
- Only one full master was generated: `../04_VOICE/MASTER/GW_EN_VO_MASTER.wav`,
  481.037 seconds, 48 kHz mono PCM24, -18.02 LUFS, -2.00 dBTP.
- Scribe v2 forced/content alignment similarity: 0.992298. All locked names and
  terms were detected. No pickup was required.
- Cue sheet, EDL, SRT, and VTT end on the selected master and are mutually timed
  to the same 481.037-second source.

## Picture-lock metrics

| Test | Result |
|---|---:|
| Actual edit shots | 124 |
| Actual contiguous asset runs | 124 |
| Distinct semantic motifs / selected exports | 124 |
| Still/image selections | 115 |
| Motion selections | 9 |
| Asset return after an interruption | 0 — PASS |
| Exact content-hash repeats | 0 — PASS |
| Near repeats, 64-bit DCT pHash distance ≤2 | 0 — PASS |
| Cross-episode exact collisions found | 0 — PASS in current worktree |
| Cross-episode near collisions found | 0 — PASS in current worktree |
| Visible mode badges | 0 — PASS |
| Longest static hold | 7.625 s — PASS |
| Longest overall hold | 10.735 s |
| Unjustified holds over 10 s | 0 — PASS |

Top repetitions: none. Repeat Count: 0.

EP01 has no final media exports in this worktree. The shared registry therefore
confirms zero currently testable collisions and must be rerun if EP01 finals are
later merged or copied into this checkout. Every EP02 selection is marked
`series_usage=EP02_ONLY`.

## Holds at or above 8 seconds

1. `GW-SHOT-001`, 10.735 s, `GW_EN_CLIP01_THREE_TIMES_RECOMMENDATION_H.mp4`:
   accepted because the hook visibly advances through six protocol stages—three
   observers, target, present/past/future positions, then comparison—and consumes
   one continuous source pass without restart. This is not a static zoom.
2. `GW-SHOT-077`, 8.860 s, `GW_EN_CLIP07_TEN_DIGITS.mp4`: accepted because the
   procedure visibly progresses from number placement to blinding to partial
   retrieval and the explicit incomplete result, with no repeated source range.

No static hold reaches the 8-second review line.

## Semantic and factual visual checks

- McDonnell is introduced on his authentic signature block. A later anonymous,
  from-behind reconstruction is not asserted to be his likeness.
- Monroe is introduced with an authentic Monroe Institute portrait and then
  distinct laboratory sources; no portrait returns after a cut.
- Bentov is introduced with the sourced historical portrait, followed by a
  separate object/model context.
- Flight 191 is anchored by the NTSB accident report, route map, and government
  crash-site image.
- Fort Meade first appears as a geographic map. The later Ken Lund photograph is
  explicitly contemporary context, not a 1983 archive claim.
- Army authorship and CIA archive/declassification provenance are separated in
  narration, document crop, archive-chain motion, and card copy.
- Recommendation H, binaural-beat arithmetic, acoustics-to-cosmology transition,
  Focus states, ten-digit procedure, Recommendations J/K, and PEAR handoff each
  have a dedicated, non-returning visual sequence aligned to their voice beat.
- Abstract/subjective imagery contains no `INNER / HYPOTHESIS` label and makes no
  claim of documentary evidence.

## Clip QA

All selected clips were reviewed at beginning, midpoint, and end.

- Veo accepted: `GW_EN_CLIP03_MONROE_EXIT.mp4`, `GW_EN_CLIP05_CROSSING.mp4`,
  `GW_EN_CLIP06_FOCUS_WHEEL.mp4`.
- Veo rejected: `GW_EN_CLIP09_NONPHYSICAL_DOCTRINE.mp4`; the midpoint formed a
  literal smoky figure and failed the ambiguity requirement. It is isolated in
  `../03_VISUALS/REJECTED/VEO/` and not selected.
- Replacement: `GW_EN_CLIP09_NONPHYSICAL_PRESENCE_SAFE.mp4`, controlled
  code-native motion from the accepted source still; the empty perimeter changes
  through environmental response without forming a body or face.
- Code-native clips 01, 02, 04, 07, and 10 pass first/middle/final continuity,
  legibility, geometry, and single-pass checks.

## Visual inspection and rejection criteria

The final hook sheet, 20-second whole-episode coverage sheet, mobile card proof,
archive sheet, Vertex still sheet, and both clip sheets were inspected. No
selected visual shows malformed identity/anatomy, invented readable historical
text, wrong map geometry, visible production labels, or a style break severe
enough to reject. Historical documents are raster extracts of acquired originals;
code cards do not imitate historical paperwork.

## Rights gate

The Army/CIA memorandum, NTSB report and imagery, and Census map data have
government-source provenance. Fort Meade is CC BY-SA 2.0 with attribution and a
contemporary-date caveat. Monroe imagery is listed CC BY-NC-ND 4.0 and needs
permission review for monetized use. The Bentov portrait is copyrighted with a
fair-use rationale at its source and needs episode-specific legal review or a
cleared replacement. These two issues block an unconditional publication-ready
claim, but not timeline assembly or internal review render.

Machine-readable evidence: `GW_EN_PICTURE_LOCK_HASH_REGISTRY.csv` and
`../03_VISUALS/QA/GW_EN_PICTURE_LOCK_QA.json`.
