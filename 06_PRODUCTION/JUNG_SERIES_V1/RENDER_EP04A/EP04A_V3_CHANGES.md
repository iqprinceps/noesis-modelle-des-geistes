# EP04A — V3 gegenüber V2

**Renderer:** `tools/render_jung_ep04a_v3.py`
**Master:** `final/EP04A_JUNG_KUNDALINI_FINAL_V3.mp4`
**V2 bleibt unangetastet und reproduzierbar** (`render_jung_ep04a_final.py`, eigene Segment- und Asset-Pfade).

## Was garantiert gleich geblieben ist

| | V2 | V3 |
|---|---|---|
| Voice-Master | `EP04A_GEORGE_VO_MASTER.wav` | identisch, kein neuer Take |
| Cue-Raster | 62 Cues | **bitgleich** |
| Gesamtframes | 19.003 | 19.003 |
| Gesamtdauer | 633,433333 s | 633,433333 s |

Alle Änderungen liegen **innerhalb** der Cue-Grenzen. Kein Schnitt wandert über eine Sprechgrenze.

## Was geändert wurde

### 1. Bildverdichtung — 151 statt 120 Shots

31 zusätzliche Shots, alle aus bisher **ungenutztem** Material. Keine Wiederholung: 151 Shots, 151 unikate Bilder.

| Kennzahl | V2 | V3 | Hausstandard |
|---|---|---|---|
| Shots (ohne Outro) | 120 | **151** | 140–155 |
| Ø Shotdauer | 5,11 s | **4,06 s** | 3,5–4,5 s |
| Längster Shot | 7,4 s | **6,7 s** | max 9 s |
| Unikate Bilder | 120 | **151** | ≥ 85 |
| Direkte Wiederholung | 0 | **0** | ≤ 4× |

Kamerabewegung am fertigen Master gemessen (mittlere Graustufendifferenz erstes/letztes Frame je Segment, nur Stills):

| | V1 | V2 | **V3** |
|---|---|---|---|
| Mittel | 28,9 | 15,2 | **19,5** |
| Median | 27,8 | 11,2 | **16,5** |
| Shots unter 10 | 9 / 113 | 41 / 105 | **32 / 136** |
| lang **und** fast still | — | 13 | **5** |

Die verbleibenden fünf sind bewusste Haltemomente (rote Sonne, Hauer-Portrait, „Da ist Wut", die CTA-Karte, „Sechs").

Ausgewählte Zusätze, jeweils am Sprechanker gebunden:

- `A002` „vor Kundalini" → indisches Blatt am Tisch
- `A009` „Bruch mit Freud" → zerrissener Brief
- `A024` „Philemon" → Eisvogelgefieder (der Text nennt die Flügel eines Eisvogels)
- `A042` „Da ist Wut" → Fire-to-Air-Abstract (genau der Übergang Manipura → Anahata)
- `A044` „Nur ein Name" → `PHONE_NAME_ONLY`
- `A046` „formulierst eine Antwort" → `REPLY_FORMING_UNREADABLE`
- `A050` „Karte in Bewegung" → Londoner Druckprozess 1919
- `A053` „Sechs" → Vers über Sahasrara

### 2. Hook

| | V2 | V3 |
|---|---|---|
| Erster Schnitt | 4,83 s | **2,43 s** (Standard ≤ 2,5 s) |
| Shots in den ersten 30 s | 7 | **11** |

### 3. Kamera — Boden angehoben, Spitzentempo unverändert

Die Zurückhaltung von V2 bleibt bewusst erhalten. Geändert wurde nur der **Boden**: in V2 standen 41 von 105 Stills praktisch still, weil reine Schwenks bei Basiszoom 1,045 nur 4,3 % der Bildbreite zu durchqueren hatten.

- `tempo`: `min(1.0, max(.62, d/7.0))` → `min(1.05, max(.70, d/6.2))`
- `pan_tempo`: `.46 × tempo` → `.62 × tempo`
- Basiszoom für reine Schwenks: 1,040–1,045 → 1,072–1,082 (Schwenkweg)
- Zoom-Delta: 0,016–0,025 → 0,022–0,034
- Klemme: 1,008–1,065 → 1,012–1,098

Karten und Videoclips bleiben wie in V2 **ohne** Kamerabewegung.

### 4. Reset-Frames statt Schwarzbilder

`A027` (3:50) und `A062` (10:09) waren flache Schwarzbilder — auf dem Handy liest sich das als „Video zu Ende". V3 legt eine sehr weiche Lichtfahne darüber: Mittel 11 → 32, Maximum 13 → 47. Bleibt der dunkelste Moment der Folge, ist aber als Raum lesbar. Eigene Dateien (`*_V3.png`), V2-Assets unverändert.

### 5. Echtes Archiv statt Nachbildung

An drei Stellen nutzte V2 ein erzeugtes Bild, obwohl die reale Aufnahme im Repo liegt:

| Cue | V2 | V3 |
|---|---|---|
| `A028` „Herbst 1932" | erzeugter Saal | **Zürich Bahnhofplatz 1930** (CC-BY-SA-4.0) |
| `A032` | erzeugtes Galvanometer | **Jungs Galvanometer, Burghölzli 1904/05** (PD) |
| `A054` | erzeugtes Leadbeater-Portrait | **Leadbeater-Foto ca. 1925** (PD) |

Ergänzt: Burghölzli ca. 1890 (PD) bei `A013`, Jung im Burghölzli ca. 1909/10 bei `A056`.

Rekonstruktionsanteil: 88 % → **86 %**. Zwei erzeugte Portraits realer Personen sind durch echte Fotografien ersetzt.

### 5b. Korrektur an `A007`

Ein erster V3-Durchgang setzte bei „Jetzt liegt vor ihm eine **indische** Karte" eine erzeugte **europäische** illuminierte Handschrift (lateinische Textura) ein — falsche Kultur an genau der Stelle, an der der Text die Herkunft benennt. Ersetzt durch die reale **Sapta-Chakra-Platte von 1899** (PD). Damit steht dort eine echte indische Quelle statt einer erzeugten europäischen.

> **Attribution:** `EP04A_Zuerich_Bahnhofplatz_1930` ist CC-BY-SA-4.0 und muss in die Videobeschreibung. Lizenzdatei liegt neben dem Bild.

### 6. Pauli-Kette entzerrt

V2 zeigte in den letzten 30 s viermal Pauli (zwei Portraits, Karte, Endcard). Das zweite erzeugte Portrait ist durch **ETH Zürich** ersetzt.

### 7. Auslieferungspegel

Der erste Versuch — nur die Limiter-Schwelle von `.95` auf `.89` zu senken — hat **das Gegenteil bewirkt** und ist verworfen: eine tiefere Schwelle komprimiert mehr, hebt den Durchschnittspegel (−13,6 → −13,0 LUFS) und lässt den Limiter so hart arbeiten, dass die Intersample-Peaks auf 0,0 dBTP steigen. Gemessen, nicht vermutet:

| Kette | I (LUFS) | True Peak |
|---|---|---|
| V2 `alimiter=.95` | −13,6 | −0,5 |
| `alimiter=.89` | −13,0 | **0,0** |
| 192 kHz + `.89` | −13,0 | 0,0 |
| `loudnorm TP=-1` allein | −14,0 | −0,9 |
| **192 kHz + `.89` + `loudnorm TP=-1.5`** | **−14,1** | **−1,4** |

Ausgeliefert wird die letzte Zeile: begrenzt auf 192-kHz-Oversample, danach `loudnorm` mit echter True-Peak-Kontrolle. Ergebnis **−14,1 LUFS / −1,4 dBTP** — genau der Wert, auf den YouTube normalisiert, mit sicherem Abstand nach oben.

## Bewusst nicht geändert

- **Keine Rekonstruktionslabels.** Redaktionelle Entscheidung. `CLAIMS_LOCK_V5.md` (Visual Lock `A-G05`) und `01_GLOBAL/00_PRODUKTIONSSTANDARD.md` („Wenn rekonstruiert wird") schreiben sie weiterhin vor — **die beiden Dokumente sind noch offen und widersprechen dem ausgelieferten Schnitt.** Die YouTube-Pflichtangabe für synthetische Inhalte wird über das Upload-Formular abgedeckt, nicht über eine Bauchbinde.
- **Mid-Roll-CTA** bleibt bei 72 % der Laufzeit — verschiebbar nur mit neuer Voice.
- **Haltemomente** `A005` (rote Sonne), `A040` (Du bist wütend), `A043`, `A056` bleiben einzeln stehen. Dort ist der Stillstand der Inhalt.
