# Checkpoint 1 remediation status

Branch: `integration/checkpoint-1-remediation`

## Completed in this branch

- Integrated the Pineal EP09, EP10 and EP12 source-lock/source-catalogue packages onto a branch created from current `master` instead of merging the heavily diverged historical branches.
- Added `07_ENGLISH_PRODUCTION/PINEAL_SERIES_ASSET_OWNERSHIP.md` to lock series-wide motif ownership and prevent Descartes/Ajna/Leadbeater/Dean/parietal-eye duplication.
- Added `tools/validate_asset_csv.py`; automated acquisition must fail on malformed row widths or suspicious status/state values.
- Added `tools/normalize_asset_csv.py` for the known legacy failure mode: literal commas inside file-like URLs. It percent-encodes only those URL commas, rewrites through `csv.writer`, and refuses rows that remain ambiguous rather than guessing rights/status fields.
- EP13 tightened: repeated envelope/archive explanation removed; projectile language is deliberately conservative and does not choose between conflicting immediate-provenance accounts.
- EP14 rewritten around one narrative question: why the 81-seal Causa Anglica survived while parts of the archive were displaced, discarded or lost. Templer detour removed; Galileo reduced to a short archive control case.
- EP15 rewritten with a concrete Valla text-forensics reveal (`satrapa`) and corrected framing: roughly eleven centuries after Constantine; Constantine-era Christianity described as transition to toleration/imperial support rather than an absolute end of persecution; Donation not treated as sole basis of papal power.
- EP16 structurally rebuilt from the 1948→1966 anomaly. Galileo is now book→Index-entry, not process-file repetition; Descartes is book→`donec corrigantur`, not portrait reuse.
- EP17 structurally rebuilt around the contested Surey Demoniack print dispute (1696 accusation / 1698 defence), with Canon 1172 and the 1999 rite used as the modern decision framework. Medical categories are explicitly kept separate and may not be used as generic possession texture.

## Pre-acquisition CSV gate

Before any downloader consumes Pineal CSVs, run the normalizer and validator as a pair:

```bash
python tools/normalize_asset_csv.py
python tools/validate_asset_csv.py
```

For CI/read-only checks, `python tools/normalize_asset_csv.py --check` returns non-zero if normalization would still change a manifest.

The normalizer is intentionally narrow. It repairs mechanically identifiable commas inside file-like URLs and then requires every row to match the header width. If a row remains malformed, acquisition stays blocked and the row requires explicit human repair. Rights/status values are never inferred by position-shifting heuristics.

## Production gates that remain intentionally open

### Heroasset gates

- EP13: real crown/projectile plus manuscript facsimile with usable rights. Do not restore a more specific immediate projectile provenance unless the conflicting accounts are reconciled.
- EP14: rights-clean high-resolution Causa Anglica / 81-seal document is mandatory.
- EP15: exact Valla manuscript/edition page used for the on-screen `satrapa` reveal must be page-mapped and rights-cleared.
- EP16: rights-clean 1948 Index title/relevant pages are mandatory.
- EP17: exact 1614 wording/page must be verified before quoting historical caution rules as text; Surey 1696/1698 originals must be page-mapped.

## Rule

`VERIFIED` means source/content verification only unless the record also contains acquisition and rights-lock evidence. Picture lock requires local original, provenance, rights basis, dimensions/page count, SHA-256 and (for visual files where useful) perceptual hash.
