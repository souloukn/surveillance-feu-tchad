"""
Script to generate map with real FIRMS API data, with demo data fallback
"""
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import io
import json
from popup_template import create_cyberpunk_popup

# NASA FIRMS API Configuration
FIRMS_API_KEY = "bf5e35a4b23a40fdf6b1ce6ec90b8312"
FIRMS_CSV_URL = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{FIRMS_API_KEY}/MODIS_NRT/TCD/7"

print("🔥 Generating fire detection map...")
print(f"📡 Fetching real-time data from NASA FIRMS API...")

# Try to fetch real data from API
df = pd.DataFrame()
use_demo_data = False

try:
    response = requests.get(FIRMS_CSV_URL, timeout=15)
    response.raise_for_status()
    
    if response.text.strip():
        df = pd.read_csv(io.StringIO(response.text))
        print(f"✅ Successfully fetched {len(df)} fire detections from API")
    else:
        print("⚠️  API returned empty data")
        use_demo_data = True
except Exception as e:
    print(f"⚠️  API fetch failed: {e}")
    use_demo_data = True

# Fallback to demo data if API failed
if use_demo_data or df.empty:
    print("📦 Loading demo data from fire_data.json...")
    try:
        with open('fire_data.json', 'r', encoding='utf-8') as f:
            demo_data = json.load(f)
        
        # Convert detailList to DataFrame
        records = []
        for fire in demo_data['detailList']:
            lat_str, lon_str = fire['location'].split(',')
            records.append({
                'latitude': float(lat_str.strip()),
                'longitude': float(lon_str.strip()),
                'acq_date': fire['date'],
                'acq_time': fire['time'],
                'confidence': int(fire['confidence']),
                'satellite': 'MODIS',
                'brightness': 350.0  # Default value
            })
        
        df = pd.DataFrame(records)
        df['acq_date'] = pd.to_datetime(df['acq_date'])
        print(f"✅ Loaded {len(df)} fire detections from demo data")
    except Exception as e:
        print(f"❌ Error loading demo data: {e}")
        df = pd.DataFrame()

# If still no data, exit
if df.empty:
    print("❌ No data available. Please check your API key or demo data file.")
    exit(1)

# Clean data
print("🔧 Processing data...")
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['brightness'] = pd.to_numeric(df.get('brightness', 350), errors='coerce').fillna(350)
df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(50)

# Remove invalid coordinates
df = df.dropna(subset=['latitude', 'longitude']).copy()
print(f"📊 Valid fire detections: {len(df)}")

# Create map
center_lat = df['latitude'].mean() if not df.empty else 15.45
center_lon = df['longitude'].mean() if not df.empty else 19.17

print("🗺️  Creating interactive map...")
fire_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles='OpenStreetMap'
)

# Add base layers
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satellite',
    overlay=False,
    control=True
).add_to(fire_map)

folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB',
    name='Carte Sombre',
    overlay=False,
    control=True
).add_to(fire_map)

# Create marker cluster
marker_cluster = MarkerCluster(name='Détections Feux').add_to(fire_map)

# Color function
def get_fire_color(confidence):
    if confidence > 79:
        return '#ff0040'  # High - Red
    elif confidence >= 30:
        return '#ff8c00'  # Nominal - Orange
    else:
        return '#00ff88'  # Low - Green

# Add markers
print(f"📍 Adding {len(df)} fire markers...")
for idx, row in df.iterrows():
    try:
        # Get values
        lat = row['latitude']
        lon = row['longitude']
        conf = row.get('confidence', 50)
        brightness = row.get('brightness', 350)
        date = row.get('acq_date', pd.NaT)
        time = row.get('acq_time', 'N/A')
        satellite = row.get('satellite', 'MODIS')
        
        # Format date
        date_str = date.strftime('%Y-%m-%d') if pd.notna(date) else 'N/A'
        time_str = str(time).zfill(4) if pd.notna(time) else 'N/A'
        
        # Create popup
        popup_html = create_cyberpunk_popup(
            date=date_str,
            time=time_str,
            latitude=f"{lat:.2f}",
            longitude=f"{lon:.2f}",
            brightness=f"{brightness:.1f} K",
            confidence=f"{conf}",
            satellite=satellite,
            brightness_raw=brightness
        )
        
        # Add marker
        color = get_fire_color(conf)
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"🔥 Feu: {date_str} {time_str}"
        ).add_to(marker_cluster)
        
        if (idx + 1) % 50 == 0:
            print(f"  ✓ Added {idx + 1} markers...")
            
    except Exception as e:
        print(f"  ⚠️  Error adding marker {idx}: {e}")
        continue

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(fire_map)

# Save map
output_file = 'firms_tcd_map.html'
fire_map.save(output_file)

print(f"\n✅ Map saved to {output_file}")
print(f"📊 Summary:")
print(f"   - Total fires: {len(df)}")
if not df.empty:
    print(f"   - Date range: {df['acq_date'].min().strftime('%Y-%m-%d')} to {df['acq_date'].max().strftime('%Y-%m-%d')}")
    print(f"   - Satellites: {', '.join(df['satellite'].unique())}")
print(f"\n🌐 Data source: {'NASA FIRMS API' if not use_demo_data else 'Demo data (fire_data.json)'}")
print(f"🗺️  Open {output_file} or view in dashboard.html")
