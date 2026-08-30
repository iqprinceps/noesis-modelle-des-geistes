# EP12_EN — Codex Handoff

## Goal

Acquire, verify and integrate the **full original-asset research set** for EP12 without committing large binaries to Git. Store production media in the external production storage and update repository manifests with provenance, hashes, dimensions, rights snapshots and technical QA.

The detailed source/rights/use inventory is now in:

- `02_SOURCES/ASSET_RESEARCH_CATALOG.md`
- `02_SOURCES/ORIGINAL_ASSET_MANIFEST.csv`

These two files are canonical for acquisition.

## Acquisition policy

### GREEN assets
Download into the appropriate `originals/` subfolder only after the source page and exact license are captured. Preserve attribution metadata and a rights snapshot.

### YELLOW / RIGHTS_VERIFY assets
Download only into `reference_only/`. Do **not** promote into edit-approved storage until permission or a clear reuse basis is documented.

### RED / restricted assets
Do not download as production artwork unless the rights basis has been explicitly cleared. Use bibliographic/editor-created cards or generated reconstruction instead.

## Tier-1 acquisition queue — acquire and QA first

1. Dean et al. 2019 full PDF.
2. Dean Figures 1, 2, 3 and 4 from publisher originals.
3. Timmermann et al. 2018 full PDF and relevant comparison table/page.
4. Rick Strassman CC BY portrait from Commons.
5. Robin Carhart-Harris CC BY-SA portrait from Commons.
6. DMT, tryptamine, tryptophan and serotonin vector structures.
7. CC BY-SA cerebral microdialysis schematic.
8. CC0 pineal gland infographic.
9. Descartes public-domain pineal/nervous-system diagram(s).
10. Wellcome tantric/chakra manuscript CC BY.
11. Leadbeater 1927 chakra plates and nervous-plexi diagram (public-domain record to be archived).
12. Ajna CC0 icon.
13. Human DMT fMRI/EEG CC BY figures listed in the asset catalog.
14. Human near-death EEG CC BY figures listed in the asset catalog.
15. Barker et al. 2013 PubMed bibliographic record/source card.

## Tier-2 reference acquisition — rights unresolved

Place in `reference_only/` with source HTML/screenshot and rights note:

- Jimo Borjigin official University of Michigan portrait.
- Jon G. Dean UC San Diego portrait candidate.
- Christopher Timmermann Imperial portrait and laboratory images.
- Michael M. Wang official portrait.
- Borjigin + Mashour laboratory photograph if original institutional provenance can be confirmed.
- NCI pineal illustration.
- Borjigin & Liu 2008 microdialysis figures unless exact article reuse rights are confirmed.
- Barker 2013 article figures unless exact reuse rights are confirmed.

## Highest-value story assets

### Central experimental reveal
`EP12_SRC_DEAN_FIG4`
- retain publisher original;
- retain complete PDF page/caption context;
- generate no editorial crop until the research master is stored;
- verify no third-party credit overrides the article CC license;
- picture function: pineal-intact vs pinealectomized rats, baseline vs cardiac-arrest measurement.

### Distributed-biology reveal
`EP12_SRC_DEAN_FIG1`, `EP12_SRC_DEAN_FIG2`, `EP12_SRC_DEAN_FIG3`
- preserve complete captions;
- use Figure 1 for rat/human INMT transcript context;
- Figure 2 for real microscopy / enzyme-location context;
- Figure 3 only as secondary widening beyond the brain.

### Human-experience bridge
`EP12_SRC_TIMMERMANN_PDF`
- archive full paper;
- extract complete relevant comparison table/page;
- do not present phenomenological overlap as causal proof.

### Human DMT measurements
Acquire the Timmermann 2023 fMRI/EEG Commons figures listed in the catalog.
- These are **administered DMT** studies.
- They must never be cut so that the viewer thinks they show endogenous DMT at death.

### Human near-death physiology
Acquire the near-death EEG Commons figures listed in the catalog.
- These are useful as visual answers to “what can actually be measured in a dying human brain?”
- They **do not measure DMT**.

### Historical/esoteric layer
Acquire Descartes, Wellcome tantric manuscript, Leadbeater plates/plexi and Ajna icon.
- Keep these under `originals/history/` and `originals/esoteric/`.
- Do not mix them into `originals/science/`.
- Every edit cue must preserve whether the image is historical science, esoteric history or modern evidence.

## External storage layout

`NOESIS/EP12_PINEAL_04/originals/science/`  
`NOESIS/EP12_PINEAL_04/originals/portraits/`  
`NOESIS/EP12_PINEAL_04/originals/history/`  
`NOESIS/EP12_PINEAL_04/originals/esoteric/`  
`NOESIS/EP12_PINEAL_04/extracts/`  
`NOESIS/EP12_PINEAL_04/generated/`  
`NOESIS/EP12_PINEAL_04/reference_only/`  
`NOESIS/EP12_PINEAL_04/rights/`  
`NOESIS/EP12_PINEAL_04/qa/`

## Manifest updates required after acquisition

Update `02_SOURCES/ORIGINAL_ASSET_MANIFEST.csv` with:

- exact resolved source page;
- exact resolved original/download URL;
- external/local storage path;
- SHA-256;
- file size;
- raster dimensions or SVG/PDF metadata;
- PDF page count where applicable;
- creator/institution/date;
- exact verified license string and license URL;
- rights/provenance snapshot path;
- acquisition date;
- `QA_PASS` only after source identity, technical integrity, rights basis and editorial claim limit are checked.

## Technical QA

- PDFs open without error and page count matches publisher version.
- SVGs render correctly and are retained as vectors in the research master.
- Raster originals are not replaced by low-resolution screenshots when a direct file exists.
- Full-page/document masters are retained beside crops.
- No figure labels or captions are silently removed from the research master.
- Attribution strings are recorded for CC BY / CC BY-SA assets.
- Public-domain rationale from Commons is archived, especially for historical works.
- Rights-unclear portraits never enter approved originals by accident.
- No generated reconstruction uses an `EP12_SRC_*` identifier.

## Script/claim alignment QA

Before voice/picture lock verify:

- DMT measured in **rat visual cortex**, not a generic human brain.
- Pinealectomized baseline DMT remained detectable in the reported experiment.
- Cardiac-arrest increase remains tied to the rat experiment and its method.
- INMT human evidence is transcript localization, not direct terminal human-DMT measurement.
- Timmermann 2018 is phenomenological overlap, not a causal mechanism.
- Timmermann 2023 brain figures are administered-DMT data.
- Near-death EEG figures are terminal-brain electrophysiology and do not measure DMT.
- Descartes / tantric / Leadbeater / Ajna imagery is historical or symbolic, never modern scientific evidence.

## Git policy

Commit scripts, prompts, manifests, rights/provenance records, cue sheets, source URLs and production notes. Keep large PDFs, images, audio and rendered media in external production storage unless a separate explicit Git LFS decision is made.
