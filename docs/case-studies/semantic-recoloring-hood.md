# Case study — semantic recoloring before object isolation

**Date:** 2026-11-07  
**Project:** Car-hood segmentation from a rendered orthographic top view  
**Status:** Qualitative observation, not a quantified benchmark

## Observation

Direct image-to-image prompts such as "isolate the hood" repeatedly produced plausible but **structurally incorrect** replacements: changed the topology of the hood, introduced a crescent-shaped panel, or returned multi-panel infographic layouts. Explicitly disambiguating the windshield with a **simple recoloring instruction** ("turn the windshield green") instead yielded a more usable visual partition: the green transparent canopy versus the black ribbed hood with its white perimeter lighting.

The user identified this as a valuable general technique: **ask the generator for an easy, visually unequivocal edit that produces a machine-segmentable attribute**, rather than asking it to reason about and extract a complex semantic part in one operation.

The next controlled step asked the generator to **remove only the silver vehicle body and place the remaining components on a solid red background**. The output did remove silver and visibly retained the green canopy plus black ribs, but the model ALSO reinterpreted the black perimeter into much longer pointed extremities. Therefore this output must **not** be treated as pixel-accurate original geometry, despite looking clean.

## Important distinction

- **Semantic segmentation hypothesis:** an image generator may more reliably recolor an identifiable region than precisely cut it out while preserving all geometry.
- **Observation:** the green-glass prompt succeeded *qualitatively* at disambiguating the glass from dark ribs; the silver-removal/red-background step still introduced shape drift.
- **NOT established:** that visual-color edits preserve pixels, contours, metric orthographic proportions, actual 3D landmark correspondence or original topology.

## Suggested prompt sequence for a controlled comparison

### A. Locate without deleting

> Using the supplied overhead reference as the *only* geometry source, recolor the entire windshield/glass region bright saturated green. The user-provided yellow circle (if present) is only a locator, NOT the shape or boundary. Leave the ribbed black hood, white curved lighting, silver car body and camera framing unchanged. Remove the locator circle. Produce one single image.

### B. Remove one already-distinguishable class

> Use the previous green-glass image as input. Replace **only the outer silver painted car body**, including silver side rails and silver rear trim, with a uniform, solid #FF0000 red background. Keep the original black ribbed hood, its white light band, and the entire green glass region in precisely their current positions, outlines and proportions. Do not invent extended fins, redraw the hood, modify ribs, or change camera orientation. No text, labels, legends, diagrams or additional views.

### C. Deterministic extraction

Use **code**, not a third generation, to segment the green windshield and remove it from the intermediate. Extract the black ribbed hood bounded by its original light strip; emit a true-alpha PNG, a binary mask, a contour-coordinate file, and an overlay against the untouched original.

## Evaluation criteria

For each intermediate:
1. Original-to-output image registration: maintain common pixel dimensions or estimate and report the actual transform.
2. Pixel/contour preservation **outside the requested edit region**; count changed pixels and report structural deviation.
3. Segmentation precision/recall against a human-verified target mask.
4. Silhouette discrepancy of the ribbed hood in original and masked images, especially at the LED perimeter, left nose and rear tips.
5. Machine-decoder simplicity: HSV green mask, red background mask, connected-component analysis, alpha edge feathering.
6. Compare **direct semantic extraction**, **sequential recolor+extract**, and **deterministic manual/algorithmic masking** on identical inputs.

## Failure handling

A new red background image may seem cleaner yet be unusable as a geometric reference if its boundaries move. If the model hallucinates long fins or rounded ends, reject for ground-truth fitting, preserve as an experimental failure case, and derive the mask directly from the original image where possible.

## Relation to lab principles

This case illustrates **goal decomposition**, **machine-readable visual encodings**, **semantic-color masking**, and **human-in-the-loop verification**. It does not prove a universal best sequence; method selection depends on source quality, object topology, ambiguity and required precision.
