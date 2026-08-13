import os
import json
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point
import numpy as np

def analyze_road_topology(roads_gpkg_path, nodes_gpkg_out, issues_gpkg_out, report_json_out, snap_dist=5.0):
    """
    Performs road network topology validation and analysis:
    - Extracts road segment endpoints.
    - Connects vertices within snap_dist meters.
    - Builds a NetworkX graph.
    - Validates geometries and flags duplicate segments, isolated segments, dangling endpoints.
    - Generates road_nodes.gpkg, topology_issues.gpkg, and topology_report.json.
    """
    os.makedirs(os.path.dirname(nodes_gpkg_out), exist_ok=True)
    os.makedirs(os.path.dirname(issues_gpkg_out), exist_ok=True)
    os.makedirs(os.path.dirname(report_json_out), exist_ok=True)
    
    roads_gdf = gpd.read_file(roads_gpkg_path, layer="roads")
    crs = roads_gdf.crs
    
    # 1. Geometry Validation & Duplicates
    invalid_geoms = []
    duplicate_segments = []
    
    seen_geom_coords = set()
    for idx, row in roads_gdf.iterrows():
        geom = row.geometry
        if not geom.is_valid:
            invalid_geoms.append(idx)
            continue
            
        # Check duplicates by comparing simplified coords
        coords = tuple(np.round(np.array(geom.coords), 3).flatten())
        rev_coords = tuple(np.round(np.array(geom.coords[::-1]), 3).flatten())
        if coords in seen_geom_coords or rev_coords in seen_geom_coords:
            duplicate_segments.append(idx)
        else:
            seen_geom_coords.add(coords)
            
    # 2. Extract Nodes and Build Graph
    def get_snapped_coord(coord):
        return (round(coord[0] / snap_dist) * snap_dist, round(coord[1] / snap_dist) * snap_dist)
        
    G = nx.Graph()
    edges_info = []
    
    for idx, row in roads_gdf.iterrows():
        if idx in invalid_geoms or idx in duplicate_segments:
            continue
        geom = row.geometry
        coords = list(geom.coords)
        
        start_raw = coords[0]
        end_raw = coords[-1]
        
        start_snap = get_snapped_coord(start_raw)
        end_snap = get_snapped_coord(end_raw)
        
        G.add_edge(start_snap, end_snap, weight=geom.length, road_id=row.get("feature_id", f"ROD_{idx}"))
        edges_info.append((start_snap, end_snap, row))
        
    # 3. Analyze Graph properties
    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()
    
    # Connected Components
    components = list(nx.connected_components(G))
    num_components = len(components)
    
    # Nodes features
    nodes_records = []
    issues_records = []
    
    node_id_counter = 1
    issue_id_counter = 1
    
    for node_coord, degree in G.degree():
        pt = Point(node_coord)
        node_type = "junction" if degree >= 3 else ("dead_end" if degree == 1 else "segment_connection")
        
        nodes_records.append({
            "geometry": pt,
            "node_id": f"NOD_{node_id_counter:03d}",
            "node_type": node_type,
            "degree": degree
        })
        node_id_counter += 1
        
        # Dangling Endpoints are degree 1
        if degree == 1:
            issues_records.append({
                "geometry": pt,
                "issue_id": f"ISS_{issue_id_counter:03d}",
                "issue_type": "dangling_endpoint",
                "severity": "MEDIUM",
                "description": f"Dangling road endpoint at snapped coordinates {node_coord}"
            })
            issue_id_counter += 1
            
    # Isolated segments are components smaller than the main component
    if num_components > 1:
        sizes = [len(c) for c in components]
        max_size_idx = np.argmax(sizes)
        
        for comp_idx, c in enumerate(components):
            if comp_idx == max_size_idx:
                continue
            for u, v, data in G.edges(c, data=True):
                for start_s, end_s, row in edges_info:
                    if (start_s == u and end_s == v) or (start_s == v and end_s == u):
                        issues_records.append({
                            "geometry": row.geometry,
                            "issue_id": f"ISS_{issue_id_counter:03d}",
                            "issue_type": "isolated_segment",
                            "severity": "HIGH",
                            "description": f"Isolated road segment {row.get('feature_id')}"
                        })
                        issue_id_counter += 1
                        break

    # Add duplicate segments as issues
    for idx in duplicate_segments:
        row = roads_gdf.iloc[idx]
        issues_records.append({
            "geometry": row.geometry,
            "issue_id": f"ISS_{issue_id_counter:03d}",
            "issue_type": "duplicate_segment",
            "severity": "LOW",
            "description": f"Duplicate road segment {row.get('feature_id')}"
        })
        issue_id_counter += 1
        
    # Add invalid geoms as issues
    for idx in invalid_geoms:
        row = roads_gdf.iloc[idx]
        issues_records.append({
            "geometry": row.geometry,
            "issue_id": f"ISS_{issue_id_counter:03d}",
            "issue_type": "invalid_geometry",
            "severity": "HIGH",
            "description": f"Invalid road geometry {row.get('feature_id')}"
        })
        issue_id_counter += 1

    # Save Nodes GPKG and GeoJSON
    if nodes_records:
        nodes_gdf = gpd.GeoDataFrame(nodes_records, crs=crs)
    else:
        nodes_gdf = gpd.GeoDataFrame(columns=["geometry", "node_id", "node_type", "degree"], crs=crs)
    nodes_gdf.to_file(nodes_gpkg_out, layer="road_nodes", driver="GPKG")
    print(f"Road nodes saved to: {nodes_gpkg_out}")
    
    # Save Issues GPKG and GeoJSON
    if issues_records:
        issues_gdf = gpd.GeoDataFrame(issues_records, crs=crs)
    else:
        issues_gdf = gpd.GeoDataFrame(columns=["geometry", "issue_id", "issue_type", "severity", "description"], crs=crs)
    issues_gdf.to_file(issues_gpkg_out, layer="topology_issues", driver="GPKG")
    print(f"Topology issues saved to: {issues_gpkg_out}")
    
    # Save WGS84 GeoJSONs
    nodes_geojson_path = nodes_gpkg_out.replace(".gpkg", ".geojson").replace("/gis/", "/geojson/")
    issues_geojson_path = issues_gpkg_out.replace(".gpkg", ".geojson").replace("/gis/", "/geojson/")
    
    if not nodes_gdf.empty:
        nodes_gdf_4326 = nodes_gdf.to_crs(epsg=4326)
    else:
        nodes_gdf_4326 = nodes_gdf.copy()
        nodes_gdf_4326.crs = "EPSG:4326"
    nodes_gdf_4326.to_file(nodes_geojson_path, driver="GeoJSON")
    
    if not issues_gdf.empty:
        issues_gdf_4326 = issues_gdf.to_crs(epsg=4326)
    else:
        issues_gdf_4326 = issues_gdf.copy()
        issues_gdf_4326.crs = "EPSG:4326"
    issues_gdf_4326.to_file(issues_geojson_path, driver="GeoJSON")
    
    # 4. Write Topology JSON Report
    report = {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "disconnected_components": num_components,
        "dangling_endpoints": sum(1 for nod in nodes_records if nod["node_type"] == "dead_end"),
        "invalid_geometries": len(invalid_geoms),
        "duplicate_segments": len(duplicate_segments)
    }
    
    with open(report_json_out, "w") as jf:
        json.dump(report, jf, indent=2)
        
    print(f"Topology report generated: {report_json_out}")
    return report

if __name__ == "__main__":
    roads_gpkg = "/home/jupyter/Apple_Change_Detection_POC/output/gis/roads.gpkg"
    nodes_out = "/home/jupyter/Apple_Change_Detection_POC/output/gis/road_nodes.gpkg"
    issues_out = "/home/jupyter/Apple_Change_Detection_POC/output/gis/topology_issues.gpkg"
    report_out = "/home/jupyter/Apple_Change_Detection_POC/output/reports/topology_report.json"
    
    analyze_road_topology(roads_gpkg, nodes_out, issues_out, report_out)
