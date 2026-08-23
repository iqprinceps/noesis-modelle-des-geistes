#!/usr/bin/env python3
"""NOESIS Schlafparalyse EP06-EP08 — Phase 2 Asset Downloader.

Downloads only assets marked auto_download=true in asset_manifest.json.
RED/reference-only entries are never downloaded as media; URL sidecars are created instead.

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
DEFAULT_MANIFEST = SCRIPT_DIR / "asset_manifest.json"
DEFAULT_ROOT = Path.cwd() / "SCHLAFPARALYSE_ASSETS_PHASE2"
USER_AGENT = "NOESIS-Asset-Fetcher/2.0 (+documentary-production; respects source licenses)"

MAGIC = [
    (b"\xff\xd8\xff", ".jpg", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", ".png", "image/png"),
    (b"%PDF", ".pdf", "application/pdf"),
    (b"II*\x00", ".tif", "image/tiff"),
    (b"MM\x00*", ".tif", "image/tiff"),
    (b"PK\x03\x04", ".zip", "application/zip"),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download verified NOESIS sleep-paralysis assets into a production folder tree.")
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to asset_manifest.json")
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Output root directory")
    p.add_argument("--only", choices=["EP06", "EP07", "EP08", "SHARED"], action="append",
                   help="Restrict to episode(s). Repeat flag for several. Shared assets serving a selected episode are included.")
    p.add_argument("--green-only", action="store_true", help="Skip YELLOW assets (RED is always reference-only).")
    p.add_argument("--dry-run", action="store_true", help="Create metadata/reference files and print planned downloads, but fetch no media.")
    p.add_argument("--force", action="store_true", help="Re-download files that already exist.")
    p.add_argument("--timeout", type=int, default=45, help="HTTP timeout in seconds (default: 45).")
    p.add_argument("--retries", type=int, default=3, help="Attempts per download (default: 3).")
    return p.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "assets" not in data or not isinstance(data["assets"], list):
        raise ValueError("Manifest does not contain an assets list")
    return data


def selected(asset: dict[str, Any], only: list[str] | None) -> bool:
    if not only:
        return True
    eps = set(asset.get("episodes", []))
    requested = set(only)
    if "SHARED" in requested and str(asset.get("relative_dir", "")).startswith("00_SHARED/"):
        return True
    return bool(eps & requested)


def sanitize_text(text: str) -> str:
    return text.replace("\r", " ").strip()


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
        "application/zip": ".zip",
    }
    return mapping.get(ctype) or mimetypes.guess_extension(ctype)


def expected_ok(kind: str, ext: str | None, content_type: str | None, header: bytes) -> tuple[bool, str]:
    ctype = (content_type or "").split(";", 1)[0].lower()
    stripped = header.lstrip().lower()
    if ctype.startswith("text/html") or stripped.startswith(b"<!doctype html") or stripped.startswith(b"<html"):
        return False, "received HTML instead of media"
    if kind in ("none", "detect"):
        return True, ""
    if kind == "image":
        if (ext and ext in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}) or ctype.startswith("image/"):
            return True, ""
        return False, f"expected image, got content-type={content_type!r}, ext={ext!r}"
    if kind == "pdf":
        if ext == ".pdf" or ctype == "application/pdf":
            return True, ""
        return False, f"expected PDF, got content-type={content_type!r}, ext={ext!r}"
    return True, ""


def choose_target(base_target: Path, requested_name: str, expected_kind: str, detected_ext: str | None, content_type: str | None) -> Path:
    requested = Path(requested_name)
    if requested.suffix:
        return base_target / requested.name
    ext = detected_ext or ext_from_content_type(content_type) or ".bin"
    return base_target / f"{requested.name}{ext}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download(asset: dict[str, Any], root: Path, timeout: int, retries: int, force: bool, dry_run: bool) -> dict[str, Any]:
    out_dir = root / asset["relative_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    requested_name = asset["filename"]
    declared_target = out_dir / requested_name

    if dry_run:
        print(f"DRY  {asset['traffic_light']:6} {asset['id']}: {asset.get('download_url')}")
        return {"id": asset["id"], "status": "DRY_RUN", "planned_path": str(declared_target)}

    if Path(requested_name).suffix and declared_target.exists() and not force:
        digest = sha256(declared_target)
        print(f"SKIP {asset['id']}: exists -> {declared_target}")
        write_license_sidecar(declared_target, asset)
        return {"id": asset["id"], "status": "EXISTS", "path": str(declared_target), "bytes": declared_target.stat().st_size, "sha256": digest}

    url = asset.get("download_url")
    if not url:
        return {"id": asset["id"], "status": "NO_URL"}

    last_error = "unknown"
    for attempt in range(1, retries + 1):
        part = out_dir / (requested_name + ".part")
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urlopen(req, timeout=timeout) as resp:
                content_type = resp.headers.get("Content-Type")
                final_url = resp.geturl()
                header = resp.read(64)
                magic_ext, magic_mime = detect_magic(header)
                ok, why = expected_ok(asset.get("expected_kind", "detect"), magic_ext, content_type, header)
                if not ok:
                    raise RuntimeError(why)

                target = choose_target(out_dir, requested_name, asset.get("expected_kind", "detect"), magic_ext, content_type)
                if target.exists() and not force:
                    digest = sha256(target)
                    print(f"SKIP {asset['id']}: exists -> {target}")
                    write_license_sidecar(target, asset)
                    return {"id": asset["id"], "status": "EXISTS", "path": str(target), "bytes": target.stat().st_size, "sha256": digest, "final_url": final_url}

                part = target.with_suffix(target.suffix + ".part")
                with part.open("wb") as f:
                    f.write(header)
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                os.replace(part, target)
                digest = sha256(target)
                write_license_sidecar(target, asset)
                print(f"OK   {asset['id']}: {target} ({target.stat().st_size:,} bytes)")
                return {
                    "id": asset["id"], "status": "DOWNLOADED", "path": str(target),
                    "bytes": target.stat().st_size, "sha256": digest,
                    "content_type": content_type, "detected_mime": magic_mime,
                    "source_url": url, "final_url": final_url,
                }
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            try:
                if part.exists():
                    part.unlink()
            except OSError:
                pass
            if attempt < retries:
                wait = min(2 ** (attempt - 1), 8)
                print(f"WARN {asset['id']}: attempt {attempt}/{retries} failed ({last_error}); retry in {wait}s", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"FAIL {asset['id']}: {last_error}", file=sys.stderr)
    return {"id": asset["id"], "status": "FAILED", "error": last_error, "source_url": url}


def write_license_sidecar(media_path: Path, asset: dict[str, Any]) -> None:
    sidecar = Path(str(media_path) + ".license.txt")
    text = (
        f"ID: {asset['id']}\n"
        f"Title: {asset['title']}\n"
        f"Traffic light: {asset['traffic_light']}\n"
        f"License/status: {asset['license']}\n"
        f"Rights basis: {sanitize_text(asset['rights_basis'])}\n"
        f"Credit: {sanitize_text(asset['credit'])}\n"
        f"Source page: {asset['source_page']}\n"
        f"Download URL: {asset.get('download_url') or ''}\n"
        f"Production note: {sanitize_text(asset['shot_recommendation'])}\n"
    )
    sidecar.write_text(text, encoding="utf-8")


def write_reference_file(asset: dict[str, Any], root: Path) -> Path:
    out_dir = root / asset["relative_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / asset["filename"]
    path.write_text(
        f"TITLE={asset['title']}\n"
        f"URL={asset['source_page']}\n"
        f"STATUS={asset['traffic_light']} / REFERENCE ONLY\n"
        f"LICENSE={asset['license']}\n"
        f"RIGHTS_BASIS={sanitize_text(asset['rights_basis'])}\n"
        f"CREDIT={sanitize_text(asset['credit'])}\n"
        f"SHOT={sanitize_text(asset['shot_recommendation'])}\n"
        f"RECON_PROMPT={sanitize_text(asset.get('reconstruction_prompt',''))}\n",
        encoding="utf-8"
    )
    return path


def write_meta(root: Path, assets: list[dict[str, Any]], report: list[dict[str, Any]], source_manifest: Path) -> None:
    meta = root / "_META"
    meta.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_manifest, meta / "asset_manifest_used.json")

    cols = ["id", "episodes", "traffic_light", "title", "category", "license", "source_page", "download_url", "relative_dir", "filename", "credit", "shot_recommendation", "verification"]
    with (meta / "MANIFEST.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for a in assets:
            row = {k: a.get(k, "") for k in cols}
            row["episodes"] = ",".join(a.get("episodes", []))
            w.writerow(row)

    credit_lines = ["# CREDITS / LICENSE NOTES", "", "Always re-check license page immediately before final publication if the production date is much later than this manifest.", ""]
    for a in assets:
        if a["traffic_light"] in {"GREEN", "YELLOW"}:
            credit_lines += [f"## {a['id']} — {a['title']}", f"- Status: **{a['traffic_light']}**", f"- License: {a['license']}", f"- Credit: {a['credit']}", f"- Source: {a['source_page']}", f"- Rights basis: {a['rights_basis']}", ""]
    (meta / "CREDITS.md").write_text("\n".join(credit_lines), encoding="utf-8")

    refs = ["# REFERENCE-ONLY SOURCES", "", "These URLs are research/reconstruction references. The downloader intentionally does not fetch their copyrighted/uncleared media.", ""]
    for a in assets:
        if not a.get("auto_download"):
            refs += [f"- **{a['id']} — {a['title']}**: {a['source_page']} — {a['license']}"]
    (meta / "REFERENCE_LINKS.md").write_text("\n".join(refs), encoding="utf-8")

    (meta / "download_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    assets = [a for a in manifest["assets"] if selected(a, args.only)]
    if args.green_only:
        assets = [a for a in assets if a["traffic_light"] != "YELLOW"]

    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    print(f"NOESIS Asset Phase 2\nRoot: {root}\nAssets selected: {len(assets)}\n")

    report: list[dict[str, Any]] = []
    for asset in assets:
        if asset.get("auto_download"):
            report.append(download(asset, root, args.timeout, args.retries, args.force, args.dry_run))
        else:
            ref_path = write_reference_file(asset, root)
            print(f"REF  {asset['id']}: {ref_path}")
            report.append({"id": asset["id"], "status": "REFERENCE_ONLY", "path": str(ref_path), "url": asset["source_page"]})

    write_meta(root, assets, report, args.manifest)

    counts: dict[str, int] = {}
    for r in report:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\nSummary:")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    print(f"\nMetadata: {root / '_META'}")
    return 1 if counts.get("FAILED", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
