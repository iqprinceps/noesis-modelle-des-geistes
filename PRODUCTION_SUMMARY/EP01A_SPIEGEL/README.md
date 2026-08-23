# EP01A Die Spiegel

**Stand:** 20.08.2026
**Status:** Hochgeladen als `a4WGQDDVwls`, terminiert auf 20.08.2026 17:00.
**Laufzeit:** 9:43 (9:23 Sprechtext + 20 s Endcard)

---

## Was diese Folge ist

Die Kozyrev-Spiegel von Nowosibirsk: eine Konstruktion aus gebogenen
Aluminiumplatten, ein Patent der Russischen Föderation, Tausende Protokolle
über dreißig Jahre und ein Fernwahrnehmungsversuch am Nordpolarmeer.

Sie läuft vor EP01 (Kozyrev selbst) und endet mit dem Vorgriff darauf.

Der Sprechtext war bei Produktionsbeginn fertig und freigegeben. Er wurde
nicht angefasst — weder umgeschrieben noch gekürzt.

## Pipeline

Alles ist aus einer Textquelle abgeleitet: `07_VOICE_SCRIPT_CLEAN.txt`.
Änderungen gehören immer dorthin, nie in die Sprechtexte.

```bash
python tools/spg_texts.py                 # acht Sprechtexte + Batchdatei
python "…/NOESIS Channel/tools/elevenlabs_cli.py" batch \
    --batch-file 06_PRODUCTION/EP01A_SPIEGEL/voice/voice_batch.json --execute
python tools/spg_voice.py all             # VO-Master + Forced Alignment
python tools/spg_image_gen.py all         # Motive nach VISUAL_SPEC
python tools/spg_motion.py                # vier Animationen
python tools/spg_graphics.py              # Karten + Endcard
python tools/spg_graphics.py thumbnail spg_tuer_geht_auf
python tools/spg_produce.py prepare
python tools/spg_produce.py all           # Timeline, Ton, Render, SRT, QA
```

Alle sechs Werkzeuge sind **abgeleitete Kopien** der EP02-V7-Vorlagen; die
Vorlagen selbst sind unverändert geblieben.

## Die acht Akte

Die Aktgrenzen liegen auf den Absätzen der Reinschrift und werden aus dem
Stem-Report berechnet, nicht fest eingetragen — verschiebt sich der
Sprechrhythmus, ziehen Intensitätskurve, Blenden und Kapitel mit.

| Akt | Aufgabe | Start | Dauer |
|---|---|---|---|
| 1 | Hook: die Sitzung in der Spirale, dann die Quelle | 0:00 | 59,6 s |
| 2 | Nowosibirsk, Kaznacheev, Trofimov | 1:00 | 103,8 s |
| 3 | Die Maschine: Maße, Bauform, Patent | 2:45 | 49,2 s |
| 4 | Der Kozyrev-Raum — der Sprung | 3:34 | 36,0 s |
| 5 | Die Protokolle, ausgebreitet, Mid-Roll-CTA am Ende | 4:11 | 105,7 s |
| 6 | Aurora Borealis — der Moment | 5:57 | 56,5 s |
| 7 | Dikson, Blatt und Stift — voll ausgespielt | 6:55 | 62,4 s |
| 8 | Was bleibt, Schlussbild, Vorgriff auf EP01 | 7:58 | 82,7 s |

## Bild

| Kennzahl | Ziel (§ 3) | Diese Folge |
|---|---|---|
| Shots | 140–155 | **155** |
| Einzelbilder | ≥ 85 | **117** |
| Maximale Wiederholung | ≤ 4× | **4×** |
| Wiederholung im selben Akt | 0 | **0** |
| Kamerafahrt, Einzelbilder | jedes Segment sichtbar | **34,8 im Mittel** |
| Zappeln (§ 3) | Median ≤ 0,10, keins über 0,20 | **Median 0,063, keins über 0,20** |
| Bewegtbild | 3–5 Clips | **5** (4 eigene + 1 NASA) |
| Beschriftungen | 25–35 | **35** |

Die Spiegel sind überall nach Patent dargestellt: gebogene Platten, offener
Zylinder oder Spirale mit Einstiegsspalt, ein Mensch auf einem einfachen
Stuhl im Zentrum. Keine Röhre, kein Kegel, keine Haube, keine Elektroden,
keine Kabel am Kopf. Jedes Motiv wurde einzeln gesichtet; fünf Bilder wurden
verworfen und mit geschärftem Prompt neu erzeugt (zwei wegen Röhrenform, eins
weil es ein Windrad statt der Anlage zeigte, eins wegen eingebrannter
Farbcodes im Bild, eins weil das Gesicht der Rekonstruktion zu frontal stand).

## Animationen

Vier eigene, prozedural mit numpy und PIL, in der Kozyrev-Palette
(`motion/`):

| Datei | Rolle |
|---|---|
| `polarlicht.mp4` | Aurora-Bänder, die wandern und atmen. Trägt Akt 1 und 5. |
| `magnetfeld.mp4` | Erdfeldlinien, die im Zentrum ausdünnen und aufreißen. Akt 4. |
| `spirale.mp4` | Die Anlage von oben, rotierend, mit Brennpunkt. Akt 3. |
| `zeitfluss.mp4` | Ein Partikelstrom, der die Richtung verliert. Akt 2, 5, 6. |

Dazu ein echter NASA-Clip (TRACERS, gemeinfrei) unter den beiden Stellen
über die geomagnetische Lage — genau die Verwendung, die die Quelle erlaubt.

## Ton

Stimme George (`JBFqnCBsd6RMkjVDRZzb`), `eleven_multilingual_v2`,
stability 0.58 · similarity_boost 0.80 · style 0.08 · speed 1.06 · seed 2402.
8.867 Zeichen in acht Stems.

Bett aus Eigensynthese, drei Schichten, Anteil über 620 Hz. Die
Intensitätskurve folgt § 6 über alle acht Akte, Spitze in Akt 6 und 7.

Master: **−14,01 LUFS**, True Peak **−1,00 dBTP**.

## Auslieferung

```text
render/final/EP01A_SPIEGEL_FINAL_1080p.mp4   1920×1080, 30 fps, H.264, AAC 320k
render/final/EP01A_SPIEGEL_QA.json           alle Prüfungen
render/final/EP01A_SPIEGEL_CONTACT_SHEET.jpg Kontaktbogen
captions/EP01A_SPIEGEL_de.srt                Untertitel
thumbnail/                                   Thumbnail + Lesbarkeitsprobe 246 px
SOURCES.md                                   Lizenzen und Attributionen
METADATA.md                                  Titel, Kapitel, Beschreibung, Kommentar
```

## Abweichungen vom Standard

1. **Laufzeit 9:43 statt 10:00–10:40.** Der freigegebene Text hat 1.314
   Wörter, George spricht ihn bei `speed 1.06` in 9:23. Ohne Eingriff in den
   Text nicht zu ändern — und der Text wird nicht angefasst.
2. **Ø Shotdauer 3,63 s statt 4,0–4,5 s.** Direkte Folge von Punkt 1: bei
   155 Shots auf 563 s Sprechzeit. Die Shotzahl liegt im geforderten Fenster
   145–155; die Alternative wären 130 Shots und damit zu wenige.
3. **Aktlängen weichen ab.** Akt 4 ist mit 36 s kürzer als der Richtwert 55 s,
   Akt 5 mit 106 s länger als 85 s. Die Grenzen liegen dort, wo der fertige
   Text seine Absätze setzt; sie zu verschieben hieße, den Text neu zu
   gliedern.
4. **131 Quellzeilen statt 90–100.** Jede Rekonstruktion trägt die Zeile
   `Rekonstruktion`. Das ist nach § 5 der Grund, warum es keine
   Persönlichkeitsrechtsfrage gibt — deshalb wurde nicht gekürzt.
5. **Kein Upload**, wie beauftragt. Freigabe nach § 9.7 steht aus.

---

## Überarbeitung vom 20.08.2026

Der erste Master war fertig und technisch sauber und trotzdem nicht gut. Der
Befund beim Ansehen: zu viele Wiederholungen, zu viele Bilder, denen man
ansieht, dass sie erzeugt sind, zu wenig Kamerabewegung, insgesamt monoton.
Alle vier Punkte waren messbar, und alle vier sind an der Ursache behoben.

**Kamerafahrt.** Der Filtergraph zählte den Zoom pro Bild hoch. Die Strecke
hing damit an der Standzeit, und bei 3,6 s Ø kam praktisch nichts zustande —
gemessen 4 bis 5. Der Weg wird jetzt über die Shotlänge interpoliert
(`p = on/frames`) und aus acht Bewegungen im Wechsel gezogen: hinein,
heraus, Schwenk links, Schwenk rechts, hoch, runter, diagonal hinein,
Schwenk und heraus. Gemessen am fertigen Master, erstes gegen letztes Bild
jedes Segments: **34,8 im Mittel für Einzelbilder**.

**Farbe.** Die Palette stand global im Style Key, in einem einzigen
Türkiston. Dadurch sah jeder Akt aus wie der vorige. Die Farbe steht jetzt
in `AKT_FARBE` und wechselt mit dem Akt — dunkle Kammer, warmes Wolframlicht
im Institut, Stahl und Kupfer in der Werkstatt, Aluminium im Spiegelakt,
gesättigte Farbe im Visionsakt, arktische Nacht, Küche gegen Polarnacht,
stiller Archivton am Schluss.

**Die Signatur des erzeugten Bildes.** Elf Motive trugen Polarlichtfarbe
mitten im Innenraum — Magenta- und Cyanbänder über Tisch, Papier, Hand und
Gesicht, in einem Fall ein Leuchten, das aus der Haut kam. Genau daran
erkennt man ein erzeugtes Bild sofort. Die Regel steht jetzt im Style Key:
Polarlicht gehört an den Himmel und ins Fenster, ein Innenraum wird von
seinen eigenen Lampen beleuchtet. Alle elf wurden neu erzeugt. Prüfen mit
`python tools/spg_neonpruefung.py <timeline.json>`.

**Wiederholungen.** 19 Stellen liefen mit demselben Bild zweimal im selben
Akt. Dafür sind 30 zusätzliche Motive entstanden; die Einzelbildzahl steigt
von 89 auf 117, Wiederholung im selben Akt auf 0. Dabei sind auch zwei
falsch gesetzte Bilder aufgefallen — unter „Einen Kreis" lief ein
Blätterstapel, unter „Ein Dreieck" ein Kreis. Beide haben jetzt ihr Motiv.

**Die Fahrt lief in Stufen.** Der zweite Befund nach dem ersten Nachbessern:
„die Kamerabewegung zappelt und wackelt". Zwei getrennte Ursachen, beide nur
am fertigen Bild zu sehen, nicht am Filtergraph.

`zoompan` rechnet ganzzahlig. Es bekam ein Bild in Ausgabegröße, also war ein
Schritt ein voller Ausgabepixel. Die Vorlage geht jetzt auf 7680×4320, bevor
`zoompan` daraufsieht — ein Schritt ist dann ein Viertel Ausgabepixel.

Bei langsamen Fahrten reicht das nicht: liegt der Schritt je Bild unter einem
Ausgabepixel, rundet die Fahrt abwechselnd auf zwei und drei Eingangspixel.
Feiner rechnen hilft nur begrenzt (0,40 bei 7680, 0,24 bei 11520, 0,17 bei
15360). Deshalb wird die Fahrt in vier Zwischenschritten je Ausgabebild
gerechnet und gemittelt. Nebenbei entsteht die Bewegungsunschärfe, die eine
Kamera ohnehin hat.

| Aufbau | langsamster Shot | schneller Shot |
|---|---|---|
| 1920, ganzzahlig | 1,89 | 0,28 |
| 7680 | 0,40 | 0,09 |
| **7680 + vier Zwischenschritte** | **0,089** | **0,051** |

Dazu: die Strecke hängt jetzt an der Shotdauer statt für jeden Shot gleich zu
sein — ein Shot von einer Sekunde mit derselben Strecke wie einer von acht war
ein Ruck. Die Enden laufen weich an und aus. Bewegtbild bekommt keinen Schwenk
mehr, nur eine ruhige Fahrt aus der Mitte; ein Schwenk auf einem Clip, der
sich selbst bewegt, legt zwei Bewegungen übereinander.

Prüfen mit `python tools/spg_zappelpruefung.py <timeline.json>`.

**Der Render läuft parallel.** Ein einzelner ffmpeg-Lauf nutzt im Filterteil
rund anderthalb der sechs Kerne — gemessen 29,5 %. Die Segmente hängen nicht
voneinander ab, also laufen jetzt vier nebeneinander: 73 % Auslastung, rund
zweieinhalbmal so schnell.

**Thumbnail.** Das erste zeigte ein erzeugtes Gesicht, und ein Gesicht ist
die Stelle, an der ein erzeugtes Bild zuerst auffliegt. Jetzt sitzt die
Person von hinten als Silhouette in der Spirale, das Polarlicht fällt über
den Rand herein. Zweite Zeile in Kupfer statt Grün — grüne Schrift auf
grünem Polarlicht war bei 246 px zur Hälfte weg. Die Unterzeile lautet nicht
mehr „Sie sagen: nein."; sie hat die Überschrift im selben Bild
zurückgenommen.
