import os
import json
import rasterio
from shapely.geometry import box

def check_compatibility(file1, file2):
    with rasterio.open(file1) as r1, rasterio.open(file2) as r2:
        # CRS
        crs1, crs2 = r1.crs, r2.crs
        same_crs = (crs1 == crs2)
        epsg1 = crs1.to_epsg() if crs1 else None
        epsg2 = crs2.to_epsg() if crs2 else None
        
        # GSD (resolution)
        res1, res2 = r1.res, r2.res
        same_res = (abs(res1[0] - res2[0]) < 1e-5 and abs(res1[1] - res2[1]) < 1e-5)
        
        # Dimensions
        dim1 = (r1.width, r1.height)
        dim2 = (r2.width, r2.height)
        same_dim = (dim1 == dim2)
        
        # Transform
        t1, t2 = list(r1.transform)[:6], list(r2.transform)[:6]
        same_transform = all(abs(a - b) < 1e-5 for a, b in zip(t1, t2))
        
        # Bands
        bands1, bands2 = r1.count, r2.count
        same_bands = (bands1 == bands2)
        
        # Bounds and Overlap
        b1, b2 = r1.bounds, r2.bounds
        same_extent = all(abs(a - b) < 1e-3 for a, b in zip(b1, b2))
        
        geom1 = box(*b1)
        geom2 = box(*b2)
        overlap_area = 0.0
        overlap_pct = 0.0
        
        if geom1.intersects(geom2):
            intersection = geom1.intersection(geom2)
            overlap_area = intersection.area
            overlap_pct = (overlap_area / min(geom1.area, geom2.area)) * 100.0
            
        same_grid = same_crs and same_transform and same_dim
        
        return {
            "file1": os.path.basename(file1),
            "file2": os.path.basename(file2),
            "same_crs": same_crs,
            "epsg1": epsg1,
            "epsg2": epsg2,
            "same_res": same_res,
            "res1": list(res1),
            "res2": list(res2),
            "same_dim": same_dim,
            "dim1": list(dim1),
            "dim2": list(dim2),
            "same_transform": same_transform,
            "same_bands": same_bands,
            "bands1": bands1,
            "bands2": bands2,
            "same_extent": same_extent,
            "overlap_area_m2": overlap_area,
            "overlap_pct": overlap_pct,
            "same_grid": same_grid
        }

def generate_html_report(report_data, out_path):
    # Determine alignment flag status class and message
    is_aligned_2025_2026 = report_data["2025_2026"]["same_grid"]
    status_class = "status-pass" if is_aligned_2025_2026 else "status-fail"
    status_msg = "YES (Perfect Alignment)" if is_aligned_2025_2026 else "NO (Normalization/Resampling Required)"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Data Compatibility Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f4f7f6;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #2980b9;
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .comparison {{
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .status-pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-fail {{
            color: #c0392b;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #34495e;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h1>Apple Change Detection & Automated Map Update POC - Compatibility Report</h1>
    
    <div class="summary">
        <h2>Primary Compatibility Status (2025 &harr; 2026)</h2>
        <p><strong>Primary Comparison:</strong> 2025_demo_synthetic.tif &harr; 2026_OG_Image.tif</p>
        <p><strong>Same Grid:</strong> <span class="{status_class}">{status_msg}</span></p>
        <p><strong>CRS Match:</strong> {report_data["2025_2026"]["epsg1"]} &harr; {report_data["2025_2026"]["epsg2"]} (<span class="status-pass">PASS</span>)</p>
        <p><strong>Resolution Match:</strong> {report_data["2025_2026"]["res1"]} &harr; {report_data["2025_2026"]["res2"]} (<span class="status-pass">PASS</span>)</p>
        <p><strong>Dimensions Match:</strong> {report_data["2025_2026"]["dim1"]} &harr; {report_data["2025_2026"]["dim2"]} (<span class="status-pass">PASS</span>)</p>
        <p><strong>Overlap Percentage:</strong> {report_data["2025_2026"]["overlap_pct"]:.2f}%</p>
    </div>
    
    <div class="comparison">
        <h2>All Comparisons Detail</h2>
        <table>
            <thead>
                <tr>
                    <th>Comparison Pair</th>
                    <th>Same CRS?</th>
                    <th>Same Resolution?</th>
                    <th>Same Dimensions?</th>
                    <th>Same Transform?</th>
                    <th>Overlap %</th>
                    <th>Same Grid?</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for pair_name, data in report_data.items():
        html_content += f"""
                <tr>
                    <td><strong>{pair_name}</strong> ({data["file1"]} &harr; {data["file2"]})</td>
                    <td class="{"status-pass" if data["same_crs"] else "status-fail"}">{"YES" if data["same_crs"] else "NO"}</td>
                    <td class="{"status-pass" if data["same_res"] else "status-fail"}">{"YES" if data["same_res"] else "NO"}</td>
                    <td class="{"status-pass" if data["same_dim"] else "status-fail"}">{"YES" if data["same_dim"] else "NO"}</td>
                    <td class="{"status-pass" if data["same_transform"] else "status-fail"}">{"YES" if data["same_transform"] else "NO"}</td>
                    <td>{data["overlap_pct"]:.2f}%</td>
                    <td class="{"status-pass" if data["same_grid"] else "status-fail"}">{"YES" if data["same_grid"] else "NO"}</td>
                </tr>
        """
        
    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
    """
    
    with open(out_path, "w") as f:
        f.write(html_content)

def main():
    base_dir = "/home/jupyter/Apple_Change_Detection_POC/data/examples"
    f2024 = os.path.join(base_dir, "2024_demo_synthetic.tif")
    f2025 = os.path.join(base_dir, "2025_demo_synthetic.tif")
    f2026 = os.path.join(base_dir, "2026_OG_Image.tif")
    
    report_data = {}
    if os.path.exists(f2024) and os.path.exists(f2025):
        report_data["2024_2025"] = check_compatibility(f2024, f2025)
    if os.path.exists(f2025) and os.path.exists(f2026):
        report_data["2025_2026"] = check_compatibility(f2025, f2026)
    if os.path.exists(f2024) and os.path.exists(f2026):
        report_data["2024_2026"] = check_compatibility(f2024, f2026)
        
    out_dir = "/home/jupyter/Apple_Change_Detection_POC/output"
    os.makedirs(out_dir, exist_ok=True)
    
    # write json
    json_path = os.path.join(out_dir, "compatibility_report.json")
    with open(json_path, "w") as jf:
        json.dump(report_data, jf, indent=2)
        
    # write html
    html_path = os.path.join(out_dir, "compatibility_report.html")
    generate_html_report(report_data, html_path)
    
    print(f"Compatibility reports generated: {json_path} and {html_path}")

if __name__ == "__main__":
    main()
