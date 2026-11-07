# Prompt playbook — image generation as a synthetic geometry instrument

This is a **tool-agnostic, experimental prompt library**, not a claim that current image models obey quantitative encodings perfectly. Preserve each prompt and produced image with a model/version, date, raw original, and extraction report.

## Workflow discovery: the original intent

The user introduced the following idea as a proposed instrument for scripts, not simply for attractive illustration:

> Maybe we can ask the AI image generation for something that is more comprehensive that the script can parse higher resolution data of the curvature from any ideas for what might work well? Keep in mind that the AI image generation can generate pretty much any type of detectable surface. Whether it be like a topology map or a heat map or even a hybrid of both. Or whatever. My only question is will a script be able to detect a method like that like we could put stuff on it like a combination of things for easier detection

### The deliberate staged windshield workflow

The following brief user instructions are quoted from the supplied earlier conversation. They capture the **sequencing** that led to the first acceptable windshield reconstruction, not a verified claim that the result was physically accurate.

1. *After requesting a synthetic gridded multi-view guide:*
   > Perfect now you have the perfect guide to use with scripting Although you might want to isolate each view and make sure that they are all aligned proportionately with each other

2. *After the views and their candidate landmarks were separated and normalized:*
   > All right, will this help you immensely now?

3. *Only after confirming the scoped references were useful:*
   > OK, go ahead then. The goal is only to create the windshield model right now

4. *After inspecting the isolated canopy:*
   > its perfect!. Now, do you want to do this for every other panel of the car? I'd recommend that you do that.

**Interpretation:** perform one narrowly scoped visual task, evaluate its usefulness and geometry, then reuse the method on the next component. Do not ask one generator to build the entire vehicle from scratch in a single pass.

## Experiment prompt 1 — isolated orthographic plate

**Input:** untouched original photos or prior synthetic concept references.

> Produce **one** clean orthographic [SIDE / TOP / FRONT / REAR] technical view of the same subject. Preserve the visible silhouette, selected landmarks and all identifiable features from the provided reference. Eliminate environmental texture, perspective styling, shadows, labels and decorative elements. Use a pure background and a sharply defined single contour. Show an axis marker and calibration grid of constant *image-space* spacing. Do not invent occluded dimensions. The result is a candidate drawing, not certified orthographic geometry.

**Decoder:** detect silhouette, axes and known image-space grid. **Gate:** compare to original reference mask; do not assert metric calibration without a known physical dimension or camera estimate.

## Experiment prompt 2 — sparse indexed landmarks

**Input:** one accepted, independently registered view from step 1.

> On this exact orthographic image, mark a **sparse** set of structurally meaningful surface positions using high-contrast magenta dots with unique short IDs (P00, P01...). Keep the underlying outline unchanged. Avoid more than [N] marks. Do not crowd labels or invent marks behind the surface. Maintain every accepted dot position for this view.

**Decoder:** image segmentation + ID recognition. **Gate:** marker precision/recall and reprojection pixel error. Across views, do **not** assume matching IDs refer to the same 3D point unless independently checked.

## Experiment prompt 3 — single-encoding surface guide

**Input:** one approved view with reference axis and boundary.

> Represent the visible [surface] using only a **[UV grid / equally indexed transverse sections / isolines / normal-direction hue]** encoding. Keep its boundary fixed and avoid lighting, reflections or artistic shading. Use separated high-contrast feature colors. Maintain a constant coordinate orientation; do not print numeric measurements unless you can genuinely calibrate them. Provide one unambiguous encoding per image.

**Decoder:** graph tracing, curve detector or channel decoder. **Gate:** reject false/missing intersections, mislabeled contours and channel conflicts.

## Experiment prompt 4 — atlas consistency review

**Input:** decoded candidate maps and deterministic CAD render projections.

> Inspect the generated views for disagreements in boundaries, landmark IDs and curvature transitions. Report only identifiable differences. Do not redraw or beautify the original and do not claim missing depth or geometry is known. Propose one localized correction for the next generation step.

**Gate:** a script must confirm any claimed improvement using the original reference and actual re-rendered fitted mesh. A language-model critique is hypothesis generation, not quantitative verification.

## Notes on actual units and geometry

For any requested AI-generated depth/normal/curvature channel, the generator can supply **qualitative visual hypotheses**. The script must not interpret its RGB values as literal unit vectors, millimeters or curvature radii unless a calibration and consistency check makes that interpretation defensible.

## Comparison policy

Log alternate prompts, including failures and tradeoffs. Prefer empirical measurements on the *same* known CAD surface and fixed camera geometry over subjective preference. More colored dots are not automatically better data.
