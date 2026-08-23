# EP01A Die Spiegel — Quellen und Lizenzen

Diese Datei liegt neben den Assets und trägt die Attributionen, die in die
Videobeschreibung gehören (Produktionsstandard § 5 und § 9.6).

**Kein Upload erfolgt.** Die Attributionen sind vorbereitet, nicht veröffentlicht.

---

## 1 Echtes Archivmaterial, frei lizenziert

Hat nach § 5 Vorrang vor jeder Generierung und ist überall dort eingesetzt,
wo es das Erzählte deckt.

| Datei im Schnitt | Inhalt | Urheber | Lizenz |
|---|---|---|---|
| `K01_kozyrev_portrait_1959_CC0.png` | Nikolai Kozyrev, 1959 | unbekannt | CC0 / gemeinfrei |
| `KZ_WC_02_BIG_S1_2015.jpg` | Anlage BIG-S1, Nowosibirsk 2015 | Brattarb | CC BY-SA 3.0 / GFDL |
| `KZ_WC_01_HORIZONTAL_BIG_G2PF_2015.jpg` | Horizontale Anlage BIG-G2pf, 2015 | Brattarb | CC BY-SA 3.0 / GFDL |
| `KZ_003_Kozyrev_mirrors_modern_photo_2014.jpg` | Anlage in Nowosibirsk, 2014 | SerMega | CC BY-SA 4.0 |
| `KZ_WC_04_PATENT_APPARATUS_1992.gif` → `KZ_PATENT_APPARATUS_1992.png` | Zeichnung der Anlage zur Patentschrift | SerMega | CC BY-SA 4.0 |
| `K04_RU2122446C1_patent_AMBER.pdf` → `KZ_PATENT_SEITE_01/02.png` | Patentschrift RU 2122446 C1, Seite 1 und 2 | Rospatent | Amtsdokument |
| `K05a_patent_fig1_AMBER.png` | Figur 1 der Patentschrift | Rospatent | Amtsdokument |
| `KZ_004_Pulkovo_big_refractor.jpg` | Großer Refraktor, Pulkowo-Observatorium | unbekannt | gemeinfrei |
| `K06_Alphonsus_LRO_NASA_PD.png` | Krater Alphonsus | NASA | gemeinfrei |
| `NASA_TRACERS_MAGNETIC_RECONNECTION_1080p.mov` | Magnetische Rekonnexion am Erdfeld | NASA/GSFC, Visualisierung Adriana Manrique Gutierrez | gemeinfrei |

Die GIF- und PDF-Vorlagen werden von `tools/spg_produce.py prepare` in PNG
überführt; Inhalt und Lizenz ändern sich dabei nicht.

**Auflage zur NASA-Visualisierung** (aus `NASA_SVS/SOURCES.md`): nur unter
Erzählung über magneto-ionosphärische Bedingungen einsetzen, nie als Beleg für
die Anlage. Eingehalten — beide Einsätze liegen unter „wo das Magnetfeld der
Erde von sich aus am dünnsten ist" und „in den Phasen, in denen die
geomagnetische Aktivität niedrig ist".

**Nicht verwendet:** CC BY-NC und CC BY-ND scheiden nach § 5 aus.

## 2 Rekonstruktionen

Alle mit `tools/spg_image_gen.py` erzeugt, Modell `gemini-2.5-flash-image`
über Vertex AI, 16:9, 2K. In der Timeline durchgehend mit der Quellzeile
`Rekonstruktion` gekennzeichnet.

**Kaznacheev und Trofimov:** kein frei lizenziertes Porträt auffindbar. Nach
§ 5 rekonstruiert — in Handlung, halbnah, Kaznacheev streng von hinten, ohne
erkennbares Gesicht. Die Identität tragen Patentschrift und Anlagenfotos.

**Keine Familienfotos**, keine erfundenen Dokumente, keine erfundenen
kyrillischen Beschriftungen.

## 3 Karten und Animationen

Vollständig eigene Erzeugung mit Pillow und numpy:
`tools/spg_graphics.py` (zehn Karten und Endcard, Thumbnail) und
`tools/spg_motion.py` (`polarlicht`, `magnetfeld`, `spirale`, `zeitfluss`).
Kein fremdes Material, keine Fremdschriften außer den Systemschriften.

## 4 Ton

Stimme: ElevenLabs, `JBFqnCBsd6RMkjVDRZzb` (George), `eleven_multilingual_v2`.
Musikbett: Eigensynthese mit ffmpeg, drei Schichten, keine Samples.
Kein Stockmaterial, kein Fremdton.

## 5 Attributionsblock für die Videobeschreibung

```
Bildnachweise
Anlagen in Nowosibirsk: Brattarb, CC BY-SA 3.0 (Wikimedia Commons) —
  „Установка БИГ-С1 2015-01-15", „Горизонтальная установка БИГ-Г2пф 2015-09-12"
Anlage 2014 und Zeichnung zur Patentschrift: SerMega, CC BY-SA 4.0
  (Wikimedia Commons) — „Kozyrev mirrors", „Kozyrevs Mirrors Patent 2122446"
Nikolai Kozyrev, 1959: gemeinfrei (CC0)
Pulkowo-Observatorium, Großer Refraktor: gemeinfrei
Krater Alphonsus: NASA, gemeinfrei
Magnetische Rekonnexion: NASA Goddard Space Flight Center, TRACERS,
  Visualisierung Adriana Manrique Gutierrez, gemeinfrei
Patentschrift RU 2122446 C1: Amtsdokument der Russischen Föderation

Alle übrigen Bilder sind gekennzeichnete Rekonstruktionen. Karten,
Animationen und Musik sind Eigenproduktion.
```
