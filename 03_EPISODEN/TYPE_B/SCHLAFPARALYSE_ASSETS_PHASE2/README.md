# NOESIS — Schlafparalyse Phase 2 Assets

Produktionspaket für EP06–EP08.

## Inhalt

- `asset_manifest.json` — Master-Manifest (49 Einträge)
- `PHASE2_ASSET_LIST.md` — lesbare Liste mit Direktlinks, Rechten und Shot-Einsatz
- `LINK_VERIFICATION.md` — Prüfstatus und Kontextfallen
- `RECON_PROMPTS.md` — KI-Reconstruction-Prompts
- `download_schlafparalyse_assets.py` — Downloader mit MIME/Magic-Byte-Check, SHA-256 und License-Sidecars
- `dry_run.txt` — aktueller Dry-Run

## Rechte-Ampel

- GREEN: 27
- YELLOW: 11
- RED/reference only: 11

## Download

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

Das Script speichert GREEN und YELLOW getrennt, schreibt pro Asset eine `.license.txt`-Datei und erzeugt `_META/MANIFEST.csv`, Credits und einen JSON-Downloadreport. RED-Quellen werden ausschließlich als Referenzlinks abgelegt.

## Redaktionsregel

`GREEN` heißt „Rechtestatus ausreichend dokumentiert“, nicht „beliebig kontextfrei einsetzbar“. Besonders bei späteren Salem-Darstellungen, generischem Labormaterial und UFO-Kontext muss die Beschriftung verhindern, dass ein Ersatzbild wie Primärbeweis wirkt.
