# Schlafparalyse EP06–EP08 — Full Production Handoff V4

**Status:** READY FOR PRODUCTION INPUTS  
**Standard:** `01_GLOBAL/00_PRODUKTIONSSTANDARD.md`  
**Scope:** EP06 / EP07 / EP08

## Was im Repo gelockt ist

### Editorial / Voice
- finale Voice-Authenticity-Drehbücher EP06–EP08
- Claims Locks
- 8-Akt-Retention-Struktur und CTAs
- `tools/prepare_schlafparalyse_production_inputs.py`
  - extrahiert den kanonischen Sprechertext aus jedem finalen `DREHBUCH.md`
  - erzeugt `07_VOICE_SCRIPT_CLEAN_V4.txt`
  - erzeugt 8 Voice-Source-Stems je Episode
  - erzeugt `voice_batch_v4.json` mit gelockten George-/ElevenLabs-Einstellungen
  - erzeugt Audio-, Motion-, Cue-, Thumbnail-/Endcard- und Production-Guide-Dateien
- `tools/schlafparalyse_voice.py`
  - normalisiert die 8 Voice-Stems
  - baut 48-kHz-PCM24-VO-Master
  - erzeugt ElevenLabs Forced-Alignment-JSON

### Image / Archive
- `SCHLAFPARALYSE_ASSETS_PHASE2/`
  - 49 geprüfte Asset-/Research-Einträge
  - Downloader
  - Rechte-Ampel GREEN / YELLOW / RED
  - Credits / Link Verification / Dry Run
- `SCHLAFPARALYSE_PROMPTS_V4_REPO_READY.zip`
- `tools/unpack_schlafparalyse_prompts_v4.py`
  - SHA-256-verifizierter Unpack
  - sichere Zielpfade
- pro Episode nach Unpack:
  - `NANOBANANA_GUIDE_V4.md`
  - `NANOBANANA_PROMPTS_V4_S1_S2.md`
  - `NANOBANANA_PROMPTS_V4_S3_S4.md`
  - `NANOBANANA_PROMPTS_V4_S5_S6.md`
  - `NANOBANANA_PROMPTS_V4_S7_S8.md`
- 56 MAIN + 8 RESERVE Prompts je Folge
- exakte reale Referenzdateinamen
- keine `.url.txt`- oder PDF-Datei wird als direkte Bildreferenz an die Bild-KI übergeben

## Audio / Stems

Nach `prepare_schlafparalyse_production_inputs.py` existiert pro Episode ein `AUDIO_STEMS_PLAN.md` mit:
- Voice Engine / Voice Settings
- 3 Music Stems: LOW / HARMONIC / NOISE
- episode-spezifischen SFX-/Atmos-Stems
- relativer Act-Energie
- Mix-/Loudness-Lock
- finalem Stem-Exportset

Musik/SFX werden projektintern synthetisiert/gebaut; keine lizenzpflichtige Fremdmusik ist notwendig.

## Visual / Edit Handoff

Nach dem Prep existiert pro Episode:
- `MOTION_GRAPHICS_V4.md`
- `VISUAL_CUE_SHEET.csv`
- `THUMBNAIL_ENDCARD_V4.md`
- `PRODUCTION_GUIDE_V4.md`
- `PRODUCTION_COMMANDS.md`

Edit-Guardrails:
- ca. 140–155 Shots
- Ø ca. 3.5–4.5 s
- kein Still >9 s
- >=85 Einzelmotive
- keine Wiederholung im selben Akt
- 3–5 Motion-Clips/Grafiken
- AI/Reconstruction <=65 %, wo genügend Archiv existiert
- EP07 besonders archivlastig halten

## Einmalige lokale Vorbereitung

Vom Repository-Root:

```bash
git pull origin master
python3 tools/prepare_schlafparalyse_production_inputs.py
```

Der Prep-Schritt entpackt auch das verifizierte Prompt-Paket in EP06/EP07/EP08.

## Quellenassets laden

```bash
cd 03_EPISODEN/TYPE_B/SCHLAFPARALYSE_ASSETS_PHASE2
python3 download_schlafparalyse_assets.py
```

YELLOW-Assets vor Einsatz kurz reviewen. RED bleibt Research-only.

## Voice generieren

Beispiel EP06:

```bash
elevenlabs_cli.py batch --batch-file PRODUCTION_SUMMARY/EP06_SCHLAFPARALYSE_V4/voice/voice_batch_v4.json --execute
python3 tools/schlafparalyse_voice.py EP06 all
```

Analog für EP07 und EP08.

## Runtime Outputs — absichtlich nicht in Git

Diese Dateien entstehen erst in der Produktion und sind **keine fehlenden Preproduction-Inputs**:
- 24 ElevenLabs MP3 Voice-Stems (8 je Folge)
- 3 VO-Master WAVs
- 3 Forced-Alignment JSONs
- generierte Style-Anker und AI-Bilder
- Music-/SFX-WAV-Stems
- Timeline / finaler Schnitt
- SRT / Chapter Timestamps
- Thumbnail-Render
- finale Video-Exports

Diese Outputs hängen von API-Rendering, lokalem ffmpeg, finaler Bildselektion und Schnitt ab und sollen deshalb nicht als statische Binärdateien im Repo vorproduziert werden.

## Finaler Produktionsstatus

**Ja: Die Trilogie kann an Produktion übergeben werden.**

Nach `git pull` + `python3 tools/prepare_schlafparalyse_production_inputs.py` sind alle kreativen und technischen Eingaben vorhanden, um Voice, Bilder, Audio-Stems, Motion, Untertitel, Thumbnail und finalen Edit ohne weitere konzeptionelle Entscheidung zu produzieren.
