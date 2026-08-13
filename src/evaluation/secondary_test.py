import os
import json
from src.preprocessing.preprocess import run_preprocessing_pipeline
from src.registration.registration import register_images
from src.change_detection.detector import detect_changes
from src.change_detection.polygonize import polygonize_mask
from src.false_change_filter.filter import apply_filters
from src.evaluation.evaluation import run_evaluation

def run_secondary_test():
    """
    Runs the secondary temporal test: 2024_demo_synthetic.tif vs 2025_demo_synthetic.tif
    """
    base_dir = "/home/jupyter/Apple_Change_Detection_POC/data/examples"
    f2024 = os.path.join(base_dir, "2024_demo_synthetic.tif")
    f2025 = os.path.join(base_dir, "2025_demo_synthetic.tif")
    
    working_dir = "/home/jupyter/Apple_Change_Detection_POC/data/working"
    hist_out = os.path.join(working_dir, "prepared_historical_2024.tif")
    curr_out = os.path.join(working_dir, "prepared_current_2025.tif")
    
    output_dir = "/home/jupyter/Apple_Change_Detection_POC/output"
    
    print("="*60)
    print("RUNNING PHASE 14: SECONDARY TEMPORAL TEST (2024 VS 2025)")
    print("="*60)
    
    # 1. Preprocessing
    print("\n--- [Step 1] Preprocessing ---")
    run_preprocessing_pipeline(f2024, f2025, hist_out, curr_out)
    
    # 2. Registration
    print("\n--- [Step 2] Registration ---")
    reg_report_path = os.path.join(output_dir, "registration_report_2024_2025.json")
    register_images(hist_out, curr_out, reg_report_path)
    
    # 3. Change Detection
    print("\n--- [Step 3] Change Detection ---")
    score_out = os.path.join(output_dir, "raster", "change_score_2024_2025.tif")
    mask_out = os.path.join(output_dir, "raster", "change_mask_2024_2025.tif")
    detect_changes(hist_out, curr_out, score_out, mask_out, threshold=30, minimum_area_m2=15.0)
    
    # 4. Polygonization
    print("\n--- [Step 4] Polygonization ---")
    gpkg_raw = os.path.join(output_dir, "gis", "change_polygons_2024_2025.gpkg")
    geojson_raw = os.path.join(output_dir, "geojson", "changes_2024_2025.geojson")
    polygonize_mask(mask_out, gpkg_raw, geojson_raw, run_id="RUN_SECONDARY_2024_2025")
    
    # 5. False-Change Filter
    print("\n--- [Step 5] False-Change Filter ---")
    gpkg_filt_raw = os.path.join(output_dir, "gis", "raw_changes_2024_2025.gpkg")
    gpkg_filt_out = os.path.join(output_dir, "gis", "filtered_changes_2024_2025.gpkg")
    apply_filters(gpkg_raw, hist_out, curr_out, gpkg_filt_raw, gpkg_filt_out)
    
    # 6. Evaluation against 2024 Ground Truth
    print("\n--- [Step 6] Ground Truth Evaluation ---")
    gt_gpkg = "/home/jupyter/Apple_Change_Detection_POC/data/reference/synthetic_ground_truth_2024.gpkg"
    metrics_json = os.path.join(output_dir, "evaluation", "change_detection_metrics_2024_2025.json")
    report_html = os.path.join(output_dir, "evaluation", "change_detection_report_2024_2025.html")
    vis_png = os.path.join(output_dir, "evaluation", "change_detection_vis_2024_2025.png")
    
    run_evaluation(gpkg_filt_out, gt_gpkg, metrics_json, report_html, vis_png)
    
    print("\n" + "="*60)
    print("PHASE 14: SECONDARY TEMPORAL TEST SUCCESSFUL")
    print("="*60)

if __name__ == "__main__":
    run_secondary_test()
