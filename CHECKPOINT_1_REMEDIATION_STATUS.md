# Checkpoint 1 remediation status

Branch: `integration/checkpoint-1-remediation`

## Completed in this branch

- Integrated the Pineal EP09, EP10 and EP12 source-lock/source-catalogue packages onto a branch created from current `master` instead of merging the heavily diverged historical branches.
- Added `07_ENGLISH_PRODUCTION/PINEAL_SERIES_ASSET_OWNERSHIP.md` to lock series-wide motif ownership and prevent Descartes/Ajna/Leadbeater/Dean/parietal-eye duplication.
- Added `tools/validate_asset_csv.py`; automated acquisition fails on malformed row widths, blank workflow states or invalid machine-status tokens while leaving descriptive rights notes as free text.
- Added `tools/normalize_asset_csv.py` as a lossless RFC-4180 canonicalizer. It never guesses whether an unquoted comma belongs to a URL or separates fields; ambiguous legacy rows were repaired explicitly in their manifests.
- EP13 tightened: repeated envelope/archive explanation removed; projectile language is deliberately conservative and does not choose between conflicting immediate-provenance accounts.
- EP14 rewritten around one narrative question: why the 81-seal Causa Anglica survived while parts of the archive were displaced, discarded or lost. Templer detour removed; Galileo reduced to a short archive control case.
- EP15 rewritten with a concrete Valla text-forensics reveal (`satrapa`) and corrected framing: roughly eleven centuries after Constantine; Constantine-era Christianity described as transition to toleration/imperial support rather than an absolute end of persecution; Donation not treated as sole basis of papal power.
- EP16 structurally rebuilt from the 1948→1966 anomaly. Galileo is now book→Index-entry, not process-file repetition; Descartes is book→`donec corrigantur`, not portrait reuse.
- EP17 structurally rebuilt around the contested Surey Demoniack print dispute (Zachary Taylor 1697 / Thomas Jollie 1698), with Canon 1172 and the 1999 rite used as the modern decision framework. The script identifies this as a comparative English dispute rather than a Vatican case. Medical categories are explicitly kept separate and may not be used as generic possession texture.
- Added `07_ENGLISH_PRODUCTION/PINEAL_SERIES_FINAL_STORY_LOCK.md`: final EP09–EP12 anti-lecture, retention and macro-outro rules. Each episode now has a single dramatic engine, evidence rhythm and explicit production handoff.
- Added `03_EPISODEN/TYPE_B/VATIKAN_SERIE_FINAL_STORY_LOCK.md`: final EP13–EP17 hero-object, pacing and primary-document rules. The series is locked as five investigations rather than five topic lectures.

## Final editorial lock

EP06–EP08 are the production-quality reference, not an episode-content template.

For EP09–EP17:
- story voice carries question, action, contradiction and consequence;
- viewer cards carry dense explanatory structure;
- primary documents are shown full before locator/crop/highlight;
- no uninterrupted textbook/institutional explanation should survive when it can be converted into an experiment, person, object, document or consequence;
- AI reconstruction fills action gaps only and never impersonates primary evidence;
- macro-outros must make the next episode feel like the logical consequence of the current discovery.

## Pre-acquisition CSV gate

Before any downloader consumes Pineal CSVs, run the normalizer and validator as a pair:

```bash
python tools/normalize_asset_csv.py
python tools/validate_asset_csv.py
```

For CI/read-only checks, `python tools/normalize_asset_csv.py --check` returns non-zero if normalization would still change a manifest.

The normalizer is intentionally conservative. It parses and rewrites only already-valid RFC-4180 data, requires every row to match the header width and refuses ambiguous rows instead of shifting fields. Rights/status values are never inferred by position.

Verified on 2026-08-30 after explicit legacy-row repair:

- `python tools/normalize_asset_csv.py` → exit 0;
- `python tools/normalize_asset_csv.py --check` → exit 0;
- `python tools/validate_asset_csv.py` → exit 0.

## Heroasset decisions and remaining acquisition checks

### Heroasset gates

- EP13: crown/projectile is GREEN via CC BY 3.0; the exact Vatican manuscript remains reference-only and is replaced visually by a briefly disclosed reconstruction/evidence card. Do not restore a more specific immediate projectile provenance unless the conflicting accounts are reconciled.
- EP14: object facts are locked; protected exact photography remains reference-only. The production path uses a briefly disclosed schematic scale/seal reconstruction and must never impersonate the original.
- EP15: Coleman printed p. 87 is the locked `satrapa` locator. Match it to the rights-safe Commons facsimile before cue-sheet lock and store the territory/provenance record.
- EP16: 1948 bibliographic facts are locked; the exact scan remains reference-only. The script and visual lock now use a disclosed bibliographic reconstruction plus correctly dated older public-domain Index pages.
- EP17: the 1697 Taylor accusation and 1698 Jollie defence are locked through live Wellcome Public Domain Mark records/IIIF manifests. The 1614 caution rule is source-located; quote Latin only after exact-page comparison.

All 14 URLs in the five `HEROASSET_LOCK.md` files returned HTTP success in the final link audit. Reachability is not treated as a rights grant; each selected local original still requires its recorded licence/provenance snapshot.

### Production-package gates

After heroasset/source lock, build episode-specific outputs in this order:
1. final clean voice script / pronunciation notes for actually spoken terms;
2. viewer/evidence cards;
3. `VISUAL_CUE_SHEET_V5` tied to voice beats and asset IDs;
4. NanoBanana prompt batches only for missing reconstruction/action states;
5. three Shorts/derivative hooks;
6. acquisition, provenance, rights, SHA-256/pHash and visual QA.

Do not create fake precision by timing cue sheets against a voice draft or by generating reconstruction art before the real heroassets are locked.

## Rule

`VERIFIED` means source/content verification only unless the record also contains acquisition and rights-lock evidence. Picture lock requires local original, provenance, rights basis, dimensions/page count, SHA-256 and (for visual files where useful) perceptual hash.
