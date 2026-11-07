#!/usr/bin/env python3
"""Rebuild POC using the original supplied code and compare measured metrics."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POC = REPO_ROOT / "runs" / "windshield-original"
EXPECTED = {
    "side": 0.8687551053012535,
    "top": 5.100669594800991,
    "front": 4.666409403805031,
    "rear": 5.980677859447268,
}

def verify(poc: Path) -> None:
    build = poc / "source" / "build.py"
    baseline = poc / "validation.json"
    if not build.is_file() or not baseline.is_file():
        raise FileNotFoundError("Run import_archive.py first.")
    prior = json.loads(baseline.read_text())
    print("Running the unmodified source/build.py from the checksum-pinned ZIP...")
    subprocess.run([sys.executable, str(build)], check=True, cwd=poc)
    regenerated = json.loads(baseline.read_text())
    for view, reference in EXPECTED.items():
        got = regenerated[view]["envelope_rmse_reference_pixels"]
        archived = prior[view]["envelope_rmse_reference_pixels"]
        delta = abs(got - reference)
        print(f"{view:>5}: regenerated={got:.7f}px archived={archived:.7f}px expected={reference:.7f}px delta={delta:.8f}")
        if not (math.isfinite(got) and abs(got - archived) <= 1e-3 and delta <= 1e-3):
            raise AssertionError(f"{view} envelope did not reproduce the archived result")
    g = regenerated["geometry"]
    assert g["finite"] and g["winding_consistent"] and g["connected_components"] == 1
    assert g["open_surface_expected"] and g["minimum_interior_jacobian"] > 0
    assert regenerated["export_reload"] == "GLB and OBJ reloaded successfully"
    print("PASS: reproduced archived envelope metrics, topology checks and export/reload.")
    print("NOTE: this establishes baseline reproducibility, not physical 3D accuracy.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--poc", type=Path, default=DEFAULT_POC)
    args = parser.parse_args()
    try:
        verify(args.poc)
    except (OSError, ValueError, KeyError, AssertionError, subprocess.CalledProcessError) as exc:
        sys.exit(f"FAILED: {exc}")
