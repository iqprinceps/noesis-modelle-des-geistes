# NOESIS — Schlafparalyse EP06–EP08 Assets V5

## Kanonischer Einstieg

`asset_manifest_v5.json` ist der **kanonische Manifest-Einstiegspunkt**. Er umfasst drei normalisierte CSV-Layer:

1. `asset_manifest.csv` — 49 geprüfte Phase-2-Basisassets
2. `asset_manifest_v5_additions.csv` — 2 erste V5-Erweiterungen
3. `asset_manifest_v5_expansion.csv` — 25 zusätzliche retention-orientierte Original-/Kontextassets

Der V5-Downloader verarbeitet alle drei Layer automatisch und prüft sie mit demselben resilienten Downloadpfad.

## Bestand

- **76 eindeutige Asset-Einträge**
- **46 GREEN / 19 YELLOW / 11 RED**
- **65 automatisch downloadbare Medienassets**
- **EP06: 22 Assets inkl. Shared**
- **EP07: 28 Assets**
- **EP08: 32 Assets inkl. Shared**

Damit sind die gesetzten Original-/Kontextziele für den individuellen V5-Visualplan erreicht. Zusammen mit den separaten AI-Reconstruction-Pools und Motion-/Diagramm-Slots reicht die Basis für rund 146–150 Shots und >90 eindeutige Visuals pro Folge, ohne lange Holds oder sichtbare Bildloops.

## Download

Empfohlen:

```bash
python3 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets_v5.py
```

Nur eine Folge:

```bash
python3 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets_v5.py --only EP07
```

Nur GREEN:

```bash
python3 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets_v5.py --green-only
```

Standard lädt GREEN + YELLOW. RED bleibt Reference-only. Erfolgreiche Dateien werden bei späteren Läufen übersprungen.

## Rechte-Ampel

- **GREEN:** dokumentierter Rechtestatus; grundsätzlich produktionsfähig, Kontextpflicht bleibt.
- **YELLOW:** nutzbar/reviewbar, aber Attribution, ShareAlike, Persönlichkeitsrechte oder finaler Lizenzcheck beachten.
- **RED:** nur Recherche/Reconstruction; keine direkte Medienveröffentlichung.

## KI-Aufbereitung von Originals

Originale dürfen für Retention und visuelle Konsistenz editorial aufbereitet werden: Cleanup, Color Grade, Detail-Crops, Parallax, Depth, Matte Expansion, isolierte Objekte, native NOESIS-Callouts und Motion-Composites.

Nicht erlaubt ist dabei eine faktische Verfälschung: kein erfundener Dokumenttext, keine veränderten Messdaten, keine falsche Datierung/Identität/Provenienz und kein Kontextbild als angebliches Foto eines konkreten Experiments.

## Wichtige redaktionelle Locks

- generische Schlaflaborbilder nie als Takeuchi-Originalversuch ausgeben;
- historische Salem-Darstellungen mit Jahr bzw. als spätere Darstellung kennzeichnen;
- Burney Relief nicht als sicher identifizierte Lilitu behandeln;
- Jinn-/Japan-Ikonografie illustriert kulturelle Deutungsräume, keine direkte genealogische Beweiskette;
- Roswell/Area 51 nur UFO-Kultur-/Institutionenkontext, nie Beweis für Abduction oder Schlafparalyse;
- Radio-/Modem-/CRT-Objekte als Periodenkontext nutzen, nicht als Art Bells konkretes Studioequipment behaupten.
