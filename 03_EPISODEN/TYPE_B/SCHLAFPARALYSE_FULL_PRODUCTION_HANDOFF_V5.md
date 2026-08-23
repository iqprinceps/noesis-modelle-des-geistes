# Schlafparalyse EP06–EP08 — Full Production Handoff V5

**Status:** READY FOR PRODUCTION  
**Kanonischer Visual-Lock:** `SCHLAFPARALYSE_PRODUCTION_READY_LOCK_V5.md`

## Wichtig

Die Sprechertexte, Claims Locks, Voice-/Audio-Logik und der V4-Prompt-Pool bleiben gültig. V5 ersetzt ausschließlich die bisher zu schematische Annahme, jede Folge müsse denselben 56+8-AI-Workflow verwenden.

## Visual Targets

- EP06: 149 Shots — science/recon hybrid
- EP07: 146 Shots — archive/document heavy
- EP08: 150 Shots — media/recon/motion hybrid

Details:
- `SCHLAFPARALYSE_VISUAL_COVERAGE_V5.md`
- je Episode `VISUAL_COVERAGE_V5.md`

## Workflow

```bash
# Repo aktualisieren
git pull origin master

# Originalassets laden
python3 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets.py

# V4-Basis + individuelle V5 Visual Cues bauen
python3 tools/prepare_schlafparalyse_visuals_v5.py
```

Danach existiert pro Folge zusätzlich:
- `PRODUCTION_SUMMARY/EP06_SCHLAFPARALYSE_V4/VISUAL_CUE_SHEET_V5.csv`
- `PRODUCTION_SUMMARY/EP07_SCHLAFPARALYSE_V4/VISUAL_CUE_SHEET_V5.csv`
- `PRODUCTION_SUMMARY/EP08_SCHLAFPARALYSE_V4/VISUAL_CUE_SHEET_V5.csv`

## Voice

Voice bleibt wie V4 gelockt:
- George / `JBFqnCBsd6RMkjVDRZzb`
- `eleven_multilingual_v2`
- stability 0.58
- similarity 0.80
- style 0.08
- speed 1.06
- seed 2402

Voice bauen/alignen wie im bestehenden V4-Handoff.

## Bilder

1. Originale zuerst auf konkrete Sprecherbeats mappen.
2. Motion-Slots aus V5-Coverage setzen.
3. Nur die tatsächlich benötigten Recons aus dem V4-Prompt-Pool erzeugen.
4. Reservebilder erzeugen, wenn ein Motiv im Schnitt zu ähnlich/repetitiv wirkt.
5. Render-Manifest darf mehrere Assets pro Cue enthalten; diese werden als eigene Shots ausgespielt.

## Render

Für EP06–EP08 den V5-Wrapper verwenden:

```bash
python3 tools/noesis_render_schlafparalyse_v5.py EP06 doctor
python3 tools/noesis_render_schlafparalyse_v5.py EP06 manifest
python3 tools/noesis_render_schlafparalyse_v5.py EP06 plan
python3 tools/noesis_render_schlafparalyse_v5.py EP06 all
```

Analog EP07/EP08.

## QA

Vor finalem Render:
- Shot-Target ungefähr treffen; Sprechertext entscheidet, nicht starre Sekundenmathematik
- kein Still >9 s
- kein identischer Frame doppelt
- keine sichtbare wiederkehrende Bildsequenz
- keine zwei aufeinanderfolgenden Shots aus demselben Basisasset
- Non-16:9 contained mit weich/dunkel gleichem Bild im Hintergrund
- Quellen-/Rights-Kontext aus Manifest beachten
- EP07 muss sichtbar archivlastiger sein als EP06/EP08
- EP08 Hat Man erst spät vollständig zeigen

## Original-Asset-Gaps

`SCHLAFPARALYSE_ORIGINAL_ASSET_GAPS_V5.md` listet zusätzliche Rechercheziele. Sie sind Qualitätsverbesserungen, keine Erlaubnis für ungeprüftes Material und kein Grund, Produktion zu blockieren.

## Kanonische Entscheidung

**Visuelle Dichte bleibt hoch. Materialmix wird individuell.** Das ist der V5-Lock.
