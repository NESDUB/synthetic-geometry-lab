# Case study: semantic recoloring as an intermediate segmentation mask

**Date:** 2026-11-07  
**Domain:** isolated black ribbed hood surface from a silver concept-car top view  
**Status:** qualitative observation in a single interactive image-generation session, **not** a quantitative success-rate benchmark.

## User discovery

A direct image-generation instruction to "isolate only the hood" produced a shape that was stylistically plausible but geometrically incorrect and confused the hood with the adjacent windshield/canopy. In the top view, the black ribbed hood occupies the **left, U-shaped crescent between the windshield and the white perimeter light**, whereas the smooth large dark panel to the right is glazing. A yellow circle was provided to help clarify the windshield area; its outline was not the actual glazing boundary.

The user then changed the *intermediate task* from extracting the hood to **recoloring the windshield green**. This yielded a visibly clearer green-vs-black material separation while keeping the black pinstriped hood region recognizable. A change in instructions was sufficient to obtain a useful candidate segmentation guide.

> Key methodological insight: when the image generator struggles to isolate a material/part semantically, request a simple high-contrast **class recoloring step**, inspect that result, and only afterward ask for the desired extraction. Each stage should have one measurable objective.

## Controlled candidate workflow

1. **Original evidence** — preserve the original image, camera projection and proportion assumptions.
2. **Semantic part marking** — ask the image model to recolor the unwanted windshield/glass bright green, while leaving the black ribbed hood unchanged. Preserve the yellow circle only as a pointer in the input; remove it from subsequent results.
3. **Inspection gate** — verify full green region coverage, non-green hood preservation, unchanged silhouette and no unintended material recoloring.
4. **Inverse selection / extraction** — in the next edit, explicitly identify **the black densely ribbed crescent on the left between green windshield and white U-shaped light** as the target. Remove the green windshield, silver body, light trim and everything else to RGBA alpha=0.
5. **Independent parser verification** — decode segmentation masks in color space; evaluate against the original with boundaries, precision/recall and false inclusion of windshield pixels.
6. **Topology annotation** — only on an approved, truly isolated object, generate and evaluate UV/section/intersection overlays.

## Extraction prompt to test

```text
Using the uploaded car image, perform a precise object extraction,
not a redesign or new rendering.

The bright green region is the windshield and glass canopy. It was
intentionally colored green to distinguish it from the hood.
Exclude every part of this green region.

The ONLY object to retain is the black, densely ribbed hood surface
on the LEFT side of the image, located between the curved green
windshield boundary and the white U-shaped perimeter light strip.

Preserve the hood's exact original shape, proportions, orientation,
fine radial pinstripe grooves, surface shading, and visible curvature.

Remove the entire green windshield, the silver vehicle body, the white
perimeter light strip, surrounding trim, and everything else.

Replace all removed regions with genuine alpha transparency (RGBA,
alpha=0). Do not fill the removed windshield area with invented hood
material.

Output: one isolated, original-looking black ribbed hood surface,
viewed directly from above, in its original orientation. No labels,
guides, topology grids, annotations, new geometry, or background.
```

## What this demonstrates—and doesn't

**Observed:** an indirect semantic marking/recoloring prompt provided a clearer material partition than direct hood-only extraction in this example.

**Not proven:** improved geometry accuracy, robustness across models/images, literal mask semantics inside the generator, perfectly crisp RGB green pixels, or consistent image-to-image edit reuse without user re-upload. Green shading/reflections may require hue/saturation thresholds, holes cleanup and boundary auditing. A generated image can slightly redraw edges even when instructed not to.

## Experimental comparison proposal

A/B/C on the **same** original top reference:

- A: direct hood-only extraction.
- B: green windshield semantic marking → generator hood extraction.
- C: green windshield semantic marking → deterministic image mask (HSV+boundary constraints).

Measure (i) mask IoU and boundary F1 against a manually audited target mask, (ii) rib-detail preservation in the original pixel region, (iii) unintended movement/shape change, (iv) image reconstruction error around the glass/hood seam, and (v) success across multiple seeds/repetitions.

Preserve each input/output separately (model, date, prompt, image dimensions and SHA-256). Avoid claiming that an aesthetic cutout is geometrically exact until these metrics are computed.
