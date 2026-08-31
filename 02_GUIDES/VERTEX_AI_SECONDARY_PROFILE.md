# Vertex AI: zweites lokales Produktionsprofil

## Zweck

Das zweite Google-Cloud-Projekt ist als isoliertes Ausweich- und
Produktionsprofil eingerichtet. Dadurch koennen Bild- und Videogeneratoren das
neue Projekt verwenden, ohne die bisherige Cloud-Konfiguration zu veraendern.

| Einstellung | Wert |
|---|---|
| Projekt | `project-3e0eb782-5078-446c-845` |
| Vertex API | `aiplatform.googleapis.com` — aktiviert |
| Bildmodell | `gemini-3-pro-image` (Nano Banana Pro) |
| Videomodell | `veo-3.1-generate-001` |
| Region | `global` |

Die lokale ADC-Anmeldung liegt ausserhalb des Repositories unter
`%USERPROFILE%\Documents\Codex\_credentials\gcloud-noesis-secondary`. Dieser
Ordner darf weder in Git aufgenommen noch in Logs oder Aufgaben kopiert werden.

## Zugang pruefen

```powershell
pwsh -File tools/run_with_vertex_secondary.ps1 -Check
```

## Bestehenden Generator mit dem neuen Projekt starten

```powershell
pwsh -File tools/run_with_vertex_secondary.ps1 python tools/generate_ep08_vertex.py
```

Alle weiteren Argumente werden an das aufgerufene Programm durchgereicht. Das
Startskript setzt die Projekt- und Zugangsumgebung nur fuer diesen Prozess. Ein
normal gestarteter Generator verwendet weiterhin seine bisherige Umgebung.

## Verifizierter Stand

Am 1. September 2026 wurden beide Modellendpunkte mit leeren, nicht
generierenden Testanfragen geprueft. Beide erreichten das jeweilige Modell und
antworteten erwartungsgemaess mit `INVALID_ARGUMENT` fuer den fehlenden Inhalt.
Damit sind API-Aktivierung, lokale Anmeldung, Projektberechtigung und
Modellrouting bestaetigt, ohne ein Bild oder einen Clip abzurechnen.
