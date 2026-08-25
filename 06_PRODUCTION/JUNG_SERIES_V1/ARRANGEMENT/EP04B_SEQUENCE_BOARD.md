# EP04B — Editor Sequence Board

**Episode:** EP04B — Wer hat die Karte gezeichnet, die heute jeder kennt?  
**Status:** Pre-Voice arrangement lock  
**Kanonische Reihenfolge:** `PRODUCTION_SUMMARY/EP04B_CHAKRA_GENEALOGIE_V5/VISUAL_CUE_SHEET_V5.csv`  
**Kanonische Bildprompts:** `NANOBANANA_PROMPTS_V5_S1_S4.md` und `NANOBANANA_PROMPTS_V5_S5_S8.md`  
**Kanonische Motion-Namen:** `MOTION_GRAPHICS_V5.md`

Diese Tafel fixiert Reihenfolge, Bausteinwahl und Rhythmusfunktion vor der Voice-Produktion. Sie enthält bewusst keine Sekunden-Timecodes. Die spätere Forced-Alignment-Spur verschiebt Cue-Grenzen, aber nicht die semantische Reihenfolge.

## Pace-Bänder

| Band | Editor-Funktion vor Voice |
|---|---|
| `DENSE` | schneller Beleg-, Kontrast- oder Reveal-Lauf; mehrere klar unterscheidbare visuelle Zustände vorbereiten |
| `NORMAL` | ein Hauptgedanke mit lesbarer Bild- oder Quellenbewegung |
| `HOLD` | Motiv oder Aussage landen lassen; keine zusätzliche Information in denselben Beat stapeln |
| `RESET` | sichtbarer Moduswechsel; vorherige Bildwelt akustisch und visuell verlassen |

## Sequenztafel

| Cue | Akt | Pace | Voice-Anker | Generierter Bildbaustein | Kanonischer Quellenbaustein | Motion-/Edit-Baustein | Editor-Lock |
|---|---|---|---|---|---|---|---|
| B001 | S1 | `DENSE` | Diese Grafik | `EP04B_IMG001_MODERN_RAINBOW_MAP.png` | — | `B-G01` Modern map reverse | Moderne Karte klar als Gegenwartsobjekt etablieren. |
| B002 | S1 | `DENSE` | Sieben Zentren / sieben Farben | `EP04B_IMG003_MODERN_POSTER_IN_ROOM.png` | — | `B-G01` Modern map reverse | Genau sieben Zentren; Spektralfarben nur auf moderner Ebene. |
| B003 | S1 | `DENSE` | hundert Jahre zurück | `EP04B_IMG002_RAINBOW_LAYER_PEEL.png` | — | `B-G01` Modern map reverse | Regenbogen als oberste Papierschicht abheben; kein magischer Morph. |
| B004 | S1 | `DENSE` | Bilder verändern sich | — | `EP04B_CHAKRA_007`, `EP04B_CHAKRA_008`, `SHARED_CHAKRA_001`, `SHARED_CHAKRA_002` | `B-G02` Many maps | Originale nebeneinander in ihren realen Proportionen zeigen. |
| B005 | S1 | `HOLD` | andere Zahl | — | `EP04B_CHAKRA_008` | `B-G03` SECHS | Sechs-Center-Quelle vollständig enthalten; niedrige Auflösung nur kurz und unverfälscht. |
| B006 | S1 | `HOLD` | Sechs | — | `EP04B_CHAKRA_008` als Quellenresiduum | `B-G03` SECHS | Reduzierte deutsche Typografie; keine Debunk- oder Fake-Ästhetik. |
| B007 | S1 | `NORMAL` | Wer hat die Karte gezeichnet | `EP04B_IMG004_MANY_SYSTEMS_TABLE_BASE.png` | Quellen aus B004 als getrennte Einleger | — | Kein Red-String-/Conspiracy-Board; offene Forschungsfrage halten. |
| B008 | S2 | `NORMAL` | Fehler ... Singular | `EP04B_IMG004_MANY_SYSTEMS_TABLE_BASE.png` | `EP04B_CHAKRA_007`, `EP04B_CHAKRA_008`, `SHARED_CHAKRA_001`, `SHARED_CHAKRA_002` | `B-G02` Many maps | Keine gemeinsame Anatomie erzwingen; Unterschiede sichtbar lassen. |
| B009 | S2 | `DENSE` | Andere Gottheiten / Silben / Lotusblätter | — | `SHARED_CHAKRA_001`, `SHARED_CHAKRA_002`, `SHARED_CHAKRA_003` | Quellen-Detailfahrten | Nur echte Schrift und Formen aus den Originalobjekten; keine KI-Schrift. |
| B010 | S2 | `NORMAL` | Er macht sie sauber | `EP04B_IMG001_MODERN_RAINBOW_MAP.png` | — | `B-G01` Modern map reverse, vorwärts als moderne Ausrichtung | Modernisierung erklären, nicht lächerlich machen. |
| B011 | S3 | `NORMAL` | Ṣaṭ-cakra-nirūpaṇa | `EP04B_IMG005_MANUSCRIPT_MATERIAL_WORLD.png` | `SHARED_BOOK_001` nur als echter späterer Quellenkontext | Quellen-/Material-Composite | Rekonstruktion erzeugt nur Materialwelt; kein erfundenes Sanskrit. |
| B012 | S3 | `NORMAL` | 1577 | — | — | Editor-Typografie `1577` | Datum als moderne Karte; Formulierung bei Bedarf „häufig datiert auf 1577“. |
| B013 | S3 | `HOLD` | Sechs Zentren | — | `EP04B_CHAKRA_008` | `B-G03` SECHS | Historisches Bild vollständig enthalten; Count nicht durch Crop zerstören. |
| B014 | S3 | `NORMAL` | Sahasrara | — | `SHARED_CHAKRA_001` | `B-G04` Six plus Sahasrara | Sahasrara sichtbar absetzen; nicht als „falsches siebtes Chakra“ framen. |
| B015 | S3 | `NORMAL` | Zählen ist bereits Interpretation | `EP04B_IMG006_SIX_PLUS_ABOVE_BASE.png` | `EP04B_CHAKRA_008`, `SHARED_CHAKRA_001` als getrennte Quellencrops | `B-G04` Six plus Sahasrara | Moderne Erklärgrafik klar von historischen Quellen unterscheiden. |
| B016 | S3 | `DENSE` | Sanskritzeichen / Tiere / Formen | — | `SHARED_CHAKRA_001`, `SHARED_CHAKRA_002` | Quellen-Detailfahrten | Source-native Farbe und Proportionen erhalten. |
| B017 | S3 | `NORMAL` | beginnt nun zu reisen | `EP04B_IMG011_BOOK_TRAVEL_PACKAGE.png` | — | `B-G07` Calcutta → London, Anlauf | Kein roter Reiserouten-Strich; Materialtransport statt Abenteuerbild. |
| B018 | S4 | `NORMAL` | 1919 erscheint | — | `SHARED_BOOK_001` | `B-G05` 1919 / 1924 source discipline | Moderne Karte `Erstausgabe 1919`; echter Scan ausdrücklich `Ausgabe 1924`. |
| B019 | S4 | `HOLD` | Arthur Avalon | — | `SHARED_BOOK_001` als Buch-/Namenskontext | `B-G06` Arthur Avalon / network | Pseudonym als Projekt-/Namensknoten, nicht als Spott-Reveal. |
| B020 | S4 | `NORMAL` | Sir John Woodroffe | `EP04B_IMG008_COLONIAL_LEGAL_STUDY_GENERIC.png` | `EP04B_PLACE_005` | `B-G06` + `B-G07` | Kein Fake-Woodroffe-Porträt; High Court und generische Study sauber trennen. |
| B021 | S4 | `NORMAL` | bengalischen Gelehrten | `EP04B_IMG009_WOODROFFE_GHOSE_COLLAB_WIDE.png` | — | `B-G06` Arthur Avalon / network | Beim ersten Einsatz `REKONSTRUKTION`; keine Dienerhierarchie. |
| B022 | S4 | `NORMAL` | Atal Bihari Ghose | `EP04B_IMG010_COLLAB_HANDS_DETAIL.png` | — | `B-G06` Arthur Avalon / network | Kein erfundenes Ghose-Porträt; Name und Wissensrelation tragen den Beat. |
| B023 | S4 | `DENSE` | Gelehrsamkeit / Macht / Freundschaft / Übersetzung | — | `EP04B_PLACE_005`, `SHARED_BOOK_001` | `B-G06` Arthur Avalon / network | Relationstypen getrennt aufbauen; Ghose nicht zum „Assistenten“ reduzieren. |
| B024 | S4 | `NORMAL` | Druck in London | `EP04B_IMG007_LONDON_PRINT_SHOP_1919.png`; Reserve: `EP04B_RSV01_PRINT_TYPE_DETAIL.png` | — | `B-G07` Calcutta → London | Trockener Papier-/Druckprozess; keine lesbaren erfundenen Titel. |
| B025 | S5 | `RESET` | 1927 ... Leadbeater | — | `EP04B_PORTRAIT_001` | Name-/Jahreskarte im Edit | Echten Leadbeater-Hero-Anker setzen; Aufnahme korrekt datieren. |
| B026 | S5 | `NORMAL` | Theosoph und Hellseher | `EP04B_IMG012_THEOSOPHICAL_LECTURE_ROOM_GENERIC.png` optional als Brücke | `EP04B_GROUP_001`, `EP04B_PLACE_001` | Quellenlabels im Edit | London 1901 und Adyar 1890 nicht als Ereignis von 1927 ausgeben. |
| B027 | S5 | `HOLD` | Ich sehe das direkt | `EP04B_IMG013_CLAIRVOYANCE_AUTHORITY_SHIFT_BASE.png` | `EP04B_PORTRAIT_001`, `SHARED_BOOK_001` | `B-G08` Authority changes | Frage nach Autorität stellen; Hellsehen weder bestätigen noch verspotten. |
| B028 | S5 | `HOLD` | Bilder werden einflussreich | — | `EP04B_CHAKRA_002` | `B-G09` Leadbeater plates | Echte Plattentafel wirken lassen; Farben nicht neu kolorieren. |
| B029 | S5 | `DENSE` | Andere Farben / Bewegungen / Funktionen | — | `EP04B_CHAKRA_003`, `EP04B_CHAKRA_004`, `EP04B_CHAKRA_005`, `EP04B_CHAKRA_006` | `B-G09` Leadbeater plates | Einzelplatten nacheinander isolieren; Source-native Farbe bleibt unverändert. |
| B030 | S5 | `NORMAL` | drei Schichten | — | `EP04B_CHAKRA_008`, `SHARED_BOOK_001`, `EP04B_CHAKRA_002` | `B-G10` Mutation stack | Drei Ebenen kurz und lesbar; keine Vorlesungsfolie bauen. |
| B031 | S6 | `DENSE` | eigentliche Mutation | `EP04B_IMG014_EMPTY_ACETATE_MUTATION_STACK.png` | `EP04B_CHAKRA_008`, `EP04B_CHAKRA_007`, `SHARED_CHAKRA_001`, `EP04B_CHAKRA_002` | `B-G10` Mutation stack | Historische Ebenen in echten Proportionen auf separate Acetate setzen. |
| B032 | S6 | `NORMAL` | Farben wichtiger | — | `EP04B_CHAKRA_002`–`EP04B_CHAKRA_006` | `B-G10` Mutation stack | Veränderung schrittweise zeigen; keinen Einzelerfinder behaupten. |
| B033 | S6 | `NORMAL` | Körperfunktionen / Psychologie / Entwicklungsstufen | — | Historische Ebenen aus B031 nur als Unterbau | `B-G12` Layers added | Jede Deutung auf eigenes modernes Acetat; Labels nicht in Quellen drucken. |
| B034 | S6 | `NORMAL` | klare Leiter | `EP04B_IMG015_MODERN_SPECTRUM_INTERFACE.png` | — | `B-G11` Spectrum locks in | Oberfläche sichtbar modern; keine Anatomie- oder Altertumsbehauptung. |
| B035 | S6 | `DENSE` | Rot ... Violett | `EP04B_IMG015_MODERN_SPECTRUM_INTERFACE.png` | — | `B-G11` Spectrum locks in | Genau Rot, Orange, Gelb, Grün, Blau, Indigo, Violett; sauber einrasten lassen. |
| B036 | S6 | `NORMAL` | anschlussfähiger | `EP04B_IMG018_MAP_ABSORBS_CONTEXTS.png` | — | `B-G12` Layers added | Objekte überlagern sich materiell; kein magisches Verschmelzen. |
| B037 | S6 | `HOLD` | Nähte | `EP04B_IMG019_SEAMS_SIDE_VIEW.png` | Quellenlagen aus B031 als getrennte Composites | `B-G10` Mutation stack | Seitenansicht halten; physische Trennkanten sind der Erkenntnisbeat. |
| B038 | S7 | `RESET` | warum fühlt sie sich ... richtig an | `EP04B_IMG016_MODERN_LIFE_YOGA_OFFICE_APP.png` | — | `B-G13` Cultural second turn, Auftakt | Harter Wechsel in normale Gegenwart; kein Wellness-Werbelook. |
| B039 | S7 | `NORMAL` | Yoga / Büro / Therapie / App | `EP04B_IMG016_MODERN_LIFE_YOGA_OFFICE_APP.png`, `EP04B_IMG017_PSYCHOLOGY_LANGUAGE_LAYER.png` | — | `B-G13` Cultural second turn | Alltagskontexte benachbart zeigen, nicht als Beweiskette. |
| B040 | S7 | `NORMAL` | absorbiert die Karte alles | `EP04B_IMG018_MAP_ABSORBS_CONTEXTS.png` | — | `B-G13` Cultural second turn | Sichtbare Überlagerung statt mystischer Fusion. |
| B041 | S7 | `HOLD` | kulturell ... Superkraft | `EP04B_IMG020_FINAL_HEADON_AND_SEAMS.png` | — | `B-G13` Cultural second turn | Funktion kulturell zeigen, nicht metaphysisch bestätigen. |
| B042 | S7 | `NORMAL` | C. G. Jung | — | `EP04A_PORTRAIT_003`, `SHARED_CHAKRA_001` | `B-G14` Jung layer | Jung-Porträt als echtes Archiv; psychologische Deutung nur eine weitere Lage. |
| B043 | S7 | `NORMAL` | Muladhara / Manipura / Anahata | — | `SHARED_CHAKRA_001` als Quellenkontext | `B-G14` Jung layer | Kurze Labels `BODEN`, `AFFEKT`, `ABSTAND`; EP04A nicht erneut erklären. |
| B044 | S8 | `RESET` | dieselbe Karte | `EP04B_IMG001_MODERN_RAINBOW_MAP.png` | — | — | Exakt dasselbe Hero-Objekt wie B001 wiederholen; Erkenntnis, nicht Objekt, hat sich verändert. |
| B045 | S8 | `HOLD` | jetzt sieht man die Nähte | `EP04B_IMG020_FINAL_HEADON_AND_SEAMS.png` | Historische Lagen aus B031 | `B-G15` Final seams | Leichter Kamerawinkelwechsel legt getrennte Kanten frei. |
| B046 | S8 | `NORMAL` | Texte / Übersetzungen / Kolonialgeschichte ... | — | `EP04B_CHAKRA_008`, `SHARED_BOOK_001`, `EP04B_PLACE_005`, `EP04B_CHAKRA_002`, `EP04A_PORTRAIT_003` | `B-G10` + `B-G12` als Quellenlagen-Montage | Keine Checklistenüberladung; Quellenlabels an den Objekten halten. |
| B047 | S8 | `HOLD` | Sind ... deshalb falsch? | `EP04B_IMG020_FINAL_HEADON_AND_SEAMS.png` | — | — | Keine Urteilsgrafik, kein roter Stempel, kein Debunk-Sound. |
| B048 | S8 | `NORMAL` | Symbole funktionieren nicht wie Fossilien | Reserve: `EP04B_RSV04_LAYER_SHADOWS.png` | — | Ruhige Materialfahrt im Edit | Papier-/Acetatschichten in Benutzung; Aussage offen halten. |
| B049 | S8 | `NORMAL` | jede Generation | — | Historische Lagen aus B031 plus moderne Top-Lage | `B-G15` Final seams | Lagen ausrichten, aber nicht verschmelzen; Konstruktion sichtbar lassen. |
| B050 | S8 | `HOLD` | vergessen, dass jemand sie gezeichnet hat | `EP04B_IMG020_FINAL_HEADON_AND_SEAMS.png` | — | `B-G15` Final seams → Schwarz | Head-on beginnen, minimal zur Seite fahren, nach dem Gedanken Schwarz; Endcard erst danach. |

## Wiederkehrende Kontinuitätsobjekte

| Objekt | Erste Setzung | Wiederaufnahme | Lock |
|---|---|---|---|
| Moderne Siebenfarben-Karte | B001 | B002–B003, B010, B034–B036, B041, B044–B050 | Dasselbe klare Hero-Design; exakt sieben Spektralfarben; immer sichtbar modern. |
| Historische Sechs-Center-Quelle | B004–B006 | B008, B013–B015, B030–B031, B046, B049 | Original vollständig enthalten; niemals zu einem modernen Körperdiagramm umzeichnen. |
| Serpent-Power-Quellenwelt | B011 | B014, B016, B018–B019, B023, B030–B033, B042–B043, B046 | 1919 nur Bibliografie; sichtbarer Originalscan ist 1924 und so zu labeln. |
| Acetat-/Nähte-Metapher | B003 | B030–B037, B040–B041, B045–B050 | Physische Trennung und echte Proportionen; kein magischer historischer Evolutionsmorph. |
| Leadbeater-Quellen | B025 | B027–B032, B046 | Nur authentische Porträts/Platten; Farben nie nachkolorieren. |

## Pre-Voice Editor Locks

- Cue-Reihenfolge B001–B050 bleibt unverändert.
- `DENSE`, `NORMAL`, `HOLD` und `RESET` sind Rhythmusbänder, keine Dauerangaben.
- Alle echten Quellen werden vollständig eingepasst; Quellenlabels und Attribution bleiben am Objekt.
- Sichtbare redaktionelle Typografie ist Deutsch. Generierte Frames enthalten keinen lesbaren historischen Text.
- `REKONSTRUKTION` erscheint beim ersten nicht dokumentierten historischen Schauspielbild.
- Keine Quelle wird durch generiertes „Archiv“ ersetzt. Keine Fake-Porträts von Woodroffe oder Ghose.
- Die finale EDL entsteht erst nach Voice-Render und Forced Alignment; diese Tafel bleibt ihr semantischer Shot-Order-Lock.
