# Schlafparalyse EP06–EP08 — Visual Coverage V5

**Status:** CANONICAL VISUAL LOCK  
**Stand:** 23.08.2026  
**Scope:** EP06 / EP07 / EP08

## Grundsatz

Die drei Folgen behalten die hohe visuelle Dichte der veröffentlichten NOESIS-Produktionen: Sprechertext wird eng und konkret bebildert, ohne lange Holds oder sichtbare Wiederholungsschleifen. Standardisiert ist die Qualität und Schnittdichte — **nicht die kreative Menge eines Assettyps**.

- kein Still >9 s; Ziel meist 2,8–4,8 s
- erster Schnitt <=2,5 s
- kein identischer Frame zweimal
- keine zwei aufeinanderfolgenden Shots aus demselben Basisasset
- Ken Burns allein macht kein neues Motiv
- Originalbeleg bei konkreter Person/Akte/Studie/Technik zuerst
- Motion bei Ablauf/Vergleich/Klassifikation
- Recon/AI für subjektive Erfahrung und nicht dokumentierbare Situationen

## Serienziele

| Folge | Shot-Target | Original-Shots | Recon-Shots | Motion-Shots | kanonischer AI-Pool |
|---|---:|---:|---:|---:|---:|
| EP06 Mechanismus | **149** | 58 | 63 | 28 | 32 MAIN + 8 RESERVE |
| EP07 Kultur/Salem | **146** | 88 | 27 | 31 | 20 MAIN + 4 RESERVE |
| EP08 Hat Man/Internet | **150** | 58 | 57 | 35 | 32 MAIN + 8 RESERVE |

Der AI-Pool ist **nicht** identisch mit der Zahl der Recon-Shots. Ein hochauflösendes Recon darf höchstens zwei Shots liefern, und nur wenn Full/Detail tatsächlich unterschiedliche Sprecherinformationen tragen. Reiner Zoom auf denselben Bildinhalt zählt nicht.

---

# EP06 — 149 Shots

| Akt | Shots | Original | Recon | Motion |
|---|---:|---:|---:|---:|
| S1 ZIMMER | 20 | 2 | 16 | 2 |
| S2 OLD_HAG | 18 | 7 | 9 | 2 |
| S3 REM_ATONIE | 19 | 13 | 3 | 3 |
| S4 DREI_FAMILIEN | 19 | 6 | 9 | 4 |
| S5 LABOR | 19 | 14 | 2 | 3 |
| S6 KOERPER_BESUCHER | 18 | 6 | 9 | 3 |
| S7 PRAESENZ | 22 | 5 | 13 | 4 |
| S8 WAS_BLEIBT | 14 | 5 | 2 | 7 |

**Logik:** Science/Lab ist original-first; S1/S4/S6/S7 tragen die Recon-Dichte. Bett/Schatten nie länger als zwei Shots hintereinander. Spätestens nach 20–30 s subjektiver Rekonstruktion wieder echter Science-/Archiv-/Motion-Anker.

---

# EP07 — 146 Shots

| Akt | Shots | Original | Recon | Motion |
|---|---:|---:|---:|---:|
| S1 SALEM | 19 | 13 | 4 | 2 |
| S2 NACHTMAHR | 18 | 11 | 4 | 3 |
| S3 VIELE_NAMEN | 19 | 10 | 3 | 6 |
| S4 KULTUR_WIRD_WAHR | 19 | 11 | 4 | 4 |
| S5 HUFFORD | 18 | 11 | 2 | 5 |
| S6 ERFAHRUNG_KULTUR | 19 | 10 | 4 | 5 |
| S7 AEGYPTEN_DAENEMARK | 20 | 14 | 2 | 4 |
| S8 DAEMON_LERNT | 14 | 8 | 4 | 2 |

**Logik:** Akten, Kunst, Karten und historische Quellen liefern die Dichte. Dokumente dürfen Full → Datum/Name → relevante Passage → Detail liefern, wenn jeder Shot eine andere Aussage trägt. Füssli maximal vier klar unterschiedliche Nutzungen. Keine generischen KI-Hexen-/Dämonengalerien.

---

# EP08 — 150 Shots

| Akt | Shots | Original | Recon | Motion |
|---|---:|---:|---:|---:|
| S1 4500_NACHRICHTEN | 20 | 10 | 3 | 7 |
| S2 SHADOW_PEOPLE | 19 | 4 | 12 | 3 |
| S3 ALIENS | 18 | 7 | 7 | 4 |
| S4 HARVARD | 17 | 10 | 2 | 5 |
| S5 HAT_MAN | 22 | 3 | 15 | 4 |
| S6 MUSTER_MEME | 19 | 6 | 7 | 6 |
| S7 INTERNET_ANFALL | 20 | 10 | 6 | 4 |
| S8 RUECKKOPPLUNG | 15 | 8 | 5 | 2 |

**Logik:** echte Radio/Fax/CRT/Modem/Research-Anker wechseln mit Shadow-/Hat-Man-Recons und Feedback-Motion. Hat-Man-Hero erst S5. Gleiche Silhouette maximal vier Einsätze in deutlich anderem Setup. Visuellen Modus spätestens alle 20–25 s wechseln.

---

# Wiederholungslock serienweit

1. Kein identischer Frame zweimal.
2. Ein Basisasset normalerweise max. 2 Einsätze; Ausnahme Hero-Dokument/Kunst nur mit klar anderem Detail und anderer Aussage.
3. Keine zwei aufeinanderfolgenden Shots aus demselben Basisasset.
4. Kein Motiv im selben Akt wiederholen, wenn eine Alternative vorhanden ist.
5. Full → Passage → Detail auf einer Quelle ist erlaubt, wenn es drei unterschiedliche Informationsbeats sind.
6. Nicht mehr als drei gleichartige AI-Stimmungsbilder hintereinander.
7. Non-16:9 vollständig enthalten über weich/dunkel kopiertem Eigenhintergrund.
8. Quelle erscheint dort, wo sie den Plot verankert oder dreht — nicht minutenlang als Beweislager.

# Produktionsreihenfolge

1. V5-Source-Assets laden und YELLOW reviewen.
2. Pro Episode `VISUAL_COVERAGE_V5.md` lesen.
3. Originale in konkrete Sprecherbeats einplanen.
4. Motion-/Diagramm-Slots festlegen.
5. vorhandenen direkten NanoBanana-Pool selektiv erzeugen.
6. Render-Manifest pro Cue mit mehreren konkreten Medienpfaden füllen, bis Shot-Target erreicht ist.
7. `python3 tools/check_schlafparalyse_visual_coverage_v5.py EP06` (analog EP07/EP08) vor dem Render ausführen.
8. Nur wenn der Checker echte Coverage-Lücken meldet, zusätzliche AI-Prompts für genau diese Sprecherbeats ergänzen.
