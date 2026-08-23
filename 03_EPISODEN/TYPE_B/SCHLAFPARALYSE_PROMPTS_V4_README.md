# Schlafparalyse — Nano Banana Prompts V4

**Status:** direkte Repo-Ablage wie EP05 Jung–Pauli.

Die finalen Bildprompts liegen sichtbar und kanonisch in den jeweiligen Episodenordnern. Es ist kein ZIP und kein Entpack-Schritt mehr erforderlich.

## EP06

`03_EPISODEN/TYPE_B/EP06_SCHLAFPARALYSE_01/`
- `NANOBANANA_GUIDE_V4.md`
- `NANOBANANA_PROMPTS_V4_S1_S2.md`
- `NANOBANANA_PROMPTS_V4_S3_S4.md`
- `NANOBANANA_PROMPTS_V4_S5_S6.md`
- `NANOBANANA_PROMPTS_V4_S7_S8.md`

Prepared pool: **32 MAIN + 8 RESERVE**, plus real science/location assets and motion.

## EP07

`03_EPISODEN/TYPE_B/EP07_SCHLAFPARALYSE_02/`
- `NANOBANANA_GUIDE_V4.md`
- four S1–S8 prompt batches

Prepared pool: **20 MAIN + 4 RESERVE**. Deliberately archive-first: Salem primary documents and historical art carry the strongest evidence beats.

## EP08

`03_EPISODEN/TYPE_B/EP08_SCHLAFPARALYSE_03/`
- `NANOBANANA_GUIDE_V4.md`
- four S1–S8 prompt batches

Prepared pool: **32 MAIN + 8 RESERVE**, plus real Art Bell/science assets and motion.

## Prompt format

Every image follows the same production format as Jung–Pauli:

```text
EXAKTER_DATEINAME.png
Referenz: EXAKTE_REFERENZDATEI.jpg
Prompt:
<vollständiger eigenständiger Prompt>
```

No hidden global prompt is required. Exact factual references were selected from the verified asset package; research-only URLs/PDFs are not used as direct image-generation references.

## Why counts differ

The layout is standardized; the creative quantity is not. EP07 has stronger original historical material and therefore needs less AI coverage than EP06/EP08. This follows `01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md`.

## Global consistency rule

See `01_GLOBAL/00C_IMAGE_PROMPT_STRUCTURE.md`. Run:

```bash
python3 tools/check_image_prompt_layout.py
```

A production-ready episode may no longer hide its final prompt text only in `PRODUCTION_SUMMARY` or a ZIP.