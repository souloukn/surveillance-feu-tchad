# Generate animated fire map with GeoJSON boundaries - NO CLUSTERING
import json
import folium
from folium import plugins
import numpy as np
from popup_template import create_modern_popup

print("Loading demo fire data...")

# Load data from JSON
with open('fire_data.json', 'r', encoding='utf-8') as f:
    dashboard_data = json.load(f)

fire_records = dashboard_data['fireRecords']
print(f"Loaded {len(fire_records)} fire records")

if len(fire_records) == 0:
    print("❌ No fire data available!")
    exit(1)

# Extract coordinates and data
fires_data = []
for record in fire_records:
    try:
        lat = float(record[2])
        lon = float(record[3])
        brightness_str = record[4]
        brightness = float(brightness_str.split(' K')[0])
        confidence = int(record[5])
        
        fires_data.append({
            'lat': lat,
            'lon': lon,
            'date': record[0],
            'time': record[1],
            'brightness': brightness,
            'confidence': confidence,
            'satellite': record[6]
        })
    except Exception as e:
        print(f"Warning: Could not parse record: {e}")
        continue

print(f"Parsed {len(fires_data)} valid fire records")

# Calculate map center
lats = [f['lat'] for f in fires_data]
lons = [f['lon'] for f in fires_data]
center_lat = np.median(lats)
center_lon = np.median(lons)

print(f"Map center: {center_lat:.2f}°N, {center_lon:.2f}°E")

# Create map
folium_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles='Esri World Imagery',
    attr='Tiles © Esri',
    control_scale=True
)

# Add tile layers
folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(folium_map)
folium.TileLayer('CartoDB darkmatter', name='Carte Fond Sombre', show=False).add_to(folium_map)

# Add Administrative Boundaries from GeoJSON
print("Adding administrative boundaries from GeoJSON files...")

try:
    # Provinces
    provinces_group = folium.FeatureGroup(name='🏛️ Provinces (23)', show=True)
    
    print("  Loading chad_provinces.geojson...")
    with open('chad_provinces.geojson', 'r', encoding='utf-8') as f:
        provinces_geojson = json.load(f)
    
    for feature in provinces_geojson['features']:
        province_name = feature['properties'].get('NAME_1', 'Province inconnue')
        
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 220px;">
            <div style="background: linear-gradient(135deg, #2196F3 0%, #1565C0 100%); padding: 12px; margin: -9px -9px 12px -9px; border-radius: 4px 4px 0 0;">
                <h4 style="margin: 0; color: white; font-size: 15px; font-weight: 600;">🏛️ Province</h4>
            </div>
            <div style="padding: 10px;">
                <div style="font-size: 18px; font-weight: 700; color: #1565C0; margin-bottom: 8px;">
                    {province_name}
                </div>
                <div style="font-size: 11px; color: #666;">
                    📍 Niveau administratif 1<br>
                    🗺️ Source: Shapefile officiel
                </div>
            </div>
        </div>
        """
        
        folium.GeoJson(
            feature,
            style_function=lambda x: {
                'fillColor': '#2196F3',
                'color': '#2196F3',
                'weight': 2.5,
                'fillOpacity': 0.05,
                'opacity': 0.8
            },
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Province: {province_name}"
        ).add_to(provinces_group)
    
    provinces_group.add_to(folium_map)
    print(f"  ✅ Added {len(provinces_geojson['features'])} provinces")
    
except FileNotFoundError:
    print("  ⚠️ chad_provinces.geojson not found")
except Exception as e:
    print(f"  ⚠️ Error loading provinces: {e}")

try:
    # Départements
    depts_group = folium.FeatureGroup(name='🏘️ Départements (55)', show=False)
    
    print("  Loading chad_departments.geojson...")
    with open('chad_departments.geojson', 'r', encoding='utf-8') as f:
        depts_geojson = json.load(f)
    
    for feature in depts_geojson['features']:
        dept_name = feature['properties'].get('NAME_2', 'Département inconnu')
        
        folium.GeoJson(
            feature,
            style_function=lambda x: {
                'fillColor': '#4CAF50',
                'color': '#4CAF50',
                'weight': 1.5,
                'fillOpacity': 0.03,
                'opacity': 0.6
            },
            popup=f"<b>Département:</b> {dept_name}",
            tooltip=f"Département: {dept_name}"
        ).add_to(depts_group)
    
    depts_group.add_to(folium_map)
    print(f"  ✅ Added {len(depts_geojson['features'])} départements")
    
except FileNotFoundError:
    print("  ⚠️ chad_departments.geojson not found")
except Exception as e:
    print(f"  ⚠️ Error loading départements: {e}")

# Create feature groups
fires_group = folium.FeatureGroup(name='🔥 Feux Actifs (Animation)', show=True)
fires_group.add_to(folium_map)

# Load administrative data for fire location identification
print("Loading administrative data for fire identification...")
try:
    with open('chad_provinces.geojson', 'r', encoding='utf-8') as f:
        provinces_geojson = json.load(f)
    with open('chad_departments.geojson', 'r', encoding='utf-8') as f:
        departments_geojson = json.load(f)
    print("  ✅ Administrative data loaded")
except Exception as e:
    print(f"  ⚠️ Error loading administrative data: {e}")
    provinces_geojson = None
    departments_geojson = None

def get_admin_units(lat, lon):
    """Identify province and department for given coordinates"""
    from shapely.geometry import Point, shape
    
    point = Point(lon, lat)
    province_name = "Province inconnue"
    department_name = "Département inconnu"
    
    if provinces_geojson:
        for feature in provinces_geojson['features']:
            try:
                poly = shape(feature['geometry'])
                if poly.contains(point):
                    province_name = feature['properties'].get('NAME_1', 'Province inconnue')
                    break
            except:
                pass
    
    if departments_geojson:
        for feature in departments_geojson['features']:
            try:
                poly = shape(feature['geometry'])
                if poly.contains(point):
                    department_name = feature['properties'].get('NAME_2', 'Département inconnu')
                    break
            except:
                pass
    
    return province_name, department_name

def get_weather_data(lat, lon):
    """Fetch weather data from OpenWeatherMap API"""
    import requests
    
    api_key = '93001eb223da7a2e6159542cf220c81c'
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}&lang=fr'
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind'].get('deg', 0),
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon']
            }
    except Exception as e:
        print(f"  ⚠️ Weather API error for {lat},{lon}: {e}")
    
    return None

def calculate_fire_risk(weather, brightness, confidence):
    """Calculate fire risk score based on weather and fire data"""
    if not weather:
        return 'INCONNU', '#9E9E9E', 50
    
    risk_score = 0
    
    # Temperature factor
    if weather['temp'] > 40:
        risk_score += 35
    elif weather['temp'] > 35:
        risk_score += 25
    elif weather['temp'] > 30:
        risk_score += 15
    
    # Humidity factor (inverse)
    if weather['humidity'] < 20:
        risk_score += 30
    elif weather['humidity'] < 30:
        risk_score += 20
    elif weather['humidity'] < 40:
        risk_score += 10
    
    # Wind factor
    if weather['wind_speed'] > 15:
        risk_score += 25
    elif weather['wind_speed'] > 10:
        risk_score += 15
    elif weather['wind_speed'] > 5:
        risk_score += 8
    
    # Fire intensity factor
    if brightness > 400:
        risk_score += 10
    elif brightness > 380:
        risk_score += 7
    
    if confidence > 90:
        risk_score += 5
    elif confidence > 80:
        risk_score += 3
    
    # Determine risk level
    if risk_score >= 80:
        return 'CRITIQUE', '#D32F2F', risk_score
    elif risk_score >= 60:
        return 'TRÈS ÉLEVÉ', '#F57C00', risk_score
    elif risk_score >= 40:
        return 'ÉLEVÉ', '#FFA726', risk_score
    elif risk_score >= 20:
        return 'MODÉRÉ', '#FFCA28', risk_score
    else:
        return 'FAIBLE', '#66BB6A', risk_score

# Add ANIMATED fire markers with custom SVG icon (NO CLUSTERING!)
print("Adding animated fire markers with weather data and charts...")

# Fetch weather data for ALL fires (with caching to avoid duplicate API calls)
print("  Fetching weather data for all fire locations...")
weather_cache = {}
for idx, fire in enumerate(fires_data):
    key = f"{fire['lat']:.2f},{fire['lon']:.2f}"
    if key not in weather_cache:
        weather = get_weather_data(fire['lat'], fire['lon'])
        if weather:
            weather_cache[key] = weather
            print(f"    [{idx+1}/{len(fires_data)}] Weather fetched for {fire['lat']:.2f}, {fire['lon']:.2f}", end='\r')
print(f"\n  ✅ Fetched weather for {len(weather_cache)} unique locations")

# Custom CSS for realistic animated flames
flame_animation = """
<style>
@keyframes fireFlicker {
    0%, 100% { 
        transform: scale(1) translateY(0px) rotate(-2deg);
        opacity: 1;
        filter: brightness(1) drop-shadow(0 0 10px rgba(255, 100, 0, 0.8));
    }
    25% { 
        transform: scale(1.08) translateY(-2px) rotate(1deg);
        opacity: 0.95;
        filter: brightness(1.1) drop-shadow(0 0 12px rgba(255, 80, 0, 0.9));
    }
    50% { 
        transform: scale(1.12) translateY(-4px) rotate(-1deg);
        opacity: 0.9;
        filter: brightness(1.2) drop-shadow(0 0 15px rgba(255, 60, 0, 1));
    }
    75% { 
        transform: scale(1.06) translateY(-2px) rotate(2deg);
        opacity: 0.95;
        filter: brightness(1.15) drop-shadow(0 0 12px rgba(255, 70, 0, 0.9));
    }
}

@keyframes fireGlow {
    0%, 100% { 
        box-shadow: 0 0 20px rgba(255, 100, 0, 0.6), 0 0 30px rgba(255, 50, 0, 0.4);
    }
    50% { 
        box-shadow: 0 0 30px rgba(255, 100, 0, 0.8), 0 0 40px rgba(255, 50, 0, 0.6);
    }
}

.fire-marker {
    animation: fireFlicker 1.5s ease-in-out infinite;
    cursor: pointer;
    position: relative;
}

.fire-marker::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    animation: fireGlow 2s ease-in-out infinite;
    z-index: -1;
}

.fire-marker:hover {
    animation-duration: 0.8s;
    transform: scale(1.3) !important;
}
</style>
"""

# Add each fire as individual marker with SVG flame icon
for i, fire in enumerate(fires_data):
    # Get administrative units
    province, department = get_admin_units(fire['lat'], fire['lon'])
    
    # Get weather data (use cached if available)
    key = f"{fire['lat']:.2f},{fire['lon']:.2f}"
    weather = weather_cache.get(key, None)
    
    # Calculate fire risk
    risk_level, risk_color, risk_score = calculate_fire_risk(weather, fire['brightness'], fire['confidence'])
    
    # Determine size and colors based on intensity (REDUCED SIZES)
    if fire['brightness'] > 400:
        size = 32  # Reduced from 45
        base_color = '#FF0000'
        mid_color = '#FF4400'
        top_color = '#FFAA00'
        intensity_label = 'EXTRÊME'
    elif fire['brightness'] > 380:
        size = 28  # Reduced from 38
        base_color = '#FF2200'
        mid_color = '#FF5500'
        top_color = '#FFBB00'
        intensity_label = 'TRÈS HAUTE'
    elif fire['brightness'] > 350:
        size = 24  # Reduced from 32
        base_color = '#FF4400'
        mid_color = '#FF6600'
        top_color = '#FFCC00'
        intensity_label = 'HAUTE'
    else:
        size = 20  # Reduced from 26
        base_color = '#FF6600'
        mid_color = '#FF8800'
        top_color = '#FFDD00'
        intensity_label = 'MODÉRÉE'
    
    # Create realistic SVG flame
    svg_flame = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <!-- Outer flame glow -->
        <ellipse cx="50" cy="90" rx="35" ry="15" fill="{base_color}" opacity="0.3"/>
        
        <!-- Main flame body -->
        <path d="M 50 10 Q 30 30 35 50 Q 30 70 50 95 Q 70 70 65 50 Q 70 30 50 10 Z" 
              fill="url(#flameGradient{i})" stroke="{base_color}" stroke-width="1" opacity="0.95"/>
        
        <!-- Inner flame -->
        <path d="M 50 20 Q 40 35 42 50 Q 40 65 50 80 Q 60 65 58 50 Q 60 35 50 20 Z" 
              fill="url(#innerFlame{i})" opacity="0.8"/>
        
        <!-- Flame core (bright center) -->
        <ellipse cx="50" cy="55" rx="8" ry="15" fill="#FFFFFF" opacity="0.7"/>
        <ellipse cx="50" cy="50" rx="5" ry="10" fill="#FFFFAA" opacity="0.9"/>
        
        <!-- Gradient definitions -->
        <defs>
            <radialGradient id="flameGradient{i}" cx="50%" cy="70%" r="60%">
                <stop offset="0%" style="stop-color:{top_color};stop-opacity:1" />
                <stop offset="50%" style="stop-color:{mid_color};stop-opacity:0.9" />
                <stop offset="100%" style="stop-color:{base_color};stop-opacity:0.7" />
            </radialGradient>
            <radialGradient id="innerFlame{i}" cx="50%" cy="60%" r="50%">
                <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:0.8" />
                <stop offset="30%" style="stop-color:#FFFF99;stop-opacity:0.7" />
                <stop offset="100%" style="stop-color:{mid_color};stop-opacity:0.5" />
            </radialGradient>
        </defs>
    </svg>
    """
    
    # Wrap SVG in animated div
    icon_html = f"""
    {flame_animation if i == 0 else ''}
    <div class="fire-marker" title="Feu {intensity_label}">
        {svg_flame}
    </div>
    """
    
    # Create ultra-modern popup with weather and charts
    popup_html = create_modern_popup(
        fire=fire,
        province=province,
        department=department,
        weather=weather,
        risk_level=risk_level,
        risk_color=risk_color,
        risk_score=risk_score,
        base_color=base_color,
        mid_color=mid_color,
        intensity_label=intensity_label,
        i=i
    )
    
    # Create DivIcon marker with custom SVG
    folium.Marker(
        location=[fire['lat'], fire['lon']],
        icon=folium.DivIcon(html=icon_html, icon_size=(size, size)),
        popup=folium.Popup(popup_html, max_width=450),
        tooltip=f"🔥 Feu {intensity_label}: {fire['brightness']:.0f}K - {fire['confidence']}% | Risque: {risk_level}"
    ).add_to(fires_group)

print(f"  ✅ Added {len(fires_data)} animated SVG fire markers (NO CLUSTERING)")

# Don't add weather legend on map (removed as requested)

# Add layer control
folium.LayerControl(position='topright').add_to(folium_map)

# Save map
output_file = 'firms_tcd_map.html'
folium_map.save(output_file)

print(f"\n✅ Map saved to {output_file}")
print(f"🔥 Total animated fire markers: {len(fires_data)}")
print(f"🏛️ Administrative boundaries: GeoJSON")
print("\n🌐 Open dashboard.html to see the complete dashboard!")
