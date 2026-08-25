# EP06 — Originalasset- und Wiederholungs-Audit

**Status:** Planung vor Voice-/Bildgenerierung  
**Hauptschnitt:** 152 visuelle Einsätze + 1 statische 20-s-Endcard  
**Geschätztes Voice-Ende:** `00:10:43.750`  
**Geschätztes Videoende inkl. Endcard:** `00:11:04.550`

## Gates

- Einmalige Motive im geplanten Schnitt: **133**.
- Davon aktuelle/noch zu beschaffende Originalassets: **27**.
- Bereits produktionsbereite eindeutige Assets: **67**.
- Noch zu erstellende oder zu lizenzierende eindeutige Assets: **66**.
- Wiederholung desselben Assets innerhalb eines Akts: **0** (hart validiert).
- Wiederholungs-Slots ohne Karten/Endcard: **20/139 = 14.39%** (Limit 15%).
- Höchste Verwendung eines Basisassets: **2×** (Lock: normalerweise höchstens 2×).
- Semantische Ersatzshots für frühere Wiederholungen: **29** (`SHOT09` ff.).
- Karten: immer `STATIC_NO_ZOOM_NO_PAN`.
- Originaldokumente/-karten: `CONTAIN`, kein Beschnitt, vollständig statisch. Andere Quellen bleiben ebenfalls statisch oder erhalten ausnahmsweise weniger als 1 Prozent Bewegung.
- Generierte Stills: ruhiger Push bis maximal 1,025 oder statischer Hold.
- Veo-Clips: native Bewegung, kein Retiming und keine zusätzliche Kamerafahrt.

## Klassen im Schnitt

| Klasse | Einsätze |
|---|---:|
| CARD | 7 |
| GENERATED_STILL | 54 |
| ORIGINAL_ASSET | 19 |
| PLANNED_CARD | 7 |
| PLANNED_EDITORIAL_DERIVATIVE | 13 |
| PLANNED_GENERATED_DERIVATIVE | 16 |
| PLANNED_GENERATED_STILL | 16 |
| PLANNED_ORIGINAL_ASSET | 11 |
| PLANNED_TRANSFORM_CLIP | 6 |
| VEO_CLIP | 4 |

## Wiederholte Assets

| Asset | Einsätze |
|---|---:|
| `IMG002` | 2 |
| `IMG003` | 2 |
| `IMG005` | 2 |
| `IMG007` | 2 |
| `IMG009` | 2 |
| `IMG011` | 2 |
| `IMG013` | 2 |
| `IMG014` | 2 |
| `IMG016` | 2 |
| `IMG024` | 2 |
| `IMG026` | 2 |
| `IMG028` | 2 |
| `IMG030` | 2 |
| `IMG031` | 2 |
| `IMG037` | 2 |
| `IMG038` | 2 |
| `IMG043` | 2 |
| `ORIG_FOGO_VILLAGE` | 2 |
| `ORIG_REM_PSG` | 2 |
| `ORIG_SENSOR_CONNECTIONS` | 2 |

## Noch fehlende IDs

- `CARD008`
- `CARD009`
- `CARD010`
- `CARD011`
- `CARD012`
- `CARD013`
- `CARD014`
- `CLIP005`
- `CLIP006`
- `CLIP007`
- `CLIP008`
- `CLIP009`
- `CLIP010`
- `IMG033`
- `IMG034`
- `IMG035`
- `IMG036`
- `IMG037`
- `IMG038`
- `IMG039`
- `IMG040`
- `IMG041`
- `IMG042`
- `IMG043`
- `IMG044`
- `IMG045`
- `ORIG017`
- `ORIG018`
- `ORIG019`
- `ORIG020`
- `ORIG021`
- `ORIG022`
- `ORIG023`
- `ORIG024`
- `ORIG025`
- `ORIG026`
- `ORIG027`
- `SHOT09`
- `SHOT10`
- `SHOT11`
- `SHOT12`
- `SHOT13`
- `SHOT14`
- `SHOT15`
- `SHOT16`
- `SHOT17`
- `SHOT18`
- `SHOT19`
- `SHOT20`
- `SHOT21`
- `SHOT22`
- `SHOT23`
- `SHOT24`
- `SHOT25`
- `SHOT26`
- `SHOT27`
- `SHOT28`
- `SHOT29`
- `SHOT30`
- `SHOT31`
- `SHOT32`
- `SHOT33`
- `SHOT34`
- `SHOT35`
- `SHOT36`
- `SHOT37`

## Redaktionelle Originalasset-Regeln

- Generische Schlaflaborfotos werden niemals als Bildmaterial des Takeuchi-Versuchs ausgegeben.
- Jede historische Darstellung erhält sichtbare Jahres-/Kontextangabe in der Edit-Quellzeile.
- YELLOW-Assets bleiben bis zum finalen Lizenz-, Attribution- und Persönlichkeitsrechtscheck gesperrt.
- RED-/reference-only Material wird nicht in den Schnitt gelegt.
- Hufford und Cheyne werden nicht durch erfundene Porträts identifiziert; Rekonstruktionen zeigen Handlung, Rückenansicht oder Hände und tragen die Quellzeile `Rekonstruktion`.
- Karten und Dokumente bleiben statisch, vollständig sichtbar und werden nie zum dekorativen Ken-Burns-Hintergrund.
