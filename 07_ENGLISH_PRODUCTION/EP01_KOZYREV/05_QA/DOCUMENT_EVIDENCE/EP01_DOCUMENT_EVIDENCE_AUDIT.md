# EP01 Kozyrev — Dokument-Evidenz-Audit

Stand: 2026-08-27  
Scope: ausschließlich vorhandene/geplante Dokumentshots; kein Voice-, Bild-, Video- oder Masterjob.

## Ergebnis

- 27 Dokumentereignisse stehen in der aktuellen EDL.
- Der vorhandene Patent-Deconstruction-Clip enthält fünf getrennte Dokumentzustände. Dadurch umfasst das tatsächliche Inventar 31 Dokumentshots.
- 11 Shots wurden aus vorhandenen Originaldateien als neue, statische Evidenzcrops gebaut und visuell in 1920×1080 sowie 480×270 geprüft.
- 20 Shots sind hart blockiert. Für sie wurde kein Ersatzcrop erzeugt.
- Gesamtstatus: **BLOCKED_FOR_RENDER / DOCUMENT_QA_FAIL**.
- Es wurde kein Render gestartet und kein kostenpflichtiger Generierungsdienst aufgerufen.

## Freigegebene lokale Kandidaten

| Shot | Asset | Originalquelle / Seite | Verifizierte Fundstelle |
|---|---|---|---|
| KZ_DOC_002 | KZ_SRC_PATENT_TITLE_CROP | KZ-SRC-001, S. 2 | `DEVICE FOR CORRECTION OF MAN'S PSYCHOSOMATIC DISEASES` |
| KZ_DOC_005 | KZ_SRC_PATENT_FIG4_ROTATION | KZ-SRC-001, S. 2 | `platform coupled to` + `motor` + `rotation.` im vollständigen Abstract |
| KZ_DOC_009 | KZ_SRC_PATENT_FOCUS | KZ-SRC-001, S. 2 | `for focus at a distance of 50 cm from operating surface.` |
| KZ_DOC_013 | KZ_SRC_RESEARCHERS_LATER_WORK | KZ-SRC-007, S. 6 | `Distant-information interaction` im vollständigen Autor-/Titelblock |
| KZ_DOC_014 | KZ_SRC_2006_MODELED_SPACE | KZ-SRC-006, S. 9 | `modeled “Kozirev space”` im vollständigen Autor-/Titelblock |
| KZ_DOC_016 | KZ_SRC_EVIDENCE_PATENT | KZ-SRC-001, S. 2 | `RUSSIAN AGENCY FOR PATENTS AND TRADEMARKS` |
| KZ_DOC_019B | KZ_SRC_PATENT_NUMBER_CROP | KZ-SRC-001, S. 2 | `2 122 446`; `RU` und `C1` bleiben im selben Header sichtbar |
| KZ_DOC_019C | KZ_SRC_PATENT_DATES_CROP | KZ-SRC-001, S. 2 | Anmelde- und Veröffentlichungsdatum, jeweils vollständige Zeile |
| KZ_DOC_019D | KZ_SRC_PATENT_INVENTORS_CROP | KZ-SRC-001, S. 2 | `Kaznacheev V.P.` + `Trofimov A.V.` im vollständigen Inventor-Feld |
| KZ_DOC_021 | KZ_SRC_PATENT_DIMENSIONS | KZ-SRC-001, S. 2 | Material, 0.5 mm, 280 cm und 120 cm im vollständigen Abstract |
| KZ_DOC_025 | KZ_SRC_PATENT_DOCUMENTED_CHAMBER | KZ-SRC-001, S. 2 | `SUBSTANCE: device has` + `construction which` im vollständigen Abstract |

Alle 11 Kandidaten haben Seitenkontext, eine vergrößerte echte Fundstelle, dezente transparente Hervorhebung und vollständige relevante Zeilen/Blöcke. Dokumentbewegung ist auf `STATIC_NO_PAN_ZOOM` gesperrt. Unter den 11 Exporten gibt es keine identischen SHA-256-Dateien.

## Harte Fehler

| Shot(s) | Fehler | Konsequenz |
|---|---|---|
| KZ_DOC_001 | Compound-Voice: Datum, Erfinder und Aluminiumkonstruktion waren im alten Einzelcrop nicht gemeinsam lesbar belegt. | Kein Crop. Passage benötigt mehrere echte Belegmomente oder eine Voice-/Bild-Neuzuordnung. |
| KZ_DOC_003, KZ_DOC_019E | Patentfiguren besitzen keine exakt belegende Textphrase für „cylinder“ bzw. „technical drawings“. | Kein beliebiger Figurencrop. |
| KZ_DOC_004 | Figur 3 zeigt eine Spirale, kodiert aber keine Drehrichtung. | „Clockwise“ bleibt unbelegt. |
| KZ_DOC_006, KZ_DOC_010, KZ_DOC_012 | Russische Patent-Scanseiten ohne Textebene; exakte Phrase zu Mond-/geomagnetischen/heliogeophysikalischen Aussagen nicht verifiziert. | Build stoppt. |
| KZ_DOC_007 | Geplante 2019-Seite 161 behandelt ein Lunar-Testprojekt, nicht die komplette Voice-Aussage zu Körper, Umwelt und Informationsaustausch. | Falsche Seite. |
| KZ_DOC_008 | Englischer Abstract sagt `ground surface`, nicht `ground or polished`. | Voice ist stärker als sichtbare Quelle. |
| KZ_DOC_011 | Alter Crop zur „Antwort der Erfinder“ ist nicht auf eine exakte Passage rückführbar. | Build stoppt. |
| KZ_DOC_015 | `altered internal time` ist im geplanten 2006-Beleg nicht vorhanden. | Build stoppt. |
| KZ_DOC_017 | `unusual optical effects` ist nicht dasselbe wie die gesprochene Behauptung `extraordinary information effects`. | Semantischer Mismatch. |
| KZ_DOC_018, KZ_DOC_019A | „trap“/„verdict“ sind Erzählerinterpretationen, keine Originalphrase. | Kein pseudo-belegender Dokumentcrop. |
| KZ_DOC_020 | 2019-Seite 138 ist eine klinische Tabelle und belegt nicht, warum das Patent „invaluable“ sei. | Falsche Quelle/Seite. |
| KZ_DOC_022, KZ_DOC_024 | Würden KZ_DOC_009 bzw. KZ_DOC_005 exakt wiederholen. | Nach No-Repeat-Lock blockiert. |
| KZ_DOC_023 | Exakte Richtungsphrase nicht verifiziert. | Build stoppt. |
| KZ_DOC_026 | Eine einzelne sichtbare Passage stützt nicht gleichzeitig Wahrnehmung, Information und Zeit. | Compound-Voice nicht ausreichend belegt. |
| KZ_DOC_027 | Auf der geplanten Seite 142 keine exakte Phrase zu „intense experiences“ gefunden. | Build stoppt. |

## QA-Matrix

| Prüfung | Status |
|---|---|
| Originaldatei und Seitenzuordnung der 31 Shots inventarisiert | PASS |
| Exakte Phrase / semantisch gleich starke Fundstelle | PASS 11 / FAIL 20 |
| Vollständige Zeilen bzw. relevanter Block | PASS für alle 11 Exporte |
| Keine abgeschnittenen Satzanfänge/-enden | PASS für alle 11 Exporte |
| Mobile Lesbarkeit bei 480×270 | PASS für alle 11 Exporte, manuell visuell geprüft |
| Dezente Hervorhebung echter Originalphrase | PASS für alle 11 Exporte |
| Exakte Exportduplikate unter den akzeptierten Kandidaten | PASS, 0 Treffer |
| Statische spätere Darstellung ohne Pan/Zoom | LOCKED |
| Renderfreigabe | FAIL / BLOCKED |

Die aktuelle EDL und der bisherige Review-Master wurden nicht verändert. Die 11 Bilder sind geprüfte Ersatzkandidaten, aber noch nicht in eine Timeline integriert. Vor einem neuen Render müssen die 20 blockierten Zuordnungen entfernt, neu belegt oder semantisch neu geschnitten werden.
