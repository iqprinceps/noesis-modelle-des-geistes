# EP10_EN — Codex / Production Handoff

Status: ready for acquisition pass

## Codex tasks

1. Read `04_SOURCES/SOURCE_AND_LICENSE_MANIFEST.csv` and `03_VISUALS/ORIGINAL_ASSET_PLAN.md`.
2. Download only rows marked `CLEARED` or `CLEARED_PENDING_DOWNLOAD` into external production storage; do not commit large binaries to GitHub.
3. For every binary, record final source URL, redirect-resolved URL if different, acquisition timestamp, HTTP/content type, local filename, byte size and SHA-256.
4. Verify that AT III correspondence pages 660–695 are legible and extract the exact page images needed for 6 May, 21 May, 10 June and 28 June 1643.
5. Archive institution/license metadata for the Rijksmuseum Elisabeth portrait, Commons Descartes portrait and Wellcome assets.
6. Locate a public-domain scan of *Les Passions de l'âme* and verify Part I articles 31–35 before use.
7. Reject any asset whose license/provenance cannot be verified; mark it `REFERENCE_ONLY` rather than silently substituting it into the edit.
8. Update the external asset manifest and, if the pipeline maintains text manifests in GitHub, commit only those manifest/provenance changes.

## Expected local filenames

- `Oeuvres_Descartes_AT_III.pdf`
- `Elisabeth_Cooper_Rijksmuseum_PD.*`
- `Descartes_Frans_Hals_PD.*`
- `Descartes_L_Homme_1664.*`
- `Descartes_burning_pain_Wellcome.*`
- `Descartes_Passions_1649_PD_scan.*`

## Verification gates

- AT III 660–662: first Elisabeth letter.
- AT III 663–668: Descartes reply of 21 May.
- AT III 683–685: Elisabeth reply of 10 June.
- AT III 690–695: Descartes reply of 28 June.
- *Passions de l'âme*, Part I arts. 31–35: pineal / single-central-structure material.

## Do not do

- do not commit PDFs, TIFFs, PNG masters, audio or rendered clips to the repository;
- do not generate a fake facsimile when the original page exists;
- do not use modern copyrighted illustrations as generic filler;
- do not turn reconstruction assets into implied evidence.
