# Schlafparalyse-Serie — Canonical Asset Index V5

**Stand:** 24.08.2026  
**Status:** PRODUCTION READY / CANONICAL

## Source of truth

`asset_manifest_v5.json` ist der **kanonische Einstiegspunkt**. Er umfasst:

- `asset_manifest.csv` — 49 Basisassets
- `asset_manifest_v5_additions.csv` — 2 V5-Additions
- `asset_manifest_v5_expansion.csv` — 25 zusätzliche Assets

Alle Source-Links, Direktdownloads, Lizenzampeln, Dateinamen und Zielordner stehen in diesen drei CSV-Layern. Der V5-Downloader verarbeitet sie gemeinsam.

## Bestand

- **76 eindeutige Asset-Einträge**
- **46 GREEN / 19 YELLOW / 11 RED**
- **65 automatisch downloadbar**
- **EP06: 22 Assets inkl. Shared**
- **EP07: 28 Assets**
- **EP08: 32 Assets inkl. Shared**

Damit sind die zuvor gesetzten Original-/Kontextziele erreicht: EP06 ca. 22–28, EP07 ca. 28–35, EP08 ca. 25–32. Zusammen mit individuellen AI-Recons und Motion-Slots reicht der Pool für rund 146–150 Shots und >90 eindeutige Visuals pro Folge.

## Retention-Regel

Originale sind keine langen Holds. Dokumente werden semantisch geschnitten: Full → Datum/Name → Passage → Detail. Labor-/Technikbilder dienen als kurze 2–5-s-Anker und wechseln sich mit Reconstruction/Motion ab. Kein identischer Frame zweimal, kein Basisasset direkt hintereinander.

## Neu durch die Expansion

### EP06
- Sleep EEG Stage 1 + Stage 2
- zusätzliche Polysomnographie-Spur
- ambulante PSG-Patientenreferenz
- EEG-Cap-Icon und 64-Kanal-EEG-Cap
- zusätzlicher Fogo-Locator

### EP07
- weitere originale Salem-Akten: Tituba/Sarah Good/Sarah Osburn, Rebecca Nurse, Walcott/Hubbard v. Proctor, Mittimus mehrerer Angeklagter
- Salem Village Parsonage Foundation und Proctor’s Ledge
- Jinn-Manuskript sowie japanische Ghost-/Dream-Demon-Kunst

### EP08
- BBS-Screenshot
- mehrere Dial-up-Modems / Modem-PCB
- Monochrom-CRT
- Telefon-/Mikrofon-Assets
- historischer Electro-Artograph/Fax-Kontext

## KI-Aufbereitung

Originalassets dürfen per Cleanup, Grading, Parallax, Depth, Detailcrop, Matte Expansion und Motion-Composite visuell verdichtet werden. Das darf niemals neue historische Beweise erfinden oder Text/Messdaten verändern.
