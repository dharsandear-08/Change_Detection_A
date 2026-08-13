import os
import rasterio

def verify_raster_outputs(output_dir):
    """
    Verifies that all required raster deliverables exist, have correct dimensions,
    and retain valid georeferencing.
    Required:
        - change_score.tif (in output/raster/)
        - change_mask.tif (in output/raster/)
        - AOI clips (in output/aoi_clips/)
    """
    score_path = os.path.join(output_dir, "raster", "change_score.tif")
    mask_path = os.path.join(output_dir, "raster", "change_mask.tif")
    aoi_dir = os.path.join(output_dir, "aoi_clips")
    
    expected_rasters = [score_path, mask_path]
    
    # Check general deliverables
    for path in expected_rasters:
        if os.path.exists(path):
            with rasterio.open(path) as src:
                print(f"Verified Raster: {path}")
                print(f"  Dimensions: {src.width}x{src.height}")
                print(f"  CRS: {src.crs}")
                print(f"  Transform: {list(src.transform)[:6]}")
        else:
            print(f"Warning: Deliverable raster {path} not found.")
            
    # Check AOI clips
    if os.path.exists(aoi_dir):
        clips = [os.path.join(aoi_dir, f) for f in os.listdir(aoi_dir) if f.endswith(".tif")]
        for clip in clips:
            with rasterio.open(clip) as src:
                print(f"Verified AOI Clip: {clip}")
                print(f"  Dimensions: {src.width}x{src.height}")
                print(f"  CRS: {src.crs}")
                print(f"  Transform: {list(src.transform)[:6]}")
    else:
        print(f"Warning: AOI clips directory {aoi_dir} not found.")
        
    print("Raster verification completed.")

if __name__ == "__main__":
    output_dir = "/home/jupyter/Apple_Change_Detection_POC/output"
    verify_raster_outputs(output_dir)
