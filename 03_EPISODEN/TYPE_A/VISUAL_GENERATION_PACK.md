# TYPE A — Visual Generation Pack

## Umfang

- **EP01**: 10:45 min · 96 Voice-Cues · 75 KI/Design Hauptvisuals · 15 Reserve · 21 Originalfoto/Dokument-Cues
- **EP02**: 11:35 min · 101 Voice-Cues · 77 KI/Design Hauptvisuals · 16 Reserve · 24 Originalfoto/Dokument-Cues
- **EP03**: 12:20 min · 110 Voice-Cues · 71 KI/Design Hauptvisuals · 15 Reserve · 39 Originalfoto/Dokument-Cues

## Agenten-Reihenfolge

1. `Rights Agent` prüft/holt Originalassets aus dem bestehenden Asset-Pack.
2. `Voice Agent` rendert die endgültige Narration.
3. `Sync Agent` mapped Voice-Anker auf echte Wort-Timestamps.
4. `Image Agent` rendert alle `role=MAIN`-Zeilen aus `AI_IMAGE_BATCH.csv` in Batches; Reserve erst nach erster Sichtung oder direkt bei günstiger Batch-Produktion.
5. `Document Agent` baut Originalseiten, Crops und Highlights.
6. `Edit Agent` setzt nach `VISUAL_CUE_SHEET.csv` und ersetzt schwache Bilder durch Reserve.
7. `QC Agent` prüft Aussage-Bild-Synchronität, Rechte, Evidenzstatus und 5–8-s-Rhythmus.

## Wichtige Regel

Ein Bild darf nie mehr behaupten als der gesprochene Satz. Bei Hypothesen/Behauptungen: neutrale Rekonstruktion oder klar konzeptuelle Grafik; keine visuelle „Bestätigung“ des behaupteten Phänomens.