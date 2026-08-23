# EP04A / EP04B — Verified Asset Production Package

**Status:** Phase-2 Produktionspaket  
**Stand:** 2026-08-23  
**Episoden:** EP04A Jung & Kundalini + EP04B Chakra-Genealogie

Dieses Paket ist die kanonische Asset-Sammelstelle für die beiden Folgen des Jung/Chakra-V5-Splits. Es trennt hart zwischen **verwendbarem Originalmaterial**, **review-pflichtigem Material**, **Reference-only** und **KI-Rekonstruktionen**.

## Inhalt

- `asset_manifest.csv` — kanonisches Manifest mit Direktlinks, Rights-Ampel, Zielpfaden, Script-Akten und Shot-Einsatz.
- `ASSET_SHOT_LIST.md` — konkrete Empfehlung, welches Asset in welchem Akt wie eingesetzt werden soll.
- `LINK_VERIFICATION.md` — Prüflog, Erreichbarkeit, Direktlink-Status und bekannte Kontextfallen.
- `CREDITS.md` — Lizenz-/Attributionshinweise.
- `RECON_PROMPTS.md` — scene-specific KI-Reconstruction-Prompts für nicht vorhandene oder nicht nutzbare Originalassets.
- `download_ep04ab_assets.py` — fail-closed Downloader mit Redirect-, MIME-, Magic-Byte-, SHA-256- und License-Sidecar-Prüfung.

## Rights-Ampel

- **GREEN: 27** — Rechtebasis ausreichend klar für den Produktionsworkflow; Attribution trotzdem beibehalten.
- **YELLOW: 9** — nutzbar/recherchiert, aber ShareAlike, Jurisdiktion oder sonstige Rechte-/Kontextprüfung vor finalem Export nötig.
- **RED: 12** — kein automatischer Medieneinsatz. Davon sind 4 externe Reference-only-Fälle und 8 bewusst als Rekonstruktion definierte fehlende Assets.

**Gesamt: 48 Manifest-Einträge.**

## Wichtige redaktionelle Locks

1. Jungs schwarze Schlange von 1913 ist **REKONSTRUKTION**. Historische Kundalini-Grafiken dürfen sie nicht „belegen“.
2. Kein Red-Book-Bild wird als frei verfügbares Produktionsasset behandelt.
3. Das verfügbare, verifizierte Vollscan-Asset von *The Serpent Power* ist eine **1924-Ausgabe**. Im Film nie als Scan der 1919-Erstausgabe ausgeben.
4. Das exakte Zürcher Seminar 1932 hat in diesem Paket **kein verifiziertes Originalfoto**. Seminarraum/Audience = Rekonstruktion, umgeben von echten Orts-/Personenankern.
5. Sir John Woodroffes NPG-Portrait bleibt **RED / Reference-only**.
6. Für Atal Bihari Ghose wurde **kein verifiziert frei nutzbares Portrait** gefunden. Kein erfundenes Archivportrait.
7. Moderne siebenfarbige Chakra-Grafiken dürfen nie zur Illustration des Ṣaṭ-cakra-nirūpaṇa / 1577-Reveals benutzt werden.
8. Historische Bilder mit anderem Jahr werden im Edit entsprechend beschriftet: Hauer 1935, Zürich 1930, Jung-Bibliothek 1950er usw.

## Link-QA

Die Source Pages wurden am 2026-08-23 einzeln gegen aktuelle Quellen geprüft. Bei Wikimedia-Commons-Einträgen wurde nur aufgenommen, was als existierende Datei mit Originaldatei/Metadaten auffindbar war. Die Direktdownload-URLs verwenden den stabilen Commons-Pfad `Special:Redirect/file/...`.

Der Downloader prüft bei der tatsächlichen Ausführung **erneut**:
- Redirect-Ziel,
- HTTP-Erfolg,
- Content-Type,
- Datei-Signatur/Magic Bytes,
- HTML-Fehlerseiten,
- SHA-256.

Er schreibt eine Mediendatei nur, wenn die Antwort zum erwarteten Medientyp passt. RED-Einträge werden nie als Medien geladen.

### Sonderfall Internet Archive

Der 1924-*Serpent Power*-Scan ist auf der Item-Seite als Public Domain ausgewiesen und die PDF-Route ist aufgelöst. Internet Archive leitet große Dateien auf CDN-Ziele um. Deshalb ist das Voll-PDF bewusst `auto_download=0`: Seiten selektiv/manuell ziehen oder den Downloader nach Produktionsbedarf gezielt erweitern.

## Download

Nur Planung/Metadaten:

```bash
python3 download_ep04ab_assets.py --dry-run
```

EP04A:

```bash
python3 download_ep04ab_assets.py --only EP04A
```

EP04B:

```bash
python3 download_ep04ab_assets.py --only EP04B
```

Nur GREEN:

```bash
python3 download_ep04ab_assets.py --green-only
```

Eigener Zielordner:

```bash
python3 download_ep04ab_assets.py --root ./EP04AB_MEDIA
```

## Produktionsregel

**GREEN heißt nicht „kontextfrei einsetzbar“.** Ein historisches Bild kann rechtlich grün und redaktionell trotzdem falsch sein, wenn es das falsche Jahr, den falschen Ort oder eine subjektive Erfahrung als objektiven Beleg suggeriert. Deshalb gelten `script_act` und `shot_use` im Manifest mit.
