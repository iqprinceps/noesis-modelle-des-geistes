# Repository-Struktur und Ablageregeln

## Zweck

GitHub ist die lesbare, versionierte Quelle für Drehbücher, Recherchelogik,
Prompts, Metadaten, Timelines, QA-Berichte und Produktionscode. Große binäre
Medien bleiben lokal. Dadurch kann ChatGPT neue Themen verstehen und auf dem
vorhandenen Niveau weiterentwickeln, ohne sich durch Renderreste zu arbeiten.

## Lebenszyklus einer Episode

1. **Themenentwicklung:** `03_EPISODEN/<TYPE>/<EPISODE>/`
2. **Deutsche Produktion:** `06_PRODUCTION/<EPISODE>/`
3. **Englische Adaption:** `07_ENGLISH_PRODUCTION/<EPISODE>/`
4. **Pipeline-Übergabe:** `PRODUCTION_SUMMARY/<EPISODE>/`, wenn bestehende
   Werkzeuge diesen Pfad benötigen.
5. **Veralteter, nicht mehr kanonischer Stand:** `99_ARCHIVE/` oder ein klar
   benannter `SUPERSEDED_*`-Ordner innerhalb der Episode.

Neue Dateien werden nicht lose im Repository-Root abgelegt. Allgemeine
Werkzeuge gehören nach `tools/`; episodenexklusive Werkzeuge bleiben im
jeweiligen Episodenordner.

## Empfohlener Episodenvertrag

```text
EPxx_NAME/
  README.md
  episode.json
  01_SCRIPT/
    VOICE_SCRIPT_<LANG>.txt
    EDITORIAL_MAP.md
    SCRIPT_QA.md
    CLAIMS_BOUNDARY.md
  02_VOICE/
    PRONUNCIATION_SHEET.md
    manifest.json
  03_VISUALS/
    VISUAL_RETENTION_PLAN.md
    SOURCE_AND_RIGHTS_REGISTER.md
    ASSET_ACQUISITION_PLAN.md
  04_AUDIO/
    AUDIO_PLAN.md
  05_TIMELINE/
  06_RENDER/
  07_THUMBNAIL/
  08_SUBTITLES/
  09_UPLOAD/
    SEO_PROFILE.md
```

Nicht jede frühe Drehbuchaufgabe muss alle Ordner füllen. Der kanonische
Sprechertext bleibt aber immer unter `01_SCRIPT/` und wird nicht in einem
Render- oder Uploadordner versteckt.

## Versionen

- Der aktuell verwendete Text heißt `VOICE_SCRIPT_EN.txt` oder
  `VOICE_SCRIPT_DE.txt` und ist die kanonische Quelle.
- Frühere Fassungen werden nicht als `final_final_v2` daneben gelegt. Sie
  bleiben in Git-History oder wandern begründet nach `SUPERSEDED_*`.
- Ein Versionsordner wird nur angelegt, wenn eine bestehende Pipeline ihn
  benötigt. `PRODUCTION_SUMMARY/` bleibt deshalb vorerst pfadstabil.
- Umzüge produktionskritischer Ordner erfordern gleichzeitig aktualisierte
  Referenzen und einen Pfadtest.

## Was GitHub enthält

Erwünscht sind insbesondere `.md`, `.txt`, `.json`, `.csv`, `.srt`, `.vtt`,
`.ass`, `.py`, `.ps1`, `.yaml`, `.yml`, `.toml`, `.html`, `.js`, `.css` und
kleine textbasierte Grafiken.

Nicht ins Repository gehören Stimmen, Musik, Render, Bildgenerationen,
Kontaktbögen, Rohclips, lokale Caches, API-Schlüssel oder heruntergeladene
Original-PDFs. Ihre Herkunft und Verwendung wird stattdessen in Manifesten
dokumentiert.
