# Proposed synthetic visual encodings

These representations are **hypotheses to test**; none should be assumed to reconstruct metric 3D shape just because a model generated a plausible picture.

| Representation | Decoder idea | Strength | Primary risk |
|---|---|---|---|
| Binary silhouette mask | threshold/connected components | Robust edges and area | Shape underdetermined in depth |
| Orthographic indexed grid | marker segmentation + character/ID matching | Potential cross-view correspondences | IDs can be copied incorrectly; points may not match |
| Section curves | color-coded curve tracing | Local profile fitting and loft guides | Missing depth/camera calibration |
| Height contours | contour tracking + assigned heights | Relative elevation constraints | Contour values may be fabricated |
| RGB normals | decode signed components to unit vectors | Strong local orientation cue | Non-integrable or inconsistent field |
| Grayscale/16-bit depth | calibrated intensity -> depth | Direct candidate depth field | Uncalibrated imagery is not distance |
| UV lattice | grid intersection graph tracing | Surface parameterization clues | Grid follows stylization, not necessarily geometry |
| Curvature/heat map | detect ridges and gradients | Highlights transitions | Colors do not encode actual curvature unless calibrated |
| Hybrid geometry atlas | compare channels under common coordinate system | Redundancy enables consistency testing | Shared hallucination across generated views |

## Atlas generation contract proposal

Ask for **one representation per image** whenever practical (not a dense infographic), transparent or solid flat background, unoccluded edge, no highlights/shadows unless shading is the measurement, known frame extents, axis arrows, grid spacings, unique marker labels and strictly separated palette. Prefer an accompanying deterministic sidecar (JSON/CSV) if the generating system can actually provide it. An image model printing JSON into pixels does **not** guarantee a faithful machine-readable sidecar.

## Consistency checks

For matched point i: side(X,Z), top(X,Y), front(Y,Z) must share X, Y and Z within projection uncertainty. RGB normals should be unit-length, curl/integrability consistency should be examined, and normals derived from a fitted depth field should roughly agree with the predicted normals. Failure -> flag input; do not deform fitted geometry until contradictions disappear cosmetically.

## Controlled experiments

- Mask-only baseline vs indexed correspondence with known ground-truth CAD rendering.
- Orthographic vs perspective images with intentionally unknown camera parameters.
- AI-generated normal/depth maps against exact maps rendered from a CAD ground truth.
- Single-view vs multi-view fit under matched total point count.
- Effect of increasing grid resolution on *actual geometry error*, not number of colored dots.
