# EP03 PEAR V2 — Production Guide

## Status
- **V2 Script**: `07_VOICE_SCRIPT_CLEAN_V2.txt` (fertig)
- **Voice Source Files**: `voice/source/EP03_V2_*.txt` (8 Stems, fertig)
- **Voice Batch**: `voice/voice_batch_v2.json` (fertig)
- **Alte Assets**: 84 generierte Bilder + 10 Cards + 4 Motion-Videos (wiederverwendbar)
- **Alte Voice Stems**: `voice/raw_stems/EP03_VO_*.mp3` (V1, NICHT wiederverwendbar)

---

## Schritt 1: Voice generieren

```bash
# Voice Batch ausführen (braucht ElevenLabs API Key)
python tools/pear_voice.py
```

**Achtung**: Die `pear_voice.py` referenziert noch `voice_batch.json` (V1).
Entweder:
- `voice_batch_v2.json` → `voice_batch.json` umbenennen, ODER
- `pear_voice.py` anpassen, dass es `voice_batch_v2.json` liest

---

## Schritt 2: Neue Bilder generieren (Vertex AI)

### Wiederverwendbare Bilder (V1)

Diese Bilder aus V1 können 1:1 übernommen werden:

| V1-Bild | Verwendung in V2 |
|---|---|
| `pe_a01_keller_weit` | S1 Paradoxon: „Er sitzt im Keller" |
| `pe_a02_kiste_detail` | S1 Paradoxon: „graue Kiste mit roter Leuchtziffer" |
| `pe_a05_gesicht_konzentration` | S3 Maschinen: „Dann sitzt der Mensch da" |
| `pe_b01_jahn_portraet` | S1 Paradoxon: „Robert Jahn" |
| `pe_b02_jahn_schreibtisch` | S1 Paradoxon: „hat das Standardwerk geschrieben" |
| `pe_b05_buchruecken` | S1 Paradoxon: „Standardwerk" |
| `pe_b06_fakultaetssitzung` | S1 Paradoxon: „entscheidet über Berufungen" |
| `pe_b10_dunne_portraet` | S2 McDonnell: „Brenda Dunne" |
| `pe_b11_dunne_am_ordner` | S2 McDonnell: „bleibt bis zum letzten Tag" |
| `pe_b13_efeu_backstein` | S2 McDonnell: „Princeton" |
| `pe_c01_werkbank` | S3 Maschinen: „Und dann bauen sie Maschinen" |
| `pe_c02_platine_makro` | S3 Maschinen: „Schaltung" |
| `pe_c03_rauschdiode` | S3 Maschinen: „Rauschdiode" |
| `pe_c04_oszilloskop_rauschen` | S3 Maschinen: „Rauschen" |
| `pe_c05_schaltung_zeichnung` | S3 Maschinen: „Schaltung" |
| `pe_c06_kiste_offen` | S3 Maschinen: „Das Herzstück ist eine Kiste" |
| `pe_c07_kabel_bundel` | S3 Maschinen: „Mit nichts als Aufmerksamkeit" |
| `pe_c08_geraet_reihe` | S3 Maschinen: „Apparate" |
| `pe_c09_patent_mappe` | S3 Maschinen: „Erwartungswert" |
| `pe_d01_labor_weit` | S3 Maschinen: „Labor" |
| `pe_d02_sitzung_seitlich` | S3 Maschinen: „Teilnehmer" |
| `pe_d03_zettel_absicht` | S3 Maschinen: „legt fest, was er will" |
| `pe_d04_uhr_wand` | S3 Maschinen: „Zwei, drei Minuten" |
| `pe_d05_kugelwand_weit` | S3 Maschinen: „Wand aus Acrylglas" |
| `pe_d06_kugeln_fallen` | S3 Maschinen: „Kugeln fallen" |
| `pe_d07_faecher_unten` | S3 Maschinen: „neunzehn Fächer" |
| `pe_d08_pendel_quarz` | S3 Maschinen: „Pendel" |
| `pe_d09_springbrunnen` | S3 Maschinen: „Springbrunnen" |
| `pe_d10_kopfhoerer_tisch` | S3 Maschinen: „Kopfhörer" |
| `pe_d11_protokollbuch` | S3 Maschinen: „Labor notiert" |
| `pe_d12_stuhl_leer_labor` | S4 Operator 10: „leerer Stuhl" |
| `pe_e01_linie_steigt` | S4 Operator 10: „Linie steigt" |
| `pe_e02_muenzen_flug` | S4 Operator 10: „Münzwürfe" |
| `pe_e03_null_eins_strom` | S4 Operator 10: „Nullen und Einsen" |
| `pe_e04_waage_zunge` | S4 Operator 10: „ganze Effekt" |
| `pe_e05_sandkorn` | S4 Operator 10: „Sandkorn" |
| `pe_f01_endlospapier_boden` | S5 Replikation: „Endlospapier" |
| `pe_f03_zwei_stapel` | S5 Replikation: „zwei Stapel" |
| `pe_f04_fenster_regen` | S5 Replikation: „Regen" |
| `pe_f06_person_am_stapel` | S5 Replikation: „Person am Stapel" |
| `pe_f07_einzelner_stuhl_reihe` | S5 Replikation: „einzelner Stuhl" |
| `pe_f08_taschenrechner` | S5 Replikation: „Taschenrechner" |
| `pe_g01_institut_freiburg` | S5 Replikation: „Freiburg" |
| `pe_g02_labor_deutsch` | S5 Replikation: „deutsches Labor" |
| `pe_g03_drei_geraete` | S5 Replikation: „drei Geräte" |
| `pe_g04_protokoll_unterschrift` | S5 Replikation: „Protokoll" |
| `pe_g05_versand_kiste` | S5 Replikation: „Versand" |
| `pe_g06_telefonat_nacht` | S5 Replikation: „Telefonat" |
| `pe_g07_zwei_kurven` | S5 Replikation: „zwei Kurven" |
| `pe_g08_flaches_ergebnis` | S5 Replikation: „flaches Ergebnis" |
| `pe_g09_veroeffentlichung` | S5 Replikation: „Veröffentlichung" |
| `pe_g10_labor_weiterarbeit` | S5 Replikation: „weiterarbeiten" |
| `pe_h01_kisten_packen` | S7 Was bleibt: „Kisten packen" |
| `pe_h02_leerer_raum` | S7 Was bleibt: „leerer Raum" |
| `pe_h03_archivkarton` | S7 Was bleibt: „Archiv" |
| `pe_h04_datentraeger` | S7 Was bleibt: „Datenträger" |
| `pe_h05_fenster_abend` | S7 Was bleibt: „Abend" |
| `pe_h06_grabstein_schlicht` | S7 Was bleibt: „Grabstein" |
| `pe_h07_schreibtisch_leer` | S7 Was bleibt: „leerer Schreibtisch" |
| `pe_h08_netz_weltkarte` | S7 Was bleibt: „Weltkarte" |
| `pe_h09_serverraum_klein` | S7 Was bleibt: „Serverraum" |
| `pe_h10_generator_heute` | S7 Was bleibt: „Generator heute" |

### NEUE Bilder (müssen generiert werden)

| ID | Prompt | Verwendung |
|---|---|---|
| `pe_v2_01_mcdonnell_f15` | McDonnell Douglas F-15 im Flug, dramatisches Licht, 1970er Jahre Ästhetik | S2 McDonnell: „Die F-15" |
| `pe_v2_02_mcdonnell_mercury` | Mercury-Kapsel im Weltraum, historischer NASA-Stil | S2 McDonnell: „Die Mercury-Kapsel" |
| `pe_v2_03_pilot_cockpit` | Pilot im Cockpit einer F-15, Nachdenklichkeit, 1970er | S2 McDonnell: „Gedanken des Piloten" |
| `pe_v2_04_offtime_uhr` | Uhr die rückwärts läuft, verschwommene Zeiger, surrealistisch | S6 Off-Time: „73 Stunden vorher" |
| `pe_v2_05_baseline_glatt` | Perfekte Glockenkurve die zu glatt aussieht, unheimlich | S6 Off-Time: „Zu brav. Zu glatt." |
| `pe_v2_06_geist_still` | Menschlicher Kopf im Profil, darin ein ruhiger See, Meditation | S6 Off-Time: „Ist mein Geist überhaupt jemals still?" |
| `pe_v2_07_schweine_fliegen` | Surrealistisches Bild: Schwein das fliegt, im Stil von Magritte | S7 Kritik: „Schweine können nicht fliegen" |
| `pe_v2_08_princeton_schweigen` | Princeton Campus bei Nacht, leere Straßen, Stille | S7 Kritik: „Princeton schweigt" |

### Wiederverwendbare Cards

| Card | Verwendung in V2 |
|---|---|
| `PE_CARD_PATENT` | S3 Maschinen: Patent |
| `PE_CARD_MASSE` | S3 Maschinen: 200 Würfe |
| `PE_CARD_MUSTER` | S3 Maschinen: Mehr Einsen |
| `PE_CARD_KASKADE` | S3 Maschinen: 12 Minuten |
| `PE_CARD_FRAGE` | S4 Operator 10: 5000 Kopf |
| `PE_CARD_COMMENT` | S4 Operator 10: Kommentar-Prompt |
| `PE_CARD_PROBE` | S5 Replikation: Selbstüberprüfung |
| `PE_CARD_ZWEI_ERGEBNISSE` | S5 Replikation: zwei Ergebnisse |
| `PE_CARD_SCHLUSSSTAND` | S7 Was bleibt: Schlussstand |
| `PE_ENDCARD` | Endcard (muss aktualisiert werden) |

### NEUE Cards (müssen generiert werden)

| ID | Text | Verwendung |
|---|---|---|
| `PE_V2_CARD_MCDONNELL` | McDONNELL DOUGLAS / F-15 · F/A-18 · Mercury | S2 McDonnell |
| `PE_V2_CARD_OFFTIME` | OFF-TIME / 73h vorher · 336h nachher | S6 Off-Time |
| `PE_V2_CARD_BASELINE` | BASELINE BIND / „Zu brav" | S6 Off-Time |
| `PE_V2_CARD_MODELL` | MODELL DES GEISTES / „Ist mein Geist jemals still?" | S6 Off-Time |

### Motion Videos (wiederverwendbar)

| Video | Verwendung |
|---|---|
| `muenzwurf.mp4` | S3 Maschinen: „200 Würfe" |
| `rauschen.mp4` | S3 Maschinen: „Rauschen" |
| `abweichung.mp4` | S4 Operator 10: „Abweichung" |
| `kaskade.mp4` | S3 Maschinen: „Kugeln fallen" |

---

## Schritt 3: Timeline bauen

Die Shotliste muss komplett neu gebaut werden, da sich die Textstruktur geändert hat.

**Neue Aktstruktur (8 Akte):**

| Akt | Name | Inhalt |
|---|---|---|
| S1 | Paradoxon | Dekan, Keller, 28 Jahre, „Warum?" |
| S2 | McDonnell | McDonnell Douglas, F-15, Pilotengedanken, PEAR-Gründung, Dunne |
| S3 | Maschinen | REG, RMC, Patent, Technik, Glockenkurve |
| S4 | Operator 10 | Effektgröße, Operator 10, Mystery, Kommentar-Prompt |
| S5 | Replikation | Freiburg/Gießen, gescheitert, weiterarbeiten |
| S6 | Off-Time | Off-Time-Experimente, Baseline Bind, „Modell des Geistes" |
| S7 | Kritik | Meta-Analyse, „Schweine fliegen nicht", Princeton schweigt, Schließung |
| S8 | Was bleibt | Jahn stirbt, GCP, Cliffhanger |

---

## Schritt 4: Endcard aktualisieren

Die Endcard muss folgende Elemente enthalten:
- **Subscribe-Button** (YouTube-konform, nicht spammy)
- **Kommentar-Prompt**: „Was denkst du: Kann der Geist die Materie beeinflussen?"
- **Nächste Folge**: Global Consciousness Project
- **Playlist-Link**: Modelle des Geistes

---

## Schritt 5: Production Pipeline ausführen

```bash
# 1. Voice generieren (ElevenLabs)
python tools/pear_voice.py

# 2. Neue Bilder generieren (Vertex AI)
python tools/pear_image_gen.py

# 3. Timeline bauen
python tools/pear_produce.py timeline

# 4. Audio mischen
python tools/pear_produce.py audio

# 5. Segmente rendern
python tools/pear_produce.py render

# 6. Untertitel generieren
python tools/pear_produce.py captions

# 7. QA
python tools/pear_produce.py qa
```

---

## Zusammenfassung

| Was | Status | Nächster Schritt |
|---|---|---|
| V2 Script | ✅ fertig | — |
| Voice Source Files | ✅ fertig | ElevenLabs API aufrufen |
| Voice Batch JSON | ✅ fertig | — |
| Alte Bilder (65+) | ✅ wiederverwendbar | — |
| Neue Bilder (8) | ❌ müssen generiert werden | Vertex AI Prompts oben |
| Neue Cards (4) | ❌ müssen generiert werden | Vertex AI Prompts oben |
| Timeline | ❌ muss neu gebaut werden | Nach Voice-Generierung |
| Audio Mix | ❌ muss neu gebaut werden | Nach Timeline |
| Render | ❌ muss neu gebaut werden | Nach Audio |
| Endcard | ❌ muss aktualisiert werden | — |
| Captions | ❌ müssen neu generiert werden | Nach Render |
