# Experimental protocol v0.1

## Input/source manifest

Every run records a stable run ID, UTC date, original reference files with SHA-256, provenance type (original, generated, transformed, manually annotated), prompt text if applicable, generator/version when known, and limitations of each image.

## Coordinate conventions

Use a declared right-handed reconstruction frame unless an experiment explicitly justifies another: X longitudinal (negative toward nose), Y lateral, Z up. Each view must declare image axes, pixel origin, projection type and raw-image -> registered-image transform. Units are **relative** until a physical dimension has been supplied. Report all scaling, stretching and mirroring; do not claim all four projections are consistent if they were independently normalized.

## Extraction

Preserve an untouched original; compute a mask/landmark/curve extraction in its own output folder. For points: record label, view, raw pixel, registered pixel, confidence, detection method and whether correspondence is verified. For maps: record encoding (e.g. RGB normal convention or contour interval) and decoder.

## Surface fitting

Keep solver and generator separable. Fitted surface files should include degree, knot vectors, control points, coordinate frame, trimming boundaries, basis and weight definitions. A NURBS control net is not the same as uniformly sampled surface vertices. Reject interior folds and non-finite surfaces; document endpoint singularities rather than hiding them.

## Evaluation

Required: source-vs-reprojection overlays for every supported view, stated metric and pixel scale, geometry regularity checks, export/reimport checks, and a human visual critique. Report at least:
- projected boundary distance and silhouette-envelope RMSE, **per view**;
- when correspondence exists, landmark reprojection error by point ID;
- topology/surface conditions (finite, normals, degenerate faces, connected components, open/watertight, Jacobian samples);
- seam/gap and G0/G1/G2 diagnostics when multiple panels are joined;
- input sensitivity and failure modes.

If no camera calibration / true depth / correspondence is available, state that recovered shape is **underdetermined** and that results are candidate reconstructions.

## Quality gate

Each iteration has hypothesis -> one controlled alteration -> generated evidence -> extraction -> reconstruction -> metric comparison -> actual mesh/render -> critique -> keep/reject decision. Do not substitute generated concept art for a render of the final CAD artifact.

## Promotion criteria

A branch is promoted only with:
1. a runnable command or fully documented required input set;
2. a frozen comparison dataset and provenance manifest;
3. evaluated claims with reproducible numbers;
4. side/top/front/rear renders or an explicit unsupported-view explanation;
5. failure cases and a comparison to the baseline with the same measurement definition.
