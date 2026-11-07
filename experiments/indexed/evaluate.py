#!/usr/bin/env python3
"""Compare predicted per-view indexed landmarks against known geometry."""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean

SCALE, CX, CY = 900.0, 540.0, 360.0
VIEWS = {"side", "top", "front"}

def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def evaluate(truth_path: Path, pred_path: Path) -> dict:
    truth = {r["point_id"]: r for r in rows(truth_path)}
    predicted = {}
    invalid, duplicates = 0, 0
    for p in rows(pred_path):
        key = (p["point_id"], p["view"])
        if p["point_id"] not in truth or p["view"] not in VIEWS:
            invalid += 1
            continue
        if key in predicted:
            duplicates += 1
            continue
        predicted[key] = (float(p["u_px"]), float(p["v_px"]))
    errs = []
    for (pid, view), (u, v) in predicted.items():
        t = truth[pid]
        errs.extend([(u - float(t[f"{view}_u"]))**2, (v - float(t[f"{view}_v"]))**2])
    mismatches = []
    for pid in truth:
        a, b, c = (predicted.get((pid, view)) for view in ("side", "top", "front"))
        if a and b and c:
            # Shared X: side.u and top.u; shared Y: top.v and front.u;
            # shared Z: side.v and front.v.
            mismatches.extend([((a[0] - b[0]) / SCALE)**2,
                               (((CY - b[1]) - (c[0] - CX)) / SCALE)**2,
                               ((a[1] - c[1]) / SCALE)**2])
    return {"truth_points": len(truth), "expected_view_observations": len(truth) * 3,
            "unique_matched_observations": len(predicted),
            "coverage": len(predicted) / max(1, len(truth) * 3),
            "invalid_predictions": invalid, "duplicate_predictions": duplicates,
            "coordinate_rmse_px": math.sqrt(mean(errs)) if errs else None,
            "cross_view_disagreement_rmse_units": math.sqrt(mean(mismatches)) if mismatches else None,
            "matched_triplets": len(mismatches) // 3,
            "note": "Pixel coordinates are truth-matched by *explicit* ID; no inferred correspondences."}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("truth_csv", type=Path)
    parser.add_argument("predictions_csv", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.truth_csv, args.predictions_csv), indent=2))
