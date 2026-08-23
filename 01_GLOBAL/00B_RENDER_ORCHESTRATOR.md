# NOESIS — Individualisierter Render-Orchestrator

**Status:** technischer Produktionslayer für EP04A, EP04B, EP05, EP06, EP07, EP08  
**Ausführung:** lokal  
**Engine:** `tools/noesis_render.py`

## Grundprinzip

Der Renderer ist gemeinsam, die Folge bleibt individuell.

Er erzwingt **keine** globale Laufzeit, Shotzahl, Standzeit, Stemzahl oder identische Kamerafahrt. Die tatsächlichen Beat-Grenzen kommen aus dem Forced Alignment der fertigen Voice. Die kreative Dramaturgie kommt aus dem jeweiligen `VISUAL_CUE_SHEET`, dem finalen lokalen Asset-Manifest und dem Episodenprofil.

Damit bleibt `01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md` maßgeblich: Zahlen aus Gateway/PEAR/SPG sind Referenzen und QA-Signale, keine Quoten.

## Episodenprofile

- **EP04A / Jung & Kundalini:** `vision` — mehr Tiefe, langsamere Holds, stärkere Ruhe bei Symbolbildern.
- **EP04B / Chakra-Genealogie:** `archive` — kontrollierte horizontale Dokumentfahrten, geringere Zoomamplitude.
- **EP05 / Jung & Pauli:** `precision` — sachlich-präzise Fahrten für Dokumente, Briefe, Diagramme und Personenwechsel.
- **EP06 / Schlafparalyse I:** `intimate` — zurückhaltende Nähe, keine Horror-Kameraführung.
- **EP07 / Schlafparalyse II:** `archive` — quellen- und dokumentorientiert, besonders ruhig.
- **EP08 / Schlafparalyse III:** `network` — etwas dynamischer für Medien-/Netzwerkmutation, ohne Social-Media-Hektik.

Alle Profile verwenden geglättete Ken-Burns-Fahrten mit Oversampling (`SUB=4`) und übernehmen die etablierte Zappel-QA aus `tools/spg_zappelpruefung.py`.

## Lokaler Ablauf

Nach fertiger Voice + Forced Alignment + lokal vorhandenen Bildern/Clips:

```bash
python tools/noesis_render.py EP04A doctor
python tools/noesis_render.py EP04A manifest
python tools/noesis_render.py EP04A plan
python tools/noesis_render.py EP04A all
```

Analog mit `EP04B`, `EP05`, `EP06`, `EP07`, `EP08`.

### `doctor`
Prüft Cue Sheet, Voice-Master, Forced Alignment, ffmpeg und ffprobe.

### `manifest`
Durchsucht lokale `04_ASSETS/`, `05_GENERATED/` sowie episodenspezifische `06_PRODUCTION/.../visuals`/`motion`-Ordner. Eindeutige Cue-IDs/Asset-Tokens werden automatisch zugeordnet. Ergebnis:

```text
06_PRODUCTION/<EPISODE>/render_manifest.json
```

Ein Cue kann entweder auf **eine Datei** oder auf **eine Liste von Dateien** zeigen. Eine Liste wird innerhalb des echten Voice-Fensters dieses Cues/Akts in einzelne Shots expandiert. Dadurch wird die Shotmenge vom tatsächlich ausgewählten Material bestimmt und bleibt vollständig episode- und beat-spezifisch.

Nicht eindeutig auflösbare Cues bleiben leer und werden **nicht erfunden**. Dort wird einmalig der korrekte lokale Pfad bzw. die gewünschte Pfadliste eingetragen.

Für EP06–EP08 ist diese Listenfunktion zentral, weil deren Cue-Sheets bewusst aktbasiert sind. Details: `03_EPISODEN/TYPE_B/SCHLAFPARALYSE_RENDER_HANDOFF_V4.md`.

### `plan`
Liest das Forced Alignment und baut eine wortverankerte Timeline. Die Dauer jedes Cue-/Aktfensters endet am nächsten Voice-Anker; der letzte endet am echten Voice-Master. Enthält ein Manifest-Eintrag mehrere Assets, werden sie nur innerhalb dieses Fensters verteilt. Kein Zielruntime-Backfill und keine globale Shotzahl.

### `render`
Rendert die Bildsegmente lokal mit dem jeweiligen Episodenprofil. Hoch-/Querformat wird wie in der bewährten Gateway/PEAR/SPG-Linie behandelt; nicht-16:9-Material wird vollständig eingepasst statt inhaltlich abgeschnitten.

### `final`
Verkettet die Segmente und muxxt den besten vorhandenen lokalen Master/Mix; falls noch kein Mix vorhanden ist, wird der Voice-Master verwendet. Die eigentliche Musik-/SFX-Erzeugung bleibt im jeweiligen Episoden-Audio-Workflow.

### `qa`
Prüft Segmentexistenz und Dauer; anschließend wird — sofern verfügbar — die bestehende Zappelprüfung gegen die gerenderten Kamerafahrten ausgeführt. Lange Holds werden als Hinweis gemeldet, aber nicht automatisch verboten: ob ein starkes Bild länger stehen darf, bleibt eine Entscheidung der Folge.

### `all`
`manifest -> timeline -> render -> final -> qa`

## Fail-closed-Regeln

- Kein Render mit fehlenden/unaufgelösten visuellen Cues.
- Keine erfundene Archivdatei, kein stiller Ersatz durch Stockmaterial.
- Der Renderer entscheidet keine historischen Rechtefragen; die GREEN/YELLOW/RED-Logik der Asset-Pakete bleibt vorgeschaltet.
- Motion-Graphics, deren finaler Clip noch nicht existiert, müssen lokal als Datei vorliegen oder im `render_manifest.json` explizit zugeordnet werden.
- Endcard-Länge bleibt eine Episodenentscheidung und wird nicht global erzwungen.

## Git vs. lokal

Git enthält Engine, Cue Sheets, Prompts, Produktionslogik und technische Regeln. Große Bilder, Voice-/Audio-WAVs, Alignment-Runtime-Outputs, Timeline-JSONs, Segmente und Finalvideos bleiben gemäß `.gitignore` lokal.

Das Ziel ist: **Voice und Assets fertig -> ein lokaler Orchestrator-Befehl -> individueller NOESIS-Rohschnitt/Finalrender**, ohne die Folgen auf dieselbe Schablone zu zwingen.
