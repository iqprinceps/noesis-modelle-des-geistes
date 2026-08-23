# EP05 V5 — Source Asset Download Map

**Status:** PRODUKTION  
**Zweck:** Exakte lokale Dateinamen für Referenzen, Schnitt und Prompt-Batches.

## Pflicht-Originale

### SRC01_Wolfgang_Pauli_1924.jpg
- Motiv: Wolfgang Pauli, 1924
- Quelle: Wikimedia Commons — `File:Wolfgang_Pauli.jpg`
- Source page: `https://commons.wikimedia.org/wiki/File:Wolfgang_Pauli.jpg`
- Einsatz: Identitätsreferenz für AI + Originalbild im Schnitt
- Gate: Lizenz-/PD-Block der konkreten Description Page beim Download archivieren

### SRC03_Solvay_Conference_1927.jpg
- Motiv: Solvay-Konferenz 1927
- Quelle: Wikimedia Commons — bevorzugt hochauflösende freigegebene Fassung
- Source pages:
  - `https://commons.wikimedia.org/wiki/File:Solvay_conference_1927.jpg`
  - Alternative: `https://commons.wikimedia.org/wiki/File:Solvay_conference_1927_Version2.jpg`
- Einsatz: harte wissenschaftliche Realität / Pauli-Crop
- Gate: PD-Begründung der tatsächlich geladenen Datei archivieren

### SRC05_Carl_Gustav_Jung_Portrait.jpg
- Motiv: C. G. Jung
- Quelle: Wikimedia Commons — `File:Carl_Gustav_Jung_portrait.jpg`
- Source page: `https://commons.wikimedia.org/wiki/File:Carl_Gustav_Jung_portrait.jpg`
- Einsatz: Identitätsreferenz + Originalanker S2/S4/S8
- Gate: konkreten PD-Status archivieren

### SRC06_ETH_Zuerich_Historical.jpg
- Motiv: historische ETH Zürich
- Quelle: Wikimedia Commons — `File:ETH_Zuerich_1880.jpg`
- Source page: `https://commons.wikimedia.org/wiki/File:ETH_Zuerich_1880.jpg`
- Einsatz: Institutionsanker
- Claim-Gate: Jahreszahl sichtbar/Source-Line; niemals als exakte Aufnahme von Paulis ETH-Jahren verkaufen

### SRC07_Johannes_Kepler_Portrait.jpg
- Motiv: Johannes Kepler
- Quelle: Wikimedia Commons — `File:Portrait_of_Johannes_Kepler.jpg`
- Source page: `https://commons.wikimedia.org/wiki/File:Portrait_of_Johannes_Kepler.jpg`
- Einsatz: Originalanker S7 + optionale AI-Identitätsreferenz
- Gate: PD-Status archivieren

### SRC08_Cetonia_Aurata_Species.jpg
- Motiv: Rosenkäfer / Cetonia aurata
- Quelle: Wikimedia Commons
- bevorzugt: `https://commons.wikimedia.org/wiki/File:Cetonia_aurata.jpg`
- Alternative CC0: `https://commons.wikimedia.org/wiki/File:Cetonia-aurata-21-fws.jpg`
- Einsatz: Artenreferenz / zoologischer Originalanker
- Claim-Gate: im Schnitt als `ROSENKÄFER · ARTBEISPIEL` oder gleichwertig kennzeichnen; nie als Jungs konkretes Tier ausgeben

## Dokument-Reveals

### DOC01_JUNG_PAULI_LETTER
**Default:** NICHT als Scan einplanen.

CERN/Pauli-Archivmaterial ist urheber-/reproduktionsrechtlich nicht automatisch frei. Ein echter Scan darf erst nach explizit geklärter Reproduktionsfreigabe in den Film.

**Produktionsfallback:**
- echte bibliografische Daten/Datum aus verifizierter Quelle
- neutrale moderne Editorial-Grafik oder generische Papierrekonstruktion
- keine erfundene Handschrift, kein Fake-Briefkopf, kein erfundenes Zitat

### DOC02_NATURERKLAERUNG_UND_PSYCHE_1952
**Default:** bibliografische Grafik `G10` aus `MOTION_GRAPHICS_V5.md`.

Verifizierte Kerndaten:
- Werk: *Naturerklärung und Psyche*
- Autoren/Beiträge: C. G. Jung + Wolfgang Pauli
- Verlag: Rascher
- Ort: Zürich
- Jahr: 1952

Ein echter Buch-/Titelblatt-Scan wird nur eingesetzt, wenn die konkrete Reproduktion für den Kanal geklärt ist. Das Publikationsjahr allein macht den Scan nicht frei.

## Download-Ordner

Empfohlen:
`05_GENERATED/EP05_JUNG_PAULI_V5/REFERENCES/`

Darin exakt die oben definierten Dateinamen verwenden, weil die Prompt-Batches diese Namen referenzieren.

Zusätzlich pro Original eine `.source.txt` oder Source-Manifest-Zeile ablegen mit:
- Source URL
- Urheber, wenn angegeben
- Lizenz/PD-Begründung
- Download-Datum
- etwaige Attribution

## Red Flags

Nicht verwenden:
- Pinterest-/Blog-Reuploads ohne Provenienz
- moderne kolorierte historische Fotos mit unklaren Bearbeitungsrechten
- CC BY-NC für monetarisierbaren Kanal
- CC BY-ND, wenn Crop/Kamerafahrt/Farbkorrektur nötig ist
- AI-Faksimiles echter Briefe oder Buchseiten
- vermeintliche Weltuhr-Buchscans ohne Rechteklärung
