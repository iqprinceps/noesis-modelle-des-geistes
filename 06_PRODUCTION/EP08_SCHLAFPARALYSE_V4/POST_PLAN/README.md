# EP08 — Voice-, Bild- und Tonübergabe vor der Generierung

Verbindliche Serienregeln: `../../SCHLAFPARALYSE_EP06-EP08_SYNC_AND_EDIT_LOCK.md`.

Diese Fassung korrigiert die Schwächen des EP04A-Erstschnitts bereits in der Planung:

- exakt 150 visuelle Slots statt eines zu kleinen Cue-Pools;
- 58 Original-/Quellenslots, 57 Rekonstruktionsslots und 35 Motion-/Karten-Slots;
- etwa 31 % geplante Quellenlaufzeit und 9 % Kartenlaufzeit;
- keine identischen direkten Bildwiederholungen;
- jedes fertige Frame maximal einmal im Plan;
- vier Transformationsclips, jeder genau einmal;
- Karten und Quellen immer statisch und lesbar;
- generierte Stills locked oder höchstens Micro-Push 1,025;
- keine aggressiven Schwenks, diagonalen Fahrten oder Ken-Burns-Ersatzclips.

## Verbindliche Dateien

- `../VOICE_EP08/EP08_SPRECHERFASSUNG_GEORGE_FINAL.md` — finaler menschlich geglätteter Sprechertext.
- `../VOICE_EP08/source/` — 27 einzeln nachnehmbare George-Takes.
- `../VOICE_EP08/take_manifest.csv` — Take-Länge, Bild-Cues und Regiehinweis.
- `EP08_VOICE_VISUAL_SYNC_PLAN.csv` — 150 Textanker mit Bild, Quelle, Clip/Karte, SFX und Bewegungsregel.
- `EP08_REPEAT_ORIGINAL_AUDIT.md` — Mengen-, Laufzeit- und Wiederholungsprüfung.
- `EP08_MISSING_ASSETS_AND_PROMPTS.md` — Quellenbeschaffung, Originalerweiterung und vier optionale 2K-Prompts.
- `EP08_SOUND_DESIGN_PLAN.md` — Musik-, SFX- und Mixlock.
- `../ORIGINAL_EXPANSIONS/` — 50 bereits gerenderte statische 2K-Ansichten aus vorhandenen Originalassets samt Manifest und Kontaktbögen.
- `../SEMANTIC_CUTS/` — 23 bereits gerenderte 2K-Reframes für auseinanderliegende Textanker; keine Live-Zooms.

## Nächster technischer Schritt

George wird mit dem vorhandenen ElevenLabs-Lock erzeugt. Danach liefert Forced Alignment die realen Wortzeiten. Die 150 Cues werden an ihren `voice_anchor` gebunden; die Zielsekunden sind nur Budgets und dürfen nicht durch Beschleunigen der Sprache erzwungen werden.
