# NOESIS — Modelle des Geistes

Produktions- und Drehbuchrepository für den deutschen Kanal **Modelle des
Geistes** und seine englische Ausgabe **NOESIS**.

## Für neue Drehbücher

Der verbindliche Einstieg für ChatGPT und andere Autoren ist
[`02_GUIDES/CHATGPT_DREHBUCH_BRIEF.md`](02_GUIDES/CHATGPT_DREHBUCH_BRIEF.md).
Er erklärt Ton, Retention-Ziel, Evidenzsprache, visuelle Dramaturgie und das
erwartete Dateipaket. Alte Episoden liefern Beispiele, aber keine Schablone.

Die höchste kreative Regel steht in
[`01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md`](01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md):
**Jede Episode wird einzeln aus Zuschauersicht entwickelt und bewertet.** Es
gibt keine universelle Pflichtzahl für Wörter, Akte, Shots, Bilder, Clips,
Karten, SFX, Fragen oder Sekundenmarken.

## Repository-Struktur

| Pfad | Aufgabe |
|---|---|
| `01_GLOBAL/` | Aktuelle kanalweite redaktionelle und technische Standards |
| `02_GUIDES/` | Einstieg, Repository-Logik und Vorlagen für neue Arbeiten |
| `03_EPISODEN/` | Deutsche Themenentwicklung, Recherche und Drehbuchpakete |
| `06_PRODUCTION/` | Deutsche Produktionsstände, Timelines, QA und Pipeline-Dateien |
| `07_ENGLISH_PRODUCTION/` | Kanonische englische Adaptionen und Produktionspakete |
| `PRODUCTION_SUMMARY/` | Pipeline-kompatible Übergaben und historische Zusammenfassungen |
| `tools/` | Produktions-, QA-, Render- und Veröffentlichungswerkzeuge |
| `99_ARCHIVE/` | Klar als veraltet markierte Referenzstände |

Die vollständige Ablagelogik steht in
[`02_GUIDES/REPOSITORY_STRUCTURE.md`](02_GUIDES/REPOSITORY_STRUCTURE.md).
Binäre Rohassets, Stimmen, Render, Thumbnails und Original-PDFs werden lokal
verwaltet und sind bewusst nicht Teil des Git-Repositories.

## Vertex AI

Das getrennte zweite Produktionsprofil fuer Nano Banana Pro und Veo ist in
[`02_GUIDES/VERTEX_AI_SECONDARY_PROFILE.md`](02_GUIDES/VERTEX_AI_SECONDARY_PROFILE.md)
dokumentiert. Generatoren werden ueber
`tools/run_with_vertex_secondary.ps1` gestartet; Zugangsdaten bleiben
ausserhalb des Repositories.

## Starke englische Referenzen

| Episode | Kanonischer Sprechertext | Wofür sie als Referenz dient |
|---|---|---|
| Kozyrev | `07_ENGLISH_PRODUCTION/EP01_KOZYREV/01_SCRIPT/VOICE_SCRIPT_EN.txt` | Objektmysterium, Patent und menschliche Widersprüche |
| Gateway | `07_ENGLISH_PRODUCTION/EP02_GATEWAY/01_SCRIPT/VOICE_SCRIPT_EN.txt` | Akten-Thriller, Quellenenthüllung und eskalierende Theorie |
| Sleep Paralysis I | `07_ENGLISH_PRODUCTION/EP05_SLEEP_PARALYSIS_01/01_SCRIPT/VOICE_SCRIPT_EN.txt` | Körpererfahrung, Laborbefund und übernatürliche Bildwelt |
| Sleep Paralysis II | `07_ENGLISH_PRODUCTION/EP06_SLEEP_PARALYSIS_02/01_SCRIPT/VOICE_SCRIPT_EN.txt` | Kulturgeschichte, Gestalten und kontrastreiche visuelle Reise |

Diese Texte zeigen das Qualitätsniveau. Ein neues Thema übernimmt ihre Stärke,
nicht automatisch ihren Aufbau.

## Entscheidungsreihenfolge

1. Aktuelle ausdrückliche Entscheidung des Kanalinhabers.
2. Individuelle Zuschauerwirkung und Retention der konkreten Episode.
3. Fakten-, Rechte-, Identitäts- und technische Sicherheit.
4. Sprachspezifischer Standard und Episodenunterlagen.
5. Frühere Folgen nur als Vergleich und Lernmaterial.

## Rechte

Drehbücher, Konzepte und selbst erstellter Produktionscode: alle Rechte
vorbehalten. Rechte externer Quellen stehen in den jeweiligen
Quellen-/Lizenzmanifesten.
