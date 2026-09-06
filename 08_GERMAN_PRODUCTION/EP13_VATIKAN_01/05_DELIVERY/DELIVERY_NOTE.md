# EP13_DE — Lieferhinweis

Deutsche Fassung derselben Episode. Gerendert 2026-09-06.

| | |
|---|---|
| Laufzeit | 9:35 (574,96 s) |
| Bild | H.264, 1920x1080, 30 fps |
| Ton | AAC 48 kHz mono |
| Lautheit | −14,2 LUFS, −1,5 dBTP, LRA 2,3 |
| Größe | 329 MiB |
| SHA-256 | `d91a2c86510360625cc61ff784bf03041bfd489baf6d50d81ddb6237b4d176ee` |

## Was aus der englischen Fassung übernommen ist

Jedes Bild, jeder Clip und jedes erworbene Original. Das geht, weil das deutsche
Skript an denselben 115 Beats entlang geschrieben wurde statt frei übersetzt zu
werden, also gehört jedes Einzelbild weiterhin dorthin, wo es war. Es gibt im
Repository ein älteres deutsches Drehbuch; das folgt einer anderen Struktur und
nennt den Inhalt der Vision bereits im Kaltstart, was den Mittelpunkt der Folge
zerstört. Es wurde verworfen.

Sprachlich neu ist alles, was Sprache trägt: Erzählung, elf Karten, drei
Thumbnails, Beschreibung und Metadaten.

## Was die Sprache technisch verändert hat

Deutsch braucht **575 s für denselben Inhalt, den Englisch in 508 s erzählt**.
Daraus folgen drei Dinge, die nicht offensichtlich sind.

**Die Abschnittsgrenzen der Musik** stehen als absolute Sekunden. Sie wurden über
den jeweils zugehörigen Beat auf die deutschen Zeiten abgebildet, nicht mit einem
Faktor gestreckt, damit jede Wende weiterhin auf ihrer Aktgrenze sitzt.

**CLIP09** muss jetzt 9,1 s aus einer 6-Sekunden-Quelle füllen. Der Renderer
verlangsamt ihn bis zur Grenze von 1,35-fach und hält dann das letzte Bild, auf
dem die Hände ohnehin still liegen.

**H54_SEAL_SINGLE_MACRO** steht in der deutschen Fassung still. Die längere
Standzeit macht die Kamerabewegung noch langsamer, und die feine Gravur des
Siegels beginnt zu schimmern. In der englischen Fassung bewegt es sich weiterhin.

## Ein Fehler, den erst die Lokalisierung sichtbar gemacht hat

Das Cue-Sheet-Werkzeug zählte Wörter mit `[0-9a-z']`. Diese Zeichenklasse zerlegt
jedes deutsche Wort, das in der Mitte einen Umlaut oder ein Eszett trägt, sodass
„Größe" als zwei Wörter zählte, der Zeiger verrutschte und vier Beats hinten
abfielen. Es zählt jetzt Unicode-Wortzeichen, und das deutsche Cue-Sheet stimmt
mit dem englischen überein: 134 Zustände über 115 Beats.

Ebenfalls sichtbar geworden: das deutsche Bindewort „oder" ist breiter als „or"
und überlappte auf zwei Karten das folgende Wort. Beide messen es jetzt.

## Lautheit

Die Gain-Schleife blieb bei −15,0 LUFS stehen, ein volles Dezibel unter dem
Kanalziel. Die Ursache lag nicht am Material: die deutsche und die englische
Sprachspur sind mit −18,4 und −18,3 LUFS praktisch identisch, und beide Mischungen
messen gleich. `alimiter` arbeitet auf Sample-Ebene und sieht keine
Intersample-Spitzen, meldete also −0,9 dBTP und verhinderte damit jede weitere
Anhebung. Der Limiter läuft jetzt bei 192 kHz und kommt danach zurück auf 48; das
schafft genug Reserve, um das Ziel zu erreichen.

Ein Zwischenversuch, das jeweils beste Teilergebnis zu behalten, machte es
schlechter, weil dann der erste Durchlauf gewann, der die Spitzengrenze gerade
einhielt, und die Schleife aufhörte zu steigen. Verworfen.

## Prüfungen

| Prüfung | Ergebnis |
|---|---|
| Kadenz-Gate, bewegte Standbilder | PASS, 101 geprüft, 0 Beanstandungen |
| Segment-Integrität | 126 / 126 |
| Beats gegen die englische Fassung | 115 / 115, deckungsgleich |
| Zustände | 126 Segmente |
| Lautheit | −14,2 LUFS, −1,5 dBTP |

## Offen

**Die Blind-Transkription konnte nicht laufen.** Das ElevenLabs-Hauptkonto hat
kein Guthaben mehr, und der Schlüssel des Ausweichkontos trägt keine Berechtigung
für Spracherkennung. Damit fehlt genau die Prüfung, die in der englischen Fassung
„John the Thirteenth" gefunden hat.

Als Ersatz wurde das Forced Alignment ausgewertet, das dieselbe Aufnahme
beurteilt. Die ausgeschriebenen Ordinalzahlen liegen unauffällig: „Johannes der
Dreiundzwanzigste" bei 0,84, „Paul der Sechste" bei 0,34, „Johannes Paul der
Zweite" bei 0,22. Alle Jahreszahlen und Eigennamen liegen unter 1,0. Auffällig
sind nur „Agca" mit 3,15 und die Großbuchstabenwörter „WELT" und „ICH". Diese drei
Stellen wurden als Hörprobe zur Beurteilung vorgelegt.

Sobald das Hauptkonto am 14. September zurückgesetzt ist, sollte
`produce_ep13_de_voice.py qa` nachgeholt werden.
