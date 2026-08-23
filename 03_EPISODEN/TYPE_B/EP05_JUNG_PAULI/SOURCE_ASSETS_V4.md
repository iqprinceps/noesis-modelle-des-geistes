# EP05 V4 — Source Asset Manifest

**Status:** Recherche-Manifest  
**Regel:** Vor finalem Download jeweils die konkrete Description Page mitspeichern/screenshotten und Lizenz/Attribution in der Projekt-Dokumentation festhalten.

## Produktionsbereit / frei nutzbar

### SRC01 — Wolfgang Pauli, 1924
- Titel: `Wolfgang Pauli.jpg`
- Quelle: Wikimedia Commons
- URL: https://commons.wikimedia.org/wiki/File:Wolfgang_Pauli.jpg
- Motiv: Wolfgang Pauli, 1924
- Auflösung laut Commons: 935 × 1171
- Einsatz: S1 Pauli-Reveal, S8 Rückkehr
- Gate: Lizenz-/PD-Block der Description Page archivieren

### SRC02 — Wolfgang Pauli, 1945
- Titel: `Pauli.jpg`
- Quelle: Wikimedia Commons / Nobel Foundation
- URL: https://commons.wikimedia.org/wiki/File:Pauli.jpg
- Motiv: Wolfgang Pauli, 1945
- Status laut Commons: Public Domain
- Einsatz: optionaler Nobel-Anker; nicht nötig, wenn SRC01 visuell stärker ist

### SRC03 — Solvay-Konferenz 1927
- Titel: `Solvay conference 1927 Version2.jpg`
- Quelle: Wikimedia Commons / Institut International de Physique Solvay
- URL: https://commons.wikimedia.org/wiki/File:Solvay_conference_1927_Version2.jpg
- Auflösung laut Commons: 2126 × 1463
- Status laut Commons: Public Domain
- Motiv: Pauli mit Einstein, Bohr, Curie, Heisenberg, Schrödinger u. a.
- Einsatz: S1/S7; Gesamtgruppe → Crop auf Pauli

### SRC04 — Solvay-Konferenz 1927, hochauflösende Alternative
- Titel: `Solvay conference 1927.jpg`
- Quelle: Wikimedia Commons
- URL: https://commons.wikimedia.org/wiki/File:Solvay_conference_1927.jpg
- Auflösung laut Commons: 3000 × 2171
- Einsatz: bevorzugen, wenn Crop-Qualität besser ist
- Gate: konkrete PD-Begründung der gewählten Fassung archivieren

### SRC05 — Carl Gustav Jung
- Titel: `Carl Gustav Jung portrait.jpg`
- Quelle: Wikimedia Commons
- URL: https://commons.wikimedia.org/wiki/File:Carl_Gustav_Jung_portrait.jpg
- Status laut Commons: Public Domain
- Einsatz: S2, S4, S8
- Hinweis: niedriger aufgelöst; mit ruhigem Crop statt aggressivem Zoom verwenden

### SRC06 — ETH Zürich, historisch
- Titel: `ETH Zuerich 1880.jpg`
- Quelle: Wikimedia Commons / Baugeschichtliches Archiv Zürich
- URL: https://commons.wikimedia.org/wiki/File:ETH_Zuerich_1880.jpg
- Status laut Commons: Public Domain
- Einsatz: historischer Institutionsanker
- Claim-Gate: nicht als exakte Darstellung der ETH in Paulis Jahren beschriften

### SRC07 — Johannes Kepler
- Titel: `Portrait of Johannes Kepler.jpg`
- Quelle: Wikimedia Commons / Smithsonian Institute
- URL: https://commons.wikimedia.org/wiki/File:Portrait_of_Johannes_Kepler.jpg
- Auflösung laut Commons: 1258 × 1689
- Status: Public Domain
- Einsatz: S7 Kepler-Reveal

### SRC08 — Rosenkäfer / Cetonia aurata
- Titel: `Cetonia aurata.jpg`
- Quelle: Wikimedia Commons
- URL: https://commons.wikimedia.org/wiki/File:Cetonia_aurata.jpg
- Status laut Commons: Public Domain
- Einsatz: S4 als zoologischer Artenanker
- Claim-Gate: Einblendung `ROSE CHAFER — SPECIES REFERENCE` oder vergleichbar; niemals als historisches Originaltier aus Jungs Praxis ausgeben

### SRC09 — Rosenkäfer, CC0-Alternative
- Titel: `Cetonia-aurata-21-fws.jpg`
- Quelle: Wikimedia Commons
- URL: https://commons.wikimedia.org/wiki/File:Cetonia-aurata-21-fws.jpg
- Status laut Commons: CC0
- Einsatz: bevorzugen, falls Makro/Komposition besser zur Szene passt

---

## Hohe Priorität — Rechte/Verfügbarkeit noch prüfen

### R01 — Jung/Pauli-Briefscan
- Zielquelle: ETH-Bibliothek / Pauli-Archiv / CERN
- Gesucht: Briefseiten aus dem relevanten Austausch, ideal 1938 bzw. 1949–1950
- Verwendung: S3/S5
- Gate: Nutzungsbedingungen des Digitalisats; keine Annahme, dass ein alter Briefscan automatisch frei ist
- Fallback: typografische Brief-Rekonstruktion ohne erfundenes Zitat

### R02 — `Naturerklärung und Psyche` (1952)
- Gesucht: Titelblatt + Inhalts-/Trennseite, die Jung- und Pauli-Beiträge sichtbar macht
- Verwendung: stärkster Artifact-Reveal in S7
- Gate: Rechte der Ausgabe und des Scans separat klären
- Fallback: bibliografisch korrekte eigene Titelfläche, klar als grafische Rekonstruktion markiert

### R03 — Weltuhr-Abbildung aus Jungs Publikationskontext
- Gesucht: belegbare publizierte Darstellung / Diagramm
- Verwendung: optional in S1/S8
- Gate: Werk-/Ausgaben-/Scanrechte
- Fallback: eigene geometrische Rekonstruktion nach textlicher Beschreibung; keine Faksimile-Optik

### R04 — historische Zürich-/ETH-Aufnahmen aus Paulis Zeit
- Ziel: ca. 1928–1950, frei oder sauber lizenzierbar
- Verwendung: S2/S3 als bessere Alternative zu SRC06
- Gate: Motivzeit und Lizenz

---

## Nicht verwenden

- Blog-/Pinterest-/Stock-Reuploads von Pauli oder Jung ohne nachvollziehbare Lizenz
- moderne kolorierte Versionen historischer Fotos, wenn die Bearbeitungsrechte unklar sind
- KI-generierte „Originalbriefe“ oder „Buchseiten“
- Fake-Nobelurkunde
- beliebige Skarabäus-Abbildung als Jungs konkreter Käfer

## Download-Reihenfolge

1. SRC01/SRC03/SRC05/SRC07/SRC08 sichern.
2. Description Pages + Lizenzblöcke archivieren.
3. R02 `Naturerklärung und Psyche` priorisieren.
4. R01 Briefscans recherchieren.
5. Erst danach AI-Batch erzeugen, damit Rekonstruktionen nicht echte Belege ersetzen.
