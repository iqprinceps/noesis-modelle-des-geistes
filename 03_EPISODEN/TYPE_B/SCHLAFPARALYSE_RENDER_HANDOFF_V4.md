# Schlafparalyse EP06–EP08 — Individualisierter Render-Handoff V4

**Ausführung:** lokal  
**Engine:** `tools/noesis_render.py`  
**Voraussetzung:** `tools/prepare_schlafparalyse_production_inputs.py` + fertige Voice/Forced Alignment + ausgewählte lokale Assets

## Warum der Render hier anders arbeitet

Die `VISUAL_CUE_SHEET.csv` der drei Folgen ist absichtlich **aktbasiert**: S1 bis S8 definieren die dramaturgischen Voice-Fenster, nicht acht fertige Shots.

Der Renderer darf daraus deshalb keine starre Shotzahl ableiten. Stattdessen enthält das lokale `render_manifest.json` für jeden Akt eine **Liste der tatsächlich ausgewählten Bilder/Clips**. Die Länge dieser Liste ist pro Akt und pro Folge frei. Genau diese Liste wird innerhalb des echten Voice-Fensters in einzelne Shots expandiert.

Beispiel:

```json
{
  "assets": {
    "S1": [
      "05_GENERATED/EP06/.../bedroom_wide.png",
      "04_ASSETS/.../sleep_lab_photo.jpg",
      "06_PRODUCTION/EP06_SCHLAFPARALYSE_V4/motion/rem_atonia.mp4"
    ],
    "S2": [
      "04_ASSETS/.../old_hag_source.jpg",
      "05_GENERATED/EP06/.../doorway_presence.png"
    ]
  }
}
```

Das ist **kein Soll für 3 oder 2 Shots**. Es zeigt nur das Format. Wenn S1 sieben Motive braucht und S2 vier, werden sieben bzw. vier gerendert. Wenn ein stärkeres Motiv länger stehen soll, kann die Auswahl kleiner sein. Retention und Verständlichkeit entscheiden, nicht eine globale Zahl.

## EP06

Nach dem Production Prep und Voice-Build:

```bash
python tools/noesis_render.py EP06 doctor
python tools/noesis_render.py EP06 manifest
```

Dann `06_PRODUCTION/EP06_SCHLAFPARALYSE_V4/render_manifest.json` prüfen und S1–S8 mit der finalen Auswahl füllen.

```bash
python tools/noesis_render.py EP06 plan
python tools/noesis_render.py EP06 all
```

Kameraprofil: **`intimate`** — zurückhaltende Nähe, kontrollierte Push-ins, keine Horror-Kameraführung und keine Jump-Scare-Bewegung.

## EP07

```bash
python tools/noesis_render.py EP07 doctor
python tools/noesis_render.py EP07 manifest
# Manifest S1–S8 mit der finalen archivlastigen Auswahl prüfen/füllen
python tools/noesis_render.py EP07 plan
python tools/noesis_render.py EP07 all
```

Kameraprofil: **`archive`** — besonders ruhige Dokument-/Quellenfahrten, niedrige Zoomamplitude. EP07 bleibt visuell quellenlastiger als EP06/EP08, wo das Material dies erlaubt.

## EP08

```bash
python tools/noesis_render.py EP08 doctor
python tools/noesis_render.py EP08 manifest
# Manifest S1–S8 mit der finalen Auswahl prüfen/füllen
python tools/noesis_render.py EP08 plan
python tools/noesis_render.py EP08 all
```

Kameraprofil: **`network`** — etwas beweglicher bei Medien-/Internet-Mutation, aber ohne hektische Social-Media- oder Cyberpunk-Ästhetik.

## Was automatisch passiert

- echte Voice-/Forced-Alignment-Zeiten bestimmen die Aktfenster
- Manifestlisten werden innerhalb dieser Fenster in individuelle Shots expandiert
- Bilder/Clips werden lokal gerendert
- nicht-16:9-Material wird vollständig eingepasst
- geglättete Ken-Burns-Fahrten mit Oversampling
- Aktgrenzen erhalten die zum Episodenprofil passende Transition
- Segmente werden zum Picture Master verkettet
- vorhandener Episode-Mix/Master wird bevorzugt, sonst Voice-Master als technischer Fallback
- Segmentdauer-QA und vorhandene `spg_zappelpruefung.py`

## Fail closed

Der Renderer startet keinen finalen Render, solange ein benötigter Cue/Akt ohne lokale Medienzuordnung bleibt. Er erfindet keine Archivbilder, zieht kein Stockmaterial als Ersatz und überschreibt keine Rechteentscheidung.

## Individueller Qualitätscheck

Nach `plan` die erzeugte Timeline ansehen. Lange Holds sind ein **Hinweis**, keine automatisch verbotene Zahl. Wenn ein Abschnitt visuell zu arm wirkt, mehr passende Assets in genau diesen Akt eintragen. Wenn ein Bild bewusst tragen soll, darf es länger stehen. Die stärkste Folge gewinnt, nicht die gleichmäßigste Tabelle.
