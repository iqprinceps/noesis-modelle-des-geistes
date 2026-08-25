# EP07 - Fehlende Assets und Ergänzungsprompts

**Status:** Plan vollständig, Generierung absichtlich nicht gestartet  
**Grundlage:** `EP07_VOICE_VISUAL_SYNC.csv`  
**Ziel:** 146 inhaltlich unterschiedliche Bildslots, 35-45 % Quellenzeit, maximal zwei Einsätze je konkreter Exportdatei

## Globale Bildregeln

- Ausgabe: horizontales 16:9-PNG, 2K, Dateiname exakt wie angegeben.
- Stilreferenz je nach Motiv: `STYLE_ARCHIVE_EP07.png`, `STYLE_CINEMATIC_EP07.png` oder `STYLE_CONCEPTUAL_EP07.png`.
- Mystisch und tief, aber lesbare Mitteltöne; keine großflächig zugelaufenen Schatten.
- Kein generierter lesbarer Text, keine Fantasieschrift, Logos oder Wasserzeichen.
- Kein generisches Horrormonster, keine leuchtenden Augen, keine Fantasy-Magie und keine Polarlichtfarbe in Innenräumen.
- Historische Dokumente, Kunstwerke und Forschungsseiten werden niemals per KI nachgebaut. Sie kommen später als statische Originalquelle in den Schnitt.
- Alle historischen Spielszenen erhalten im Edit den Hinweis `Rekonstruktion`.
- Bett oder Schlafzimmer nur dort, wo der Text den körperlichen Ausgangszustand wirklich braucht. Die Ergänzungsbatch arbeitet überwiegend außerhalb des Bettes.
- Ruhige Komposition mit echtem Vorder-, Mittel- und Hintergrund; keine auf eine spätere aggressive Kamerafahrt angewiesene Bildgestaltung.

## Priorität A - Quellen beschaffen und prüfen

Diese zehn Masterquellen fehlen. Eine einzige Masterquelle darf mehrere **semantisch verschiedene**, statische Editor-Exporte liefern, etwa Titel, Methode und Ergebnis. Jeder Export erhält einen eigenen Dateinamen unter `04_EDITOR_DERIVATIVES/`. Quelle und Jahr bleiben sichtbar; keine Kamerabewegung.

| Master-Datei | Benötigter Inhalt | Einsatz | Gate |
|---|---|---|---|
| `ORIG_NEWFOUNDLAND_MAP_PD.png` | frei nutzbare historische oder amtliche Karte Neufundlands | Old-Hag-Ort und Hufford-Feldarbeit | Public Domain/CC prüfen |
| `ORIG_CHINESE_GHOST_PRESSURE_SOURCE_PD.png` | belastbare historische Quelle zum chinesischen Druckmotiv; keine beliebige Geistergrafik | S3 China | Aussage und Bildkontext prüfen |
| `ORIG_HUFFORD_TERROR_BOOK_COVER_LICENSED.png` | rechtlich geklärtes Cover von *The Terror That Comes in the Night* | S5 Forschungsanker | Coverrecht klären |
| `ORIG_HUFFORD_PORTRAIT_LICENSED.png` | rechtlich geklärtes David-Hufford-Porträt | S5 Autor | Lizenz/Attribution klären |
| `ORIG_JALAL_HINTON_EGYPT_DENMARK_PAPER.png` | Originalpaper oder autorisierte Repositoriumsseite mit Titel, Autoren, Methode, Ergebnis | S7 Studie | Nutzungsrecht/Screenshotrecht klären |
| `ORIG_EGYPT_MAP_PD.png` | nüchterne frei nutzbare Karte | S7 Verortung | keine dekorative Pseudokarte |
| `ORIG_DENMARK_MAP_PD.png` | nüchterne frei nutzbare Karte | S7 Verortung | gleiche Kartensprache wie Ägypten |
| `ORIG_EGYPT_SLEEP_PARALYSIS_SOURCE.png` | echter Forschungs-/Kontextanker für die ägyptische Stichprobe | S7 | keine touristische Symbolik |
| `ORIG_DENMARK_SLEEP_PARALYSIS_SOURCE.png` | echter Forschungs-/Kontextanker für die dänische Stichprobe | S7 | kein generisches Klinikstockfoto |
| `ORIG_ART_BELL_2001_BROADCAST_SOURCE.png` | rechtlich nutzbarer Sendungs-/Archivanker vom 12. April 2001 | S8 EP08-Handoff | Datum und Herkunft belegen |

Vier weitere Salem-Dokumente stehen im vorhandenen `ASSET_AUDIT.json` als optionale Downloads. Sie blockieren den Schnitt nicht, wären aber gute zusätzliche Originalanker, falls ihre Digitalisate sauber geladen werden können.

## Priorität B - Quellenableitungen aus vorhandenem Material

`EP07_VOICE_VISUAL_SYNC.csv` spezifiziert 47 statische Exporte aus bereits vorhandenen Quellen. Besonders wichtig:

- Coman-Aussage: ganze Vorderseite, Name/Eröffnung, Passage zu Druck und Bewegungsunfähigkeit, Eid/Signatur. Keine zwei Ausschnitte erzählen dieselbe Information.
- Bridget-Bishop-Untersuchung: ganze Vorderseite, Überschrift/Datum, Signaturbereich.
- Füssli: Gesamtwerk, Frau, aufliegende Figur und Pferdekopf als vier getrennte Beobachtungen. Jeder Export statisch.
- Abildgaard: Gesamtwerk und zwei inhaltliche Details, nicht dieselben Crops wie Füssli.
- Malleus/Salem-Darstellungen: immer Jahreszahl und bei späteren Bildern ausdrücklich `spätere Darstellung`.
- REM-/NHLBI-Material: Messspur, Mikro-Arousal-Detail und reale Schlaflaborumgebung als wissenschaftliche Erdung.

Die Ableitungen werden im geplanten Ordner `04_EDITOR_DERIVATIVES/` vollständig eingepasst. Hochformatige Blätter bekommen den NOESIS-Quellenhintergrund; Zoom, Pan und Drift bleiben aus.

## Priorität C - neue Bildmotive

Jeder Eintrag schließt eine konkrete Textlücke. Es sind keine austauschbaren Moodshots.

| Datei | Referenz | Promptkern / konkrete Bildfunktion |
|---|---|---|
| `IMG024_NIGHTMARE_PRINT_WORKSHOP.png` | CINEMATIC | Historische Druckwerkstatt um 1800, Hände legen eine frisch gedruckte Nachtmahr-Reproduktion neben andere Blätter; Verbreitung eines Bildmotivs, keine schlafende Person, kein lesbarer Text. |
| `IMG025_MANY_ORIGINS_ARCHIVE_TABLE.png` | ARCHIVE | Großer Archivtisch mit voneinander getrennten Papiergruppen aus verschiedenen Zeiten und Regionen, kein Stammbaum, keine Verbindungspfeile; viele Ursprünge statt einer Genealogie. |
| `IMG026_SHARED_MECHANIC_RELIEF.png` | CONCEPTUAL | Helles Leinenrelief aus offenem Auge, blockierter Hand, Druckfalte und stummer Mundkontur; gemeinsames körperliches Rohmaterial, kein Bett und kein Wesen. |
| `IMG027_KANASHIBARI_THRESHOLD.png` | CONCEPTUAL | Aufrechte anonyme Figur in einem klaren Shoji-Raster, Bewegung durch starre geometrische Rahmen blockiert; respektvolle Zustandsvisualisierung ohne Samurai-, Geisha- oder Geisterklischee. |
| `IMG028_NEWFOUNDLAND_ORAL_HISTORY.png` | CINEMATIC | Tageslicht in einer schlichten neufundländischen Küche, zwei Menschen im Gespräch, Kassette und Notizbuch auf dem Tisch, Küstennebel am Fenster; Feldüberlieferung statt Spukzimmer. |
| `IMG029_HOUSEHOLD_EXPLANATION_CHOICES.png` | CINEMATIC | Frühneuzeitlicher Haushalt bei Tagesanbruch, Gebetbuch, schlichtes Kreuz, Leinen und Eisenobjekt auf getrennten Flächen; mehrere verfügbare Erklärungen, kein okkulter Altar. |
| `IMG030_RITUAL_AS_PRACTICAL_RESPONSE.png` | CINEMATIC | Hände ordnen einfache Schutzobjekte an einer Türschwelle; menschliche Handlung gegen geglaubte Ursache, warmes realistisches Innenlicht, kein Dämon und kein Bett. |
| `IMG031_HUFFORD_FIELD_INTERVIEW.png` | CINEMATIC | Sachliches Oral-History-Interview in Neufundland am Tag, Forscher seitlich, ältere befragte Person nicht frontal exponiert, Recorder und Notizen, keine erfundene lesbare Schrift. |
| `IMG032_UNNAMED_FIRST_EPISODE.png` | CONCEPTUAL | Anonyme wache Augen-, Hand- und Brustkonturen in neutralem Material, dahinter versiegelte unbeschriftete Bücher; Erfahrung vor Kenntnis der Überlieferung. |
| `IMG033_AWAKE_BRAIN_BODY_LOCK.png` | CONCEPTUAL | Zweischichtiges wissenschaftlich-poetisches Modell: waches Augen-/Kortexmotiv oben, blockierte Motorik als ruhige Körperkontur unten; kein Energiefluss, keine Seele als Fakt. |
| `IMG034_TWO_EXPECTATIONS_THRESHOLD.png` | CONCEPTUAL | Zwei aufrechte Menschen vor derselben dunklen Schwelle, gleiche Körperhaltung; eine Umgebung enthält Schlafwissen, die andere Familien- und Religionsobjekte, ohne eine Seite abzuwerten. |
| `IMG035_EGYPT_INTERVIEW_CONTEXT.png` | CINEMATIC | Zeitgenössische ägyptische Interviewumgebung bei hellem natürlichem Licht, alltäglich und nicht touristisch, aufrechter Teilnehmer im Gespräch, keine Jinn-Figur. |
| `IMG036_DENMARK_INTERVIEW_CONTEXT.png` | CINEMATIC | Zeitgenössische dänische Interviewumgebung mit vergleichbarer Brennweite, Haltung und Helligkeit wie IMG035; keine visuelle Wertung durch Luxus oder Kälte. |
| `IMG037_FEAR_SLEEP_DAY_NIGHT_LOOP.png` | CONCEPTUAL | Vier klar getrennte Zustände aus Abendanspannung, fragmentiertem Schlaf, morgendlicher Erschöpfung und wachsender Erwartung; Materialkreis ohne Pfeile, Wesen oder Dashboard. |
| `IMG038_BODY_CULTURE_BRAID.png` | CONCEPTUAL | Körperkontur und kulturelle Papier-/Stofflagen flechten sich gegenseitig, ohne zu verschmelzen; Erfahrung und Erzählung als dynamische Beziehung, heller Schwerpunkt. |
| `IMG039_GENERATIONS_OF_NIGHT_STORIES.png` | CINEMATIC | Vier Generationen in getrennten warmen Alltagsszenen geben eine Geschichte über Gespräch, Buch, Bild und Radio weiter; keine Geistererscheinung, keine Textblasen. |
| `IMG040_PRINT_TO_RADIO_NETWORK.png` | CONCEPTUAL | Materielle Folge aus Druckplatte, Buchseite, Radiowelle und frühem Modemkabel; zunehmende Übertragungsgeschwindigkeit ohne HUD, Text oder leuchtende Energie. |
| `IMG041_2001_RADIO_STUDIO_HANDOFF.png` | CINEMATIC | Amerikanisches Nacht-Radiostudio um 2001, Mikrofon, Kopfhörer, Mischpult und Telefonleitungen, Moderator nur als neutrale Rücken-/Seitenfigur; kein imitierbares Porträt und kein lesbares Branding. |
| `IMG042_EARLY_WEB_SHADOW_NETWORK.png` | CONCEPTUAL | Frühe CRT-Bildschirme und Modemleitungen, kleine voneinander verschiedene Schattenzeichnungen erscheinen auf getrennten Monitorflächen; noch keine einheitliche Figur und kein lesbarer Webtext. |
| `IMG043_FIRST_EPISODE_BODY_TRACE.png` | CONCEPTUAL | Erste Episode als tastbare Spur aus Auge, Druckfalte und blockierter Hand; Bücher und Symbole bleiben hinter einer klaren Grenze und noch geschlossen. |
| `IMG044_SAME_BODY_TWO_INTERPRETATIONS.png` | CONCEPTUAL | Derselbe neutrale Körperumriss zweimal als echtes Vergleichspaar, links medizinische Messmaterialien, rechts Alltags- und Überlieferungsobjekte; gleiche Helligkeit und Würde. |
| `IMG045_EXPECTATION_ENTERS_BODY.png` | CONCEPTUAL | Ein neutraler Erwartungsschatten legt sich über Atem-, Hals- und Handrelief, ohne Wesen zu werden; mögliche Wirkung von Erwartung auf Körperempfinden. |
| `IMG046_RAW_MATERIAL_TO_FORM.png` | CONCEPTUAL | Auge, Druckkontur und Handabdruck ordnen sich schrittweise zu einer kulturell lesbaren Schwellenform; kein Pfeil, keine universelle Entität, kein Text. |
| `IMG047_CULTURE_FEEDBACK_BRAID.png` | CONCEPTUAL | Zwei Materialstränge - Körperzustand und kulturelle Form - kreuzen sich und kehren verändert zurück; Kreis bleibt offen, damit keine harte Kausalität behauptet wird. |
| `IMG048_STORY_BODY_RETURN.png` | CONCEPTUAL | Gesprächssilhouetten werden zu Papierwellen, die in Rippen- und Halsrelief zurückkehren; helles Zentrum, keine aufliegende Gestalt. |
| `IMG049_DECISION_LAYERS_HOLD.png` | CONCEPTUAL | Ruhige statische Zwischenkomposition mit zwei Deutungsschichten um einen identischen Körperabdruck; für einen Hold ohne Kamerafahrt geeignet. |
| `IMG050_PRIVATE_TO_PUBLIC_NETWORK.png` | ARCHIVE | Leere Zeugenbank, eine einzelne Federkielspur verzweigt sich in viele gesichtslose Publikumsschatten; Originaldokumente werden später separat eingesetzt und nicht generiert. |
| `IMG051_NAME_WAITING_IN_SHADOW.png` | CONCEPTUAL | Eine unbestimmte Schwellenform vor mehreren unbeschrifteten Namenskarten; der Zustand ist schon da, die kulturelle Benennung wartet im Hintergrund. |
| `IMG052_QUESTION_BETWEEN_MODELS.png` | CONCEPTUAL | Identischer Körperabdruck zwischen zwei offenen, aber unbeschrifteten Modellen; bewusste Leerstelle für die Zuschauerfrage, kein Gleichgewichtswaagen-Klischee. |
| `IMG053_PRESSURE_PRESENCE_RELIEF.png` | CONCEPTUAL | Nahes Leinenrelief von Brustdruck und verändertem Negativraum, Präsenz ohne Körper oder Gesicht; Variation mit anderer Geometrie als IMG026. |
| `IMG054_BODY_RAW_MATERIAL.png` | CONCEPTUAL | Museumsartige Anordnung von Auge, Atemspur, Hand und Druckfalte als vier reale Materialobjekte; Kernthese „Rohmaterial“ ohne Diagrammoptik. |
| `IMG055_CULTURAL_FORM_SETTLES.png` | CONCEPTUAL | Mehrere Papier- und Stofflagen legen sich um denselben Körperabdruck, bleiben aber sichtbar getrennt; statischer Endzustand statt wiederholtem Veo-Clip. |
| `IMG056_PRESSURE_AS_MEMORY_RELIEF.png` | CONCEPTUAL | Druckereignis als bereits vergangene, im Material verbliebene Vertiefung; Feldnotizen im Hintergrund unlesbar, keine Kreatur. |
| `IMG057_PUBLIC_MEMORY_SHADOWS.png` | ARCHIVE | Salem-Quellenraum nach der Anklage: leere Bank, viele voneinander getrennte menschliche Schatten und Aktenhalter; keine Schuldmarke und keine bewegte Quelle. |
| `IMG058_RADIO_NETWORK_TRANSFORMATION_END_FRAME.png` | CONCEPTUAL | Statischer Endframe einer beschleunigten Übertragung: Radiowellen zerfallen in viele unterschiedliche frühe Netzwerkknoten; keine einzelne universelle Schattenfigur. |
| `IMG059_FUSELI_TO_SCREEN_STATIC.png` | ARCHIVE | Leerer Museums-/Medientisch mit reservierten Flächen für echtes Füssli-Werk und frühen CRT-Bildschirm; beide Quellen später statisch einsetzen, kein generierter Bildtext. |
| `IMG060_WORD_LAYERS_CTA_BG.png` | CONCEPTUAL | Helle, ruhige Papierlagen mit verschiedenen Schwellengeometrien und großer leerer Mitte; statischer CTA-Hintergrund, keine lesbaren KI-Wörter. |

## Kartenstatus

Alle sieben vorgesehenen Karten sind vorhanden und werden eingesetzt:

- `CARD001_VIELE_NAMEN.png`
- `CARD002_PRIVATNACHT_GERICHT.png`
- `CARD003_HUFFORD_INVERSION.png`
- `CARD004_AEGYPTEN_DAENEMARK.png`
- `CARD005_FEEDBACK_LOOP.png`
- `CARD006_CTA_ERFAHRUNG_KULTUR.png`
- `CARD007_ENDCARD.png`

Geplante Kartenzeit: 53 Sekunden beziehungsweise rund 8,1 % der Folge. Jede Karte erscheint einmal. Alle Karten bleiben vollständig statisch.

## Ausführungsreihenfolge

1. Zuerst die zehn fehlenden Originalquellen rechtlich klären und herunterladen.
2. Dann 47 statische Quellenableitungen erzeugen; kein KI-Modell nötig.
3. Danach nur die in der Sync-Tabelle tatsächlich noch mit `MISSING_GENERATION` markierten 37 Bilder generieren.
4. Kontaktbogen, Helligkeit, Textartefakte, historische Verwechslungen und Bettquote prüfen.
5. Erst nach echter George-Aufnahme die Planzeiten per Forced Alignment ersetzen. Die Textanker und Bildreihenfolge bleiben bestehen.

