import os
import geopandas as gpd

def verify_and_finalize_geojson_exports(gis_dir, geojson_dir):
    """
    Verifies that all required GeoJSON layers exist and are in the proper WGS84 (EPSG:4326) CRS.
    Expected layers:
        - changes.geojson (filtered changes)
        - roads.geojson
        - buildings.geojson
        - construction.geojson
        - qa_tasks.geojson
    """
    os.makedirs(geojson_dir, exist_ok=True)
    
    # Mapping of expected GeoJSON files to their source GPKG and table names
    gpkg_mappings = [
        ("changes.geojson", "filtered_changes.gpkg", "filtered_changes"),
        ("roads.geojson", "roads.gpkg", "roads"),
        ("buildings.geojson", "buildings.gpkg", "buildings"),
        ("construction.geojson", "construction.gpkg", "construction"),
        ("qa_tasks.geojson", "qa_tasks.gpkg", "qa_tasks")
    ]
    
    for geojson_name, gpkg_name, layer_table in gpkg_mappings:
        gpkg_path = os.path.join(gis_dir, gpkg_name)
        out_path = os.path.join(geojson_dir, geojson_name)
        
        if os.path.exists(gpkg_path):
            try:
                # Load the layer
                gdf = gpd.read_file(gpkg_path, layer=layer_table)
                # Reproject to WGS84 for browser compatibility
                gdf_4326 = gdf.to_crs(epsg=4326)
                # Write to GeoJSON
                gdf_4326.to_file(out_path, driver="GeoJSON")
                print(f"Exported and verified GeoJSON: {out_path} (CRS: EPSG:4326)")
            except Exception as e:
                print(f"Error exporting {geojson_name}: {e}")
        else:
            print(f"Warning: Source GPKG {gpkg_path} not found.")
            
    print("GeoJSON verification and export completed.")

if __name__ == "__main__":
    gis_dir = "/home/jupyter/Apple_Change_Detection_POC/output/gis"
    geojson_dir = "/home/jupyter/Apple_Change_Detection_POC/output/geojson"
    verify_and_finalize_geojson_exports(gis_dir, geojson_dir)
