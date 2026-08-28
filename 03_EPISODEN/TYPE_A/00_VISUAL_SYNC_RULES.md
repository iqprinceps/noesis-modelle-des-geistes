# TYPE A — Visual Sync & Generative Image Rules

## Ziel und Geltung

Diese Regeln dienen der semantischen Voice-Bild-Synchronität. Kreative Mengen,
Standzeiten und Offenlegungsformen werden je Episode aus Nutzersicht entschieden;
`01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md` hat Vorrang.

Ein Bild darf einen zusammenhängenden Gedanken tragen. Danach entwickelt sich der
visuelle Ablauf mit einem neuen Motiv weiter. Ein Originaldokument darf während
eines zusammenhängenden Zitats länger stehen, solange Crop, Highlight oder
Kamerabewegung dem gesprochenen Satz folgt; nach Verlassen dieses Blocks kehrt
diese Seite nicht später als Füllbild zurück.

## Synchronisations-Hierarchie

1. Sprecheraufnahme erzeugen.
2. Wort-Timestamps/Transkript aus der finalen Aufnahme gewinnen.
3. `voice_anchor_start` und `voice_anchor_end` aus `VISUAL_CUE_SHEET.csv` gegen die Audio-Timestamps mappen.
4. Erst dann echte In/Out-Timecodes setzen.
5. Bildwechsel bevorzugt auf Satzteil-/Gedankenwechsel, nicht mitten in Eigennamen oder Zahlen.

Die geschätzten Timecodes im CSV sind nur Layout-/Budgetwerte.

## Dokumentregel

- Originalseite, niemals KI-Nachbau.
- Ganze Seite 0.8–1.5 s etablieren, dann auf den relevanten Absatz fahren.
- Highlight startet synchron mit dem gesprochenen Schlüsselwort.
- Highlight nur auf verifizierter Originalformulierung; bei Paraphrase den Quellabschnitt markieren, nicht erfundene Wörter einblenden.
- Wenn der Sprecher 12–18 s über denselben Absatz spricht, bleibt das Dokument stehen; visuell dürfen Crop, Zoom und Highlight wechseln.

## Historische Personen

Benannte reale Personen werden mit echten freigegebenen Porträts gezeigt. Keine synthetischen Gesichter von Kozyrev, McDonnell oder anderen benannten Personen erzeugen. Rekonstruktionen dürfen anonyme Forscher, Analysten und Versuchspersonen zeigen.

## KI-Rekonstruktionen

Rekonstruktionen müssen redaktionell von Originalmaterial unterscheidbar bleiben,
aber nicht dauerhaft beschriftet werden. Die Produktionsklasse steht im Manifest.
Optional kann beim ersten Eintritt in einen längeren Rekonstruktionsblock für
1,5–2,0 Sekunden eine dezente Einordnung erscheinen. `INNER / HYPOTHESIS` und
andere Produktionscodes sind niemals sichtbare Dauerlabels. Eine Rekonstruktion
illustriert den gesprochenen Inhalt; sie ist keine Evidenz.

## Referenzbilder

Referenzbilder dienen der Formtreue (Gerät, Ort, Material, Zeitraum). Das Prompting soll ausdrücklich verlangen:
- Gerätetyp/Geometrie aus Referenz übernehmen,
- keine neuen Messinstrumente oder Eigenschaften erfinden,
- keine nicht belegten Effekte sichtbar machen,
- Zeit- und Ortsdetails nur soweit belegt.

## Reserve nach Bedarf

Es gibt keine feste Reservequote. Reservebilder werden nur erzeugt, um konkret
erkannte Probleme abzufangen:
- unbrauchbare Hände/Gesichter,
- zu ähnliche Kompositionen,
- fehlende B-Roll in einer längeren Voicepassage,
- zusätzliche Crop-/Transition-Bedürfnisse,
- ein Prompt trifft die Aussage visuell nicht exakt.

## Kein visueller Rücksprung

Ein Still, Dokument, Kartenexport oder Clip darf nur in einem zusammenhängenden
Timeline-Block vorkommen. Nach dem Wechsel zu einem anderen Motiv ist ein späterer
Return desselben Assets nicht zulässig. Neue Crops, Zooms, Pans oder Overlays des
gleichen Exports umgehen diese Regel nicht. Wiederkehrende Themen erhalten einen
neuen belegten Kontext oder einen sichtbar weiterentwickelten Bildzustand.

## Schnittdichte

- Statischer oder nahezu statischer Shot: normalerweise etwa 3–6 s.
- Ab 8 s: bewusster Retentionreview statt automatischer Freigabe.
- Etwa 10 s sind eine seltene Oberkante, keine starre Grenze. Länger nur mit
  sichtbarer innerer Entwicklung und konkreter Zuschauerbegründung.
- Ein langsamer Zoom, Crop, Pan oder Farbwechsel allein trägt keinen langen Hold.
- Benachbarte Cues desselben Bildzustands zählen zusammen als ein Hold.
- Keine zwei generischen KI-Laborbilder direkt nacheinander, wenn ein echtes Dokument/Diagramm verfügbar ist.
