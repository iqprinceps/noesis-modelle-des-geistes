# Checkpoint 1 remediation status

Branch: `integration/checkpoint-1-remediation`

## Completed in this branch

- Integrated the Pineal EP09, EP10 and EP12 source-lock/source-catalogue packages onto a branch created from current `master` instead of merging the heavily diverged historical branches.
- Added `07_ENGLISH_PRODUCTION/PINEAL_SERIES_ASSET_OWNERSHIP.md` to lock series-wide motif ownership and prevent Descartes/Ajna/Leadbeater/Dean/parietal-eye duplication.
- Added `tools/validate_asset_csv.py`; automated acquisition must fail on malformed row widths or suspicious status/state values.
- EP14 rewritten around one narrative question: why the 81-seal Causa Anglica survived while parts of the archive were displaced, discarded or lost. Templer detour removed; Galileo reduced to a short archive control case.
- EP15 rewritten with a concrete Valla text-forensics reveal (`satrapa`) and corrected framing: roughly eleven centuries after Constantine; Constantine-era Christianity described as transition to toleration/imperial support rather than an absolute end of persecution; Donation not treated as sole basis of papal power.
- EP16 structurally rebuilt from the 1948→1966 anomaly. Galileo is now book→Index-entry, not process-file repetition; Descartes is book→`donec corrigantur`, not portrait reuse.
- EP17 structurally rebuilt around the contested Surey Demoniack print dispute (1696 accusation / 1698 defence), with Canon 1172 and the 1999 rite used as the modern decision framework. Medical categories are explicitly kept separate and may not be used as generic possession texture.

## Production gates that remain intentionally open

### CSV normalization

The validator is now in place, but malformed legacy CSV rows must be normalized before any downloader consumes them. Do **not** treat integration of a legacy manifest as acquisition approval. Run:

```bash
python tools/validate_asset_csv.py
```

and fix every reported row before acquisition. The known failure mode is an unquoted comma in URL/title fields shifting subsequent columns.

### EP13

Story remains KEEP. Before production: trim repeated envelope/archive explanation and use only the conservative projectile statement until the conflicting provenance detail is resolved. Heroasset gate remains the real crown/bullet plus manuscript facsimile with usable rights.

### Heroasset gates

- EP14: rights-clean high-resolution Causa Anglica / 81-seal document is mandatory.
- EP15: exact Valla manuscript/edition page used for the on-screen `satrapa` reveal must be page-mapped and rights-cleared.
- EP16: rights-clean 1948 Index title/relevant pages are mandatory.
- EP17: exact 1614 wording/page must be verified before quoting historical caution rules as text; Surey 1696/1698 originals must be page-mapped.

## Rule

`VERIFIED` means source/content verification only unless the record also contains acquisition and rights-lock evidence. Picture lock requires local original, provenance, rights basis, dimensions/page count, SHA-256 and (for visual files where useful) perceptual hash.
