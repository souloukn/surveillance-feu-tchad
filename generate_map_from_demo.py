"""
Generate Folium map from demo fire_data.json with enhanced cyberpunk popups
"""
import json
import folium
from folium.plugins import MarkerCluster
from popup_template import create_cyberpunk_popup

# Load demo data
print("Loading demo data from fire_data.json...")
with open('fire_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {data['stats']['total_detections']} fire detections")

# Create map centered on Chad
center_lat = 15.45
center_lon = 19.17

print("Creating Folium map...")
fire_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles='OpenStreetMap'
)

# Add different base layers
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri World Imagery',
    name='Satellite',
    overlay=False,
    control=True
).add_to(fire_map)

folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB Dark',
    name='Carte Fond Sombre',
    overlay=False,
    control=True
).add_to(fire_map)

# Create marker cluster for fire detections
marker_cluster = MarkerCluster(name='Détections Feux').add_to(fire_map)

# Color mapping for confidence levels
def get_fire_color(confidence_str):
    """Get color based on confidence level"""
    conf_lower = str(confidence_str).lower()
    if 'haute' in conf_lower or int(confidence_str) > 79:
        return '#ff0040'  # Red for high confidence
    elif 'nominale' in conf_lower or (30 <= int(confidence_str) <= 79):
        return '#ff8c00'  # Orange for nominal
    elif 'basse' in conf_lower or int(confidence_str) < 30:
        return '#00ff88'  # Green for low
    else:
        return '#888888'  # Gray for unknown

# Add fire markers from detailList
print(f"Adding {len(data['detailList'])} fire markers to map...")
for idx, fire in enumerate(data['detailList']):
    try:
        # Parse location (format: "lat, lon")
        lat_str, lon_str = fire['location'].split(',')
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        
        # Get fire details
        date = fire.get('date', 'N/A')
        time = fire.get('time', 'N/A')
        confidence = fire.get('confidence', 'N/A')
        
        # Create enhanced popup
        popup_html = create_cyberpunk_popup(
            date=date,
            time=time,
            latitude=f"{lat:.2f}",
            longitude=f"{lon:.2f}",
            brightness="N/A",  # Not available in detailList
            confidence=confidence,
            satellite="MODIS"  # Default
        )
        
        # Determine marker color
        color = get_fire_color(confidence)
        
        # Add circle marker
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"🔥 Feu: {date} {time}"
        ).add_to(marker_cluster)
        
        if (idx + 1) % 20 == 0:
            print(f"  Added {idx + 1} markers...")
            
    except Exception as e:
        print(f"Error processing fire {idx}: {e}")
        continue

print(f"Successfully added {len(data['detailList'])} fire markers")

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(fire_map)

# Save map
output_file = 'firms_tcd_map.html'
print(f"Saving map to {output_file}...")
fire_map.save(output_file)
print(f"✅ Map saved successfully to {output_file}")
print(f"\n📊 Map Summary:")
print(f"   - Total fires: {data['stats']['total_detections']}")
print(f"   - Date range: {data['stats']['recent_date_range']}")
print(f"   - Satellites: {', '.join(data['stats']['satellite_counts'].keys())}")
print(f"\n🗺️ Open {output_file} in a browser to view the map!")
