# Schlafparalyse V4 — Production Ready Lock

**Folgen:** EP06–EP08  
**Status:** READY FOR PRODUCTION nach Asset-Download + YELLOW-Review  
**Promptformat:** an JUNG V4 / PEAR-Produktionslogik angeglichen

## Enthalten

Für jede Folge sind im repo-ready Prompt-Paket enthalten:
- `NANOBANANA_GUIDE_V4.md` — Format, 3 Style-Anker, Reference Map und Reserve-Prompts
- `NANOBANANA_PROMPTS_V4_S1_S2.md`
- `NANOBANANA_PROMPTS_V4_S3_S4.md`
- `NANOBANANA_PROMPTS_V4_S5_S6.md`
- `NANOBANANA_PROMPTS_V4_S7_S8.md`

Jede Folge enthält exakt **56 MAIN + 8 RESERVE** Bildprompts.

Serienweit vorhanden:
- `SCHLAFPARALYSE_SERIE_V2_RETENTION_VISUAL_PLAN.md`
- `SCHLAFPARALYSE_ASSETS_PHASE2/` mit Manifest, Downloader, Credits, Rights-Ampel und Dry-Run
- Voice-Authenticity-Fassungen der Drehbücher EP06–EP08

## Produktionsreihenfolge

1. `SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets.py` ausführen.
2. YELLOW-Dateien im Credits/Manifest kurz freigeben oder aus Referenzsets entfernen.
3. Pro Episode zuerst die drei `STYLE_*`-Bilder aus `NANOBANANA_GUIDE_V4.md` erzeugen.
4. Danach die vier Main-Batches sequenziell abarbeiten.
5. Originalarchive/Dokumente im Schnitt bevorzugen; AI nur dort, wo kein sauberes Original existiert oder eine erklärende/rekonstruktive Szene gebraucht wird.
6. Generierte historische Szenen beim ersten Auftreten als Rekonstruktion kenntlich machen, wenn sonst Archivcharakter suggeriert würde.

## Referenz-Lock

- Alle faktischen `Referenz:`-Dateinamen wurden gegen das aktuelle Asset-Manifest geprüft.
- Keine `.url.txt`-Researchdatei wird als Bildreferenz verwendet.
- Keine PDF-Datei wird als direkte Bildreferenz verwendet.
- YELLOW-Referenzen sind in den Guides als Review-pflichtig gekennzeichnet.

## Qualitäts-Lock

- 16:9 Hauptframes
- keine generischen Neon-/Cyberpunk-Horrorwelten
- keine falschen historischen Dokumente
- keine behaupteten Dämonen/Entitäten als bewiesene Realität
- keine falsche visuelle Genealogie zwischen Lilitu/Lilith/Incubus
- Burney Relief nur als umstrittener historischer Echo-Anker
- Roswell/Area 51 nur als UFO-Kulturkontext, nicht als Alien-Abduction-Beweis
- Takeuchi-Labor generisch rekonstruiert, nie als Originalfoto ausgegeben
- Art-Bell-Studio rekonstruiert; CC0-Porträt darf als echte Personreferenz dienen
- reale Forscher ohne sauber lizenzierte Porträts nicht fotorealistisch exakt imitieren

## Coverage

- EP06: 56 MAIN + 8 RESERVE AI-Bilder; Wissenschaft/Archive zusätzlich
- EP07: 56 MAIN + 8 RESERVE AI-Bilder, aber im finalen Schnitt wegen Archivstärke weniger AI nutzen; Originals priorisieren
- EP08: 56 MAIN + 8 RESERVE AI-Bilder; Medien-/Technik-Originale zusätzlich

Die Prompt-Batches sind bewusst größer als der tatsächliche AI-Anteil im finalen Film. Sie sind ein Coverage-Pool; der Schnitt hält weiterhin die Serienvorgabe von ca. 145–155 Shots und mindestens 85 Einzelmotiven pro Folge.