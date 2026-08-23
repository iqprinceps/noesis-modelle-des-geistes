# Produktionsstandard — NOESIS / Modelle des Geistes

**Stand:** 19.08.2026
**Referenzfolge:** EP02 Gateway V7 (`06_PRODUCTION/EP02_GATEWAY_V7/`)
**Gilt für:** alle folgenden Episoden

---

Dieses Dokument hält fest, wie EP02 V7 gebaut wurde. Es ist kein Konzept,
sondern ein Rezept: konkrete Zahlen, konkrete Regeln, konkrete Fehler, die
schon einmal passiert sind. Wer eine neue Folge baut, arbeitet es von oben
nach unten ab.

**Oberstes Ziel ist Retention.** Alles andere ordnet sich dem unter, solange
es keine Lizenzprobleme erzeugt.

---

## 1 Aufbau

Acht Akte. Jeder Akt hat eine Aufgabe und endet mit einem Grund
weiterzuschauen.

| Akt | Aufgabe | Richtwert |
|---|---|---|
| 1 | Hook: der bizarrste konkrete Fund, dann die Quelle | 55–65 s |
| 2 | Die Menschen dahinter, mit einer echten Biografie-Wendung | 110–125 s |
| 3 | Der harmlose, nachvollziehbare Mechanismus | 60–70 s |
| 4 | Der Sprung ins Außergewöhnliche | 50–60 s |
| 5 | Die Landkarte / das System, ausgebreitet | 80–90 s |
| 6 | **Der Moment, in dem etwas passiert** | 65–75 s |
| 7 | Das wildeste Material der Akte, voll ausgespielt | 65–75 s |
| 8 | Was prüfbar ist, was bleibt, Schlussbild | 85–95 s |

Gesamt 1.300–1.450 Wörter, bei `speed 1.06` rund 10:00–10:40 plus 20 s
Endcard.

### Der Hook

1. Die bizarrste **konkrete** Handlung zuerst, in kurzen Sätzen. Keine
   Einordnung, keine Institution, kein Kontext.
2. Erst danach die Quelle: Datum, Autor, Behörde.
3. Die Umdeutung: welche Frage wirklich zählt.
4. **Vorgriff auf den stärksten Beat aus Akt 7.** In EP02: „Weiter, als die
   meisten vermuten. Auf den letzten Seiten empfiehlt er, Soldaten auf
   Begegnungen mit nicht-körperlichen Intelligenzen vorzubereiten."
5. „Aber der Reihe nach."

Erster Bildschnitt spätestens bei **2,5 s**. Quellen-Reveal um **17 s**.

### Der Moment, in dem etwas passiert

Akt 6 ist der wichtigste und der, den frühere Fassungen vergessen haben.
Jede Akte enthält irgendwo eine Stelle, an der etwas Konkretes versucht wurde
und ein Ergebnis herauskam. **Diese Stelle bekommt einen eigenen Akt.**

Ein unsauberes Ergebnis ist dabei wertvoller als ein sauberes. In EP02: „Manche
trafen genug Ziffern, um ihn zu beeindrucken. Alle zehn bekam niemand." Das
wird ausdrücklich als Stärke erzählt — so sieht eine echte Anomalie aus, eine
erfundene Geschichte hätte einen Volltreffer.

### Cliffhanger

Sechs Stück, an den Aktenden. Kurz, ein Satz, ohne Zusammenfassung des
Vorherigen. Beispiele aus EP02:

- „Was dabei herauskam, beginnt harmlos."
- „Dann macht die Akte einen Sprung, den man nur einmal richtig lesen muss."
- „Und dieser Offizier zeichnet jetzt eine Landkarte."
- „Und gegen dieses eine Problem entwirft er die Lösung, mit der dieses Video
  begonnen hat." ← schließt die Schleife zum Hook

### Interaktion

- **Mid-Roll-CTA** bei etwa 60 % der Laufzeit, direkt vor dem stärksten Akt.
  Binär gestellt, das kostet den Zuschauer eine Sekunde:
  „Schreib mir vorher in die Kommentare, was du bis hier glaubst."
- **Endcard**, 20 s, mit einer Ja/Nein-Frage und dem Verweis auf die
  Vorgängerfolge. Ohne diese 20 s kann YouTube keine Endscreens einblenden.
- Mindestens **sieben Fragezeichen** im Sprechtext.

---

## 2 Sprache

### Zwei verbotene Muster

**Die Antithese.** Im ersten V7-Entwurf steckte sie neunmal:

> „X sollte nicht A. X sollte B."
> „Die Frage lautet nicht A, sondern B."
> „Nicht poetisch, konkret."
> „Nicht als Metapher. Als Einsatzrisiko."

Die Figur klingt beim ersten Mal geschliffen und ab dem zweiten Mal maschinell.
Ersatz: direkte Aussage oder echte Frage.

**Der Rücknahmesatz.** Sätze, die zurücknehmen, was gerade Spannung erzeugt hat:

> „Das ist die Annahme."
> „Das ist die Erklärung des Berichts, nicht sein Ergebnis."
> „Das ist interessant, aber noch kein Beleg."
> „Dokumentiert ist … Nicht dokumentiert ist …"

Was in der Akte steht, wird als das erzählt, was in der Akte steht. Die
Zuschreibung übernimmt ein eingeschobenes „schreibt McDonnell" oder „steht in
der Akte" — **im Satz, nicht als nachgestellter Dämpfer.**

Falsch: „…könne sich mit einem Informationsfeld verbinden. Das ist die Annahme."
Richtig: „…verbindet sich, schreibt McDonnell, mit einem größeren Informationsfeld."

### Weitere Verbote

- **Keine Produktionsbuchhaltung im Film.** „Von X ist kein frei nutzbares
  Porträt bekannt" gehört in die Notizen, nicht in den Sprechtext.
- **Keine Methodenlehre am Stück.** Blindauswertung, Trefferregeln,
  Vorabdefinition: höchstens zwei Sätze, nie ein eigener Absatz.
- **Forschungsteil maximal 35 Sekunden**, und als „was ließe sich prüfen"
  formuliert, nicht als „warum es wahrscheinlich nichts ist".

### Prüfschritt vor der Voice

```bash
python tools/gw_pruefe_text.py <reinschrift.txt>
```

Meldet Antithesen, Rücknahmesätze, fehlende Fragen und Aktlängen.

---

## 3 Bild

### Mengengerüst

| Kennzahl | Ziel | EP02 V7 | EP01A |
|---|---|---|---|
| Shots | 140–155 | 148 | 155 |
| Ø Shotdauer | 3,5–4,5 s | 4,18 s | 3,63 s |
| **Einzelbilder** | **≥ 85** | **90** | **117** |
| Maximale Wiederholung | **≤ 4×** | 4× | 4× |
| Wiederholung im selben Akt | **0** | 0 | 0 |
| Bewegtbild | 3–5 Clips | 4 | 4 |

Wiederholungen prüfen:

```bash
python tools/gw_wiederholungen.py <timeline.json>
```

Ein Motiv, das dreimal oder öfter läuft, bekommt ein Gegenstück. Bei EP02
waren das elf zusätzlich generierte Motive.

### Verbote

- **Kein Stockmaterial.** V5 hatte drei Pexels-Clips im Schnitt: ein Mann mit
  Kettlebell am Strand lief fünfmal, unter anderem unter dem wichtigsten
  Umdeutungssatz der Folge. Ein Nachtclub lief elf Sekunden unter „der
  entscheidende Wechsel".
- **Kein Text im Bild, der nicht auf dem gezeigten Blatt steht.** Siehe § 4.
- **Keine unlesbaren Fachgrafiken.** PRISMA-Flussdiagramme, Forest Plots und
  Ähnliches sind bei 1080p und vier Sekunden Standzeit wertlos.
- **Kein Kontextfoto ohne Jahreszahl**, wenn es aus einer anderen Zeit stammt
  als das Erzählte.
- **Keine Polarlichtfarbe im Innenraum.** Magenta-, Cyan- und Grünbänder, die
  über Tisch, Papier, Hand oder Gesicht liegen, sind die Stelle, an der ein
  erzeugtes Bild sofort auffliegt. Farbe dieser Art gehört an den Himmel und
  ins Fenster. Ein Innenraum wird von seinen eigenen Lampen beleuchtet und von
  sonst nichts. Bei EP01A trugen elf Motive diese Signatur; alle elf wurden
  neu erzeugt, nachdem sie im Schnitt aufgefallen waren.
- **Kein Leuchten, das aus Haut kommt.** Der erste Kozyrev-Durchgang hatte
  Prompts wie „a glow that seems to come from the skin of her cheeks" — das
  widerspricht dem eigenen Style Key und sieht in jedem Fall gemacht aus.
- **Gesichter sind erlaubt und oft richtig.** Ein Gesicht im Lampenlicht,
  Augen geschlossen, ist eine starke Einstellung. Verboten ist nur das, was
  ein Gesicht kaputtmacht: Farbflecken auf der Haut, ein Leuchten von innen,
  ein zu frontaler Blick in die Kamera. Wo die Person anonym bleiben soll
  oder der Raum die Hauptsache ist, trägt die Rückenansicht besser — das ist
  eine Bildentscheidung, keine Regel.

Prüfschritt, bevor der Schnitt steht — der Anteil kräftig gesättigter
Magenta- und Cyanpixel je Motiv. Landschaften und Visionen dürfen oben
stehen, Innenräume nicht:

```bash
python tools/spg_neonpruefung.py <timeline.json>
```

### Format

Alles, was vom 16:9-Format abweicht, wird **vollständig eingepasst**, nie
beschnitten. Der Rand bekommt eine unscharfe, abgedunkelte Kopie derselben
Vorlage statt schwarzer Balken.

```python
contain = not (1.62 <= aspect <= 1.95)
```

Grund: Patentseiten (Seitenverhältnis 0,68) verlieren beim Beschnitt über die
halbe Höhe, breite Originaldiagramme (bis 2,70) bis zu 34 % der Breite. V5
hatte stattdessen gepaddet und ließ bis zu **69 % der Fläche schwarz**.

Eingepasste Vorlagen bekommen nur eine sehr leichte Kamerafahrt (Cap 1.045),
sonst wandert die Beschriftung wieder aus dem Bild.

Der Rand darf nicht flach werden. Bei EP01A war die unscharfe Kopie einer
cremefarbenen Patentseite nach dem Abdunkeln ein gleichmäßiges Grau über zwei
Drittel des Bildes — technisch nach Vorschrift, im Erleben eine Leerstelle.
Der Grund wird deshalb zusätzlich ins Nachtblau der Folge gezogen und
randseitig abgedunkelt, das Blatt bekommt eine schmale warme Kante:

```text
gblur=sigma=52, eq brightness -0.66 · saturation 0.28 · contrast 0.82,
colorbalance bs 0.22 · bm 0.10 · rs -0.06, vignette
Blatt: pad +6 px in 0x2E2418
```

So liest sich die Seite als fotografiertes Blatt auf einer Fläche statt als
Scan, der vor grauem Nichts schwebt.

### Kamera und Übergänge

- Ken Burns: acht Bewegungen im Wechsel — hinein, heraus, Schwenk links,
  Schwenk rechts, hoch, runter, diagonal hinein, Schwenk und heraus. Der Weg
  wird über die Shotlänge interpoliert (`p = on/frames`), nicht pro Bild
  hochgezählt; sonst hängt die Strecke an der Standzeit und kurze Shots
  stehen still.
- Gemessen wird am fertigen Master, nicht am Filtergraph: erstes und letztes
  Bild jedes Segments, mittlere Pixeldifferenz in Graustufen.
  EP01A liegt bei **34,8 im Mittel für Einzelbilder**; das einzige Segment darunter ist ein Schnitt von 1,4 s, bei dem die Strecke bewusst kurz ist.
  Der erste Durchgang lag bei 4–5 und wirkte wie eine Diaschau.
- Die Strecke hängt an der Shotdauer, nicht die Geschwindigkeit. Ein Shot von
  einer Sekunde mit derselben Strecke wie einer von acht ist ein Ruck.
  `tempo = clamp(dauer / 3.6, 0.50, 1.55)`, für Schwenks bei 1.0 gedeckelt —
  darüber klemmt `zoompan` am Rand fest und die Fahrt bleibt mitten im Shot
  stehen.
- Weiche Enden: 60 % linear, 40 % Smoothstep. Spitzengeschwindigkeit 1,2 statt
  1,5 des Mittels — genug, dass Anfang und Ende nicht schlagen, zu wenig, dass
  es in der Mitte zieht.
- Eingepasste Vorlagen behalten den kleinen Cap (1.045), sonst wandert die
  Beschriftung aus dem Bild.
- Blende 0,35 s an jeder Aktgrenze, Hartschnitt innerhalb der Akte.

### Die Fahrt muss glatt laufen

Zwei getrennte Fehler machen aus einer Fahrt ein Zappeln. Beide sind nicht am
Filtergraph zu sehen, nur am fertigen Bild.

**`zoompan` rechnet ganzzahlig.** Bekommt es ein Bild in Ausgabegröße, ist ein
Schritt ein voller Ausgabepixel und die Fahrt läuft in Stufen. Die Vorlage
wird deshalb auf **7680×4320** gebracht, bevor `zoompan` daraufsieht — ein
Schritt ist dann ein Viertel Ausgabepixel. Bewegtbild reicht 5760, es bringt
eigene Bewegung mit.

**Bei langsamen Fahrten reicht das nicht.** Liegt der Schritt je Bild unter
einem Ausgabepixel, rundet die Fahrt abwechselnd auf zwei und drei
Eingangspixel — ein Wackeln von rund 20 % der Geschwindigkeit, jedes Bild.
Feiner rechnen hilft nur begrenzt. Deshalb wird die Fahrt in **vier
Zwischenschritten je Ausgabebild** gerechnet und gemittelt (`tmix`): die vier
Positionen runden unterschiedlich, ihr Mittel bewegt sich in Vierteln.
Nebenbei entsteht die Bewegungsunschärfe, die eine Kamera ohnehin hat.

Kennzahl ist die **zweite Differenz**: wie stark sich die Bilddifferenz von
einem Bild zum nächsten ändert, im Verhältnis zum Mittel. Die Streuung allein
taugt nicht — eine Fahrt mit weichen Enden ändert ihre Geschwindigkeit
absichtlich. Zappeln ist das Hin und Her von Bild zu Bild.

| Aufbau | langsamer Shot | schneller Shot |
|---|---|---|
| 1920, ganzzahlig | 1,89 | 0,28 |
| 7680 | 0,40 | 0,09 |
| 11520 | 0,24 | — |
| 15360 | 0,17 | — |
| **7680 + vier Zwischenschritte** | **0,089** | **0,051** |

Der Rest ist kein Encoder-Rauschen: bei crf 6 statt 16 bleibt er stehen.
Richtwert für die Freigabe: **Median unter 0,10, kein Segment über 0,20** bei
einer Bilddifferenz ab 1,0.

```bash
python tools/spg_zappelpruefung.py <timeline.json>
```

### Der Render muss nicht langsam sein

Die feine Fahrt kostet Rechenzeit, aber weit weniger als der erste Aufbau
vermuten ließ. Zwei Messungen an EP01A, 155 Segmente:

| Aufbau | Segmente/min |
|---|---|
| seriell, Skalierung je Bild | 1,24 |
| vier parallel, Skalierung je Bild | ~2,0 |
| **vier parallel, Skalierung einmal** | **7,3** |

**Parallel.** Ein einzelner ffmpeg-Lauf nutzt im Filterteil rund anderthalb
Kerne — gemessen 29,5 % von sechs. Die Segmente hängen nicht voneinander ab,
also laufen mehrere nebeneinander: `arbeiter = cpu_count() // 2 + 1`, gedeckelt
bei vier. Ein Drittel der Kerne bleibt als Luft fürs System.

**Skalierung einmal.** Der größere Anteil. Bei einem Standbild lief die
Skalierung auf 7680×4320 für jedes Eingangsbild — bei vier Zwischenschritten
also 120-mal je Sekunde Ausgabe dasselbe Ergebnis. Der `loop`-Filter hält das
fertig skalierte Bild:

```text
-i bild.png -vf "scale=7680:4320…,crop=…,loop=loop=-1:size=1:start=0,fps=120,zoompan=…"
```

statt `-loop 1 -framerate 120 -i bild.png`. Am selben Segment unter gleicher
Last: 175 s statt 308 s, bei Bild für Bild identischem Ergebnis — gleiche
Dauer, gleiche Bildzahl, gleicher Zappelwert.

Für Bewegtbild gilt das nicht: dort sind die Eingangsbilder verschieden.

### Bewegtbild

Drei bis fünf prozedurale Clips pro Folge, gebaut in `tools/gw_motion.py`
mit numpy und PIL, Frame für Frame nach ffmpeg. Kein Browser, deterministisch,
exakt in der Markenpalette. Jeder Clip illustriert genau einen Begriff, der
sonst nur behauptet würde: eine Schwebung, eine Resonanz, ein Zeitrad, ein
Feld das sich ordnet.

---

## 4 Einblendungen

Zwei Zeilen unten links: deutsche Beschriftung, darunter die Quellzeile.

**Die Beschriftung benennt nur, was auf dem gezeigten Blatt steht.** Absender,
Abschnittsnummer, Datum, Lebensdaten, Originalüberschrift mit Übersetzung.

Die Probe: *Steht das so oder sinngemäß auf dem Blatt?* Wenn nein, gehört es
nicht ins Bild.

Falsch, weil Kommentar: „Freigabevermerk der CIA, 2003 — das Archiv, nicht der
Autor" · „Ein Patent belegt die Methode, nicht die Wirkung"

Richtig: „Freigabevermerk, 2003" · „Abschnitt 33: Informationsgewinnung" ·
„„Travel into the Past“ · Reise in die Vergangenheit"

Richtwert 25–35 Beschriftungen plus 90–100 Quellzeilen pro Folge. Shots unter
1,6 s bekommen keine.

Dokumentbilder dürfen **keine eingebrannten englischen Kopf- oder Fußzeilen**
tragen — sonst steht oben Englisch und unten Deutsch. Bereinigung:

```bash
python tools/gw_clean_docs.py
```

Karten sind ebenfalls durchgehend deutsch. V5 hatte zwölf englische Karten auf
17 Shots im Schnitt.

---

## 5 Personen und Porträts

**Reihenfolge, immer in dieser Folge:**

1. **Echtes Archivbild mit freier Lizenz.** Wikimedia Commons, NARA, DVIDS,
   Bundesarchiv, Wellcome, Smithsonian. Lizenz und Urheber in `SOURCES.md`
   neben der Datei ablegen, Attribution in die Videobeschreibung.
2. **Echtes Bild mit klärbarer Lizenz.** Anfragen, dokumentieren, erst danach
   verwenden.
3. **Rekonstruktion.** Wenn nichts existiert.

**Nicht verwendbar:** CC BY-**NC** (schließt einen Kanal aus) und CC BY-**ND**
(verbietet Beschnitt, Farbkorrektur und Kamerafahrt). Das Monroe-Institute-Archiv
auf archive.org fällt genau darunter.

### Wenn rekonstruiert wird

- Diskret als `Rekonstruktion` in der Quellzeile kennzeichnen. Das ist keine
  Vorsicht, sondern der Grund, warum es keine Persönlichkeitsrechtsfrage gibt.
- **Kein Heldenporträt.** Die Person in einer Handlung zeigen, halbnah, von der
  Seite oder von hinten. In EP02: Monroe an der Bandmaschine, Bentov an der
  Werkbank, McDonnell von hinten am Schreibtisch.
- Die Identität tragen die **echten Dokumente**: Unterschrift, Patentschrift,
  Briefkopf. Ein Gesicht muss das nicht leisten.

### Biografie als Erzählmotor

Jede Person bekommt eine echte Wendung, wenn es eine gibt. Bentov war im
ersten Entwurf „Autor, Tüftler und Erfinder medizinischer Geräte". Tatsächlich:
Holocaust-Überlebender, Erfinder des steuerbaren Herzkatheters, gestorben am
25. Mai 1979 in American Airlines Flug 191 auf dem Weg zu einem Vortrag über
genau die Arbeit, auf der die Army vier Jahre später ihr Modell aufbaut.

Solche Fakten sind belegbar und recherchierbar. **Vor dem Schreiben eine Runde
Biografie-Recherche pro Hauptperson.**

---

## 6 Ton

### Stimme

| Parameter | Wert |
|---|---|
| Voice | `JBFqnCBsd6RMkjVDRZzb` — George |
| Modell | `eleven_multilingual_v2` |
| stability | 0.58 |
| similarity_boost | 0.80 |
| style | 0.08 |
| **speed** | **1.06** |
| seed | 2402 |

`speed 1.12` war zu schnell und hat den Rhythmus holprig gemacht.

**Keine Lautschrift-Krücken.** George ist eine englischsprachige Stimme und
spricht `Wayne M. McDonnell`, `Gateway`, `Focus`, `Hemi-Sync`, `Fort Meade`
und `CIA` von sich aus korrekt. Getrennt geschriebene Buchstaben (`C I A`) und
Bindestrich-Phonetik (`Mak-Donnell`) erzeugen genau die Pausen, die stören.

Ausgeschrieben werden nur **Zahlen und Datumsangaben**.

### Musikbett

Eigensynthese, keine Fremdmusik. Drei Schichten: Grundton unter 520 Hz,
harmonische Schicht zwischen 700 und 2600 Hz, Pink Noise.

**Der Anteil über 620 Hz ist Pflicht.** V5 war komplett tiefpassgefiltert und
auf Handy-Lautsprechern nicht vorhanden — dort schaut die Mehrheit.

Intensitätskurve entlang der acht Akte, Spitze in Akt 6 und 7:

```
0.85  Hook
0.58  die Menschen
0.70  der Mechanismus
0.88  der Sprung
0.74  die Landkarte
0.92  der Moment
1.00  das wildeste Material
0.66  was bleibt
```

Bett auf −30 LUFS, Ducking gegen die Stimme, Mix auf −14 LUFS.

---

## 7 Auslieferung

| Prüfung | Wert |
|---|---|
| Auflösung | 1920×1080, H.264 High, yuv420p |
| Bildrate | 30 fps |
| Ton | AAC, 48 kHz, Stereo, 320 kbit/s |
| Lautheit | −14 LUFS ±0,5 |
| True Peak | ≤ −0,8 dBTP |
| Untertitel | SRT, Blöcke ≤ 84 Zeichen |
| Endcard | 20 s |

### Thumbnail

Ein Motiv, ein deutsches Schlagwort, hoher Kontrast. Immer eine
Lesbarkeitsprobe bei **246 px Breite** danebenlegen — das ist die Größe in der
App.

Nicht: englischer Text auf einem deutschen Kanal, Textwände, generische
Piktogramme. Das V5-Thumbnail war bei 246 px ein grauer Fleck.

### Kapitelmarken

Immer aus der fertigen Timeline erzeugen, nie aus einer früheren Fassung
übernehmen. In V5 zeigten die letzten beiden Kapitel hinter das Videoende.

---

## 8 Pipeline

Eine Textquelle, alles andere wird abgeleitet:

```bash
python tools/gw_v7_texts.py
```

```bash
python tools/gw_v7_voice.py all
```

```bash
python tools/produce_ep02_gateway_v7.py all
```

Die Reinschrift geht unverändert ins Forced Alignment, in die Untertitel und
in die Bildanker. Die Shots hängen an **Textankern**, nicht an festen Zeiten —
ändert sich der Sprechrhythmus, ziehen alle Bilder automatisch mit.

**Änderungen immer in der Reinschrift**, nie in den abgeleiteten Sprechtexten.
V2 pflegte beide getrennt; daher kamen die Abweichungen zwischen Gesprochenem
und Untertitel.

### Fallstricke aus der Praxis

- Abgebrochene Renderläufe hinterlassen halb geschriebene Segmente, die der
  Concat **stillschweigend überspringt**. Der Producer prüft deshalb jedes
  vorhandene Segment mit `ffprobe`, bevor er es überspringt.
- ffmpeg-Filterlabels dürfen nicht `[v]` oder `[a]` heißen — das kollidiert mit
  den Stream-Specifiern. Ein Label darf nur einmal verbraucht werden, sonst
  `asplit`.
- Videoclips brauchen `-stream_loop -1`, Standbilder `-loop 1`.

---

## 9 Freigabe

Vor jedem Upload:

1. Alle QA-Checks grün
2. Kontrollhörung auf Handy-Lautsprecher **und** Kopfhörer
3. Kontaktbogen durchsehen: keine Wiederholung im selben Akt, kein
   angeschnittenes Diagramm, keine englische Karte
4. Kapitelmarken gegen die fertige Laufzeit geprüft
5. Thumbnail bei 246 px geprüft
6. Attributionen für alle CC-Assets in der Beschreibung
7. **Ausdrückliche Freigabe des Kanalinhabers**

Kein Upload ohne Punkt 7.
