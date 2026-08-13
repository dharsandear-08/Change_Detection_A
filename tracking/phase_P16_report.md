# Phase Report: P16

PHASE:
P16

OBJECTIVE:
Export individual GIS spatial vector database layers to standard ESRI Shapefile formats and pack them into a zip archive.

STATUS:
PASS

TASKS:
- [x] Create separate subfolders for each feature type (changes, roads, buildings, construction, qa_tasks) under `output/shapefile/`
- [x] Export spatial features as standard ESRI Shapefile components (.shp, .shx, .dbf, .prj)
- [x] Handle mixed-geometry constraints for `qa_tasks` by dynamically computing centroids (Points) to avoid Shapefile write collisions
- [x] Package all subfolders into a single zip archive `/home/jupyter/Apple_Change_Detection_POC/output/packages/Apple_POC_Shapefiles.zip`

FILES CREATED:
- `output/shapefile/changes/`
- `output/shapefile/roads/`
- `output/shapefile/buildings/`
- `output/shapefile/construction/`
- `output/shapefile/qa_tasks/`
- `output/packages/Apple_POC_Shapefiles.zip`
- `src/export/shapefile_export.py`
- `tracking/phase_P16_report.md`

FILES MODIFIED:
- `PROJECT_STATUS.md`
- `tracking/MASTER_TRACKER.md`

TESTS EXECUTED:
- Ran `src/export/shapefile_export.py` to perform the conversion.

TESTS RESULTS:
All 5 layers were successfully converted to Shapefile sets. The `qa_tasks` layer was safely cast to Point geometries (centroids) to maintain strict Shapefile standards, and all files were successfully zipped.

OUTPUTS VERIFIED:
- Verified all directories and the compiled `.zip` file exist under `output/`.

KNOWN LIMITATIONS:
- Due to ESRI Shapefile column limit standards (10 characters max), some long attribute headers were automatically truncated/laundered (e.g. `feature_type` to `feature_ty`). This is normal and expected behaviour for Shapefile compatibility.

NEXT PHASE:
Phase 17 &mdash; GeoJSON
