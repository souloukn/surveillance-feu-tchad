"""
Complete update script: Fetch API data, generate map, and update fire_data.json
"""
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import io
import json
from popup_template import create_cyberpunk_popup
from datetime import datetime

# NASA FIRMS API Configuration
FIRMS_API_KEY = "bf5e35a4b23a40fdf6b1ce6ec90b8312"
FIRMS_CSV_URL = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{FIRMS_API_KEY}/MODIS_NRT/TCD/7"

print("🔥 SURVEILLANCE FEU TCHAD - Data Update")
print("=" * 50)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

# Try to fetch real data from API with retries
df = pd.DataFrame()
use_demo_data = False
api_success = False

for attempt in range(3):
    try:
        print(f"\n📡 Attempt {attempt + 1}/3: Fetching from NASA FIRMS API...")
        response = requests.get(FIRMS_CSV_URL, timeout=30)
        response.raise_for_status()
        
        if response.text.strip():
            df = pd.read_csv(io.StringIO(response.text))
            print(f"✅ API SUCCESS! Fetched {len(df)} fire detections")
            api_success = True
            break
        else:
            print("⚠️  API returned empty data")
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout on attempt {attempt + 1}")
    except Exception as e:
        print(f"❌ Error on attempt {attempt + 1}: {str(e)[:100]}")
    
    if attempt < 2:
        print("   Retrying in 2 seconds...")
        import time
        time.sleep(2)

# Fallback to demo data if API failed
if not api_success or df.empty:
    print("\n📦 Using demo data from fire_data.json...")
    use_demo_data = True
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
                'brightness': 350.0
            })
        
        df = pd.DataFrame(records)
        df['acq_date'] = pd.to_datetime(df['acq_date'])
        print(f"✅ Loaded {len(df)} detections from demo data")
    except Exception as e:
        print(f"❌ Error loading demo data: {e}")
        exit(1)

if df.empty:
    print("❌ No data available!")
    exit(1)

# Clean and process data
print("\n🔧 Processing data...")
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['brightness'] = pd.to_numeric(df.get('brightness', 350), errors='coerce').fillna(350)
df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(50)
df['satellite'] = df.get('satellite', 'MODIS').fillna('MODIS')

# Ensure acq_date is datetime
if 'acq_date' not in df.columns:
    df['acq_date'] = pd.Timestamp.now()
else:
    df['acq_date'] = pd.to_datetime(df['acq_date'], errors='coerce')

df = df.dropna(subset=['latitude', 'longitude']).copy()

print(f"📊 Valid detections: {len(df)}")
print(f"   Date range: {df['acq_date'].min().strftime('%Y-%m-%d')} to {df['acq_date'].max().strftime('%Y-%m-%d')}")

# Calculate statistics
stats = {
    'total_detections': int(len(df)),
    'confidence_counts': {
        'Détections Haute Confiance': int((df['confidence'] > 79).sum()),
        'Détections Nominale Confiance': int(((df['confidence'] >= 30) & (df['confidence'] <= 79)).sum()),
        'Détections Basse Confiance': int((df['confidence'] < 30).sum()),
        'Détections Confiance Inconnue': 0
    },
    'satellite_counts': df['satellite'].value_counts().to_dict(),
    'recent_date_range': f"{df['acq_date'].max().strftime('%Y-%m-%d')} - {df['acq_date'].min().strftime('%Y-%m-%d')}"
}

# Create detailList
detail_list = []
for _, row in df.head(100).iterrows():  # Limit to 100 for performance
    detail_list.append({
        'date': row['acq_date'].strftime('%Y-%m-%d'),
        'time': str(row.get('acq_time', '0000')).zfill(4),
        'location': f"{row['latitude']:.2f}, {row['longitude']:.2f}",
        'confidence': str(int(row['confidence']))
    })

# Save updated fire_data.json
print("\n💾 Saving fire_data.json...")
fire_data = {
    'stats': stats,
    'detailList': detail_list,
    'fireRecords': []  # Will be populated by dashboard
}

with open('fire_data.json', 'w', encoding='utf-8') as f:
    json.dump(fire_data, f, indent=2, ensure_ascii=False)
print("✅ fire_data.json updated")

# Create map
print("\n🗺️  Creating interactive map...")
center_lat = df['latitude'].mean()
center_lon = df['longitude'].mean()

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
    overlay=False
).add_to(fire_map)

folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB',
    name='Carte Sombre',
    overlay=False
).add_to(fire_map)

# Marker cluster
marker_cluster = MarkerCluster(name='Détections Feux').add_to(fire_map)

# Color function
def get_color(conf):
    return '#ff0040' if conf > 79 else '#ff8c00' if conf >= 30 else '#00ff88'

# Add markers
print(f"📍 Adding {len(df)} markers...")
for idx, row in df.iterrows():
    try:
        popup_html = create_cyberpunk_popup(
            date=row['acq_date'].strftime('%Y-%m-%d'),
            time=str(row.get('acq_time', '0000')).zfill(4),
            latitude=f"{row['latitude']:.2f}",
            longitude=f"{row['longitude']:.2f}",
            brightness=f"{row['brightness']:.1f} K",
            confidence=str(int(row['confidence'])),
            satellite=row['satellite'],
            brightness_raw=row['brightness']
        )
        
        color = get_color(row['confidence'])
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"🔥 {row['acq_date'].strftime('%Y-%m-%d')}"
        ).add_to(marker_cluster)
    except Exception as e:
        continue

folium.LayerControl(position='topright', collapsed=False).add_to(fire_map)

# Save map
fire_map.save('firms_tcd_map.html')
print("✅ firms_tcd_map.html saved")

# Summary
print("\n" + "=" * 50)
print("✅ UPDATE COMPLETE!")
print("=" * 50)
print(f"📊 Statistics:")
print(f"   - Total fires: {stats['total_detections']}")
print(f"   - High confidence: {stats['confidence_counts']['Détections Haute Confiance']}")
print(f"   - Nominal confidence: {stats['confidence_counts']['Détections Nominale Confiance']}")
print(f"   - Low confidence: {stats['confidence_counts']['Détections Basse Confiance']}")
print(f"   - Satellites: {', '.join(stats['satellite_counts'].keys())}")
print(f"\n🌐 Data source: {'NASA FIRMS API (REAL-TIME)' if api_success else 'Demo data (fallback)'}")
print(f"🗺️  View dashboard.html to see the updated map")
