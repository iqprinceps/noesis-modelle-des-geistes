# Schlafparalyse V5 — Production Ready Lock

**Folgen:** EP06–EP08  
**Status:** READY FOR PRODUCTION nach Asset-Download + YELLOW-Review + V5-Visual-Prep  
**Visualstandard:** individuelle Coverage je Folge, V4-Prompt-Pool bleibt Reserve

## Was V5 ändert

V4 hatte pro Folge denselben AI-Prompt-Pool von 56 MAIN + 8 RESERVE. Das bleibt als **Rohmaterialreserve** erhalten, ist aber nicht mehr die Produktionsquote.

V5 setzt stattdessen:
- EP06: **149 Shots**, ca. 39 % Original / 42 % Recon / 19 % Motion
- EP07: **146 Shots**, ca. 60 % Original / 19 % Recon / 21 % Motion
- EP08: **150 Shots**, ca. 39 % Original / 38 % Recon / 23 % Motion

Die visuelle Dichte bleibt also hoch und sprechertextnah. Nur die Materialmischung wird episodenspezifisch.

## Kanonische V5-Dateien

Serienweit:
- `SCHLAFPARALYSE_VISUAL_COVERAGE_V5.md`
- `SCHLAFPARALYSE_ORIGINAL_ASSET_GAPS_V5.md`
- `SCHLAFPARALYSE_PRODUCTION_READY_LOCK_V5.md`

Pro Folge:
- `EP06_SCHLAFPARALYSE_01/VISUAL_COVERAGE_V5.md`
- `EP07_SCHLAFPARALYSE_02/VISUAL_COVERAGE_V5.md`
- `EP08_SCHLAFPARALYSE_03/VISUAL_COVERAGE_V5.md`

Tools:
- `tools/prepare_schlafparalyse_visuals_v5.py`
- `tools/noesis_render_schlafparalyse_v5.py`

## Produktionsreihenfolge

1. Source-Assets laden:
```bash
python3 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets.py
```

2. V5-Visual-Handoff bauen:
```bash
python3 tools/prepare_schlafparalyse_visuals_v5.py
```

Der V5-Prep ruft den bestehenden V4-Prep auf, entpackt den V4-Prompt-Pool und erzeugt danach pro Folge `VISUAL_CUE_SHEET_V5.csv` mit individuellen Shot-/Mix-Zielen.

3. Voice wie bisher erzeugen und alignen.

4. Render/Manifest über den V5-Entry-Point:
```bash
python3 tools/noesis_render_schlafparalyse_v5.py EP06 manifest
python3 tools/noesis_render_schlafparalyse_v5.py EP06 plan
```
Analog für EP07/EP08.

## Prompt-Regel

- V4-Prompt-Pool **nicht löschen**.
- Nicht automatisch alle 56 MAIN pro Folge generieren.
- AI nach V5-Coverage priorisieren:
  - EP06 ca. 48–54 unterschiedliche Recons + 8 Reserve
  - EP07 ca. 26–32 unterschiedliche Recons + 8 Reserve
  - EP08 ca. 50–58 unterschiedliche Recons + 10 Reserve
- Originale und Motion füllen den Rest der dichten Sprechertext-Coverage.

## Original-Regel

- vorhandene GREEN/YELLOW-Assets zuerst ausschöpfen
- YELLOW vor Einsatz prüfen
- RED bleibt Reference-only
- neue Originalquellen erst nach Rechte-/Kontextprüfung ins `asset_manifest.csv` aufnehmen
- niemals unsicheres Fremdmaterial verwenden, nur um eine numerische Originalquote zu erfüllen

## Wiederholungs-Lock

- kein identischer Frame zweimal
- keine zwei aufeinanderfolgenden Shots aus demselben Basisasset
- Ken Burns macht aus einem wiederholten Bild kein neues Motiv
- Hero-Dokumente/Kunst dürfen mehrfach erscheinen, aber nur mit semantisch anderem echten Crop/Detail
- kein Still >9 s
- visualer Modus regelmäßig wechseln, damit keine sichtbare Bildschleife entsteht

## Status

Die Trilogie ist mit V5 **visuell individuell produktionsbereit**. Offene Original-Asset-Gaps sind Qualitätsverbesserungen, keine Blocker; wo kein sauberes Original existiert, übernehmen native Motion oder klar erkennbare Reconstruction die Coverage.
