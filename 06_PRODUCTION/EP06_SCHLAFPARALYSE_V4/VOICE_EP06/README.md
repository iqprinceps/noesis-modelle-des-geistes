# EP06 Voice-/Visual-Paket

Dieses Verzeichnis ist die verbindliche Vorstufe für Voice, Schnitt und Audio von EP06. Es wurde an EP04A als Qualitätsmaßstab ausgerichtet, übernimmt dessen Struktur aber nicht schematisch.

## Enthalten

- `EP06_SPRECHERFASSUNG_FINAL.md` — menschlich überarbeiteter, claims-konformer Sprechertext für George.
- `EP06_VOICE_SCRIPT_CLEAN.txt` — identische Reinschrift ohne Überschriften für Alignment und Untertitel.
- `source/` — 26 einzeln nachbesserbare Take-Dateien.
- `take_manifest.csv` — Wortzahl und geschätzte George-Zeit je Take.
- `sync/EP06_VOICE_VISUAL_SYNC.csv` — 152 textankerbasierte visuelle Einsätze plus statische 20-s-Endcard.
- `MISSING_ASSETS_AND_PROMPTS.md` — 11 Originalasset-Lücken, 13 Bildprompts, 7 zusätzliche Karten und 6 Transformationsclips.
- `SEMANTIC_DERIVATIVE_BATCH.md` — 29 neue, textankerspezifische Ersatzshots gegen Bildwiederholung.
- `ORIGINAL_ASSET_REPEAT_AUDIT.md` — Originalanteil, Wiederholungen und Bewegungs-Gates.
- `SFX_MUSIC_CUE_PLAN.md` — vollständiger Stem- und Ereignisplan.

## Aktueller Produktionsstand

- Text: fertig.
- Asset-/Schnittplanung: fertig.
- Voice: noch nicht generiert.
- Fehlende Bilder/Karten/Originale: spezifiziert, noch nicht erzeugt oder beschafft.
- SFX/Musik: geplant, noch nicht gerendert.
- Zeitangaben: Schätzung auf Basis der bisherigen George-Performance; nach Voice durch echtes Forced Alignment ersetzen.

## Nächster sichere Schritt

Zuerst die 66 fehlenden Asset-IDs aus `MISSING_ASSETS_AND_PROMPTS.md` und `SEMANTIC_DERIVATIVE_BATCH.md` schließen und visuell prüfen. Danach George einmal als 26-Take-Batch erzeugen, nur fehlerhafte Takes neu aufnehmen, Forced Alignment laufen lassen und daraus die endgültige Timeline ableiten. Karten bleiben immer statisch; bei Originalen gilt `contain`, kein Beschnitt.
