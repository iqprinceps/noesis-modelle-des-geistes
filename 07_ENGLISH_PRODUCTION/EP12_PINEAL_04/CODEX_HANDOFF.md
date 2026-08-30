# EP12_EN — Codex Handoff

## Goal

Acquire, verify and integrate the original scientific media for EP12 without committing large binaries to Git. Store media in the external production storage and update repository manifests with provenance, hashes and technical QA.

## Acquisition queue

1. `EP12_SRC_DEAN_PDF`
   - Download: https://www.nature.com/articles/s41598-019-45812-w.pdf
   - Archive full PDF.
   - Capture publisher rights/license statement.
   - Compute SHA-256.
   - Record file size and page count.

2. `EP12_SRC_DEAN_FIG1`
   - Extract Figure 1 from the archived Dean PDF at maximum available quality.
   - Preserve a full-page p. 2 capture as documentary context.
   - Verify figure has no separately credited third-party material.

3. `EP12_SRC_DEAN_FIG4`
   - Extract Figure 4 from the archived Dean PDF at maximum available quality.
   - Preserve a full-page p. 5 capture before editorial crops.
   - Figure function: central evidence reveal for pineal-intact vs pinealectomized rats and cardiac-arrest change.

4. `EP12_SRC_TIMMERMANN_PDF`
   - Download: https://www.frontiersin.org/articles/10.3389/fpsyg.2018.01424/pdf
   - Archive full PDF.
   - Capture the explicit CC BY rights statement from Frontiers.
   - Compute SHA-256.

5. `EP12_SRC_TIMMERMANN_TABLE1`
   - Extract the complete relevant table/page.
   - Keep title/caption/source visible in the research master.
   - Use only as phenomenology-comparison evidence.

6. `EP12_SRC_STRASSMAN_BOOK`
   - Do not acquire/reproduce a book scan unless legal source and reproduction basis are clear.
   - If the production wants a direct quote, verify exact edition, page and wording first.
   - Otherwise use bibliographic/editor-created context rather than a scan.

## External storage layout recommendation

`NOESIS/EP12_PINEAL_04/originals/`  
`NOESIS/EP12_PINEAL_04/extracts/`  
`NOESIS/EP12_PINEAL_04/generated/`  
`NOESIS/EP12_PINEAL_04/rights/`  
`NOESIS/EP12_PINEAL_04/qa/`

## Manifest updates

Update `02_SOURCES/ORIGINAL_ASSET_MANIFEST.csv` after acquisition with:

- exact local/external path;
- SHA-256;
- dimensions for extracted raster assets;
- PDF page count / file size where relevant;
- verified license text or rights basis;
- acquisition date;
- status `QA_PASS` only after the source identity and technical file are checked.

## Technical checks

- PDF opens without error and page count matches publisher version.
- Raster extraction has no interpolation artifacts or missing labels.
- No screenshot is silently substituted for a higher-quality extract when the original figure is available.
- Full-page documentary master retained alongside any crop.
- Attribution source line is preserved in edit metadata.
- Generated reconstructions use filenames from `03_VISUALS/IMAGEGEN_PROMPTS.md` and are never stored under `EP12_SRC_*` IDs.

## Script alignment checks

Before final voice lock, verify these beats against the source master:

- DMT measured in **rat visual cortex**, not a generic human brain.
- Pinealectomized baseline DMT remained detectable.
- Cardiac-arrest increase is tied to the experiment and species.
- No significant post-arrest concentration difference between pineal-intact and pinealectomized groups is described beyond the study's reported comparison.
- INMT human evidence is transcript localization, not direct measurement of human-brain DMT production or terminal release.
- Timmermann is phenomenological overlap, not causal mechanism.

## Git policy

Commit scripts, prompts, manifests, rights/provenance text, cue sheets and production notes. Keep large PDFs, images, audio and rendered media in external production storage unless a separate explicit Git LFS decision is made.
