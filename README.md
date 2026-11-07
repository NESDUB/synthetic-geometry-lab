# Synthetic Geometry Lab

**Research into AI-assisted, machine-readable visual representations for reconstructing three-dimensional geometry.**

The central hypothesis: an image generator can be used as a **synthetic geometric information generator**, not just a concept-art renderer. By requesting deliberately structured visual intermediate products—aligned orthographic views, indexed point grids, silhouettes, UV lines, cross-sections, normal/depth hypotheses and curvature guides—we may obtain detectable constraints for an independent geometry solver.

**This is a laboratory, not a finished reconstruction algorithm.** Generated diagrams can be wrong, internally inconsistent or physically impossible. No visual code is treated as calibrated metric data until independently validated.

## Why break image generation into stages?

A single request to generate an attractive "perfect 3D windshield" makes it difficult to tell whether the generator preserved object proportions, point correspondence or surface continuity. A sequence of narrowly scoped requests makes every intermediate representation **inspectable, rejectable and measurable**.

```text
original evidence
  -> isolate individual views (preserve originals)
  -> register scale, axes and landmarks; document uncertainty
  -> ask AI for one specialized representation per step
  -> segment/parse colored marks, curves or channels
  -> reconcile measurements across views
  -> solve a continuous geometry model (e.g. B-spline/NURBS)
  -> render exact CAD geometry back into the reference cameras
  -> evaluate projection errors, topology, continuity and uncertainty
  -> critique -> revise -> save provenance for the next experiment
```

**The image generator proposes candidate constraints. The solver, validation code and original references decide whether to accept them.** Do not assume visually plausible normal/depth/UV values are physically accurate.

## Start here

- [Research principles](docs/principles.md) — the working philosophy and non-negotiable verification rules.
- [Prompt playbook](docs/prompt-playbook.md) — the staged windshield conversation and experimental image-generation templates.
- [Experimental protocol](docs/protocol.md) — coordinate conventions, metrics, evidence and decision criteria.
- [Visual representation atlas](docs/representation-atlas.md) — proposed machine-readable image encodings and tradeoffs.
- [Windshield proof of concept](docs/windshield-poc.md) — what was actually attempted, produced and validated.
- [Experiment registry](experiments/README.md) — independent competing investigations, not a ranked leaderboard.
- [Agent handoff](docs/agent-handoff.md) — operating instructions for AI coding/modeling agents.
- [Manifest schema](schemas/experiment.schema.json) — machine-readable provenance contract.
- [Baseline experiment branch](https://github.com/NESDUB/synthetic-geometry-lab/tree/exp/windshield-silhouette-baseline) — archival reproduction from the user's supplied windshield-model.zip.

## Experiment philosophy

**main** contains shared methodology, interfaces and neutral benchmarks. Each **exp/** branch contains one hypothesis or method. Branches are deliberately not evidence of superiority. When an experiment is promoted, it needs a reproducible artifact, quantitative comparisons to a common baseline, inspection images and a clear limitation statement.

Initial tracks:
1. `exp/windshield-silhouette-baseline` — reconstruct the original canopy from four normalized silhouette envelopes.
2. `exp/indexed-correspondence` — test explicit cross-view indexed landmarks, without assuming AI dots correspond automatically.
3. `exp/geometry-atlas` — evaluate multi-channel depth/normal/contour/UV maps as hypothetical constraints.

## Current evidence

The first windshield POC generated one open bicubic spline surface, not a full glass solid or vehicle. Its original report measured projected **silhouette-envelope** fit on normalized AI-generated guides (not photographic reconstruction error). It did **not** establish unique 3D ground truth, interior point correspondence, or body-panel continuity.

## Reproduction and provenance

Keep original generated images and reference measurements alongside their extraction scripts and transformations. Store prompts/model identity/seed if exposed, generation dates, view assumptions, coordinate transforms and the exact output of geometry checks. Never overwrite an input with an "aligned" derivative.

**Status:** early research / proof of concept. **Licensing:** no license granted yet; reuse rights have not been selected by the repository owner.
