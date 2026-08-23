#!/usr/bin/env python3
"""NOESIS EP04A/EP04B verified asset downloader.

Reads the canonical CSV manifest. GREEN and YELLOW rows with auto_download=1
may be downloaded. RED, reconstruction and manual-source rows are written as
reference sidecars only.

Fail-closed:
- follows redirects
- rejects HTML/error pages
- checks MIME + magic bytes
- computes SHA-256
- writes per-file rights sidecars

Python 3 standard library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = SCRIPT_DIR / "asset_manifest.csv"
DEFAULT_ROOT = Path.cwd() / "EP04A_EP04B_MEDIA"
USER_AGENT = "NOESIS-Asset-Fetcher/2.1 (+documentary-production; rights-gated)"

MAGIC = [
    (b"\xff\xd8\xff", ".jpg", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", ".png", "image/png"),
    (b"%PDF", ".pdf", "application/pdf"),
    (b"II*\x00", ".tif", "image/tiff"),
    (b"MM\x00*", ".tif", "image/tiff"),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download verified NOESIS EP04A/EP04B assets.")
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    p.add_argument("--only", choices=["EP04A", "EP04B"], action="append",
                   help="Restrict to one or both episodes. Shared rows are included if they serve the selected episode.")
    p.add_argument("--green-only", action="store_true",
                   help="Skip YELLOW assets. RED/manual/reconstruction remains reference-only.")
    p.add_argument("--dry-run", action="store_true",
                   help="Create metadata/reference files and print plan, but fetch no media.")
    p.add_argument("--force", action="store_true")
    p.add_argument("--timeout", type=int, default=45)
    p.add_argument("--retries", type=int, default=3)
    return p.parse_args()


def load_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            row["episodes_list"] = [x for x in row.get("episodes", "").split(";") if x]
            row["auto_download_bool"] = row.get("auto_download", "0").strip().lower() in {"1", "true", "yes"}
            rows.append(row)
    return rows


def selected(asset: dict[str, Any], only: list[str] | None) -> bool:
    if not only:
        return True
    return bool(set(asset["episodes_list"]) & set(only))


def detect_magic(header: bytes) -> tuple[str | None, str | None]:
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return ".webp", "image/webp"
    for sig, ext, mime in MAGIC:
        if header.startswith(sig):
            return ext, mime
    return None, None


def ext_from_content_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    ctype = content_type.split(";", 1)[0].strip().lower()
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/tiff": ".tif",
        "application/pdf": ".pdf",
    }
    return mapping.get(ctype) or mimetypes.guess_extension(ctype)


def expected_ok(kind: str, ext: str | None, content_type: str | None, header: bytes) -> tuple[bool, str]:
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    stripped = header.lstrip().lower()

    if ctype.startswith("text/html") or stripped.startswith(b"<!doctype html") or stripped.startswith(b"<html"):
        return False, "received HTML instead of media"

    if kind in {"none", "detect", ""}:
        return True, ""

    if kind == "image":
        if ext in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"} or ctype.startswith("image/"):
            return True, ""
        return False, f"expected image, got content-type={content_type!r}, magic-ext={ext!r}"

    if kind == "pdf":
        if ext == ".pdf" or ctype == "application/pdf":
            return True, ""
        return False, f"expected PDF, got content-type={content_type!r}, magic-ext={ext!r}"

    return True, ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_rights_sidecar(media_path: Path, asset: dict[str, Any], final_url: str = "") -> None:
    p = Path(str(media_path) + ".license.txt")
    p.write_text(
        "\n".join([
            f"ID: {asset['id']}",
            f"Episode(s): {asset['episodes']}",
            f"Title: {asset['title']}",
            f"Traffic light: {asset['traffic_light']}",
            f"License/status: {asset['license']}",
            f"Source page: {asset['source_page']}",
            f"Manifest direct URL: {asset['download_url']}",
            f"Resolved final URL: {final_url}",
            f"Verified: {asset['verification_date']} / {asset['verification_status']}",
            f"Script act: {asset['script_act']}",
            f"Shot use: {asset['shot_use']}",
            "",
            "Production rule: traffic-light status does not override context/date/evidence notes.",
        ]),
        encoding="utf-8",
    )


def write_reference_file(asset: dict[str, Any], root: Path) -> Path:
    out_dir = root / asset["relative_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = asset["filename"] or f"{asset['id']}.url.txt"
    p = out_dir / filename
    p.write_text(
        "\n".join([
            f"ID={asset['id']}",
            f"EPISODES={asset['episodes']}",
            f"TITLE={asset['title']}",
            f"TRAFFIC_LIGHT={asset['traffic_light']}",
            f"LICENSE={asset['license']}",
            f"SOURCE_PAGE={asset['source_page']}",
            f"DIRECT_URL={asset['download_url']}",
            f"VERIFICATION={asset['verification_status']}",
            f"VERIFIED_DATE={asset['verification_date']}",
            f"SCRIPT_ACT={asset['script_act']}",
            f"SHOT_USE={asset['shot_use']}",
        ]),
        encoding="utf-8",
    )
    return p


def choose_target(out_dir: Path, filename: str, magic_ext: str | None, content_type: str | None) -> Path:
    p = Path(filename)
    if p.suffix:
        return out_dir / p.name
    ext = magic_ext or ext_from_content_type(content_type) or ".bin"
    return out_dir / f"{p.name}{ext}"


def download(asset: dict[str, Any], root: Path, args: argparse.Namespace) -> dict[str, Any]:
    out_dir = root / asset["relative_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    requested_name = asset["filename"]
    direct = asset["download_url"]

    if args.dry_run:
        print(f"DRY  {asset['traffic_light']:6} {asset['id']}: {direct}")
        return {"id": asset["id"], "status": "DRY_RUN", "direct_url": direct}

    if not direct:
        return {"id": asset["id"], "status": "NO_DIRECT_URL"}

    declared = out_dir / requested_name
    if declared.exists() and not args.force:
        digest = sha256(declared)
        write_rights_sidecar(declared, asset)
        print(f"SKIP {asset['id']}: exists -> {declared}")
        return {"id": asset["id"], "status": "EXISTS", "path": str(declared), "sha256": digest}

    last_error = "unknown"
    for attempt in range(1, args.retries + 1):
        part: Path | None = None
        try:
            req = Request(direct, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urlopen(req, timeout=args.timeout) as resp:
                content_type = resp.headers.get("Content-Type")
                final_url = resp.geturl()
                header = resp.read(64)
                magic_ext, detected_mime = detect_magic(header)

                ok, why = expected_ok(asset.get("expected_kind", "detect"), magic_ext, content_type, header)
                if not ok:
                    raise RuntimeError(why)

                target = choose_target(out_dir, requested_name, magic_ext, content_type)
                if target.exists() and not args.force:
                    digest = sha256(target)
                    write_rights_sidecar(target, asset, final_url)
                    print(f"SKIP {asset['id']}: exists -> {target}")
                    return {
                        "id": asset["id"], "status": "EXISTS", "path": str(target),
                        "sha256": digest, "final_url": final_url,
                    }

                part = target.with_suffix(target.suffix + ".part")
                with part.open("wb") as f:
                    f.write(header)
                    while True:
                        block = resp.read(1024 * 1024)
                        if not block:
                            break
                        f.write(block)

                os.replace(part, target)
                digest = sha256(target)
                write_rights_sidecar(target, asset, final_url)
                print(f"OK   {asset['id']}: {target} ({target.stat().st_size:,} bytes)")
                return {
                    "id": asset["id"],
                    "status": "DOWNLOADED",
                    "path": str(target),
                    "bytes": target.stat().st_size,
                    "sha256": digest,
                    "content_type": content_type,
                    "detected_mime": detected_mime,
                    "source_url": direct,
                    "final_url": final_url,
                }

        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if part is not None:
                try:
                    if part.exists():
                        part.unlink()
                except OSError:
                    pass
            if attempt < args.retries:
                delay = min(2 ** (attempt - 1), 8)
                print(f"WARN {asset['id']}: attempt {attempt}/{args.retries} failed: {last_error}; retry {delay}s",
                      file=sys.stderr)
                time.sleep(delay)

    print(f"FAIL {asset['id']}: {last_error}", file=sys.stderr)
    return {"id": asset["id"], "status": "FAILED", "error": last_error, "direct_url": direct}


def write_meta(root: Path, assets: list[dict[str, Any]], report: list[dict[str, Any]], manifest_path: Path) -> None:
    meta = root / "_META"
    meta.mkdir(parents=True, exist_ok=True)

    shutil.copy2(manifest_path, meta / "asset_manifest_used.csv")

    with (meta / "DOWNLOAD_RESULTS.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields = ["id", "status", "path", "bytes", "sha256", "final_url", "error"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for item in report:
            writer.writerow(item)

    (meta / "download_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    credit = [
        "# Runtime asset credits",
        "",
        "Generated from the canonical manifest. Use the repository CREDITS.md as the editorial master.",
        "",
    ]
    for a in assets:
        if a["traffic_light"] in {"GREEN", "YELLOW"}:
            credit += [
                f"## {a['id']} — {a['title']}",
                f"- Traffic light: **{a['traffic_light']}**",
                f"- License/status: {a['license']}",
                f"- Source: {a['source_page']}",
                "",
            ]
    (meta / "CREDITS.md").write_text("\n".join(credit), encoding="utf-8")


def main() -> int:
    args = parse_args()
    all_assets = load_manifest(args.manifest)
    assets = [a for a in all_assets if selected(a, args.only)]

    if args.green_only:
        assets = [a for a in assets if a["traffic_light"] != "YELLOW"]

    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    print(f"NOESIS EP04A/EP04B Asset Downloader\nRoot: {root}\nRows selected: {len(assets)}\n")

    report: list[dict[str, Any]] = []

    for asset in assets:
        can_fetch = (
            asset["traffic_light"] in {"GREEN", "YELLOW"}
            and asset["auto_download_bool"]
            and bool(asset["download_url"])
        )

        if can_fetch:
            report.append(download(asset, root, args))
        else:
            ref = write_reference_file(asset, root)
            mode = "MANUAL" if asset["download_url"] else "REF"
            print(f"{mode:4} {asset['id']}: {ref}")
            report.append({
                "id": asset["id"],
                "status": "MANUAL_SOURCE" if asset["download_url"] else "REFERENCE_ONLY",
                "path": str(ref),
            })

    write_meta(root, assets, report, args.manifest)

    counts: dict[str, int] = {}
    for r in report:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print("\nSummary:")
    for status, count in sorted(counts.items()):
        print(f"  {status}: {count}")

    return 1 if counts.get("FAILED", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
