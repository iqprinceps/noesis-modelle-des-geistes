# EP06 — SFX- und Musik-Cue-Plan

**Status:** vollständig geplant, noch nicht gerendert  
**Grundsatz:** Stimme bleibt Vordergrund. Ton vermittelt Material, Raum und Körper; er behauptet nie eine objektiv anwesende Entität.

## Mischvorgaben

- Projekt-eigene Synthese/Foley, keine lizenzpflichtige Fremdmusik.
- 48 kHz, 24-bit WAV-Stems; SFX mono oder echtes Stereo, keine künstliche Extrembreite.
- Normaler Musikpegel etwa −30 LUFS unter der Voice, weich gegen George geduckt.
- VO-Arbeitsmaster ungefähr −18 LUFS integrated, ≤ −2 dBTP.
- Finaler Mix −14 LUFS ±0,5; True Peak ≤ −0,8 dBTP.
- Musik enthält stets eine hörbare Schicht oberhalb 620 Hz, damit sie auf Smartphone-Lautsprechern nicht verschwindet.
- Keine Trailer-Booms, Jumpscares, Reverse-Chöre, Herzschläge, Monsterstimmen oder Sci-Fi-Beepketten.

## Musikbogen

| Akt | Energie | Klangidee | Übergang |
|---|---:|---|---|
| S1 | 0,90 | trockener Raum, tiefer ruhiger Puls, einzelne warme Obertöne | erster Schritt fast ohne Musik |
| S2 | 0,72 | Küstenluft, Holz, leises Bandrauschen, offene harmonische Fläche | Karte/Fogo öffnet den Raum |
| S3 | 0,60 | klarer Grundton, kleine technische Impulse, keine Sci-Fi-Sprache | unter REM-Karten stark ausdünnen |
| S4 | 0,72 | drei unaufdringliche Tonfarben für die drei Familien | keine leitmotivische Monsterzuordnung |
| S5 | 0,84 | Laborraum, Uhr, trockene elektrische Textur | bei „sechs Episoden“ Musik kurz freigeben |
| S6 | 0,88 | intimer Raumton, tiefe Luft, dann Stille unter CTA | CTA vollständig ohne Bewegung, Musik sehr klein |
| S7 | 1,00 | stärkste harmonische Spannung, aber ohne Horror-Drohne | ab „Ein Rest bleibt“ langsam öffnen |
| S8 | 0,66 | warme Auflösung mit kühl bleibender Restnote | EP07-Handoff trockener, Endcard 20 s ausfaden |

## Zu erzeugende Stems

| Dateiname | Inhalt | Einsatzregel |
|---|---|---|
| `EP06_MX_LOW.wav` | Grundton und sehr langsame harmonische Bewegung | durchgehend, aktweise automatisiert |
| `EP06_MX_HARMONIC.wav` | hörbare obere Textur 700–2600 Hz | sparsam, auf Telefon hörbar |
| `EP06_MX_NOISE.wav` | feiner Raum-/Luftanteil | nicht als Rauschteppich wahrnehmbar |
| `EP06_ATMO_DORM_1963.wav` | ruhiger Innenraum, entfernte Heizung, Winterluft | nur S1 |
| `EP06_SFX_WINTER_WINDOW_AIR.wav` | kaum hörbare kalte Fenster-/Außenluft | einmal im zweiten Hook-Shot |
| `EP06_ATMO_FOGO_COAST.wav` | Wind an Holz/Küste, sehr zurückhaltend | S2 und Rückkehr in S8 |
| `EP06_ATMO_SLEEP_LAB.wav` | Lüftung, Kabel, leises Gerät | S5, ohne Krankenhausalarm |
| `EP06_SFX_DOOR_LATCH_SOFT.wav` | ein glaubwürdiges Türgeräusch | einmal S1 |
| `EP06_SFX_FOOTSTEPS_DISTANT_2.wav` | exakt zwei trockene Schritte | S1 und Zuschauerexperiment S6; verschiedene Mischperspektive |
| `EP06_SFX_FOOTSTEP_SINGLE_NEAR.wav` | einzelner näherer Schritt | S1, sehr leise |
| `EP06_SFX_MATTRESS_WEIGHT_SOFT.wav` | Stoff und ein kurzes Nachgeben | nur S1, kein Jump-Scare |
| `EP06_SFX_BREATH_BODY_LOW.wav` | neutrale Atem-/Körpertextur | S3/S4/S7, niemals Erstickung spielen |
| `EP06_SFX_EEG_TICK_SUBTLE.wav` | kleine technische Ticks | nur echte/erklärende Messbilder |
| `EP06_SFX_CLOCK_TICK_SOFT.wav` | einzelne Uhrimpulse | Takeuchi-Protokoll, nicht durchgehend |
| `EP06_SFX_CABLE_TOUCH_SOFT.wav` | Sensor-/Kabelmaterial | S5-Makros |
| `EP06_SFX_TAPE_RECORDER.wav` | Klick und sehr leises Bandrauschen | S2 Oral History; kein Markenklang |
| `EP06_SFX_FLOOR_CREAK_SINGLE.wav` | ein neutrales Holzknacken | S6/S7; nie zusätzlich eine Gestalt hörbar machen |
| `EP06_SFX_CURTAIN_RUSTLE_SOFT.wav` | kurzer Stoffzug | nur bei sichtbarem Vorhang |
| `EP06_SFX_PAPER_QUILL_SOFT.wav` | Papier, Feder, kein Gerichtsgemurmel im Vordergrund | S8 Handoff |

## Synchronisationsregel

Jeder konkrete Einsatz steht bereits in `sync/EP06_VOICE_VISUAL_SYNC.csv` in den Spalten `sfx_cue` und `music_atmo`. Die dortigen Zeitangaben sind Planwerte. Nach der George-Generierung werden ausschließlich die Textanker durch Forced Alignment ersetzt; Reihenfolge, Asset-ID, Bewegungsregel und SFX-Bedeutung bleiben stabil.

## Stille als Gestaltung

- Nach „kein Ton“: Musik und Raum für etwa 0,4 s deutlich absenken, keine komplette digitale Stille.
- Vor `CARD006_CTA_KOERPER_BESUCHER.png`: SFX beenden; Karte mindestens 4,5 s statisch tragen lassen.
- Nach „sechs dokumentierte Episoden“: kurzer Raum von ungefähr 0,3 s, dann Messbild.
- Vor dem letzten Satz über öffentliche Wahrheit: Musik zurücknehmen, Papierklang trocken lassen.
- Endcard: kein SFX, nur harmonische Auflösung über exakt 20 s.
