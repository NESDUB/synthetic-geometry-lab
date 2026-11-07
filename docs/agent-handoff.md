# Agent handoff / operating instructions

Objective: research **synthetic geometric information generation** as a computer-vision-to-CAD pipeline. This lab is **not restricted to car windshields**.

## Non-negotiables
- Treat the repository owner's documented workflow as a *hypothesis*, not a frozen best method.
- Use image generation as a task-scoped information producer; prefer focused successive passes over a giant one-shot prompt.
- Publish every meaningful revision's **actual model render**, associated prompt/asset inputs, metric and critique; never describe an AI concept render as a rendered mesh.
- Do not equate visual plausibility with physical calibration. Do not invent units, view correspondences or benchmark outcomes.
- Keep the original references immutable; image generation, segmentation, fitting, rendering and validation must be reproducibly separable.
- Avoid adding experiments to main prematurely. Branch names `exp/<hypothesis>`; each experiment explains success criteria and falsification conditions.
- Preserve negative results and limitations.

## Immediate research tracks
1. Reproduce the approved isolated windshield from its source ZIP, hash inputs, and regenerate the B-spline and reference overlays.
2. Benchmark encoded point correspondences on synthetic known-geometry shapes before asking image generation to reproduce them.
3. Compare synthetic height, normal, contour and section representations, using CAD-rendered true maps as controls.
4. Develop cross-view agreement metrics and camera-scale uncertainty instead of arbitrary image stretching.

## Recommended artifact structure per run
```text
runs/<id>/
  manifest.json
  originals/        # immutable, sha256 listed
  generated/        # output with prompt/model provenance
  registration/     # transforms, aligned views
  extracted/        # masks, coordinates, confidences
  solved/           # control nets and CAD/mesh exports
  evaluated/        # metrics, overlays, checks
  review.md         # critique and decision
```
Avoid uploading third-party binaries or enormous dependency source trees. Track their upstream URLs and pin versions instead.
