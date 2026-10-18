"""Find files with the same contents. This project never deletes anything."""

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path


def file_hash(path):
    """Read in small chunks so a large file doesn't fill up memory."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(folder):
    """Return duplicate groups and warnings for files we couldn't read."""
    by_size = defaultdict(list)
    warnings = []

    def walk_error(error):
        warnings.append(str(error))

    # os.walk lets us report unreadable directories and skip directory links.
    import os
    for directory, folders, filenames in os.walk(folder, onerror=walk_error):
        folders[:] = sorted(
            name for name in folders
            if not (Path(directory) / name).is_symlink()
        )
        for name in sorted(filenames):
            path = Path(directory) / name
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                by_size[path.stat().st_size].append(path)
            except OSError as error:
                warnings.append(f"{path}: {error}")

    duplicates = []
    # Different sizes can't contain identical bytes, so skip hashing those.
    for size, paths in sorted(by_size.items()):
        if len(paths) < 2:
            continue
        by_hash = defaultdict(list)
        for path in paths:
            try:
                by_hash[file_hash(path)].append(path)
            except OSError as error:
                warnings.append(f"{path}: {error}")
        for matching_paths in by_hash.values():
            if len(matching_paths) > 1:
                duplicates.append((size, sorted(matching_paths)))
    return duplicates, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Folder to scan, including subfolders")
    args = parser.parse_args()
    if not args.folder.is_dir():
        parser.error("Please provide an existing directory.")

    groups, warnings = find_duplicates(args.folder)
    for number, (size, paths) in enumerate(groups, start=1):
        print(f"\nGroup {number}: {len(paths)} matching files, {size} bytes each")
        for path in paths:
            print(f"  {path}")

    extra_bytes = sum(size * (len(paths) - 1) for size, paths in groups)
    print(f"\nDuplicate groups: {len(groups)}")
    print(f"Extra content bytes: {extra_bytes}")
    print("Preview only. No files were changed.")
    for warning in warnings:
        print(f"Warning: {warning}")
    # A nonzero status tells scripts that the scan was incomplete.
    return 1 if warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
