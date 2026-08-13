import os
import geopandas as gpd

def generate_qa_tasks(gis_dir, geojson_dir):
    """
    Generates QA Tasks from extracted features (buildings, roads, construction)
    - Aggregates all features.
    - Creates corresponding QA task records.
    - Determines priority based on confidence (LOW/MEDIUM confidence gets higher QA priority).
    - Saves output as GPKG and reprojected GeoJSON.
    """
    os.makedirs(gis_dir, exist_ok=True)
    os.makedirs(geojson_dir, exist_ok=True)
    
    features_list = []
    
    # Load buildings
    b_path = os.path.join(gis_dir, "buildings.gpkg")
    if os.path.exists(b_path):
        gdf = gpd.read_file(b_path, layer="buildings")
        for idx, row in gdf.iterrows():
            features_list.append({
                "geometry": row.geometry,
                "feature_id": row["feature_id"],
                "change_id": row["change_id"],
                "feature_type": "building",
                "confidence": row["final_confidence"]
            })
            
    # Load roads
    r_path = os.path.join(gis_dir, "roads.gpkg")
    if os.path.exists(r_path):
        gdf = gpd.read_file(r_path, layer="roads")
        for idx, row in gdf.iterrows():
            features_list.append({
                "geometry": row.geometry,
                "feature_id": row["feature_id"],
                "change_id": row["change_id"],
                "feature_type": "road",
                "confidence": row["final_confidence"]
            })
            
    # Load construction
    c_path = os.path.join(gis_dir, "construction.gpkg")
    if os.path.exists(c_path):
        gdf = gpd.read_file(c_path, layer="construction")
        for idx, row in gdf.iterrows():
            features_list.append({
                "geometry": row.geometry,
                "feature_id": row["feature_id"],
                "change_id": row["change_id"],
                "feature_type": "construction",
                "confidence": row["final_confidence"]
            })
            
    if not features_list:
        print("No features found to generate QA tasks.")
        # Save empty
        qa_gdf = gpd.GeoDataFrame(columns=[
            "geometry", "task_id", "feature_id", "change_id", "feature_type",
            "confidence", "priority", "status", "reason"
        ], crs="EPSG:3857")
    else:
        # Create GeoDataFrame
        qa_gdf = gpd.GeoDataFrame(features_list, crs="EPSG:3857")
        
        # Assign fields
        qa_gdf["task_id"] = [f"TSK_{i+1:03d}" for i in range(len(qa_gdf))]
        
        # Determine priority: HIGH confidence -> LOW priority QA, MEDIUM/LOW confidence -> HIGH/MEDIUM priority
        def get_priority(conf):
            if conf == "LOW":
                return "HIGH"
            elif conf == "MEDIUM":
                return "MEDIUM"
            else:
                return "LOW"
                
        qa_gdf["priority"] = qa_gdf["confidence"].apply(get_priority)
        qa_gdf["status"] = "PENDING_QA"
        qa_gdf["reason"] = "new_feature_candidate"
        
    # Save GPKG
    gpkg_out = os.path.join(gis_dir, "qa_tasks.gpkg")
    qa_gdf.to_file(gpkg_out, layer="qa_tasks", driver="GPKG")
    print(f"QA Tasks GeoPackage saved to: {gpkg_out}")
    
    # Save WGS84 GeoJSON
    geojson_out = os.path.join(geojson_dir, "qa_tasks.geojson")
    if not qa_gdf.empty:
        qa_gdf_4326 = qa_gdf.to_crs(epsg=4326)
    else:
        qa_gdf_4326 = qa_gdf.copy()
        qa_gdf_4326.crs = "EPSG:4326"
    qa_gdf_4326.to_file(geojson_out, driver="GeoJSON")
    print(f"QA Tasks GeoJSON saved to: {geojson_out}")
    
    print(f"Total QA Tasks generated: {len(qa_gdf)}")
    return len(qa_gdf)

if __name__ == "__main__":
    gis_dir = "/home/jupyter/Apple_Change_Detection_POC/output/gis"
    geojson_dir = "/home/jupyter/Apple_Change_Detection_POC/output/geojson"
    generate_qa_tasks(gis_dir, geojson_dir)
