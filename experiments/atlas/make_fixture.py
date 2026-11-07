#!/usr/bin/env python3
"""Make a deterministic, calibrated synthetic geometry atlas, not AI imagery."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

LENGTH, WIDTH = 1.0, 0.6

def surface(u, v):
    """Analytic height and its derivatives w.r.t. unit-interval u and v."""
    z = 0.04 + 0.16 * np.sin(np.pi * u) * (1 - (2 * v - 1) ** 2) + 0.02 * np.sin(2 * np.pi * u) * np.sin(np.pi * v)
    zu = (0.16 * np.pi * np.cos(np.pi * u) * (1 - (2 * v - 1)**2)
          + 0.04 * np.pi * np.cos(2 * np.pi * u) * np.sin(np.pi * v))
    zv = (-0.64 * np.sin(np.pi * u) * (2 * v - 1)
          + 0.02 * np.pi * np.sin(2 * np.pi * u) * np.cos(np.pi * v))
    return z, zu, zv

def build(out: Path, n: int):
    out.mkdir(parents=True, exist_ok=True)
    # Pixel (0,0) is at left/top. v increases upwards in geometric coordinates.
    u = (np.arange(n, dtype=np.float64) + 0.5)[None, :] / n
    v = 1 - (np.arange(n, dtype=np.float64) + 0.5)[:, None] / n
    z, zu, zv = surface(u, v)
    px = np.broadcast_to(zu / LENGTH, (n, n))
    py = np.broadcast_to(zv / WIDTH, (n, n))
    normal = np.stack([-px, -py, np.ones_like(px)], axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    rgb = np.round(255 * (normal + 1) / 2).clip(0,255).astype(np.uint8)
    Image.fromarray(rgb, mode="RGB").save(out / "normal_rgb.png")

    z_min, z_max = float(z.min()), float(z.max())
    depth = np.round(65535 * (z - z_min) / (z_max - z_min)).astype(np.uint16)
    Image.fromarray(depth).save(out / "depth_u16.png")

    # Visualization-only contour and UV curves; numeric data is in depth + metadata.
    interval = 0.02
    dist = np.abs(z / interval - np.round(z / interval)) * interval
    contours = np.zeros((n, n, 3), dtype=np.uint8)
    contours[:] = [18, 22, 28]
    contours[dist < interval / 30] = [253, 242, 232]
    Image.fromarray(contours, mode="RGB").save(out / "contours.png")
    uv = np.zeros((n,n,3), dtype=np.uint8)
    uv[:] = [24,28,34]
    step = max(1, n // 12)
    uv[::step,:,:] = [190,205,214]
    uv[:,::step,:] = [190,205,214]
    Image.fromarray(uv, mode="RGB").save(out / "uv_grid.png")
    meta = {
        "status": "executed", "source": "deterministic analytic surface; NOT image-generated",
        "surface": "z=0.04+0.16*sin(pi*u)*(1-(2*v-1)^2)+0.02*sin(2*pi*u)*sin(pi*v)",
        "width_px": n, "height_px": n, "world_length_x": LENGTH,
        "world_width_y": WIDTH, "units": "relative",
        "pixel_center_u": "(column+0.5)/N",
        "pixel_center_v": "1-(row+0.5)/N",
        "z_min": z_min, "z_max": z_max,
        "depth_encoding": "uint16 linear z_min..z_max, valid entire rectangle",
        "normal_encoding": "RGB uint8, round(255*(component+1)/2), component basis XYZ",
        "normal_orientation": "positive Z",
        "contour_interval_z": interval,
        "notes": ["UV-grid is a visualization of parameter coordinates, not control points",
                  "Contours are nearest-isoline visual approximations",
                  "Quantized normals will not match depth-derived normals exactly"]
    }
    (out/"atlas.json").write_text(json.dumps(meta, indent=2)+"\n")
    print(f"Wrote known-geometry atlas: {n}x{n}, z in [{z_min:.6f}, {z_max:.6f}]")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("runs/atlas-fixture"))
    p.add_argument("--size", type=int, default=384)
    args = p.parse_args()
    if args.size < 32:
        p.error("--size must be at least 32")
    build(args.out, args.size)
