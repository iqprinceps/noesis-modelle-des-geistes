#!/usr/bin/env python3
"""NOESIS Schlafparalyse EP06-EP08 — resilient Phase 2 asset downloader.

Goals:
- attempt every auto_download=1 manifest asset; no dimension/quality threshold filters assets out
- keep GREEN and YELLOW by default; RED/reference-only stays reference-only for rights reasons
- be polite to Wikimedia's 2026 rate limits and use supported thumbnail sizes as fallbacks
- survive transient 429/503, resets and IncompleteRead without aborting the whole batch
- keep already-downloaded files and their license sidecars
- try source-page-discovered media URLs when a direct endpoint returns HTML

Python 3 standard library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import os
import random
import shutil
import socket
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from http.client import IncompleteRead, RemoteDisconnected
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = SCRIPT_DIR / "asset_manifest.csv"
DEFAULT_ROOT = Path.cwd() / "SCHLAFPARALYSE_ASSETS_PHASE2"
USER_AGENT = (
    "NOESIS-Asset-Fetcher/3.0 "
    "(https://github.com/iqprinceps/noesis-modelle-des-geistes; documentary asset retrieval) "
    "Python-urllib"
)

WIKIMEDIA_WIDTHS = (3840, 1920, 1280, 960)

MAGIC = [
    (b"\xff\xd8\xff", ".jpg", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", ".png", "image/png"),
    (b"%PDF", ".pdf", "application/pdf"),
    (b"II*\x00", ".tif", "image/tiff"),
    (b"MM\x00*", ".tif", "image/tiff"),
    (b"PK\x03\x04", ".zip", "application/zip"),
]

_LAST_HOST_REQUEST: dict[str, float] = {}


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"a", "img", "source"}:
            return
        data = dict(attrs)
        for key in ("href", "src"):
            value = data.get(key)
            if value:
                self.links.append(value)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download verified NOESIS sleep-paralysis assets into a production folder tree.")
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to asset_manifest.csv or .json")
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Output root directory")
    p.add_argument("--only", choices=["EP06", "EP07", "EP08", "SHARED"], action="append",
                   help="Restrict to episode(s). Repeat flag for several. Shared assets serving a selected episode are included.")
    p.add_argument("--green-only", action="store_true",
                   help="OPTIONAL: skip YELLOW assets. Default downloads both GREEN and YELLOW; no quality filter is applied.")
    p.add_argument("--dry-run", action="store_true", help="Create metadata/reference files and print planned downloads, but fetch no media.")
    p.add_argument("--force", action="store_true", help="Re-download files that already exist.")
    p.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds (default: 90).")
    p.add_argument("--retries", type=int, default=5, help="Attempts per candidate URL (default: 5).")
    p.add_argument("--wikimedia-delay", type=float, default=2.0,
                   help="Minimum delay between Wikimedia requests in seconds (default: 2.0).")
    p.add_argument("--no-wikimedia-thumbnails", action="store_true",
                   help="Disable Wikimedia 3840/1920/1280/960 fallbacks and request manifest URL only.")
    return p.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".csv":
        assets: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                row["episodes"] = [x for x in row.get("episodes", "").split(";") if x]
                row["auto_download"] = row.get("auto_download", "0").strip().lower() in {"1", "true", "yes"}
                row["download_url"] = row.get("download_url") or None
                row["rights_basis"] = row.get("license", "")
                row["credit"] = row.get("license", "")
                row["shot_recommendation"] = "See PHASE2_ASSET_LIST.md"
                row["reconstruction_prompt"] = "See RECON_PROMPTS.md"
                assets.append(row)
        return {"assets": assets}
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
    """Validate only media type/safety, never dimensions or quality."""
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


def choose_target(base_target: Path, requested_name: str, detected_ext: str | None, content_type: str | None) -> Path:
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


def host_key(url: str) -> str:
    return urlsplit(url).netloc.lower()


def is_wikimedia(url: str) -> bool:
    host = host_key(url)
    return host.endswith("wikimedia.org") or host.endswith("wikimediausercontent.org")


def add_query(url: str, **params: str) -> str:
    parts = urlsplit(url)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    q.update(params)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))


def wikimedia_candidates(url: str, expected_kind: str, enabled: bool) -> list[tuple[str, str]]:
    if not enabled or expected_kind != "image" or not is_wikimedia(url):
        return [(url, "manifest")]
    candidates = [(add_query(url, width=str(width)), f"wikimedia-{width}px") for width in WIKIMEDIA_WIDTHS]
    candidates.append((url, "wikimedia-original"))
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for item in candidates:
        if item[0] not in seen:
            seen.add(item[0])
            out.append(item)
    return out


def throttle(url: str, wikimedia_delay: float) -> None:
    if not is_wikimedia(url):
        return
    host = host_key(url)
    now = time.monotonic()
    previous = _LAST_HOST_REQUEST.get(host)
    if previous is not None:
        remain = wikimedia_delay - (now - previous)
        if remain > 0:
            time.sleep(remain)
    _LAST_HOST_REQUEST[host] = time.monotonic()


def retry_after_seconds(exc: BaseException) -> float | None:
    if not isinstance(exc, HTTPError):
        return None
    raw = exc.headers.get("Retry-After") if exc.headers else None
    if not raw:
        return None
    raw = raw.strip()
    if raw.isdigit():
        return float(raw)
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
    except Exception:
        return None


def wait_for_retry(attempt: int, exc: BaseException) -> float:
    retry_after = retry_after_seconds(exc)
    status = exc.code if isinstance(exc, HTTPError) else None
    if status in {429, 503}:
        base = min(120.0, 10.0 * (2 ** (attempt - 1)))
    else:
        base = min(30.0, 2.0 * (2 ** (attempt - 1)))
    if retry_after is not None:
        base = max(base, retry_after)
    return base + random.uniform(0.4, 1.8)


def existing_target(out_dir: Path, requested_name: str) -> Path | None:
    requested = Path(requested_name)
    if requested.suffix:
        p = out_dir / requested.name
        return p if p.exists() else None
    matches = [
        p for p in out_dir.glob(requested.name + ".*")
        if p.is_file() and not p.name.endswith(".license.txt") and not p.name.endswith(".part")
    ]
    return matches[0] if matches else None


def fetch_source_fallbacks(asset: dict[str, Any], timeout: int, wikimedia_delay: float) -> list[str]:
    source = asset.get("source_page")
    if not source:
        return []
    try:
        throttle(source, wikimedia_delay)
        req = Request(source, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*;q=0.5"})
        with urlopen(req, timeout=timeout) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "html" not in ctype:
                return []
            body = resp.read(2 * 1024 * 1024)
            charset = resp.headers.get_content_charset() or "utf-8"
        parser = LinkCollector()
        parser.feed(body.decode(charset, errors="replace"))
    except Exception:
        return []

    direct = asset.get("download_url") or ""
    found: list[str] = []
    for raw in parser.links:
        absolute = urljoin(source, raw)
        path = urlsplit(absolute).path.lower()
        if (
            "/download/" in path
            or "/download/file/" in path
            or "/iiif/" in path
            or path.endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".pdf", ".zip"))
        ):
            if absolute != direct and absolute not in found:
                found.append(absolute)
    return found[:20]


def request_once(url: str, asset: dict[str, Any], out_dir: Path, requested_name: str,
                 timeout: int, force: bool, wikimedia_delay: float) -> dict[str, Any]:
    throttle(url, wikimedia_delay)
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "image/avif,image/webp,image/apng,image/*,application/pdf,application/zip,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("Content-Type")
        final_url = resp.geturl()
        header = resp.read(64)
        magic_ext, magic_mime = detect_magic(header)
        ok, why = expected_ok(asset.get("expected_kind", "detect"), magic_ext, content_type, header)
        if not ok:
            raise RuntimeError(why)

        target = choose_target(out_dir, requested_name, magic_ext, content_type)
        if target.exists() and not force:
            digest = sha256(target)
            write_license_sidecar(target, asset)
            return {
                "id": asset["id"], "status": "EXISTS", "path": str(target),
                "bytes": target.stat().st_size, "sha256": digest, "final_url": final_url,
            }

        part = target.with_suffix(target.suffix + ".part")
        try:
            with part.open("wb") as f:
                f.write(header)
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
            os.replace(part, target)
        except BaseException:
            try:
                if part.exists():
                    part.unlink()
            except OSError:
                pass
            raise

    digest = sha256(target)
    write_license_sidecar(target, asset)
    return {
        "id": asset["id"], "status": "DOWNLOADED", "path": str(target),
        "bytes": target.stat().st_size, "sha256": digest,
        "content_type": content_type, "detected_mime": magic_mime,
        "source_url": asset.get("download_url"), "final_url": final_url,
    }


RETRIABLE = (
    HTTPError, URLError, TimeoutError, socket.timeout, ConnectionResetError,
    BrokenPipeError, IncompleteRead, RemoteDisconnected, OSError, RuntimeError,
)


def download(asset: dict[str, Any], root: Path, timeout: int, retries: int, force: bool,
             dry_run: bool, wikimedia_delay: float, use_wikimedia_thumbnails: bool) -> dict[str, Any]:
    out_dir = root / asset["relative_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    requested_name = asset["filename"]
    declared_target = out_dir / requested_name

    if dry_run:
        print(f"DRY  {asset['traffic_light']:6} {asset['id']}: {asset.get('download_url')}")
        return {"id": asset["id"], "status": "DRY_RUN", "planned_path": str(declared_target)}

    if not force:
        existing = existing_target(out_dir, requested_name)
        if existing:
            digest = sha256(existing)
            print(f"SKIP {asset['id']}: exists -> {existing}")
            write_license_sidecar(existing, asset)
            return {
                "id": asset["id"], "status": "EXISTS", "path": str(existing),
                "bytes": existing.stat().st_size, "sha256": digest,
            }

    url = asset.get("download_url")
    if not url:
        return {"id": asset["id"], "status": "NO_URL"}

    candidates = wikimedia_candidates(url, asset.get("expected_kind", "detect"), use_wikimedia_thumbnails)
    source_fallback_added = False
    last_error = "unknown"
    tried: list[dict[str, Any]] = []
    candidate_index = 0

    while candidate_index < len(candidates):
        candidate_url, variant = candidates[candidate_index]
        candidate_index += 1

        for attempt in range(1, retries + 1):
            try:
                result = request_once(candidate_url, asset, out_dir, requested_name, timeout, force, wikimedia_delay)
                result["retrieval_variant"] = variant
                result["attempt"] = attempt
                print(f"OK   {asset['id']}: {result['path']} ({result.get('bytes', 0):,} bytes; {variant})")
                return result
            except RETRIABLE as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                status = exc.code if isinstance(exc, HTTPError) else None
                tried.append({
                    "variant": variant, "url": candidate_url, "attempt": attempt,
                    "status": status, "error": last_error,
                })

                if (
                    not source_fallback_added
                    and isinstance(exc, RuntimeError)
                    and "received HTML instead of media" in str(exc)
                ):
                    discovered = fetch_source_fallbacks(asset, timeout, wikimedia_delay)
                    for fallback in discovered:
                        if all(fallback != existing_url for existing_url, _ in candidates):
                            candidates.append((fallback, "source-page-fallback"))
                    source_fallback_added = True

                if attempt < retries:
                    wait = wait_for_retry(attempt, exc)
                    print(
                        f"WARN {asset['id']}: {variant} attempt {attempt}/{retries} failed "
                        f"({last_error}); retry in {wait:.1f}s",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                else:
                    print(
                        f"WARN {asset['id']}: {variant} exhausted after {retries} attempts "
                        f"({last_error}); trying next candidate if available",
                        file=sys.stderr,
                    )

    print(f"FAIL {asset['id']}: {last_error}", file=sys.stderr)
    return {
        "id": asset["id"], "status": "FAILED", "error": last_error,
        "source_url": url, "tried": tried,
    }


def write_license_sidecar(media_path: Path, asset: dict[str, Any]) -> None:
    sidecar = Path(str(media_path) + ".license.txt")
    text = (
        f"ID: {asset['id']}\n"
        f"Title: {asset['title']}\n"
        f"Traffic light: {asset['traffic_light']}\n"
        f"License/status: {asset['license']}\n"
        f"Rights basis: {sanitize_text(asset.get('rights_basis', asset['license']))}\n"
        f"Credit: {sanitize_text(asset.get('credit', asset['license']))}\n"
        f"Source page: {asset['source_page']}\n"
        f"Manifest download URL: {asset.get('download_url') or ''}\n"
        f"Production note: {sanitize_text(asset.get('shot_recommendation', 'See PHASE2_ASSET_LIST.md'))}\n"
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
        f"SHOT={asset.get('shot_recommendation', 'See PHASE2_ASSET_LIST.md')}\n"
        f"RECON_PROMPT={asset.get('reconstruction_prompt', 'See RECON_PROMPTS.md')}\n",
        encoding="utf-8",
    )
    return path


def write_meta(root: Path, assets: list[dict[str, Any]], report: list[dict[str, Any]], source_manifest: Path) -> None:
    meta = root / "_META"
    meta.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_manifest, meta / ("asset_manifest_used" + source_manifest.suffix.lower()))
    cols = ["id", "episodes", "traffic_light", "title", "license", "source_page", "download_url", "relative_dir", "filename"]
    with (meta / "MANIFEST.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for a in assets:
            row = {k: a.get(k, "") for k in cols}
            row["episodes"] = ",".join(a.get("episodes", []))
            w.writerow(row)
    credit_lines = ["# CREDITS / LICENSE NOTES", ""]
    for a in assets:
        if a["traffic_light"] in {"GREEN", "YELLOW"}:
            credit_lines += [
                f"## {a['id']} — {a['title']}", f"- Status: **{a['traffic_light']}**",
                f"- License: {a['license']}", f"- Source: {a['source_page']}", "",
            ]
    (meta / "CREDITS.md").write_text("\n".join(credit_lines), encoding="utf-8")
    refs = ["# REFERENCE-ONLY SOURCES", ""]
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
    media_count = sum(1 for a in assets if a.get("auto_download"))
    ref_count = len(assets) - media_count
    print(
        "NOESIS Asset Phase 2 — resilient downloader\n"
        f"Root: {root}\n"
        f"Assets selected: {len(assets)} ({media_count} media + {ref_count} reference-only)\n"
        "Quality filtering: OFF (no dimension threshold)\n"
        f"Wikimedia preferred fallback widths: {WIKIMEDIA_WIDTHS if not args.no_wikimedia_thumbnails else 'disabled'}\n"
    )

    report: list[dict[str, Any]] = []
    for asset in assets:
        if asset.get("auto_download"):
            try:
                report.append(download(
                    asset, root, args.timeout, args.retries, args.force, args.dry_run,
                    args.wikimedia_delay, not args.no_wikimedia_thumbnails,
                ))
            except BaseException as exc:
                if isinstance(exc, KeyboardInterrupt):
                    raise
                error = f"{type(exc).__name__}: {exc}"
                print(f"FAIL {asset['id']}: unexpected {error}; continuing", file=sys.stderr)
                report.append({
                    "id": asset["id"], "status": "FAILED", "error": error,
                    "source_url": asset.get("download_url"),
                })
        else:
            ref_path = write_reference_file(asset, root)
            print(f"REF  {asset['id']}: {ref_path}")
            report.append({
                "id": asset["id"], "status": "REFERENCE_ONLY",
                "path": str(ref_path), "url": asset["source_page"],
            })

    write_meta(root, assets, report, args.manifest)
    counts: dict[str, int] = {}
    for r in report:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print("\nSummary:")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    print(f"\nMetadata: {root / '_META'}")

    failed = [r for r in report if r["status"] == "FAILED"]
    if failed:
        print("\nFailed assets (rerun later; successful files will be skipped):")
        for r in failed:
            print(f"  - {r['id']}: {r.get('error', 'unknown')}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
