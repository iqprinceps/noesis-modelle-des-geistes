# Schlafparalyse-Shorts — V4 Final QA

Erzeugt von `tools/qa_schlafparalyse_shorts_v4_report.py` aus den
`final_v4/QA_REPORT.json` der einzelnen Shorts.

## Technik

| Short | Dauer | Bild | Lautheit | True Peak | Schwarz |
|---|---:|---|---:|---:|---:|
| SP06A_ATEM | 42.28 s | 1080x1920, 24 fps | -14.7 LUFS | -1.5 dBTP | 0 |
| SP06B_RUECKENLAGE | 42.25 s | 1080x1920, 24 fps | -14.8 LUFS | -1.5 dBTP | 0 |
| SP07A_ALBTRAUMWORT | 42.71 s | 1080x1920, 24 fps | -14.7 LUFS | -1.5 dBTP | 0 |
| SP07B_SALEM_ZEUGE | 42.93 s | 1080x1920, 24 fps | -14.7 LUFS | -1.5 dBTP | 0 |
| SP08A_HAT_MAN_HUT | 42.58 s | 1080x1920, 24 fps | -14.8 LUFS | -1.5 dBTP | 0 |
| SP08B_UNSICHTBARE_PERSON | 46.17 s | 1080x1920, 24 fps | -14.5 LUFS | -1.5 dBTP | 0 |

## Schnitt

| Short | Shots | kürzester | längster | Mittel | Motive |
|---|---:|---:|---:|---:|---:|
| SP06A_ATEM | 18 | 1.56 s | 3.74 s | 2.35 s | 16 |
| SP06B_RUECKENLAGE | 17 | 1.54 s | 3.80 s | 2.48 s | 16 |
| SP07A_ALBTRAUMWORT | 16 | 1.60 s | 3.66 s | 2.67 s | 16 |
| SP07B_SALEM_ZEUGE | 16 | 1.58 s | 3.78 s | 2.68 s | 16 |
| SP08A_HAT_MAN_HUT | 15 | 1.72 s | 3.66 s | 2.83 s | 15 |
| SP08B_UNSICHTBARE_PERSON | 18 | 1.85 s | 3.80 s | 2.56 s | 16 |

Zum Vergleich hielt V2 sieben Standbilder pro Short für jeweils exakt
6,0 bis 6,3 Sekunden. V4 liegt bei 15 bis 18 Shots und im Mittel bei 2.60 s.

## Hook und Endcard

| Short | Hook | Endcard |
|---|---|---|
| SP06A_ATEM | DU ERSTICKST NICHT | GANZE FOLGE IM KANAL / Warum du jemanden im Zimmer spürst |
| SP06B_RUECKENLAGE | RÜCKENLAGE? | GANZE FOLGE IM KANAL / Warum du jemanden im Zimmer spürst |
| SP07A_ALBTRAUMWORT | ALBTRAUM WAR EIN WESEN | GANZE FOLGE IM KANAL / Salem 1692: Schlafparalyse als Hexerei |
| SP07B_SALEM_ZEUGE | DER UNSICHTBARE ZEUGE | GANZE FOLGE IM KANAL / Salem 1692: Schlafparalyse als Hexerei |
| SP08A_HAT_MAN_HUT | WARUM DER HUT? | GANZE FOLGE IM KANAL / Shadow People: Warum viele den Hat Man sehen |
| SP08B_UNSICHTBARE_PERSON | EINE PERSON AUS DEM NICHTS | GANZE FOLGE IM KANAL / Shadow People: Warum viele den Hat Man sehen |

## Sichtprüfung

Diese Punkte fängt kein automatischer Test und sie brauchen einen Blick
auf den Kontaktbogen in `final_v4/`:

- [ ] Kein gekipptes Zimmer, keine quer liegende Figur
- [ ] Kein gerenderter Rahmen, kein Handy-Bezel, kein Passepartout
- [ ] Keine angeschnittenen Köpfe in den engen Ausschnitten
- [ ] Untertitel durchgehend im mobilen Safe-Bereich
- [ ] Endcard vollständig lesbar und ohne Überlappung mit dem letzten Satz
- [ ] Badge-Nummer passt zur geplanten Veröffentlichungsreihenfolge

## Dateien

- `06_PRODUCTION/SCHLAFPARALYSE_SHORTS_V1/SP06A_ATEM/final_v4/SP06A_ATEM_FINAL_V4.mp4`
- `06_PRODUCTION/SCHLAFPARALYSE_SHORTS_V1/SP06B_RUECKENLAGE/final_v4/SP06B_RUECKENLAGE_FINAL_V4.mp4`
- `06_PRODUCTION/SCHLAFPARALYSE_SHORTS_V1/SP07A_ALBTRAUMWORT/final_v4/SP07A_ALBTRAUMWORT_FINAL_V4.mp4`
- `06_PRODUCTION/SCHLAFPARALYSE_SHORTS_V1/SP07B_SALEM_ZEUGE/final_v4/SP07B_SALEM_ZEUGE_FINAL_V4.mp4`
- `06_PRODUCTION/SCHLAFPARALYSE_SHORTS_V1/SP08A_HAT_MAN_HUT/final_v4/SP08A_HAT_MAN_HUT_FINAL_V4.mp4`
- `06_PRODUCTION/SCHLAFPARALYSE_SHORTS_V1/SP08B_UNSICHTBARE_PERSON/final_v4/SP08B_UNSICHTBARE_PERSON_FINAL_V4.mp4`
