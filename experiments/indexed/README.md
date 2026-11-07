# Experiment 002 — Indexed multi-view correspondences

**Status:** prepared benchmark; no AI-generated experiment run yet.

## Hypothesis

If image generation is asked to add **explicitly indexed, parsable point correspondences** to each of several aligned views, it can produce more useful geometric constraints than unmatched colored points or convex silhouette envelopes alone.

## Why this experiment matters

The windshield POC's magenta dots were detectable but did **not** establish that dot #n in one view was the same physical 3D point in another. Artificially matching them would make 3D fitting appear more certain than it is.

Start with mathematically known geometry and exact orthographic projections. Generate a ground-truth point CSV and three SVG drawings, then ask an AI image generator to **recreate only one view at a time** with colored numbered landmarks while preserving the projections. Extract point ID + pixel coordinate from its output and evaluate against the known original.

## Start

```bash
python experiments/indexed/generate_fixture.py
# inspect runs/indexed-fixture/{side,top,front}.svg
# run one image-generation step per view; decode into predictions.csv
python experiments/indexed/evaluate.py runs/indexed-fixture/truth.csv predictions.csv
```

The generator uses only Python's standard library. Its SVGs are **deterministic ground truth, not image-generator output**. The reference fixture contains naturally overlapping projections; this is a legitimate correspondence ambiguity, not something an extractor may erase by guessing.

## Predictions format

CSV header: `point_id,view,u_px,v_px`. View in `side,top,front`. ID matches e.g. `P03_05`. Frame coordinates are in exact pixels of each SVG's 1080x720 canvas. Undetected points must be omitted (never fabricated). If a model duplicates an ID, the evaluator counts a duplicate instead of silently picking a match.

## Evaluation

Measure detection coverage, invalid/duplicate IDs, point reprojection RMSE (px), and cross-view consistency in relative 3D units. Repeat with grid densities, color palettes, occlusion, image-generation prompts and output resolutions held as separately documented independent variables.

**Falsification:** if labels degrade extraction, correspondences are guessed, or known-geometry error increases versus silhouette-only controls, the method has not demonstrated improvement.
