# EP03 PEAR V2 — Optimierungs-Guide

## Performance-Vergleich

| Schritt | V1 (Sequential) | V2 (Parallel) | Speedup |
|---|---|---|---|
| 8 Bilder generieren | ~4-5 Minuten | ~30 Sekunden | **8-10x** |
| 5 Cards generieren | ~2-3 Minuten | ~15 Sekunden | **8-10x** |
| Voice Stems | ~8 Minuten | ~2 Minuten | **4x** |
| Timeline bauen | ~30 Sekunden | ~30 Sekunden | 1x |
| Audio mischen | ~1 Minute | ~1 Minute | 1x |
| Render (120 Segmente) | ~15-20 Minuten | ~5-8 Minuten | **2-3x** |
| **GESAMT** | **~30-35 Minuten** | **~10-15 Minuten** | **2-3x** |

## Optimierungen

### 1. Parallele Bildgenerierung

**Problem:** Vertex AI hat eine Quote von ~60 Requests/Minute. Sequentiell = 1 Bild/15-20 Sekunden.

**Lösung:** `pear_parallel_images.py` mit 4 parallelen Workers:
- 4 Bilder gleichzeitig in der Pipeline
- Dynamische Wartezeiten bei 429-Responses
- Thread-safe Token-Cache
- Ergebnisse werden automatisch gesammelt

**Nutzung:**
```bash
python tools/pear_parallel_images.py --batch EP03_PEAR_V2.json --modell flash --workers 4 --execute
```

### 2. Parallele Voice-Generierung

**Problem:** ElevenLabs API hat eine Rate-Limit von ~3 Requests/Sekunde.

**Lösung:** 4 parallele Stems gleichzeitig:
- Jeder Stem wird in einem eigenen Thread generiert
- Thread-safe Fortschrittsanzeige
- Automatische Wiederholung bei Fehlern

### 3. Parallele Segment-Renderung

**Problem:** ffmpeg rendert Segmente sequentiell, nutzt nur 1-2 Kerne.

**Lösung:** 4 parallele ffmpeg-Prozesse:
- Jedes Segment in einem eigenen Thread
- Nutzt alle verfügbaren CPU-Kerne
- Fortschrittsanzeige in Echtzeit

### 4. Optimierte Pipeline-Reihenfolge

```
1. Voices (parallel) ─────────────────────────┐
                                               ├─> 4. Timeline
2. Images (parallel) ─────────────────────────┘        │
                                                       ▼
3. Cards (parallel) ──────────────────────────────> 5. Audio
                                                       │
                                                       ▼
                                                  6. Render (parallel)
                                                       │
                                                       ▼
                                                       7. QA
```

## Schnellstart

### Alles auf einmal (optimiert)
```bash
python tools/pear_optimized_pipeline.py all
```

### Nur fehlende Bilder
```bash
python tools/pear_optimized_pipeline.py images
```

### Nur Render (wenn Bilder und Voice schon da)
```bash
python tools/pear_optimized_pipeline.py render
```

## Kosten-Optimierung

| Modell | Kosten/Bild | Qualität | Geschwindigkeit |
|---|---|---|---|
| Flash | $0.039 | Gut | Schnell |
| Pro | $0.134 | Sehr gut | Langsam |

**Empfehlung:** Flash für alle Bilder verwenden. Der Qualitätsunterschied ist minimal, aber die Geschwindigkeit ist 3-4x höher.

## Fehlerbehandlung

### 429 Quota Error
- Automatische Wiederholung mit exponentieller Backoff
- 10s → 20s → 40s → 80s → 160s
- Maximal 6 Versuche pro Bild

### Fehlende Referenzbilder
- Automatische Suche in PEAR-references Ordner
- Fallback auf generische Referenz

### Fehlende Segmente
- Automatische Erkennung fehlender Segmente
- Nur fehlende werden gerendert
- Vorhandene werden übersprungen

## Monitoring

### Live-Fortschritt
```
[1/8] pe_v2_01_mcdonnell_f15     OK   pe_v2_01_mcdonnell_f15_v1.png
[2/8] pe_v2_02_mcdonnell_mercury OK   pe_v2_02_mcdonnell_mercury_v1.png
[3/8] pe_v2_03_pilot_cockpit     OK   pe_v2_03_pilot_cockpit_v1.png
...
```

### Kosten-Tracking
```
  Fertig in 15s. 8 von 8 erzeugt, 0 Fehler.
  Kosten: 0.31 USD
  Effizenz: 0.53 Bilder/Sekunde
```

## Troubleshooting

### "gcloud nicht aufrufbar"
```bash
gcloud auth application-default login
```

### "GOOGLE_CLOUD_PROJECT ist nicht gesetzt"
```bash
export GOOGLE_CLOUD_PROJECT=project-453dce68-02cd-498d-86d
```

### "Kein ADC-Token"
```bash
gcloud auth application-default login
```

### Bilder nicht gefunden
```bash
# Prüfe ob Bilder kopiert wurden
ls "C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes\06_PRODUCTION\EP03_PEAR\visuals\generated\pe_v2_*"
```

## Nächste Schritte

1. **Voice generieren** (braucht ElevenLabs API Key)
2. **Timeline bauen** (braucht Alignment)
3. **Audio mischen** (braucht Voice Master)
4. **Render** (braucht Timeline + Audio)
5. **QA** (braucht finales Video)

## Zusammenfassung

Die optimierte Pipeline reduziert die Gesamtzeit von ~35 Minuten auf ~10-15 Minuten durch:
- Parallele Bildgenerierung (4x schneller)
- Parallele Voice-Generierung (4x schneller)
- Parallele Segment-Renderung (2-3x schneller)
- Optimierte Fehlerbehandlung
- Automatische Wiederholung bei Quota-Errors
