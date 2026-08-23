# Schlafparalyse EP06–EP08 — Full Production Handoff V5

**Status:** READY FOR V5 PRODUCTION INPUTS  
**Scope:** EP06 / EP07 / EP08  
**Visual Canon:** `SCHLAFPARALYSE_VISUAL_COVERAGE_V5.md`

## Vorbereitung

Vom Repository-Root:

```bash
git pull origin master
python3 tools/prepare_schlafparalyse_v5.py
```

Der V5-Prep nutzt den bewährten V4-Builder für Voice/Audio/Prompt-Unpack und legt danach die individuellen V5-Visualziele darüber.

## Source Assets

```bash
python3 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets_v5.py
```

Der Wrapper lädt das bestehende Phase-2-Manifest plus die verifizierten V5-Additions mit dem robusten Downloader. Bereits vorhandene Dateien werden übersprungen.

## Visuelle Zielwerte

| Episode | Shots | Original | Recon/AI | Motion | erwartete AI-Stills im Edit |
|---|---:|---:|---:|---:|---:|
| EP06 | 149 | 58 | 63 | 28 | 48–54 |
| EP07 | 146 | 88 | 27 | 31 | 26–32 |
| EP08 | 150 | 58 | 57 | 35 | 50–58 |

Ein Basisbild darf nur dann mehrere Shots liefern, wenn die Crops unterschiedliche Informationen zeigen. Identische Frames oder reine Ken-Burns-Varianten gelten nicht als neue Motive.

## Bildworkflow

1. episodisches `VISUAL_COVERAGE_V5.md` lesen.
2. echte Originalassets zuerst konkreten Sprecherbeats zuweisen.
3. Dokumente/Kunst in semantisch unterschiedliche Crops zerlegen, wenn verschiedene Aussagen dieselbe Quelle betreffen.
4. Motion-/Diagramm-Slots planen.
5. AI selektiv aus dem V4-Prompt-Pool erzeugen; `SCHLAFPARALYSE_PROMPT_STRATEGY_V5.md` steuert die Auswahl.
6. `06_PRODUCTION/<episode>/render_manifest.json` pro Cue mit einem oder mehreren konkreten Medienpfaden füllen.
7. Renderer expandiert Listen innerhalb des Cue-Zeitraums in einzelne Shots.
8. vor Final Render Wiederholung und Coverage prüfen.

## Voice

Voice bleibt auf dem gelockten George-Setup: `JBFqnCBsd6RMkjVDRZzb`, `eleven_multilingual_v2`, stability 0.58, similarity 0.80, style 0.08, speed 1.06, speaker boost true, seed 2402.

Beispiel EP06:

```bash
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP06_SCHLAFPARALYSE_V4/voice/voice_batch_v4.json --execute
python3 tools/schlafparalyse_voice.py EP06 all
```

## Render

```bash
python3 tools/noesis_render.py EP06 manifest
python3 tools/noesis_render.py EP06 timeline
python3 tools/noesis_render.py EP06 render
```

Analog EP07 / EP08.

Der Renderer darf fehlende Coverage nicht durch lange Holds kaschieren. Hohe Bilddichte wird im Manifest geplant, nicht durch Zoom simuliert.

## Episodenstrategie

- **EP06:** echte Science-/PSG-/Lab-Originale erden subjektive Bedroom-/Presence-Recons.
- **EP07:** Originalakten, Kunst, Karten und historische Dokumente dominieren; KI dient nur räumlicher/subjektiver Rekonstruktion.
- **EP08:** Radio-/Fax-/CRT-/Modem-/Research-Originale wechseln mit Shadow-/Hat-Man-Recons und Feedback-Motion.

## Runtime Outputs — nicht in Git

Voice-/Audio-Dateien, Forced Alignment, heruntergeladene Source-Medien, generierte AI-Bilder, Audio-Stems, Rendersegmente und finale Exporte bleiben lokal. Textbasierte Produktionspläne, Manifeste, QA, Cue-Sheets und Scripts dürfen im Repo bleiben.

## Final Gate

Final-ready bedeutet:
- Shot-Target ungefähr erreicht;
- kein Still >9 s;
- kein identischer Frame wiederholt;
- keine sichtbare Motivschleife;
- Mix entspricht ungefähr dem Episodenlock;
- zentrale Sprecherbeats sind konkret bebildert;
- historische/technische Kontexte korrekt beschriftet;
- YELLOW-Assets reviewt und Credits geklärt.
