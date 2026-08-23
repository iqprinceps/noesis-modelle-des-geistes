# EP04B — Source Asset Map V5

The canonical rights/source database is `03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/asset_manifest.csv`.

## Archive-first default

EP04B can be produced on a **GREEN-first** path. YELLOW material is optional after its listed review; RED material is never used as source media.

Key cleared evidence anchors:

- `SHARED_Serpent_Power_Lotuses_Wellcome_M0005455_CC-BY-4.0.jpg`
- `SHARED_Brow_Chakra_Serpent_Power_PD.jpg`
- `SHARED_Serpent_Power_Uddiyana_Bandha_PD.jpg`
- `SHARED_The_Serpent_Power_1924_PD.pdf` — label as 1924 edition.
- `EP04B_Yogin_six_chakras_late18c_PD.jpg` — strong six-center historical beat; low resolution, use briefly.
- `EP04B_Sapta_Chakra_1899_PD.jpg`
- `EP04B_Calcutta_High_Court_Frith_PD.jpg`
- `EP04B_Leadbeater_c1925_PD.jpg`
- `EP04B_Leadbeater_alt_PD.jpg`
- `EP04B_Besant_Leadbeater_London_1901_PD.jpg`
- `EP04B_Adyar_HQ_1890_PD.jpg`
- `EP04B_Adyar_Library_1920_PD.jpg`
- `EP04B_Leadbeater_7_Chakras_Combined_1927_PD.jpg`
- `EP04B_Leadbeater_Chakras_Pictures_1927_PD.jpg`
- `EP04B_Leadbeater_Root_1927_PD.jpg`
- `EP04B_Leadbeater_Heart_1927_PD.jpg`
- `EP04B_Leadbeater_Throat_1927_PD.jpg`
- `EP04B_Leadbeater_Crown_1927_PD.jpg`

## Fallback locks

- Woodroffe NPG portrait remains RED/reference-only. Use the High Court, real book material and a clearly labeled generic reconstruction instead of a fake archive portrait.
- No verified reusable Atal Bihari Ghose portrait was found. Use collaboration documents, names and a non-identifying reconstruction of scholarly work.
- The available full *Serpent Power* scan is 1924. A 1919 title beat must be a clearly modern graphic reconstruction, never an aged fake facsimile.
- Modern rainbow graphics are contemporary reconstruction/motion and never illustrate 1577.

## Downloader

```bash
python 03_EPISODEN/TYPE_B/EP04A_EP04B_ASSETS_PHASE2/download_ep04ab_assets.py --only EP04B --green-only
```

Add YELLOW material only when its exact license/attribution requirement has been signed off for the final cut.
