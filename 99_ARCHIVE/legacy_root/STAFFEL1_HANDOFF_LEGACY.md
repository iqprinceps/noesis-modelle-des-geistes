# Staffel 1 — Produktionspaket v2

**Stand:** 15.08.2026  
**Aktueller Produktionsblock:** **TYPE A — Akte, Maschine & geheimes Experiment**  
**Status:** Type A vollständig als Produktionsbriefing ausgearbeitet. Type B und C werden bewusst separat produziert.

> **Aktuelle Produktionspriorität:** Für neue Videos gilt
> [`01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md`](01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md).
> Ältere Mengen-, Timing-, Karten-, Clip- und Labelvorgaben sind historische
> Episodenwerte, keine universellen Pflichten.

---

## 1. Was dieses Paket ist

Dieses Paket ist die Übergabe an ein Agententeam für einen faceless, narrator-led YouTube-Kanal über Esoterik, Bewusstseinsmodelle, Grenzforschung und dokumentierte institutionelle Berührungspunkte.

Es enthält **keine fertigen Videodateien** und behauptet keine ungeprüften Assets als lizenzfrei. Es enthält:

- vollständige Longform-Drehbücher für Type A,
- Claims Locks,
- Quellen- und Rechte-Gates,
- Asset-Pläne,
- Voice-/Audio-/Edit-Regeln,
- Shorts,
- Agentenaufgaben,
- eine maschinenlesbare Staffelübersicht.

---

## 2. Redaktioneller Kern

### Drei Archetypen

- **TYPE A — Akte / Maschine / geheimes Experiment**
- **TYPE B — Landkarte / Bewusstsein / Selbsterkenntnis**
- **TYPE C — Kontroverse / wissenschaftliches Rätsel**

Nicht jede Folge braucht eine Behörde. Nicht jede Folge braucht „Kontrolle“. Nicht jede Folge endet unentschieden.

### Vier Evidenzebenen

- `BELEGT`
- `BEHAUPTET`
- `VERMUTET`
- `OFFEN`

Diese Ebenen dienen der internen Redaktion. Sie sind keine dauerhaften
Zuschauerlabels.

### Neue Retention-Regel

Es gibt keinen separaten Disclaimer- oder Gegenbefund-Block. Gegenbelege werden als **Plot** geschrieben: neues Experiment, neue Akte, widersprüchliche Quelle, Kontrolltest oder methodische Wendung.

---

## 3. Type A — Dateien

### EP01 — Kozyrev

`03_EPISODEN/TYPE_A/EP01_KOZYREV/`

- `DREHBUCH.md`
- `CLAIMS_LOCK.md`
- `ASSET_PLAN.md`
- `AGENT_RUNBOOK.md`
- `SHORTS.md`

### EP02 — Gateway

`03_EPISODEN/TYPE_A/EP02_GATEWAY/`

- `DREHBUCH.md`
- `CLAIMS_LOCK.md`
- `ASSET_PLAN.md`
- `AGENT_RUNBOOK.md`
- `SHORTS.md`

### EP03 — Psychotronik

`03_EPISODEN/TYPE_A/EP03_PSYCHOTRONIK/`

- `DREHBUCH.md`
- `CLAIMS_LOCK.md`
- `ASSET_PLAN.md`
- `AGENT_RUNBOOK.md`
- `SHORTS.md`

Blockübersicht: `03_EPISODEN/TYPE_A/TYPE_A_OVERVIEW.md`

---

## 4. Globale Regeln

`01_GLOBAL/00A_PRODUKTIONS_INDIVIDUALITAET.md` — **der verbindliche adaptive Standard.**

Jede neue Folge wird aus Nutzersicht individuell auf Retention, Interaktion,
Bildwirkung, Kosten und Aufwand geprüft. `01_GLOBAL/00_PRODUKTIONSSTANDARD.md`
dokumentiert die EP02-Gateway-V7-Erfahrungen nur noch als Referenz; seine Mengen,
Timings, CTAs und sichtbaren Kennzeichnungen sind keine globale Pflicht.

Referenzfolge zum Nachschlagen: `06_PRODUCTION/EP02_GATEWAY_V7/`

Zwei beratende Prüfwerkzeuge können dabei helfen. Sie liefern standardmäßig
Signale, blockieren aber keine individuelle Produktionsentscheidung:

```bash
python tools/gw_pruefe_text.py <reinschrift.txt>
```

```bash
python tools/gw_wiederholungen.py <timeline.json>
```

Die übrigen Dateien in `01_GLOBAL/` sind Konzeptpapiere aus der Planungsphase.
Bei Widerspruch gilt ausdrücklich `00A_PRODUKTIONS_INDIVIDUALITAET.md`.

## 5. Adaptive Ausführungsreihenfolge

Die genaue Reihenfolge folgt der Episode. Bewährt ist:

1. RESEARCH_AGENT liest `DREHBUCH.md` + `CLAIMS_LOCK.md`.
2. COUNTERPLOT_AGENT prüft, ob die Gegenprüfung als Story trägt.
3. RIGHTS_AGENT arbeitet `ASSET_PLAN.md` ab und schreibt einen Rechtebeleg pro Originalasset.
4. SCRIPT_AGENT legt einen freigegebenen Arbeitskanon an; neue Fakten-, Voice-
   oder Retentionbefunde dürfen ihn gezielt verbessern.
5. VOICE_AGENT vergleicht kurze Auditions und erzeugt danach einen Master plus Pickups.
6. SYNC_AGENT richtet Voice und Cue-Sheet semantisch aufeinander aus.
7. VISUAL_AGENT erzeugt nur die daraus tatsächlich benötigten Archivderivate,
   Bilder, Karten und Clips.
7. AUDIO_AGENT erstellt Musikbett/SFX nach Bible.
8. EDIT_AGENT baut Longform.
9. QC_AGENT prüft Claims, Rechte, Evidenzlabels und Kontinuität.
10. DELIVERY_AGENT erzeugt Longform + Caption-Version + Shorts + Manifeste.

**Kein späterer Agent darf einen früheren Lock still überschreiben.**

---

## 6. Type-A-Reihenfolge

1. **EP01 Kozyrev** — Maschine ohne erzwungene Geheimdienstverbindung.
2. **EP02 Gateway** — dokumentiertes Army-Assessment und mögliche Informationsnutzung.
3. **EP03 Psychotronik** — strategische Bedrohungsanalyse und die Quellenkritik der Akte selbst.

Diese Reihenfolge steigert die institutionelle Ebene, ohne bereits Folge 1 künstlich auf „Behörden“ zu trimmen.

---

## 7. Was vor Veröffentlichung zwingend offen bleibt

- Titel, Beschreibung, Thumbnail und Suchsprache werden je Episode aus
  Zuschauerintention, aktuellem Suchverhalten und dem stärksten ehrlichen
  Versprechen entwickelt. Frühere Titelvorschläge sind Fallbacks, keine Locks.
- Jede konkrete Dokumentseite/Archivdatei durch Rights Gate.
- Keine medizinischen oder physikalischen Claims aus Patenten/Autorenarbeiten als aktuelle Wirksamkeitsbehauptung übernehmen.
- Kein Einsatz-/Kontrollclaim ohne entsprechende Kontrollklasse.
- Keine generierte historische Szene ohne Kennzeichnung als Rekonstruktion.

---

## 8. Nächster Block

Nach Type A: **TYPE B — Landkarte & Bewusstsein**.

Er wird separat gebaut, damit die Landkartenfolgen nicht in die Type-A-Schablone gepresst werden. Danach folgt Type C.
