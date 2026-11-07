# Windshield proof of concept — evidence and limits

## Origin

A car-modeling attempt produced visibly segmented canopy geometry. After exploring parametric B-splines/NURBS, a different AI workflow generated a four-view gridded canopy image. A coding agent isolated the views, registered proportions, extracted magenta markers and silhouette envelopes, and fitted an isolated windshield.

The **sequence was intentionally staged** to keep image generation focused:
1. produce an informative gridded canopy reference;
2. split it into individual views, register proportions and extract points;
3. confirm the guides are useful and inspect the alignment;
4. fit the isolated canopy, not the rest of the car;
5. export the exact fitted surface/meshes and inspect overlays;
6. only afterward consider applying the approach to additional panels.

## What the supplied windshield-model archive contains

- `source/build.py`: SciPy least-squares tensor-product spline fit to reference envelope coordinates, plus export and tests.
- `source/render.py`: actual geometry previews and overlays.
- `source/load_geomdl.py`: optional geomdl B-spline adapter.
- `reference/{side,top,front,rear}.csv`: aligned extracted 2D coordinates.
- `reference/*.png` + `alignment.json`: guides and transformations.
- `models/surface.json`: editable 18 × 14 degree-3 B-spline control lattice, weights = 1.
- `models/windshield.{obj,glb}`: display meshes, not native trimmed CAD solids.
- `validation.json`: measurements and geometry checks.

## Reported results (original POC, not independently re-estimated here)

| Projection | Envelope RMSE in normalized reference pixels |
|---|---:|
| Side | 0.8688 |
| Top | 5.1007 |
| Front | 4.6664 |
| Rear | 5.9807 |

These compare **projected convex envelopes to generated/aligned guides**, scaled by the original script's 1200px normalization. They are *not* physical-accuracy claims, real-photograph errors or point-correspondence errors. The surface is an **open single sheet**, about 1 × 0.370 × 0.131 in length-normalized coordinates. It is not a glass solid or assembled vehicle.

## Modeling details

The original algorithm uses each view's convex hull envelopes, cosine-spaced longitudinal sampling, a transverse crown profile averaged from front/rear projections, a tensor-product cubic fit, symmetry constraints and a monotonic longitudinal control correction. It intentionally collapses the two longitudinal parameter ends into tips; C2 internal continuity does not imply regularity at those tips. Interior dots **were not matched as common 3D vertices across views**, because correspondence was unverified.

## Research question

Is a structured, stagewise image-generation process more accurate and reproducible than raw single-prompt image-to-mesh modeling, when evaluated against *held-out known 3D surfaces*? This remains unproven. We must preserve the windshield as a successful preliminary example while testing alternatives against fair ground truth.

## Reproduction

Use `exp/windshield-silhouette-baseline` for an import helper and the exact source files from the supplied `windshield-model(1).zip`. Keep the original ZIP unchanged; licensing and source provenance should be settled before redistributing its raw images.
