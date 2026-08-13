import os
import folium
import geopandas as gpd

def create_map_preview(geojson_dir, out_html_path):
    """
    Creates an interactive HTML Map Preview using Folium (Leaflet):
    - Centers map around scene coordinates.
    - Loads WGS84 GeoJSON files.
    - Adds styled layers for changes, roads, buildings, construction, AOIs, and QA tasks.
    - Adds interactive popup cards.
    - Adds Folium LayerControl for active layer selection.
    """
    os.makedirs(os.path.dirname(out_html_path), exist_ok=True)
    
    # Initialize Folium Map centered on the scene
    # Center approx: (26.541, -81.773)
    m = folium.Map(location=[26.541, -81.773], zoom_start=17, control_scale=True)
    
    # Layer stylings
    styles = {
        "aoi": {"fillColor": "#3498db", "color": "#2980b9", "weight": 2, "fillOpacity": 0.15},
        "changes": {"fillColor": "#e74c3c", "color": "#c0392b", "weight": 2, "fillOpacity": 0.3},
        "buildings": {"fillColor": "#2ecc71", "color": "#27ae60", "weight": 1.5, "fillOpacity": 0.5},
        "roads": {"color": "#f1c40f", "weight": 4, "opacity": 0.8},
        "construction": {"fillColor": "#e67e22", "color": "#d35400", "weight": 2, "fillOpacity": 0.4}
    }
    
    def style_fn(feature_name):
        return lambda x: styles.get(feature_name, {})
        
    def add_geojson_layer(filename, layer_name, style_name, popup_fields):
        file_path = os.path.join(geojson_dir, filename)
        if os.path.exists(file_path):
            try:
                gdf = gpd.read_file(file_path)
                if gdf.empty:
                    print(f"Layer '{layer_name}' is empty. Skipping layer.")
                    return
                    
                tooltip = folium.GeoJsonTooltip(
                    fields=[f for f in popup_fields if f in gdf.columns],
                    aliases=[f.replace("_", " ").upper() + ":" for f in popup_fields if f in gdf.columns],
                    localize=True
                )
                
                geojson_layer = folium.GeoJson(
                    gdf,
                    name=layer_name,
                    style_function=style_fn(style_name),
                    tooltip=tooltip,
                    popup=folium.GeoJsonPopup(fields=[f for f in popup_fields if f in gdf.columns])
                )
                geojson_layer.add_to(m)
                print(f"Added layer '{layer_name}' to the map.")
            except Exception as e:
                print(f"Error adding layer '{layer_name}': {e}")
                
    # Add regular vector layers
    add_geojson_layer("aoi.geojson", "Area of Interest (AOI)", "aoi", ["aoi_id"])
    add_geojson_layer("changes.geojson", "Detected Changes (KEEP)", "changes", ["change_id", "area_m2", "confidence", "source", "change_type"])
    add_geojson_layer("buildings.geojson", "New Buildings", "buildings", ["feature_id", "change_id", "area_m2", "confidence", "processing_method", "model_name", "model_version"])
    add_geojson_layer("roads.geojson", "New Roads", "roads", ["feature_id", "change_id", "length_m", "confidence", "processing_method"])
    add_geojson_layer("construction.geojson", "Construction Areas", "construction", ["feature_id", "change_id", "status", "type"])
    
    # QA tasks are special: we add them as custom-colored markers
    qa_path = os.path.join(geojson_dir, "qa_tasks.geojson")
    if os.path.exists(qa_path):
        try:
            gdf_qa = gpd.read_file(qa_path)
            qa_group = folium.FeatureGroup(name="QA Tasks (Pins)")
            
            for idx, row in gdf_qa.iterrows():
                geom = row.geometry
                centroid = geom.centroid if geom else None
                if centroid:
                    lat, lon = centroid.y, centroid.x
                    
                    # Styled popup HTML
                    popup_html = f"""
                    <div style="font-family: Arial, sans-serif; font-size: 12px; width: 220px;">
                        <h4 style="margin: 0 0 5px 0; color: #2c3e50;">QA Task: {row.get('task_id')}</h4>
                        <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ccc;" />
                        <b>Feature ID:</b> {row.get('feature_id')}<br/>
                        <b>Type:</b> {row.get('feature_type')}<br/>
                        <b>Confidence:</b> {row.get('confidence')}<br/>
                        <b>Priority:</b> <span style="color: {'red' if row.get('priority') == 'HIGH' else ('orange' if row.get('priority') == 'MEDIUM' else 'green')}; font-weight: bold;">{row.get('priority')}</span><br/>
                        <b>Status:</b> {row.get('status')}<br/>
                        <b>Reason:</b> {row.get('reason')}
                    </div>
                    """
                    
                    # Choose icon color based on priority
                    prio = row.get("priority")
                    color = "red" if prio == "HIGH" else ("orange" if prio == "MEDIUM" else "green")
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_html, max_width=250),
                        icon=folium.Icon(color=color, icon="info-sign"),
                        tooltip=f"Task: {row.get('task_id')} ({row.get('feature_type')})"
                    ).add_to(qa_group)
                    
            qa_group.add_to(m)
            print("Added layer 'QA Tasks' to the map.")
        except Exception as e:
            print(f"Error adding QA Tasks layer: {e}")
            
    # Add Layer Control
    folium.LayerControl().add_to(m)
    
    # Save Map
    m.save(out_html_path)
    print(f"Standalone Map Preview saved to: {out_html_path}")

if __name__ == "__main__":
    geojson_dir = "/home/jupyter/Apple_Change_Detection_POC/output/geojson"
    out_html = "/home/jupyter/Apple_Change_Detection_POC/output/preview/Apple_POC_Map_Preview.html"
    create_map_preview(geojson_dir, out_html)
