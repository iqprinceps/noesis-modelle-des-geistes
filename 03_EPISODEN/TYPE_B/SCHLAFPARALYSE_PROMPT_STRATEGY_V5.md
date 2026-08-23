# Schlafparalyse — Prompt Strategy V5

**Ziel:** hohe NOESIS-Bilddichte beibehalten, AI aber episodenindividuell einsetzen.

## Kanonische direkte Prompt-Pools

- EP06: **32 MAIN + 8 RESERVE**
- EP07: **20 MAIN + 4 RESERVE**
- EP08: **32 MAIN + 8 RESERVE**

Die vollständigen Prompts liegen direkt in den jeweiligen Episodenordnern. Es gibt keinen ZIP-only-Workflow mehr.

## Wichtige Unterscheidung

**Promptanzahl != Shotanzahl.**

Der finale Schnitt erreicht 149/146/150 Shots durch die Kombination aus:
- echten Originalassets;
- semantisch unterschiedlichen Source-Crops;
- Recon/AI;
- Motion/Diagramm/Typografie.

Ein AI-Basisbild darf höchstens zwei Shots liefern und nur, wenn die Ausschnitte tatsächlich verschiedene Sprecherinformationen visualisieren. Ein bloßer Zoom/Pan ist kein zweites Motiv.

## EP06

AI priorisieren:
- Schlafzimmer-POV / Bewegungsunfähigkeit
- subtile Präsenz / Tür / Flur / Bettende
- Intruder / Incubus / vestibuläre Familien
- Körper-vs-Besucher

AI reduzieren:
- generisches Schlaflabor
- austauschbare Gehirn-/Neuronenbilder
- mehrfach fast identische Schatten-am-Bett-Kompositionen

Science-/Lab-Beats zuerst aus echten PSG-/Sleep-Lab-Originalen und nativer Motion bauen.

## EP07

Der kleinere AI-Pool ist bewusst korrekt.

AI priorisieren:
- sparsame räumliche Salem-Rekonstruktion
- einzelne Brustdruck-/Nachtmahr-Situationen
- subjektive Kultur-/Erwartungsbeats

AI vermeiden:
- generische Hexenportraits
- Dämonengalerien ohne Quelle
- pseudo-ethnografische Jinn/Kanashibari/Mahr-Bilder
- KI-Faksimiles vorhandener Akten/Gemälde

Dichte stattdessen über Originalakte, Salem-Karte, Füssli/Abildgaard-Details, Malleus-/Bull-Crops, Kulturkarte und Studien-Motion erzeugen.

## EP08

AI priorisieren:
- Shadow People
- Hat-Man-Reveal: Rand → Hutkante → Distanz → Hero
- zurückhaltender Abduction-Overlap
- Erwartungs-/Feedbackwelt
- markenfreie frühe-Web-/Interface-Rekonstruktion

AI reduzieren:
- redundante schwarze Silhouetten
- generische Grey-Aliens
- Cyberpunk-/Neon-Netzwerke
- AI-Radio/PC, wenn echte Periodentechnik vorhanden ist

## Wann neue Prompts ergänzt werden

Nicht vorsorglich auf eine künstliche Gleichzahl auffüllen. Erst:

```bash
python3 tools/check_schlafparalyse_visual_coverage_v5.py EP06
```

Wenn der Checker bzw. der konkrete Sprecherbeat eine echte Lücke zeigt, wird **für genau diese Lücke** ein zusätzlicher vollständiger Prompt im Episodenordner ergänzt. So wachsen EP06/EP07/EP08 nur dort, wo der Schnitt es tatsächlich braucht.

## Qualitätsgate für einen zusätzlichen Prompt

Ein neuer Prompt muss mindestens eine Funktion erfüllen:
- neuen Sprecherinhalt konkret bebildern;
- sichtbare Wiederholung verhindern;
- neuen Raum/Winkel/Informationswert liefern;
- subjektive Erfahrung verständlicher machen;
- darf keinen stärkeren Originalbeleg verdrängen.

Sonst ist er Füllmaterial und wird nicht angelegt.
