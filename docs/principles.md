# Working principles

This document describes the research philosophy behind the lab; it is **not** a claim that a particular implementation has been proven optimal.

## 1. Generate information, not just images

The useful output may be a segmented mask, indexed lattice, curvature guide, orthographic construction plate, candidate normal map or contour field. Visual attractiveness is secondary to how robustly an extractor can read it.

## 2. Use deliberately small generation tasks

One generation should aim at one measurable outcome: isolate a view; regularize a silhouette; add indexed landmarks; map cross-sections; propose a depth field. Do not mix separation, annotation, interpolation, reconstruction and artistic styling in a single uncontrollable step. Inspect each stage before proceeding.

## 3. Keep every iteration visible and attributable

Render the actual 3D geometry and inspect it. Keep ordered source images, prompts, extracted features, CAD outputs, overlays, errors and critiques. Subsequent experiments must not silently reuse unverified visual assumptions.

## 4. Preserve raw evidence

An aligned/generated image is derivative evidence, not a replacement for an original. Track raw-to-aligned transforms and distinguish author-supplied, AI-generated, algorithmically derived and manually measured values.

## 5. Encode for parsers

Prefer high-contrast separated channels, unique IDs, known orientation, calibration bars, coordinate axes, consistent fixed camera assumptions, explicit backgrounds and non-overlapping labels. Validate segmentation against a held-out mask; never infer true geometry merely from nice-looking colors.

## 6. Reconcile views instead of averaging contradictions away

Use side (X,Z), top (X,Y), and front/rear (Y,Z) only after verifying coordinate directions, scales, camera projection and point correspondence. If source views conflict, record residuals and uncertainty. Do not treat an apparent orthographic view as an engineering drawing without evidence.

## 7. Spline continuity is not fit quality

A surface can be C2-continuous and look wrong. Track geometric fit (2D/3D), normal/tangent continuity at boundaries (G1/G2 when meaningful), regularity/Jacobian, self-intersections, seam gaps and topology independently.

## 8. Be explicit about unknowns

AI synthetic normal/depth maps do not guarantee an integrable field. Brightness, color or contour spacing has no physical units without calibration. A rendered control grid is not necessarily the underlying NURBS control net. An open surface does not equal watertight glass.

## 9. Compare hypotheses fairly

Use identical reference inputs, known transforms, objective functions and exports wherever possible. Keep failures and counterexamples, not only successful previews. Branches are experimental tracks, not a hierarchy.

## 10. Separate CAD and simulation readiness

Native CAD splines -> tessellated GLB/OBJ/JOE are different artifacts. Game physics requires separate suspension, wheel pivots, collision shapes and parameters; rendering fidelity alone does not establish drivable accuracy.
