# EP10_EN — Codex / Production Handoff

Status: ready for **expanded verified acquisition pass**

## Canonical research inputs

1. `04_SOURCES/VERIFIED_ASSET_CATALOG.md` — human-readable audit with verified content, rights, fit and exclusions.
2. `04_SOURCES/SOURCE_AND_LICENSE_MANIFEST.csv` — machine-friendly source/rights inventory.
3. `03_VISUALS/ORIGINAL_ASSET_PLAN.md` — P0/P1/P2 acquisition order and edit use.

## Codex tasks

1. Acquire **P0 first**, then P1. P2 is only the final EP11 handoff and must not dominate EP10.
2. Download only manifest rows marked `CLEARED`, `CLEARED_ATTRIBUTION`, `SOURCE_HUB` where a specific derivative is subsequently selected, or other explicitly approved status. Do **not** download `REFERENCE_ONLY`, `EXCLUDED_*` or `REJECTED` items into the final asset pool.
3. Store binaries in external production storage, not GitHub.
4. For every binary, record:
   - asset/source ID;
   - original landing URL;
   - redirect-resolved binary URL;
   - acquisition UTC timestamp;
   - HTTP status and MIME type;
   - creator/institution and original date;
   - verbatim rights statement and licence URL where applicable;
   - local filename;
   - byte size;
   - pixel dimensions or PDF page count;
   - SHA-256.
5. For CC BY assets, carry exact attribution into the final credits/provenance record.
6. For public-domain/CC0 assets, retain source/institution credit even when attribution is not legally mandatory.

## P0 acquisition queue

- EP10-A01 — Descartes Frans Hals portrait.
- EP10-A03 — Elisabeth Cooper/Honthorst Rijksmuseum miniature.
- EP10-A04 — Elisabeth Honthorst full portrait, 1636.
- EP10-A07 — Adam–Tannery vol. III facsimile master.
- EP10-A08 — Elisabeth 6 May 1643, AT III 660–662.
- EP10-A09 — Descartes 21 May 1643, AT III 663–668.
- EP10-A10 — Elisabeth 10 June 1643, AT III 683–685.
- EP10-A11 — Descartes 28 June 1643, AT III 690–697.
- EP10-A13 — *Les Passions de l’âme* 1649 facsimile.
- EP10-A14 — *Passions* title page.
- EP10-A16 — *L’Homme* title page.
- EP10-A17 — Wellcome burning-pain pathway.
- EP10-A18 — animal-spirits/body-machine engraving.
- EP10-A19 — Descartes brain section.
- EP10-A20 — Wellcome ventricles diagram L0008517.
- EP10-A21 — Wellcome posterior brain L0008518.
- EP10-A28 — modern human pineal histology.

## Documentary page extraction gates

### AT III

- **660–662:** Elisabeth → Descartes, manuscript-date convention 6 May 1643.
- **663–668:** Descartes → Elisabeth, 21 May 1643; prioritize 664–666.
- **683–685:** Elisabeth → Descartes, manuscript-date convention 10 June 1643; prioritize 684–685.
- **690–697:** Descartes → Elisabeth, 28 June 1643; prioritize 691–692.

The source edition/navigation can expose dual-calendar/editorial variants such as 16 May / 20 June. Preserve the source wording in metadata. Do not alter the facsimile. The voice script follows the manuscript-date convention.

### *Les Passions de l’âme*

- Extract complete historical pages around **Part I, arts. 31–35**.
- Confirm the passage used for pineal centrality on the acquired page image before edit lock.

## Specific image verification

For each historical anatomy image, confirm the downloaded master visually matches the catalog description:

- A17: burning pain / nerve pathway.
- A18: animal spirits acting on body-machine.
- A19: brain section.
- A20: ventricles diagram.
- A21: posterior brain / pineal-region view.
- A22: *De homine* physiology/body image if selected.

Do not silently substitute a different Descartes diagram simply because the filename is similar.

## P2 esoteric handoff rule

A33–A39 may only enter the **final handoff** after narration explicitly moves from Descartes/Elisabeth to later third-eye/occult reception. They are historical reception assets, not seventeenth-century evidence.

Especially useful:

- A35 — Rajasthan brow chakra, 18th century.
- A36 — Leadbeater chakra plates, 1927.
- A37 — Leadbeater pineal/pituitary image, 1927.

## Explicit rejects

- `https://philotextes.info/IMG/pdf/1643.pdf` — unstable/timed out; rights unclear.
- `https://plato.stanford.edu/entries/pineal-gland/` — broken current URL; use archived SEP only for research.
- Wellcome yoga-lotuses image `ymn7dwzj` — explicitly **In copyright**.
- Generic modern spiritual/anatomy web images without clear reusable rights.

## Do not do

- do not commit PDFs, TIFFs, PNG masters, audio or rendered clips to GitHub;
- do not generate fake letters or fake seventeenth-century pages when originals exist;
- do not treat a reconstruction as archive or science evidence;
- do not use a modern English modernization as an apparent 1643 facsimile;
- do not hide source-date variants by retouching a historical page.
