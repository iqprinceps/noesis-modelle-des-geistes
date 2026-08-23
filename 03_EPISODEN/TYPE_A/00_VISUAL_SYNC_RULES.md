# TYPE A — Visual Sync & Generative Image Rules

## Ziel

Alle 5–8 Sekunden soll sich die visuelle Information ändern — **nicht zwingend das zugrunde liegende Asset**. Ein Originaldokument darf während eines Zitats länger stehen, solange Crop, Highlight oder Kamerabewegung dem gesprochenen Satz folgt.

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

Jede Rekonstruktion muss im Schnitt entweder global als synthetisch offengelegt oder bei Bedarf klein als `REKONSTRUKTION` markiert werden. Sie illustriert den gesprochenen Inhalt; sie ist niemals Evidenz.

## Referenzbilder

Referenzbilder dienen der Formtreue (Gerät, Ort, Material, Zeitraum). Das Prompting soll ausdrücklich verlangen:
- Gerätetyp/Geometrie aus Referenz übernehmen,
- keine neuen Messinstrumente oder Eigenschaften erfinden,
- keine nicht belegten Effekte sichtbar machen,
- Zeit- und Ortsdetails nur soweit belegt.

## 20-%-Reserve

Reservebilder sind keine zusätzlichen Pflicht-Cues. Sie werden erzeugt, um folgende Probleme abzufangen:
- unbrauchbare Hände/Gesichter,
- zu ähnliche Kompositionen,
- fehlende B-Roll in einer längeren Voicepassage,
- zusätzliche Crop-/Transition-Bedürfnisse,
- ein Prompt trifft die Aussage visuell nicht exakt.

## Schnittdichte

- Normaler Erklärbeat: 5–8 s pro visuelle Information.
- Starker Dokumentbeleg: 8–18 s möglich, wenn innerhalb des Dokuments visuelle Zustände wechseln.
- Porträt: meist 5–9 s, danach Detail/Timeline/Ort.
- Abstrakte Metapher: maximal 5–7 s am Stück.
- Keine zwei generischen KI-Laborbilder direkt nacheinander, wenn ein echtes Dokument/Diagramm verfügbar ist.
