# Experiment registry

Each experiment is a **competing hypothesis**, not a ranking. Keep methods on separate `exp/` branches until evidence supports a change to the shared protocol.

| Branch | Hypothesis | Stage | Evidence needed |
|---|---|---|---|
| `exp/windshield-silhouette-baseline` | Four registered envelope views can constrain a coherent spline canopy | Preliminary POC; archived input required | Reproduce original validation, compare against true geometry |
| `exp/indexed-correspondence` | Explicitly numbered multi-view intersections improve 3D constraint quality | Proposed | Ground-truth landmark accuracy and detection reliability |
| `exp/geometry-atlas` | Multiple specialized image encodings outperform a silhouette baseline | Proposed | Depth/normal integrability, distortion and geometry error |

Always report whether a claim is from a run, from an original attachment, or only a proposed test.
