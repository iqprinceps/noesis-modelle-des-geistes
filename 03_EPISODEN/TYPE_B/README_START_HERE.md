# Staffel 1 — Produktionspaket Type B

**Status:** Handoff-produktionsreif für Type B.

## Zuerst lesen

Die verbindliche Episoden- und Serienzuordnung steht in **`EPISODE_MAP.md`**. Diese Datei ist die Source of Truth, wenn ältere Ordnernamen oder Commits uneindeutig wirken.

## Kanonische Episodenstruktur

### Jung / Chakra — V5 Split
- **EP04A — Jung & Kundalini: Die Schlange im Inneren**  
  Repo-Pfad bleibt aus Kompatibilitätsgründen `EP04_JUNG_CHAKREN/`.  
  Kanonisches Skript: `DREHBUCH_V5.md`.
- **EP04B — Chakra-Genealogie**  
  Repo-Pfad: `EP04B_CHAKRA_GENEALOGIE/`.  
  Zweite Folge aus dem EP04-V5-Split, aber standalone publizierbar und öffentlich nicht zwingend als „Teil 2“ zu labeln.

**Gemeinsames verifiziertes Asset-Paket:** `EP04A_EP04B_ASSETS_PHASE2/`  
Dort liegen kanonisches Download-Manifest, Direktlinks, Rights-Ampel, Shot-Mapping, Link-QA, Credits, Reconstruction-Prompts und fail-closed Downloader.

### Eigenständige Episode
- **EP05 — Jung & Pauli / Synchronizität**  
  Repo-Pfad: `EP05_JUNG_PAULI/`.  
  **Nicht Teil von EP04A/EP04B. Keine EP04C.** Jung ist hier eine narrative Brücke, keine Serienzuordnung.

### Schlafparalyse — explizite Trilogie
- **EP06 — Schlafparalyse I**
- **EP07 — Schlafparalyse II**
- **EP08 — Schlafparalyse III**

Gemeinsamer Plan: `SCHLAFPARALYSE_SERIE_V2_RETENTION_VISUAL_PLAN.md`  
Gemeinsames Asset-Paket: `SCHLAFPARALYSE_ASSETS_PHASE2/`

## Type-B-Prinzip

Type B ist das Landkarten- und Bewusstseinsformat. Es erzeugt Spannung nicht durch eine erzwungene geheime Institution, sondern durch die Frage, ob ein altes oder ungewöhnliches Modell etwas im eigenen Erleben sichtbar macht.

## Produktionsreihenfolge

1. Rights Agent prüft Asset Manifest.
2. Research Agent prüft Claims Lock gegen Primär-/Archivquellen.
3. Voice Agent erzeugt die finale Voice mit derselben Stimme wie Type A.
4. Sync Agent mappt Voice-Anker auf echte Wort-Timestamps.
5. Asset Agent lädt freigegebene Originalassets.
6. Visual Agent rendert MAIN plus Reserve.
7. Editor setzt Originalassets und generierte Visuals gemäß Cue Sheet.
8. QC Agent prüft Evidenzlabels, Rechte, Rhythmus und Tonfall.

**Wichtig:** Dateien mit Status `EVIDENCE-ONLY`, `AMBER`, `YELLOW` oder `RED` dürfen nicht automatisch als final freigegebenes Bildmaterial behandelt werden. Für EP04A/EP04B gilt die Ampellogik des gemeinsamen Phase-2-Pakets.

## Naming Lock

Ab jetzt in neuen Commits und Handoffs konsequent **EP04A**, **EP04B**, **EP05**, **EP06**, **EP07**, **EP08** verwenden. Serienbeziehungen niemals allein aus wiederkehrenden Personen oder benachbarten Episodennummern ableiten.
