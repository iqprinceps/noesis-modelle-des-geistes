# Schlafparalyse V4 — Production Ready Lock

**Folgen:** EP06–EP08  
**Status:** READY FOR PRODUCTION nach Asset-Download + ggf. YELLOW-Review  
**Promptformat:** kanonisch wie EP05 Jung–Pauli, direkt im jeweiligen Episodenordner

## Enthalten pro Folge

Direkt unter `03_EPISODEN/TYPE_B/EP0x_.../`:
- `NANOBANANA_GUIDE_V4.md`
- `NANOBANANA_PROMPTS_V4_S1_S2.md`
- `NANOBANANA_PROMPTS_V4_S3_S4.md`
- `NANOBANANA_PROMPTS_V4_S5_S6.md`
- `NANOBANANA_PROMPTS_V4_S7_S8.md`

Kein ZIP und kein Entpack-Schritt ist für die Produktion erforderlich.

## Individuelle Coverage

- **EP06:** 32 MAIN + 8 RESERVE; stärker rekonstruktiv/psychologisch plus Science-/Location-Originale.
- **EP07:** 20 MAIN + 4 RESERVE; bewusst archive-first, weil Salem-Primärquellen und historische Kunst die Hero-Belege sind.
- **EP08:** 32 MAIN + 8 RESERVE; stärker rekonstruktiv/konzeptuell für frühes Internet, Shadow People, Memory und Hat Man plus echte Art-Bell-/Science-Assets.

Diese Mengen sind vorbereitete Coverage-Pools, keine Quoten. Shotzahl, Bildauswahl und Standzeit folgen der fertigen Voice, dem Beweiswert und der individuellen Dramaturgie.

## Produktionsreihenfolge

1. `SCHLAFPARALYSE_ASSETS_PHASE2/download_schlafparalyse_assets.py` ausführen.
2. YELLOW-Dateien nur nach der im Asset-Paket verlangten Review verwenden.
3. Pro Episode die drei `STYLE_*`-Master aus dem lokalen `NANOBANANA_GUIDE_V4.md` erzeugen.
4. Die lokalen Promptbatches in Story-Reihenfolge abarbeiten und nur die tatsächlich benötigte Coverage auswählen.
5. Originalarchive/Dokumente im Schnitt vor KI-Imitation priorisieren.
6. Historische Rekonstruktionen beim ersten Auftreten als `REKONSTRUKTION` kennzeichnen, wenn sonst Archivcharakter entstehen könnte.
7. Layout vor Production Lock prüfen: `python3 tools/check_image_prompt_layout.py`.

## Referenz-Lock

- `Referenz:` nennt exakte lokale Dateien.
- Research-only `.url.txt`-Dateien werden nicht als Bildreferenz verwendet.
- PDFs werden nicht direkt als Bildreferenz an die Bild-KI gegeben.
- Reale Personen ohne sauber wiederverwendbares Porträt werden nicht fotorealistisch imitiert.
- Originaldokumente/Originalkunst bleiben echte Edit-Layer und werden nicht als KI-Faksimile neu erfunden.

## Qualitäts-Lock

- 16:9 Hauptframes
- keine generischen Neon-/Cyberpunk-Horrorwelten
- keine falschen historischen Dokumente
- keine behaupteten Dämonen/Entitäten als bewiesene Realität
- keine falsche visuelle Genealogie Lilitu/Lilith/Incubus
- Burney Relief nur als vorsichtiger historischer Echo-/Vergleichsanker
- Takeuchi-Labor generisch rekonstruiert, nie als Originalfoto ausgegeben
- Art-Bell-Studio rekonstruiert; CC0-Porträt darf als Identitätsreferenz dienen
- Alien-/Shadow-People-/Hat-Man-Überlappungen nicht als Totalerklärung darstellen
- Diphenhydramin nicht als zuverlässigen Hat-Man-Auslöser visualisieren

## Repo-weite Regel

`01_GLOBAL/00C_IMAGE_PROMPT_STRUCTURE.md` ist ab jetzt maßgeblich: finale Bildprompts müssen direkt im Episodenordner sichtbar sein. `PRODUCTION_SUMMARY` darf spiegeln, ZIPs dürfen exportieren, aber beides darf niemals die einzige Quelle der Produktionsprompts sein.