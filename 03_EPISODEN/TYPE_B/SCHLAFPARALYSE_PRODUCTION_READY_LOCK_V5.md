# Schlafparalyse EP06–EP08 — Production Ready Lock V5

**Status:** READY FOR V5 PREPRODUCTION / final visual gate before render  
**Visual Canon:** `SCHLAFPARALYSE_VISUAL_COVERAGE_V5.md`

## V5 ersetzt die alte Gleichbehandlung

Die Promptstruktur ist einheitlich, die kreative Menge nicht:
- EP06: 32 MAIN + 8 RESERVE AI-Pool, 149 final geplante Shots.
- EP07: 20 MAIN + 4 RESERVE AI-Pool, 146 final geplante Shots, archive-first.
- EP08: 32 MAIN + 8 RESERVE AI-Pool, 150 final geplante Shots.

Die hohe Shotdichte bleibt in allen drei Folgen erhalten. Unterschiedlich ist, **womit** sie gefüllt wird.

## Kanonische Dateien

- `SCHLAFPARALYSE_VISUAL_COVERAGE_V5.md`
- `SCHLAFPARALYSE_PROMPT_STRATEGY_V5.md`
- `SCHLAFPARALYSE_FULL_PRODUCTION_HANDOFF_V5.md`
- `EP06_SCHLAFPARALYSE_01/VISUAL_COVERAGE_V5.md`
- `EP07_SCHLAFPARALYSE_02/VISUAL_COVERAGE_V5.md`
- `EP08_SCHLAFPARALYSE_03/VISUAL_COVERAGE_V5.md`
- `SCHLAFPARALYSE_ASSETS_PHASE2/ORIGINAL_ASSET_GAPS_V5.md`
- `SCHLAFPARALYSE_ASSETS_PHASE2/asset_manifest_v5_additions.csv`
- `SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets_v5.py`
- `tools/prepare_schlafparalyse_v5.py`
- `tools/check_schlafparalyse_visual_coverage_v5.py`

## Source-Download

```bash
python3 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets_v5.py
```

Base-Manifest + V5-Additions werden mit dem robusten Downloader geladen. YELLOW vor Einsatz reviewen; RED bleibt Research-only.

## Production Prep

```bash
python3 tools/prepare_schlafparalyse_v5.py
```

Der bestehende V4-Builder bleibt technische Basis für Voice/Audio/Handoff. Die Promptdateien liegen inzwischen direkt und kanonisch in den Episodenordnern; der alte Unpack-Befehl ist nur noch ein Kompatibilitätscheck und entpackt nichts mehr.

## Bilddichte-Lock

- erster Schnitt <=2,5 s
- kein Still >9 s
- meist 2,8–4,8 s
- kein identischer Frame zweimal
- keine zwei aufeinanderfolgenden Shots aus demselben Basisasset
- Basisasset normalerweise max. 2 Einsätze, nur bei wirklich anderer Information
- Ken Burns ist keine neue Coverage
- Original/Dokument vor AI, wenn es eine konkrete Behauptung besser belegt

## Final Visual Gate

Vor `noesis_render.py ... render`:

```bash
python3 tools/check_schlafparalyse_visual_coverage_v5.py EP06
python3 tools/check_schlafparalyse_visual_coverage_v5.py EP07
python3 tools/check_schlafparalyse_visual_coverage_v5.py EP08
```

Neue AI-Prompts werden nur ergänzt, wenn dieser Gate bzw. ein konkreter Sprecherbeat eine echte Lücke zeigt. Keine künstliche Angleichung der Promptzahlen.

## Unverändert gelockt

Voice-Authenticity-Drehbücher, Claims Locks, George-/ElevenLabs-Settings, Audio-Stem-Logik, Endcard-Prinzipien und faktische Source-Disziplin bleiben bestehen.
