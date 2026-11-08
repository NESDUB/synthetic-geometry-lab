#!/usr/bin/env python3
"""Reproduce the November 2026 concept-car visual hull from three traced masks.

Input is the *unmodified* `vehicle-traced-blueprints/` directory within the
vehicle-aligned-references archive. All output dimensions are wheelbase ratios,
never meters. The script reconstructs the same mask warps, voxel grid, smoothing,
and marching-cubes geometry as the case-study generation pipeline.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes
import trimesh

CANVAS_W, CANVAS_H = 1800, 1050
PIXELS_PER_WHEELBASE = 900.0
CENTER_X, TOP_CENTER_Y, ELEV_CENTER_Y = 900.0, 525.0, 680.0
GRID = ((-0.84, 0.83, 185), (-0.355, 0.355, 85), (-0.128, 0.292, 68))


def load_geometry(traced: Path):
    return {v: json.loads((traced / f"{v}_geometry.json").read_text())
            for v in ('top', 'side', 'front')}


def registration(geo):
    side, top, front = (geo[k] for k in ('side', 'top', 'front'))
    sf, sr = (p[0] for p in side['wheel_centerpoints_px'])
    tf, tr = top['wheel_centerpoints_px'][0][0], top['wheel_centerpoints_px'][1][0]
    sb, tb = sr - sf, tr - tf
    if sb <= 0 or tb <= 0:
        raise ValueError('Front and rear axle centers must be ordered by increasing x')
    side_y = float(np.mean([p[1] for p in side['wheel_centerpoints_px']]))
    top_y = float(np.mean([p[1] for p in top['wheel_centerpoints_px']]))
    front_y = float(np.mean([p[1] for p in front['wheel_centerpoints_px']]))
    front_x = float(np.mean([p[0] for p in front['wheel_centerpoints_px']]))
    track = abs(top['wheel_centerpoints_px'][2][1] - top['wheel_centerpoints_px'][0][1]) / tb
    front_ppu = (front['wheel_centerpoints_px'][1][0] - front['wheel_centerpoints_px'][0][0]) / track
    oh_front = {'side': (sf - side['outer_bbox_px'][0]) / sb,
                'top': (tf - top['outer_bbox_px'][0]) / tb}
    oh_rear = {'side': (side['outer_bbox_px'][2] - sr) / sb,
               'top': (top['outer_bbox_px'][2] - tr) / tb}
    target_front, target_rear = np.mean(list(oh_front.values())), np.mean(list(oh_rear.values()))
    roof = {'side': (side_y - side['outer_bbox_px'][1]) / sb,
            'front': (front_y - front['outer_bbox_px'][1]) / front_ppu}
    below = {'side': (side['outer_bbox_px'][3] - side_y) / sb,
             'front': (front['outer_bbox_px'][3] - front_y) / front_ppu}
    target_roof, target_below = np.mean(list(roof.values())), np.mean(list(below.values()))
    if min(track, front_ppu, target_front, target_rear, target_roof, target_below) <= 0:
        raise ValueError('Degenerate mask registration: verify landmarks and bounds')
    views = {'top': (tf, tr, tb, top_y),
             'side': (sf, sr, sb, side_y),
             'front': (front_x, front_x, front_ppu, front_y)}
    report = {'wheelbase': 1.0, 'track_ratio': float(track),
              'overhang_front_ratio': float(target_front),
              'overhang_rear_ratio': float(target_rear),
              'roof_above_axle_ratio': float(target_roof),
              'ground_below_axle_ratio': float(target_below),
              'individual_overhangs': {'front': oh_front, 'rear': oh_rear},
              'individual_heights': {'roof': roof, 'ground': below}}
    return views, oh_front, oh_rear, roof, below, report


def remap_source_mask(mask, view, registration_data):
    views, foh, roh, roof, below, report = registration_data
    axle_f, axle_r, source_ppu, anchor_y = views[view]
    target_front = report['overhang_front_ratio']
    target_rear = report['overhang_rear_ratio']
    target_roof = report['roof_above_axle_ratio']
    target_below = report['ground_below_axle_ratio']
    xs = np.arange(CANVAS_W, dtype=np.float32)[None, :]
    ys = np.arange(CANVAS_H, dtype=np.float32)[:, None]
    if view != 'front':
        world_x = (xs - CENTER_X) / PIXELS_PER_WHEELBASE
        # Exact axle anchors x=-0.5 and +0.5; independent linear overhang warp.
        source_x = np.where(world_x < -.5,
            axle_f + (world_x + .5) * source_ppu * foh[view] / target_front,
            np.where(world_x > .5,
                axle_r + (world_x - .5) * source_ppu * roh[view] / target_rear,
                axle_f + (world_x + .5) * source_ppu))
        mx = np.broadcast_to(source_x, (CANVAS_H, CANVAS_W)).copy()
    if view == 'top':
        world_y = (ys - TOP_CENTER_Y) / PIXELS_PER_WHEELBASE
        source_y = anchor_y + world_y * source_ppu
        my = np.broadcast_to(source_y, (CANVAS_H, CANVAS_W)).copy()
    else:
        world_z = (ELEV_CENTER_Y - ys) / PIXELS_PER_WHEELBASE
        source_y = anchor_y - np.where(world_z >= 0,
            world_z * roof[view] / target_roof,
            world_z * below[view] / target_below) * source_ppu
        my = np.broadcast_to(source_y, (CANVAS_H, CANVAS_W)).copy()
        if view == 'front':
            world_y = (CENTER_X - xs) / PIXELS_PER_WHEELBASE
            source_x = axle_f - world_y * source_ppu
            mx = np.broadcast_to(source_x, (CANVAS_H, CANVAS_W)).copy()
    return cv2.remap(mask, mx.astype(np.float32), my.astype(np.float32),
                     cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def contains(mask, pixel_x, pixel_y):
    ix, iy = np.broadcast_arrays(np.rint(pixel_x).astype(int), np.rint(pixel_y).astype(int))
    valid = (ix >= 0) & (ix < CANVAS_W) & (iy >= 0) & (iy < CANVAS_H)
    result = np.zeros(ix.shape, dtype=bool)
    result[valid] = mask[iy[valid], ix[valid]] != 0
    return result


def reconstruct(aligned_masks, sigma=.56):
    x, y, z = [np.linspace(lo, hi, n, dtype=np.float32) for lo, hi, n in GRID]
    scale = PIXELS_PER_WHEELBASE
    xy = contains(aligned_masks['top'], CENTER_X + scale * x[:, None],
                  TOP_CENTER_Y + scale * y[None, :])
    xz = contains(aligned_masks['side'], CENTER_X + scale * x[:, None],
                  ELEV_CENTER_Y - scale * z[None, :])
    yz = contains(aligned_masks['front'], CENTER_X - scale * y[:, None],
                  ELEV_CENTER_Y - scale * z[None, :])
    occupancy = xy[:, :, None] & xz[:, None, :] & yz[None, :, :]
    if not occupancy.any():
        raise ValueError('No common silhouette occupancy; check view orientation and registration')
    # Marching-cubes extracts level 0.5 of the blurred binary intersection.
    field = gaussian_filter(occupancy.astype(np.float32), sigma=sigma)
    vertices, faces, _, _ = marching_cubes(
        field, .5, spacing=(x[1]-x[0], y[1]-y[0], z[1]-z[0]))
    vertices += np.array([x[0], y[0], z[0]])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    # Projection IoU compares VOXEL occupation, not rendered mesh nor real-world truth.
    expected = {'top': xy, 'side': xz, 'front': yz}
    projection = {'top': occupancy.any(axis=2), 'side': occupancy.any(axis=1),
                  'front': occupancy.any(axis=0)}
    quality = {}
    for view in expected:
        numerator = np.count_nonzero(projection[view] & expected[view])
        denominator = np.count_nonzero(projection[view] | expected[view])
        quality[view] = float(numerator / denominator) if denominator else None
    return mesh, quality


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--traced', type=Path, required=True,
                        help='Directory containing top/side/front_area_mask.png and *_geometry.json')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--sigma', type=float, default=.56,
                        help='Gaussian blur in grid cells, matching the original .56')
    args = parser.parse_args()
    geo = load_geometry(args.traced)
    reg = registration(geo)
    args.out.mkdir(parents=True, exist_ok=True)
    aligned = {}
    for view in ('top', 'side', 'front'):
        src = cv2.imread(str(args.traced / f'{view}_area_mask.png'), cv2.IMREAD_GRAYSCALE)
        if src is None:
            raise FileNotFoundError(args.traced / f'{view}_area_mask.png')
        aligned[view] = remap_source_mask(src, view, reg)
        cv2.imwrite(str(args.out / f'aligned_mask_{view}.png'), aligned[view])
    mesh, metrics = reconstruct(aligned, sigma=args.sigma)
    mesh.export(args.out / 'visual_hull_proxy.obj')
    mesh.export(args.out / 'visual_hull_proxy.glb')
    diagnostics = {'normalization': reg[-1], 'grid': GRID, 'sigma': args.sigma,
                   'projection_iou_at_voxel_resolution': metrics,
                   'mesh': {'vertices': len(mesh.vertices), 'faces': len(mesh.faces),
                            'volume_wheelbase_cubed': abs(float(mesh.volume)),
                            'watertight': bool(mesh.is_watertight)}}
    (args.out / 'diagnostics.json').write_text(json.dumps(diagnostics, indent=2))
    print(json.dumps(diagnostics, indent=2))


if __name__ == '__main__':
    main()
