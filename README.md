# Apple Change Detection & Automated Map Update POC

A real, runnable Geospatial Remote Sensing Proof of Concept (POC) designed to detect temporal changes between high-resolution satellite imagery, segment new GIS map features (buildings, roads, construction footprints), validate topological networks, generate human QA inspection logs, and compile standard GIS deliverables.

---

## 🚀 Project Objectives
The objective of this system is to automate the map updating pipeline from imagery to map-ready deliverables:
1. **Change Detection**: Isolate physical change boundaries (e.g. new structures, roads, clearing) while rejecting false positives (e.g. seasonal vegetation, illumination shadow variation).
2. **Feature Extraction**: Automatically extract vector boundaries representing building roofs (polygons), road networks (skeletal centerlines), and construction sites (footprints).
3. **Quality & Topology**: Validate geometric correctness and logical connections (junctions vs dead-ends) to alert on dangling lines or disconnected networks.
4. **Human-In-The-Loop QA**: Compile automated review tasks prioritizing features based on detection confidence, allowing spatial edits and approvals.
5. **GIS Deliverables Compilation**: Bundle outputs into standardized, authoritative GIS assets (Master GeoPackage, ESRI Shapefiles, WGS84 GeoJSONs, and an interactive Leaflet map preview).

---

## 🛠️ GIS System Architecture

The pipeline is designed using a **modular, sequential phase-gate workflow**:

```text
+-----------------------+      +---------------------------+      +---------------------------+
|  01. Data Ingestion   | ---> |     02. Preprocessing     | ---> |   03. Image Registration  |
|  (TIFF GSD & Metadata)|      |   (RGB + Alpha masking)   |      |  (Visual Phase Correlate) |
+-----------------------+      +---------------------------+      +---------------------------+
                                                                                |
                                                                                v
+-----------------------+      +---------------------------+      +---------------------------+
| 06. False-Change      | <--- | 05. Change                | <--- |   04. Change Detection    |
| (Veg/Shadow Filters)  |      | (Raster-to-Vector GPKG)   |      |  (Smoothing & Threshold)  |
+-----------------------+      +---------------------------+      +---------------------------+
            |
            v
+-----------------------+      +---------------------------+      +---------------------------+
|  07. AOI Generation   | ---> |  08. Feature Extraction   | ---> |    09. Road Topology      |
| (Buffering & Clipping)|      | (Buildings/Roads/Const)   |      |  (Graph Vertex Snapping)  |
+-----------------------+      +---------------------------+      +---------------------------+
                                                                                |
                                                                                v
+-----------------------+      +---------------------------+      +---------------------------+
|  12. QA Task Compiler | <--- |   11. Quality/Confidence  | <--- |   10. Schema Attributes   |
| (Priority Pin Marker) |      |   (HIGH/MEDIUM/LOW scores)|      |   (Enforce Provenance)    |
+-----------------------+      +---------------------------+      +---------------------------+
            |
            v
+---------------------------------------------------------------------------------------------+
|                                13-19. Consolidated Deliverables                             |
|  (Apple_POC_Final.gpkg, Shapefiles ZIP, WGS84 GeoJSONs, Standalone Leaflet Map Preview HTML) |
+---------------------------------------------------------------------------------------------+
```

---

## 📦 Directory Structure

The repository follows a strict, highly organized GIS production structure:

```text
Apple_Change_Detection_POC/
│
├── app.py                          # Streamlit Interactive Web Application
├── recommended.txt                 # Deployment, installation, and environment guide
├── requirements.txt                # Python libraries dependencies manifest
├── LICENSE.txt                     # Standard MIT License and Open-Source Software Inventory
├── DEVELOPER_GUIDE.md              # VS Code Launch Guide for Windows Launcher
├── run_app.bat                     # One-click Windows Batch file launcher
├── PROJECT_STATUS.md               # Dynamic project development status ledger
│
├── Tools/                          # DD_Style flat-file source compilations
│   └── folder_to_txt.py            # Flat-file snapshot compiler
├── Apple_POC_V1_Source.txt         # Sourced codebase tree compilation (V1 snapshot)
├── Apple_POC_V2_Source.txt         # Sourced codebase tree compilation (V2 snapshot)
│
├── src/                            # Modular pipeline Python packages
│   ├── ingestion/                  # Data ingestion and verification
│   ├── preprocessing/              # Band selection and Alpha NoData masking
│   ├── registration/               # Sub-pixel visual phase correlation
│   ├── change_detection/           # Baseline detector & polygonization
│   ├── false_change_filter/        # Area, vegetation, and shadow filters
│   ├── aoi/                        # Buffering, dissolve, and clipping
│   ├── feature_extraction/         # Compact segmenters and centerline skeletons
│   ├── topology/                   # Endpoint connectivity & NetworkX graph validation
│   ├── attributes/                 # Schema tables and lineage provenance
│   ├── qa/                         # Automated tasks priority scoring
│   ├── evaluation/                 # Ground-truth overlap precision engine
│   └── export/                     # GPKG, Shapefile and GeoJSON compiles
│
├── data/                           # Sized geospatial inputs
│   ├── examples/                   # Compressed temporal TIFFs (2024, 2025, 2026)
│   ├── working/                    # Aligned RGB intermediate rasters
│   └── reference/                  # Expected ground-truth GeoPackage reference
│
├── output/                         # Main deliverables outputs
│   ├── raster/                     # Georeferenced change mask & score GeoTIFFs
│   ├── gis/                        # Consolidated Master GPKG (10 layers)
│   ├── geojson/                    # WGS84 GeoJSON layers for Leaflet
│   ├── shapefile/                  # Individual ESRI Shapefile directories
│   ├── packages/                   # Compiled results zip packages
│   ├── evaluation/                 # Precision/Recall reports and plot charts
│   └── preview/                    # Standalone interactive Leaflet web map
│
└── tests/                          # Automated PyTest unit/integration suites
    ├── test_pipeline.py            # 12-stage sequential pytest suite
    ├── verify_installation.py      # Automated requirements check
    └── verify_git.py               # Automated git status, commits, and SSH validation
```

---

## ⚡ How To Run the Application

The POC can be run through multiple interfaces to accommodate any deployment pipeline:

### 1. The streamlit Web Interface (Recommended)
This launches a gorgeous, 10-tab visual GIS workspace enabling real-time slider controls to tune parameters, click-and-run execution, live logs, interactive QA edits, and map visualisations.
- **How to Launch**:
  - Run the Windows Launcher: **Double-click `run_app.bat`** (or open it inside VS Code following the **`DEVELOPER_GUIDE.md`**!).
  - Or manually execute from terminal:
    ```bash
    streamlit run app.py
    ```

### 2. Sourced Command-Line Pipelines
You can trigger individual modules directly:
- **Change Detection**: `python3 src/change_detection/detector.py`
- **Feature Extraction**: `python3 src/feature_extraction/extractor.py`
- **Topology Assessment**: `python3 src/topology/topology.py`
- **Consolidated Master GPKG**: `python3 src/export/master_geopackage.py`

---

## 🧪 Testing & Validation Strategy

The codebase enforces robust quality-assurance checking through three dedicated test layers:

1. **Pipeline Integration Tests (`tests/test_pipeline.py`)**
   - Asserts that every single pipeline component runs without throwing exceptions on standard paths, verifying coordinates, bands, transforms, and layer file creation.
   - Run command: `python3 -m pytest tests/test_pipeline.py`
2. **Clean-Install Validation (`tests/verify_installation.py`)**
   - Parses `requirements.txt` and tests that all 13 Python modules are importable and logs their exact active versions.
   - Run command: `python3 tests/verify_installation.py`
3. **Git State Verification (`tests/verify_git.py`)**
   - Validates git status responsiveness, checks commit histories, tracks configured remotes, and tests secure client-side SSH handshakes with GitHub.
   - Run command: `python3 tests/verify_git.py`

---

## 📋 Delivery & Acceptance Checklist

To verify that the system is fully production-ready, ensure the following checkpoints are satisfied:

- [x] All 28 sequential phases (Phase 0 to 27) have been executed, tested, and reported successfully.
- [x] All required raster files (`change_score.tif`, `change_mask.tif`, `AOI_001.tif`) retain identical spatial transforms and georeferencing coordinate grids (EPSG:3857).
- [x] All required vector layers are correctly integrated as relational tables inside the master GeoPackage container `Apple_POC_Final.gpkg`.
- [x] High-resolution sample TIFF images are compressed under **50 MB** using lossless LZW compression, comfortably satisfying GitHub soft-warnings.
- [x] Handshake authentication via Git SSH is configured and successfully pushed to GitHub on the `master` branch.
- [x] Standalone interactive Leaflet web map preview (`Apple_POC_Map_Preview.html`) displays styled polygons, lines, and priority-colored QA markers.
- [x] State-handoff state has been preserved inside `/home/jupyter/Gemini_CLI_nxt_VM_Prompt.txt`.
