# EP01B V3 — Link- und Rechteprüfung

**Stand:** 23.08.2026  
**Manifest:** `asset_manifest_v3.csv`  
**Gesamt:** 18 Einträge  
**GREEN:** 3 · **YELLOW:** 13 · **RED:** 2

## Prüfmethodik

- Quellseiten, sichtbare Lizenz-/Rights-Blöcke und verfügbare Originaldateien wurden redaktionell geprüft.
- Commons-Assets verwenden im Manifest entweder `Special:Redirect/file/...` oder den verifizierten `upload.wikimedia.org`-Originalpfad.
- Der gemeinsame NOESIS-Downloader validiert beim tatsächlichen Download Content-Type und Dateisignatur; HTML-/Fehlerpayloads werden nicht als Medien gespeichert.
- YELLOW bedeutet nicht „verboten“, sondern: Attribution, territorialer Status, historische Provenienz oder Reproduktionsrecht muss im Delivery-Workflow beachtet werden.
- RED wird nicht automatisch heruntergeladen und dient ausschliesslich als Research-/Fact-Check-Quelle.

## Verifiziert

- **EP01B_SRC01 — Nikolai Kozyrev portrait, 1959:** YELLOW; Commons-Seite live, 892×631 PNG, dort CC0 1.0 ausgewiesen. Historische Originalurheberschaft ist nicht transparent genug fuer ein bedingungsloses GREEN; deshalb Provenienzseite archivieren.
- **EP01B_SRC02 — Alphonsus LRO:** GREEN; Commons-Seite live, 2878×2878 PNG, NASA/Public-Domain-Status ausgewiesen.
- **EP01B_SRC03 — Alphonsus Apollo 16 AS16-M-2478:** GREEN; Commons-Seite live, 4048×4048 PNG, NASA/Public Domain.
- **EP01B_SRC04 — Pulkovo Observatory 1855:** GREEN; 1087×757 JPG, Public Domain; Autor Evgeny Bernardsky starb 1889.
- **EP01B_SRC05 — Pulkovo 30-inch refractor:** YELLOW; 1296×1792 JPG; Commons weist US-Public-Domain aus und warnt explizit, dass der Status ausserhalb der USA abweichen kann.
- **EP01B_SRC06 — Pulkovo Observatory 2020:** YELLOW; 4160×3120 JPG, CC BY-SA 4.0.
- **EP01B_SRC07 — Crimean Astrophysical Observatory telescope 2005:** YELLOW; 1280×960 JPG, CC BY 2.0.
- **EP01B_SRC08 — Gulag prisoners c.1930:** YELLOW; 1280×854 JPG, Commons Public Domain, historischer Autor unbekannt. Kontext-Risiko hoch: kein Norillag-/Kozyrev-Foto.
- **EP01B_SRC09 — Norilsk central shop 1957:** YELLOW; 737×479 JPG, CC BY 4.0. Nach Kozyrevs Freilassung aufgenommen.
- **EP01B_SRC10 — Norillag/Gulag museum Norilsk 2016:** YELLOW; 2741×2188 JPG, CC BY 2.0. Gegenwarts-/Memory-site, kein historisches Lagerbild.
- **EP01B_SRC11 — Kozyrev mirrors 2014:** YELLOW; 540×721 JPG, CC BY-SA 4.0. Spaeter Device-Anker, kein Kozyrev-eigenes Geraet.
- **EP01B_SRC12 — BIG-G2pf 2015:** YELLOW; 1512×1134 JPG, CC BY-SA 3.0 / GFDL. Spaetere Apparaturvariation.
- **EP01B_SRC13 — ISRIKA mirror 2018:** YELLOW; 385×513 JPG, CC BY-SA 4.0. Spaeter Device-Anker.
- **EP01B_DOC01 — RU2122446C1 PDF:** YELLOW; direkter `patentimages.storage.googleapis.com`-PDF-Link live, `application/pdf`, 8 Seiten. Google Patents zeigt keine separate audiovisuelle Medienlizenz; deshalb fuer Fact Check herunterladen, finale Scan-Nutzung nur nach normalem Legal Review.
- **EP01B_DOC02–DOC04 — Patent figures:** YELLOW; direkte PNG-Endpunkte live. Fuer Geometrie-/Redraw-Referenz freigegeben, finale direkte Reproduktion bleibt Legal-Review-Gate.
- **EP01B_DOC05 — Alter 1959 PASP:** RED; NASA ADS direkter PDF-Zugriff live, `application/pdf`, Copyright-Hinweis der Astronomical Society of the Pacific sichtbar. Research only.
- **EP01B_DOC06 — Kozyrev Properties of Time:** RED; der alternative `astro.puc.cl`-PDF-Link ist live, 16 Seiten. Der derzeitige PDF-Link auf der Zelmanov/PTEP-Seite liefert 404. Reproduktionsrecht des Scans nicht geklaert; Research only.

## Besonders wichtige Kontext-Gates

1. **Alphonsus LRO/Apollo:** freie reale Mondbilder, aber nicht Kozyrevs 1958-Fotoplatte.
2. **Alter-Paper:** belegt die zeitgenoessische Diskussion, darf aber nicht einfach als copyrighted Scan in den Film kopiert werden.
3. **Pulkovo-Bilder:** Institution/Instrumentgeschichte, nicht exakte Dokumentation von Kozyrevs Arbeitsplatz 1936.
4. **Gulag/Norilsk:** kein gefundenes freies Bild zeigt Kozyrev selbst im Lager. Jede Rekonstruktion muss als solche lesbar bleiben.
5. **Spaetere Spiegel:** reale Apparaturen, aber weder Kozyrevs Konstruktion noch Wirksamkeitsnachweis.
6. **Patent:** reale Anmeldung/Konstruktion/Erfinder; keine Evidenz fuer die behauptete Wirkung.

## Downloader

```bash
python 03_EPISODEN/TYPE_A/EP01_KOZYREV/download_ep01b_assets.py --dry-run
python 03_EPISODEN/TYPE_A/EP01_KOZYREV/download_ep01b_assets.py
```

Der Wrapper nutzt `tools/noesis_asset_downloader.py`. GREEN/YELLOW mit `auto_download=1` werden versucht; RED/Reference-only werden als Sidecars abgelegt.
