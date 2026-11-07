#!/usr/bin/env python3
"""Check whether PNG-quantized geometry channels agree; benchmark control only."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

def check(folder: Path):
    meta = json.loads((folder/"atlas.json").read_text())
    raw = np.asarray(Image.open(folder/"depth_u16.png"),dtype=np.float64)
    qnorm = np.asarray(Image.open(folder/"normal_rgb.png"),dtype=np.float64)
    if raw.shape[:2] != qnorm.shape[:2] or qnorm.shape[2] != 3:
        raise ValueError("Depth and normal image dimensions do not match")
    z = meta["z_min"] + (raw / 65535) * (meta["z_max"]-meta["z_min"])
    ny,nx = z.shape
    # Image row increases downward while geometric Y increases upward.
    dz_dy = np.gradient(z, axis=0) / (-meta["world_width_y"] / ny)
    dz_dx = np.gradient(z, axis=1) / (meta["world_length_x"] / nx)
    derived = np.stack([-dz_dx, -dz_dy, np.ones_like(z)],axis=-1)
    derived /= np.linalg.norm(derived,axis=-1,keepdims=True)
    encoded = (qnorm / 255) * 2 - 1
    norms = np.linalg.norm(encoded,axis=-1)
    encoded /= np.maximum(norms[...,None],1e-12)
    # Exclude image boundaries where first derivatives have one-sided differences.
    dot = np.clip(np.sum(derived[1:-1,1:-1]*encoded[1:-1,1:-1],axis=-1),-1,1)
    errors_deg = np.degrees(np.arccos(dot))
    result = {
        "status": "validated", "input_provenance": "known analytic surface, not an AI result",
        "pixels": [nx, ny],
        "mean_angular_disagreement_deg": float(errors_deg.mean()),
        "p95_angular_disagreement_deg": float(np.percentile(errors_deg,95)),
        "max_angular_disagreement_deg": float(errors_deg.max()),
        "mean_encoded_normal_norm_before_renormalization": float(norms.mean()),
        "note": "Small residuals reflect derivative approximation and 8/16-bit channel quantization, not physical inference."
    }
    if not np.isfinite(errors_deg).all() or float(errors_deg.mean()) > 2.0:
        raise AssertionError("Known-geometry depth/normal consistency failed")
    (folder/"consistency.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--folder",type=Path,default=Path("runs/atlas-fixture"))
    args=p.parse_args()
    check(args.folder)
