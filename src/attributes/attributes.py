import os
import geopandas as gpd

def enrich_attributes(gis_dir, geojson_dir):
    """
    Enriches buildings, roads, and construction layers with standard GIS attributes.
    Enforces the evidence hierarchy and uses 'UNKNOWN' for unproven attributes.
    Adds attribute_source to track provenance.
    """
    # 1. Buildings
    b_path = os.path.join(gis_dir, "buildings.gpkg")
    if os.path.exists(b_path):
        b_gdf = gpd.read_file(b_path, layer="buildings")
        b_gdf["area_m2"] = b_gdf.geometry.area
        b_gdf["height_m"] = "UNKNOWN"
        b_gdf["material"] = "UNKNOWN"
        b_gdf["attribute_source"] = "imagery_derived_deterministic"
        b_gdf.to_file(b_path, layer="buildings", driver="GPKG")
        
        # update GeoJSON
        b_gdf_4326 = b_gdf.to_crs(epsg=4326)
        b_gdf_4326.to_file(os.path.join(geojson_dir, "buildings.geojson"), driver="GeoJSON")
        print("Enriched buildings attributes.")

    # 2. Roads
    r_path = os.path.join(gis_dir, "roads.gpkg")
    if os.path.exists(r_path):
        r_gdf = gpd.read_file(r_path, layer="roads")
        r_gdf["road_name"] = "UNKNOWN"
        r_gdf["speed_limit"] = "UNKNOWN"
        r_gdf["lanes"] = "UNKNOWN"
        r_gdf["surface"] = "UNKNOWN"
        r_gdf["access"] = "UNKNOWN"
        r_gdf["length_m"] = r_gdf.geometry.length
        r_gdf["attribute_source"] = "imagery_derived_deterministic"
        r_gdf.to_file(r_path, layer="roads", driver="GPKG")
        
        # update GeoJSON
        r_gdf_4326 = r_gdf.to_crs(epsg=4326)
        r_gdf_4326.to_file(os.path.join(geojson_dir, "roads.geojson"), driver="GeoJSON")
        print("Enriched roads attributes.")

    # 3. Construction
    c_path = os.path.join(gis_dir, "construction.gpkg")
    if os.path.exists(c_path):
        c_gdf = gpd.read_file(c_path, layer="construction")
        c_gdf["status"] = "ACTIVE"
        c_gdf["type"] = "CONSTRUCTION_FOOTPRINT"
        c_gdf["attribute_source"] = "imagery_derived_deterministic"
        c_gdf.to_file(c_path, layer="construction", driver="GPKG")
        
        # update GeoJSON
        c_gdf_4326 = c_gdf.to_crs(epsg=4326)
        c_gdf_4326.to_file(os.path.join(geojson_dir, "construction.geojson"), driver="GeoJSON")
        print("Enriched construction attributes.")

if __name__ == "__main__":
    gis_dir = "/home/jupyter/Apple_Change_Detection_POC/output/gis"
    geojson_dir = "/home/jupyter/Apple_Change_Detection_POC/output/geojson"
    enrich_attributes(gis_dir, geojson_dir)
