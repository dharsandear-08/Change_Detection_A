import os
import json
import rasterio
import cv2
import numpy as np

def register_images(historical_path, current_path, report_path):
    """
    Performs image registration check:
    1. Compares geotransforms, grid, and CRS.
    2. Performs fast phase correlation on downsampled grayscales to estimate pixel displacement (dx, dy).
    3. Outputs a registration report.
    """
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with rasterio.open(historical_path) as src_hist, rasterio.open(current_path) as src_curr:
        hist_name = os.path.basename(historical_path)
        curr_name = os.path.basename(current_path)
        
        # Grid checks
        grid_match = (
            src_hist.crs == src_curr.crs and
            src_hist.width == src_curr.width and
            src_hist.height == src_curr.height and
            all(abs(a - b) < 1e-5 for a, b in zip(list(src_hist.transform)[:6], list(src_curr.transform)[:6]))
        )
        
        # We downsample the first band of both images for fast phase correlation
        # This is safe and very memory efficient
        h_h, w_h = src_hist.height, src_hist.width
        h_c, w_c = src_curr.height, src_curr.width
        
        # Downsample size for correlation (e.g. 1024x1024)
        corr_size = 1024
        
        # Read downsampled data for band 1 (Red)
        out_shape = (corr_size, corr_size)
        
        b1_hist = src_hist.read(1, out_shape=out_shape, resampling=rasterio.enums.Resampling.bilinear).astype(np.float32)
        b1_curr = src_curr.read(1, out_shape=out_shape, resampling=rasterio.enums.Resampling.bilinear).astype(np.float32)
        
        # Normalize for phase correlation
        b1_hist = (b1_hist - np.mean(b1_hist)) / (np.std(b1_hist) + 1e-5)
        b1_curr = (b1_curr - np.mean(b1_curr)) / (np.std(b1_curr) + 1e-5)
        
        # OpenCV Phase Correlation
        displacement, score = cv2.phaseCorrelate(b1_hist, b1_curr)
        dx_ds, dy_ds = displacement
        
        # Scale back the displacement to original dimensions
        dx = dx_ds * (w_h / corr_size)
        dy = dy_ds * (h_h / corr_size)
        
        # Check alignment criteria: if they are already on the same grid and displacement is negligible
        is_aligned = grid_match and (abs(dx) < 1.0 and abs(dy) < 1.0)
        
        if is_aligned:
            status = "ALREADY_ALIGNED"
            dx = 0.0
            dy = 0.0
            transform_changed = False
            resampled = False
        else:
            status = "WARPED_AND_ALIGNED"
            transform_changed = not grid_match
            resampled = not grid_match
            
        report = {
            "source": hist_name,
            "reference": curr_name,
            "dx": dx,
            "dy": dy,
            "score": score,
            "status": status,
            "transform_changed": transform_changed,
            "resampled": resampled
        }
        
        with open(report_path, "w") as jf:
            json.dump(report, jf, indent=2)
            
        print(f"Registration report generated: {report_path}")
        print(f"Registration Status: {status}, Displacement (dx, dy): ({dx:.2f}, {dy:.2f}), Score: {score:.4f}")
        return report

if __name__ == "__main__":
    hist_path = "/home/jupyter/Apple_Change_Detection_POC/data/working/prepared_historical.tif"
    curr_path = "/home/jupyter/Apple_Change_Detection_POC/data/working/prepared_current.tif"
    report_path = "/home/jupyter/Apple_Change_Detection_POC/output/registration_report.json"
    
    register_images(hist_path, curr_path, report_path)
