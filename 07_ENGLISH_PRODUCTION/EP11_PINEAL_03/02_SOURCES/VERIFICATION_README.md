# EP11_EN — Verified asset acquisition authority

For actual acquisition, use these files in this order:

1. `VERIFIED_ASSET_REGISTER.csv` — machine-readable verified URLs and statuses.
2. `URL_VERIFICATION_REPORT.md` — human-readable verification notes, corrections, rights nuances and intended use.
3. `ACQUISITION_MANIFEST.csv` — external-storage targets / Codex acquisition workflow.
4. `ASSET_POOL_EXPANDED.csv` — broad discovery pool only; where it conflicts with the verified register, the verified register wins.

## Critical corrections from URL verification

- The earlier Iguana path ending in `.jpg` is invalid. Use:
  `https://commons.wikimedia.org/wiki/File:Klinckowstroem_(1894)_parietal_eye_of_Iguana.png`
- Do not treat Commons category pages or museum collection searches as selected assets. They are discovery endpoints only.
- Prefer exact Ajna files:
  - `Traditional_Hindu_Diagram_of_Brow_Chakra.jpg`
  - `Brow_Chakra_Rajasthan_18th_Century.JPG`
- Prefer exact Leadbeater primary evidence:
  - `Pineal_Gland_and_Pituitary_Body.jpg`
- Prefer exact Shiva evidence:
  - `Shiva_Musée_Guimet_22971.jpg`
- Prefer exact Descartes evidence:
  - `Descartes_diagram.png`
  - Wellcome posterior-brain/pineal-in-situ file if its exact reuse metadata is captured.
- Wellcome M0005455 remains `RIGHTS_HOLD_METADATA_CONFLICT`; do not picture-lock it until the exact binary/reuse basis is resolved.

No binary is `ACQUIRED` merely because a URL was verified. Codex still must download the file, inspect it, record direct-download URL, exact license statement, retrieval date, SHA-256, dimensions/page count and external production path.