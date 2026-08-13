import os
import rasterio
import cv2
import numpy as np

def detect_changes(
    historical_path,
    current_path,
    out_score_path,
    out_mask_path,
    threshold=30,
    minimum_area_m2=15.0,
    gaussian_kernel=5,
    opening_kernel=3,
    closing_kernel=9
):
    """
    Performs baseline change detection on two preprocessed, co-registered images.
    - Computes absolute difference in grayscale.
    - Applies Gaussian smoothing.
    - Thresholds to create a binary mask.
    - Applies morphological opening and closing.
    - Filters components based on minimum area (in square meters).
    - Writes change_score.tif and change_mask.tif.
    """
    os.makedirs(os.path.dirname(out_score_path), exist_ok=True)
    os.makedirs(os.path.dirname(out_mask_path), exist_ok=True)
    
    with rasterio.open(historical_path) as src_hist, rasterio.open(current_path) as src_curr:
        # Verify matching dimensions
        if src_hist.shape != src_curr.shape:
            raise ValueError(f"Image shapes do not match: {src_hist.shape} vs {src_curr.shape}")
            
        # Read RGB data
        hist_rgb = src_hist.read()
        curr_rgb = src_curr.read()
        
        # Transpose to HWC for OpenCV
        hist_hwc = np.transpose(hist_rgb, (1, 2, 0))
        curr_hwc = np.transpose(curr_rgb, (1, 2, 0))
        
        # Convert to grayscale
        gray_hist = cv2.cvtColor(hist_hwc, cv2.COLOR_RGB2GRAY)
        gray_curr = cv2.cvtColor(curr_hwc, cv2.COLOR_RGB2GRAY)
        
        # Calculate raw change score (absolute difference)
        change_score = cv2.absdiff(gray_curr, gray_hist)
        
        # Save change score
        profile = src_curr.profile.copy()
        profile.update({
            'count': 1,
            'dtype': 'uint8',
            'nodata': 0
        })
        
        with rasterio.open(out_score_path, 'w', **profile) as dst_score:
            dst_score.write(change_score, 1)
            
        # Apply Gaussian smoothing (must be odd kernel size)
        if gaussian_kernel % 2 == 0:
            gaussian_kernel += 1
        blurred = cv2.GaussianBlur(change_score, (gaussian_kernel, gaussian_kernel), 0)
        
        # Apply thresholding
        _, thresh = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations
        if opening_kernel > 0:
            k_open = cv2.getStructuringElement(cv2.MORPH_RECT, (opening_kernel, opening_kernel))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, k_open)
            
        if closing_kernel > 0:
            k_close = cv2.getStructuringElement(cv2.MORPH_RECT, (closing_kernel, closing_kernel))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, k_close)
            
        # Calculate pixel size in square meters
        res = src_curr.res
        pixel_area_m2 = res[0] * res[1]
        minimum_area_pixels = int(np.round(minimum_area_m2 / pixel_area_m2))
        
        # Connected Components filtering
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
        
        change_mask = np.zeros_like(thresh)
        for label in range(1, num_labels):
            area_px = stats[label, cv2.CC_STAT_AREA]
            if area_px >= minimum_area_pixels:
                change_mask[labels == label] = 255
                
        # Save change mask
        with rasterio.open(out_mask_path, 'w', **profile) as dst_mask:
            dst_mask.write(change_mask, 1)
            
        print(f"Change detection completed.")
        print(f"Change Score saved to: {out_score_path}")
        print(f"Change Mask saved to: {out_mask_path}")
        print(f"Filtered out components smaller than {minimum_area_m2} m2 ({minimum_area_pixels} pixels).")
        
        # Calculate percentage of area changed
        total_pixels = change_mask.size
        changed_pixels = np.sum(change_mask == 255)
        pct_changed = (changed_pixels / total_pixels) * 100.0
        print(f"Area changed: {changed_pixels * pixel_area_m2:.2f} m2 ({pct_changed:.3f}%)")
        
        return changed_pixels

if __name__ == "__main__":
    hist_path = "/home/jupyter/Apple_Change_Detection_POC/data/working/prepared_historical.tif"
    curr_path = "/home/jupyter/Apple_Change_Detection_POC/data/working/prepared_current.tif"
    
    out_dir = "/home/jupyter/Apple_Change_Detection_POC/output/raster"
    score_out = os.path.join(out_dir, "change_score.tif")
    mask_out = os.path.join(out_dir, "change_mask.tif")
    
    detect_changes(hist_path, curr_path, score_out, mask_out)
