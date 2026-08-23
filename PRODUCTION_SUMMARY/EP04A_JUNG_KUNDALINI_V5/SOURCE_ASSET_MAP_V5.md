# EP04A — Source Asset Map V5

The canonical rights/source database is `03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/asset_manifest.csv`.

## Default production path

Use **GREEN** assets automatically. Use **YELLOW** only after the listed attribution/jurisdiction/ShareAlike review. **RED** is reference-only or reconstruction-by-design and never enters the edit as source media.

Critical cleared anchors include:

- `EP04A_Jung_portrait_PD.jpg` — general Jung identity anchor.
- `EP04A_Clark_University_group_1909_PD.jpg` — Freud/Jung historical context.
- `EP04A_Burghoelzli_c1890_PD.jpg` — psychiatry/institution anchor.
- `EP04A_Jung_Association_Method_1910_PD.png` — scientific/clinical contrast.
- `EP04A_Europe_1914_Shepherd_PD.jpg` — 1914 reality snap.
- `SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg` — historical chakra/lotus hero asset.
- `SHARED_Brow_Chakra_Serpent_Power_PD.jpg` — historical detail.
- `SHARED_Serpent_Power_Uddiyana_Bandha_PD.jpg` — historical practice context.
- `SHARED_The_Serpent_Power_1924_PD.pdf` — verified public-domain scan; label it as the 1924 edition, never a facsimile of 1919.

Useful but review-gated examples include the 1930 Zurich view, Hauer 1935, current Jung house/Burghölzli and other ShareAlike/jurisdiction-sensitive files already marked YELLOW in the manifest.

## Hard visual rights locks

- Jung's 1913 black snake, flood, cave and Philemon are **reconstructions**, not archive.
- Red Book pages/art are not production assets without separate permission and are not copied into AI generations.
- No verified photo of the exact 1932 seminar is claimed; the seminar room is reconstruction surrounded by real place/person evidence.
- Historical Kundalini plates appear as their own sources; they never prove that Jung's black snake was Kundalini.

## Downloader

From the asset package:

```bash
python 03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/download_ep04ab_assets.py --only EP04A
```

For a rights-minimal first pass:

```bash
python 03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/download_ep04ab_assets.py --only EP04A --green-only
```

Keep source-page/license sidecars with the media through final delivery.
