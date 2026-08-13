import os
import geopandas as gpd

def compile_master_geopackage(gis_dir, master_gpkg_path):
    """
    Compiles all individual vector layers into a single consolidated, authoritative GeoPackage.
    Required layers:
        - raw_changes
        - filtered_changes
        - aoi
        - buildings
        - roads
        - construction
        - road_nodes
        - topology_issues
        - qa_tasks
        - approved_changes (empty layer with schema of filtered_changes)
    """
    os.makedirs(os.path.dirname(master_gpkg_path), exist_ok=True)
    
    # If file exists, remove it to ensure a clean rewrite
    if os.path.exists(master_gpkg_path):
        os.remove(master_gpkg_path)
        
    layers_to_import = [
        ("raw_changes", "raw_changes.gpkg", "raw_changes"),
        ("filtered_changes", "filtered_changes.gpkg", "filtered_changes"),
        ("aoi", "aoi.gpkg", "aoi"),
        ("buildings", "buildings.gpkg", "buildings"),
        ("roads", "roads.gpkg", "roads"),
        ("construction", "construction.gpkg", "construction"),
        ("road_nodes", "road_nodes.gpkg", "road_nodes"),
        ("topology_issues", "topology_issues.gpkg", "topology_issues"),
        ("qa_tasks", "qa_tasks.gpkg", "qa_tasks")
    ]
    
    for layer_name, gpkg_name, layer_table in layers_to_import:
        gpkg_path = os.path.join(gis_dir, gpkg_name)
        if os.path.exists(gpkg_path):
            try:
                gdf = gpd.read_file(gpkg_path, layer=layer_table)
                gdf.to_file(master_gpkg_path, layer=layer_name, driver="GPKG")
                print(f"Added layer '{layer_name}' to master GeoPackage.")
            except Exception as e:
                print(f"Error importing layer '{layer_name}': {e}")
        else:
            print(f"Warning: Source layer '{layer_name}' ({gpkg_path}) not found.")
            
    # Add approved_changes layer: an empty layer with schema matching filtered_changes
    filt_path = os.path.join(gis_dir, "filtered_changes.gpkg")
    if os.path.exists(filt_path):
        try:
            gdf_filt = gpd.read_file(filt_path, layer="filtered_changes")
            # Create empty copy
            gdf_approved = gdf_filt.iloc[0:0].copy()
            gdf_approved.to_file(master_gpkg_path, layer="approved_changes", driver="GPKG")
            print("Added empty layer 'approved_changes' with matching schema to master GeoPackage.")
        except Exception as e:
            print(f"Error creating approved_changes layer: {e}")
            
    print(f"Master GeoPackage successfully compiled at: {master_gpkg_path}")

if __name__ == "__main__":
    gis_dir = "/home/jupyter/Apple_Change_Detection_POC/output/gis"
    master_gpkg = "/home/jupyter/Apple_Change_Detection_POC/output/gis/Apple_POC_Final.gpkg"
    compile_master_geopackage(gis_dir, master_gpkg)
