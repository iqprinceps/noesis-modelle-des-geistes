# NOESIS — Kanonische Struktur für Bildgenerierungs-Prompts

**Status:** globale Produktionsregel  
**Referenz:** EP05 Jung–Pauli

## Harte Strukturregel

Finale Bildgenerierungs-Prompts liegen **immer direkt im Ordner der jeweiligen Episode** unter `03_EPISODEN/.../<EPISODE>/`.

Eine produktionsreife Episode mit generierten Bildern enthält dort sichtbar:

- `NANOBANANA_GUIDE_V*.md`
- ein oder mehrere `NANOBANANA_PROMPTS_V*_S*.md`
- optional `NANOBANANA_PROMPTS.md` als kurzer Pointer auf die kanonischen lokalen Batches

`PRODUCTION_SUMMARY/` darf Kopien oder Handoff-Dokumente enthalten, ist aber **niemals die einzige kanonische Ablage** für die Bildprompts.

ZIP-Dateien dürfen als Export/Backup existieren, aber **niemals die einzige Quelle** der Prompttexte sein. Niemand soll vor der Bildgenerierung ein Paket entpacken müssen, um die Prompts überhaupt lesen zu können.

## Promptformat

Jeder einzelne Bildprompt folgt dem Jung–Pauli-Schema:

```text
EXAKTER_DATEINAME.png
Referenz: STYLE_...png; EXAKTE_FAKTISCHE_REFERENZ.jpg
Prompt:
<vollständiger, eigenständig nutzbarer Prompt für genau dieses Bild>
```

Regeln:

- Jeder Prompt ist vollständig; kein versteckter Global-Prompt muss manuell vorangestellt werden.
- Unter `Referenz:` stehen nur tatsächlich benötigte, exakt benannte Dateien.
- `Referenz: Keine` bedeutet keine Referenzdatei.
- Reale Personen nur mit sauberer Identitätsreferenz erkennbar generieren.
- Originalarchive und echte Dokumente bleiben Originale und werden nicht als KI-Faksimile nachgebaut.
- Rekonstruktionen dürfen nicht wie angebliches Archivmaterial ausgegeben werden.
- Batchanzahl, Bildmenge und Aufteilung S1–S8 bleiben **episodenspezifisch**. Die Struktur ist standardisiert, nicht die kreative Menge.

## Production-ready Gate

Eine Folge darf für Bildgenerierung nicht als `READY` gelten, wenn:

1. der Guide nur außerhalb des Episodenordners liegt,
2. die vollständigen Promptbatches nur in einem ZIP liegen,
3. ein Batch nur Kurzbeschreibungen statt vollständiger Einzelprompts enthält,
4. Referenzdateinamen nicht gegen das Assetpaket geprüft wurden.

Prüftool:

```bash
python3 tools/check_image_prompt_layout.py
```

Das Tool prüft die Ablagestruktur. Inhaltliche Quellen-/Rechte-QA bleibt zusätzlich verpflichtend.
