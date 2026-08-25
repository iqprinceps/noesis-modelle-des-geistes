# EP08 — Production QA und Übergabe

**Status:** DELIVERY READY  
**Bilder:** 32 MAIN + 8 SHOT  
**Karten:** 8 redaktionelle Karten inkl. CTA und Endcard  
**Motion:** 4 kuratierte transformative Veo-Hauptclips  
**Namensstandard:** kein `EP08_`-Präfix; nur `IMGxxx`, `SHOTxx`, `CARDxxx` und `CLIPxxx`

## Technische Abnahme

- Exakt 40 Core-Stills im Nutzordner: 32 `IMGxxx` + 8 `SHOTxx`.
- Alle 40 PNG-Endfassungen: 2560 × 1440, 16:9; keine exakten Dateiduplikate.
- Alle acht Karten: 2560 × 1440, 16:9.
- Exakt vier MP4-Hauptfassungen: H.264, 1920 × 1080, 24 fps, 6,0 Sekunden.
- Keine Audiospur in den Clips; Voice-over und Sounddesign bleiben vollständig frei.
- Keine Zwischenversionen, `QA_V…`- oder `GRADE_V…`-Dateien im Nutzordner.
- Schlafzimmer-/Bettmotive sind auf 10 von 40 Core-Stills begrenzt. Das übrige Bildsystem arbeitet mit Radio, Archiv, Wahrnehmungslabor, Interview, Erinnerung, Mediennetzwerk, Museumstypologie und abstrakten Kausalmodellen.

## Produktionsweg

Der korrekt authentifizierte Vertex-Aufruf von NanoBanana Pro (`gemini-3-pro-image`, global, 2K/16:9) erreichte den Dienst, wurde durch die Bildmodell-Projektquote jedoch wiederholt mit `429 RESOURCE_EXHAUSTED` abgewiesen. Die Stills wurden deshalb mit dem freigegebenen built-in ImageGen-Fallback erzeugt, visuell abgenommen und als 2K-Lieferdateien normalisiert.

Die Videoquote war verfügbar. Die Motion-Shots wurden über Vertex AI mit `veo-3.1-generate-001` als Image-to-Video erzeugt.

## Inhaltliche QA

Geprüft wurden Motivtreue, zeitlich passende Technik, 16:9-Komposition, Helligkeit, Anatomie, Hände, doppelte Körperteile, Figurenanzahl, lesbare Fantasietexte, Logos, Wasserzeichen und unerwünschte übernatürliche Behauptungen.

Besondere Korrekturen:

- `IMG004_SHADOW_PERIPHERAL_GLIMPSE.png`: fehlendes peripheres Motiv ersetzt; jetzt klar angeschnittener, weiterhin plausibel mehrdeutiger Rand-Schatten.
- `IMG017_HAT_MAN_FOOT_OF_BED.png` und `IMG018_HAT_BRIM_MINIMAL.png`: Hat-Brim-/Silhouettenmotiv erhalten, Mitteltöne geöffnet.
- `IMG003`, `IMG004`, `IMG008`, `IMG011`, `IMG025` und `IMG032`: konservativer Schatten-/Mitteltöne-Lift ohne Motiv- oder Geometrieänderung.
- Art Bell wurde ausschließlich im rekonstruierten `IMG001` mithilfe der bereitgestellten CC0-Identitätsreferenz dargestellt. Es wurden keine Coast-to-Coast-Logos oder behaupteten Original-Broadcastbilder erzeugt.

## Veo-Hauptclips — kuratierter Transformationssatz

Alle acht neuen Transformationskandidaten wurden an Anfang, Mitte und Ende geprüft. Die vier visuell und erzählerisch stärksten Clips liegen im Nutzordner; alle übrigen Varianten liegen in `RESERVE_CLIPS` und sind nicht Teil des primären Schnittplans. Reine Ken-Burns-/Dolly-Varianten sind ebenfalls nur Reserve.

### CLIP001_RADIO_NETWORK_ENTITY.mp4

- Startframe: `IMG002_4500_MESSAGES_MATERIAL.png`
- Einsatz: S1–S2, Übertragung vom Radiosignal in eine kollektive Wesenform
- Bewegung: Radiowellen wandern durch Papierstapel und CRT-Flächen; Schattenfragmente konvergieren kurz zu einer mehrdeutigen Form und zerfallen wieder.
- QA: deutliche Binnenbewegung und Transformation statt bloßer Kamerafahrt; keine reale Person, kein Logo und keine lesbare Schrift.

### CLIP002_SHADOW_DETACHES.mp4

- Startframe: `SHOT05_HAT_SHADOW_EMPTY_ROOM.png`
- Einsatz: S3–S4, subjektive Rekonstruktion einer verselbständigten Schattenwahrnehmung
- Bewegung: Der Gegenstandsschatten löst sich sichtbar gegen die Lichtlogik, durchquert die Wandfläche und fällt anschließend auf seine Quelle zurück.
- QA: klarer Bewegungsbogen mit Anfang und Rückkehr; kein Wesen wird als objektiv real behauptet, keine Anatomie- oder Geometriemutation.

### CLIP003_MEMORY_RECONSTRUCTION.mp4

- Startframe: `IMG014_MEMORY_RECONSTRUCTION_LAYERS.png`
- Einsatz: S3–S4, Gedächtnis als aktive Rekonstruktion
- Bewegung: Raum-, Körper- und Schattenfragmente ordnen sich neu; die Hutkante entsteht erst in der Überlagerung und verschwindet wieder.
- QA: Gesicht und Körper bleiben anatomisch stabil; die Transformation findet nachvollziehbar in den Erinnerungsebenen statt.

### CLIP004_COLLECTIVE_IMAGE_LOOP.mp4

- Startframe: `IMG020_HAT_MAN_REPORT_VARIATIONS.png`
- Einsatz: S5–S8, kulturelle Rückkopplung vom Einzelbericht zum geteilten Bild
- Bewegung: Unterschiedliche Zeichnungen verdichten sich zu einer gemeinsamen Hat-Man-Negativform und zerstreuen sich anschließend wieder als unabhängige Berichte.
- QA: starke Motivtransformation, verständlicher visueller Loop, keine lesbare Schrift und keine behauptete übernatürliche Materialisierung.

## Nächster Produktionsschritt

Die Bild-, Karten- und Motion-Basis ist vollständig. Für die Voice-Produktion kann `EP08_SHOTLIST.csv` als Reihenfolge verwendet werden; die acht Karten sind dort mit konkreten Einfügepunkten integriert. Die endgültigen Bildhaltezeiten werden danach an Sprecherpausen, Satzakzente und Belegstellen angepasst. `VEO_CLIP_LOG.md` dokumentiert die vier freigegebenen Hauptclips und die Reserveabgrenzung.
