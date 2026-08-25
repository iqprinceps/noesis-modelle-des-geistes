# EP07 - finale Bild- und Clip-QA nach Diversity-Redesign

## Ergebnis

- 20 MAIN-Bilder: freigegeben
- 4 RESERVE-Shots: freigegeben
- 12 gezielt ersetzte Motive ohne Bett/Schlafzimmer: freigegeben
- 4 transformative Veo-Clips: freigegeben
- Fehlende Motive: 0
- Nicht freigegebene Varianten im finalen Ordner: 0

## Visuelle Vielfalt

- Bett/Schlafzimmer als Hauptmotiv: **6 von 24** statischen Motiven, Zielwert eingehalten.
- Ohne Bett/Schlafzimmer: **18 von 24** Motiven.
- Die zwölf Ersatzbilder arbeiten mit Archivräumen, Schwellen, Ritualobjekten, Papierreliefs, Körperabdrücken, Oral History, kulturellen Bildträgern, Wahrnehmungsmodellen und negativem Raum.
- Helligkeitslock: mystisch und kontrastreich, aber mit angehobenen Mitteltönen; kein Motiv verlässt sich auf großflächig zugelaufene Schatten.

## Bildtechnik

- Generator: Vertex AI NanoBanana Pro, Modell `gemini-3-pro-image`
- Format: PNG, RGB, 2752 x 1536, horizontal 16:9
- Benennung: ausschließlich `IMG001...IMG020` und `SHOT01...SHOT04`
- Helligkeit: Schatten und Mitteltöne auf normale Laptop- und Smartphone-Wiedergabe geprüft; das dunkelste Salem-Motiv erhielt einen nicht-destruktiven Mittenton-Lift.
- Sichtprüfung: Motivtreue, zeitlicher Kontext, Raumgeometrie, Anatomie, Doppelungen, Textartefakte und Wasserzeichen.

## Quellenintegrität

Bei KI-generierten Dokumentarcomposites darf ein historisches Objekt nicht neu gezeichnet werden. Deshalb wurden folgende finale Frames nach dem Vertex-Layout mit den unveränderten Originalquellen bestückt:

- `IMG003_PRIVATE_NIGHT_TO_COURT.png`: echter Richard-Coman-Scan
- `IMG005_NIGHTMARE_MOTIF_ROOM_BASE.png`: echtes Fuseli-Bild
- `IMG008_BURNEY_RELIEF_SOURCE_ROOM.png`: echtes Burney-Relief-Foto
- `IMG019_SALEM_LOOP_RETURN.png`: echter Coman-Scan plus echte Bridget-Bishop-Lithografie
- `SHOT04_FUSELI_TO_SCREEN_TRANSITION.png`: echtes Fuseli-Bild

Die Quellen wurden nur proportional skaliert und als klar getrennte fotografische Objekte eingesetzt. Innerhalb der Quellen wurde nichts ergänzt oder umgeschrieben.

## Textbereinigung

- `IMG020_MEDIA_SPEED_HANDOFF.png`: generierte Bildschirmbeschriftungen unlesbar neutralisiert; Fenstergeometrie und früher Computer bleiben erhalten.
- `SHOT03_CASSETTE_NOTEBOOK_MACRO.png`: Fantasiehandschrift in den ausdrücklich unlesbaren Bereich zurückgeführt.
- `SHOT04_FUSELI_TO_SCREEN_TRANSITION.png`: Monitorinhalt textfrei neutralisiert.

## Veo-QA

- Generator: Vertex AI `veo-3.1-generate-001`
- Ausgabe: MP4/H.264, 1920 x 1080, 24 fps, 6.0 Sekunden
- Audio: deaktiviert; kein Audiostream vorhanden
- Prüfmethode: Anfangs-, Mittel- und Endframe jedes Clips visuell geprüft
- Bewegungslock: keine reine Dolly-, Zoom- oder Ken-Burns-Fahrt im finalen Vierer-Set.
- `CLIP001_CULTURAL_MASKS.mp4`: kulturelle Ebenen ordnen sich zu wechselnden Schwellen-/Maskenformen; keine historische Quellenbehauptung.
- `CLIP002_NIGHTMARE_PRESSURE.mp4`: Druck verformt Relief, Rippen- und Handabdruck als subjektive Materialvisualisierung.
- `CLIP003_SALEM_PUBLIC_TRANSFORMATION.mp4`: echte Coman-Seite und Salem-Darstellung bleiben orts- und bildstabil; ausschließlich die konstruierten Publikumsschatten bewegen sich.
- `CLIP004_FEEDBACK_ENTITY.mp4`: der Angst-Schlaf-Kreislauf bildet eine vorübergehende negative Raumform und löst sie wieder auf.
- Abgewiesene ruhige bzw. quelleninstabile Fassungen liegen ausschließlich in `RESERVE_CLIPS` und gehören nicht zum Hauptsatz.

Die empfohlene Reihenfolge und Einsatzposition aller Dateien steht in `EP07_SHOTLIST.csv`. Die vollständigen Video-Prompts und Startframe-Zuordnungen stehen in `VEO_CLIP_LOG.md`.
