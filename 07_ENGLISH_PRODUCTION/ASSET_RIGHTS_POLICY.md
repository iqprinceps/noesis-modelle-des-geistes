# NOESIS Asset Rights Policy

Status: production rule

## Principle

NOESIS does not make episode production dependent on obtaining bespoke archive permissions.

For every required visual, use this order:

1. same authentic asset with a clearly documented commercial-friendly licence (CC0, Public Domain Mark, PD-old, CC BY, CC BY-SA);
2. another authentic primary-source image/object with a clearly documented commercial-friendly licence;
3. another historical public-domain source that supports the same claim without pretending to be the exact object;
4. an original NOESIS diagram/card derived from facts/data that can legally be restated;
5. a clearly labelled reconstruction for action/atmosphere only.

A permission request is optional and may improve quality, but it is never a production prerequisite unless explicitly approved as an exception.

## Status meanings

- `GREEN`: commercial reuse basis documented; required attribution/SA terms known.
- `AMBER`: source is authentic and usable in principle, but one limited issue remains (licence-chain recheck, resolution, attribution wording, jurisdiction note).
- `RED`: do not use this exact file in final production without a different rights basis. RED does **not** mean 'request permission'; it triggers replacement/reconstruction search.
- `REFERENCE_ONLY`: source may support research/claims but must not be reproduced as visual material.

## Evidence versus reconstruction

- Evidence/document claim -> authentic source asset whenever possible.
- Historical action for which no usable original image exists -> reconstruction is allowed if it is not presented as archival evidence.
- Never generate a facsimile that could be mistaken for a real manuscript, legal instrument, scientific figure or historical photograph.
- AI visuals must not impersonate news footage, archival scans or museum photography.

## Licence record required for every GREEN/AMBER visual

Store:
- canonical source page;
- direct file/download URL if available;
- creator/institution;
- date;
- licence/status (exact version, e.g. CC BY 3.0);
- licence URL;
- attribution/credit text;
- whether adaptation/crop/grade is allowed;
- ShareAlike requirement if applicable;
- original dimensions/page count;
- local filename;
- SHA-256 after acquisition;
- source-page snapshot or equivalent evidence;
- episode/shot IDs.

## Creative Commons handling

### CC BY
Commercial use and adaptation are allowed when the licence is valid for the asset. Credit creator/source, link the licence and indicate modifications.

### CC BY-SA
Same as CC BY, but adaptations must follow the applicable ShareAlike obligation. Production must document how the SA condition is being met before picture lock.

### CC0 / Public Domain Mark / PD-old
Generally preferred. Still retain source and credit where practical because provenance matters even when attribution is not legally mandatory.

## Websites and embeds

A page being publicly accessible does not make its images reusable. Treat website screenshots, archive viewer images and institutional photography as protected unless the specific asset has a reuse basis.

## Viewer-facing claim discipline

Licence status and factual authority are separate. A Commons file can be legally reusable but still require an authoritative source for the factual claim. Prefer two chains when useful:

- **visual rights chain**: e.g. Commons CC BY image;
- **claim/provenance chain**: e.g. museum, archive, Vatican, peer-reviewed paper.

This avoids using a rights-clean file as the sole authority for a sensitive historical claim.

## Production rule

No downloader may treat `VERIFIED_SOURCE` alone as permission for final use. Final production requires `GREEN` or an explicitly accepted `AMBER` record with its remaining condition documented.
