# Workspace instructions

## Vertex AI: zweites lokales Profil

Fuer Vertex-Bild- oder Videogenerierung steht ein getrenntes lokales Profil fuer
das Projekt `project-3e0eb782-5078-446c-845` bereit. Es darf die bestehende
globale Google-Cloud-Konfiguration nicht ueberschreiben.

- Bestehende Python-Generatoren ueber
  `tools/run_with_vertex_secondary.ps1` starten.
- Das Startskript setzt `CLOUDSDK_CONFIG`, `GOOGLE_CLOUD_PROJECT` und die
  globale Vertex-Region nur fuer seinen eigenen Prozess und dessen Kinder.
- Zugangsdaten niemals anzeigen, kopieren, committen oder in Produktionslogs
  schreiben.
- Vor einem Lauf kann der Zugang kostenfrei mit
  `pwsh -File tools/run_with_vertex_secondary.ps1 -Check` geprueft werden.
- Nano Banana Pro: `gemini-3-pro-image`, Region `global`.
- Veo: `veo-3.1-generate-001`, Region `global`.

Details und Beispiele: `02_GUIDES/VERTEX_AI_SECONDARY_PROFILE.md`.
