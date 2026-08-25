# EP08 — Wiederholungs- und Originalasset-Audit

**Planstand:** vor Voice-Erzeugung; Zeiten sind Schnittbudgets und werden nach Forced Alignment an Wortanker gebunden.  
**Gesamt:** 150 visuelle Slots · ca. 624.7 s inklusive 20-s-Endcard.

## Harte Kennzahlen

| Kennzahl | Ergebnis | Ziel | Status |
|---|---:|---:|---|
| Original-/Quellen-Slots | 58 / 150 | V5-Lock | PASS |
| Original-/Quellen-Laufzeit | 196.3 s / 624.7 s = 31.4 % | 25–35 % | PASS |
| Karten-Laufzeit | 56.0 s / 624.7 s = 9.0 % | 8–12 % | PASS |
| Bewegte gewöhnliche Stills | 29 / 57 = 50.9 % | 40–60 % | PASS |
| Erster visueller Wechsel | 2.5 s | <=2,5 s | PASS |
| Identische direkte Wiederholungen | 0 | 0 | PASS |
| Wiederholungs-Slots desselben fertigen Frames | 0 / 150 = 0.0 % | <=15 % | PASS |
| Maximale Nutzung eines konkreten Basisassets | 2x | <=2x | PASS |
| Hauptclips | 4, je einmal | 3–5 | PASS |
| Karten | 8, je einmal | 8 | PASS |
| Noch zu bauende redaktionelle Quellen-Crops/Composites | 22 | vor Render fertigstellen | OPEN |
| Noch zu beschaffende Originalquellen | 9 Slots | vor Render klären | OPEN |
| Noch zu generierende neue Stills | 2 | Promptbatch vorbereitet | OPEN |

## Bewegungslock

- Karten: vollständig statisch; keine Zooms, Schwenks oder Parallaxen.
- Dokumente, Screens und Originalquellen: `contain`, statisch und lesbar. Statt Ken Burns werden vorab unterschiedliche semantische Ausschnitte als eigene Dateien gebaut und hart geschnitten.
- Generierte Stills: 29 von 57 erhalten einen vorher festgelegten Micro-Push von 1,5–2,5 Prozent; alle übrigen bleiben statisch. Kein laterales Reisen, keine Diagonalflüge.
- Veo-Clips: native Transformation ohne zusätzliche Fahrt, Geschwindigkeitsänderung oder Reframing.
- Kein Still länger als 9 s; einzige Ausnahme ist die statische 20-s-Endcard nach dem gesprochenen Schluss.

## Wiederholungslogik

Die 150 Slots benutzen eindeutige fertige Frame-IDs. Wo eine Quelle zweimal vorkommt, sind es vorher gerenderte, inhaltlich verschiedene Ansichten — etwa Gesamtseite und belegrelevanter Ausschnitt. Das ist kein digitaler Zoom im laufenden Shot. Kein konkretes Basisasset liegt über zwei Verwendungen. Kein identischer Frame steht direkt hinter sich selbst, und jeder Clip sowie jede Karte erscheint nur einmal.
