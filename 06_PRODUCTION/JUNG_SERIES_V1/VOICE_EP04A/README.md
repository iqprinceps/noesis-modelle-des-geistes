# EP04A — fertige George-Voice-Übergabe

**Status: fertig erzeugt und technisch geprüft.** Die 26 Takes verwenden den bestehenden ElevenLabs-Sprecher **George**. Sie sind bewusst an vollständigen Gedanken, Szenenwechseln und natürlichen Atemstellen getrennt. Dadurch kann ein einzelner problematischer Abschnitt neu erzeugt werden, ohne die Episode oder eine lange Szene erneut einzusprechen.

Der Sprecherlauf dauert inklusive Montagepausen **10:13,436**. Die WAV-Ausgabe ist mono, 48 kHz, PCM24, auf −18 LUFS normalisiert und auf −2 dBTP begrenzt. Es wurde nichts zeitlich gestreckt.

## Verbindliche Dateien

- `EP04A_SPRECHERFASSUNG_FINAL.md`: Take-Reihenfolge, Bild-Cues und Regiehinweise.
- `source/`: exakt zu sprechende Texte, jeweils eine Datei pro Pickup-Take.
- `voice_batch.json`: vorbereitete Batch-Liste mit dem bestehenden George-Lock.
- `elevenlabs_voice_lock.json`: unveränderte Voice-ID und Einstellungen der V5-Produktion.
- `raw_stems/`: 26 originale ElevenLabs-MP3-Takes samt API-Nachweis und Hashes.
- `final_stems_wav/`: 26 schnittfertige WAV-Pickups.
- `master/EP04A_GEORGE_VO_MASTER.wav`: vollständiger Voice-Master mit den vorgesehenen Übergängen.
- `master/stem_report.json`: exakte Start-/Endzeit, Dauer und Hash jedes Takes.
- `alignment/EP04A_GEORGE_VO_ALIGNMENT.json`: Wort- und Zeichentiming aus dem fertigen Master.
- `sync/EP04A_VOICE_VISUAL_SYNC.csv`: 62 Bild-Cues mit Take-, Zeit-, Karten-, Originalasset- und Still-Zuordnung.
- `qa/EP04A_AUDIO_TECH_QA.json`: Dekodierung, Lautheit, Peak und Pausenprüfung.
- `qa/EP04A_GEORGE_SCRIBE_QA.json`: unabhängige Rücktranskription zur Vollständigkeitskontrolle.

## Prüfergebnis

- 26 von 26 Takes vorhanden und dekodierbar.
- 62 von 62 Bild-Cues im Sync-Ledger erfasst; drei Übergangsbilder laufen absichtlich über zwei benachbarte Takes.
- Rücktranskription: 99,17 % Wortfolgen-Übereinstimmung. Die wenigen formalen Unterschiede sind nur ausgeschriebene Jahreszahlen und die Getrenntschreibung von „Chakrenbilder“.
- Die Eigennamen und Kernbegriffe Jung, Kundalini, Muladhara, Manipura, Anahata, Sahasrara, Pauli, Philemon und Ṣaṭ-cakra-nirūpaṇa wurden erkannt.
- Keine ungewollte Binnenpause über 1,5 Sekunden.

## Schnittregel

- Takes werden in nummerierter Reihenfolge montiert.
- Satzanfänge und -enden werden nie über zwei Dateien geteilt.
- Die vorgesehenen Abstände stehen in `voice_timing.json` und sind bereits im Master enthalten.
- Nach `EP04A_TAKE_018_ZWEI_SEKUNDEN.txt` werden im Schnitt echte zwei Sekunden Nicht-Handlung gesetzt. Diese Pause wird nicht durch künstlich verlangsamte Sprache erzeugt.
- Bei einer Korrektur nur den betroffenen Take mit identischer Voice-ID, Modellkonfiguration und Seed-Strategie neu erzeugen.
