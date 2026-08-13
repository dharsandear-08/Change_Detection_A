import os
import rasterio
import rasterio.features
import geopandas as gpd
from shapely.geometry import shape

def polygonize_mask(mask_path, gpkg_out_path, geojson_out_path, run_id="RUN_DEMO_PRIMARY"):
    """
    Polygonizes a binary change mask GeoTIFF:
    - Extracts polygons where mask value is 255.
    - Creates a GeoPandas GeoDataFrame in EPSG:3857.
    - Adds required attributes: change_id, area_m2, confidence, source, change_type, run_id.
    - Saves as GeoPackage (EPSG:3857).
    - Reprojects to EPSG:4326 and saves as GeoJSON.
    """
    os.makedirs(os.path.dirname(gpkg_out_path), exist_ok=True)
    os.makedirs(os.path.dirname(geojson_out_path), exist_ok=True)
    
    with rasterio.open(mask_path) as src:
        mask = src.read(1)
        transform = src.transform
        crs = src.crs
        
        # Extract shapes from mask (only where value is 255)
        shapes = rasterio.features.shapes(mask, mask=(mask == 255), transform=transform)
        
        polygons = []
        for geom, val in shapes:
            polygons.append(shape(geom))
            
    if not polygons:
        print("No change polygons detected.")
        # Create empty GeoDataFrame
        gdf = gpd.GeoDataFrame(columns=[
            "geometry", "change_id", "area_m2", "confidence", "source", "change_type", "run_id"
        ], crs=crs)
    else:
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=crs)
        
        # Add attributes
        gdf["change_id"] = [f"CHG_{i+1:03d}" for i in range(len(gdf))]
        gdf["area_m2"] = gdf.geometry.area
        gdf["confidence"] = 0.85  # default confidence for baseline detector
        gdf["source"] = "2025_2026_diff"
        gdf["change_type"] = "candidate_change"
        gdf["run_id"] = run_id
        
    # Save as GeoPackage
    # Authoritative GeoPackage is saved in EPSG:3857
    gdf.to_file(gpkg_out_path, layer="raw_changes", driver="GPKG")
    print(f"Authoritative GeoPackage saved to {gpkg_out_path} (layer 'raw_changes')")
    
    # Save as GeoJSON (reprojected to EPSG:4326 for web)
    if not gdf.empty:
        gdf_4326 = gdf.to_crs(epsg=4326)
    else:
        gdf_4326 = gdf.copy()
        gdf_4326.crs = "EPSG:4326"
        
    gdf_4326.to_file(geojson_out_path, driver="GeoJSON")
    print(f"GeoJSON saved to {geojson_out_path} (EPSG:4326)")
    
    print(f"Total polygonized changes: {len(gdf)}")
    return len(gdf)

if __name__ == "__main__":
    mask_path = "/home/jupyter/Apple_Change_Detection_POC/output/raster/change_mask.tif"
    gpkg_out = "/home/jupyter/Apple_Change_Detection_POC/output/gis/change_polygons.gpkg"
    geojson_out = "/home/jupyter/Apple_Change_Detection_POC/output/geojson/changes.geojson"
    
    polygonize_mask(mask_path, gpkg_out, geojson_out)
