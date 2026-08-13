import os
import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np

def preprocess_image(input_path, output_path, target_grid_src=None):
    """
    Preprocesses a single imagery file:
    - If target_grid_src is provided, aligns (reprojects/resamples) this image to match the target's CRS, extent, resolution, and dimensions.
    - Extracts RGB bands.
    - Uses Alpha channel (band 4) as NoData mask if present.
    - Writes a 3-band RGB GeoTIFF with proper masking.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with rasterio.open(input_path) as src:
        # If target grid is provided, we need to match it
        if target_grid_src is not None:
            # We will read target's properties
            target_crs = target_grid_src.crs
            target_transform = target_grid_src.transform
            target_width = target_grid_src.width
            target_height = target_grid_src.height
            
            # Create profile for intermediate aligned image
            temp_profile = src.profile.copy()
            temp_profile.update({
                'crs': target_crs,
                'transform': target_transform,
                'width': target_width,
                'height': target_height,
                'count': src.count  # keep all bands for now, will extract RGB next
            })
            
            # Read and reproject
            aligned_data = np.zeros((src.count, target_height, target_width), dtype=src.dtypes[0])
            for b in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, b),
                    destination=aligned_data[b-1],
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=target_transform,
                    dst_crs=target_crs,
                    resampling=Resampling.bilinear
                )
            
            # Now extract RGB and Alpha from aligned_data
            rgb_data = aligned_data[0:3]
            alpha_data = aligned_data[3] if src.count >= 4 else None
        else:
            # No target grid, just read raw RGB/Alpha
            rgb_data = src.read((1, 2, 3))
            alpha_data = src.read(4) if src.count >= 4 else None
            target_crs = src.crs
            target_transform = src.transform
            target_width = src.width
            target_height = src.height
            temp_profile = src.profile.copy()

        # Handle masking: if Alpha channel exists, set RGB pixels where Alpha == 0 to 0 (NoData)
        if alpha_data is not None:
            mask = (alpha_data == 0)
            for b in range(3):
                rgb_data[b][mask] = 0
                
        # Write output as 3-band RGB image
        out_profile = temp_profile.copy()
        out_profile.update({
            'count': 3,
            'driver': 'GTiff',
            'crs': target_crs,
            'transform': target_transform,
            'width': target_width,
            'height': target_height,
            'nodata': 0,
            'dtype': 'uint8'
        })
        
        with rasterio.open(output_path, 'w', **out_profile) as dst:
            dst.write(rgb_data)
            
    print(f"Preprocessed and saved: {output_path}")

def run_preprocessing_pipeline(historical_path, current_path, output_hist_path, output_curr_path):
    """
    Runs the full preprocessing pipeline:
    - Preprocesses current image first (serves as the master grid).
    - Preprocesses historical image and aligns it to the current image's grid.
    """
    # 1. Preprocess current image (defines the target grid)
    preprocess_image(current_path, output_curr_path, target_grid_src=None)
    
    # 2. Preprocess historical image, aligning it to the current image's grid
    with rasterio.open(output_curr_path) as curr_src:
        preprocess_image(historical_path, output_hist_path, target_grid_src=curr_src)
        
    print("Preprocessing pipeline completed successfully.")

if __name__ == "__main__":
    base_dir = "/home/jupyter/Apple_Change_Detection_POC/data/examples"
    hist_in = os.path.join(base_dir, "2025_demo_synthetic.tif")
    curr_in = os.path.join(base_dir, "2026_OG_Image.tif")
    
    working_dir = "/home/jupyter/Apple_Change_Detection_POC/data/working"
    hist_out = os.path.join(working_dir, "prepared_historical.tif")
    curr_out = os.path.join(working_dir, "prepared_current.tif")
    
    run_preprocessing_pipeline(hist_in, curr_in, hist_out, curr_out)
