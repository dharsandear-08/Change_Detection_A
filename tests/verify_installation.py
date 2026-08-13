import importlib
import pkg_resources

def verify_clean_install():
    """
    Parses requirements.txt and verifies that all required packages
    are installed and importable in the current environment.
    """
    req_file = "/home/jupyter/Apple_Change_Detection_POC/requirements.txt"
    print("============================================================")
    print("RUNNING AUTOMATED CLEAN INSTALL VERIFICATION CHECK")
    print("============================================================")
    
    # Simple mapping of pip package names to python import names
    package_to_import_map = {
        "opencv-python-headless": "cv2",
        "scikit-image": "skimage",
        "rasterio": "rasterio",
        "geopandas": "geopandas",
        "shapely": "shapely",
        "pyproj": "pyproj",
        "networkx": "networkx",
        "numpy": "numpy",
        "pandas": "pandas",
        "streamlit": "streamlit",
        "folium": "folium",
        "matplotlib": "matplotlib",
        "pytest": "pytest"
    }
    
    all_passed = True
    missing_packages = []
    
    with open(req_file, "r") as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        # Skip comments or empty lines
        if not line or line.startswith("#"):
            continue
            
        # Extract package name (remove version specifiers like >=, ==)
        parts = line.split(">")
        pkg_name = parts[0].split("=")[0].split("<")[0].strip()
        
        # Get import name
        import_name = package_to_import_map.get(pkg_name.lower(), pkg_name)
        
        try:
            mod = importlib.import_module(import_name)
            # Try to get version
            try:
                version = mod.__version__
            except AttributeError:
                try:
                    version = pkg_resources.get_distribution(pkg_name).version
                except Exception:
                    version = "UNKNOWN"
            print(f"✅ [IMPORTABLE] {pkg_name} ({import_name}) - Installed Version: {version}")
        except ImportError as e:
            print(f"❌ [MISSING] {pkg_name} ({import_name}) - Error: {e}")
            all_passed = False
            missing_packages.append(pkg_name)
            
    print("============================================================")
    if all_passed:
        print("[CLEAN INSTALL CHECK] PASS: All required packages are present and importable.")
        print("============================================================")
        return True
    else:
        print(f"[CLEAN INSTALL CHECK] FAIL: Missing packages: {missing_packages}")
        print("============================================================")
        return False

if __name__ == "__main__":
    import sys
    success = verify_clean_install()
    if not success:
        sys.exit(1)
