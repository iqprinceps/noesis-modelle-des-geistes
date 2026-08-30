# EP09_EN — Production Plan

Reviewed: 2026-08-30
Episode: `EP09_PINEAL_01 — The Eye Within`
Canonical voice: `01_SCRIPT/VOICE_SCRIPT_EN.txt`

## Current state

- Script: SOURCE-LOCKED; three evidence-driven wording edits applied.
- Scientific claims: mapped to primary/authoritative sources.
- Original assets: researched and queued in `02_SOURCES/ORIGINAL_ASSET_MANIFEST.csv`.
- Generated visuals: prompt plan complete in `03_VISUALS/VISUAL_PROMPTS.md`.
- Binary media: intentionally not stored in GitHub; acquisition belongs in external production storage.

## Codex acquisition job

Codex should process every row marked `PENDING_CODEX` in `02_SOURCES/ORIGINAL_ASSET_MANIFEST.csv`.

For each acquired file:

1. download the highest-quality original from the source page rather than a thumbnail;
2. store the binary in the external production root for `EP09_PINEAL_01`;
3. record exact final source URL, creator/institution, title, date, license name/version, attribution string and retrieval date;
4. compute SHA-256;
5. record pixel dimensions / page count / file type;
6. preserve the uncropped source original;
7. create an editorial derivative only after provenance is locked;
8. for documents, record exact page/plate and the narration beat it supports;
9. reject any candidate whose license or identity cannot be verified;
10. update the textual manifest in GitHub with `ACQUIRED`, local external-storage path, hash and QA result.

## Required media QA

### A. Tuatara / parietal eye
- Prefer a living tuatara photo whose license is explicit and reusable.
- Do not caption an ordinary head photograph as a visible functional “third eye” unless the chosen source specifically establishes that feature.
- Acquire Dendy 1899 plates XI–XIII and preserve full plate/page context.
- Acquire Spencer 1886 historical parietal-eye plate as a secondary anatomy anchor.

### B. Human anatomy and pathway
- Acquire Gray plate 719 in original high resolution.
- Verify the exact creator and CC BY 4.0 attribution for the SCN pathway image before using it.
- Cross-check any visualized route against Moore 1996 and Endotext; the production animation may simplify appearance, not anatomy.

### C. Chang et al. experiment
- Acquire the complete article/PDF for editorial reference.
- Do not blindly reuse the paper’s figure artwork. If figure rights are not explicitly compatible with production, recreate the graphic from the reported values with a citation.
- Lock these study facts in the data graphic notes: 12 healthy adults, randomized crossover, five consecutive evenings per condition, approximately four hours reading before bedtime; reported melatonin suppression 55.12 ± 20.12%, DLMO delayed by more than 1.5 h, sleep latency roughly 10 min longer, lower next-morning alertness.
- Do not convert this study into a universal claim that every phone produces the same magnitude of effect.

### D. Descartes / Elisabeth bridge
- Acquire the public-domain Descartes portrait.
- For the Elisabeth letter, obtain a stable archival facsimile from Gallica, Internet Archive or another archival host where possible; keep Wikisource only as a locator/transcription aid.
- Full historical source treatment continues in EP10; EP09 needs only enough to make the cliffhanger authentic.

## Edit progression

1. **0:00–0:35 — Living biological impossibility**: real tuatara → authentic historical anatomy → reconstruction.
2. **0:35–2:00 — Light as time**: ecology/time passage → pineal/parietal relationship.
3. **2:00–3:45 — Human detour**: retina → SCN → autonomic relay → pineal.
4. **3:45–4:45 — Payoff**: darkness → melatonin → “The sky becomes a molecule.”
5. **4:45–6:25 — Modern experiment**: Chang paper → study reconstruction → recreated data motion graphic.
6. **6:25–7:25 — Personal night**: ordinary modern evening; rhythm larger than one gland.
7. **7:25–8:20 approx. — Meaning and handoff**: human anatomy → Descartes portrait → Elisabeth letter → viewer question.

Timing follows final voice; these are edit proportions, not hard timestamps.

## Voice QA before render

- Native aloud read for naturalness and stress.
- Pronunciation lock: `tuatara`, `parietal`, `pineal`, `melatonin`, `circadian`, `Descartes`, `Elisabeth`.
- Preserve short sentence spacing around `The sky becomes a molecule.`
- Do not add explanatory filler or generic disclaimer language during voice production.

## Production gates

- `SOURCE_LOCK`: PASS
- `VOICE_TEXT_LOCK`: PASS pending native aloud read
- `ORIGINAL_ASSET_RIGHTS_LOCK`: PENDING_CODEX
- `ORIGINAL_ASSET_BINARY_QA`: PENDING_CODEX
- `GENERATED_VISUALS`: READY_TO_GENERATE after reference assets are acquired
- `PICTURE_LOCK`: BLOCKED until asset manifest has hashes/licenses
- `UPLOAD_RIGHTS_REGISTER`: BLOCKED until final selected assets are known
