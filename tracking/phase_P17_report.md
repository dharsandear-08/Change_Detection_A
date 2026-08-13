# Phase Report: P17

PHASE:
P17

OBJECTIVE:
Export and verify standard WGS84 (EPSG:4326) GeoJSON files for map preview and web visualization.

STATUS:
PASS

TASKS:
- [x] Sourced vector layers: changes (filtered changes), roads, buildings, construction, qa_tasks
- [x] Reproject all spatial layers from EPSG:3857 to standard WGS84 (EPSG:4326) for browser/Leaflet mapping
- [x] Generate and verify five outputs inside `output/geojson/`:
  - `changes.geojson`
  - `roads.geojson`
  - `buildings.geojson`
  - `construction.geojson`
  - `qa_tasks.geojson`

FILES CREATED:
- `output/geojson/changes.geojson`
- `output/geojson/roads.geojson`
- `output/geojson/buildings.geojson`
- `output/geojson/construction.geojson`
- `output/geojson/qa_tasks.geojson`
- `src/export/geojson_export.py`
- `tracking/phase_P17_report.md`

FILES MODIFIED:
- `PROJECT_STATUS.md`
- `tracking/MASTER_TRACKER.md`

TESTS EXECUTED:
- Ran `src/export/geojson_export.py` to compile and verify WGS84 outputs.

TEST RESULTS:
All 5 required GeoJSON layers successfully exported and verified as valid EPSG:4326 structures.

OUTPUTS VERIFIED:
- Inspected the coordinates inside `/home/jupyter/Apple_Change_Detection_POC/output/geojson/changes.geojson`. Confirmed decimal degree values (longitude, latitude) are in standard WGS84 coordinates (approx -81.77, 26.54 for the scene bounds).

KNOWN LIMITATIONS:
None.

NEXT PHASE:
Phase 18 &mdash; Raster Outputs
