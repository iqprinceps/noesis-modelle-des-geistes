# Zirbeldrüsen-Serie — Asset-Gap-Review — CHECKPOINT 1

## Fassungen und aktuelle Assetautorität

| Folge | Deutsch | Englisch | Aktueller Assetstand |
|---|---|---|---|
| EP09 | `EP09_ZIRBELDRUESE_01/DREHBUCH.md`, V6, ca. 1.223 Wörter | source-locked EN auf `origin/production/ep09-pineal-01-source-lock`, ca. 1.124 Wörter | Branch-Manifest mit 70 Zeilen; nicht auf `master` |
| EP10 | `EP10_ZIRBELDRUESE_02/DREHBUCH.md`, V7, ca. 1.249 Wörter | source-locked EN auf `origin/source-lock/ep10-pineal-02-en`, ca. 1.170 Wörter | Branch-Katalog mit 39 Assets/Quellen; nicht auf `master` |
| EP11 | `EP11_ZIRBELDRUESE_03/DREHBUCH.md`, V6, ca. 1.143 Wörter | aktuelle EN auf `master`, ca. 1.210 Wörter | `VERIFIED_ASSET_REGISTER.csv`, 30 Zeilen; Branch und `master` inhaltlich identisch |
| EP12 | `EP12_ZIRBELDRUESE_04/DREHBUCH.md`, V6, ca. 1.237 Wörter | EN auf Branch und `master` identisch, ca. 1.222 Wörter | Branch-Manifest mit 54 Zeilen; Paket nicht auf `master` |

Die Assetlisten wurden gegen die gesprochenen Beats beider Sprachfassungen geprüft. EP09/EP10 EN enthalten kleine source-lock-Korrekturen gegenüber `master`; bei einer englischen Produktion sind die Branchskripte maßgeblich.

## Technischer Befund vor Bildbewertung

1. Es existieren in den relevanten Verzeichnissen **null** Bild-/PDF-/Clip-Binaries. SHA-256/pHash und Cropvergleich realer Dateien sind nicht möglich.
2. EP09, EP10 und EP12 sind nicht zuverlässig maschinenlesbar. Ungequotete Kommata in URLs/Titeln verschieben Felder. Sichtbar betroffen sind mindestens:
   - EP09: A18, A24, A27, A38, A41, A47, A52, A59, A63, A64, A70;
   - EP10: SRC-001, 003, 006, 011, 012, 028;
   - EP12: CARHART_HARRIS, DESCARTES_PORTRAIT, EYE_PROVIDENCE, BLAVATSKY_PORTRAIT, DMT_EEG.
3. Keine automatische Beschaffung darf auf diesen CSVs laufen, bevor RFC-konformes Quoting, Spaltenzahlprüfung und erlaubte Statuswerte validiert sind.
4. `VERIFIED` beschreibt überwiegend URL-/Inhaltsprüfung, nicht visuelle Datei-QA. Die Acquisition-States stehen weiterhin auf pending/reference/hold.

## Folge-für-Folge-Asset-Gap-Matrix

| Folge | Bereits stark | Ersetzen / ergänzen | Neu recherchieren | Generieren – später, selektiv | Möglicher Clip |
|---|---|---|---|---|---|
| EP09 — Auge im Inneren | echte Tuatara-Fotos; Spencer/Dendy-Platten; Retina, SCN, Pinealis-Histologie; Chang-Studie; Descartes/Elisabeth-Handoff | sechs ähnliche TimVickers-Tuatara-Fotos auf 2 starke Zustände reduzieren; Esoterik-/Shiva-Pool auf kurzen Handoff begrenzen; Study-Paper um menschliche Handlung und klares Databild ergänzen | rechtegeklärtes Makro/Video des parietalen Bereichs; authentischer Studien-/Labor-Kontext; exakte Facsimile-Seite Elisabeth statt Webchrome | Retina→SCN→Pinealis als klare, ruhige Route; Abendlicht-Rekonstruktion; keine generische glühende Drüse | kurzer lebender Tuatara-Moment oder Licht→Abend→Retina-Transformation; echter Mehrwert, kein Pflichtclip |
| EP10 — Sitz der Seele | Descartes-/Elisabeth-Porträts; vier Briefseiten mit AT-Locators; `L'Homme`/`Passions`; historische Nerven-/Ventrikelbilder; moderne Histologie | P2-Esoterikassets fast vollständig an EP11 abgeben; mehrere Descartes-Porträts nicht als künstliche Vielfalt zählen; Kartenbeat sehr kurz | lesbare, vollständige Facsimile-Extrakte; The-Hague-/Exilkontext mit belastbarer Datierung; gegebenenfalls Rechte für einen historischen Schreib-/Raumkontext | Augenwechsel, Briefschreiben und Handheben als 2–3 realistische Handlungsmomente; keine Fake-Briefe | Auge schließen/öffnen als Startframe-Clip; Handheben/Impuls→Bewegung als kurze Transformation |
| EP11 — Wer machte sie zum dritten Auge? | Blavatsky und Leadbeater als Gesichter; Parietalauge-Platten; Ajna/Shiva/Leadbeater-Zuordnung; Dean-Paper als EP12-Brücke | 8–10 Crops derselben Blavatsky-Seiten nicht als 8–10 neue Bilder zählen; ungenannte Spencer/Leydig-Porträts nur verwenden, wenn Voice sie nennt; Descartes nur als Sekunden-Callback | **entscheidend:** rights-clean vollständiger Scan von *Secret Doctrine* Vol. II, p.289 und p.294–301; finaler Woodroffe/Ajna-Master; Leadbeater-EU-Rechte; exakt identifiziertes menschliches Pinealisbild statt Commons-Kategorie | Dreiseiten-Montage Wissenschaft/Ajna/Blavatsky als räumlich klare Komposition; eine Nahtstellen-Animation, keine endlose Dokumentkarte | kurzer, glatter Übergang, in dem drei Originalseiten zueinanderfinden; kein eigener langer Clip nötig |
| EP12 — DMT an der Grenze | Dean-Paper/Fig.1–4; Timmermann-Vergleich; DMT-Struktur; Mikrodialyse-Schema; Strassman-Porträt; getrennte DMT-fMRI- und NDE-EEG-Quellen | 10+ fMRI/EEG/NDE-Grafiken auf maximal 1–2 verständliche Evidenzbilder reduzieren; historische Rückblenden auf 2–3 einzigartige Shots begrenzen; Pineal-Infografik nicht aus EP09 wiederholen | authentischer Dean-/Labor-/Instrumentkontext mit Rechten oder eindeutig generischer, nicht als Dean-Labor behaupteter Originalkontext; Rechte an Forscherporträts; exakter Strassman-Beleg nur falls sichtbares Zitat | Mikrodialyse-Prozess, vier Zustände (mit/ohne Pinealis × vor/nach Herzstillstand), subjektiver Wahrnehmungswechsel; intern sauber als Rekonstruktion geführt | methodischer Clip für Probenfluss/Messung und kurzer Wahrnehmungswechsel; keine OP- oder Flatline-Sensationsbilder |

## Zeilenlogik und inhaltliche Deckung

### EP09

Der biologische Hauptteil ist vollständig gedeckt: Tier, historische Vergleichsanatomie, menschliche Lage, Gewebe, Retina, circadiane Route und Studie. Die größte Lücke liegt nicht in Wissenschaft, sondern in Zuschauerleben und Bewegung. Der Manifestblock A44–A70 überversorgt einen kurzen kulturellen Ausblick mit Chakra-, Shiva- und Theosophieassets. Diese Assets konkurrieren mit EP11, wo sie erzählerisch gebraucht werden. A03–A08 sind verschiedene Dateien, wirken aber wegen gleicher Tierart, gleichem Fotografen und ähnlicher Bildwelt leicht wie Varianten derselben Quelle.

**Priorität:** A01/A02/A03/A10/A14–A22/A26/A27/A31/A37–A42. Danach stoppen und erst die Cue-Lücken prüfen. Nicht pauschal alle 23 MUST-Zeilen verwenden.

### EP10

Die vier Briefe und die historische Körpermaschine decken nahezu jede historische Behauptung. Stark ist, dass vollständige Seitenbereiche festgelegt sind. Schwach ist die Bilddramaturgie: Porträt→Brief→Diagramm kann über Minuten wie eine Präsentation wirken. Augenexperiment, Handbewegung, Schreiben und Antwort müssen die Philosophie körperlich machen. Die P2-Zeilen A33–A39 gehören aus Zuschauersicht EP11; ein einziges einzigartiges Teaserbild genügt.

**Priorität:** A01/A03/A04/A07–A11/A13/A16–A21/A28. A02/A05/A06 sind Varianten, nicht automatisch neue Szenen.

### EP11

Das verifizierte Register ist ehrlich darin, Discovery und Reference nicht als fertige Assets auszugeben. Dadurch ist aber auch klar: Der wichtigste Beweis fehlt noch als finaler Master — die komplette, lesbare 1888er Buchseite. Ohne p.289 und die Sequenz p.294–301 wird die Folge gezwungen, ihre Hauptthese mit Transkriptionswebseiten oder dekorativen Crops zu erzählen. Gleiches gilt abgeschwächt für Leadbeater. Das Assetziel „5 historische Personenporträts“ ist mechanisch; im Voice-Text tragen vor allem Blavatsky und Leadbeater die Handlung.

**Priorität:** Blavatsky-Masterseiten, Blavatsky-Porträt, drei unterschiedliche Parietalauge-Belege, ein Ajna-Original, ein Shiva-Objekt, Leadbeater-Zuordnung, ein kurzer Dean-Teaser.

### EP12

Das Manifest deckt die Claims außergewöhnlich sauber, trennt Rat visual cortex, administered human DMT, NDE-EEG und kulturelle Rückblenden. Visuell ist es trotzdem gefährdet: vier Dean-Figuren plus viele Strukturformeln, fMRI-, EEG- und Near-Death-Grafiken können zu einer Diagrammserie werden. Der Kern braucht nur Dean Fig.4 als Hauptbeweis, Fig.1/2 als Erweiterung und ein getrenntes menschliches Vergleichsbild. Die restlichen Grafiken sind Reserve. Historische Assets aus EP10/11 sollten nicht erneut als volle Montage erscheinen.

**Priorität:** Dean-PDF + Fig.4 + Fig.1, Mikrodialyse-Schema, DMT-Struktur, Strassman-Porträt/Attribution, Timmermann-Tabelle, höchstens eine Human-DMT- und eine Near-Death-Physiologie-Grafik.

## Exakte Cross-Episode-Dubletten im aktuellen Plan

Die folgenden Source-URLs tauchen in mindestens zwei Episoden auf. Ein anderer lokaler Name oder Crop wäre keine neue Zuschauererfahrung:

- `Chakra6.svg`: EP09, EP10, EP12.
- `Leadbeater's Chakras Pictures`: EP09, EP10, EP12.
- `Pineal Gland and Pituitary Body`: EP09, EP10, EP11.
- `Traditional Hindu Diagram of Brow Chakra`: EP09, EP10, EP11.
- Rajasthan Brow Chakra: EP10, EP11.
- `Descartes_diagram.png`: EP09, EP11, EP12.
- Descartes brain section: EP09, EP10.
- Wellcome posterior brain: EP10, EP11.
- Frans-Hals-Descartes-Motiv: EP09, EP10, EP12, zusätzlich thematisch EP16 Vatikan.
- Blavatsky-Rijksmuseum-Porträt: EP11, EP12.
- Dean et al. 2019 / PMC6597727: EP11, EP12.
- Pineal-gland infographic: EP09, EP12.
- Parietalauge Hatteria/Iguana: EP09, EP11.

### Empfohlenes Motiv-Ownership

| Motiv | Owner | Andere Folgen |
|---|---|---|
| lebendes Tuatara + biologische Pinealis | EP09 | EP11 nur andere Art/andere historische Platte |
| Descartes + Elisabeth + Hauptporträts | EP10 | EP09 ein einzigartiger Teaser; EP11 ein Diagramm; EP12 kein Porträtcallback nötig |
| Ajna, Blavatsky, Leadbeater, Shiva | EP11 | EP09/EP10 höchstens je ein anderes Teaserbild; EP12 keine Wiederholung |
| Dean Fig.4, DMT-Labor, Mikrodialyse | EP12 | EP11 nur Paper-Cover/Fig.4-Teaser ohne Reveal |

## Cross-Series-Monotonie

- **Dokumentkarten:** Pineal EP10–EP12 und Vatikan EP14–EP17 konkurrieren alle um Seiten, Markierungen und langsame Push-ins. Jede Folge braucht eine andere Handlung um das Dokument: Briefwechsel, drei Seiten zusammenfügen, Laborprobe, Archivtransport, Druck/Korrektur, gesprochenes Ritual.
- **Descartes:** Pineal EP10 besitzt ihn. Vatikan EP16 sollte ihn primär als Indexeintrag/Buch behandeln, nicht wieder als Philosophenporträt.
- **Galileo:** Vatikan EP14 besitzt Prozessakte/Archiv; EP16 besitzt `Dialogo`/Indexeintrag. Die exakt doppelte Mondskizzen-URL sollte nur eine Folge verwenden.
- **Dunkle Innenräume:** EP12 und Vatikan EP17 dürfen nicht beide auf schwarzem Raum, leuchtender Kopfmitte und Papier beruhen. EP12 braucht Laborweiß/physiologische Übergänge; EP17 menschlichen Raum, liturgische Handlung und historische Kontroverse.
- **Crops/Reframes:** Vollseite→Zoom→Highlight ist eine dokumentarische Sequenz, aber nicht drei verschiedene Assets. In der Dublettenprüfung müssen alle Derivate dieselbe `source_asset_id` tragen.

## Dokument-, Karten-, Lesezeit- und Rechteprüfung

- Vollständige Dokumentseite zuerst, dann Fundstelle; mindestens ein Shot mit Titel/Institution/Datum und ein Shot mit lesbarer relevanter Passage.
- Keine Karte in EP09/EP11/EP12 nötig. EP10 Den Haag nur als kurzer Kontext. Karten dürfen keine Erklärfläche ersetzen.
- Dichte wissenschaftliche Figuren nicht länger statisch zeigen; erst Gesamtfigur, dann 1–2 geführte Variablen. Keine Zuschauerkarte mit internen Claim-/Rights-Labels.
- `REFERENCE_ONLY`, `SOURCE_ONLY`, `HOLD_*` und Discovery-Kategorien sind keine freigegebenen Viewerassets.
- EU-/Deutschland-Rechte nicht allein aus einer US-PD-Markierung ableiten. Leadbeater 1927 und moderne Archivporträts besonders prüfen.
- Erst nach Download: final URL, Rechte-Snapshot, Urheber/Institution, Datum, Dimension/Pagecount, SHA-256, pHash und `derivative_of` erfassen.

## Nächster sinnvoller Schritt

1. Branchpakete auf einen gemeinsamen, reviewbaren Stand bringen.
2. CSVs reparieren und mit einem Schema-Test absichern.
3. Pro Episode eine **ausgewählte** 25–40-Shot-Cuelist erzeugen, nicht weitere Recherchekandidaten sammeln.
4. Serienweites Ownership/Dublettenregister vor jeder Beschaffung anwenden.
5. Erst danach wenige Tier-1-Originale beschaffen und visuell prüfen; generierte Bilder/Clips nur für verbleibende Handlungslücken.

**REVIEW CHECKPOINT 1 — STOP.**
