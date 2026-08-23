# EP04A / EP04B — Link Verification

**Prüfdatum:** 2026-08-23

## Methodik

- Source Page im Web auf Existenz/Metadaten geprüft.
- Wikimedia Commons nur aufgenommen, wenn die konkrete File-Page bzw. ein aktueller Commons-Eintrag die Datei/Originaldatei ausweist.
- Direktlinks für Commons werden aus dem **exakten** Dateinamen als `Special:Redirect/file/...` erzeugt.
- Rechteampel folgt der Source Page, mit konservativer Verschärfung für ShareAlike, Jurisdiktion und Provenienzprobleme.
- `SHARED_BOOK_001` wurde auf Internet Archive als Public-Domain-Item verifiziert; die PDF-Route ist aufgelöst, bleibt wegen CDN-Redirect/Größe manuell.
- RED/Reconstruction-Einträge haben bewusst keinen Media-Download.
- Der Downloader validiert beim echten Download noch einmal Redirect, MIME und Magic Bytes. Eine HTML-/Fehlerseite wird nicht gespeichert.

## Statusliste

| ID | Ampel | Linkstatus | Direktdownload | QA / Kontext |
|---|---|---|---|---|
| `EP04A_PORTRAIT_001` | YELLOW | Source OK | ja | source ok original present rights jurisdiction review |
| `EP04A_GROUP_001` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04A_PLACE_001` | YELLOW | Source OK | ja | source ok original present license ok sharealike |
| `EP04A_PLACE_002` | YELLOW | Source OK | ja | source ok original present license ok sharealike |
| `EP04A_PLACE_003` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04A_PLACE_004` | YELLOW | Source OK | ja | source ok original present license ok sharealike |
| `EP04A_OBJECT_001` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04A_DOC_001` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04A_PLACE_005` | YELLOW | Source OK | ja | source ok original present license ok sharealike |
| `EP04A_PORTRAIT_002` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04A_PORTRAIT_003` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04A_PLACE_006` | YELLOW | Source OK | ja | source ok original present license ok sharealike |
| `EP04A_PORTRAIT_004` | YELLOW | Source OK | ja | source ok original present license ok sharealike |
| `EP04A_MAP_001` | GREEN | Source OK | ja | source ok original present license ok |
| `SHARED_CHAKRA_001` | GREEN | Source OK | ja | source ok original present license ok |
| `SHARED_CHAKRA_002` | GREEN | Source OK | ja | source ok original present license ok |
| `SHARED_CHAKRA_003` | GREEN | Source OK | ja | source ok original present license ok |
| `SHARED_BOOK_001` | GREEN | Source OK | manuell | source ok download route resolved runtime redirect qa |
| `EP04B_PORTRAIT_001` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_PORTRAIT_002` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_GROUP_001` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_PORTRAIT_003` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_GROUP_002` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_PLACE_001` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_PLACE_002` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_PLACE_003` | YELLOW | Source OK | ja | source ok original present license ok sharealike |
| `EP04B_PLACE_004` | YELLOW | Source OK | ja | source ok original present license ok sharealike |
| `EP04B_PLACE_005` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_CHAKRA_001` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_CHAKRA_002` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_CHAKRA_003` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_CHAKRA_004` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_CHAKRA_005` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_CHAKRA_006` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_CHAKRA_007` | GREEN | Source OK | ja | source ok original present license ok |
| `EP04B_CHAKRA_008` | GREEN | Source OK | ja | source ok original present license ok low res |
| `EP04B_REF_001` | RED | Source OK | nein | source ok reference only metadata conflict |
| `EP04B_REF_002` | RED | Source OK | nein | source ok reference only rights managed |
| `EP04B_REF_003` | RED | Source OK | nein | source ok reference only no reusable portrait |
| `EP04A_REF_001` | RED | Source OK | nein | source ok reference only copyright |
| `EP04A_RECON_001` | RED | — | nein | no source by design reconstruction a-r02 |
| `EP04A_RECON_002` | RED | — | nein | no source by design reconstruction a-r03 |
| `EP04A_RECON_003` | RED | — | nein | no source by design reconstruction a-r04 |
| `EP04A_RECON_004` | RED | — | nein | no source by design reconstruction a-r05 |
| `EP04A_RECON_005` | RED | — | nein | no source by design reconstruction a-r01 |
| `EP04B_RECON_001` | RED | — | nein | no source by design reconstruction b-r06 |
| `EP04B_RECON_002` | RED | — | nein | no source by design reconstruction b-r04 |
| `EP04B_RECON_003` | RED | — | nein | no source by design reconstruction b-r01 |

## Bekannte Sonderfälle

### Jung 1910
Die Commons-Datei ist erreichbar, aber die Source Page warnt explizit vor einer möglichen Abweichung des Public-Domain-Status außerhalb der USA. Deshalb YELLOW.

### *The Serpent Power*
Der verifizierte frei zugängliche Vollscan ist **1924**. Das Drehbuch nennt die Publikation 1919. Im Bild daher entweder `Ausgabe 1924` labeln oder 1919 nur als grafische Datums-/Titelkarte zeigen.

### NPG / Woodroffe
Source Page erreichbar, aber kein frei verwendbarer Produktionsdownload freigegeben. RED.

### Atal Bihari Ghose
Research-Link vorhanden, aber kein verifiziert frei nutzbares Portrait. RED + Reconstruction.

### Red Book
Research-/Ausstellungsseite erreichbar; Kunstseiten werden nicht als freies Asset behandelt. RED.

### Internet-Archive-CDN
Die PDF-Route kann beim Abruf auf einen separaten Archive-CDN-Host umleiten. Diese Weiterleitung ist normal. Der Downloader folgt Redirects, akzeptiert die Datei aber nur, wenn die Antwort als PDF validiert wird.

## Fail-closed-Regel

`download_ep04ab_assets.py` meldet ein Asset als FAILED, sobald HTML, ein falscher Medientyp oder eine nicht passende Dateisignatur zurückkommt. Ein fehlerhafter Direktlink wird dadurch nicht stillschweigend als Medienasset in den Produktionsordner geschrieben.
