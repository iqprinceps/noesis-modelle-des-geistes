# EP04B V5 — Production Ready Lock

**Folge:** EP04B — Wer hat die Karte gezeichnet, die heute jeder kennt?  
**Status:** **READY FOR PRODUCTION INPUTS**  
**Kanonisches Skript:** `DREHBUCH.md`  
**Individualitätsregel:** `01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md`

## Script / Voice

- finaler Sprechertext + Clean Transcript vorhanden;
- 10 Reveal-/Evidence-Stems, weil die Dokumentketten länger zusammenhängend gelesen werden sollen;
- George / `eleven_multilingual_v2`;
- EP04B-Startprofil: speed `1.07`, stability `0.62`, similarity `0.80`, style `0.05`, seed `24042`;
- individuelle Gap-Startwerte;
- `tools/ep04ab_voice.py EP04B all` baut VO-Master + Forced Alignment.

Auch hier sind Stemzahl und Parameter Ausgangsarchitektur, keine Quote.

## Archive / Rights

EP04B ist bewusst **archive-first**. Das gemeinsame Phase-2-Manifest liefert eine starke GREEN-Route mit historischen Chakra-Bildern, Serpent-Power-Material, Leadbeater-Porträts/-Tafeln, High-Court- und Adyar-Kontext.

Fallbacks sind gelockt:
- Woodroffe-NPG-Porträt bleibt RED/reference-only;
- kein erfundenes Ghose-Porträt;
- 1919 wird bibliografisch gezeigt, echter Vollscan ist 1924;
- moderne Regenbogenkarte illustriert nie 1577.

## Image Generation

Aktuell vorbereitet: **20 MAIN + 4 RESERVE** vollständige Einzelprompts. Die geringere Menge ist Absicht: echte historische Objekte sind hier stärker als KI-Ersatz. Wenn der Archivschnitt bereits trägt, werden einzelne Prompts gar nicht erzeugt.

## Visual / Motion

- source-led Cue Sheet mit 50 Textankern;
- 15 Motion-/Morph-Beats;
- reale historische Quellen behalten Proportionen und sichtbare Nähte;
- kein visueller Kurzschluss `Indien = sechs / Westen = sieben`;
- kein Fake-/Debunk-Stempel;
- zweite Wendung schützt die kulturelle Stärke der Hybridität, ohne historische Herkunft zu verwischen.

## Audio

Eigene EP04B-Architektur:
- 3 trockene Musiklayer + Premix;
- 6 Archiv-/Papier-/Layer-SFX-Stems;
- keine EP04A-Höhlen-/Wasserästhetik;
- `tools/ep04ab_audio_render.py EP04B` liefert bis zur realen VO-Länge; Schluss-/Endscreen-Hold bleibt Editentscheidung.

## Delivery

Thumbnailbase, Einsatz echter historischer Gegenquelle, flexible Endcard, Commands und Produktionsguide sind vorhanden. Technische Exportqualität bleibt verbindlich, kreative Dauer/Shotdichte variabel.

## Bedeutung von READY

Es fehlt keine kreative oder strukturelle Vorentscheidung mehr. Voice, Archiv, Bildgeneration, Motion, Audio und Schnitt können direkt produziert werden. MP3/WAV/Bilder/Motion/SRT/Finalvideo sind Laufzeitoutputs der Pipeline.
