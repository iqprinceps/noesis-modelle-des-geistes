# Schlafparalyse EP06–EP08 — finale Übergabe

**Stand:** 26.08.2026
**Status:** Alle drei Folgen sind fertig exportiert und die Serien-QA ist bestanden.

## Finaldateien

| Episode | Laufzeit | Video | Audio | Untertitel |
|---|---:|---|---|---:|
| EP06 | 10:19 | H.264, 1920×1080, 30 fps | AAC, 48 kHz Stereo | 180 Cues |
| EP07 | 10:39 | H.264, 1920×1080, 30 fps | AAC, 48 kHz Stereo | 194 Cues |
| EP08 | 10:36 | H.264, 1920×1080, 30 fps | AAC, 48 kHz Stereo | 181 Cues |

- `EP06_SCHLAFPARALYSE_V4/render/final/EP06_SCHLAFPARALYSE_V4_FINAL.mp4`
- `EP07_SCHLAFPARALYSE_V4/render/final/EP07_SCHLAFPARALYSE_V4_FINAL.mp4`
- `EP08_SCHLAFPARALYSE_V4/render/final/EP08_SCHLAFPARALYSE_V4_FINAL.mp4`

Finalmix-Messung:

| Episode | Integrated Loudness | True Peak | LRA |
|---|---:|---:|---:|
| EP06 | −14,00 LUFS | −0,91 dBTP | 2,40 LU |
| EP07 | −14,00 LUFS | −0,88 dBTP | 2,10 LU |
| EP08 | −14,00 LUFS | −0,94 dBTP | 2,40 LU |

## Voice-Übergänge und Inhalts-QA

Der Übergangsfehler wurde an der Ursache behoben. Jeder normalisierte Take
erhält jetzt 120 ms digitale Randsicherheit. Dadurch endet kein Wort mehr
direkt an einer Dateigrenze; die wahrgenommene Pause bleibt bei etwa 650 ms.

Zusätzlich wurden zwei konkrete Inhaltsfehler gefunden und neu eingesprochen:

- EP07: ElevenLabs hatte im achten Take „Stammbaum“ doppelt halluziniert.
  Der Satz wurde eindeutig neu formuliert und als Pickup ersetzt.
- EP08: Zwischen Take 16 und 17 war „medizinisch dokumentiert“ bereits im
  Autorentext doppelt angelegt. Take 16 wurde gekürzt und neu eingesprochen.

Die drei fertigen Master wurden anschließend mit ElevenLabs Scribe gegen die
Solltexte geprüft. Es bleiben nur Schreibweisen von Zahlen, Namen und
Komposita; keine verschluckten, eingefügten oder doppelt gesprochenen Inhalte.

## Karten aus Zuschauerperspektive

Die Karten aller drei Folgen wurden neu formuliert und erneut gerendert.
Interne Bezeichnungen wie „Sachlage“, „S1“ und „Zeitkontext“ sind aus dem
sichtbaren Video entfernt. Die Karten arbeiten jetzt mit verständlichen
Fragen, kurzen Aussagen und „Kurz gesagt“-Zusammenfassungen.

| Episode | Karten im Schnitt | Kartenzeit |
|---|---:|---:|
| EP06 | 13 | 56,7 s |
| EP07 | 10 | 49,3 s |
| EP08 | 12 | 55,5 s |

## Bildwiederholungen und visuelle QA

Der finale Schnitt enthält:

| Episode | Shots | unterschiedliche Dateien | Wiederverwendungen | identische Wiederholung unter 30 s |
|---|---:|---:|---:|---:|
| EP06 | 149 | 127 | 22 | 0 |
| EP07 | 140 | 127 | 13 | 0 |
| EP08 | 152 | 148 | 4 | 0 |

Gezielt ersetzt wurden unter anderem die engen Fogo-Wiederholungen in EP06,
die wiederholten Ägypten-/Dänemark-Karten in EP07 sowie die direkt benachbarten
Art-Bell-, BBS- und Schlussmotive in EP08. Wiederverwendungen mit größerem
Abstand bleiben nur dort, wo sie als verständlicher Rückruf funktionieren.

Ein erster neu erzeugter Fogo-Entwurf zeigte eine Person ohne sichtbaren Kopf.
Er wurde verworfen und liegt ausschließlich im Ordner `QA_REJECTED`. Die
korrigierte Fassung zeigt beide Personen vollständig. Ein weiteres Motiv mit
der erfundenen Beschriftung „Atemspur“ wurde ebenfalls aus dem Schnitt entfernt
und durch eine textfreie, visuell geprüfte Szene ersetzt.

Die Bildprüfung umfasst nun ausdrücklich:

- vollständige Köpfe, Hände, Körper und relevante Bildränder;
- keine ungewollt lesbaren oder erfundenen Beschriftungen;
- Motiv und Beleggrenze passend zum gesprochenen Satz;
- keine engen visuellen Wiederholungen;
- Abgleich eines Frames aus dem finalen Export, nicht nur der Quelldatei.

Beim letzten EP08-Austausch wurde dadurch zusätzlich ein Cache-Fehler entdeckt:
Der Schnittplan zeigte das neue Bild, der Export noch das alte Segment. Der
Renderer speichert nun einen Quellen-Fingerprint und invalidiert Segmente bei
geändertem Bild, geänderter Dauer oder geändertem Bewegungsmodus automatisch.

## Veo

Es wurden keine weiteren Veo-Clips ergänzt. Die vorhandenen Clips decken die
Bewegungsakzente bereits ab; die Retention-Lücken lagen in wiederholten Stills,
Karten und Voice-Übergängen. Neue Clips hätten an diesen Stellen keinen
zusätzlichen erzählerischen Nutzen gebracht.

## Uploadpakete und QA

Zu jeder Folge liegen Titel, Beschreibung, Kapitel, Quellen, Thumbnail und
deutsche Untertitel im jeweiligen `upload`-Ordner. Der abschließende technische
Seriencheck steht in `SCHLAFPARALYSE_EP06-EP08_FINAL_QA.md` und meldet
**BESTANDEN**.
