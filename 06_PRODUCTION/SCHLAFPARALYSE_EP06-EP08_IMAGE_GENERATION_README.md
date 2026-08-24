# Schlafparalyse EP06–EP08 — Bildgenerierung

**Status:** READY FOR GENERATION  
**Stand:** 24.08.2026

Die Prompt- und Asset-Kits liegen getrennt nach Episode:

- `EP06_SCHLAFPARALYSE_V4/IMAGE_GENERATION_KIT/`
- `EP07_SCHLAFPARALYSE_V4/IMAGE_GENERATION_KIT/`
- `EP08_SCHLAFPARALYSE_V4/IMAGE_GENERATION_KIT/`

Jeder Kit enthält:

- `00_START_HERE.md` — konkrete Reihenfolge
- `GENERATION_QUEUE.csv` — Style-Master, MAIN und RESERVE in Ausführungsreihenfolge
- `01_PROMPTS/` — Guide und Prompt-Batches
- `02_ASSETS/` — alle verwendbaren Referenzen der Episode flach und unter exakt den Prompt-Namen; einschließlich der fertigen Style-Master
- `03_GENERATED_OUTPUT/` — fertige KI-Bilder
- `ASSET_INDEX.csv` — neuer Name, ursprünglicher Downloadname, Rechte-Ampel und Prompt-Pflichtstatus
- `ASSET_AUDIT.json` — Vollständigkeitsstatus

## Ergebnis des Abgleichs

| Episode | Direkte Prompts | Style-Master-Dateien | Sach-/Personenreferenzen | Status |
|---|---:|---:|---:|---|
| EP06 | 40 | 3/3 | 5/5 | READY |
| EP07 | 24 | 3/3 | 4/4 | READY |
| EP08 | 40 | 3/3 | 1/1 | READY |

Alle neun Style-Referenzen sind als echte PNG-Dateien vorhanden. Die drei zu dunklen Master wurden in einer helleren, auf Laptop- und Handybildschirmen besser lesbaren Fassung ersetzt. Zusätzlich enthält jeder lokale Bildprompt eine verbindliche Helligkeitsregel: offene Mitteltöne, sichtbare Schattendetails, klare Motivtrennung und keine großflächig abgesoffenen Schwarzbereiche.

Die Richard-Coman-Referenz in EP07 wurde auf den real vorhandenen Dateinamen mit `.pdf` normalisiert.

Vier zusätzliche Salem-Archivdateien sind derzeit nicht lokal verfügbar, weil das Massachusetts-Archiv automatisierte Abrufe serverseitig blockiert. Sie sind optionale Source-Pool-Erweiterungen und werden von keinem aktuellen KI-Prompt verlangt; Details stehen in `EP07_SCHLAFPARALYSE_V4/IMAGE_GENERATION_KIT/ASSET_AUDIT.json`.

## Neu aufbauen oder aktualisieren

Vom Repository-Root:

```powershell
python tools/prepare_schlafparalyse_image_kits.py
```

Der Builder prüft Promptanzahl, Referenznamen und die lokale Existenz **jeder** genannten Datei – einschließlich der Style-Master – und kopiert die kanonischen Dateien erneut in die Episoden-Kits.
