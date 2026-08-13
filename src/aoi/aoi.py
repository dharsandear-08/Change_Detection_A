import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask as riomask
from shapely.geometry import MultiPolygon, Polygon

def generate_aois(filt_gpkg_path, current_raster_path, aoi_gpkg_path, clips_dir_path):
    """
    Generates Area of Interest (AOI) polygons from meaningful changes:
    - Selects changes where filter_status is "KEEP".
    - Applies a buffer (e.g. 15.0 meters) to expand the AOI around the change.
    - Dissolves overlapping buffers to merge them.
    - Exports aoi.gpkg and aoi.geojson.
    - Clips current_raster_path to each AOI and saves TIFF files in clips_dir_path.
    """
    os.makedirs(os.path.dirname(aoi_gpkg_path), exist_ok=True)
    os.makedirs(clips_dir_path, exist_ok=True)
    
    gdf_filt = gpd.read_file(filt_gpkg_path, layer="filtered_changes")
    
    # Filter to KEEP features only
    gdf_keep = gdf_filt[gdf_filt["filter_status"] == "KEEP"].copy()
    
    if gdf_keep.empty:
        print("No meaningful changes found for AOI generation.")
        # Save empty files
        gdf_empty = gpd.GeoDataFrame(columns=["geometry", "aoi_id"], crs=gdf_filt.crs)
        gdf_empty.to_file(aoi_gpkg_path, layer="aoi", driver="GPKG")
        return 0
        
    # Apply buffer (15 meters)
    gdf_keep["geometry"] = gdf_keep.geometry.buffer(15.0)
    
    # Dissolve to merge overlapping buffers
    # unary_union returns a single geometry representing the union of all geometries
    union_geom = gdf_keep.geometry.unary_union
    
    # Extract individual polygons from the dissolved geometry
    if isinstance(union_geom, Polygon):
        aoi_geoms = [union_geom]
    elif isinstance(union_geom, MultiPolygon):
        aoi_geoms = list(union_geom.geoms)
    else:
        aoi_geoms = []
        
    # Create AOI GeoDataFrame
    aoi_gdf = gpd.GeoDataFrame(geometry=aoi_geoms, crs=gdf_filt.crs)
    aoi_gdf["aoi_id"] = [f"AOI_{i+1:03d}" for i in range(len(aoi_gdf))]
    
    # Save GeoPackage
    aoi_gdf.to_file(aoi_gpkg_path, layer="aoi", driver="GPKG")
    print(f"AOI GeoPackage saved to {aoi_gpkg_path} (layer 'aoi')")
    
    # Save GeoJSON
    geojson_out = aoi_gpkg_path.replace(".gpkg", ".geojson").replace("/gis/", "/geojson/")
    os.makedirs(os.path.dirname(geojson_out), exist_ok=True)
    aoi_gdf_4326 = aoi_gdf.to_crs(epsg=4326)
    aoi_gdf_4326.to_file(geojson_out, driver="GeoJSON")
    print(f"AOI GeoJSON saved to {geojson_out}")
    
    # Clip the original imagery for each AOI
    with rasterio.open(current_raster_path) as src:
        for idx, row in aoi_gdf.iterrows():
            aoi_id = row["aoi_id"]
            geom = row.geometry
            
            # Clip rasterio
            try:
                clipped_img, clipped_transform = riomask(src, [geom], crop=True)
                
                # Write clipped GeoTIFF
                out_profile = src.profile.copy()
                out_profile.update({
                    'height': clipped_img.shape[1],
                    'width': clipped_img.shape[2],
                    'transform': clipped_transform
                })
                
                clip_path = os.path.join(clips_dir_path, f"{aoi_id}.tif")
                with rasterio.open(clip_path, 'w', **out_profile) as dst:
                    dst.write(clipped_img)
                    
                print(f"Clipped imagery saved to: {clip_path}")
            except Exception as e:
                print(f"Error clipping imagery for {aoi_id}: {e}")
                
    print(f"Total AOIs generated and clipped: {len(aoi_gdf)}")
    return len(aoi_gdf)

if __name__ == "__main__":
    filt_gpkg = "/home/jupyter/Apple_Change_Detection_POC/output/gis/filtered_changes.gpkg"
    current_raster = "/home/jupyter/Apple_Change_Detection_POC/data/examples/2026_OG_Image.tif"
    
    aoi_gpkg = "/home/jupyter/Apple_Change_Detection_POC/output/gis/aoi.gpkg"
    clips_dir = "/home/jupyter/Apple_Change_Detection_POC/output/aoi_clips"
    
    generate_aois(filt_gpkg, current_raster, aoi_gpkg, clips_dir)
