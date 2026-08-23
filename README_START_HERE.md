# Staffel 1 — Produktionspaket v2

**Stand:** 15.08.2026  
**Aktueller Produktionsblock:** **TYPE A — Akte, Maschine & geheimes Experiment**  
**Status:** Type A vollständig als Produktionsbriefing ausgearbeitet. Type B und C werden bewusst separat produziert.

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

`01_GLOBAL/00_PRODUKTIONSSTANDARD.md` — **das verbindliche Rezept.**

Es hält fest, wie EP02 Gateway V7 gebaut wurde, und gilt für alle folgenden
Episoden: Aktaufbau und Hook, die zwei verbotenen Sprachmuster, Bildmengen und
Formatregeln, Einblendungen, Porträtpolitik, Stimme und Musikbett, Auslieferung
und Freigabe.

Referenzfolge zum Nachschlagen: `06_PRODUCTION/EP02_GATEWAY_V7/`

Zwei Prüfwerkzeuge gehören dazu:

```bash
python tools/gw_pruefe_text.py <reinschrift.txt>
```

```bash
python tools/gw_wiederholungen.py <timeline.json>
```

Die übrigen Dateien in `01_GLOBAL/` sind Konzeptpapiere aus der Planungsphase.
Bei Widerspruch gilt der Produktionsstandard.

## 5. Ausführungsreihenfolge

Für **jede** Folge:

1. RESEARCH_AGENT liest `DREHBUCH.md` + `CLAIMS_LOCK.md`.
2. COUNTERPLOT_AGENT prüft, ob die Gegenprüfung als Story trägt.
3. RIGHTS_AGENT arbeitet `ASSET_PLAN.md` ab und schreibt einen Rechtebeleg pro Originalasset.
4. SCRIPT_AGENT friert den finalen Text ein.
5. VISUAL_AGENT erstellt eigene Diagramme und Rekonstruktionsbriefings.
6. VOICE_AGENT erzeugt alle Takes mit derselben Stimme.
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

- Kozyrev-Titel: stärkste Purpose-Formulierung aus Autoren-/Primärquelle vor Master schließen; ansonsten auf den in `CLAIMS_LOCK.md` vorgesehenen sicheren Titel wechseln.
- Jede konkrete Dokumentseite/Archivdatei durch Rights Gate.
- Keine medizinischen oder physikalischen Claims aus Patenten/Autorenarbeiten als aktuelle Wirksamkeitsbehauptung übernehmen.
- Kein Einsatz-/Kontrollclaim ohne entsprechende Kontrollklasse.
- Keine generierte historische Szene ohne Kennzeichnung als Rekonstruktion.

---

## 8. Nächster Block

Nach Type A: **TYPE B — Landkarte & Bewusstsein**.

Er wird separat gebaut, damit die Landkartenfolgen nicht in die Type-A-Schablone gepresst werden. Danach folgt Type C.