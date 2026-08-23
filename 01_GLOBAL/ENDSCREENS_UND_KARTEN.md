# Endscreens, Infokarten und Wasserzeichen

**Kurz:** Endscreens und Infokarten gehen **nicht** über die API. Das
Wasserzeichen geht.

---

## Was die API kann und was nicht

Geprüft am 21.08.2026 direkt am Discovery-Dokument der YouTube Data API v3:
**31 Ressourcen, 82 Methoden.** Keine einzige davon betrifft Endscreens,
Infokarten, Annotationen oder Overlays. Das ist keine Rechte- oder
Kontingentfrage — die Endpunkte existieren nicht und haben nie existiert.

```bash
# Gegenprobe, jederzeit wiederholbar
python - <<'EOF'
import sys; sys.path.insert(0, "…/NOESIS Channel/tools")
from noesis_cli import data_api
api = data_api("de")
print(sorted(api._resourceDesc["resources"]))
EOF
```

| | über API | im Studio |
|---|---|---|
| Video hochladen, terminieren | ✅ | |
| Titel, Beschreibung, Schlagwörter | ✅ | |
| Thumbnail | ✅ | |
| Untertitelspur | ✅ | |
| Playlist zuordnen | ✅ | |
| Kommentar setzen | ✅ | |
| Kommentar **anpinnen** | ❌ | ✅ |
| **Wasserzeichen** (Abo-Knopf im Player) | ✅ | ✅ |
| **Endscreen** (Videokachel, Abo, Playlist) | ❌ | ✅ |
| **Infokarten** im laufenden Video | ❌ | ✅ |

## Wasserzeichen — gesetzt

`01_GLOBAL/NOESIS_WATERMARK_300.png`, ab Sekunde 15, unten rechts. Läuft auf
**allen** Videos des Kanals, auch den bestehenden. Ein Klick darauf abonniert.

Zwei Fallstricke beim Setzen:

1. Das Feld `position` ist im Schema als **veraltet** markiert und führt zu
   `400 Invalid Value`. Nur `timing` und `targetChannelId` senden.
2. `watermarks.set` antwortet mit **204 No Content**. `httplib2` stürzt daran
   ab (`ValueError: range() arg 3 must not be zero`). Deshalb den Aufruf
   direkt über eine `AuthorizedSession` absetzen, nicht über den Client.
3. `brandingSettings.watermark` liest den Zustand **nicht** zurück. Das ist
   kein Fehlschlag — Kontrolle nur im Studio.

## Endscreen — was zu setzen ist

Der Abspann jeder Folge läuft **20 Sekunden** und ist so gebaut, dass die
Fläche rechts unten frei bleibt. Genau dort gehören die Elemente hin.

**Für jede Longform-Folge, im Studio unter Editor → Endscreen:**

| Element | Platz | Ziel |
|---|---|---|
| Video | linker Kasten „NÄCHSTE FOLGE" | die konkrete Folge; solange es keine gibt: „Bester Inhalt für Zuschauer" |
| Abonnieren | Fläche rechts unten | Kanalkennung |
| Playlist | daneben | MODELLE DES GEISTES |

**Zwei Infokarten im laufenden Video**, jeweils dort, wo der Text ohnehin
einen Übergang macht:

- am Mid-Roll-CTA (dort, wo die Karte „Schreib es in die Kommentare" steht)
  → Playlist
- zu Beginn des Schlussakts → die vorige Folge

### Zeitmarken je Folge

| Folge | Endscreen ab | CTA-Karte | Schlussakt |
|---|---|---|---|
| EP01A Die Spiegel (`a4WGQDDVwls`) | 9:23 | 4:11 | 7:58 |
| EP02 Gateway (`A10PQ9rHiRA`) | 10:18 | — | 8:44 |
| EP03 PEAR | 10:09 | 6:11 | 9:04 |

## Warum das zählt

Der Kanal hatte am 21.08.2026 **4.347 Aufrufe und 8 Abonnenten**, bei einem
Shorts-Anteil von 95 Prozent am Traffic. Ohne Endscreen läuft der Abspann
zwanzig Sekunden, in denen die Grafik „Jetzt ansehen" sagt und nichts
anklickbar ist. Das ist die billigste offene Stelle im ganzen Kanal.
