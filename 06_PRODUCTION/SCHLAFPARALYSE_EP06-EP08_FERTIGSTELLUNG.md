# Schlafparalyse EP06–EP08 — Fertigstellung

**Stand:** 25.08.2026

Dieses Dokument hält fest, was in diesem Durchgang gebaut wurde, was offen ist
und mit welchem Befehl das Offene abgeschlossen wird.

---

## Kurzstand

| | EP06 | EP07 | EP08 |
|---|---|---|---|
| Originalquellen aufbereitet | 13 | 17 | 50 |
| Redaktionelle Ableitungen | 13 | 47 | 21 |
| Karten / Quellenkarten | 14 | 12 | 7 |
| KI-Stills ergänzt | 29 | 37 | 2 |
| Transformationsclips | 4 + 6 | 4 | 4 |
| Ebenensequenzen | — | — | 22 |
| Sprecherfassung | ✅ 10:19 | ⛔ Kontingent | ✅ 10:38 |
| Sound-Stems + Finalmix | ✅ −14,0 LUFS | offen | ✅ −14,0 LUFS |
| Cue-Sheet + Render-Manifest | ✅ | ✅ | ✅ |
| Fertiges Video | offen | offen | ✅ |

---

## Der eine echte Blocker: EP07 hat keine Stimme

Das ElevenLabs-Kontingent (Creator-Tarif) war für zwei der drei Folgen
ausreichend. Nach EP08 und EP06 sind rund 7.100 Zeichen übrig, EP07 braucht
10.263 — es fehlen etwa 3.200.

Zwei Wege:

1. **Reset abwarten.** Das Kontingent erneuert sich am **14.09.2026**.
2. **Tarif aufstocken.** Dann sofort möglich.

Sobald Kontingent da ist, ist EP07 mit vier Befehlen fertig:

```bash
python "C:/Users/iQPrinceps/Documents/Codex/NOESIS Channel/tools/elevenlabs_cli.py" batch --batch-file 06_PRODUCTION/EP07_SCHLAFPARALYSE_V4/VOICE_EP07/voice_batch.json --execute
python tools/schlafparalyse_voice_v5.py EP07 all
python tools/build_schlafparalyse_audio_stems.py EP07
python tools/build_schlafparalyse_final_mix.py EP07
python tools/noesis_render_schlafparalyse_v5.py EP07 all
```

Die Batchdatei nutzt denselben George-Lock wie EP01–EP06 und EP08
(`JBFqnCBsd6RMkjVDRZzb`, `eleven_multilingual_v2`, Seed 2402).

**Hinweis zu den Pfaden:** `elevenlabs_cli.py` löst relative Pfade gegen sein
eigenes Repository auf, nicht gegen das aktuelle Verzeichnis. Für den Batchlauf
muss die Datei absolute Pfade enthalten; ein kleines Umschreiben der
`text_file`- und `output_dir`-Einträge auf absolute Pfade genügt.

---

## Zwei Fehler, die in diesem Durchgang gefunden und behoben wurden

### 1. Forced Alignment: geändertes API-Schema

Die ElevenLabs-Alignment-API liefert `characters` inzwischen als Liste von
Objekten (`{text, start, end}`) statt als Liste von Einzelzeichen mit zwei
parallelen Zeitarrays.

`tools/noesis_render.py` erkennt dieses Schema in seinem ersten Zweig nicht und
fällt auf `words` zurück. Dort setzt seine Heuristik vor jedes Wort ein
Leerzeichen — die Wortliste enthält aber bereits eigene Leerzeicheneinträge.
Der rekonstruierte Text bekommt doppelte Leerzeichen, **keine Ankersuche trifft
mehr, und sämtliche Cues rutschen auf Zeit 0.** Im Ergebnis: 151 von 155 Shots
unter 1,5 Sekunden, ein Shot mit 159 Sekunden.

Behoben in `tools/schlafparalyse_voice_v5.py` (`normalise_alignment`): die
Antwort wird beim Speichern zusätzlich in das erwartete Schema gebracht.

**Betrifft auch EP01–EP05**, falls deren Alignment neu geholt wird.

### 2. Kamerafahrt lief in Stufen

Die Kamera-QA (`tools/spg_zappelpruefung.py`) fiel durch: gemessene
Bilddifferenzen sprangen zwischen 0,00 und 2,50 — das Bild stand mehrere Frames
still und ruckte dann weiter.

`tools/noesis_render.py` wich an zwei Stellen vom eigenen Produktionsstandard
(`01_GLOBAL/00_PRODUKTIONSSTANDARD.md`, „Die Fahrt muss glatt laufen") ab:

| | Standard | Code bisher |
|---|---|---|
| Vorlage vor `zoompan` | 7680×4320 | 3840×2160 |
| Zwischenschritte je Bild | vier, gemittelt mit `tmix` | `tblend` über je zwei von vier |

`zoompan` rechnet ganzzahlig. Sieht es die Vorlage in Ausgabegröße, ist ein
Schritt ein voller Ausgabepixel. Gemessen am selben Segment:

| Aufbau | Zappeln |
|---|---:|
| 3840 → `zoompan` s=1920 (bisher) | 0,788 |
| 7680 → `zoompan` s=1920 | 0,407 |
| 7680 → `zoompan` s=3840 → Lanczos auf 1920 | **0,169** |

Grenzwert ist 0,20. Der abschließende Downscale ist entscheidend — gibt
`zoompan` direkt in Ausgabegröße aus, rastet sein interner Scaler wieder auf
ganze Pixel.

Zusätzlich wird die Hintergrundunschärfe in `base_filter` jetzt mit der
Arbeitsauflösung skaliert; vorher war der abgedunkelte Grund bei bewegten Shots
schärfer als bei statischen.

**Kosten:** rund 65 Sekunden statt weniger Sekunden je bewegtem Shot.
Ein Episodenrender dauert damit etwa eine Stunde.
**Betrifft ebenfalls EP04A, EP04B und EP05.**

---

## Belege, die nicht beschaffbar waren

Für nicht frei nutzbare oder nicht mehr abrufbare Quellen wurden
**Quellenkarten** gebaut — typografische Belegkarten im Hausstil, die die
Aussage, die Art der Quelle und die Beleggrenze benennen.

Es wurde **keine** Benutzeroberfläche, Archivansicht, Paperseite oder ein
Buchumschlag nachgebaut. Ein nachgestellter Forenthread oder eine erfundene
Archivseite wäre ein gefälschter Beleg und genau das, was die Claims-Locks der
Folgen verbieten.

Betroffen:

- **EP06:** Studentenzimmer 1963 und Oral-History-Gerät — keine gesicherte
  freie Quelle, bewusst als Lücke benannt.
- **EP07:** Hufford-Porträt und Buchumschlag, Jalal/Hinton-Paperseite,
  Art-Bell-Sendungsmitschnitt, chinesische Druckmotiv-Quelle.
- **EP08:** McNally/Clancy-Paperseite, DPH-Medizinquelle, Hat-Man-Forenbeleg,
  Web-Archivansichten, *The Nightmare* Key Art.

Drei Salem-Gerichtsakten aus dem Massachusetts-Digitalarchiv liefern statt der
Datei eine Bot-Erkennungsseite. Sie wurden nicht umgangen. Für den Schnitt sind
sie nicht nötig — die 47 EP07-Ableitungen stammen aus bereits vorhandenen
Mastern.

---

## Was zusätzlich korrigiert wurde

**EP06, sieben Bilder mit eingebranntem Text.** Der Companion-Prompt nannte den
deutschen Sinn-Anker in Anführungszeichen; das Modell schrieb ihn wörtlich ins
Bild („HILFLOS!", „GEFAHR / VERURSACHER", beschriftete Karteikarten). Zwei
Bilder zeigten zusätzlich eine erfundene Messkurve, beschriftet als
„1982 – STUDIE HUFFORD" beziehungsweise als PSG-Aufzeichnung — fabrizierte
Belegabbildungen. Alle sieben neu erzeugt mit explizitem Textverbot.

**EP06, CLIP009.** Erste Fassung enthielt eine erfundene EKG-artige Kurve mit
lesbaren Achsenzahlen. Neu erzeugt; die Ordnung wird jetzt rein über physische
Objekte dargestellt.

**EP08, Textkarten-Häufung.** Nach dem ersten Schnitt standen zwischen 330 s und
490 s neun Quellenkarten, zwei davon unmittelbar hintereinander — dreizehn
Sekunden Fließtext am Stück. Ursache: jeder fehlende Beleg bekam eine eigene
Karte, und dieselben Karten speisten zusätzlich die Ebenensequenzen. Redundante
Paare wurden zusammengefasst (eine „Detailansicht" einer Textkarte trägt keine
zusätzliche Information), die freiwerdenden Cues tragen jetzt Bilder.
Ergebnis: 15 statt 18 Karten, keine mehr hintereinander, 11 % statt 13 %
Laufzeit.

**EP06, zwei zu kleine Originalquellen.** Das Amygdala-GIF (200×200) und die
Circadian-Grafik (400×267) waren für 1080p unbrauchbar. Ersetzt durch das
Blausen-Diagramm des limbischen Systems (1800×1200, enthält die Amygdala) und
eine Darstellung des suprachiasmatischen Nukleus (2976×1828).

---

## Neue Werkzeuge

| Datei | Zweck |
|---|---|
| `tools/build_schlafparalyse_cue_sheets.py` | Sync-Plan → Cue-Sheet + Render-Manifest, mit Bilddichte-Prüfung |
| `tools/schlafparalyse_voice_v5.py` | VO-Master und Alignment im 06_PRODUCTION-Layout |
| `tools/build_schlafparalyse_final_mix.py` | Finalmix mit VO-Ducking nach Mix-Lock |
| `tools/build_schlafparalyse_source_cards.py` | Quellenkarten für nicht beschaffbare Belege |
| `tools/generate_ep06_supplement.py` | EP06: IMG033–045 und SHOT-Companions |
| `tools/generate_ep07_supplement.py` | EP07: IMG024–060 aus den Promptkernen |
| `tools/generate_ep06_veo_supplement.py` | EP06: CLIP005–010 |
| `06_PRODUCTION/EP0*/POST_PLAN/build_*.py` | Episodenspezifische Ableitungen |

Die Cue-Sheets liegen als `VISUAL_CUE_SHEET_V5.csv` unter
`PRODUCTION_SUMMARY/<Episode>/`, die Manifeste als `render_manifest.json` in
den Episodenordnern. Ein Cue entspricht einem Sprechertake; die zugeordnete
Liste wird innerhalb des Take-Fensters in Einzelshots aufgeteilt.
