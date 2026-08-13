# Phase Report: P04

PHASE:
P04

OBJECTIVE:
Baseline Change Detection between 2025 (synthetic) and 2026 (real) imagery.

STATUS:
PASS

TASKS:
- [x] Implement absolute difference computation in grayscale between temporal datasets
- [x] Implement Gaussian smoothing for noise reduction
- [x] Implement configurable thresholding to segment changes
- [x] Implement morphological opening and closing to clean up borders and fill holes
- [x] Implement connected components analysis to filter out changes smaller than `minimum_area_m2`
- [x] Export `output/raster/change_score.tif` and `output/raster/change_mask.tif`

FILES CREATED:
- `output/raster/change_score.tif`
- `output/raster/change_mask.tif`
- `src/change_detection/detector.py`
- `tracking/phase_P04_report.md`

FILES MODIFIED:
- `PROJECT_STATUS.md`
- `tracking/MASTER_TRACKER.md`

TESTS EXECUTED:
- Ran `src/change_detection/detector.py` on preprocessed TIFFs.

TEST RESULTS:
Change detection run succeeded. Raw difference raster and filtered binary change mask raster were generated. Total changed area is 9,110.52 square meters (approx 2.055% of the scene area). Small noise blobs (under 15 m2 or 667 pixels) were successfully filtered out.

OUTPUTS VERIFIED:
- Confirmed the existence of `/home/jupyter/Apple_Change_Detection_POC/output/raster/change_score.tif` and `change_mask.tif`.
- Checked dimensions match 6162x3198 and georeferencing is preserved.

KNOWN LIMITATIONS:
None.

NEXT PHASE:
Phase 5 &mdash; Change Polygonization

EVIDENCE:
Running `detector.py` successfully completed and output:
`Area changed: 9110.52 m2 (2.055%)`
This is written correctly to both the GeoTIFF files with identical geotransforms.
