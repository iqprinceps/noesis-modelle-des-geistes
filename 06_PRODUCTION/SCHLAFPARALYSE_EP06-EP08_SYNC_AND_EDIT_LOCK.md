# Schlafparalyse EP06-EP08 — Voice-, Visual- und Edit-Lock

Status: verbindlicher Produktionslock nach EP04A-Referenzaudit

EP04A bleibt Vorlage für George, Take-Grenzen, Forced Alignment, Cue-Synchronität,
SFX-Stems und technische Auslieferung. Seine visuelle Wiederholung und seine
Kameraamplituden werden ausdrücklich nicht übernommen.

## Voice

- Sprecher: George, Voice-ID `JBFqnCBsd6RMkjVDRZzb`
- Modell: `eleven_multilingual_v2`
- Serienlock: stability `0.58`, similarity `0.80`, style `0.08`, speed `1.06`,
  speaker boost `true`, seed `2402`
- Takes enden an vollständigen Gedanken, Mikroszenen oder natürlichen Atemstellen.
- Keine Zeitdehnung. Falsche Länge wird durch Textüberarbeitung und neue Aufnahme
  korrigiert.
- Zieltempo ungefähr 132–140 gesprochene Wörter pro Minute, ohne hektische
  Satzkaskaden.
- Zahlen und Datumsangaben werden ausgeschrieben; keine Lautschrift-Krücken.

## Menschliche Textfassung

- Konkrete Situationen und sinnliche Details vor abstrakten Zusammenfassungen.
- Gesprochene Satzlänge variieren; kurze Sätze nur an echten Erkenntnis- oder
  Spannungsstellen.
- Fragen nur an Wendepunkten, nicht als künstliches Dauer-Retention-Muster.
- Attribution und Einschränkung im Gedanken selbst formulieren, nicht als
  nachgeschobenen Disclaimer.
- Keine KI-Floskeln wie „tauchen wir ein“, „faszinierende Reise“, „doch was, wenn“,
  „hier wird es spannend“ oder mechanische Dreierlisten ohne gesprochenen Rhythmus.
- Claims Locks aus den Drehbüchern bleiben inhaltlich unverändert.

## Bilddichte und Wiederholung

- Erster visueller Wechsel spätestens nach 2,5 Sekunden.
- Meist 3,5–5,5 Sekunden pro Einstellung; kein Still länger als 9 Sekunden.
- Wiederholungs-Slots maximal 15 Prozent.
- Kein identischer Frame direkt hintereinander.
- Ein Basisasset normalerweise höchstens zweimal pro Episode; ein dritter Einsatz
  nur als markiertes Leitmotiv mit neuer Aussage.
- Innerhalb desselben Akts kein Bild wiederholen, wenn eine Alternative existiert.
- Voicefenster über 8 Sekunden benötigen mindestens zwei unterschiedliche visuelle
  Informationen; über 14 Sekunden mindestens drei oder einen echten Clip.

## Originalmaterial

- Vorhandene Originalquelle schlägt KI-Rekonstruktion, wenn sie die Behauptung
  konkret belegt.
- Ziel EP06 und EP08: 25–35 Prozent der Laufzeit aus Original-/Quellenmaterial.
- Ziel EP07: 35–45 Prozent der Laufzeit aus Original-/Quellenmaterial.
- Mindestens alle 30–45 Sekunden ein neuer Original-, Dokument-, Technik- oder
  Forschungsanker.
- Dokumentcrops sind nur dann eigene Shots, wenn Full, Passage und Detail
  unterschiedliche Informationen vermitteln.
- Originale werden nicht durch KI-Faksimiles ersetzt oder inhaltlich verändert.

## Kamera und Motion

- Eigene Karten bleiben vollständig statisch: kein Zoom, kein Pan, kein Drift.
- Quellen-, Vergleichs-, Karten- und Dokumenttafeln bleiben statisch und lesbar.
- Echte Videoclips erhalten keine zusätzliche Ken-Burns- oder Kamerafahrt.
- Nur 40–60 Prozent gewöhnlicher Stills dürfen überhaupt bewegt werden.
- Normaler Still-Zoom 1,5–2,5 Prozent; Hold 0–1 Prozent; Pan höchstens ungefähr
  1,5 Prozent der Bildbreite.
- Motion muss einen Zustand, Ablauf oder Bedeutungswechsel zeigen. Ein reiner
  Kamera-Push zählt nicht als Clip.
- Ungefähr ein sinnvoller Transformationsclip je 45–75 Sekunden; nicht alle Clips
  müssen eingesetzt werden, aber kein Clip wird als Füllmaterial wiederholt.

## Karten

- Kartenanteil ungefähr 8–12 Prozent der Laufzeit.
- Normale Karte einmalig 3,5–5,5 Sekunden, CTA höchstens 6 Sekunden.
- Karten zeigen einen vollständigen Gedanken und höchstens drei Hauptelemente.
- Keine HUD-, Dashboard-, Kachel- oder generische KI-Infografik-Optik.
- Quellenhinweis beziehungsweise Rekonstruktionshinweis bleibt sichtbar.

## Ton

- Eigene Musik: Grundton unter 520 Hz, harmonische Schicht 700–2600 Hz und
  zurückhaltendes Pink Noise; hörbarer Anteil über 620 Hz für Smartphone-Wiedergabe.
- Musikbett ungefähr `-30 LUFS`, sauber gegen George geduckt.
- SFX erklären Räume, Materialien und Übergänge; keine Jump-Scares, Trailer-Booms,
  generischen Okkult-Drones oder Sounds, die eine übernatürliche Entität als objektiv
  real behaupten.
- Finale Mischung `-14 LUFS ±0,5`, True Peak höchstens `-0,8 dBTP`, 48 kHz Stereo.
- SRT entsteht erst aus der fertigen George-Aufnahme beziehungsweise dem Forced
  Alignment; Blöcke höchstens 84 Zeichen.

## Harte Gates

Vor dem Render müssen pro Episode beide Prüfungen bestehen:

```text
python tools/check_schlafparalyse_visual_coverage_v5.py EP06
python tools/check_schlafparalyse_edit_policy.py <timeline.json>
```

Analog für EP07 und EP08. Fehlende Coverage wird mit konkretem neuem Inhalt
geschlossen, nicht mit langen Holds oder stärkeren Kamerafahrten.

