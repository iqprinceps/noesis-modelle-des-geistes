# EP08 — George-Voice-Paket

**Status:** Text und Pickup-Struktur bereit; Audio noch nicht erzeugt.  
**Umfang:** 27 Takes, 1395 Wörter, reine Sprechzeit rechnerisch etwa 10.3 Minuten beim Planwert 136 Wörter pro Minute. Der verbindliche Serienkorridor liegt bei 132–140 Wörtern pro Minute; reale Zeiten entstehen erst durch George und Forced Alignment.

- `EP08_SPRECHERFASSUNG_GEORGE_FINAL.md` ist die redaktionelle Quelle.
- `EP08_SPRECHTEXT_CLEAN.txt` ist die durchgehende Untertitel-/Alignment-Fassung.
- `source/` enthält genau einen vollständigen Gedanken pro Pickup-Datei.
- `take_manifest.csv` verbindet Takes mit den visuellen Cues V001–V150.
- `elevenlabs_voice_lock.json` hält den bereits etablierten George-Lock fest.
- `voice_batch.json` ist die vorbereitete, noch nicht ausgeführte 27-Take-Batchliste.

Nach der Voice-Erzeugung werden ausschließlich gemessene Wortzeiten in den Sync-Plan übernommen. Sprache wird nie beschleunigt oder zeitlich gestreckt.
