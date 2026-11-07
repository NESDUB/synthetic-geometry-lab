#!/usr/bin/env python3
"""Deterministic known-geometry 3-view landmark fixture. Standard library only."""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

SCALE = 900.0
CX, CY = 540.0, 360.0

def project(x: float, y: float, z: float, view: str) -> tuple[float, float]:
    axes = {"side": (x, z), "top": (x, y), "front": (y, z)}
    u, v = axes[view]
    return CX + SCALE * u, CY - SCALE * v

def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    points = []
    for i in range(11):
        x = -0.5 + i / 10
        for j in range(9):
            y = -0.32 + 0.64 * j / 8
            # The known surface is smooth and symmetric, with an absolute vertical offset.
            z = 0.02 + 0.18 * math.sin(math.pi * (x + 0.5)) * (1 - (y / 0.32) ** 2)
            pid = f"P{i:02d}_{j:02d}"
            points.append((pid, x, y, z))
    with (out / "truth.csv").open("w", newline="") as f:
        fields = ["point_id", "x", "y", "z"] + [f"{view}_{a}" for view in ("side", "top", "front") for a in ("u", "v")]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for pid, x, y, z in points:
            row = {"point_id": pid, "x": x, "y": y, "z": z}
            for view in ("side", "top", "front"):
                row[f"{view}_u"], row[f"{view}_v"] = project(x, y, z, view)
            writer.writerow(row)
    for view in ("side", "top", "front"):
        parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="720" viewBox="0 0 1080 720">',
                 '<rect width="1080" height="720" fill="#101216"/>',
                 '<line x1="40" y1="360" x2="1040" y2="360" stroke="#67717b" stroke-width="1"/>',
                 '<line x1="540" y1="30" x2="540" y2="690" stroke="#67717b" stroke-width="1"/>']
        for pid, x, y, z in points:
            u, v = project(x, y, z, view)
            parts += [f'<circle cx="{u:.4f}" cy="{v:.4f}" r="4.2" fill="#ff38b6" stroke="#fff" stroke-width=".6"/>',
                      f'<text x="{u+6:.4f}" y="{v-5:.4f}" fill="#e8e8ec" font-size="7" font-family="monospace">{pid}</text>']
        parts += [f'<text x="28" y="32" fill="#fff" font-family="monospace" font-size="18">{view.upper()} · exact projection · SCALE=900px/unit</text>',
                  '</svg>']
        (out / f"{view}.svg").write_text("\n".join(parts))
    manifest = {"status": "validated", "source": "deterministic formula, NOT image-generated",
                "point_count": len(points), "scale_px_per_unit": SCALE,
                "pixel_origin": [CX, CY], "views": {"side": ["x", "z"], "top": ["x", "y"], "front": ["y", "z"]},
                "image_size": [1080, 720], "units": "relative",
                "note": "Some point projections overlap; identities cannot always be visually resolved."}
    (out / "fixture.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Generated {len(points)} matched 3D points and 3 exact SVG views in {out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("runs/indexed-fixture"))
    args = parser.parse_args()
    main(args.out)
