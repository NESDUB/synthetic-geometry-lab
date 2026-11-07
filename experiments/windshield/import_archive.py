#!/usr/bin/env python3
"""Restore the user-supplied, checksum-pinned windshield POC archive.
Run from any directory. No external dependencies.
"""
from __future__ import annotations
import argparse
import hashlib
import pathlib
import shutil
import sys
import zipfile

EXPECTED_SHA256 = "13f2f5d42ca3ae9fd79ed6ef96cda6b6c3e18b2b7d52d7b3e5807d779e5b5d05"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO_ROOT / "runs" / "windshield-original"
PREFIX = pathlib.PurePosixPath("windshield-model")
REQUIRED = {
    "README.md", "validation.json", "models/surface.json",
    "source/build.py", "source/render.py", "source/load_geomdl.py",
    "reference/alignment.json",
    "reference/side.csv", "reference/top.csv",
    "reference/front.csv", "reference/rear.csv",
}

def restore(archive: pathlib.Path, out: pathlib.Path) -> None:
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"Unexpected archive SHA-256: {digest}\nExpected: {EXPECTED_SHA256}")
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"Destination not empty: {out}")
    with zipfile.ZipFile(archive) as zf:
        names = {str(pathlib.PurePosixPath(n).relative_to(PREFIX)) for n in zf.namelist()
                 if not n.endswith("/") and pathlib.PurePosixPath(n).parts[:1] == PREFIX.parts}
        missing = REQUIRED - names
        if missing:
            raise ValueError(f"Missing files: {sorted(missing)}")
        for info in zf.infolist():
            if info.is_dir():
                continue
            path = pathlib.PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != str(PREFIX):
                raise ValueError(f"Unsafe or unexpected archive entry: {info.filename}")
            rel = pathlib.Path(*path.parts[1:])
            target = out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, target.open("wb") as dest:
                shutil.copyfileobj(source, dest)
    print(f"Restored exact baseline to {out}")
    print(f"Archive SHA-256: {digest}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    try:
        restore(args.zip, args.out)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        sys.exit(str(exc))
