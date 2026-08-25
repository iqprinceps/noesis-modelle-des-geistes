# EP06 — Fehlende Originalassets, Zusatzbilder und Karten

**Status:** Produktionsliste, noch nichts kostenpflichtig generiert  
**Ziel:** Die 152 geplanten Einsätze aus `sync/EP06_VOICE_VISUAL_SYNC.csv` mit 133 unterschiedlichen Motiven abdecken, 25–35 Prozent Original-/Quellenlaufzeit erreichen und Wiederholungs-Slots unter 15 Prozent halten.  
**Namensregel:** Neue Produktionsbilder heißen ausschließlich `IMGxxx_...png`, Karten `CARDxxx_...png`, Originalquellen `ORIGxxx_...`; kein Dateiname beginnt mit `EP06`.

## Globale Bildregeln

- 16:9, 2560×1440, sRGB, klare Mitteltonzeichnung; nichts darf im Schwarz absaufen.
- Ruhige NOESIS-Palette: Nachtblau, warmes Lampenlicht, Papier, entsättigte Küstenfarben; kein Cyberpunk-Neon.
- Keine Schrift, Logos, Wasserzeichen oder erfundene Messkurven in generierten Bildern.
- Keine generische Geisterfigur, kein Monster, kein dämonisches Gesicht.
- Rekonstruktionen werden im Schnitt als `Rekonstruktion` gekennzeichnet.
- Wissenschaftliche Bilder sind anschauliche Metaphern, keine angeblichen Aufnahmen des Takeuchi-Versuchs.
- Betten nur, wenn der konkrete Textanker sie wirklich benötigt. Unter den zwölf Ergänzungen ist kein weiteres Bettmotiv vorgesehen.

## A. Noch zu beschaffende Originalassets

| ID / Zieldatei | Quelle / Suchziel | Rechte-Ampel | Verwendung | Produktionsregel |
|---|---|---|---|---|
| `ORIG017_BRAINSTEM_ANATOMY.png` | Blausen Medical: Brainstem Anatomy, Wikimedia Commons | YELLOW · CC BY 3.0 | S3 REM-Atonie | Attribution; vollständig einpassen, statisch |
| `ORIG018_SLEEP_CYCLE_HYPNOGRAM.svg` | `Hypro_zyklus_1_en_103.svg`, Wikimedia Commons | YELLOW · CC BY-SA 3.0 | S2/S4 Schlafphasen | Lizenz-/Share-Alike-Prüfung; deutsche Beschriftung separat im Edit |
| `ORIG019_CIRCADIAN_RHYTHM_NIH.jpg` | `Circadian_rhythm_labeled.jpg`, NIH / Wikimedia Commons | GREEN · Public Domain | S2/S4 Rhythmuskontext | Originalbeschriftung nicht verfälschen |
| `ORIG020_EEG_62_CHANNEL_CC0.svg` | `EEG_time_series_62_channels.svg`, Wikimedia Commons | GREEN · CC0 | S4 Forschungs-/Datenanker | statisch; keine Behauptung, es seien Cheyne-Daten |
| `ORIG021_AMYGDALA_ANIMATION.gif` | `Amygdala_small.gif`, Wikimedia Commons | YELLOW · CC BY-SA 2.1 JP | S4/S7 Alarmsystem-Kontext | nur als Anatomiekontext; keine monokausale Erklärung |
| `ORIG022_OBE_ICON.svg` | `Noun-Out_Of_Body_Experience_197585.svg`, Wikimedia Commons | YELLOW · CC BY 4.0 | S4 ungewöhnliche Körpererfahrung | Attribution; neutral, nicht esoterisch labeln |
| `ORIG023_SLEEP_DEPRIVATION.svg` | `Effects_of_sleep_deprivation.svg`, Wikimedia Commons | GREEN · CC0 | S2/S4 gestörter Schlaf | nur ausschnittsweise, falls bei 1080p lesbar |
| `ORIG024_1960S_DORM_CONTEXT.jpg` | Library of Congress / US-Universitätsarchiv: frei lizenziertes Dorm-/College-Zimmer um 1963 | OFFEN | S1 zeitlicher Kontext | kein Bild als Huffords echtes Zimmer ausgeben; Jahr/Archiv nennen |
| `ORIG025_ORAL_HISTORY_RECORDER.jpg` | Smithsonian Open Access / Library of Congress: tragbarer Tonbandrecorder oder Oral-History-Interviewgerät 1960er–1980er | OFFEN | S2 Feldforschung | CC0/PD bevorzugen; kein konkretes Gerät Hufford zuschreiben |
| `ORIG026_SALEM_COURT_1876.jpg` | `Witchcraft_at_Salem_Village.jpg`, Wikimedia Commons | GREEN · Public Domain | S8 EP07-Handoff | als spätere Darstellung von 1876 kennzeichnen |
| `ORIG027_BRIDGET_BISHOP_RECORD.jpg` | Salem Witch Trials Documentary Archive / Essex County Court Papers: verifizierter Bridget-Bishop-Dokumentscan | OFFEN | S8 Name / Gerichtsakte | nur Originalscan mit geklärter Public-Domain-Provenienz; kein nachgebauter Text |

### Bereits vorhandene Originale, die im Schnitt stärker eingesetzt werden

Der Sync-Plan nutzt sechzehn bestehende Quellen direkt: Fogo-Foto, Admiralty Chart von 1873, Fogo-District-Map, REM-/Stage-1-/Stage-2-/Slow-Wave-PSG, Schlafphasenbild, NHLBI-Schlafstudienbild, PSG-Trace, Tester, Sensoranschlüsse, Modell, ausgerüstete Versuchsperson, 64-Kanal-Kappe und EEG-Icon. Die YELLOW-Dateien bleiben bis zum Lizenz-/Attributionscheck gesperrt.

## B. Bildgenerierungs-Batch — dreizehn fehlende Stills

Jeder Prompt ist eigenständig. Referenzen: `STYLE_CINEMATIC_EP06.png` für Rekonstruktionen, `STYLE_CONCEPTUAL_EP06.png` für subjektive Wahrnehmung und `STYLE_SCIENCE_EP06.png` für Körper-/Laborbilder. Referenzen dienen nur der Bildsprache; ihr Inhalt darf nicht kopiert werden.

### `IMG033_HUFFORD_1963_STUDENT_RECON.png`

Create a cinematic editorial reconstruction in 16:9, 2560x1440. December 1963, a young male college student seen only from behind at a modest wooden desk in a believable North American dorm room, late-night winter atmosphere, period-correct lamp, notebook and plain clothing, open dark doorway in the far background, the person is not a portrait and must not resemble a known individual. Quiet documentary realism, warm lamp against readable blue-grey shadows, clear facial anonymity, natural materials, restrained grain. No bed as the main subject, no ghost, no supernatural figure, no text, no logo, no neon, no crushed blacks.

### `IMG034_DOOR_HANDLE_NO_RESPONSE.png`

Create a 16:9 cinematic close visual, 2560x1440. A human hand in the foreground trying to reach a slightly turning 1960s brass door handle but stopping several centimetres short, the gesture conveys intention without movement, shallow depth of field, old painted door, warm practical light and cool corridor beyond. The source of movement remains unseen. Documentary tactile realism, readable midtones. No bed, no person at the doorway, no ghost, no horror makeup, no text, no logo, no neon, no black void.

### `IMG035_VOICE_WITHOUT_SOUND.png`

Create a bright-readable conceptual 16:9 image, 2560x1440, expressing an attempted shout that produces no sound. Side profile silhouette of an anonymous human head and throat built from subtle translucent anatomical layers; a small warm impulse begins at the mouth but dissolves immediately into still air, while the surrounding room remains calm and real. Scientific-poetic, elegant, non-grotesque, no visible suffering, no glowing skin, no supernatural entity, no text, no symbols, no watermark, preserve shadow detail.

### `IMG036_HUFFORD_FIELD_NOTES.png`

Create a documentary reconstruction in 16:9, 2560x1440. Overhead fieldwork table in Newfoundland: blank notebook pages with handwritten-looking lines too soft to read, pencils, index cards, unbranded cassette recorder, knitted textile edge and a small coastal photograph without identifying faces. The arrangement suggests comparing multiple oral-history accounts without inventing quotations. Warm daylight, archival tactility, high detail, quiet human presence through hands only. No readable text, no book-cover imitation, no occult props, no logos, no neon.

### `IMG037_CULTURE_EXPERIENCE_FORK.png`

Create an elegant conceptual editorial image in 16:9, 2560x1440. One central nocturnal human experience represented as a simple warm pressure-and-threshold motif, splitting into two different visual paths: on one side woven cultural story layers and recorded testimony objects; on the other side a restrained REM timing and motor-signal structure. The paths remain connected and neither is presented as the winner. Bright readable navy, paper, amber and pale blue, subtle depth, no labels or words, no demon, no bed, no pseudo-scientific UI, no neon.

### `IMG038_BREATH_INTEROCEPTION.png`

Create a scientifically informed conceptual torso study in 16:9, 2560x1440. Anonymous upper torso seen from the front, subtle translucent ribcage and diaphragm plane, soft pressure waves converging around the sternum while a clear open airflow path remains visible. The image communicates altered perception of breathing, not literal suffocation. Calm medical-editorial aesthetic, warm anatomical highlights on readable blue-grey background, no glowing skin, no pain pose, no straps, no text, no logo, no neon, no black background.

### `IMG039_CLUSTER_OBJECT_STUDY.png`

Create a museum-like still life in 16:9, 2560x1440, showing three distinct clusters made from ordinary objects and light. Cluster one: doorway, coat and listening shadow cues. Cluster two: folded blanket, weight and compressed fabric. Cluster three: suspended chair, tilted frame and weightless paper. The triptych should visually suggest presence, pressure and vestibular displacement without written labels. Bright readable gallery lighting, navy and warm amber, no bedroom, no human figure, no monster, no text, no infographic icons.

### `IMG040_INTERRUPTION_PROTOCOL_OBJECTS.png`

Create a historically neutral sleep-research protocol still life in 16:9, 2560x1440. Analog clock, blank clipboard, six small removable markers, sensor leads, unbranded tape machine, observation window and a neatly folded blanket on a chair; show the sequence sleep, wake interval, return through object placement only, without readable labels. Early-1990s laboratory materiality, realistic practical lighting, clearly readable midtones. No patient bed, no fake graph, no text, no logo, no futuristic equipment, no neon.

### `IMG041_SIX_EPISODES_MARKERS.png`

Create a minimal evidence-focused editorial still in 16:9, 2560x1440. Six clearly separated warm markers on a dark-blue laboratory table, each paired with a unique short paper strip and sensor contact, surrounded by empty space that implies a small number of observed episodes within a larger experiment. Exact count of six must be visually unmistakable. No numerals, no words, no fake data, no patient, no bed, no decorative particles, no neon, crisp readable lighting.

### `IMG042_AGENT_DETECTION_LAYERS.png`

Create a deep but clear conceptual image in 16:9, 2560x1440. Ordinary sensory fragments—one floorboard seam, curtain edge, chair back and door shadow—are shown as separate translucent perception layers converging toward the suggestion of a shoulder-shaped contour, yet no complete person appears. The visual explains how ambiguous cues can acquire agency. Museum-grade composition, warm daylight geometry against cool shadow, bright enough for mobile viewing. No bed, no ghost, no face, no text, no neural-network cliché, no neon.

### `IMG043_PRESENCE_BEFORE_IMAGE.png`

Create a mystical yet non-supernatural 16:9 visual, 2560x1440. A large bright architectural corridor with soft fabric planes and empty central space; multiple sightlines and subtle pressure ripples point toward a location that remains visibly empty. The composition must make the viewer feel watched before any figure exists. Clean spatial surrealism, pale dawn blue, warm threshold light, fine texture and fully visible shadow detail. No bed, no humanoid silhouette, no eyes, no monster, no text, no black void.

### `IMG044_BRIDGET_TESTIMONY_HANDOFF.png`

Create a restrained historical reconstruction in 16:9, 2560x1440. A seventeenth-century wooden court table, anonymous male witness hand resting tensely beside a blank deposition sheet, quill and sealed folded paper; in the far background a softly lit courtroom doorway, no identifiable judge or accused person. The image bridges a private bodily experience into public testimony without fabricating document text. Natural window light, warm paper, readable shadows. No readable writing, no witch iconography, no bedroom, no spectacle, no text overlay, no logo.

### `IMG045_DECEMBER_WINDOW_CONTEXT.png`

Create a quiet documentary insert in 16:9, 2560x1440. Frosted college-room window at night in December 1963, restrained winter condensation, a period radiator edge and the reflection of a plain desk lamp, with no readable calendar, no person and no bed. The image must establish cold season, late hour and ordinary reality within 2.5 seconds. Natural 1960s material detail, warm amber reflection against readable blue-grey night, no ghost, no silhouette, no text, no logo, no neon, no crushed blacks.

## C. Sieben zusätzliche Karten — deterministisch setzen

Diese Karten werden nicht mit KI-Schrift erzeugt. Sie werden mit derselben typografischen Vorlage wie `CARD001` bis `CARD007` gebaut und bleiben im Schnitt vollständig statisch.

### `CARD008_HUFFORD_1963_1982.png`

- Headline: `EINE NACHT WIRD ZUR FORSCHUNGSFRAGE`
- Hauptachse: `1963` → `1982`
- Unterzeile links: `eigenes Erlebnis`
- Unterzeile rechts: `The Terror That Comes in the Night`
- Quellzeile: `David J. Hufford · autobiografischer Bericht / Buchpublikation`
- Keine Buchcover-Reproduktion.

### `CARD009_WAKE_REM_OVERLAP.png`

- Headline: `WACHHEIT KOMMT ZURÜCK`
- Zwei ruhige horizontale Ebenen: `BEWUSSTSEIN: WACH` und `MUSKELTONUS: NOCH GEHEMMT`
- Abschlusszeile: `Mischzustand · Sekunden bis Minuten`
- Quellzeile: `Erklärgrafik · REM-Atonie`

### `CARD010_TAKEUCHI_PROTOCOL.png`

- Headline: `SCHLAF · EINE STUNDE WACH · ZURÜCK INS BETT`
- Drei große, sofort lesbare Felder; keine kleinteilige Methodengrafik.
- Unterzeile: `Schlafbeginn und REM werden gegeneinander verschoben`
- Quellzeile: `Takeuchi et al. · SLEEP 15(3) · 1992`
- Nicht als Garantie eines Anfalls formulieren.

### `CARD011_SIX_EPISODES.png`

- Headline: `SECHS DOKUMENTIERTE EPISODEN`
- Sechs große Punkte, darunter klein: `isolierte Schlafparalyse`
- Zusatz: `bei experimenteller Schlafunterbrechung`
- Quellzeile: `Takeuchi et al. · 1992`
- Das Wort `nur` vermeiden; Ergebnis weder aufblasen noch kleinreden.

### `CARD012_REALNESS_AND_CAUSE.png`

- Headline: `REAL ERLEBT ≠ URSACHE GEKLÄRT`
- Zwei gleichwertige Elemente: `ERLEBNIS` und `ERKLÄRUNG`
- Unterzeile: `Messbarkeit nimmt dem Erlebnis nicht seine Wucht`
- Quellzeile: `Redaktionelle Einordnung · keine Ursachenbehauptung`

### `CARD013_OPEN_PRESENCE_QUESTION.png`

- Headline: `WARUM WIRD AUS LÄHMUNG EINE BEGEGNUNG?`
- Höchstens zwei visuelle Elemente: Körperkontur und leerer Schwellenraum.
- Unterzeile: `Die Lähmung ist erklärbar · die erlebte Präsenz bleibt eine Forschungsfrage`
- Quellzeile: `Schlafparalyse · Wahrnehmung und Präsenz`

### `CARD014_PRIVATE_NIGHT_PUBLIC_RECORD.png`

- Headline: `PRIVATE NACHT → ÖFFENTLICHE AUSSAGE`
- Zwei Felder: `ERLEBNIS` und `GERICHTSAKTE`
- Unterzeile: `Salem · 1692`
- Quellzeile: `Bridget-Bishop-Handoff · EP07`
- Keine Hexensilhouette, kein Scheiterhaufen, kein Sensationsmotiv.

## D. Sechs zusätzliche Transformationsclips

Alle Clips: 1920×1080, 16:9, 24 fps, 6 Sekunden, ohne Audio. Die Kamera bleibt ruhig. Motion muss Gegenstand, Zustand oder Bedeutung verändern; bloßer Push, Parallax oder Ken Burns ist unzulässig.

### `CLIP005_MOTOR_FREEZE.mp4`

Start from a new companion of `IMG003_HAND_WILL_NOT_MOVE.png`. A warm motor impulse travels through the forearm toward the fingers, meets a translucent inhibition boundary and disperses; the room remains ordinary and the hand visibly stays still. Fixed camera, readable anatomy metaphor, no pain, no supernatural force, no glowing skin, no text.

### `CLIP006_THREE_FAMILIES.mp4`

Three ordinary object environments transform sequentially without camera movement: doorway cues organize into an implied presence, compressed fabric expresses chest pressure, then furniture loses stable orientation to express vestibular displacement. Each state fully replaces the previous one. No monster, no literal attack, no labels, no bed montage, no camera drift.

### `CLIP007_INTERRUPTION_CYCLE.mp4`

On a fixed early-1990s laboratory table, an analog clock advances, a blank protocol marker moves from sleep position to one-hour wake interval and then back beside prepared sensors. The objects themselves execute the sequence; no readable text, no patient, no fake chart, no futuristic interface, no camera motion.

### `CLIP008_SIX_EPISODES_SIGNAL.mp4`

Fixed evidence table. Six distinct warm markers appear one by one in response to six short measurement pulses, then the surrounding unused positions remain dark and empty. Exact final count six, no numerals, no text, no celebratory effect, no particles, no camera movement.

### `CLIP009_REALNESS_CAUSE_SPLIT.mp4`

One vivid subjective pressure-and-presence form separates into two synchronized layers: a measurable REM/motor-timing structure and an unresolved empty threshold. Both remain visible without one cancelling the other. Fixed camera, conceptual but readable, no soul claim, no external entity claim, no text, no neon.

### `CLIP010_SHADOW_COMPLETION.mp4`

Fixed daylight interior with chair, curtain and door edge. Their real shadows slowly align into the suggestion of a shoulder, hold briefly, then separate again into ordinary object shadows. No person enters, no monster, no black apparition, no camera movement, preserve bright midtones.

## E. Semantische Ersatzshots für Wiederholungen

`SEMANTIC_DERIVATIVE_BATCH.md` enthält 29 zusätzliche, automatisch durchnummerierte Produktionsdateien `SHOT09` bis `SHOT37`. Sie ersetzen wiederholte Frames und sind im Sync bereits an konkrete Textanker gebunden.

- Original-Derivate: verifizierter Full-/Passage-/Detail-Crop, keine Inhaltsänderung.
- Generierte Derivate: neue Komposition und neue Informationshierarchie; kein bloßer Crop oder Kamera-Variant.
- Ergebnis im Plan: 20 Wiederholungs-Slots bei 139 Nicht-Karten-Slots = 14,39 Prozent.
- Jedes Basisasset erscheint höchstens zweimal; jede konkrete Karte und jeder Clip genau einmal.

## F. Ausführungsreihenfolge

1. Originale `ORIG017` bis `ORIG027` herunterladen bzw. Rechte prüfen.
2. Karten `CARD008` bis `CARD014` deterministisch erstellen.
3. Stills `IMG033` bis `IMG045` als einen kontrollierten 2K-Batch erzeugen.
4. Die 29 Ersatzshots aus `SEMANTIC_DERIVATIVE_BATCH.md` erstellen.
5. Clips `CLIP005` bis `CLIP010` erzeugen und auf echte Zustandsänderung prüfen.
6. Kontaktbogen erstellen und auf Helligkeit, Hände, Zählfehler bei `IMG041` sowie ungewollte Schrift prüfen.
7. Erst nach bestandenem Asset-QA Voice generieren; die geschätzten Zeiten werden anschließend durch Forced Alignment ersetzt.
