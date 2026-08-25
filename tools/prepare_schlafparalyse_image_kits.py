#!/usr/bin/env python3
"""Build self-contained local image-generation kits for EP06-EP08.

The source media stay in the manifest-managed download tree. This helper copies
the usable episode/shared pool into one flat asset folder per episode, removes
scene/license bookkeeping from the copy names, and rewrites the local prompt
copies to those friendly names. Binary outputs are ignored by Git according to
the repository's .gitignore.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TYPE_B = ROOT / "03_EPISODEN" / "TYPE_B"
ASSET_SPEC = TYPE_B / "SCHLAFPARALYSE_ASSETS_PHASE2"
ASSET_ROOT = ROOT / "SCHLAFPARALYSE_ASSETS_PHASE2"

CFG = {
    "EP06": {
        "episode": TYPE_B / "EP06_SCHLAFPARALYSE_01",
        "production": ROOT / "06_PRODUCTION" / "EP06_SCHLAFPARALYSE_V4",
        "expected_prompts": 40,
    },
    "EP07": {
        "episode": TYPE_B / "EP07_SCHLAFPARALYSE_02",
        "production": ROOT / "06_PRODUCTION" / "EP07_SCHLAFPARALYSE_V4",
        "expected_prompts": 24,
    },
    "EP08": {
        "episode": TYPE_B / "EP08_SCHLAFPARALYSE_03",
        "production": ROOT / "06_PRODUCTION" / "EP08_SCHLAFPARALYSE_V4",
        "expected_prompts": 40,
    },
}

MANIFESTS = [
    ASSET_SPEC / "asset_manifest.csv",
    ASSET_SPEC / "asset_manifest_v5_additions.csv",
    ASSET_SPEC / "asset_manifest_v5_expansion.csv",
]

BRIGHTNESS_LOCK = (
    "Keep the image visually readable on ordinary laptop and phone screens: "
    "use lifted but natural midtones, visible shadow detail, clear subject-background "
    "separation, and at least one warm or neutral visual anchor. Reserve true black "
    "for small accents only; do not crush large regions into featureless darkness or "
    "apply a uniformly bleak or depressive grade."
)


def split_refs(value: str) -> list[str]:
    value = value.strip()
    if not value or value.casefold() == "keine":
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def parse_prompt_file(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[dict] = []
    output_re = re.compile(r"^((?:(?:EP\d{2}_)?(?:IMG|RSV)\d+|SHOT\d+)_.+\.png)\s*$")
    for i, line in enumerate(lines):
        hit = output_re.match(line)
        if not hit:
            continue
        output = hit.group(1)
        ref_line = next((x.strip() for x in lines[i + 1:i + 5] if x.strip().startswith("Referenz:")), "")
        if not ref_line:
            raise RuntimeError(f"Missing reference line after {path}:{i + 1}")
        out.append({
            "kind": "RESERVE" if "_RSV" in output or output.startswith("RSV") or output.startswith("SHOT") else "MAIN",
            "output_filename": output,
            "references": split_refs(ref_line.split(":", 1)[1]),
            "prompt_source": path.name,
            "prompt_line": i + 1,
        })
    return out


def parse_style_masters(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[dict] = []
    style_re = re.compile(r"^### (STYLE_[A-Z0-9_]+\.png)\s*$")
    for i, line in enumerate(lines):
        hit = style_re.match(line)
        if not hit:
            continue
        ref_line = next((x.strip() for x in lines[i + 1:i + 6] if x.strip().startswith("Referenz:")), "")
        if not ref_line:
            raise RuntimeError(f"Missing style reference line after {path}:{i + 1}")
        out.append({
            "kind": "STYLE_MASTER",
            "output_filename": hit.group(1),
            "references": split_refs(ref_line.split(":", 1)[1]),
            "prompt_source": path.name,
            "prompt_line": i + 1,
        })
    return out


def load_manifest_rows() -> list[dict]:
    rows: list[dict] = []
    for path in MANIFESTS:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                row = dict(row)
                row["manifest"] = path.name
                rows.append(row)
    return rows


def locate_exact(filename: str) -> Path | None:
    hits = [p for p in ASSET_ROOT.rglob(filename) if p.is_file()]
    if len(hits) > 1:
        raise RuntimeError(f"Ambiguous asset reference {filename}: {hits}")
    return hits[0] if hits else None


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def friendly_asset_name(ep: str, source: Path) -> str:
    """Return a flat, readable filename without scene or license bookkeeping."""
    stem = source.stem
    stem = re.sub(r"^SHARED_", "", stem, flags=re.I)
    stem = re.sub(r"^EP\d{2}_S\d{2}_", "", stem, flags=re.I)
    stem = re.sub(r"^EP\d{2}_", "", stem, flags=re.I)
    stem = re.sub(
        r"_(?:CC[-_]?BY(?:[-_]?SA)?[-_]?\d+(?:\.\d+)?|CC0(?:[-_]?\d+(?:\.\d+)?)?|PD(?:[-_].*)?|REVIEW|personality_review|GFDL)$",
        "",
        stem,
        flags=re.I,
    )
    stem = re.sub(r"_+", "_", stem).strip("_")
    return f"{ep}_{stem}{source.suffix.lower()}"


def friendly_output_name(ep: str, filename: str) -> str:
    """Use editor-friendly output names without a redundant episode prefix."""
    main_prefix = f"{ep}_IMG"
    if filename.startswith(main_prefix):
        return filename.removeprefix(f"{ep}_")
    reserve = re.fullmatch(rf"{re.escape(ep)}_RSV(\d{{2}})_(.+\.png)", filename)
    if reserve:
        return f"SHOT{reserve.group(1)}_{reserve.group(2)}"
    return filename


def copy_prompt_with_names(source: Path, target: Path, name_map: dict[str, str]) -> None:
    text = source.read_text(encoding="utf-8")
    for old, new in sorted(name_map.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(old, new)
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != "Prompt:":
            continue
        prompt_index = index + 1
        while prompt_index < len(lines) and not lines[prompt_index].strip():
            prompt_index += 1
        if prompt_index < len(lines) and BRIGHTNESS_LOCK not in lines[prompt_index]:
            lines[prompt_index] = f"{lines[prompt_index].rstrip()} {BRIGHTNESS_LOCK}"
    text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_episode(ep: str, cfg: dict, manifest_rows: list[dict]) -> dict:
    episode: Path = cfg["episode"]
    kit = cfg["production"] / "IMAGE_GENERATION_KIT"
    prompts_dir = kit / "01_PROMPTS"
    assets_dir = kit / "02_ASSETS"
    generated_dir = kit / "03_GENERATED_OUTPUT"
    for path in (prompts_dir, assets_dir, generated_dir):
        path.mkdir(parents=True, exist_ok=True)

    prompt_files = sorted(episode.glob("NANOBANANA_PROMPTS_V4_*.md"))
    correction_files = sorted(episode.glob("NANOBANANA_CORRECTION_BATCH_*.md"))
    guide = episode / "NANOBANANA_GUIDE_V4.md"
    queue = parse_style_masters(guide)
    for prompt_file in prompt_files:
        queue.extend(parse_prompt_file(prompt_file))
    prompt_count = sum(1 for row in queue if row["kind"] != "STYLE_MASTER")
    if prompt_count != cfg["expected_prompts"]:
        raise RuntimeError(f"{ep}: parsed {prompt_count} prompts; expected {cfg['expected_prompts']}")

    factual_refs = sorted({
        ref for row in queue for ref in row["references"] if not ref.startswith("STYLE_")
    })

    asset_sources: list[Path] = []
    for source_root in (ASSET_ROOT / "00_SHARED", ASSET_ROOT / ep):
        if source_root.is_dir():
            asset_sources.extend(
                p for p in source_root.rglob("*")
                if p.is_file()
                and not p.name.endswith(".license.txt")
                and "03_REFERENCE_ONLY" not in p.parts
            )
    asset_sources = sorted(set(asset_sources))
    name_map = {source.name: friendly_asset_name(ep, source) for source in asset_sources}
    if len(name_map.values()) != len(set(name_map.values())):
        raise RuntimeError(f"{ep}: friendly asset filename collision")

    output_name_map = {
        row["output_filename"]: friendly_output_name(ep, row["output_filename"])
        for row in queue
        if row["kind"] != "STYLE_MASTER"
    }
    prompt_name_map = {**name_map, **output_name_map}
    for source in [guide, *prompt_files, *correction_files, episode / "VISUAL_COVERAGE_V5.md"]:
        copy_prompt_with_names(source, prompts_dir / source.name, prompt_name_map)

    missing_required: list[str] = []
    for name in factual_refs:
        source = locate_exact(name)
        if not source:
            missing_required.append(name)

    style_names = {row["output_filename"] for row in queue if row["kind"] == "STYLE_MASTER"}
    missing_styles = sorted(name for name in style_names if not (assets_dir / name).is_file())
    queue_rows: list[dict] = []
    for order, row in enumerate(queue, 1):
        unresolved = []
        display_refs = []
        for ref in row["references"]:
            if ref.startswith("STYLE_"):
                if ref not in style_names or not (assets_dir / ref).is_file():
                    unresolved.append(ref)
                display_refs.append(ref)
            else:
                source = locate_exact(ref)
                if not source:
                    unresolved.append(ref)
                    display_refs.append(ref)
                else:
                    display_refs.append(name_map[source.name])
        queue_rows.append({
            "order": order,
            "kind": row["kind"],
            "output_filename": friendly_output_name(ep, row["output_filename"]),
            "references": "; ".join(display_refs) if display_refs else "Keine",
            "prompt_source": f"01_PROMPTS/{row['prompt_source']}",
            "prompt_line": row["prompt_line"],
            "status": "READY" if not unresolved else "MISSING: " + "; ".join(unresolved),
        })

    asset_rows: list[dict] = []
    for source in asset_sources:
        friendly = name_map[source.name]
        target = assets_dir / friendly
        copy_file(source, target)
        traffic_light = "GREEN" if "01_ORIGINAL_GREEN" in source.parts else "YELLOW"
        asset_rows.append({
            "filename": friendly,
            "original_filename": source.name,
            "source_path": source.relative_to(ROOT).as_posix(),
            "kit_path": target.relative_to(ROOT).as_posix(),
            "required_by_prompt": "YES" if source.name in factual_refs else "NO",
            "traffic_light": traffic_light,
        })
    for style_name in sorted(style_names):
        target = assets_dir / style_name
        if not target.is_file():
            continue
        asset_rows.append({
            "filename": style_name,
            "original_filename": style_name,
            "source_path": "GENERATED_WITH_IMAGEGEN",
            "kit_path": target.relative_to(ROOT).as_posix(),
            "required_by_prompt": "YES",
            "traffic_light": "GENERATED_STYLE",
        })

    relevant_manifest = [
        row for row in manifest_rows
        if row.get("episodes") == ep or "SHARED" in row.get("id", "")
    ]
    missing_downloads = []
    for row in relevant_manifest:
        if row.get("auto_download") != "1":
            continue
        name = row.get("filename", "")
        found = locate_exact(name) or next(iter(ASSET_ROOT.rglob(name + ".*")), None)
        if not found:
            missing_downloads.append({
                "id": row.get("id", ""),
                "filename": name,
                "source_page": row.get("source_page", ""),
                "blocking_for_current_prompts": name in factual_refs,
            })

    write_csv(
        kit / "GENERATION_QUEUE.csv",
        ["order", "kind", "output_filename", "references", "prompt_source", "prompt_line", "status"],
        queue_rows,
    )
    write_csv(
        kit / "ASSET_INDEX.csv",
        ["filename", "original_filename", "source_path", "kit_path", "required_by_prompt", "traffic_light"],
        asset_rows,
    )

    audit = {
        "episode": ep,
        "prompt_count": prompt_count,
        "style_master_count": len(style_names),
        "style_master_references_ready": len(style_names) - len(missing_styles),
        "missing_style_master_references": missing_styles,
        "required_factual_reference_count": len(factual_refs),
        "required_factual_references_ready": len(factual_refs) - len(missing_required),
        "missing_required_references": missing_required,
        "flat_asset_files": len(asset_rows),
        "missing_manifest_downloads": missing_downloads,
        "generation_ready": not missing_required and not missing_styles and all(row["status"] == "READY" for row in queue_rows),
    }
    (kit / "ASSET_AUDIT.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    missing_note = (
        "Keine Pflichtreferenz fehlt."
        if not missing_required
        else "Fehlende Pflichtreferenzen: " + ", ".join(missing_required)
    )
    extra_note = (
        f"{len(missing_downloads)} optionale Manifest-Datei(en) konnten nicht geladen werden; "
        "sie blockieren die aktuellen KI-Prompts nicht."
        if missing_downloads else "Der optionale Manifest-Pool ist vollständig."
    )
    readme = f"""# {ep} — Image Generation Kit

**Status:** {'READY' if audit['generation_ready'] else 'NOT READY'}  
**Prompts:** {prompt_count} ({sum(r['kind'] == 'MAIN' for r in queue_rows)} MAIN + {sum(r['kind'] == 'RESERVE' for r in queue_rows)} RESERVE)  
**Style-Master:** {len(style_names)}  
**Style-Referenzen:** {len(style_names) - len(missing_styles)}/{len(style_names)} als echte Dateien vorhanden  
**Sach-/Personenreferenzen:** {len(factual_refs) - len(missing_required)}/{len(factual_refs)} vorhanden

## Startreihenfolge

1. `GENERATION_QUEUE.csv` öffnen.
2. MAIN- und danach bei Bedarf RESERVE-Zeilen ausführen. **Jede in den Promptdateien genannte Referenz liegt unter exakt diesem Namen in `02_ASSETS/`.**
3. Ergebnisse mit dem vorgegebenen Namen in `03_GENERATED_OUTPUT/` speichern.
4. Die STYLE_MASTER-Zeilen sind bereits erledigt; sie bleiben nur als reproduzierbare Prompts im Guide erhalten.

## Ordner

- `01_PROMPTS/` — Guide und vier Prompt-Batches
- `02_ASSETS/` — **alle Referenzen flach in einem Ordner**, einschließlich der fertigen Style-Master unter exakt den Prompt-Namen
- `03_GENERATED_OUTPUT/` — MAIN/RESERVE-Ergebnisse

## Prüfung

- {missing_note}
- {'Keine Style-Referenz fehlt.' if not missing_styles else 'Fehlende Style-Referenzen: ' + ', '.join(missing_styles)}
- {extra_note}
- `ASSET_AUDIT.json` enthält die maschinenlesbare Vollständigkeitsprüfung.
- `ASSET_INDEX.csv` listet neuen Namen, ursprünglichen Downloadnamen, Rechte-Ampel und Prompt-Pflichtstatus.

Wichtig: YELLOW-Assets bleiben vor dem finalen Einsatz reviewpflichtig. RED-/URL-Recherchelinks werden bewusst nicht in `02_ASSETS/` kopiert.
"""
    (kit / "00_START_HERE.md").write_text(readme, encoding="utf-8")
    (generated_dir / "README.md").write_text(
        "# Generated Output\n\nHier die erzeugten MAIN-/RESERVE-Bilder unter dem vorgegebenen Dateinamen ablegen.\n",
        encoding="utf-8",
    )
    print(
        f"{ep}: {prompt_count} prompts, {len(style_names)} styles, "
        f"{len(factual_refs) - len(missing_required)}/{len(factual_refs)} required refs ready, "
        f"{len(asset_rows)} flat asset files"
    )
    return audit


def main() -> int:
    if not ASSET_ROOT.is_dir():
        raise SystemExit(f"Downloaded asset root missing: {ASSET_ROOT}")
    manifest_rows = load_manifest_rows()
    audits = {ep: build_episode(ep, cfg, manifest_rows) for ep, cfg in CFG.items()}
    blocking = [ep for ep, audit in audits.items() if not audit["generation_ready"]]
    if blocking:
        print("NOT READY: " + ", ".join(blocking))
        return 1
    print("Schlafparalyse EP06-EP08 image-generation kits are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
