# Schlafparalyse-Shorts — Produktionsplan

Sechs eigenständige Ergänzungen zu EP06–EP08. Kein Short ist ein Ausschnitt aus
der Longform.

**Aktueller Stand: V4.** V1 und V2 sind abgelöst; die Ordner `assets`,
`assets_vertical_v2`, `render`, `render_vertical_v2`, `final` und
`final_vertical_v2` bleiben nur als Historie liegen.

| ID | Bezug | Arbeitstitel | Kernversprechen |
|---|---|---|---|
| SP06A | EP06 | Warum du trotz Brustdruck weiteratmest | Der Atem fühlt sich blockiert an, obwohl das Zwerchfell weiterarbeitet |
| SP06B | EP06 | Rückenlage und Schlafparalyse | Ein praktischer, aber nicht magischer Risikofaktor |
| SP07A | EP07 | Albtraum war einmal ein Wesen | Die ursprüngliche Bedeutung von Mare/Mara/Mahr |
| SP07B | EP07 | Der unsichtbare Zeuge von Salem | Wie private Gewissheit kurz zur öffentlichen Tatsache wurde |
| SP08A | EP08 | Warum trägt der Hat Man einen Hut? | Beleggrenze plus Silhouetten-Hypothese |
| SP08B | EP08 | Das Experiment mit der unsichtbaren Person | Eine elektrisch ausgelöste Präsenzillusion |

## Look

Fotorealistische, nüchterne Dokumentarbilder: tiefe Graphitschatten mit
Zeichnung, zurückhaltendes Praktikallicht, kaltes Mondlicht, feines Korn. Keine
lesbare Schrift in den generierten Bildern. Der in V1 geplante Papier- und
Halftone-Look wurde nie umgesetzt und ist gestrichen.

Pro Short gibt es **eine feste Besetzung und einen festen Drehort**. In V2
wechselte in SP06A und SP06B die Hauptfigur fast jeden Shot, was den Film zur
Stockfoto-Diashow gemacht hat.

## Pipeline

| Schritt | Werkzeug | Ergebnis |
|---|---|---|
| 1. Text | `V4_SCRIPTS.json` | Sprechfassung, 86–99 Wörter pro Short |
| 2. Stimme | `tools/schlafparalyse_shorts_v4_voice.py` | `voice_v4/*_GEORGE_V4.mp3` + Forced Alignment |
| 3. Bilder | `tools/generate_schlafparalyse_shorts_v4.py` | `assets_v4/SHOT01–16.png`, nativ 9:16, 1536×2752 |
| 4. Bild-QA | `tools/qa_schlafparalyse_shorts_v4_assets.py` | Kontaktbögen in `QA_ASSETS_V4/` |
| 5. Schnitt | `tools/render_schlafparalyse_shorts_v4.py` | `final_v4/*_FINAL_V4.mp4` + `QA_REPORT.json` |

## Sprecher

George / ElevenLabs `JBFqnCBsd6RMkjVDRZzb`, `eleven_multilingual_v2`.
Settings V4: stability 0.52, similarity 0.80, style 0.10, speed 1.02,
speaker boost an. Etwas offener und langsamer als die V2-Fassung (0.58 / 1.06),
weil die neuen Texte aus kurzen Sätzen bestehen und Pausen brauchen.

**Invariante:** Ein Short ist genau eine durchgehende ElevenLabs-Datei. Es gibt
keine internen Voice-Stitches, an denen Wörter verschluckt oder doppelt
angesetzt werden könnten.

## Bekannte Fehlerbilder der Bildgenerierung

Diese vier sind mehrfach aufgetreten und stehen deshalb explizit im
Style-Block. Sie brauchen trotzdem eine Sichtprüfung, weil kein
automatischer Test sie zuverlässig fängt:

1. Gekipptes Zimmer — Bett oder Person liegt quer zur Handyachse.
2. Gerendeter Rahmen — Handy-Bezel, Passepartout oder Polaroid um die Szene.
3. Doppelbelichtung — dieselbe Person zweimal im Bild.
4. Angeschnittene Köpfe bei engen Bildausschnitten.

Aussortierte Generierungen liegen unter `assets_v4_rejected/`.

## Warum kein Ken Burns in V2 war, und warum er jetzt zurück ist

V1 nutzte `zoompan` direkt auf 1080×1920. Der Filter rundet das Crop-Rechteck
auf ganze Eingangspixel; bei langsamer Bewegung liegt der Schritt unter einem
Pixel pro Frame und alterniert sichtbar. V2 hat daraufhin jede Bewegung
entfernt — und wurde zur Diashow mit Metronom.

V4 rendert auf einer dreifach übersampelten Leinwand **und** skaliert den
Zoomweg mit der Shotlänge, sodass die Crop-Kante immer mehr als zwei
Supersample-Pixel pro Frame wandert. Messgröße ist die Lag-1-Autokorrelation
der Frame-Differenzreihe; stark negativ heißt Stottern:

| Verfahren | Lag-1 |
|---|---:|
| V1, naiv auf 1080×1920 | −0,51 |
| 3× übersampelt, langsamer Zoom | −0,51 |
| 3× übersampelt, Zoomweg an Shotlänge gekoppelt | −0,16 |
