# EP07 - Wiederholungs-, Original- und Motion-Audit

**Prüfquelle:** `EP07_VOICE_VISUAL_SYNC.csv`  
**Stand:** nach verbindlichem Sync-/Edit-Lock  
**Ergebnis:** Planung besteht alle maschinell prüfbaren Limits

## Messwerte

| Prüfung | Ergebnis | Limit | Status |
|---|---:|---:|---|
| Sync-Zeilen | 146 | 140-155 | PASS |
| eindeutige konkrete `asset_path` | 136 | mindestens 125 | PASS |
| Wiederholungs-Slots über den ersten Einsatz hinaus | 10 / 146 = 6,85 % | höchstens 15 % | PASS |
| maximale Nutzung eines konkreten `asset_path` | 2 | höchstens 2 normal | PASS |
| direkte identische Folgeframes | 0 | 0 | PASS |
| Hauptclips in der Timeline | 4 | 3-5 | PASS |
| wiederholte Hauptclips | 0 | 0 | PASS |
| Generated-Still-Slots mit Bewegung | 32 / 71 = 45,07 % | 40-60 % | PASS |
| Kartenzeit | 53 / 652 s = 8,13 % | 8-12 % | PASS |
| bewegte Karten | 0 / 7 | 0 | PASS |
| Original-/Quellenzeit | ca. 276,96 / 652 s = 42,48 % | EP07: 35-45 % | PASS |

## Bestands- und Lückenstatus

| Klasse | Slots | konkrete Einheit |
|---|---:|---|
| vorhandene Karten | 7 | alle READY |
| vorhandene Hauptclips | 4 | jeder genau einmal |
| vorhandene Generated-Stills | 30 Slots | aus dem freigegebenen 20+4-Pool, teils maximal zweimal |
| vorhandene Quellenableitungen | 47 | aus lokalen Originalen statisch zu exportieren |
| fehlende Originalquellen-Exports | 17 | aus zehn noch zu beschaffenden Masterquellen |
| fehlende neue Bildmotive | 37 | präzise in `EP07_MISSING_ASSETS_AND_PROMPTS.md` spezifiziert |

Die hohe Zahl geplanter Ergänzungen ist Absicht: EP04A zeigte zu lange Holds und zu viele Wiederholungen. EP07 schließt jede Voicepassage mit einem inhaltlich eigenen Bild, statt die vorhandenen 24 KI-Stills durch stärkere Kamerafahrten künstlich zu verlängern.

## Wie gezählt wurde

- Wiederholung wird über den konkreten `asset_path` gezählt, nicht über eine freie Beschreibung.
- `repeat_slots = Summe(max(0, Nutzung je asset_path - 1))`.
- Dokument- und Kunstcrops erhalten nur dann einen eigenen Exportpfad, wenn Full, Passage oder Detail eine andere Information zeigen. Der unveränderte Masterpfad bleibt zusätzlich in `source_master` nachvollziehbar.
- Ein Clip zählt als Bewegtbild, nicht als bewegter Still. Clipbewegung kommt ausschließlich aus dem Clip selbst.
- `GENTLE_ZOOM_1P5_TO_2P5_PERCENT` zählt als bewegter Still. `HOLD_STATIC`, `LOCKED_STATIC`, Quellen, Karten und Quellenkomposites zählen als statisch.

## Verbindliche Render-Gates

Vor dem Render erneut ausführen:

```text
python tools/build_ep07_voice_visual_sync.py
python tools/check_schlafparalyse_visual_coverage_v5.py EP07
python tools/check_schlafparalyse_edit_policy.py <timeline.json>
```

Der letzte Check erfolgt erst auf der echten, per Forced Alignment aufgebauten Timeline. Planzeiten dürfen nicht als endgültige Untertitel- oder Voicezeiten verwendet werden.

