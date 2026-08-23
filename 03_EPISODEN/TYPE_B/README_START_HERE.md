# Staffel 1 - Produktionspaket Type B

Status: Handoff-produktionsreif fuer Type B.

Type B ist das Landkarten- und Bewusstseinsformat. Es erzeugt Spannung nicht durch eine erzwungene geheime Institution, sondern durch die Frage, ob ein altes oder ungewoehnliches Modell etwas im eigenen Erleben sichtbar macht.

## Enthalten
- EP04 Jung & Chakren
- EP05 Jung & Pauli / Synchronizitaet
- vollstaendige deutsche Sprechertexte
- Claims Lock und Quellen
- Originalasset-Manifest mit Rechteampel
- Visual-Cue-Sheets im 5-8-Sekunden-Raster
- KI-Bildprompts plus mindestens 20 Prozent Reserve
- Agenten-Runbooks und Shorts

## Produktionsreihenfolge
1. Rights Agent prueft Asset Manifest.
2. Research Agent prueft Claims Lock gegen Primar-/Archivquellen.
3. Voice Agent HTML-unescapes den Sprechertext und erzeugt die finale Voice mit derselben Stimme wie Type A.
4. Sync Agent mappt voice_anchor_start/end auf echte Wort-Timestamps.
5. Asset Agent laedt freigegebene Originalassets.
6. Visual Agent rendert MAIN plus Reserve.
7. Editor setzt Originalassets und generierte Visuals gemaess Cue Sheet.
8. QC Agent prueft Evidenzlabels, Rechte, 5-8s Rhythmus und Tonfall.

Wichtig: Dateien mit Status EVIDENCE-ONLY oder AMBER duerfen nicht automatisch als Bildmaterial verwendet werden.
