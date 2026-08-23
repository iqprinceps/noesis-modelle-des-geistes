# EP05 V5 — Production Ready Lock

**Folge:** EP05 Jung & Pauli — Der Nobelphysiker und der Zufall  
**Status:** **READY FOR PRODUCTION**  
**Timing:** keine harte Zielminute; Konzentration und natürlicher Voice-Rhythmus haben Vorrang.  
**Referenzstandard:** `01_GLOBAL/00_PRODUKTIONSSTANDARD.md`

## Script / Voice

- `DREHBUCH.md` — V4 FINAL, Retention + Voice Authenticity
- `PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/07_VOICE_SCRIPT_CLEAN_V4.txt`
- 8 vollständige Voice-Source-Stems
- `voice_batch_v4.json`
- Voice: George (`JBFqnCBsd6RMkjVDRZzb`)
- model: `eleven_multilingual_v2`
- speed `1.06`, stability `0.58`, similarity `0.80`, style `0.08`, seed `2402`
- `tools/ep05_voice.py` baut aus den erzeugten Roh-Stems den -18-LUFS-VO-Master und Forced Alignment

## Image Generation

**Production prompt package:**
- `NANOBANANA_GUIDE_V5.md`
- `NANOBANANA_PROMPTS_V5_S1_S2.md`
- `NANOBANANA_PROMPTS_V5_S3_S4.md`
- `NANOBANANA_PROMPTS_V5_S5_S6.md`
- `NANOBANANA_PROMPTS_V5_S7_S8.md`

Coverage:
- **64 MAIN**
- **8 RESERVE**

Promptformat ist Gateway/Pear-kompatibel:
1. exakter Dateiname
2. `Referenz:` mit genau hochzuladenden Dateien
3. vollständiger Prompt für genau dieses Bild

Keine Kurzprompts, keine Pflicht zum manuellen Voranstellen eines Global-Prompts.

## Original Assets / Rights

- `SOURCE_ASSET_DOWNLOAD_MAP_V5.md` — exakte lokale Referenznamen + Source Pages
- `SOURCE_ASSETS_V4.md` — Recherche-/Rechtekontext
- echte freie Originale werden AI-Imitationen vorgezogen
- Jung/Pauli-Briefscan: nur mit geklärter Reproduktionsfreigabe
- `Naturerklärung und Psyche` 1952: echter Scan nur bei geklärter Reproduktion; Default ist bibliografisch korrekte moderne Grafik
- kein Fake-Brief, kein Fake-Buchscan, kein erfundenes Zitat

## Visual Storytelling

- `ASSET_PLAN_V4.md`
- `VISUAL_CUE_SHEET.csv` als Textanker-/Beat-Map
- `MOTION_GRAPHICS_V5.md`

Finaler Schnitt orientiert sich an NOESIS-QA:
- ca. 140–155 Shots
- durchschnittlich ca. 3,5–4,5 s
- kein einzelnes Standbild >9 s
- >=85 Einzelmotive über Archive + AI + Motion
- kein Motiv zweimal im selben Akt
- AI/Rekonstruktion <=65 %, wenn genug echte Archive vorliegen

Diese Zahlen sind **Schnitt-QA**, keine Vorgabe für die Sprecherlänge.

## Audio / Stems

`PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/AUDIO_STEMS_PLAN.md` enthält:
- VO-Stems / VO master
- 3 Musikstems
- World-clock SFX
- Paper/letters SFX
- Beetle/window SFX
- neutral phone notification
- room tones
- sleep-paralysis handoff

Final:
- `-14 LUFS +/-0.5`
- true peak `<= -0.8 dBTP`
- 48 kHz stereo delivery

## Thumbnail / Endcard

`PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/THUMBNAIL_ENDCARD_V5.md`
- primary thumbnail: Pauli + Weltuhr
- vollständiger Thumbnail-Prompt vorhanden
- 246-px Lesbarkeitstest
- Endcard exakt 20 s
- EP06 handoff vorbereitet

## Production Runbook

`PRODUCTION_SUMMARY/EP05_JUNG_PAULI_V4/PRODUCTION_GUIDE_V5.md`

Reihenfolge:
1. Originalquellen downloaden + Lizenzblöcke sichern
2. Style-Refs bereitstellen
3. V5 Bildbatches generieren
4. ElevenLabs Voice-Stems generieren
5. `python tools/ep05_voice.py all`
6. Musik/SFX-Stems bauen
7. Motion-Graphics bauen
8. textankerbasierte Timeline schneiden
9. Captions aus Forced Alignment
10. Endcard / Thumbnail / QA / finaler Export

## Hard Locks

- kein Quantenphysik-Visual, das Synchronizität oder Manifestation als bewiesenen Mechanismus darstellt
- kein künstlich erzeugtes historisches Dokument
- kein melodramatisches Bild zum Suizid von Paulis Mutter
- keine Mystik-/New-Age-Dekoration aus Gewohnheit
- natürliche Voice-Marker wie „okay“ oder „und ja“ nicht zusätzlich in der Produktion vermehren
- der Schnitt darf kürzen, wenn ein visueller Beat nichts trägt; die Voice wird nicht künstlich auf eine Zielminute gedehnt

## Was „READY FOR PRODUCTION“ hier bedeutet

Alle **Inputs, Regeln, Prompttexte, Voicequellen, Stempläne, Quellen-/Rechteentscheidungen und Delivery-Spezifikationen** sind vorhanden. Die eigentlichen MP3/WAV/Bild-/Video-Dateien sind Produktionsoutputs und werden beim Ausführen der beschriebenen Pipeline erzeugt.
