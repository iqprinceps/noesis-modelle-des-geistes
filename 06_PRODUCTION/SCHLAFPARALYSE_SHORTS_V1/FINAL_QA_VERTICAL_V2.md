# Schlafparalyse Shorts — Vertical V2 Final QA

Status: **READY FOR REVIEW / UPLOAD**

## Behobene Fehler

- Alle 42 Standbilder wurden als eigenständige native 9:16-Kompositionen in 1536 × 2752 erzeugt.
- Keine 16:9-Bilder, keine Inset-Karten, keine unscharfen Füllhintergründe und keine Schwarzfelder im Schnitt.
- Zoompan/Ken-Burns wurde vollständig entfernt. Standbilder bleiben geometrisch stabil; Bildwechsel erfolgen mit sauberen harten Schnitten.
- Der einzige Veo-Einsatz ist ein nativer 9:16-Clip mit gesperrter Kamera und realer Motivbewegung in SP06A.
- Acht gedrehte/fehlerhafte Generierungen, ein quer zur Handyachse liegendes Hook-Motiv und eine historisch falsche Gerichtsszene wurden vor dem finalen Export ersetzt.
- George bleibt pro Short eine einzige durchgehende ElevenLabs-Datei; es gibt keine internen Voice-Stitches.

## Technische QA

| Short | Dauer | Bild | Audio-Lautheit | True Peak | Schwarzfelder |
|---|---:|---|---:|---:|---:|
| SP06A_ATEM | 43.918 s | 1080 × 1920, H.264, 24 fps | -14.32 LUFS | -1.48 dBTP | 0 |
| SP06B_RUECKENLAGE | 44.336 s | 1080 × 1920, H.264, 24 fps | -14.44 LUFS | -1.48 dBTP | 0 |
| SP07A_ALBTRAUMWORT | 42.896 s | 1080 × 1920, H.264, 24 fps | -14.45 LUFS | -1.49 dBTP | 0 |
| SP07B_SALEM_ZEUGE | 44.333 s | 1080 × 1920, H.264, 24 fps | -14.39 LUFS | -1.48 dBTP | 0 |
| SP08A_HAT_MAN_HUT | 42.107 s | 1080 × 1920, H.264, 24 fps | -14.48 LUFS | -1.47 dBTP | 0 |
| SP08B_UNSICHTBARE_PERSON | 43.593 s | 1080 × 1920, H.264, 24 fps | -14.51 LUFS | -1.50 dBTP | 0 |

## Sichtprüfung

- Hook-Karten sind kurze Zuschauerformulierungen und vollständig lesbar.
- Untertitel bleiben im mobilen Safe-Bereich.
- Köpfe und für die Handlung relevante Hände sind vollständig im Bild.
- Räume stehen aufrecht; kein Motiv erfordert ein Drehen des Telefons.
- Keine sichtbare Fantasie-Schrift in den final verwendeten Schlüsselmotiven.
- Die Salem-Gerichtsbilder enthalten keine versehentlichen modernen Anzüge mehr.

## Reproduzierbarkeit

- Bildprompts und Generierung: `tools/generate_schlafparalyse_shorts_vertical.py`
- Veo-Jobdefinition: `tools/generate_schlafparalyse_shorts_veo.py`
- Ruckelfreier Vollbild-Renderer: `tools/render_schlafparalyse_shorts_vertical_v2.py`
- Bildkontaktbögen: `tools/build_schlafparalyse_shorts_vertical_contact_sheets.py`
- Maschinenlesbare QA: `06_PRODUCTION/SCHLAFPARALYSE_SHORTS_V1/FINAL_QA_VERTICAL_V2.json`
