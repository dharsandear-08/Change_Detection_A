import os
import shutil
import geopandas as gpd

def export_shapefiles(gis_dir, shp_dir, packages_dir):
    """
    Exports individual spatial layers to standard ESRI Shapefile formats
    and packs them into a single zip archive.
    Layers:
        - changes (from filtered_changes.gpkg)
        - roads (from roads.gpkg)
        - buildings (from buildings.gpkg)
        - construction (from construction.gpkg)
        - qa_tasks (from qa_tasks.gpkg)
    """
    os.makedirs(shp_dir, exist_ok=True)
    os.makedirs(packages_dir, exist_ok=True)
    
    layers = [
        ("changes", "filtered_changes.gpkg", "filtered_changes"),
        ("roads", "roads.gpkg", "roads"),
        ("buildings", "buildings.gpkg", "buildings"),
        ("construction", "construction.gpkg", "construction"),
        ("qa_tasks", "qa_tasks.gpkg", "qa_tasks")
    ]
    
    for shp_name, gpkg_name, layer_table in layers:
        gpkg_path = os.path.join(gis_dir, gpkg_name)
        layer_shp_dir = os.path.join(shp_dir, shp_name)
        os.makedirs(layer_shp_dir, exist_ok=True)
        
        if os.path.exists(gpkg_path):
            try:
                gdf = gpd.read_file(gpkg_path, layer=layer_table)
                
                # Shapefile column headers are limited to 10 characters.
                # Write the shapefile
                shp_out_path = os.path.join(layer_shp_dir, f"{shp_name}.shp")
                
                # Simple cleanup of previous exports if exists
                if os.path.exists(shp_out_path):
                    shutil.rmtree(layer_shp_dir)
                    os.makedirs(layer_shp_dir, exist_ok=True)
                
                # ESRI Shapefiles do not allow mixed geometry types.
                # For qa_tasks, we convert geometries to their centroids (Points),
                # which acts as the review point pin on the map.
                if shp_name == "qa_tasks":
                    # Convert to centroids (Points) to avoid mixed-geometry write errors
                    gdf["geometry"] = gdf.geometry.centroid
                    
                gdf.to_file(shp_out_path, driver="ESRI Shapefile")
                print(f"Exported Shapefile to: {layer_shp_dir}")
            except Exception as e:
                print(f"Error exporting {shp_name} Shapefile: {e}")
        else:
            print(f"Warning: Source layer {shp_name} ({gpkg_path}) not found.")
            
    # Zip the shapefile folder
    zip_out_base = os.path.join(packages_dir, "Apple_POC_Shapefiles")
    shutil.make_archive(zip_out_base, 'zip', shp_dir)
    print(f"Shapefiles successfully packed into: {zip_out_base}.zip")

if __name__ == "__main__":
    gis_dir = "/home/jupyter/Apple_Change_Detection_POC/output/gis"
    shp_dir = "/home/jupyter/Apple_Change_Detection_POC/output/shapefile"
    packages_dir = "/home/jupyter/Apple_Change_Detection_POC/output/packages"
    
    export_shapefiles(gis_dir, shp_dir, packages_dir)
