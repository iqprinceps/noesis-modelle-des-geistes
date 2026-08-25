# EP07 - Sync-, Edit- und Sound-Guide

**Kanonische Textquelle:** `EP07_SPRECHERFASSUNG_GEORGE_FINAL.md`  
**Takes:** `VOICE_EP07/source/` und `VOICE_EP07/EP07_TAKE_MANIFEST.csv`  
**Bildfolge:** `EP07_VOICE_VISUAL_SYNC.csv`  
**Status:** Voice und neue Assets noch nicht erzeugt

## George-Lock

- Voice-ID `JBFqnCBsd6RMkjVDRZzb`, Modell `eleven_multilingual_v2`
- stability `0.58`, similarity `0.80`, style `0.08`, speed `1.06`, speaker boost aktiv, seed `2402`
- Zieltempo etwa 132-140 Wörter pro Minute; keine Zeitdehnung
- Jede der 26 Dateien endet an einem vollständigen Gedanken oder einer natürlichen Atemstelle.
- Zahlen und Datumsangaben sind ausgeschrieben. Im Voice-Input keine Lautschrift ergänzen.
- Erst George erzeugen, dann Forced Alignment. `plan_start` und `plan_end` sind lediglich belastbare Edit-Schätzungen; Textanker und Bildreihenfolge sind verbindlich.

## Aussprache und Haltung

| Ausdruck | Regiehinweis |
|---|---|
| Richard Coman | englisch natürlich, Nachname nicht künstlich eindeutschen |
| Bridget Bishop | englisch natürlich, beide Namen gleich gewichten |
| Henry Füssli | Füssli deutsch aussprechen; kein englisches „Fuseli“ erzwingen |
| Nachtmahr, Mahr, Mara | klar, aber nicht wie eine Begriffslektion |
| Incubus | ruhig im Satz, keine Horrorbetonung |
| Kanashibari | einmal sauber setzen, danach nicht überdeutlich syllabieren |
| Jinn | kurz und neutral, nicht mystifizieren |
| David Hufford | englisch natürlich |
| Baland Jalal, Devon Hinton | Namen vor der Serienproduktion einmal als kurzer Pronunciation-Test prüfen |
| Ägypten, Dänemark | beide Stichproben gleich nüchtern erzählen; keine kulturelle Wertung |

## Bildschnitt

- Erster Wechsel spätestens bei 2,5 Sekunden. Die erste Rekonstruktion darf deshalb nur kurz etablieren, bevor die Coman-Quelle erscheint.
- 146 Slots über eine geplante Gesamtlänge von 10:52; überwiegend 3,5-5,5 Sekunden.
- Hartschnitte innerhalb eines Akts. Nur an Aktgrenzen eine Blende von 0,35 Sekunden.
- Quellen, Dokumente, Vergleichstafeln und Karten bleiben statisch. Hochformatige Quellen werden vollständig eingepasst, nicht beschnitten.
- Eigene Karten bleiben vollständig statisch. Normale Karten laufen einmal 5,5 Sekunden; die Endcard exakt 20 Sekunden.
- Transformationsclips laufen nativ und erhalten keine zusätzliche Kamera. Jeder der vier Hauptclips erscheint genau einmal.
- Gewöhnliche Stills: 32 von 71 Slots mit sanftem Zoom von 1,5-2,5 Prozent; die übrigen 39 halten statisch beziehungsweise bei Quellenkomposites vollständig gelockt.
- Keine aggressiven Schwenks. Ein optionaler Pan darf höchstens etwa 1,5 Prozent der Bildbreite zurücklegen und wird in diesem Plan nicht benötigt.
- Historische Rekonstruktionen erhalten beim ersten Einsatz den Hinweis `Rekonstruktion`. Spätere Salem-Darstellungen tragen Jahr und `spätere Darstellung`.

## Originalmaterial

- Geplante Quellenzeit: rund 277 Sekunden beziehungsweise 42,5 Prozent.
- Ein neuer Dokument-, Kunst-, Orts- oder Forschungsanker erscheint mindestens alle 30-45 Sekunden.
- 47 bereits vorhandene Quellenableitungen sind in der Sync-Tabelle als `DERIVE_STATIC_FRAME` markiert.
- 17 weitere Quellenexports hängen an zehn noch zu beschaffenden Masterquellen.
- Full, Passage und Detail gelten nur als getrennte Shots, wenn sie eine neue Information zeigen. Die konkrete Variante steht in `asset_id`; das unveränderte Ausgangsobjekt in `source_master`.

## SFX-Schlüssel

Alle Effekte bleiben realistisch und leise. Kein Jump-Scare, Trailer-Boom, generischer Okkult-Drone oder Effekt, der ein Wesen objektiv real erscheinen lässt.

| Schlüssel | Inhalt | Einsatzregel |
|---|---|---|
| `ROOM_1692` | trockener kleiner Holzraum, sehr leises Leinen, ein einzelnes Bodengeräusch | keine Stimme, kein Flüstern, kein Monsteratem |
| `PRESSURE_DRY` | kurzer Atemzug, gedämpfte Stoffspannung, sehr tiefer körperlicher Druckimpuls | Impuls nur beim Druckanker, kein Sub-Boom |
| `COURT_TRANSITION` | Feder auf Papier, Holzbank, entfernter nüchterner Raumhall | Quellen-Reveal stützen, nicht dramatisieren |
| `GALLERY_AIR` | fast stiller Galerieraum, leises Rahmen-/Holzknacken | Füssli-Bild landen lassen |
| `CANVAS_DETAIL` | minimale Leinwand- und Papiertextur | keine Pferde- oder Kreaturengeräusche |
| `PAPER_GEOGRAPHY` | Papierfaltung, trockener Kartentisch, leiser Übergang | geografischer Wechsel ohne Whoosh |
| `CULTURAL_PAPER` | drei unterschiedliche Materialklänge: Pergament, Holzschnittpapier, Shoji-Papier | nicht gleichzeitig; jeder Kulturanker bekommt eigenes Material |
| `CULTURAL_ROOM` | neutraler Raumton mit sehr leiser Küstenluft am Newfoundland-Beat | keine ethnischen Musikklischees |
| `THRESHOLD_TONE` | ein heller, langsam verklingender Oberton über trockenem Raum | begleitet die Frage Körper vor Mythos |
| `CHURCH_DISTANCE` | eine weit entfernte einzelne Glocke, dann normaler Raum | nur einmal, nicht als Omen |
| `OBJECT_FOLEY` | Buchdeckel, Leinen, kleine Wasserschale, Eisenobjekt | exakt an sichtbare Objekte binden |
| `FIELD_TAPE` | Recorder-Klick, leises Bandlaufen, Bleistift | Hufford-Feldarbeit, kein künstliches Archivknistern über alle Shots |
| `PENCIL_PAPER` | Bleistift, Seitenwechsel, ruhiger Interviewraum | Quelle/Feldnotiz erden |
| `LOW_FEEDBACK` | sehr leise periodische Atem-/Raumwelle | bleibt unter Sprache, kein Dämonenton |
| `TWO_ROOMS` | zwei nüchterne, ähnlich laute Räume mit minimal anderer Akustik | Vergleich ohne kulturelle Wertung |
| `CTA_SILENCE` | Musik und SFX um etwa 3 dB zurücknehmen | Karte vollständig lesen lassen |
| `RESEARCH_DESK` | Papier, Tastaturanschlag, Seitenmarker | sachlicher Studien-Reveal |
| `CLINICAL_PULSE` | sehr leiser regelmäßiger Messpuls plus Laborraum | kein Herzmonitor-Klischee, nur bei Messbildern |
| `FEEDBACK_RISE` | vier kurze Materialimpulse, die enger zusammenrücken | synchron zu Modellstationen; vor Entitätsform wieder lösen |
| `COURT_RETURN` | Feder-/Bankmotiv aus S1, dünner und weiter entfernt | akustisches Leitmotiv, nicht dieselbe Audiodatei unverändert wiederholen |
| `MATERIAL_BREATH` | Papierfasern, Leinen und ein normaler Atemzug | Kernthese körperlich, nicht übernatürlich |
| `PRINT_TO_WIRE` | Druckpresse, Buchseite, Radioschalter, Modem-Relais in zeitlicher Folge | keine nostalgische Geräuschcollage; vier klare Übergänge |
| `RADIO_HANDOFF` | echter Radiotuning-Charakter, Telefonleitungs-Klicks, sehr kurzer Modemton | keine fremde Sendungsaufnahme ohne Recht, keine Sprecherimitation |
| `END_TONE` | warmer Grundton und eine helle harmonische Ausklingung | 20 Sekunden Platz für Endscreens |

## Musikbett

- Eigene Synthese: Grundton unter 520 Hz, harmonische Schicht 700-2600 Hz, zurückhaltendes Pink Noise.
- Bett ungefähr `-30 LUFS`, sauber gegen George geduckt. Kein dauerhaftes Horrorbrummen.
- Relative Intensität je Akt: S1 `0.85`, S2 `0.64`, S3 `0.72`, S4 `0.78`, S5 `0.70`, S6 `0.82`, S7 `1.00`, S8 `0.68`.
- Kurze Entlastung unter jeder Karte und unter Quellen mit dichter Handschrift.
- Finale Mischung `-14 LUFS ±0,5`, True Peak höchstens `-0,8 dBTP`, 48 kHz Stereo.

## Nach der Voice

1. Alle 26 George-Takes erzeugen und einzeln auf Aussprache, Atemabbrüche und künstliche Betonung prüfen.
2. Takes ohne Time-Stretch neu aufnehmen, falls ein Fenster nicht passt.
3. Forced Alignment gegen die unveränderten Take-Texte aus `VOICE_EP07/source/` ausführen.
4. Planzeiten in der CSV auf Wortanker ziehen; keine Bildfolge anhand einer alten Textfassung schneiden.
5. SRT erst aus dem finalen Masteraudio erzeugen, maximal 84 Zeichen pro Block.

