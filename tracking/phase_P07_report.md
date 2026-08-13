# Phase Report: P07

PHASE:
P07

OBJECTIVE:
AOI Generation, spatial buffering, dissolving overlapping changes, and clipping original imagery for manual QA or automated localized inspection.

STATUS:
PASS

TASKS:
- [x] Select changes with status `KEEP` (meaningful changes)
- [x] Apply a 15-meter buffer to the selected changes
- [x] Dissolve and merge overlapping change buffers into unified AOIs
- [x] Generate `output/gis/aoi.gpkg` (layer: `"aoi"`)
- [x] Generate `output/geojson/aoi.geojson` (reprojected to EPSG:4326 for web preview)
- [x] Clip original current imagery (`2026_OG_image.TIF`) for each AOI into `output/aoi_clips/AOI_xxx.tif`

FILES CREATED:
- `output/gis/aoi.gpkg`
- `output/geojson/aoi.geojson`
- `output/aoi_clips/AOI_001.tif`
- `src/aoi/aoi.py`
- `tracking/phase_P07_report.md`

FILES MODIFIED:
- `PROJECT_STATUS.md`
- `tracking/MASTER_TRACKER.md`

TESTS EXECUTED:
- Ran `src/aoi/aoi.py` on the filtered change geometries.

TEST RESULTS:
AOI generation and image clipping completed successfully.
- Buffered valid change features (15m expansion).
- Dissolved and merged into exactly 1 AOI polygon.
- Clipped `2026_OG_Image.tif` to `AOI_001.tif`.

OUTPUTS VERIFIED:
- Confirmed `/home/jupyter/Apple_Change_Detection_POC/output/gis/aoi.gpkg` contains the layer `aoi`.
- Verified `/home/jupyter/Apple_Change_Detection_POC/output/aoi_clips/AOI_001.tif` was created and contains the correct georeferencing and image data (4 channels).

KNOWN LIMITATIONS:
None.

NEXT PHASE:
Phase 8 &mdash; Feature Extraction

EVIDENCE:
Output:
`AOI GeoPackage saved to /home/jupyter/Apple_Change_Detection_POC/output/gis/aoi.gpkg`
`Clipped imagery saved to: /home/jupyter/Apple_Change_Detection_POC/output/aoi_clips/AOI_001.tif`
`Total AOIs generated and clipped: 1`
The clipped image is georeferenced and matches the spatial bounding coordinates of the expanded change zone.
