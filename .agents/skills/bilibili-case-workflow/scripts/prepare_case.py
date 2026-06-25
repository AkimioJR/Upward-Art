#!/usr/bin/env python3
"""Prepare and archive a Bilibili case workspace."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


BV_RE = re.compile(r"(BV[0-9A-Za-z]+)")
INDEXED_CASE_RE = re.compile(r"^(\d+)-")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Bilibili video URL")
    parser.add_argument(
        "--root",
        default=".",
        help="Workspace root that contains template/ and cases/",
    )
    parser.add_argument(
        "--archive-title",
        help="Archive the temporary workspace to cases/<next-index>-<title>/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print derived paths without writing files",
    )
    return parser.parse_args()


def extract_bv_id(url: str) -> str:
    match = BV_RE.search(url)
    if not match:
        raise SystemExit("Could not find a BV id in the URL")
    return match.group(1)


def sanitize_case_title(title: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "-", title.strip())
    cleaned = re.sub(r"\s+", "-", cleaned)
    cleaned = cleaned.strip(".- ")
    if not cleaned:
        raise SystemExit("Archive title cannot be empty")
    return cleaned


def next_case_index(cases_dir: Path) -> str:
    max_index = 0
    if cases_dir.exists():
        for child in cases_dir.iterdir():
            if child.is_dir():
                match = INDEXED_CASE_RE.match(child.name)
                if match:
                    max_index = max(max_index, int(match.group(1)))
    return f"{max_index + 1:03d}"


def copy_missing_templates(template_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("README.md", "script.md"):
        target = target_dir / filename
        if not target.exists():
            shutil.copy2(template_dir / filename, target)


def copy_tree_without_overwrite(source_dir: Path, target_dir: Path) -> None:
    if target_dir.exists():
        raise SystemExit(f"Archive directory already exists: {target_dir}")
    target_dir.mkdir(parents=True)
    for item in source_dir.iterdir():
        target = target_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    bv_id = extract_bv_id(args.url)
    template_dir = root / "template"
    cases_dir = root / "cases"
    work_dir = root / ".tmp" / "bilibili-case-workflow" / bv_id

    print(f"work_dir: {work_dir}")
    print(f"download_url: https://www.bilibili.com/video/{bv_id}/")
    print(f"download_target: {work_dir / 'source.mp4'}")

    if args.archive_title:
        archive_title = sanitize_case_title(args.archive_title)
        archive_dir = cases_dir / f"{next_case_index(cases_dir)}-{archive_title}"
        print(f"archive_dir: {archive_dir}")
        if not args.dry_run:
            copy_tree_without_overwrite(work_dir, archive_dir)
        return 0

    if not args.dry_run:
        copy_missing_templates(template_dir, work_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
