#!/usr/bin/env python3
"""Stage 1: trace cyan-line concept-car references into 2D binary silhouettes.

This reproduces the three masks and landmark geometry used in the 2026 case study.
Landmark positions and valid vertical body bands are manual annotations; confirm
and edit CONFIG for a *new* vehicle. No dimensions are asserted or inferred.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from scipy.ndimage import median_filter, gaussian_filter1d, percentile_filter

CONFIG = {
    'side': {
        'file': 'ChatGPT Image Nov 7, 2026, 06_59_21 PM-3.png',
        'band': [342, 713], 'guides': [326, 1127],
        'wheels': [[326, 600], [1127, 600]]},
    'front': {
        'file': 'ChatGPT Image Nov 7, 2026, 06_59_20 PM-2.png',
        'band': [218, 834], 'guides': [287, 1158],
        'wheels': [[287, 636], [1158, 636]]},
    'top': {
        'file': 'ChatGPT Image Nov 7, 2026, 06_59_20 PM-1.png',
        'band': [270, 803], 'guides': [362, 1085],
        'wheels': [[362, 332], [1085, 332], [362, 751], [1085, 751]]}}


def trace(image, view, config):
    b, g, r = cv2.split(image.astype(np.float32))
    bright_cyan = (g > 76) & (g > r * 1.65) & (b > g * .77)
    # Grid construction axes are the brightest long column and row.
    x_axis = int(bright_cyan.sum(axis=0).argmax())
    y_axis = int(bright_cyan.sum(axis=1).argmax())
    height, width = bright_cyan.shape
    allowed = bright_cyan.copy()
    lo, hi = config['band']
    allowed[:lo, :] = False
    allowed[hi:, :] = False
    allowed[max(0, y_axis - 5):y_axis + 6, :] = False
    allowed[:, max(0, x_axis - 7):x_axis + 8] = False
    for guide in config['guides']:
        allowed[:, guide - 5:guide + 6] = False
    upper = np.full(width, np.nan, dtype=np.float32)
    lower = np.full(width, np.nan, dtype=np.float32)
    span = np.zeros(width, dtype=np.float32)
    for x in range(width):
        ys = np.flatnonzero(allowed[:, x])
        if len(ys) > 1:
            upper[x] = ys[0]
            lower[x] = ys[-1]
            span[x] = ys[-1] - ys[0]
    valid = np.flatnonzero(span > 20)
    if len(valid) < 150:
        raise ValueError(f'{view}: contour not detected; check the image and CONFIG')
    start, stop = int(valid[0]), int(valid[-1])
    xs = np.arange(start, stop + 1)
    upper, lower = upper[start:stop + 1].copy(), lower[start:stop + 1].copy()
    for signal in (upper, lower):
        good = np.isfinite(signal)
        signal[~good] = np.interp(xs[~good], xs[good], signal[good])
    upper = median_filter(upper, 9)
    lower = median_filter(lower, 9)
    if view == 'front':
        lower = percentile_filter(lower, percentile=88, size=17, mode='nearest')
        lower = gaussian_filter1d(lower, 2.2)
    else:
        lower = gaussian_filter1d(lower, 1.35)
    upper = gaussian_filter1d(upper, 1.35)
    top_pts = np.stack((xs, upper), axis=-1)
    bottom_pts = np.stack((xs, lower), axis=-1)[::-1]
    polygon = np.vstack(([start - 2, y_axis], top_pts,
                         [stop + 2, y_axis], bottom_pts)).round().astype(np.int32)
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [polygon], 255)
    bounds = [start - 2, int(min(upper)), stop + 2, int(max(lower))]
    data = {'source': config['file'], 'image_size_px': [width, height],
            'axes_crossing_px': [x_axis, y_axis], 'outer_bbox_px': bounds,
            'wheel_centerpoints_px': config['wheels'],
            'silhouette_area_px2': int(np.count_nonzero(mask)),
            'notes': '2D AI-generated drawing; axle centers manually confirmed'}
    return mask, data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--config', type=Path, help='Optional JSON mapping of per-view file/band/guides/wheels')
    a = p.parse_args()
    config = CONFIG if a.config is None else json.loads(a.config.read_text())
    a.out.mkdir(parents=True, exist_ok=True)
    for view in ('top', 'side', 'front'):
        image = cv2.imread(str(a.images / config[view]['file']), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(a.images / config[view]['file'])
        mask, geometry = trace(image, view, config[view])
        cv2.imwrite(str(a.out / f'{view}_area_mask.png'), mask)
        (a.out / f'{view}_geometry.json').write_text(json.dumps(geometry, indent=2))
        print(f'{view}: {geometry["silhouette_area_px2"]} projected pixels, bbox {geometry["outer_bbox_px"]}')


if __name__ == '__main__':
    main()
