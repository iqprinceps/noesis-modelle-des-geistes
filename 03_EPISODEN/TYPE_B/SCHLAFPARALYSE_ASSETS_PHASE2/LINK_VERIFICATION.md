# Schlafparalyse — Link & Rights Verification V5

**Stand:** 24.08.2026  
**Status:** CANONICAL INDEX

Die vollständigen Source-URLs und Direktdownloads stehen in den drei kanonisch eingebundenen CSV-Layern:

1. `asset_manifest.csv`
2. `asset_manifest_v5_additions.csv`
3. `asset_manifest_v5_expansion.csv`

`asset_manifest_v5.json` ist der kanonische Einstiegspunkt und dokumentiert die erwarteten Gesamtzahlen.

## Gesamtstatus

- **76 eindeutige Asset-Einträge**
- **46 GREEN**
- **19 YELLOW**
- **11 RED / Reference-only**
- **65 automatisch downloadbare Medienassets**

## Verifikationsregel

### GREEN
Quelle und Rechtestatus sind ausreichend dokumentiert, um das Asset grundsätzlich produktiv zu verwenden. Historischer und redaktioneller Kontext muss trotzdem korrekt bleiben.

### YELLOW
Quelle ist identifiziert und das Asset ist downloadbar, aber vor Final Cut müssen je nach Eintrag Attribution, ShareAlike, Persönlichkeitsrechte oder der konkrete Lizenztext nochmals geprüft werden.

### RED
Nur Research-/Reference-Quelle. Kein automatischer Medien-Download und keine direkte Veröffentlichung.

## Neue V5-Expansion — geprüfte Quellenfamilien

### EP06
- Wikimedia Commons: Sleep EEG Stage 1 / Stage 2
- Wikimedia Commons: Polysomnography trace
- Wikimedia Commons: ambulante Polysomnographie-Patientenreferenz
- Wikimedia Commons: EEG-Cap / Fogo-Locator / 64-Kanal-EEG-Cap

### EP07
- Massachusetts Archives Digital Repository: zusätzliche Salem-Originalakten
- Wikimedia Commons: Salem Village Parsonage Foundation / Proctor’s Ledge
- Wikimedia Commons: Jinn-Manuskript / Yoshitoshi / Kunisada

### EP08
- Wikimedia Commons: BBS-Screenshot
- Wikimedia Commons: Dial-up-Modems, Modem-PCB, CRT, Telefon- und Mikrofonobjekte
- Wikimedia Commons: historischer Electro-Artograph/Fax-Kontext

## Produktionshinweis

Der V5-Downloader runtime-validiert Redirects, MIME-Type/Dateisignatur und bricht bei HTML-/Fehlerseiten nicht den gesamten Batch ab. YELLOW wird standardmäßig mitgeladen, bleibt aber reviewpflichtig. Bei langfristig späterer Veröffentlichung sollten externe Lizenzseiten erneut kurz gegengeprüft werden.
