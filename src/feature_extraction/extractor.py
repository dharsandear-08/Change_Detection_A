import os
import geopandas as gpd
from src.feature_extraction.detectors import BuildingDetector, RoadDetector, ConstructionDetector

def extract_features(filt_gpkg_path, current_raster_path, out_dir, geojson_dir):
    """
    Coordinates feature extraction:
    - Loads filtered changes with status 'KEEP'.
    - Runs BuildingDetector, RoadDetector, and ConstructionDetector on each change polygon.
    - Saves outputs to individual GPKG and GeoJSON files.
    """
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(geojson_dir, exist_ok=True)
    
    gdf_filt = gpd.read_file(filt_gpkg_path, layer="filtered_changes")
    gdf_keep = gdf_filt[gdf_filt["filter_status"] == "KEEP"].copy()
    
    building_gdfs = []
    road_gdfs = []
    construction_gdfs = []
    
    b_det = BuildingDetector()
    r_det = RoadDetector()
    c_det = ConstructionDetector()
    
    for idx, row in gdf_keep.iterrows():
        change_geom = row.geometry
        change_id = row["change_id"]
        
        # 1. Run Building Detection
        b_gdf = b_det.detect(current_raster_path, change_geom, change_id)
        if not b_gdf.empty:
            building_gdfs.append(b_gdf)
            
        # 2. Run Road Detection
        r_gdf = r_det.detect(current_raster_path, change_geom, change_id)
        if not r_gdf.empty:
            road_gdfs.append(r_gdf)
            
        # 3. Run Construction Detection
        c_gdf = c_det.detect(current_raster_path, change_geom, change_id)
        if not c_gdf.empty:
            construction_gdfs.append(c_gdf)
            
    # Concatenate and save
    categories = [
        ("buildings", building_gdfs, "building"),
        ("roads", road_gdfs, "road"),
        ("construction", construction_gdfs, "construction")
    ]
    
    for name, gdfs, ftype in categories:
        gpkg_path = os.path.join(out_dir, f"{name}.gpkg")
        geojson_path = os.path.join(geojson_dir, f"{name}.geojson")
        
        if gdfs:
            combined_gdf = gpd.GeoDataFrame(gpd.pd.concat(gdfs, ignore_index=True), crs=gdf_filt.crs)
        else:
            # Empty fallback GDF with required fields
            combined_gdf = gpd.GeoDataFrame(columns=[
                "geometry", "feature_id", "change_id", "feature_type", "confidence",
                "processing_method", "model_name", "model_version", "source", "qa_status"
            ], crs=gdf_filt.crs)
            
        # Save GPKG
        combined_gdf.to_file(gpkg_path, layer=name, driver="GPKG")
        print(f"Feature layer '{name}' saved to: {gpkg_path}")
        
        # Save GeoJSON (reprojected to 4326)
        if not combined_gdf.empty:
            combined_gdf_4326 = combined_gdf.to_crs(epsg=4326)
        else:
            combined_gdf_4326 = combined_gdf.copy()
            combined_gdf_4326.crs = "EPSG:4326"
            
        combined_gdf_4326.to_file(geojson_path, driver="GeoJSON")
        print(f"Feature layer '{name}' GeoJSON saved to: {geojson_path}")
        print(f"Total '{ftype}' features extracted: {len(combined_gdf)}")

if __name__ == "__main__":
    filt_gpkg = "/home/jupyter/Apple_Change_Detection_POC/output/gis/filtered_changes.gpkg"
    current_raster = "/home/jupyter/Apple_Change_Detection_POC/data/examples/2026_OG_Image.tif"
    
    out_dir = "/home/jupyter/Apple_Change_Detection_POC/output/gis"
    geojson_dir = "/home/jupyter/Apple_Change_Detection_POC/output/geojson"
    
    extract_features(filt_gpkg, current_raster, out_dir, geojson_dir)
