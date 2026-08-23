# NOESIS — Schlafparalyse Phase 2 Assets

Produktionspaket für EP06–EP08.

## Inhalt

- `asset_manifest.csv` — kanonisches Download-Manifest mit 49 geprüften Einträgen, Direktlinks, Dateinamen und Zielordnern
- `PHASE2_ASSET_LIST.md` — vollständige lesbare Asset-/Shot-Liste
- `LINK_VERIFICATION.md` — Link-, Lizenz- und Kontextprüfung
- `CREDITS.md` — Attribution und ShareAlike-/Personality-Hinweise
- `RECON_PROMPTS.md` — KI-Reconstruction-Prompts für fehlende/ungeklärte Visuals
- `download_schlafparalyse_assets.py` — ausführbarer Downloader mit MIME/Magic-Byte-Check, SHA-256 und License-Sidecars
- `dry_run.txt` — geprüfter 49-Einträge-Dry-Run

## Rechte-Ampel

- **GREEN: 27** — geprüft und automatisch ladbar
- **YELLOW: 11** — verfügbar, aber Attribution/ShareAlike, Persönlichkeit oder Produktionskontext prüfen
- **RED/reference only: 11** — nur Recherche/Reconstruction, kein automatischer Medien-Download

Damit sind **38 Medienassets automatisch downloadbar** und 11 weitere Quellen bewusst als Reference-only separiert.

## Download

Im Ordner ausführen:

```bash
python3 download_schlafparalyse_assets.py
```

Nur GREEN:

```bash
python3 download_schlafparalyse_assets.py --green-only
```

Nur eine Folge:

```bash
python3 download_schlafparalyse_assets.py --only EP07
```

Eigener Zielordner:

```bash
python3 download_schlafparalyse_assets.py --root ./SCHLAFPARALYSE_MEDIA
```

Das Script speichert GREEN und YELLOW getrennt, erzeugt für jedes geladene Asset eine `.license.txt`-Sidecar und schreibt `_META/MANIFEST.csv`, Credits, Reference-Links und einen JSON-Downloadreport. Vor dem Speichern werden Redirect, MIME-Type und Datei-Signatur geprüft; HTML-/Fehlerseiten werden nicht als Medienasset akzeptiert.

## Wichtige neue Assets

### EP06
- Samuel A. Kinnier Wilson Portrait (PD)
- echtes REM-Polysomnogramm (PD)
- Slow-Wave-PSG als Vergleich (PD)
- zusätzliche hochauflösende Polysomnographie-/Laborbilder

### EP07
- Bridget-Bishop-Primärakten und Richard-Coman-Zeugnis
- weitere Bridget-Bishop-/Salem-Archiv- und Kunstassets
- Füssli, Abildgaard und Malleus/Wellcome-Material
- Library-of-Congress-/Public-Domain-Gerichtsdarstellungen

### EP08
- Art Bell Portrait (CC0)
- 1990er Radiostudio-Referenz
- Radio-Konsole, Fax, Shortwave-Radio und CRT als frei verwendbare Medienwelt
- US-Government-Roswell-/Area-51-Dokumente als klar begrenzter UFO-Kulturkontext

## Redaktionsregel

`GREEN` bedeutet: **Rechtestatus ausreichend dokumentiert**, nicht „beliebig kontextfrei einsetzbar“.

- spätere Salem-Darstellungen immer als spätere Darstellung/Jahr kennzeichnen;
- generische Schlaflaborbilder nie als Takeuchi-Originalversuch ausgeben;
- Burney Relief nicht als sicher identifizierte Lilitu behandeln;
- Roswell/Area 51 nie als Beleg für Alien-Abductions oder Schlafparalyse verwenden;
- KI-Szenen sichtbar als Rekonstruktion behandeln, sobald sonst Archivcharakter suggeriert würde.
