import os
import json
import rasterio

def inspect_tiff(file_path):
    with rasterio.open(file_path) as src:
        crs = src.crs
        epsg = crs.to_epsg() if crs else None
        
        info = {
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "format": src.driver,
            "crs": str(crs) if crs else None,
            "epsg": epsg,
            "resolution": list(src.res),
            "dimensions": [src.width, src.height],
            "bounds": list(src.bounds),
            "bands": src.count,
            "dtype": src.dtypes[0] if src.dtypes else None,
            "nodata": src.nodata,
            "transform": list(src.transform)[:6] # first 6 parameters of affine transform
        }
        return info

def main():
    base_dir = "/home/jupyter/Apple_Change_Detection_POC/data/examples"
    files = [
        os.path.join(base_dir, "2024_demo_synthetic.tif"),
        os.path.join(base_dir, "2025_demo_synthetic.tif"),
        os.path.join(base_dir, "2026_OG_Image.tif")
    ]
    
    inventory = {}
    text_report = []
    
    for f in files:
        if os.path.exists(f):
            info = inspect_tiff(f)
            inventory[info["filename"]] = info
            
            # format a nice text block
            text_report.append(f"Filename: {info['filename']}")
            text_report.append(f"Size: {info['size']} bytes")
            text_report.append(f"Format: {info['format']}")
            text_report.append(f"CRS: {info['crs']}")
            text_report.append(f"EPSG: {info['epsg']}")
            text_report.append(f"Resolution: {info['resolution']}")
            text_report.append(f"Dimensions: {info['dimensions'][0]}x{info['dimensions'][1]}")
            text_report.append(f"Bounds: {info['bounds']}")
            text_report.append(f"Bands: {info['bands']}")
            text_report.append(f"DataType: {info['dtype']}")
            text_report.append(f"NoData: {info['nodata']}")
            text_report.append(f"Transform: {info['transform']}")
            text_report.append("-" * 40)
        else:
            text_report.append(f"File not found: {f}")
            text_report.append("-" * 40)
            
    out_dir = "/home/jupyter/Apple_Change_Detection_POC/output"
    os.makedirs(out_dir, exist_ok=True)
    
    # write json
    json_path = os.path.join(out_dir, "input_inventory.json")
    with open(json_path, "w") as jf:
        json.dump(inventory, jf, indent=2)
        
    # write txt
    txt_path = os.path.join(out_dir, "input_inventory.txt")
    with open(txt_path, "w") as tf:
        tf.write("\n".join(text_report))
        
    print(f"Inventory written to {json_path} and {txt_path}")

if __name__ == "__main__":
    main()
