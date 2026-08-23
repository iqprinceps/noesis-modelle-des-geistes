#!/usr/bin/env python3
"""Shared resilient asset-fetch engine for NOESIS manifest packages.

This module is intentionally generic. Episode wrappers provide a CSV manifest
and a local output root. The engine never filters media by pixel dimensions.
Rights/evidence gates remain manifest-driven: GREEN/YELLOW auto-download rows
are attempted by default; RED/manual/reference rows become local sidecars.

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
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

USER_AGENT = (
    "NOESIS-Asset-Fetcher/3.1 "
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
    return bool(set(asset.get("episodes_list", [])) & set(only))


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
        "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
        "image/tiff": ".tif", "application/pdf": ".pdf", "application/zip": ".zip",
        "video/mp4": ".mp4", "video/quicktime": ".mov",
    }
    return mapping.get(ctype) or mimetypes.guess_extension(ctype)


def expected_ok(kind: str, ext: str | None, content_type: str | None, header: bytes) -> tuple[bool, str]:
    """Safety/type validation only. No pixel-size or visual-quality threshold."""
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    stripped = header.lstrip().lower()
    if ctype.startswith("text/html") or stripped.startswith(b"<!doctype html") or stripped.startswith(b"<html"):
        return False, "received HTML instead of media"
    kind = (kind or "detect").lower()
    if kind in {"none", "detect", "file"}:
        return True, ""
    if kind == "image":
        if ext in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"} or ctype.startswith("image/"):
            return True, ""
        return False, f"expected image, got content-type={content_type!r}, magic-ext={ext!r}"
    if kind == "pdf":
        if ext == ".pdf" or ctype == "application/pdf":
            return True, ""
        return False, f"expected PDF, got content-type={content_type!r}, magic-ext={ext!r}"
    if kind == "video":
        if ctype.startswith("video/") or ext in {".mp4", ".mov", ".webm"}:
            return True, ""
        return False, f"expected video, got content-type={content_type!r}, magic-ext={ext!r}"
    return True, ""


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
    if not enabled or (expected_kind or "").lower() != "image" or not is_wikimedia(url):
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


def throttle(url: str, delay: float) -> None:
    if not is_wikimedia(url):
        return
    host = host_key(url)
    now = time.monotonic()
    previous = _LAST_HOST_REQUEST.get(host)
    if previous is not None:
        remain = delay - (now - previous)
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


def retry_wait(attempt: int, exc: BaseException) -> float:
    retry_after = retry_after_seconds(exc)
    status = exc.code if isinstance(exc, HTTPError) else None
    base = min(120.0, 10.0 * (2 ** (attempt - 1))) if status in {429, 503} else min(30.0, 2.0 * (2 ** (attempt - 1)))
    if retry_after is not None:
        base = max(base, retry_after)
    return base + random.uniform(0.4, 1.8)


def existing_target(out_dir: Path, requested_name: str) -> Path | None:
    requested = Path(requested_name)
    if requested.suffix:
        p = out_dir / requested.name
        return p if p.exists() else None
    matches = [p for p in out_dir.glob(requested.name + ".*")
               if p.is_file() and not p.name.endswith(".license.txt") and not p.name.endswith(".part")]
    return matches[0] if matches else None


def choose_target(out_dir: Path, requested_name: str, detected_ext: str | None, content_type: str | None) -> Path:
    requested = Path(requested_name)
    if requested.suffix:
        return out_dir / requested.name
    ext = detected_ext or ext_from_content_type(content_type) or ".bin"
    return out_dir / f"{requested.name}{ext}"


def write_license_sidecar(media_path: Path, asset: dict[str, Any], final_url: str = "") -> None:
    sidecar = Path(str(media_path) + ".license.txt")
    lines = [
        f"ID: {asset.get('id', '')}",
        f"Episode(s): {asset.get('episodes', '')}",
        f"Title: {asset.get('title', '')}",
        f"Traffic light: {asset.get('traffic_light', '')}",
        f"License/status: {asset.get('license', '')}",
        f"Source page: {asset.get('source_page', '')}",
        f"Manifest download URL: {asset.get('download_url', '')}",
        f"Resolved final URL: {final_url}",
    ]
    for key, label in (("verification_date", "Verified date"), ("verification_status", "Verification"),
                       ("script_act", "Script act"), ("shot_use", "Shot use"), ("note", "Note")):
        if asset.get(key):
            lines.append(f"{label}: {asset[key]}")
    lines += ["", "Production rule: traffic-light status does not override context/date/evidence notes."]
    sidecar.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reference_file(asset: dict[str, Any], root: Path) -> Path:
    out_dir = root / (asset.get("relative_dir") or "REFERENCE_ONLY")
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = asset.get("filename") or f"{asset['id']}.url.txt"
    p = out_dir / filename
    if p.suffix.lower() not in {".txt", ".url"} and not asset.get("auto_download_bool"):
        p = out_dir / f"{filename}.url.txt"
    p.write_text("\n".join([
        f"ID={asset.get('id', '')}", f"EPISODES={asset.get('episodes', '')}",
        f"TITLE={asset.get('title', '')}", f"TRAFFIC_LIGHT={asset.get('traffic_light', '')}",
        f"LICENSE={asset.get('license', '')}", f"SOURCE_PAGE={asset.get('source_page', '')}",
        f"DIRECT_URL={asset.get('download_url', '')}", f"NOTE={asset.get('note', '')}",
    ]) + "\n", encoding="utf-8")
    return p


def source_fallbacks(asset: dict[str, Any], timeout: int, wikimedia_delay: float) -> list[str]:
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
        if ("/download/" in path or "/iiif/" in path or
                path.endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".pdf", ".zip", ".mp4", ".mov"))):
            if absolute != direct and absolute not in found:
                found.append(absolute)
    return found[:20]


def request_once(url: str, asset: dict[str, Any], out_dir: Path, requested_name: str,
                 timeout: int, force: bool, wikimedia_delay: float) -> dict[str, Any]:
    throttle(url, wikimedia_delay)
    req = Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/apng,image/*,video/*,application/pdf,application/zip,*/*;q=0.8",
    })
    with urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("Content-Type")
        final_url = resp.geturl()
        header = resp.read(64)
        magic_ext, detected_mime = detect_magic(header)
        ok, why = expected_ok(asset.get("expected_kind", "detect"), magic_ext, content_type, header)
        if not ok:
            raise RuntimeError(why)
        target = choose_target(out_dir, requested_name, magic_ext, content_type)
        if target.exists() and not force:
            digest = sha256(target)
            write_license_sidecar(target, asset, final_url)
            return {"id": asset["id"], "status": "EXISTS", "path": str(target),
                    "bytes": target.stat().st_size, "sha256": digest, "final_url": final_url}
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
    write_license_sidecar(target, asset, final_url)
    return {"id": asset["id"], "status": "DOWNLOADED", "path": str(target),
            "bytes": target.stat().st_size, "sha256": digest, "content_type": content_type,
            "detected_mime": detected_mime, "source_url": asset.get("download_url"), "final_url": final_url}


RETRIABLE = (HTTPError, URLError, TimeoutError, socket.timeout, ConnectionResetError,
             BrokenPipeError, IncompleteRead, RemoteDisconnected, OSError, RuntimeError)


def download_asset(asset: dict[str, Any], root: Path, args: argparse.Namespace) -> dict[str, Any]:
    out_dir = root / (asset.get("relative_dir") or "MEDIA")
    out_dir.mkdir(parents=True, exist_ok=True)
    requested_name = asset.get("filename") or asset["id"]
    direct = asset.get("download_url") or ""
    if args.dry_run:
        print(f"DRY  {asset.get('traffic_light', ''):6} {asset['id']}: {direct}")
        return {"id": asset["id"], "status": "DRY_RUN", "direct_url": direct}
    if not direct:
        return {"id": asset["id"], "status": "NO_DIRECT_URL"}
    if not args.force:
        existing = existing_target(out_dir, requested_name)
        if existing:
            digest = sha256(existing)
            write_license_sidecar(existing, asset)
            print(f"SKIP {asset['id']}: exists -> {existing}")
            return {"id": asset["id"], "status": "EXISTS", "path": str(existing),
                    "bytes": existing.stat().st_size, "sha256": digest}

    candidates = wikimedia_candidates(direct, asset.get("expected_kind", "detect"),
                                      not args.no_wikimedia_thumbnails)
    fallback_added = False
    last_error = "unknown"
    tried: list[dict[str, Any]] = []
    idx = 0
    while idx < len(candidates):
        candidate_url, variant = candidates[idx]
        idx += 1
        for attempt in range(1, args.retries + 1):
            try:
                result = request_once(candidate_url, asset, out_dir, requested_name,
                                      args.timeout, args.force, args.wikimedia_delay)
                result["retrieval_variant"] = variant
                result["attempt"] = attempt
                print(f"OK   {asset['id']}: {result['path']} ({result.get('bytes', 0):,} bytes; {variant})")
                return result
            except RETRIABLE as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                status = exc.code if isinstance(exc, HTTPError) else None
                tried.append({"variant": variant, "url": candidate_url, "attempt": attempt,
                              "status": status, "error": last_error})
                if (not fallback_added and isinstance(exc, RuntimeError)
                        and "received HTML instead of media" in str(exc)):
                    for fallback in source_fallbacks(asset, args.timeout, args.wikimedia_delay):
                        if all(fallback != known for known, _ in candidates):
                            candidates.append((fallback, "source-page-fallback"))
                    fallback_added = True
                if attempt < args.retries:
                    wait = retry_wait(attempt, exc)
                    print(f"WARN {asset['id']}: {variant} attempt {attempt}/{args.retries} failed "
                          f"({last_error}); retry in {wait:.1f}s", file=sys.stderr)
                    time.sleep(wait)
                else:
                    print(f"WARN {asset['id']}: {variant} exhausted after {args.retries} attempts "
                          f"({last_error}); trying next candidate if available", file=sys.stderr)
    print(f"FAIL {asset['id']}: {last_error}", file=sys.stderr)
    return {"id": asset["id"], "status": "FAILED", "error": last_error,
            "direct_url": direct, "tried": tried}


def write_meta(root: Path, assets: list[dict[str, Any]], report: list[dict[str, Any]], manifest: Path) -> None:
    meta = root / "_META"
    meta.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest, meta / ("asset_manifest_used" + manifest.suffix.lower()))
    with (meta / "DOWNLOAD_RESULTS.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields = ["id", "status", "path", "bytes", "sha256", "final_url", "error"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report)
    (meta / "download_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    credits = ["# Runtime asset credits", "", "Generated from the canonical manifest.", ""]
    for a in assets:
        if a.get("traffic_light") in {"GREEN", "YELLOW"}:
            credits += [f"## {a['id']} — {a.get('title', '')}",
                        f"- Traffic light: **{a.get('traffic_light', '')}**",
                        f"- License/status: {a.get('license', '')}",
                        f"- Source: {a.get('source_page', '')}", ""]
    (meta / "CREDITS.md").write_text("\n".join(credits), encoding="utf-8")


def build_parser(program_name: str, default_manifest: Path, default_root: Path,
                 only_choices: Sequence[str] | None) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=program_name, description=f"Download verified NOESIS assets for {program_name}.")
    p.add_argument("--manifest", type=Path, default=default_manifest)
    p.add_argument("--root", type=Path, default=default_root)
    if only_choices:
        p.add_argument("--only", choices=list(only_choices), action="append")
    else:
        p.set_defaults(only=None)
    p.add_argument("--green-only", action="store_true",
                   help="OPTIONAL: skip YELLOW assets. Default attempts GREEN + YELLOW.")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--timeout", type=int, default=90)
    p.add_argument("--retries", type=int, default=5)
    p.add_argument("--wikimedia-delay", type=float, default=2.0)
    p.add_argument("--no-wikimedia-thumbnails", action="store_true")
    return p


def main_for(program_name: str, default_manifest: Path, default_root: Path,
             only_choices: Sequence[str] | None = None, argv: Sequence[str] | None = None) -> int:
    args = build_parser(program_name, default_manifest, default_root, only_choices).parse_args(argv)
    assets = [a for a in load_manifest(args.manifest) if selected(a, args.only)]
    if args.green_only:
        assets = [a for a in assets if a.get("traffic_light") != "YELLOW"]
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    media_count = sum(1 for a in assets if a.get("traffic_light") in {"GREEN", "YELLOW"}
                      and a.get("auto_download_bool") and bool(a.get("download_url")))
    print(f"NOESIS resilient asset downloader — {program_name}\n"
          f"Root: {root}\nAssets selected: {len(assets)} ({media_count} auto-download candidates)\n"
          "Quality filtering: OFF (no dimension threshold)\n"
          f"Wikimedia preferred widths: {WIKIMEDIA_WIDTHS if not args.no_wikimedia_thumbnails else 'disabled'}\n")
    report: list[dict[str, Any]] = []
    for asset in assets:
        can_fetch = (asset.get("traffic_light") in {"GREEN", "YELLOW"}
                     and asset.get("auto_download_bool") and bool(asset.get("download_url")))
        if can_fetch:
            try:
                report.append(download_asset(asset, root, args))
            except BaseException as exc:
                if isinstance(exc, KeyboardInterrupt):
                    raise
                error = f"{type(exc).__name__}: {exc}"
                print(f"FAIL {asset['id']}: unexpected {error}; continuing", file=sys.stderr)
                report.append({"id": asset["id"], "status": "FAILED", "error": error,
                               "direct_url": asset.get("download_url")})
        else:
            ref = write_reference_file(asset, root)
            status = "MANUAL_SOURCE" if asset.get("download_url") else "REFERENCE_ONLY"
            print(f"REF  {asset['id']}: {ref}")
            report.append({"id": asset["id"], "status": status, "path": str(ref)})
    write_meta(root, assets, report, args.manifest)
    counts: dict[str, int] = {}
    for item in report:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    print("\nSummary:")
    for status, count in sorted(counts.items()):
        print(f"  {status}: {count}")
    failed = [item for item in report if item["status"] == "FAILED"]
    if failed:
        print("\nFailed assets (rerun later; successful files will be skipped):")
        for item in failed:
            print(f"  - {item['id']}: {item.get('error', 'unknown')}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit("Use an episode wrapper, e.g. download_ep04ab_assets.py or download_ep05_assets.py")
