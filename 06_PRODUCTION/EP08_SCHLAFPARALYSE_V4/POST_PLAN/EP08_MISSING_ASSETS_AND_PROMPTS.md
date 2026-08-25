# EP08 — Fehlende Assets und vorbereitete Promptliste

**Status:** Planung vollständig, noch keine bezahlte Generierung ausgelöst.  
**Priorität:** zuerst Originalquellen beschaffen und redaktionell aufbereiten; neue KI-Stills nur dort erzeugen, wo sie eine tatsächlich fehlende Bildidee liefern.

## A. Zwingend zu klärende Originalquellen

| ID | Benötigter Beleg | Verwendung | Ziel-Datei | Status / Regel |
|---|---|---|---|---|
| SRC-A01 | Archiv-/Programmnachweis zu Art Bells Shadow-People-Sendung vom 12. April 2001 und der Angabe von mehr als 4.500 Reaktionen | S1, Beleg der Hook-Zahl | `SRC051_ART_BELL_ARCHIVE_2001.png` | Primärarchiv bevorzugen; Datum und Wortlaut vollständig sichern |
| SRC-A02 | Früher datierter Beleg zur öffentlichen Popularisierung von „Shadow People“ durch Heidi Hollis | S2 | `SRC052_HEIDI_HOLLIS_EARLY_REFERENCE.png` | Nicht als Erfinderin beschriften; nur „wichtige Popularisiererin“ |
| SRC-A03 | Primärpublikation bzw. offizielle Bibliografie zu John E. Mack | S4 | `SRC053_MACK_BIBLIOGRAPHY.png` | Harvard-/Verlagsquelle; keine zufällige Sekundärseite |
| SRC-A04 | Primärpaper oder offizielle Abstract-Seite von Susan Clancy / Richard McNally zur Abduction-Erinnerung, Schlafparalyse oder False Memory | S4 | `SRC054_MCNALLY_CLANCY_PAPER.png` | Autor, Titel, Jahr und Journal müssen lesbar sein |
| SRC-A05 | Medizinische Primär-/Behördenquelle zu anticholinergem Delirium und Halluzinationen bei hoher Diphenhydramin-Dosis | S5 | `SRC055_DPH_MEDICAL_SOURCE.png` | Belegt nur Delirium/Halluzinationen, niemals ein „Hat-Man-Syndrom“ |
| SRC-A06 | Datierter, anonymisierbarer Forenbeleg für Hat-Man-/Diphenhydramin-Berichte | S5 | `SRC056_ANON_HAT_FORUM.png` | Namen, Avatare und Kontaktdaten redigieren; Datum und Kontext erhalten |
| SRC-A07 | Lizenzierbares Key Art oder freigegebene Presseabbildung zu *The Nightmare* sowie eine bibliografische Filmquelle | S7 | `SRC057_NIGHTMARE_LICENSED.png`, `SRC058_NIGHTMARE_BIBLIOGRAPHY.png` | Ohne Rechte nur Bibliografiekarte zeigen; keine Filmszene nachbauen |
| SRC-A08 | Zwei datierte frühe Web-/Forum-Archivansichten zum Thema | S6/S7 | `SRC059_WEB_ARCHIVE_RESULTS.png`, `SRC060_PERIOD_FORUM_CAPTURE.png` | Persönliche Daten redigieren; keine erfundene Benutzeroberfläche als Quelle ausgeben |

Diese Quellen sind im Sync-Plan als `SOURCE_ACQUISITION` markiert. Sie sind nicht durch generische KI-Bilder ersetzbar, weil sie eine Behauptung belegen sollen.

## B. Redaktionelle Erweiterung der vorhandenen Originalassets

Aus den 26 bereits vorhandenen Originaldateien wurden `SRC001` bis `SRC050` bereits als 2K-PNGs unter `../ORIGINAL_EXPANSIONS/` gebaut und auf fünf Kontaktbögen geprüft. Das sind keine fünfzig neuen Behauptungen, sondern vorher gerenderte, semantisch verschiedene 16:9-Ansichten:

- Gesamtansicht und belegrelevanter Detailausschnitt werden als getrennte PNGs exportiert.
- Hochformatige Dokumente werden vollständig eingepasst; Hintergrund ist eine abgedunkelte, unscharfe Kopie desselben Blatts.
- Quellen bleiben im fertigen Shot statisch. Der Wechsel von Gesamtseite zu Detail erfolgt als Hartschnitt, nicht als Kamerafahrt.
- Je Basisquelle höchstens zwei Ansichten. Keine dritte Verwertung desselben Bildes.
- Jahreszahl, Autor und Lizenzkontext werden redaktionell ergänzt, ohne den Inhalt des Dokuments zu kommentieren.
- YELLOW-Assets benötigen vor dem Export die dokumentierte Lizenz-/Persönlichkeitsprüfung.

Zusätzlich wurden `CUT001` bis `CUT023` aus vorhandenen generierten Stills als feste 2K-Dateien unter `../SEMANTIC_CUTS/` gerendert und auf zwei Kontaktbögen geprüft. Sie werden nur an auseinanderliegenden Textankern mit neuer Aussage eingesetzt; der Cutter bewegt sie nicht weiter.

`EDIT001` bis `EDIT023` sind kurze redaktionelle Composites. Erlaubt sind Hartschnitt, Ebenen-Reveal, Fokuswechsel und Opacity. Die virtuelle Kamera bleibt fest. Keine Parallaxe, keine diagonale Fahrt und kein künstlicher Dolly.

## C. Neue 2K-Stills — Ergänzungsbatch

Diese vier Motive sind keine Voraussetzung für die Voice-Erzeugung, erhöhen aber die Reserve und reduzieren den Druck, vorhandene Bedroom-/Hat-Man-Motive ein zweites Mal einzusetzen. Dateinamen beginnen bewusst nur mit `IMG`.

### IMG033_CULTURAL_TEMPLATE_PRELOAD.png

**Einsatz:** S2/S6, wenn eine kulturelle Vorlage bereits vor dem späteren Erlebnis verfügbar ist.  
**Referenzen:** `STYLE_CONCEPTUAL_EP08.png`, `IMG007_NAME_STABILIZES_SHAPE.png`, `IMG027_GLOBAL_VISUAL_MEMORY.png`.

Create a luminous 16:9 conceptual documentary still about a cultural image becoming available before a later perception. In a spacious museum-like signal chamber, unrelated archival fragments, soft charcoal marks and network traces pass through translucent memory planes; one simple hat-brim contour remains only as a faint latent possibility at the far edge, never a literal person. No bedroom, bed, ghost, horror creature, readable interface or text. Deep indigo balanced by warm amber pools and pearl highlights, lifted midtones, visible shadow detail, tactile glass and paper, sophisticated scientific-poetic realism. No captions, logos, signatures or watermark.

### IMG034_EVIDENCE_BOUNDARY.png

**Einsatz:** S5, klare Trennung zwischen medizinischem Befund und Internetfigur.  
**Referenzen:** `STYLE_MEDIA_EP08.png`, `IMG021_MULTIPLE_CAUSES_SAME_SILHOUETTE.png`.

Create a precise 16:9 editorial documentary image about an evidence boundary. On the left, a clean clinical archive table with neutral molecular and delirium-related visual materials; on the right, an anonymous field of fragmented forum sketches. A bright physical gap separates the two evidence domains, while a hat-shaped negative space appears only in the unverified sketch field and never in the clinical material. No readable text, medicine branding, pill glamour, bedroom or literal apparition. Static frontal composition, luminous ivory, brass and deep blue, clear midtones, restrained grain. No labels, logos, signatures or watermark.

### IMG035_GLOBAL_MEMORY_ORBIT.png

**Einsatz:** S7, globales visuelles Gedächtnis ohne weitere Bildschirmwand.  
**Referenzen:** `STYLE_CONCEPTUAL_EP08.png`, `IMG027_GLOBAL_VISUAL_MEMORY.png`, `IMG031_HAT_MAN_DISSOLVES_INTO_PIXELS.png`.

Create a serene, complex 16:9 documentary visualization of a global visual memory. Thousands of small paper, radio-wave and recollection fragments orbit a translucent world-scale sphere; each fragment remains different, yet their empty spaces briefly suggest the same simple human-and-hat contour before dispersing. The contour is an optical absence, not a being. No screens, bedrooms, UFOs, readable words or binary code. Deep indigo, warm amber, pale cyan and pearl, bright readable midtones, layered depth and tactile materials. No captions, logos, signatures or watermark.

### IMG036_TRILOGY_THRESHOLD.png

**Einsatz:** S8, Schlussverdichtung jenseits der Bettszene.  
**Referenzen:** `STYLE_CINEMATIC_EP08.png`, `IMG029_THREE_EPISODE_MOTIF_TABLE.png`, `IMG030_BRAIN_EXPERIENCE_STORY_EXPECTATION_BASE.png`.

Create a premium luminous 16:9 closing documentary still synthesizing body, experience, story and expectation as four connected physical spaces. A sleeping-body signal chamber opens into an ambiguous perception gallery, then into an archive of cultural masks, then into a bright network horizon that loops back toward a new human silhouette. No literal monster, bedroom, bed, occult diagram or readable text. The circular relation must be visually clear without arrows or labels. Warm amber practical light, cool indigo depth, pearl highlights, subtle grain, mystical but intellectually grounded and not gloomy. No logos, signatures or watermark.

## D. Negative Prompt-Lock für alle vier Ergänzungen

`no crushed blacks, no generic horror ghost, no repeated person in bed, no neon cyberpunk room, no glowing skin, no fake document text, no title typography, no logos, no watermark, no extra limbs, no literal claim that a supernatural entity is objectively present`

## E. Generierungsreihenfolge nach Quellen-QA

1. Originalquellen SRC-A01 bis SRC-A08 beschaffen und Rechte-/Claims-Prüfung abschließen.
2. `SRC001` bis `SRC050` sind gebaut; vor dem Master nur noch YELLOW-Lizenzen und endgültige Quellenzeilen freigeben.
3. `CUT001` bis `CUT023` sind gebaut; `EDIT001` bis `EDIT023` als feste Layer-Composites beziehungsweise Edit-Sequenzen erstellen.
4. Kontaktbogen prüfen: kein identischer Frame, kein dritter Ausschnitt derselben Basisquelle.
5. Nur wenn danach noch visuelle Lücken bestehen, IMG033 bis IMG036 erzeugen.
