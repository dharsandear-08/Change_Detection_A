import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask as riomask
import numpy as np
import pandas as pd

def analyze_polygon_spectral(geom, raster_path):
    """
    Masks the raster using the geometry and computes spectral statistics:
    - mean brightness (intensity)
    - mean greenness (G / (R+G+B))
    """
    with rasterio.open(raster_path) as src:
        try:
            # Mask the raster with the polygon
            out_image, out_transform = riomask(src, [geom], crop=True)
            # out_image is shape (bands, height, width)
            # Find non-zero pixels (ignoring mask/nodata)
            valid_mask = (out_image[0] > 0) | (out_image[1] > 0) | (out_image[2] > 0)
            if not np.any(valid_mask):
                return {"brightness": 0.0, "greenness": 0.0}
                
            r = out_image[0][valid_mask].astype(np.float32)
            g = out_image[1][valid_mask].astype(np.float32)
            b = out_image[2][valid_mask].astype(np.float32)
            
            brightness = np.mean((r + g + b) / 3.0)
            greenness = np.mean(g / (r + g + b + 1e-5))
            return {"brightness": brightness, "greenness": greenness}
        except Exception as e:
            print(f"Error masking polygon: {e}")
            return {"brightness": 128.0, "greenness": 0.33}

def apply_filters(gpkg_in_path, hist_raster_path, curr_raster_path, gpkg_raw_out, gpkg_filt_out):
    """
    Loads raw change polygons, applies modular deterministic filters,
    and writes raw_changes.gpkg and filtered_changes.gpkg.
    """
    os.makedirs(os.path.dirname(gpkg_raw_out), exist_ok=True)
    os.makedirs(os.path.dirname(gpkg_filt_out), exist_ok=True)
    
    gdf = gpd.read_file(gpkg_in_path, layer="raw_changes")
    
    if gdf.empty:
        print("No input change polygons to filter.")
        # Create empty GPKG
        gdf.to_file(gpkg_raw_out, layer="raw_changes", driver="GPKG")
        gdf.to_file(gpkg_filt_out, layer="filtered_changes", driver="GPKG")
        return
        
    # Prepare raw_changes with default status
    gdf_raw = gdf.copy()
    gdf_raw["filter_status"] = "PENDING"
    gdf_raw["filter_reason"] = "NONE"
    gdf_raw.to_file(gpkg_raw_out, layer="raw_changes", driver="GPKG")
    print(f"Raw changes with status written to {gpkg_raw_out}")
    
    # Process each polygon
    filter_statuses = []
    filter_reasons = []
    
    for idx, row in gdf.iterrows():
        geom = row.geometry
        area = row["area_m2"]
        
        # 1. Filter by Small Area
        if area < 20.0:
            filter_statuses.append("FILTERED")
            filter_reasons.append("FILTERED_SMALL_AREA")
            continue
            
        # Spectral checks
        hist_stats = analyze_polygon_spectral(geom, hist_raster_path)
        curr_stats = analyze_polygon_spectral(geom, curr_raster_path)
        
        # 2. Filter by Vegetation (if greenness is very high in either image, e.g. > 0.37)
        # Greenness of balanced grey/brown is 0.33. Lush vegetation has greenness > 0.37.
        if hist_stats["greenness"] > 0.37 or curr_stats["greenness"] > 0.37:
            filter_statuses.append("FILTERED")
            filter_reasons.append("FILTERED_VEGETATION")
            continue
            
        # 3. Filter by Shadow (if brightness is extremely low, e.g. < 30)
        if curr_stats["brightness"] < 30.0:
            filter_statuses.append("FILTERED")
            filter_reasons.append("FILTERED_SHADOW")
            continue
            
        # If it passes all filters, we KEEP it
        filter_statuses.append("KEEP")
        filter_reasons.append("VALID_CHANGE_CANDIDATE")
        
    gdf_filt = gdf.copy()
    gdf_filt["filter_status"] = filter_statuses
    gdf_filt["filter_reason"] = filter_reasons
    
    # Save all features in filtered_changes.gpkg
    gdf_filt.to_file(gpkg_filt_out, layer="filtered_changes", driver="GPKG")
    print(f"Filtered changes written to {gpkg_filt_out}")
    
    # Print summary
    stats_df = pd.Series(filter_reasons).value_counts()
    print("Filter reasons summary:")
    print(stats_df)
    
    # Let's also save filtered changes as GeoJSON (for web)
    geojson_out = gpkg_filt_out.replace(".gpkg", ".geojson").replace("/gis/", "/geojson/")
    os.makedirs(os.path.dirname(geojson_out), exist_ok=True)
    gdf_filt_4326 = gdf_filt.to_crs(epsg=4326)
    gdf_filt_4326.to_file(geojson_out, driver="GeoJSON")
    print(f"Filtered changes GeoJSON saved to {geojson_out}")

if __name__ == "__main__":
    gpkg_in = "/home/jupyter/Apple_Change_Detection_POC/output/gis/change_polygons.gpkg"
    hist_raster = "/home/jupyter/Apple_Change_Detection_POC/data/working/prepared_historical.tif"
    curr_raster = "/home/jupyter/Apple_Change_Detection_POC/data/working/prepared_current.tif"
    
    gpkg_raw = "/home/jupyter/Apple_Change_Detection_POC/output/gis/raw_changes.gpkg"
    gpkg_filt = "/home/jupyter/Apple_Change_Detection_POC/output/gis/filtered_changes.gpkg"
    
    apply_filters(gpkg_in, hist_raster, curr_raster, gpkg_raw, gpkg_filt)
