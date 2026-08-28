# EP01_EN Final Visual QA Report

## Verdict

**PASS / READY.** Dokument-, Timeline-, Motion-, Audio-, Render- und serienweite No-Repeat-QA sind bestanden.

## Linearer Picture-Lock

- Voice-Cues: 129
- Finale EDL-Events / eindeutige visuelle Zustände: 111 / 111
- Asset-Returns nach einem Wechsel: 0
- Exakte Content-Duplikate: 0
- Fehlende ausgewählte Dateien: 0
- Serienkollisionen mit dem zugänglichen Gateway-V7-Finalschnitt: 0 exakt, 0 perceptual candidates
- Permanente Produktionskategorie-Badges: 0
- `series_usage`: alle finalen Exporte `EP01_ONLY`

Der Fort-Meade-Handoff nutzt zwei eigene EP01-Karten und übernimmt kein Gateway-Bild.

## Bilddramaturgie

| Modus | Finale Dauer | Anteil |
|---|---:|---:|
| Subjektiv/mystisch | 110.40 s | 25.4 % |
| Physische Kammer | 85.20 s | 19.6 % |
| Erklärgrafik | 72.20 s | 16.6 % |
| Dokumentbeleg | 47.60 s | 11.0 % |
| Testprotokoll | 38.92 s | 9.0 % |
| Personen-/Zeitgeschichte | 29.44 s | 6.8 % |
| Belegprozess | 18.60 s | 4.3 % |
| übrige Modi | 32.28 s | 7.4 % |

Die frühere Grafik-/Dokumentdominanz ist aufgelöst. Die Folge entwickelt sich als lineare Reise von Kozyrevs Person und Zeitkontext über Metall/Geometrie, Versuch und Isolation zu subjektiver Wahrnehmung, offenen Theorien, sauberem Testdesign, fehlendem Resultat und Schluss-Handoff.

## Dokument-Evidenz

- Tatsächlich verwendete Dokumentzustände: 9
- Alle statisch ohne Pan/Zoom
- Originalquelle, Seite und Phrase geprüft
- vollständige relevante Sätze/Blöcke sichtbar
- KZ_DOC_028 und KZ_DOC_029 für mobile Lesbarkeit aus unveränderten Original-Rasterfragmenten neu gestapelt
- keine zufälligen Textfragmente, kein erfundener lesbarer Text
- finale Dokumentkontaktbögen und 480×270-Proof: PASS

## Holds und Bewegung

- Kein statischer Hold ab 8 Sekunden
- Kein unbegründeter Hold über 10 Sekunden
- Fünf längere Events sind echte progressive Clips: 9.16–13.96 s; jeder besitzt eine dokumentierte Zuschauerbegründung und sichtbar fortschreitende Zustände
- 12 Clips: 1920×1080, 25 fps, vollständiger Decode PASS; Start/Mitte/Ende visuell geprüft
- 45 geeignete filmische Stills: projektweite 4×-Raumüberabtastung auf
  7680×4320, vier zeitliche Zwischenpositionen je Ausgabeframe, Cosine-Easing
  und `tmix`-Mittelung; Bewegungs-QA 45/45 PASS
- Vorher/Nachher-Kontrolle: alter Kozyrev-Render 35/45 FAIL, korrigierter
  Render 0/45 FAIL
- Dokumente, Karten, Test- und Erklärgrafiken: statisch

## Identität, Geometrie und Rechte

- Kozyrev erscheint authentisch beim ersten Namens-/Biografiebeat; 1983/1996-Kontradiktion folgt unmittelbar.
- Kaznacheev und Trofimov erscheinen mit belegten, dokumentarisch geprüften Quellen an ihrem ersten gemeinsamen Research-Beat.
- Die Kammer bleibt als offene, gekrümmte Aluminium-Paneelgeometrie konsistent; keine geschlossene Sci-Fi-Kapsel.
- Rechte-unklare Research-Referenzen KZ-SRC-010 bis 014 sind nicht ausgewählt.
- Ausgewählte Drittquellen sind Public Domain/CC0, amtlicher bzw. enger dokumentarischer Quellenbeleg oder ausdrücklich als geprüfte dokumentarische Kurzquotation geführt; vollständige Credits liegen im Upload-Paket.

## Render und Audio

- Masterdauer: 434.640 s
- Video: H.264, 1920×1080, 25 fps
- Audio: AAC, 48 kHz Stereo, -14.0 LUFS, -0.9 dBFS True Peak
- eingebettete englische Untertitel plus separate SRT/VTT
- voller Decode: PASS
- Black-/Silence-Scan: 0 / 0
- alle 111 EDL-Mittelpunkte geprüft; 6 chronologische Kontaktbögen
- vollständiger bestehender Full-Mix-Höraudit: PASS, kein Pickup/Remix erforderlich

Maschinenlesbare Belege: `05_QA/FINAL_TIMELINE/EP01_FINAL_TIMELINE_PRE_RENDER_QA.json`, `05_QA/MODE_CLUSTER_QA.json`, `05_QA/REVIEW_RENDER_QA.json`, `05_QA/EP01_EN_CAMERA_MOTION_SMOOTHNESS_QA.json`, `05_QA/SERIES_GATEWAY_COMPARISON.json`.
