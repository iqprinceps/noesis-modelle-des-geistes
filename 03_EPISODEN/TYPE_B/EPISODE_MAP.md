# Type B — Kanonische Episodenkarte

**Status:** Source of Truth für Episoden-IDs, Serienzuordnung und Produktionspfade.  
**Stand:** 2026-08-28

Wenn Ordnernamen, ältere Readmes oder Commit-Texte widersprüchlich wirken, gilt diese Datei.

## Kanonische Struktur

| ID | Arbeitstitel / Thema | Repo-Pfad | Serien-/Blockstatus | Kanonisches Skript |
|---|---|---|---|---|
| **EP04A** | Jung & Kundalini — Die Schlange im Inneren | `EP04_JUNG_CHAKREN/` | **Jung/Chakra V5 Split — A** | `DREHBUCH_V5.md` |
| **EP04B** | Chakra-Genealogie — Wer hat die Karte gezeichnet? | `EP04B_CHAKRA_GENEALOGIE/` | **Jung/Chakra V5 Split — B / eigenständig publizierbar** | `DREHBUCH.md` |
| **EP05** | Jung & Pauli / Synchronizität | `EP05_JUNG_PAULI/` | **eigenständige Episode** | `DREHBUCH.md` |
| **EP06** | Schlafparalyse I | `EP06_SCHLAFPARALYSE_01/` | **Schlafparalyse-Serie 1/3** | `DREHBUCH.md` |
| **EP07** | Schlafparalyse II | `EP07_SCHLAFPARALYSE_02/` | **Schlafparalyse-Serie 2/3** | `DREHBUCH.md` |
| **EP08** | Schlafparalyse III | `EP08_SCHLAFPARALYSE_03/` | **Schlafparalyse-Serie 3/3** | `DREHBUCH.md` |
| **EP09** | Zirbeldrüse I — Das Auge im Inneren | `EP09_ZIRBELDRUESE_01/` | **Zirbeldrüse-Serie 1/4** | `DREHBUCH.md` |
| **EP10** | Zirbeldrüse II — Der Sitz der Seele | `EP10_ZIRBELDRUESE_02/` | **Zirbeldrüse-Serie 2/4** | `DREHBUCH.md` (geplant) |
| **EP11** | Zirbeldrüse III — Wer machte sie zum dritten Auge? | `EP11_ZIRBELDRUESE_03/` | **Zirbeldrüse-Serie 3/4** | `DREHBUCH.md` (geplant) |
| **EP12** | Zirbeldrüse IV — DMT an der Grenze | `EP12_ZIRBELDRUESE_04/` | **Zirbeldrüse-Serie 4/4** | `DREHBUCH.md` (geplant) |

## EP04A / EP04B — was der V5-Split bedeutet

Der Commit `bf29829dc12bf4ed0673fdbc36adfeaedc7dd76f` trägt bewusst den Titel **“Merge EP04 V5 FINAL split”**. Er bündelt zwei getrennte Produktionspakete:

- **EP04A:** Jung, Kundalini, innere Bilder, psychologische Chakra-Lesart.
- **EP04B:** historische Genealogie der Chakra-Karte.

Beide entstanden aus dem EP04-V5-Split und gehören redaktionell zum selben **Jung/Chakra-Themenblock**. Trotzdem ist EP04B so gebaut, dass sie **allein funktioniert** und öffentlich nicht zwingend als „Teil 2“ gelabelt werden muss.

Der bestehende Ordner `EP04_JUNG_CHAKREN/` wird aus Kompatibilitätsgründen **nicht umbenannt**. Seine kanonische Episoden-ID ist ab jetzt **EP04A**.

## EP05 — klare Abgrenzung

**EP05 ist nicht Teil des EP04A/EP04B-Splits.**

EP05 darf über Jung narrativ an EP04A anschließen, ist aber:

- keine EP04C,
- kein dritter Teil der Chakra-Folgen,
- keine Fortsetzung von EP04B,
- eine eigenständige Episode zum Themenkomplex **Jung & Pauli / Synchronizität**.

Eine wiederkehrende Person — hier Jung — definiert im Repo **keine Serie**. Serienzuordnung wird nur über diese Episodenkarte und explizite Serienpläne festgelegt.

## Schlafparalyse — echte Serie

EP06, EP07 und EP08 bilden eine explizite dreiteilige Serie. Der gemeinsame Serienplan ist:

`SCHLAFPARALYSE_SERIE_V2_RETENTION_VISUAL_PLAN.md`

Gemeinsame Assets liegen in:

`SCHLAFPARALYSE_ASSETS_PHASE2/`

## Zirbeldrüse — neue vierteilige Miniserie

EP09 bis EP12 bilden eine explizite vierteilige Serie. Der gemeinsame redaktionelle Serienplan ist:

`ZIRBELDRUESE_SERIE_V1_RETENTION_PLAN.md`

Die Progression lautet:

1. EP09: reales Parietalauge, Pinealkomplex, Licht und Melatonin;
2. EP10: Descartes und der „Sitz der Seele“;
3. EP11: historische Genealogie von Pinealis und „drittem Auge“;
4. EP12: endogenes DMT, Pinealis-Hypothese und Evidenzgrenzen.

## Regeln für neue Commits und Produktionsdateien

1. EP04-Jung/Kundalini in Commit-Titeln als **EP04A** bezeichnen.
2. Chakra-Genealogie immer als **EP04B** bezeichnen.
3. EP05 immer als **EP05** oder **EP05 Jung & Pauli** bezeichnen; nie als Teil des EP04-Splits.
4. „Serie“, „Teil 1/2/3/4“ oder ähnliche Begriffe nur verwenden, wenn die Serienzuordnung hier explizit steht.
5. Bei alten Produktionspfaden nicht allein aus dem Ordnernamen auf die Serienlogik schließen.
6. Alte Skriptversionen in `EP04_JUNG_CHAKREN/` (`DREHBUCH.md`, V2–V4) sind Historie; für Produktion ist **`DREHBUCH_V5.md`** maßgeblich.
7. EP09–EP12 folgen dem gemeinsamen Zirbeldrüsen-Serienplan, behalten aber jeweils eigene Claims-, Quellen-, Visual- und Asset-Locks.

## Kurzform für Agenten

> EP04A + EP04B = gemeinsamer Jung/Chakra-V5-Split, zwei getrennte Folgen. EP04B ist standalone publizierbar. EP05 = eigenständige Jung/Pauli-Folge. EP06–EP08 = Schlafparalyse-Trilogie. EP09–EP12 = Zirbeldrüsen-Miniserie.
