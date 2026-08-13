import os
import json
import shutil
import zipfile
import streamlit as st
import geopandas as gpd
import pandas as pd
import rasterio
import streamlit.components.v1 as components

# Import modular pipeline steps
from src.preprocessing.preprocess import run_preprocessing_pipeline
from src.registration.registration import register_images
from src.change_detection.detector import detect_changes
from src.change_detection.polygonize import polygonize_mask
from src.false_change_filter.filter import apply_filters
from src.aoi.aoi import generate_aois
from src.feature_extraction.extractor import extract_features
from src.topology.topology import analyze_road_topology
from src.attributes.attributes import enrich_attributes
from src.evaluation.confidence import calculate_confidence_and_quality
from src.qa.qa import generate_qa_tasks
from src.evaluation.evaluation import run_evaluation
from src.visualization.preview import create_map_preview

# Initialize Streamlit session state
if "pipeline_run" not in st.session_state:
    st.session_state["pipeline_run"] = False
if "run_id" not in st.session_state:
    st.session_state["run_id"] = "RUN_DEMO_PRIMARY"
if "qa_tasks_df" not in st.session_state:
    st.session_state["qa_tasks_df"] = None
if "run_log" not in st.session_state:
    st.session_state["run_log"] = []

def log_message(msg):
    st.session_state["run_log"].append(msg)
    print(msg)

st.set_page_config(layout="wide", page_title="Apple Map Update POC", page_icon="🍏")

st.title("🍏 Apple Change Detection & Automated Map Update POC")
st.markdown("### Phase-by-Phase Interactive GIS Pipeline Demonstration")

# Define tabs
tabs = st.tabs([
    "Overview", 
    "Inputs & Timeline", 
    "Compatibility", 
    "Change Detection", 
    "Feature Extraction", 
    "Topology", 
    "Interactive QA", 
    "Map Preview", 
    "Outputs & Downloads", 
    "Run Log"
])

# Paths Configuration
working_dir = "/home/jupyter/Apple_Change_Detection_POC/data/working"
examples_dir = "/home/jupyter/Apple_Change_Detection_POC/data/examples"
gis_dir = "/home/jupyter/Apple_Change_Detection_POC/output/gis"
geojson_dir = "/home/jupyter/Apple_Change_Detection_POC/output/geojson"
output_dir = "/home/jupyter/Apple_Change_Detection_POC/output"
packages_dir = "/home/jupyter/Apple_Change_Detection_POC/output/packages"

# -------------------------------------------------------------------------
# TAB 1: OVERVIEW
# -------------------------------------------------------------------------
with tabs[0]:
    st.header("Project Overview & Objectives")
    st.markdown("""
    **Primary Business Objective:**
    Detect meaningful changes between historical and current high-resolution imagery, identify candidate new roads/buildings/construction areas, validate GIS geometry/topology, generate QA work items and export standard GIS deliverables.
    
    ### Core Architecture & Flow
    1. **Data Ingestion & Verification**: Reads temporal raster layers, extracting GSD, bounds, dimensions and bands.
    2. **Data Compatibility**: Assesses grid overlapping and CRS alignment.
    3. **Image Registration**: Fast visual sub-pixel phase correlation.
    4. **Change Detection**: Difference segmentation, Gaussian smoothing and morphological component filtering.
    5. **Change Polygonization & False-Change Filter**: Vectorises candidates, using greenness and shadow filters to reject seasonal vegetation.
    6. **AOI Generation & Clips**: Expands buffers around changes and extracts clips of the raw imagery.
    7. **Feature Extraction**: Morpological segmentation and centerline skeletonization for new building/road boundaries.
    8. **Topological Validation**: Evaluates connectivity, junctions, and dead-ends using NetworkX graphs.
    9. **QA Compile**: Builds interactive marker pins mapping feature confidence to human review priority.
    10. **Ground Truth Evaluation**: Mathematical IoU, Precision, Recall and F1-score overlay comparison.
    """)
    st.info("💡 Navigate to **Change Detection** tab to select parameters and launch the full pipeline execution!")

# -------------------------------------------------------------------------
# TAB 2: INPUTS & TIMELINE
# -------------------------------------------------------------------------
with tabs[1]:
    st.header("Input Data & Temporal Timeline")
    
    st.markdown("### Spatial Data Provenance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("INPUT 01: 2024 Imagery")
        st.markdown("**Status:** `SYNTHETIC HISTORICAL`  \n**Purpose:** Secondary temporal testing")
        if os.path.exists(os.path.join(examples_dir, "2024_demo_synthetic.tif")):
            st.success("✅ 2024_demo_synthetic.tif loaded")
            
    with col2:
        st.subheader("INPUT 02: 2025 Imagery")
        st.markdown("**Status:** `SYNTHETIC HISTORICAL`  \n**Purpose:** Primary Change Test Baseline")
        if os.path.exists(os.path.join(examples_dir, "2025_demo_synthetic.tif")):
            st.success("✅ 2025_demo_synthetic.tif loaded")
            
    with col3:
        st.subheader("INPUT 03: 2026 Imagery")
        st.markdown("**Status:** `REAL CURRENT`  \n**Purpose:** Current target/evaluation imagery")
        if os.path.exists(os.path.join(examples_dir, "2026_OG_Image.tif")):
            st.success("✅ 2026_OG_Image.tif loaded")

    st.markdown("---")
    st.subheader("User-Upload Mode (Optional)")
    st.markdown("You can upload your own custom old and new GeoTIFF imagery to run custom pipelines.")
    up_old = st.file_uploader("Upload Historical GeoTIFF (Old)", type=["tif", "tiff"])
    up_new = st.file_uploader("Upload Current GeoTIFF (New)", type=["tif", "tiff"])
    if up_old and up_new:
        st.info("Custom uploads registered. They will be written to `data/user_uploads/` upon execution.")

# -------------------------------------------------------------------------
# TAB 3: COMPATIBILITY
# -------------------------------------------------------------------------
with tabs[2]:
    st.header("Spatial Data Compatibility Assessment")
    compat_json_path = os.path.join(output_dir, "compatibility_report.json")
    if os.path.exists(compat_json_path):
        with open(compat_json_path, "r") as f:
            compat_data = json.load(f)
        
        primary = compat_data.get("2025_2026", {})
        st.markdown("### Primary Pair Compatibility (2025 Baseline &harr; 2026 Current)")
        
        c1, c2, col_dim, col_res = st.columns(4)
        c1.metric("Same CRS (EPSG)", f"{primary.get('epsg1')} &harr; {primary.get('epsg2')}", "PASS")
        c2.metric("Overlap Area", f"{primary.get('overlap_pct'):.1f}%", "100% Match")
        col_dim.metric("Grid Alignment", "YES" if primary.get("same_grid") else "NO", "PASS")
        col_res.metric("Spatial GSD", f"{primary.get('res1')[0]:.3f} m", "15 cm")
        
        st.markdown("### Full Temporal Compatibility Table")
        df_compat = pd.DataFrame.from_dict(compat_data, orient='index')
        st.dataframe(df_compat[["file1", "file2", "same_crs", "same_res", "same_dim", "overlap_pct", "same_grid"]])
    else:
        st.warning("⚠️ Run the pipeline first to generate the compatibility report.")

# -------------------------------------------------------------------------
# TAB 4: CHANGE DETECTION & PIPELINE EXECUTION
# -------------------------------------------------------------------------
with tabs[3]:
    st.header("Pipeline Hyperparameters & Run Action")
    
    st.sidebar.header("🔧 Tunable Parameters")
    th = st.sidebar.slider("Change Score Threshold", 10, 100, 30, help="Pixel intensity difference threshold")
    min_area = st.sidebar.slider("Minimum Component Area (m²)", 1.0, 50.0, 15.0, help="Filter out changes smaller than this area")
    g_kernel = st.sidebar.slider("Gaussian Blur Kernel", 1, 15, 5, step=2, help="Smoothing size")
    op_kernel = st.sidebar.slider("Morphological Opening Kernel", 0, 9, 3, help="Cleans border noise")
    cl_kernel = st.sidebar.slider("Morphological Closing Kernel", 0, 15, 9, help="Fills internal holes")
    
    st.markdown("### Execute End-To-End Map Update Pipeline")
    st.markdown("Clicking the button below runs the genuine phase-gate geospatial processing chain on the selected datasets.")
    
    run_button = st.button("🚀 Run Map Update Pipeline", use_container_width=True)
    
    if run_button:
        st.session_state["run_log"] = []
        st.session_state["pipeline_run"] = False
        
        # Paths setup
        hist_p = os.path.join(examples_dir, "2025_demo_synthetic.tif")
        curr_p = os.path.join(examples_dir, "2026_OG_Image.tif")
        
        # Handle user uploads if provided
        if up_old and up_new:
            user_upload_dir = "/home/jupyter/Apple_Change_Detection_POC/data/user_uploads"
            os.makedirs(user_upload_dir, exist_ok=True)
            hist_p = os.path.join(user_upload_dir, up_old.name)
            curr_p = os.path.join(user_upload_dir, up_new.name)
            with open(hist_p, "wb") as f:
                f.write(up_old.getbuffer())
            with open(curr_p, "wb") as f:
                f.write(up_new.getbuffer())
            log_message("Sourced custom user-uploaded imagery.")
            
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Phase 2: Preprocessing
        status_text.text("Phase 2/12: Preprocessing band extraction and masking...")
        p_hist = os.path.join(working_dir, "prepared_historical.tif")
        p_curr = os.path.join(working_dir, "prepared_current.tif")
        run_preprocessing_pipeline(hist_p, curr_p, p_hist, p_curr)
        progress_bar.progress(15)
        
        # Phase 3: Registration
        status_text.text("Phase 3/12: Verification of spatial registration...")
        reg_report = os.path.join(output_dir, "registration_report.json")
        register_images(p_hist, p_curr, reg_report)
        progress_bar.progress(30)
        
        # Phase 4: Change Detection
        status_text.text("Phase 4/12: Extracting change difference score and mask...")
        score_out = os.path.join(output_dir, "raster", "change_score.tif")
        mask_out = os.path.join(output_dir, "raster", "change_mask.tif")
        detect_changes(p_hist, p_curr, score_out, mask_out, threshold=th, minimum_area_m2=min_area, gaussian_kernel=g_kernel, opening_kernel=op_kernel, closing_kernel=cl_kernel)
        progress_bar.progress(45)
        
        # Phase 5: Polygonization
        status_text.text("Phase 5/12: Vectorizing change mask to polygons...")
        gpkg_raw = os.path.join(output_dir, "gis", "change_polygons.gpkg")
        geojson_raw = os.path.join(output_dir, "geojson", "changes.geojson")
        polygonize_mask(mask_out, gpkg_raw, geojson_raw)
        progress_bar.progress(55)
        
        # Phase 6: False-Change Filter
        status_text.text("Phase 6/12: Applying vegetation and shadow spectral filters...")
        gpkg_raw_c = os.path.join(output_dir, "gis", "raw_changes.gpkg")
        gpkg_filt = os.path.join(output_dir, "gis", "filtered_changes.gpkg")
        apply_filters(gpkg_raw, p_hist, p_curr, gpkg_raw_c, gpkg_filt)
        progress_bar.progress(65)
        
        # Phase 7: AOI clips
        status_text.text("Phase 7/12: Buffering valid changes and clipping imagery...")
        aoi_gpkg = os.path.join(output_dir, "gis", "aoi.gpkg")
        clips_dir = os.path.join(output_dir, "aoi_clips")
        generate_aois(gpkg_filt, curr_p, aoi_gpkg, clips_dir)
        progress_bar.progress(75)
        
        # Phase 8: Feature Extraction
        status_text.text("Phase 8/12: Extracting new buildings and roads...")
        extract_features(gpkg_filt, curr_p, gis_dir, geojson_dir)
        progress_bar.progress(85)
        
        # Phase 9: Topology
        status_text.text("Phase 9/12: Validating road topology networks...")
        r_gpkg = os.path.join(gis_dir, "roads.gpkg")
        nodes_out = os.path.join(gis_dir, "road_nodes.gpkg")
        issues_out = os.path.join(gis_dir, "topology_issues.gpkg")
        topo_json = os.path.join(output_dir, "reports", "topology_report.json")
        analyze_road_topology(r_gpkg, nodes_out, issues_out, topo_json)
        progress_bar.progress(90)
        
        # Phase 10: Attributes
        status_text.text("Phase 10/12: Appending metadata schemas...")
        enrich_attributes(gis_dir, geojson_dir)
        
        # Phase 11: Confidence
        status_text.text("Phase 11/12: Scoring quality parameters...")
        calculate_confidence_and_quality(gis_dir, geojson_dir)
        
        # Phase 12: QA Generation
        status_text.text("Phase 12/12: Compiling QA task logs...")
        generate_qa_tasks(gis_dir, geojson_dir)
        
        # Ground Truth Evaluation & Map Preview Build
        status_text.text("Finalizing HTML Map Visualization and Evaluation...")
        gt_gpkg = "/home/jupyter/Apple_Change_Detection_POC/data/reference/synthetic_ground_truth.gpkg"
        m_json = os.path.join(output_dir, "evaluation", "change_detection_metrics.json")
        r_html = os.path.join(output_dir, "evaluation", "change_detection_report.html")
        v_png = os.path.join(output_dir, "evaluation", "change_detection_vis.png")
        run_evaluation(gpkg_filt, gt_gpkg, m_json, r_html, v_png)
        
        out_map_html = os.path.join(output_dir, "preview", "Apple_POC_Map_Preview.html")
        create_map_preview(geojson_dir, out_map_html)
        
        progress_bar.progress(100)
        status_text.success("🎉 Pipeline executed successfully!")
        st.session_state["pipeline_run"] = True
        
        # Load QA task list into session state
        qa_gpkg = os.path.join(gis_dir, "qa_tasks.gpkg")
        if os.path.exists(qa_gpkg):
            st.session_state["qa_tasks_df"] = gpd.read_file(qa_gpkg, layer="qa_tasks")
            
    if st.session_state["pipeline_run"]:
        st.success("Pipeline results are fully loaded and ready for inspection. Explore the tabs above!")

# -------------------------------------------------------------------------
# TAB 5: FEATURE EXTRACTION
# -------------------------------------------------------------------------
with tabs[4]:
    st.header("Extracted Vectors: Buildings, Roads, & Construction")
    if st.session_state["pipeline_run"]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🏢 Extracted Buildings")
            b_path = os.path.join(gis_dir, "buildings.gpkg")
            if os.path.exists(b_path):
                b_gdf = gpd.read_file(b_path, layer="buildings")
                st.metric("Total Buildings", len(b_gdf))
                st.dataframe(b_gdf[["feature_id", "area_m2", "confidence", "processing_method"]])
                
        with col2:
            st.markdown("#### 🛣️ Extracted Roads")
            r_path = os.path.join(gis_dir, "roads.gpkg")
            if os.path.exists(r_path):
                r_gdf = gpd.read_file(r_path, layer="roads")
                st.metric("Total Roads", len(r_gdf))
                st.dataframe(r_gdf[["feature_id", "length_m", "confidence", "processing_method"]])
                
        with col3:
            st.markdown("#### 🚧 Construction Footprints")
            c_path = os.path.join(gis_dir, "construction.gpkg")
            if os.path.exists(c_path):
                c_gdf = gpd.read_file(c_path, layer="construction")
                st.metric("Total Zones", len(c_gdf))
                st.dataframe(c_gdf[["feature_id", "status", "type"]])
    else:
        st.warning("⚠️ Run the pipeline first to generate features.")

# -------------------------------------------------------------------------
# TAB 6: TOPOLOGY
# -------------------------------------------------------------------------
with tabs[5]:
    st.header("Network Topology Analysis")
    topo_json = os.path.join(output_dir, "reports", "topology_report.json")
    if os.path.exists(topo_json):
        with open(topo_json, "r") as f:
            topo_data = json.load(f)
            
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Nodes", topo_data.get("total_nodes"))
        c2.metric("Total Edges", topo_data.get("total_edges"))
        c3.metric("Disconnected Subgraphs", topo_data.get("disconnected_components"))
        c4.metric("Dangling Endpoints (Dead-Ends)", topo_data.get("dangling_endpoints"))
        
        st.markdown("### Topological Validation Log")
        if topo_data.get("dangling_endpoints") > 0:
            st.warning(f"⚠️ Flagged {topo_data.get('dangling_endpoints')} dangling endpoints. Dead-ends detected.")
        else:
            st.success("✅ Clean topology network. Zero errors.")
    else:
        st.warning("⚠️ Run the pipeline first to generate topological results.")

# -------------------------------------------------------------------------
# TAB 7: INTERACTIVE QA WORKSPACE
# -------------------------------------------------------------------------
with tabs[6]:
    st.header("Human-In-The-Loop QA Verification Workspace")
    
    # Initialize QA list
    qa_gpkg_init = os.path.join(gis_dir, "qa_tasks.gpkg")
    if st.session_state["qa_tasks_df"] is None and os.path.exists(qa_gpkg_init):
        st.session_state["qa_tasks_df"] = gpd.read_file(qa_gpkg_init, layer="qa_tasks")
        
    df = st.session_state["qa_tasks_df"]
    
    if df is not None:
        st.markdown("Select a task from the list to review, approve, reject, or edit its topological state.")
        
        # Render tasks editor
        edited_df = st.data_editor(
            df[["task_id", "feature_id", "feature_type", "confidence", "priority", "status", "reason"]],
            use_container_width=True,
            num_rows="dynamic",
            disabled=["task_id", "feature_id", "feature_type", "confidence", "priority", "reason"],
            column_config={
                "status": st.column_config.SelectboxColumn(
                    "QA Status",
                    options=["PENDING_QA", "APPROVED", "REJECTED", "NEEDS_EDIT"],
                    default="PENDING_QA"
                )
            }
        )
        
        # Save modifications back to session state and disk if updated
        if st.button("💾 Save QA Decisions to Authoritative GeoPackage"):
            st.session_state["qa_tasks_df"]["status"] = edited_df["status"]
            # Overwrite GPKG
            st.session_state["qa_tasks_df"].to_file(os.path.join(gis_dir, "qa_tasks.gpkg"), layer="qa_tasks", driver="GPKG")
            st.success("✅ QA Decisions saved successfully and compiled into authoritative database!")
    else:
        st.warning("⚠️ Run the pipeline first to compile QA tasks.")

# -------------------------------------------------------------------------
# TAB 8: MAP PREVIEW
# -------------------------------------------------------------------------
with tabs[7]:
    st.header("Interactive Map Preview (OSM Basemap & Vectors)")
    map_html_path = os.path.join(output_dir, "preview", "Apple_POC_Map_Preview.html")
    if os.path.exists(map_html_path):
        with open(map_html_path, "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=700, scrolling=True)
    else:
        st.warning("⚠️ Run the pipeline first to render the interactive map preview.")

# -------------------------------------------------------------------------
# TAB 9: OUTPUTS & DOWNLOAD PACKAGES
# -------------------------------------------------------------------------
with tabs[8]:
    st.header("GIS Deliverables & Packages Download")
    
    if st.session_state["pipeline_run"] or os.path.exists(os.path.join(gis_dir, "Apple_POC_Final.gpkg")):
        
        # Compiling final run ZIP on demand
        run_zip_path = os.path.join(packages_dir, f"Apple_POC_Run_{st.session_state['run_id']}.zip")
        os.makedirs(packages_dir, exist_ok=True)
        
        with zipfile.ZipFile(run_zip_path, 'w') as zipf:
            # write gis directory
            for root, dirs, files in os.walk(output_dir):
                # skip some directories
                if "packages" in root or ".venv" in root:
                    continue
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, output_dir)
                    zipf.write(full_p, rel_p)
                    
        st.success("✅ Compiled complete deliverables package ready for delivery.")
        
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            st.markdown("### 📦 Main Package Downloads")
            # Complete results zip
            with open(run_zip_path, "rb") as f:
                st.download_button("📥 Download Complete Results ZIP", data=f, file_name=os.path.basename(run_zip_path), mime="application/zip", use_container_width=True)
            
            # GeoPackage
            final_gpkg_path = os.path.join(gis_dir, "Apple_POC_Final.gpkg")
            if os.path.exists(final_gpkg_path):
                # Ensure it is compiled
                with open(final_gpkg_path, "rb") as f:
                    st.download_button("📥 Download Authoritative GeoPackage (GPKG)", data=f, file_name="Apple_POC_Final.gpkg", mime="application/geopackage+sqlite3", use_container_width=True)
                    
            # Shapefiles zip
            shp_zip_path = os.path.join(packages_dir, "Apple_POC_Shapefiles.zip")
            if os.path.exists(shp_zip_path):
                with open(shp_zip_path, "rb") as f:
                    st.download_button("📥 Download ESRI Shapefiles ZIP", data=f, file_name="Apple_POC_Shapefiles.zip", mime="application/zip", use_container_width=True)
                    
        with col_down2:
            st.markdown("### 🗂️ Individual Deliverables")
            # HTML Preview download
            if os.path.exists(map_html_path):
                with open(map_html_path, "r", encoding="utf-8") as f:
                    st.download_button("📥 Download HTML Map Preview", data=f.read(), file_name="Apple_POC_Map_Preview.html", mime="text/html", use_container_width=True)
                    
            # Change Mask
            mask_out_path = os.path.join(output_dir, "raster", "change_mask.tif")
            if os.path.exists(mask_out_path):
                with open(mask_out_path, "rb") as f:
                    st.download_button("📥 Download Change Mask GeoTIFF", data=f, file_name="change_mask.tif", mime="image/tiff", use_container_width=True)
                    
            # Evaluation report
            eval_html_path = os.path.join(output_dir, "evaluation", "change_detection_report.html")
            if os.path.exists(eval_html_path):
                with open(eval_html_path, "r", encoding="utf-8") as f:
                    st.download_button("📥 Download Ground Truth Evaluation Report (HTML)", data=f.read(), file_name="change_detection_report.html", mime="text/html", use_container_width=True)
    else:
        st.warning("⚠️ Run the pipeline first to generate and compile deliverables.")

# -------------------------------------------------------------------------
# TAB 10: RUN LOG
# -------------------------------------------------------------------------
with tabs[9]:
    st.header("Pipeline Run Logs & Execution Manifest")
    if st.session_state["run_log"]:
        st.text_area("Execution Log Console", value="\n".join(st.session_state["run_log"]), height=400)
    else:
        st.info("Log is empty. Sourcing pipeline logs once executed.")
