#!/usr/bin/env python3
"""
kenney_dl.py - download Kenney's free CC0 asset packs from kenney.nl.

Stdlib only. Polite by default (delay between requests), resumable
(skips zips you already have), and can filter by category.

Usage:
    python3 kenney_dl.py                     # everything
    python3 kenney_dl.py --category 3D       # just 3D
    python3 kenney_dl.py --category 3D --category Audio --out ~/Kenney
    python3 kenney_dl.py --list              # list packs, don't download

Please consider supporting Kenney: https://kenney.nl/donate
or buy the All-in-1 bundle: https://kenney.itch.io/kenney-game-assets
"""

import argparse
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://kenney.nl"
UA = "kenney-dl/1.0 (+https://github.com/astagename/kenney-dl; polite CC0 asset downloader)"
CATEGORIES = ["2D", "3D", "Audio", "Textures", "UI", "Pixel"]
# UI and Pixel are tags on the site, the rest are categories
LISTING_PATH = {
    "2D": "category:2D",
    "3D": "category:3D",
    "Audio": "category:Audio",
    "Textures": "category:Textures",
    "UI": "tag:interface",
    "Pixel": "tag:pixel",
}

ASSET_RE = re.compile(r"""href=["']https://kenney\.nl/assets/([a-z0-9][a-z0-9-]*)["']""")
PAGE_RE = re.compile(r"""/page:(\d+)["']""")
ZIP_RE = re.compile(r"""href=["'](https://kenney\.nl/media/pages/assets/[^"']+?\.zip)["']""")


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == retries - 1:
                raise
            wait = 5 * (attempt + 1)
            print(f"  ! {e} - retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)


def list_slugs(listing, delay):
    """Walk every page of a listing and return asset slugs in order."""
    first = fetch(f"{BASE}/assets/{listing}").decode("utf-8", "replace")
    pages = max([int(p) for p in PAGE_RE.findall(first)] or [1])
    slugs = []
    for n in range(1, pages + 1):
        html = first if n == 1 else fetch(
            f"{BASE}/assets/{listing}/page:{n}").decode("utf-8", "replace")
        for s in ASSET_RE.findall(html):
            if s not in slugs:
                slugs.append(s)
        if n < pages:
            time.sleep(delay)
    return slugs


def zip_url(slug):
    html = fetch(f"{BASE}/assets/{slug}").decode("utf-8", "replace")
    m = ZIP_RE.search(html)
    return m.group(1) if m else None


def download(url, dest):
    tmp = dest.with_suffix(".part")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 16):
            f.write(chunk)
    tmp.rename(dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--category", action="append", choices=CATEGORIES,
                    help="limit to a category (repeatable). Default: all")
    ap.add_argument("--out", default="kenney_assets", help="output folder")
    ap.add_argument("--delay", type=float, default=1.5,
                    help="seconds between requests (be nice, default 1.5)")
    ap.add_argument("--list", action="store_true", help="list packs only")
    args = ap.parse_args()

    out = Path(args.out).expanduser()
    cats = args.category or CATEGORIES

    # Collect slugs per category; a pack in several categories goes in the first
    plan, seen = [], set()
    for cat in cats:
        print(f"Scanning {cat}...")
        for slug in list_slugs(LISTING_PATH[cat], args.delay):
            if slug not in seen:
                seen.add(slug)
                plan.append((cat, slug))
        time.sleep(args.delay)
    print(f"Found {len(plan)} packs.\n")

    if args.list:
        for cat, slug in plan:
            print(f"{cat:9} {slug}")
        return

    ok = skipped = failed = 0
    for i, (cat, slug) in enumerate(plan, 1):
        folder = out / cat
        folder.mkdir(parents=True, exist_ok=True)
        if any(folder.glob(f"*{slug}*.zip")):
            skipped += 1
            continue
        try:
            url = zip_url(slug)
            if not url:
                print(f"[{i}/{len(plan)}] {slug}: no free zip found, skipping")
                failed += 1
                continue
            dest = folder / url.rsplit("/", 1)[-1]
            print(f"[{i}/{len(plan)}] {cat}/{dest.name}")
            time.sleep(args.delay)
            download(url, dest)
            ok += 1
        except Exception as e:  # keep going on any single failure
            print(f"[{i}/{len(plan)}] {slug}: FAILED ({e})", file=sys.stderr)
            failed += 1
        time.sleep(args.delay)

    print(f"\nDone: {ok} downloaded, {skipped} already had, {failed} failed.")
    print("Enjoying these? https://kenney.nl/donate")


if __name__ == "__main__":
    main()
