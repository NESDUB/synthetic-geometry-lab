# Experiment 001 — Four-view silhouette → continuous B-spline canopy

**Status:** archival reproduction of the user-supplied windshield proof of concept, **not a verified global-optimum method**.

This branch records the first successful *isolated canopy* workflow. It deliberately preserves the original's separation of tasks: gridded AI reference → 4 separate aligned views → extracted colored landmark/silhouette guides → cubic spline fitting → actual geometry render + overlay → validation.

## Source & provenance

The original `windshield-model(1).zip` was supplied in the research conversation, SHA-256:

`13f2f5d42ca3ae9fd79ed6ef96cda6b6c3e18b2b7d52d7b3e5807d779e5b5d05`

It includes the **authoritative source generator**, extracted CSV coordinates, alignment transforms, model exports, previews and original validation. Raw user-provided images and binary meshes are not bundled into this branch; the import tool restores them from the original archive. This avoids silently dropping source provenance or republishing original images without making the redistribution decision explicit.

## Reproduce

```bash
# from repository root
python experiments/windshield/import_archive.py "/path/to/windshield-model(1).zip"

python -m venv .venv
source .venv/bin/activate
pip install -r experiments/windshield/requirements.txt

python experiments/windshield/verify_reproduction.py
```

The importer places original files in `runs/windshield-original/`; it refuses archives with the wrong hash. The verifier reruns the archive's **actual source/build.py** and compares regenerated metrics with the archived results and published expected values. Run optional `source/render.py` for actual-model previews after installing `pyrender PyOpenGL Pillow` (EGL may need working OpenGL drivers).

## Numbers to reproduce

| normalized projection | original envelope RMSE (reference pixels) |
|---|---:|
| Side | 0.8687551 |
| Top | 5.1006696 |
| Front | 4.6664094 |
| Rear | 5.9806779 |

These are *convex projected envelope* checks against aligned AI guides with a scripted 1200px scale. They are not point-to-point correspondence scores or physical truth. The source uses an **18 × 14** bicubic B-spline control lattice and produces **one open sheet**, with collapsed front and rear tips. It does not model actual glass thickness, the hood/body interface or a drivable vehicle.

## Hypothesis / falsification

Hypothesis: fitting multiple registered silhouettes creates a usable continuous surface with improved reference projection agreement over an unregistered one-view profile.

Disproof would include: reproducible failures in the actual 4-view metrics, folded/self-intersecting or invalid geometry, significant degradation on held-out views or known-geometry benchmarks, or worse reconstruction under a fair competing method.

## Future controlled comparisons

1. Register all views using camera models rather than independently stretching them.
2. Optimize against detected masks (non-convex silhouettes), not just convex hulls.
3. Test cross-view indexed point correspondences *only after* identifying the same physical points.
4. Constrain the B-spline against adjoining body panels and measure G0/G1/G2 seams.
5. Compare against known synthetic CAD ground truth where 3D error is measurable.

**Do not mark this baseline as the best method by default.**
