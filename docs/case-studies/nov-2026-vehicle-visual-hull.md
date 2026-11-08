# Case study: 2026 concept-car three-view visual hull

**Goal:** turn three AI-generated orthographic-style concept-car drawings into a common proportionally aligned reference frame and a coarse 3D modeling proxy. The famous-looking result, `visual_hull_proxy.obj`, is the **intersection of three 2D silhouette constraints**, not a hidden neural 3D mesh generated directly from the illustration.

**Evidence:** the Nov 7 2026 image set and the original `vehicle-aligned-references.zip` package, including `build_vehicle_traces.py`, `reconcile_orthographic_views.py`, traced geometries, PNGs, `alignment_manifest.json` and the mesh. A smaller two-script reproduction is versioned in [experiments/orthographic-visual-hull](../../experiments/orthographic-visual-hull/README.md).

## 1. Input provenance and what the generator contributed

The object is a hypothetical silver luxury concept car, presented as one isolated image for **top, front and side**. Each drawing used cyan linework on a dark background, an intended visual centerline and tire-center markers.

The images were **generated**, not calibrated photographs or real orthographic CAD elevations. In the original set the blueprints contain inconsistent overhang and canopy proportions. Therefore the work needed registration before any projection intersection.

Input images: each 1448 × 1086 pixels. The front nose is left in the top/side drawings. Wheel centers were **checked and annotated in image pixels**:

| View | Wheel / axle centers (source pixels) |
|---|---|
| Side | front (326, 600), rear (1127, 600) |
| Top | (362, 332), (1085, 332), (362, 751), (1085, 751) |
| Front | (287, 636), (1158, 636) |

Note the top-list ordering: first two are one row, next two the opposite row; index order matters to the scripts. These points are alignment anchors, **not inferred physical dimensions**.

## 2. Trace the silhouettes (OpenCV + SciPy)

Original method, faithfully reproduced in `trace_blueprints.py`:

1. Read each PNG as BGR and find cyan line pixels using `G > 76`, `G > 1.65 R`, and `B > 0.77 G`.
2. Detect the longest construction axes from the maximum population in rows/columns.
3. Restrict the search to hand-confirmed vertical body bands: top [270, 803), side [342, 713), front [218, 834). Remove the detected centerline and known axle-guide columns.
4. For each x-column, use the first and last remaining cyan pixels as upper/lower silhouette candidates. Reject thin regions with fewer than 21 pixels of span, interpolate gaps, and median-filter with window 9.
5. Smooth the upper profile by a 1.35-pixel Gaussian. Smooth the lower profile likewise, except the front view uses the 88th-percentile lower-envelope filter (window 17) and a 2.2-pixel Gaussian to suppress decorative tire treads.
6. Connect the two profiles and the two ends into one closed polygon, then rasterize with `cv2.fillPoly`. Save `top/side/front_area_mask.png` and `*_geometry.json`.

The complete archival processing also separately removed guide lines, skeletonized interior cyan strokes, vectorized paths into SVG, and produced inspection overlays. **The hull only uses filled masks and registered 2D landmarks**; wheel-spoke vectors and lighting strokes are not required for hull intersection.

## 3. Normalize to wheelbase = 1 without inventing dimensions

3D coordinate frame:

- X longitudinal, **positive rearward**. Axle x positions: front = −0.5 and rear = +0.5.
- Y lateral, positive toward the bottom of the top drawing.
- Z upward; axle height = 0. Road level is negative Z.
- Drawing scale = 900 pixels per unit wheelbase, with aligned raster 1800 × 1050.
- Top image origin (900, 525); side and front origins (900, 680). These are pixel origins, **not car centers of gravity**.
- Front view is mirrored laterally to maintain the same 3D-handed coordinate system.

Source wheelbase is 801 px on side and 723 px on top. Track/wheelbase from top: `(751-332)/723 = 0.5795297372`. Front-image source pixels per normalized wheelbase: `(1158-287) / 0.5795297372 ≈ 1502.9427`.

For each top/side view, define front and rear source axle coordinates `x_f, x_r`, source wheelbase `w = x_r - x_f`, the measured front/rear overhang ratios `a_f, a_r`, and consensus overhangs `A_f, A_r`. The original script uses the **arithmetic mean** of top and side ratios for consensus (a choice, not an external measurement).

Source coordinate as a function of target normalized X:

```text
x_source(X) =
    x_f + (X + .5) * w * (a_f / A_f)      when X < -.5
    x_f + (X + .5) * w                    when -.5 <= X <= +.5
    x_r + (X - .5) * w * (a_r / A_r)      when X > +.5
```

This preserves axle stations, scales only their exterior overhang segments, and is continuous at both axles. Vertical registration uses a separate piecewise scale above/below axle height to reconcile side and front roof and floor estimates.

```text
z_source = Z * source_roof / consensus_roof   if Z >= 0
z_source = Z * source_floor / consensus_floor if Z < 0
source_pixel_y = source_axle_pixel_y - source_ppu * z_source
```

Top uses a direct lateral wheelbase scale; front is horizontally mirrored. Source masks are resampled with `cv2.remap(..., INTER_NEAREST)` to avoid fabricating partly occupied pixels. SVG/photographic reference overlays use their appropriate interpolation.

The case-study consensus ratios:

| Measurement, all per wheelbase | Value |
|---|---:|
| Wheel track | 0.5795297372 |
| Overall body width estimated from top | 0.6735822960 |
| Front overhang | 0.3129179812 |
| Rear overhang | 0.3029485964 |
| Roof above axle | 0.2737309643 |
| Floor / ground below axle | 0.1213887354 |

Original view disagreement, before registration: front overhang **side 0.275905 vs top 0.349931**; rear overhang **side 0.268414 vs top 0.337483**; roof **side 0.284644 vs front 0.262818**. Registration intentionally changes those proportions; it is not proof that the average is correct.

## 4. Intersect the three projected silhouettes

A regular voxel sampling grid in unitless world coordinates:

```text
X = linspace(-0.84,  +0.83, 185)
Y = linspace(-0.355, +0.355, 85)
Z = linspace(-0.128, +0.292, 68)
```

Each sample is occupied if and only if it is inside **all three** binary masks:

```python
occupied = inside_top(X, Y) & inside_side(X, Z) & inside_front(Y, Z)
```

The code executes this as broadcasting three Boolean arrays of shapes 185×85, 185×68, 85×68 to a 185×85×68 array (roughly 1.07 million voxels).

Apply `scipy.ndimage.gaussian_filter(occupied.astype(float32), sigma=0.56)` and run `skimage.measure.marching_cubes(field, level=0.5, spacing=(dx,dy,dz))`. Add the minimum X/Y/Z grid coordinates to the returned mesh vertices. Export the triangle mesh through `trimesh.Trimesh(..., process=True)` to OBJ and GLB.

This is a **three-direction generalized visual hull**, the largest volume satisfying all three silhouettes at that sample resolution. It cannot recover concavities, true normals, body-panel segmentation, or hidden components; it may connect or fill where the real surface would be hollow.

## 5. Reproduction check and diagnostics

Reproduced independently on the original three PNGs using the repository's `trace_blueprints.py` and `visual_hull.py`. All three generated 2D binary silhouette masks matched the archival masks **pixel-for-pixel**. The newly exported OBJ matched the original **byte-for-byte**, with SHA-256:

```text
003cb3aa0715e11474251f77f3fa6ae8830981926150a06e013958b669ac4933
```

Measured results with the tested environment: 51,432 vertices, 102,860 faces, 0.2728970579 normalized cubic-wheelbase units of enclosed volume; mesh was watertight. Voxel-occupancy projection IoU against the aligned input masks: top 0.9991, side 0.9999, front 1.0000.

**Do not interpret those high IoUs as independent accuracy.** They compare the constructed voxel occupancy's projected masks to *the same masks it was constructed from*. They primarily diagnose discretization and intersection losses. They say nothing about agreement with a real car's hidden geometry.

Reproduction environment observed: Python 3, NumPy 2.3.5, SciPy 1.17.0, scikit-image 0.26.0, OpenCV 4.13.0.92, trimesh 4.11.1. Floating-point, interpolation or mesh serialization changes in other dependency versions can change a byte-level digest while retaining the geometry.

## 6. What to do for production-quality modeling

Treat the hull as a **blockout and registration scaffold**. Next, align reference planes in Blender with the original `import_into_blender.py`, generate additional undistorted cross-sections, recover continuous panel curves with controlled profiles, build separate tire/hood/roof/glazing surfaces, and validate every rendered orthographic projection back against original evidence. Quantify surface differences and never silently treat AI-generated geometric details as precise manufacturing data.

For any new object, adjust the manually anchored `CONFIG` entries. A new image set will require its own diagnostic checks; fixed pixel search bands and reference wheel positions from this case are **not universal**.
