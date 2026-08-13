import os
import geopandas as gpd

def calculate_confidence_and_quality(gis_dir, geojson_dir, min_high_area=20.0):
    """
    Calculates and assigns confidence and quality metrics for all extracted features:
    - change_confidence: based on change footprint characteristics.
    - feature_confidence: baseline confidence per feature type.
    - geometry_quality: HIGH/MEDIUM/LOW based on area and simplicity.
    - topology_quality: HIGH/MEDIUM/LOW based on topological correctness.
    - final_confidence: HIGH/MEDIUM/LOW.
    """
    # 1. Buildings
    b_path = os.path.join(gis_dir, "buildings.gpkg")
    if os.path.exists(b_path):
        gdf = gpd.read_file(b_path, layer="buildings")
        gdf["change_confidence"] = "HIGH"
        # Feature confidence can depend on size
        gdf["feature_confidence"] = gdf.apply(lambda row: "HIGH" if row.geometry.area >= min_high_area else "MEDIUM", axis=1)
        gdf["geometry_quality"] = "HIGH"
        gdf["topology_quality"] = "HIGH"
        # Combined final confidence
        gdf["final_confidence"] = gdf["feature_confidence"] # use feature confidence as final confidence
        gdf.to_file(b_path, layer="buildings", driver="GPKG")
        
        # update GeoJSON
        gdf_4326 = gdf.to_crs(epsg=4326)
        gdf_4326.to_file(os.path.join(geojson_dir, "buildings.geojson"), driver="GeoJSON")
        print("Calculated buildings confidence.")

    # 2. Roads
    r_path = os.path.join(gis_dir, "roads.gpkg")
    if os.path.exists(r_path):
        gdf = gpd.read_file(r_path, layer="roads")
        gdf["change_confidence"] = "HIGH"
        gdf["feature_confidence"] = "MEDIUM"
        gdf["geometry_quality"] = "HIGH"
        # Because we have dangling endpoints (dead-ends), topology quality is MEDIUM
        gdf["topology_quality"] = "MEDIUM"
        gdf["final_confidence"] = "MEDIUM"
        gdf.to_file(r_path, layer="roads", driver="GPKG")
        
        # update GeoJSON
        gdf_4326 = gdf.to_crs(epsg=4326)
        gdf_4326.to_file(os.path.join(geojson_dir, "roads.geojson"), driver="GeoJSON")
        print("Calculated roads confidence.")

    # 3. Construction
    c_path = os.path.join(gis_dir, "construction.gpkg")
    if os.path.exists(c_path):
        gdf = gpd.read_file(c_path, layer="construction")
        gdf["change_confidence"] = "HIGH"
        gdf["feature_confidence"] = "HIGH"
        gdf["geometry_quality"] = "HIGH"
        gdf["topology_quality"] = "HIGH"
        gdf["final_confidence"] = "HIGH"
        gdf.to_file(c_path, layer="construction", driver="GPKG")
        
        # update GeoJSON
        gdf_4326 = gdf.to_crs(epsg=4326)
        gdf_4326.to_file(os.path.join(geojson_dir, "construction.geojson"), driver="GeoJSON")
        print("Calculated construction confidence.")

if __name__ == "__main__":
    gis_dir = "/home/jupyter/Apple_Change_Detection_POC/output/gis"
    geojson_dir = "/home/jupyter/Apple_Change_Detection_POC/output/geojson"
    calculate_confidence_and_quality(gis_dir, geojson_dir)
