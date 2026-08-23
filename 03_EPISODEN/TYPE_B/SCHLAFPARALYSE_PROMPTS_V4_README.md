# Schlafparalyse — Nano Banana Prompts V4

Dieses Paket bringt EP06–EP08 auf das Produktionsformat der JUNG-V4-/PEAR-Pipeline.

## Paket

`SCHLAFPARALYSE_PROMPTS_V4_REPO_READY.zip`

SHA-256:
`5f414def0f6e9eda90dc35dc111fd152d414e1708c77f486df60d80976fe37d5`

Das ZIP enthält bereits die finalen Repository-Pfade:

- `03_EPISODEN/TYPE_B/EP06_SCHLAFPARALYSE_01/`
- `03_EPISODEN/TYPE_B/EP07_SCHLAFPARALYSE_02/`
- `03_EPISODEN/TYPE_B/EP08_SCHLAFPARALYSE_03/`
- `03_EPISODEN/TYPE_B/SCHLAFPARALYSE_PRODUCTION_READY_LOCK_V4.md`

Pro Episode enthalten:

- `NANOBANANA_GUIDE_V4.md`
- `NANOBANANA_PROMPTS_V4_S1_S2.md`
- `NANOBANANA_PROMPTS_V4_S3_S4.md`
- `NANOBANANA_PROMPTS_V4_S5_S6.md`
- `NANOBANANA_PROMPTS_V4_S7_S8.md`

## Coverage

Jede Folge: **56 MAIN + 8 RESERVE**.

Jeder Main-Prompt folgt dem JUNG-V4-Schema:

```text
IMGxx.png
Referenz: STYLE_...png; VERIFIED_ASSET_FILENAME.jpg
Prompt:
...
```

Die Guides enthalten je drei Style-Anker:

- `STYLE_CINEMATIC_EPxx.png`
- `STYLE_CONCEPTUAL_EPxx.png`
- `STYLE_ARCHIVE_EPxx.png`

## Referenzen

Alle faktischen Dateinamen wurden gegen `SCHLAFPARALYSE_ASSETS_PHASE2/asset_manifest.csv` geprüft.

- Keine `.url.txt`-Datei wird als Bildreferenz an die Bild-KI gegeben.
- Keine PDF wird direkt als Bildreferenz verwendet.
- `GREEN`-Assets sind direkte Referenzen.
- `YELLOW`-Assets sind im Guide als Review-pflichtig markiert.

## Edit-Regel

Originalarchive und Originaldokumente haben Vorrang. Die 64 generierten Bilder pro Episode sind ein Coverage-Pool, kein Zwang, alle Bilder zu verwenden. Besonders EP07 soll weiterhin archivlastig bleiben.

Siehe `SCHLAFPARALYSE_PRODUCTION_READY_LOCK_V4.md` für den finalen Produktions-Lock.