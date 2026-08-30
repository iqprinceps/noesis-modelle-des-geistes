# EP11_EN — Production Plan

## Status

**GO for asset acquisition and visual preproduction.**

Voice lock is conditional on completing the acquisition checks below. The English script has received a source-precision pass; no broad rewrite is required.

## Codex / external-media handoff

Repository policy keeps large binaries outside Git. The repository confirms `D:\Noesis` as the external Noesis root for relocated production/channel media. For EP11 use:

`D:\Noesis\Production\EN\EP11_PINEAL_03\`

Suggested layout:

- `ORIGINALS\SECRET_DOCTRINE_V2\`
- `ORIGINALS\PARIETAL_EYE\`
- `ORIGINALS\AJNA\`
- `ORIGINALS\DMT_2019\`
- `ORIGINALS\PORTRAITS\`
- `RESEARCH\LEADBEATER\`
- `GENERATED\STILLS\`
- `QA\CONTACT_SHEETS\`
- `QA\LICENSE_SNAPSHOTS\`

Codex should process `02_SOURCES/ACQUISITION_MANIFEST.csv` row by row. For every acquired binary it must update the manifest with the final direct URL, retrieval date, SHA-256, dimensions/page count, local path and final rights status.

## Acquisition order

1. **Blavatsky portrait** — acquire the Rijksmuseum/Commons CC0 original and capture the Commons license page.
2. **The Secret Doctrine Vol. II** — locate a high-resolution first-edition/public-domain scan; extract full pages 289 and 294–301 as non-destructive derivatives while retaining the full PDF.
3. **Parietal-eye anatomy** — obtain one nineteenth-century plate/page whose source metadata and publication date are unambiguous.
4. **Ajna** — verify the Woodroffe/Avalon passage, then prefer a rights-clean institution scan for on-screen use; if rights remain uncertain, use the text only as research and create a clearly original visualization.
5. **Leadbeater** — verify exact sixth/pituitary, seventh/pineal language and the later pituitary-current discussion. Do not picture-lock the current web PDF until rights/provenance are acceptable; otherwise build an original editorial diagram from verified text.
6. **Dean et al. 2019** — acquire journal/PMC article under its stated open-access terms and record article license with the asset.

## Document-reveal rules

- Documents enter before reconstructions when the narration makes a historical claim.
- Show complete relevant passages at readable scale; highlight only the words being discussed.
- Do not crop away title, page number, author or publication context when these establish identity.
- Do not animate a highlight across words that are not actually present on the page.
- Never combine separate historical pages into a fabricated single “archive” page.

## Visual progression

1. 1888 book and Blavatsky identity.
2. Comparative-anatomy room and real reptile/parietal-eye evidence.
3. Ajna in a separate visual language: human practice, lotus, brow center, no brain-gland overlay.
4. Blavatsky document pages progressively bring the two lines together.
5. Three-source montage makes the construction visible.
6. Leadbeater breaks the apparent stability with a different gland map.
7. Repetition through later popular culture hides the seam.
8. Human meditative experience remains emotionally open.
9. Visual language shifts from symbol to molecule and lands on the 2019 rat experiment.

## Generated-image package

Use `03_VISUALS/IMAGEGEN_PROMPTS.md`. All generated assets are reconstructions/symbolic visualizations and must be tagged as such in provenance metadata. Generated images never substitute for primary-document evidence.

## Voice-lock checklist

- [ ] Public-domain scan locked for Blavatsky pp. 289 and 294–301.
- [ ] Exact parietal-eye plate and publication citation locked.
- [ ] Ajna source passage verified against selected edition.
- [ ] Leadbeater wording verified against a reliable scan/edition.
- [ ] Dean et al. 2019 wording checked against Fig. 4 and pinealectomy method.
- [ ] Native-English aloud read after the precision changes.
- [ ] Word count / narration estimate regenerated.

## Picture-lock risk notes

- Highest rights risk: Leadbeater scan/edition.
- Medium rights risk: arbitrary web-hosted Woodroffe scans; resolve via institution/public-domain source where possible.
- Low rights risk: Rijksmuseum CC0 Blavatsky portrait.
- Scientific article assets require the article's stated open-access attribution/license terms, not a generic “public domain” label.

## Definition of production-ready

EP11 is production-ready when the manifest has hashes/dimensions for every picture-locked original, all rights-hold rows are either cleared or replaced by original editorial visuals, and the final narration wording is unchanged after the source checks.
