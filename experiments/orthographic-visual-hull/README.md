# Orthographic silhouette registration → visual-hull blockout

A reproducible case study of the futuristic concept car reconstructed on **7 November 2026**. The shape was not modeled by hand: the pipeline starts with three separate AI-generated cyan blueprint images, traces each silhouette, aligns landmarks into a common unitless coordinate system, and intersects their projections into a 3D occupancy field. The resulting surface is extracted by marching cubes.

The original `visual_hull_proxy.obj` has **51,432 vertices**, **102,860 triangles**, and a wheelbase-normalized volume of approximately **0.2728971**. Our independently reimplemented two-script pipeline reproduced that OBJ **byte-for-byte** using the original 2026 source images.

This experiment is not automotive engineering, dimensional CAD, or validated 3D ground truth; visual-hull surfaces can look compelling while being substantially wrong in details.

## Reproduce from the images

Obtain the original `vehicle-aligned-references.zip` case-study archive from the accompanying ChatGPT conversation (it is not checked in because it contains ~9 MB of generated image/mesh binaries). Extract it to a folder, here called `DATA`, containing the three `ChatGPT Image Nov 7...` originals.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r experiments/orthographic-visual-hull/requirements.txt
unzip /path/to/vehicle-aligned-references.zip -d /path/to/data
DATA=/path/to/data/vehicle-aligned-references
python experiments/orthographic-visual-hull/trace_blueprints.py \
  --images "$DATA" --out /tmp/car-traces
python experiments/orthographic-visual-hull/visual_hull.py \
  --traced /tmp/car-traces --out /tmp/car-hull
```

Produces `/tmp/car-hull/visual_hull_proxy.obj`, `.glb`, normalized masks, and `diagnostics.json`.

To skip retracing and isolate registration/mesh-generation, point `--traced` to `$DATA/vehicle-traced-blueprints`.

Optional end-to-end regression: `python experiments/orthographic-visual-hull/verify_case_study.py --images "$DATA"`.

## What's included

| File | Purpose |
|---|---|
| `trace_blueprints.py` | Source-pixel cyan detection, outer-envelope extraction, binary masks, and empirically annotated wheel centers. |
| `visual_hull.py` | Axle-anchored cross-view normalization, binary remapping, 3D silhouette intersection, smoothing, marching cubes and OBJ/GLB export. |
| `verify_case_study.py` | Run both stages in a temporary directory, check original metrics, optionally test the OBJ checksum. |
| `requirements.txt` | Python/OpenCV/SciPy/scikit-image/trimesh dependencies. |
| [Detailed case study](../../docs/case-studies/nov-2026-vehicle-visual-hull.md) | Formulas, coordinate conventions, exact source assumptions, diagnostics, limitations, and adaptation guidance. |

## Adapting to another object

1. Request and visually inspect **three separate orthographic-looking views**: top, side, front. No labels should cross the object silhouette.
2. Decide the same front/rear/left/right convention in every image. Mark both longitudinal axle centers in top and side, and tire-center track in front and top; do not blindly trust AI placement.
3. Change the three file names, masking bands and source landmark pixel coordinates in `trace_blueprints.CONFIG`, or provide `--config custom.json`.
4. Check the three `*_area_mask.png` binary silhouettes. Reject views whose lines or perspective would create bad envelopes.
5. Run `visual_hull.py`. Inspect `diagnostics.json` for input disagreement before trusting aligned sections.
6. Import the OBJ/GLB into Blender and verify it against the aligned reference PNGs from the original full archive. Refine individual panels with additional cross-sectional evidence.

Important: unlike many photogrammetry tasks, this pipeline assumes **orthographic projection and manually anchored correspondences**. It is unsuitable for arbitrary perspective photographs without prior camera estimation / rectification.

## Provenance

The original experiment included `build_vehicle_traces.py`, `reconcile_orthographic_views.py`, three generated source images, raw traced masks and SVGs, transformed references, landmark CSV, a JSON manifest, OBJ/GLB, and a Blender reference-plane importer. The repository's two shorter scripts retain the **actual contour/mask and visual-hull math**, rather than only describing it. All numerical comparisons here are for this particular synthetic car and are not calibration claims for new vehicles.

**Status:** independently verified reproducibility of the blockout on the original case-study inputs. No claim of surface reconstruction accuracy or unique physical geometry.
