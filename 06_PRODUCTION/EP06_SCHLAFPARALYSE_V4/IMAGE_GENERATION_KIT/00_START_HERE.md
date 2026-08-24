# EP06 — Image Generation Kit

**Status:** READY  
**Prompts:** 40 (32 MAIN + 8 RESERVE)  
**Style-Master:** 3  
**Style-Referenzen:** 3/3 als echte Dateien vorhanden  
**Sach-/Personenreferenzen:** 5/5 vorhanden

## Startreihenfolge

1. `GENERATION_QUEUE.csv` öffnen.
2. MAIN- und danach bei Bedarf RESERVE-Zeilen ausführen. **Jede in den Promptdateien genannte Referenz liegt unter exakt diesem Namen in `02_ASSETS/`.**
3. Ergebnisse mit dem vorgegebenen Namen in `03_GENERATED_OUTPUT/` speichern.
4. Die STYLE_MASTER-Zeilen sind bereits erledigt; sie bleiben nur als reproduzierbare Prompts im Guide erhalten.

## Ordner

- `01_PROMPTS/` — Guide und vier Prompt-Batches
- `02_ASSETS/` — **alle Referenzen flach in einem Ordner**, einschließlich der fertigen Style-Master unter exakt den Prompt-Namen
- `03_GENERATED_OUTPUT/` — MAIN/RESERVE-Ergebnisse

## Prüfung

- Keine Pflichtreferenz fehlt.
- Keine Style-Referenz fehlt.
- Der optionale Manifest-Pool ist vollständig.
- `ASSET_AUDIT.json` enthält die maschinenlesbare Vollständigkeitsprüfung.
- `ASSET_INDEX.csv` listet neuen Namen, ursprünglichen Downloadnamen, Rechte-Ampel und Prompt-Pflichtstatus.

Wichtig: YELLOW-Assets bleiben vor dem finalen Einsatz reviewpflichtig. RED-/URL-Recherchelinks werden bewusst nicht in `02_ASSETS/` kopiert.
