#!/usr/bin/env python3
"""Turn the per-Short V4 QA_REPORT.json files into one reviewable markdown sheet."""

from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "06_PRODUCTION" / "SCHLAFPARALYSE_SHORTS_V1"
ORDER = ("SP06A_ATEM", "SP06B_RUECKENLAGE", "SP07A_ALBTRAUMWORT",
         "SP07B_SALEM_ZEUGE", "SP08A_HAT_MAN_HUT", "SP08B_UNSICHTBARE_PERSON")


def main() -> int:
    reports = {}
    for job in ORDER:
        path = PROD / job / "final_v4" / "QA_REPORT.json"
        if path.is_file():
            reports[job] = json.loads(path.read_text(encoding="utf-8"))
    if not reports:
        raise SystemExit("no V4 QA reports found")

    lines = [
        "# Schlafparalyse-Shorts — V4 Final QA",
        "",
        "Erzeugt von `tools/qa_schlafparalyse_shorts_v4_report.py` aus den",
        "`final_v4/QA_REPORT.json` der einzelnen Shorts.",
        "",
        "## Technik",
        "",
        "| Short | Dauer | Bild | Lautheit | True Peak | Schwarz |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for job, data in reports.items():
        loud = data.get("loudness", {})
        lines.append("| %s | %.2f s | %s, %d fps | %s LUFS | %s dBTP | %d |" % (
            job, data["duration"], data["resolution"], data["fps"],
            loud.get("integrated_lufs", "?"), loud.get("true_peak_dbtp", "?"),
            len(data.get("blackdetect_events", [])),
        ))

    lines += [
        "",
        "## Schnitt",
        "",
        "| Short | Shots | kürzester | längster | Mittel | Motive |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for job, data in reports.items():
        lines.append("| %s | %d | %.2f s | %.2f s | %.2f s | %d |" % (
            job, data["shots"], data["shot_min"], data["shot_max"],
            data["shot_mean"], data["distinct_assets"],
        ))

    means = [d["shot_mean"] for d in reports.values()]
    shots = [d["shots"] for d in reports.values()]
    lines += [
        "",
        "Zum Vergleich hielt V2 sieben Standbilder pro Short für jeweils exakt",
        "6,0 bis 6,3 Sekunden. V4 liegt bei %d bis %d Shots und im Mittel bei %.2f s."
        % (min(shots), max(shots), statistics.mean(means)),
        "",
        "## Hook und Endcard",
        "",
        "| Short | Hook | Endcard |",
        "|---|---|---|",
    ]
    for job, data in reports.items():
        lines.append("| %s | %s | %s |" % (job, data["hook"], data["cta"]))

    lines += [
        "",
        "## Sichtprüfung",
        "",
        "Diese Punkte fängt kein automatischer Test und sie brauchen einen Blick",
        "auf den Kontaktbogen in `final_v4/`:",
        "",
        "- [ ] Kein gekipptes Zimmer, keine quer liegende Figur",
        "- [ ] Kein gerenderter Rahmen, kein Handy-Bezel, kein Passepartout",
        "- [ ] Keine angeschnittenen Köpfe in den engen Ausschnitten",
        "- [ ] Untertitel durchgehend im mobilen Safe-Bereich",
        "- [ ] Endcard vollständig lesbar und ohne Überlappung mit dem letzten Satz",
        "- [ ] Badge-Nummer passt zur geplanten Veröffentlichungsreihenfolge",
        "",
        "## Dateien",
        "",
    ]
    for job, data in reports.items():
        lines.append("- `%s`" % Path(data["file"]).relative_to(ROOT).as_posix())

    target = PROD / "FINAL_QA_V4.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("geschrieben: %s (%d Shorts)" % (target, len(reports)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
