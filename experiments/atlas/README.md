# Experiment 003 — Geometric information atlas

**Status:** deterministic benchmark prepared. AI-generation results have not yet been evaluated.

## Hypothesis

A series of **specialized, machine-readable images** (surface-normal channels, calibrated depth maps, contours and UV grids), each generated in a deliberately limited step, can convey more useful 3D information than one shaded concept illustration.

First establish what a correct representation looks like. This branch generates **ground-truth maps from a known smooth height field**, then verifies that quantized normal and depth channels remain mutually consistent. Only then can an image generator be asked to replicate, transfer or reconstruct each channel.

## Local run

```bash
pip install -r experiments/atlas/requirements.txt
python experiments/atlas/make_fixture.py
python experiments/atlas/check_consistency.py
```

Outputs under `runs/atlas-fixture/`:
- `depth_u16.png`: height encoded as **16-bit single-channel** values, linearly scaled from `z_min` to `z_max` stated in metadata (not arbitrary shade).
- `normal_rgb.png`: signed unit normal encoded as `round(255*(n+1)/2)` independently in RGB.
- `contours.png`: approximate isoheight lines at declared increments. **Visualization**, not a substitute for the numeric depth map.
- `uv_grid.png`: parameter-space grid. These are evaluation coordinates, **not the NURBS control net**.
- `atlas.json`: formula, dimensions, projection, units and channel conventions.
- `consistency.json`: depth-vs-normal agreement when decoded back from PNGs.

The fixture is algorithm-generated, **not** evidence that an image generation model understands normal maps or physically consistent geometry.

## Protocol for AI image generation

Perform separately: (1) copy the exact UV silhouette/outline; (2) produce a depth hypothesis in a calibrated channel; (3) produce a normal hypothesis; (4) propose contour lines; (5) compare all representations with known exact maps. Preserve raw generations and reject broken channel scales, fabricated contour values and mismatched viewpoints rather than smoothing errors away.

## Failure criteria

- Decoded normals are not unit length, poorly oriented or inconsistent with derivatives of decoded depth.
- Depth/color encoding lacks quantitative calibration or clips important shape variation.
- Cross-channel geometry disagrees despite looking visually attractive.
- Increasing visual complexity improves detected pixels but worsens actual 3D reconstruction error.

This is the starting control for comparisons; not a claim that a multi-channel atlas is best.
