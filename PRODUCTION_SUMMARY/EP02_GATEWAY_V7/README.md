# EP02 Gateway V7

**Stand:** 19.08.2026
**Status:** Master gerendert, technische QA bestanden. **Kein Upload.**
**Laufzeit:** 10:38 (10:18 Voice + 20 s Endcard)

---

## Was V7 gegenüber V6 ist

V6 war eine reine Bild- und Tonüberarbeitung auf dem alten Text. V7 ist
**neuer Text, neue Stimme, neue Assets** — und übernimmt die Bildarbeit aus V6.

| | V6 | V7 |
|---|---|---|
| Stimme | Helmut Clark (`TUKJhQmz…`), deutsch | **George** (`JBFqnCBs…`), erprobte DeBeers-Werte |
| Tempo | speed 1.12 | **1.06** |
| Text | 1.222 Wörter | **1.370 Wörter** |
| Shots | 131 | **149** |
| Bewegtbild | keins | **4 eigene Animationen** |
| Fragen an den Zuschauer | 3 | 4 |
| Cliffhanger | 0 | 6 |
| CTA | nur Endcard | Mid-Roll bei 6:20 + Endcard |

---

## Die inhaltlichen Eingriffe

**Gestrichen:** der Portrait-Disclaimer zu McDonnell (drei Sätze
Produktionsbuchhaltung mitten im Film), sämtliche Rücknahmesätze
(„Es beweist nicht…", „Dokumentiert ist / Nicht dokumentiert ist…",
„Das ist interessant, aber…"), der Methodenabsatz über Trefferregeln.

**Neu und ausgebaut:**

1. **Bentov wird eine Figur.** Holocaust-Überlebender, Erfinder des
   steuerbaren Herzkatheters, Theorie vom Körper als schwingendem Oszillator
   — und sein Tod am 25. Mai 1979 in American Airlines Flug 191 auf dem Weg
   zu einem Vortrag über genau diese Arbeit. Vier Jahre bevor die Army ihr
   Modell darauf baut.
2. **Die zehn Ziffern bekommen einen eigenen Akt** (6:43–7:55). Dass niemand
   alle zehn traf, wird als das erzählt, was es ist: die Form, die eine echte
   Anomalie hat, nicht die einer erfundenen Geschichte.
3. **Empfehlung J und K ausgebaut.** Ein Offizier der US Army empfiehlt
   Vorbereitung auf nicht-körperliche Intelligenzen und Schutzwälle aus
   Bewusstsein um militärische Anlagen. Im Hook vorweggenommen, in Akt 7
   eingelöst.
4. **Monroe bekommt einen Anfang:** Radiomanager, der seinen eigenen Körper
   von außen sieht und ein Labor baut statt zum Arzt zu gehen.
5. **Forschungsteil von 80 auf 35 Sekunden**, umgedreht auf „was ließe sich
   überhaupt prüfen".

---

## Neue Assets

**Vier prozedurale Animationen** (`motion/`), gebaut mit numpy und PIL,
Frame für Frame nach ffmpeg — kein Browser, deterministisch, exakt in der
Markenpalette. V5 hatte vier HTML-Canvas-Simulationen im Ordner liegen, die
nie gerendert wurden.

| Datei | Rolle |
|---|---|
| `binaural.mp4` | Zwei Töne werden zur Schwebung. Trägt Akt 3. |
| `resonanz.mp4` | Bentovs Körper als Oszillator, Wellen laufen nach außen. |
| `zeitrad.mp4` | Focus 15, sechzehn Speichen in die Vergangenheit. |
| `feld.mp4` | Rauschen ordnet sich zum Gitter. Bild für den Sprung. |

**Vier neue Motive** über Vertex AI (`visuals/generated/gw7_*.png`):
Monroes erste außerkörperliche Erfahrung, das leere Gate in O'Hare,
der Zehn-Ziffern-Versuch als Szene, McDonnell am Schreibtisch.

**Vier neue Karten** (in `EP02_GATEWAY_V6/visuals/cards/`):
`V6_CARD_FLIGHT191`, `V6_CARD_FIVE_PERCENT` (hundert Punkte, fünf gold),
`V6_CARD_COMMENT` (Mid-Roll-CTA), `V6_CARD_DIGITS`.

---

## Kapitel

```text
00:00 Drei Beobachter, drei Zeiten
00:58 Die drei Männer hinter dem Modell
02:59 Zwei Töne
04:07 Der Sprung
04:58 Die Stufen
06:23 Zehn Ziffern
07:33 Empfehlung H, J und K
08:44 Was bleibt
```

---

## Textpflege

Es gibt **eine** Textquelle: `07_VOICE_SCRIPT_CLEAN_V7.txt`.

```bash
python tools/gw_v7_texts.py
```

leitet daraus die acht Sprechtexte ab (nur Zahlen und Daten werden
ausgeschrieben). Dieselbe Reinschrift geht ins Forced Alignment, in die
Untertitel und in die Bildanker. V2 pflegte zwei Fassungen getrennt — das ist
die Fehlerquelle, die hier entfällt.

Änderungen **immer in der Reinschrift**, nie in den Sprechtexten.

---

## Pipeline

```bash
python tools/gw_v7_texts.py
```

```bash
python tools/gw_v7_voice.py all
```

```bash
python tools/produce_ep02_gateway_v7.py all
```

Dazwischen einmalig die Stems erzeugen:
`elevenlabs_cli.py batch --batch-file voice/voice_batch.json --execute`

---

## Sprachregeln für diesen Kanal

Zwei Muster sind aus dem Text vollständig entfernt und dürfen nicht
zurückkommen:

**1. Die Antithese.** „X sollte nicht A. X sollte B." · „Die Frage lautet nicht
A, sondern B." · „Nicht poetisch, konkret." Neun Stellen im ersten Entwurf.
Die Figur klingt geschliffen und liest sich nach zwei Wiederholungen als
Maschine. Ersetzt durch direkte Aussagen und echte Fragen.

**2. Der Rücknahmesatz.** „Das ist die Annahme." · „Das ist die Erklärung des
Berichts, nicht sein Ergebnis." · „Das ist interessant, aber…" Solche Sätze
entwerten genau das, was den Zuschauer gerade gepackt hat. Was in der Akte
steht, wird als das erzählt, was in der Akte steht — zugeschrieben mit
„schreibt McDonnell", nicht relativiert.

Dasselbe gilt für die Karten: keine Fußnote, die die Karte selbst wieder
einkassiert.

---

## Offen

1. **Kontrollhörung.** George spricht die englischen Begriffe nativ; die
   Schreibweise `CIA` (statt `C I A`) wurde nach Hörprobe G gewählt. Bitte
   im Master gegenprüfen.
2. **Thumbnail** — das V6-Thumbnail passt inhaltlich weiter, könnte aber auf
   den neuen stärksten Beat umgebaut werden.
3. **Vier Fragezeichen statt sieben.** `tools/gw_pruefe_text.py` meldet das
   als einzigen offenen Punkt gegen den Produktionsstandard. Drei zusätzliche
   Fragen an den Aktenden würden eine neue Voice-Runde kosten — für die
   nächste Folge von Anfang an einplanen.
4. **Upload** — ausgeführt am 20.08.2026. Video `A10PQ9rHiRA`, Kanal
   NOESIS Deutsch, terminiert auf 24.08.2026 17:00 (+02:00). Thumbnail,
   Untertitel und Playlist gesetzt. Stand in `upload/upload_state.json`.

---

## Ältere Fassungen

V1 bis V6 liegen unberührt daneben. V6 bleibt die letzte Fassung auf dem
alten Text und der alten Stimme.
