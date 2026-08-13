import os
import pytest
import rasterio
import geopandas as gpd
import json

# Import pipeline steps
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

# Constants
BASE_DIR = "/home/jupyter/Apple_Change_Detection_POC/data/examples"
F2025 = os.path.join(BASE_DIR, "2025_demo_synthetic.tif")
F2026 = os.path.join(BASE_DIR, "2026_OG_Image.tif")

TEST_WORKING_DIR = "/home/jupyter/Apple_Change_Detection_POC/data/working"
TEST_OUTPUT_DIR = "/home/jupyter/Apple_Change_Detection_POC/output"

@pytest.fixture(scope="module")
def setup_dirs():
    os.makedirs(TEST_WORKING_DIR, exist_ok=True)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

def test_preprocessing(setup_dirs):
    p_hist = os.path.join(TEST_WORKING_DIR, "prepared_historical.tif")
    p_curr = os.path.join(TEST_WORKING_DIR, "prepared_current.tif")
    
    # Run
    run_preprocessing_pipeline(F2025, F2026, p_hist, p_curr)
    
    # Assert
    assert os.path.exists(p_hist)
    assert os.path.exists(p_curr)
    with rasterio.open(p_hist) as src:
        assert src.count == 3
        assert src.dtypes[0] == "uint8"

def test_registration(setup_dirs):
    p_hist = os.path.join(TEST_WORKING_DIR, "prepared_historical.tif")
    p_curr = os.path.join(TEST_WORKING_DIR, "prepared_current.tif")
    reg_report = os.path.join(TEST_OUTPUT_DIR, "registration_report.json")
    
    # Run
    register_images(p_hist, p_curr, reg_report)
    
    # Assert
    assert os.path.exists(reg_report)
    with open(reg_report, "r") as f:
        data = json.load(f)
    assert data["status"] in ["ALREADY_ALIGNED", "WARPED_AND_ALIGNED"]
    assert "dx" in data
    assert "dy" in data

def test_change_detection(setup_dirs):
    p_hist = os.path.join(TEST_WORKING_DIR, "prepared_historical.tif")
    p_curr = os.path.join(TEST_WORKING_DIR, "prepared_current.tif")
    score_out = os.path.join(TEST_OUTPUT_DIR, "raster", "change_score.tif")
    mask_out = os.path.join(TEST_OUTPUT_DIR, "raster", "change_mask.tif")
    
    # Run
    detect_changes(p_hist, p_curr, score_out, mask_out)
    
    # Assert
    assert os.path.exists(score_out)
    assert os.path.exists(mask_out)

def test_polygonization(setup_dirs):
    mask_out = os.path.join(TEST_OUTPUT_DIR, "raster", "change_mask.tif")
    gpkg_raw = os.path.join(TEST_OUTPUT_DIR, "gis", "change_polygons.gpkg")
    geojson_raw = os.path.join(TEST_OUTPUT_DIR, "geojson", "changes.geojson")
    
    # Run
    polygonize_mask(mask_out, gpkg_raw, geojson_raw)
    
    # Assert
    assert os.path.exists(gpkg_raw)
    assert os.path.exists(geojson_raw)

def test_false_change_filter(setup_dirs):
    p_hist = os.path.join(TEST_WORKING_DIR, "prepared_historical.tif")
    p_curr = os.path.join(TEST_WORKING_DIR, "prepared_current.tif")
    gpkg_raw = os.path.join(TEST_OUTPUT_DIR, "gis", "change_polygons.gpkg")
    gpkg_raw_c = os.path.join(TEST_OUTPUT_DIR, "gis", "raw_changes.gpkg")
    gpkg_filt = os.path.join(TEST_OUTPUT_DIR, "gis", "filtered_changes.gpkg")
    
    # Run
    apply_filters(gpkg_raw, p_hist, p_curr, gpkg_raw_c, gpkg_filt)
    
    # Assert
    assert os.path.exists(gpkg_raw_c)
    assert os.path.exists(gpkg_filt)

def test_aoi_and_clips(setup_dirs):
    gpkg_filt = os.path.join(TEST_OUTPUT_DIR, "gis", "filtered_changes.gpkg")
    aoi_gpkg = os.path.join(TEST_OUTPUT_DIR, "gis", "aoi.gpkg")
    clips_dir = os.path.join(TEST_OUTPUT_DIR, "aoi_clips")
    
    # Run
    generate_aois(gpkg_filt, F2026, aoi_gpkg, clips_dir)
    
    # Assert
    assert os.path.exists(aoi_gpkg)
    assert os.path.exists(clips_dir)

def test_feature_extraction(setup_dirs):
    gpkg_filt = os.path.join(TEST_OUTPUT_DIR, "gis", "filtered_changes.gpkg")
    gis_dir = os.path.join(TEST_OUTPUT_DIR, "gis")
    geojson_dir = os.path.join(TEST_OUTPUT_DIR, "geojson")
    
    # Run
    extract_features(gpkg_filt, F2026, gis_dir, geojson_dir)
    
    # Assert
    assert os.path.exists(os.path.join(gis_dir, "buildings.gpkg"))
    assert os.path.exists(os.path.join(gis_dir, "roads.gpkg"))
    assert os.path.exists(os.path.join(gis_dir, "construction.gpkg"))

def test_topology(setup_dirs):
    gis_dir = os.path.join(TEST_OUTPUT_DIR, "gis")
    r_gpkg = os.path.join(gis_dir, "roads.gpkg")
    nodes_out = os.path.join(gis_dir, "road_nodes.gpkg")
    issues_out = os.path.join(gis_dir, "topology_issues.gpkg")
    topo_json = os.path.join(TEST_OUTPUT_DIR, "reports", "topology_report.json")
    
    # Run
    analyze_road_topology(r_gpkg, nodes_out, issues_out, topo_json)
    
    # Assert
    assert os.path.exists(nodes_out)
    assert os.path.exists(issues_out)
    assert os.path.exists(topo_json)

def test_attributes_enrichment(setup_dirs):
    gis_dir = os.path.join(TEST_OUTPUT_DIR, "gis")
    geojson_dir = os.path.join(TEST_OUTPUT_DIR, "geojson")
    
    # Run
    enrich_attributes(gis_dir, geojson_dir)
    
    # Assert
    # Check attributes of buildings
    gdf = gpd.read_file(os.path.join(gis_dir, "buildings.gpkg"), layer="buildings")
    assert "area_m2" in gdf.columns
    assert "attribute_source" in gdf.columns

def test_confidence_scoring(setup_dirs):
    gis_dir = os.path.join(TEST_OUTPUT_DIR, "gis")
    geojson_dir = os.path.join(TEST_OUTPUT_DIR, "geojson")
    
    # Run
    calculate_confidence_and_quality(gis_dir, geojson_dir)
    
    # Assert
    gdf = gpd.read_file(os.path.join(gis_dir, "buildings.gpkg"), layer="buildings")
    assert "final_confidence" in gdf.columns

def test_qa_task_generation(setup_dirs):
    gis_dir = os.path.join(TEST_OUTPUT_DIR, "gis")
    geojson_dir = os.path.join(TEST_OUTPUT_DIR, "geojson")
    
    # Run
    generate_qa_tasks(gis_dir, geojson_dir)
    
    # Assert
    assert os.path.exists(os.path.join(gis_dir, "qa_tasks.gpkg"))

def test_evaluation(setup_dirs):
    gpkg_filt = os.path.join(TEST_OUTPUT_DIR, "gis", "filtered_changes.gpkg")
    gt_gpkg = "/home/jupyter/Apple_Change_Detection_POC/data/reference/synthetic_ground_truth.gpkg"
    m_json = os.path.join(TEST_OUTPUT_DIR, "evaluation", "change_detection_metrics.json")
    r_html = os.path.join(TEST_OUTPUT_DIR, "evaluation", "change_detection_report.html")
    v_png = os.path.join(TEST_OUTPUT_DIR, "evaluation", "change_detection_vis.png")
    
    # Run
    run_evaluation(gpkg_filt, gt_gpkg, m_json, r_html, v_png)
    
    # Assert
    assert os.path.exists(m_json)
    assert os.path.exists(r_html)
    assert os.path.exists(v_png)
