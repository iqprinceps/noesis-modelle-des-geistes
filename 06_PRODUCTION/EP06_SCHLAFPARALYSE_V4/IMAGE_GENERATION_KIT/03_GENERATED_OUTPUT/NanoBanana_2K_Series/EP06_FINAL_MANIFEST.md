# EP06 Final Visual Manifest

Finalized: 2026-08-24

| Asset class | Main pool | Reserve | Technical gate |
|---|---:|---:|---|
| MAIN stills (`IMG`) | 32 | 0 | 2560x1440 PNG |
| Insert stills (`SHOT`) | 8 | 0 | 2560x1440 PNG |
| Transformative Veo clips | 4 | 0 | 1920x1080, 24 fps, 6.00s, silent |
| Older camera/ambient clips | 0 | 4 | stored only in `RESERVE_CLIPS/` |
| Editor cards | 7 | 0 | stored in sibling `../CARDS/` |

## QA summary

- Core stills present: 40/40
- Redesign replacements: 23
- Duplicate core stills: 0
- Names beginning with `EP06`: 0
- Visible bed/bedroom/lab-bed frames: 10/40 (limit 10, PASS)
- Average still luminance: 81.88/255
- Minimum still luminance: 46.05/255
- Visual review: complete
- Main Veo clips: 4/4, all motif/state transformations rather than camera-only moves

Authoritative detail:

- Stills and ordering: `EP06_SHOT_SEQUENCE.csv`
- Technical still QA and hashes: `EP06_SHOT_QA.json`
- Contact sheets: `QA_CONTACT_SHEETS/`
- Veo review and context labels: `VEO_CLIP_LOG.md`
- Veo start/mid/end contacts: `VEO_QA_FRAMES/`
- Prompt overrides: `../../01_PROMPTS/REDESIGN_PROMPT_BATCH.md`
- Diversity decisions: `../../DIVERSITY_AUDIT.md`

