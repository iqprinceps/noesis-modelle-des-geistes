# EP12_EN — Codex Handoff

## Goal

Acquire, verify and integrate the **full original-asset research set** for EP12 without committing large binaries to Git. Store production media in external production storage and update repository manifests with provenance, hashes, dimensions, rights snapshots and technical QA.

Canonical acquisition documents:

- `02_SOURCES/URL_VERIFICATION_REPORT.md` — **live URL/content/rights audit; highest authority for what Codex may fetch**;
- `02_SOURCES/ORIGINAL_ASSET_MANIFEST.csv` — synchronized acquisition rows/statuses;
- `02_SOURCES/ASSET_RESEARCH_CATALOG.md` — editorial descriptions, use cases and claim boundaries.

## Acquisition rule after verification pass

### `VERIFIED_GREEN`
Download only from the verified source/download route in the synchronized manifest/report. Preserve source-page URL, creator, exact license and attribution.

### `VERIFIED_GREEN_EXTRACT`
Do **not** use an old standalone CDN image URL. Download the verified document master and extract the named figure/page from that master. This rule applies to Dean Figures 1–4 and the Timmermann 2018 table/page.

### `VERIFIED_SOURCE_ONLY`
Archive citation/source metadata as needed, but do not treat the article/page as freely reusable production artwork unless a specific media license is later documented.

### `VERIFIED_REFERENCE_ONLY`
May be stored only in `reference_only/` for reconstruction, permission outreach or editorial reference. Never promote to approved originals without a documented rights basis.

## Tier-1 acquisition queue — verified reusable assets

1. Dean et al. 2019 Nature PDF (`EP12_SRC_DEAN_PDF`).
2. Extract Dean Figures 1–4 from that verified PDF; retain full-page masters and captions.
3. Timmermann et al. 2018 Frontiers PDF + full relevant comparison table/page.
4. Rick Strassman CC BY portrait.
5. Robin Carhart-Harris full research-meeting photo, CC BY-SA.
6. DMT, **corrected public-domain tryptamine**, tryptophan and serotonin structures.
7. CC BY-SA cerebral microdialysis schematic.
8. CC0 pineal gland infographic.
9. Descartes public-domain diagram + Frans Hals Descartes portrait + CC BY Wellcome Descartes scan.
10. Wellcome tantric-body manuscript CC BY.
11. Leadbeater chakra plates, nervous-plexi diagram, crown/root plates and Leadbeater portrait.
12. Ajna CC0 icon + optional public-domain Eye of Providence.
13. Helena Blavatsky CC0 high-resolution portrait.
14. Human DMT fMRI/EEG Commons figures: static connectivity, dynamic connectivity, cortical gradient, EEG spectral/diversity/traveling-waves, parallel EEG/fMRI.
15. Human near-death EEG Commons figures: gamma power, synchrony, phase-amplitude coupling, cross-regional coupling and directed connectivity.

## Source/document queue — verified but not generic artwork

Archive citation/source metadata for:

- Dean PMC mirror;
- PNAS 2023 human DMT EEG-fMRI source paper;
- 2019 multivariate human DMT EEG paper;
- Strassman/Qualls 1994 dose-response PubMed records I/II;
- Nichols 2018 pineal/DMT fact-vs-myth review;
- Barker et al. 2013 rat pineal-microdialysate DMT PubMed record;
- Borjigin et al. 2013 dying-rat EEG paper;
- 2023 dying-human gamma-connectivity paper;
- official Rick Strassman chapter-summary page and “Why Won’t DMT Go Away?” essay.

These are excellent **source cards / fact-check anchors** but not automatically image-reuse licenses for journal pages.

## Reference-only queue — rights unresolved

Store only in `reference_only/`, preferably source HTML + screenshot + rights note rather than untraceable direct-image URLs:

- Jimo Borjigin official University of Michigan profile/portrait;
- official Borjigin Lab near-death research/media page;
- Jon G. Dean UC San Diego story/portrait;
- Christopher Timmermann Imperial story/portrait;
- Imperial participant/treatment-room imagery;
- Michael M. Wang official portrait;
- Steven A. Barker current LSU emeritus source;
- Borjigin & Liu 2008 paper figures unless figure-level reuse rights are established.

## URLs/assets explicitly retired by the audit

Do not use the following old choices as canonical acquisition routes:

- standalone `media.springernature.com` Dean Figure 1–4 URLs — extract from verified Nature PDF instead;
- `Tryptamine_structure.svg` — replaced by public-domain `File:Tryptamine.svg`;
- cropped Carhart-Harris derivative — replaced by full Commons meeting image;
- bare `scx2.b-cdn.net/...electricalsi.jpg` Borjigin/Mashour image — use official lab source trail only;
- bare `Dean-teaser.jpg` — use verified UCSD story as source/permission reference;
- obsolete `mvsvipa3.lsu.edu` Barker/emeritus URL — replaced by current LSU Vet Med page;
- presumed NCI pineal illustration — no standalone reusable image verified on cited page;
- unauthorized Strassman book scans/pages — unnecessary because official author pages provide the hypothesis attribution.

## Highest-value story assets

### Central experimental reveal
`EP12_SRC_DEAN_FIG4`
- full PDF page/caption master first;
- figure extract second;
- show pineal-intact vs pinealectomized groups and baseline vs cardiac arrest;
- label internally: `RAT VISUAL CORTEX — EXPERIMENTAL CARDIAC ARREST`.

### Distributed-biology reveal
`EP12_SRC_DEAN_FIG1` / `FIG2` / `FIG3`
- Figure 1: rat/human INMT transcript context;
- Figure 2: real cellular/molecular evidence;
- Figure 3: optional secondary widening beyond brain/pineal.

### Strassman attribution
`EP12_SRC_STRASSMAN_PORTRAIT` + `EP12_SRC_STRASSMAN_HYPOTHESIS`
- portrait is freely usable;
- official chapter-summary page explicitly frames pineal/birth/NDE/death ideas as speculation;
- avoid unauthorized book page/cover as the primary evidence.

### Human DMT measurement
Use the 2023 CC BY fMRI/EEG figures and 2019 EEG source.
- label internally: `ADMINISTERED DMT — LIVING HUMAN PARTICIPANTS`.
- never cross-cut so they appear to measure endogenous DMT at death.

### Human near-death physiology
Use the five CC BY near-death EEG figures as a **separate evidence lane**.
- label internally: `EEG — NOT DMT MEASUREMENT`.

### Historical/esoteric layer
Use Descartes, Wellcome tantra, Leadbeater and Blavatsky assets as historical/cultural evidence.
- store separately in `history/` and `esoteric/`;
- never mix symbolic/theosophical imagery into modern-science source folders.

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

## Required QA after physical acquisition

For each actual file:

- verify final resolved URL and source identity;
- capture creator/institution/date;
- capture exact license text + license URL / PD rationale;
- save rights/provenance snapshot;
- compute SHA-256 and file size;
- record raster dimensions or SVG/PDF metadata;
- record PDF page count;
- preserve original/vector/full-page master before crops;
- record attribution string for CC BY/CC BY-SA;
- only then change manifest status from `VERIFIED_GREEN*` to `QA_PASS`.

## Script/claim alignment QA

- Dean result = **rat visual cortex**, experimental cardiac arrest.
- Pinealectomized animals still had measurable DMT in the reported experiment.
- Human INMT evidence = transcript localization, not measured terminal DMT release.
- Timmermann 2018 = phenomenological overlap, not causal mechanism.
- Human DMT fMRI/EEG = administered DMT.
- Near-death EEG = electrophysiology, not DMT measurement.
- Descartes/tantra/Leadbeater/Ajna = historical or symbolic material, not modern biological evidence.

## Git policy

Commit scripts, prompts, source URLs, manifests, rights/provenance records, verification reports, cue sheets and production notes. Keep large PDFs, images, audio and renders in external production storage unless a separate explicit Git LFS decision is made.
