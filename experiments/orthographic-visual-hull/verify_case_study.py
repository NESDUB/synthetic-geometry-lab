#!/usr/bin/env python3
"""Regression test for the Nov 2026 three-view visual-hull case study."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

EXPECTED_SHA256 = "003cb3aa0715e11474251f77f3fa6ae8830981926150a06e013958b669ac4933"
EXPECTED_VERTICES = 51432
EXPECTED_FACES = 102860
EXPECTED_VOLUME = 0.2728970579109498


def run(command):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(command, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--images", type=Path, required=True,
                    help="Folder containing the three original Nov 7 2026 PNG files")
    ap.add_argument("--strict-hash", action="store_true",
                    help="Require byte-identical OBJ on this platform and package set")
    args = ap.parse_args()
    root = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="three-view-hull-") as temp:
        work = Path(temp)
        traced, out = work / "traced", work / "mesh"
        run([sys.executable, root / "trace_blueprints.py",
             "--images", args.images, "--out", traced])
        run([sys.executable, root / "visual_hull.py",
             "--traced", traced, "--out", out])
        report = json.loads((out / "diagnostics.json").read_text())
        mesh = report["mesh"]
        assert mesh["vertices"] == EXPECTED_VERTICES, mesh
        assert mesh["faces"] == EXPECTED_FACES, mesh
        assert abs(mesh["volume_wheelbase_cubed"] - EXPECTED_VOLUME) < 1e-8, mesh
        assert mesh["watertight"], mesh
        expected = {"top": 0.9991, "side": 0.9999, "front": 1.0}
        for view, target in expected.items():
            assert abs(report["projection_iou_at_voxel_resolution"][view] - target) < 0.0001
        digest = hashlib.sha256((out / "visual_hull_proxy.obj").read_bytes()).hexdigest()
        print(f"OBJ SHA-256: {digest}")
        if args.strict_hash:
            assert digest == EXPECTED_SHA256, "OBJ bytes changed; investigate software versions"
        print("PASS: original three-view case study regenerated at matching numeric resolution.")
        if digest == EXPECTED_SHA256:
            print("PASS: byte-for-byte OBJ match with the archived original.")
        else:
            print("NOTE: byte checksum differs; exact output depends on library/OS versions.")


if __name__ == "__main__":
    main()
