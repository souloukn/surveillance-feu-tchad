# Generate map with demo fire data
import json
import folium
from folium.plugins import MarkerCluster
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull

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

# Add Administrative Boundaries
print("Adding administrative boundaries from OpenStreetMap...")

try:
    import requests
    from shapely.geometry import shape, Point
    
    # Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Query for Chad provinces (admin_level=4)
    overpass_query = """
    [out:json][timeout:60];
    area["ISO3166-1"="TD"][admin_level=2]->.chad;
    (
      relation["admin_level"="4"](area.chad);
    );
    out geom;
    """
    
    print("  Fetching province boundaries from Overpass API...")
    response = requests.post(overpass_url, data={'data': overpass_query}, timeout=90)
    
    if response.status_code == 200:
        data = response.json()
        provinces_group = folium.FeatureGroup(name='🏛️ Provinces du Tchad', show=True)
        provinces_data = []
        
        print(f"  Processing {len(data.get('elements', []))} province boundaries...")
        
        for element in data.get('elements', []):
            if element.get('type') == 'relation':
                tags = element.get('tags', {})
                province_name = tags.get('name', tags.get('name:fr', 'Province inconnue'))
                
                # Extract outer boundary coordinates
                coordinates = []
                for member in element.get('members', []):
                    if member.get('role') == 'outer' and member.get('type') == 'way':
                        if 'geometry' in member:
                            way_coords = [[point['lat'], point['lon']] for point in member['geometry']]
                            if way_coords:
                                coordinates.extend(way_coords)
                
                if len(coordinates) > 2:
                    # Create popup
                    popup_html = f"""
                    <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 220px;">
                        <div style="background: linear-gradient(135deg, #2196F3 0%, #1565C0 100%); padding: 12px; margin: -9px -9px 12px -9px; border-radius: 4px 4px 0 0;">
                            <h4 style="margin: 0; color: white; font-size: 15px; font-weight: 600;">🏛️ Province du Tchad</h4>
                        </div>
                        <div style="padding: 10px;">
                            <div style="font-size: 18px; font-weight: 700; color: #1565C0; margin-bottom: 8px;">
                                {province_name}
                            </div>
                            <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                                Division administrative de niveau 1
                            </div>
                            <div style="background: #f5f5f5; padding: 8px; border-radius: 4px; font-size: 11px;">
                                <strong>📍 Source:</strong> OpenStreetMap<br>
                                <strong>📏 Périmètre:</strong> ~{len(coordinates)} points
                            </div>
                        </div>
                    </div>
                    """
                    
                    # Add polygon to map
                    folium.Polygon(
                        locations=coordinates,
                        color='#2196F3',
                        weight=2.5,
                        fill=True,
                        fillColor='#2196F3',
                        fillOpacity=0.05,
                        opacity=0.8,
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"Province: {province_name}"
                    ).add_to(provinces_group)
                    
                    provinces_data.append({
                        'name': province_name,
                        'coords': coordinates
                    })
                    print(f"    ✓ {province_name}")
        
        provinces_group.add_to(folium_map)
        print(f"  ✅ Successfully added {len(provinces_data)} province boundaries")
        
        # Store for later use in fire statistics
        chad_provinces = provinces_data
        
    else:
        print(f"  ⚠️ Could not fetch province boundaries (HTTP {response.status_code})")
        print(f"  Using simplified boundaries as fallback...")
        # Keep the simplified version as fallback
        chad_provinces = [
            {'name': 'Salamat', 'coords': [[10.5, 20.5], [12.0, 20.5], [12.0, 22.5], [10.5, 22.5], [10.5, 20.5]]},
            {'name': 'Moyen-Chari', 'coords': [[9.0, 18.0], [10.5, 18.0], [10.5, 20.0], [9.0, 20.0], [9.0, 18.0]]},
            {'name': 'Logone Oriental', 'coords': [[8.0, 16.0], [9.5, 16.0], [9.5, 17.0], [8.0, 17.0], [8.0, 16.0]]},
            {'name': 'Chari-Baguirmi', 'coords': [[11.0, 14.5], [12.5, 14.5], [12.5, 16.5], [11.0, 16.5], [11.0, 14.5]]}
        ]
        
except ImportError:
    print("  ⚠️ shapely not installed. Installing...")
    import subprocess
    subprocess.run(['pip', 'install', 'shapely'], check=False)
    print("  Please run the script again after installation.")
    chad_provinces = []
    
except Exception as e:
    print(f"  ⚠️ Error fetching boundaries: {e}")
    print(f"  Using simplified boundaries as fallback...")
    chad_provinces = [
        {'name': 'Salamat', 'coords': [[10.5, 20.5], [12.0, 20.5], [12.0, 22.5], [10.5, 22.5], [10.5, 20.5]]},
        {'name': 'Moyen-Chari', 'coords': [[9.0, 18.0], [10.5, 18.0], [10.5, 20.0], [9.0, 20.0], [9.0, 18.0]]}
    ]

# Create feature groups
marker_cluster = MarkerCluster(name='Points de Détection')
marker_cluster.add_to(folium_map)

fire_polygons_group = folium.FeatureGroup(name='Zones de Feu (Polygones)', show=True)
fire_polygons_group.add_to(folium_map)

# Add individual markers
print("Adding fire markers to map...")
for fire in fires_data:
    # Determine marker color based on confidence
    if fire['confidence'] > 79:
        color = 'red'
    elif fire['confidence'] >= 30:
        color = 'orange'
    else:
        color = 'cyan'
    
    # Determine marker size based on brightness
    if fire['brightness'] > 400:
        radius = 8
    elif fire['brightness'] > 380:
        radius = 6
    elif fire['brightness'] > 350:
        radius = 4
    else:
        radius = 3
    
    popup_html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 280px; padding: 5px;">
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%); padding: 12px; margin: -9px -9px 12px -9px; border-radius: 4px 4px 0 0;">
            <h3 style="margin: 0; color: white; font-size: 16px; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">
                🔥 Détection de Feu
            </h3>
        </div>
        <div style="padding: 0 5px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 8px 4px; color: #666; font-weight: 500;">📅 Date</td>
                    <td style="padding: 8px 4px; text-align: right; font-weight: 600;">{fire['date']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 8px 4px; color: #666; font-weight: 500;">⏰ Heure</td>
                    <td style="padding: 8px 4px; text-align: right; font-weight: 600;">{fire['time']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 8px 4px; color: #666; font-weight: 500;">📍 Latitude</td>
                    <td style="padding: 8px 4px; text-align: right; font-weight: 600;">{fire['lat']:.4f}°N</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 8px 4px; color: #666; font-weight: 500;">📍 Longitude</td>
                    <td style="padding: 8px 4px; text-align: right; font-weight: 600;">{fire['lon']:.4f}°E</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee; background: {'rgba(255,0,0,0.1)' if fire['brightness'] > 380 else 'rgba(255,200,0,0.1)' if fire['brightness'] > 340 else 'white'};">
                    <td style="padding: 8px 4px; color: #666; font-weight: 500;">🌡️ Luminosité</td>
                    <td style="padding: 8px 4px; text-align: right; font-weight: 700; color: {'#d32f2f' if fire['brightness'] > 380 else '#f57c00' if fire['brightness'] > 340 else '#388e3c'};">
                        {fire['brightness']:.1f} K {'🔥🔥🔥' if fire['brightness'] > 400 else '🔥🔥' if fire['brightness'] > 380 else '🔥'}
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #eee; background: {'rgba(255,0,0,0.1)' if fire['confidence'] > 80 else 'rgba(255,200,0,0.1)' if fire['confidence'] > 60 else 'white'};">
                    <td style="padding: 8px 4px; color: #666; font-weight: 500;">🎯 Confiance</td>
                    <td style="padding: 8px 4px; text-align: right;">
                        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px;">
                            <div style="flex: 1; max-width: 100px; background: #eee; border-radius: 10px; height: 8px; overflow: hidden;">
                                <div style="width: {fire['confidence']}%; height: 100%; background: {'#4caf50' if fire['confidence'] > 80 else '#ff9800' if fire['confidence'] > 60 else '#f44336'}; border-radius: 10px;"></div>
                            </div>
                            <span style="font-weight: 700; color: {'#4caf50' if fire['confidence'] > 80 else '#ff9800' if fire['confidence'] > 60 else '#f44336'};">{fire['confidence']}%</span>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 4px; color: #666; font-weight: 500;">🛰️ Satellite</td>
                    <td style="padding: 8px 4px; text-align: right; font-weight: 600; color: #1976d2;">{fire['satellite']}</td>
                </tr>
            </table>
        </div>
        <div style="margin-top: 12px; padding: 10px; background: #f5f5f5; border-radius: 4px; font-size: 11px; color: #666;">
            <strong style="color: #333;">💡 Évaluation:</strong> 
            {'⚠️ Feu très intense - Surveillance prioritaire' if fire['brightness'] > 380 and fire['confidence'] > 80 else 
             '⚠️ Feu intense - Surveillance recommandée' if fire['brightness'] > 340 or fire['confidence'] > 70 else 
             'ℹ️ Feu modéré - Surveillance normale'}
        </div>
    </div>
    """
    
    folium.CircleMarker(
        location=[fire['lat'], fire['lon']],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        weight=1,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"Feu: {fire['date']} {fire['time']}"
    ).add_to(marker_cluster)

# Generate polygons
print("Generating fire polygons...")
coords = np.array([[f['lat'], f['lon']] for f in fires_data])

# DBSCAN clustering
clustering = DBSCAN(eps=0.5, min_samples=3).fit(coords)
labels = clustering.labels_

unique_labels = set(labels)
n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
print(f"Found {n_clusters} fire clusters")

# Create polygons for each cluster
for cluster_id in unique_labels:
    if cluster_id == -1:
        continue
    
    cluster_mask = labels == cluster_id
    cluster_fires = [f for i, f in enumerate(fires_data) if cluster_mask[i]]
    
    if len(cluster_fires) < 3:
        continue
    
    # Statistics
    avg_brightness = np.mean([f['brightness'] for f in cluster_fires])
    max_brightness = np.max([f['brightness'] for f in cluster_fires])
    avg_confidence = np.mean([f['confidence'] for f in cluster_fires])
    fire_count = len(cluster_fires)
    
    # Create convex hull
    points = np.array([[f['lat'], f['lon']] for f in cluster_fires])
    
    try:
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]
        
        # Buffer
        center = hull_points.mean(axis=0)
        buffer_factor = 1.3
        buffered_points = center + (hull_points - center) * buffer_factor
        
        # Color based on intensity
        if avg_brightness > 380 or avg_confidence > 90:
            color = '#FF0000'
            fill_opacity = 0.4
            intensity = "TRÈS ÉLEVÉE"
        elif avg_brightness > 340 or avg_confidence > 70:
            color = '#FF6600'
            fill_opacity = 0.35
            intensity = "ÉLEVÉE"
        else:
            color = '#FFAA00'
            fill_opacity = 0.3
            intensity = "MODÉRÉE"
        
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 320px; max-width: 400px;">
            <div style="background: linear-gradient(135deg, {color} 0%, {'#cc0000' if color == '#FF0000' else '#cc5200' if color == '#FF6600' else '#cc8800'} 100%); padding: 15px; margin: -9px -9px 15px -9px; border-radius: 6px 6px 0 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 5px 0; color: white; font-size: 18px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    🔥 Zone de Feu #{cluster_id + 1}
                </h3>
                <div style="display: inline-block; background: rgba(255,255,255,0.25); padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; color: white; text-transform: uppercase; letter-spacing: 0.5px;">
                    {intensity}
                </div>
            </div>
            <div style="padding: 5px 10px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 15px;">
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid {color};">
                        <div style="font-size: 11px; color: #666; font-weight: 500; margin-bottom: 4px;">🔥 NOMBRE DE FEUX</div>
                        <div style="font-size: 24px; font-weight: 700; color: #333;">{fire_count}</div>
                    </div>
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid {color};">
                        <div style="font-size: 11px; color: #666; font-weight: 500; margin-bottom: 4px;">🎯 CONFIANCE MOY.</div>
                        <div style="font-size: 24px; font-weight: 700; color: #333;">{avg_confidence:.0f}%</div>
                    </div>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 12px;">
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px 4px; color: #666; font-weight: 500;">🌡️ Luminosité moyenne</td>
                        <td style="padding: 10px 4px; text-align: right; font-weight: 700; color: {color};">{avg_brightness:.1f} K</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px 4px; color: #666; font-weight: 500;">🔥 Luminosité maximale</td>
                        <td style="padding: 10px 4px; text-align: right; font-weight: 700; color: #d32f2f;">{max_brightness:.1f} K</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 4px; color: #666; font-weight: 500;">📍 Surface estimée</td>
                        <td style="padding: 10px 4px; text-align: right; font-weight: 600; color: #1976d2;">~{len(hull_points)} km²</td>
                    </tr>
                </table>
                
                <div style="background: {'#ffebee' if intensity == 'TRÈS ÉLEVÉE' else '#fff3e0' if intensity == 'ÉLEVÉE' else '#e8f5e9'}; padding: 12px; border-radius: 6px; border-left: 4px solid {color};">
                    <div style="font-weight: 600; color: #333; margin-bottom: 6px; font-size: 12px;">
                        {'⚠️ ALERTE MAXIMALE' if intensity == 'TRÈS ÉLEVÉE' else '⚠️ SURVEILLANCE RENFORCÉE' if intensity == 'ÉLEVÉE' else 'ℹ️ SURVEILLANCE STANDARD'}
                    </div>
                    <div style="font-size: 11px; color: #555; line-height: 1.5;">
                        {'Zone à très haute intensité. Déploiement prioritaire recommandé. Risque de propagation rapide.' if intensity == 'TRÈS ÉLEVÉE' else 
                         'Zone à forte intensité. Surveillance accrue nécessaire. Intervention recommandée.' if intensity == 'ÉLEVÉE' else 
                         'Zone à intensité modérée. Surveillance de routine suffisante.'}
                    </div>
                </div>
                
                <div style="margin-top: 12px; padding: 8px; background: #f5f5f5; border-radius: 4px; text-align: center;">
                    <div style="font-size: 10px; color: #999; text-transform: uppercase; letter-spacing: 0.5px;">Données NASA FIRMS</div>
                </div>
            </div>
        </div>
        """
        
        folium.Polygon(
            locations=buffered_points.tolist(),
            color=color,
            weight=3,
            fill=True,
            fill_color=color,
            fill_opacity=fill_opacity,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Zone: {fire_count} feux - {intensity}"
        ).add_to(fire_polygons_group)
        
        # Center marker
        folium.CircleMarker(
            location=center.tolist(),
            radius=10,
            color=color,
            fill=True,
            fill_color='white',
            fill_opacity=0.8,
            weight=3,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(fire_polygons_group)
        
        print(f"  Created polygon for cluster {cluster_id + 1}: {fire_count} fires")
        
    except Exception as e:
        print(f"  Warning: Could not create polygon for cluster {cluster_id}: {e}")

# Add layer control
folium.LayerControl(position='topright').add_to(folium_map)

# Save map
output_file = 'firms_tcd_map.html'
folium_map.save(output_file)

print(f"\n✅ Map saved to {output_file}")
print(f"📍 Total fires displayed: {len(fires_data)}")
print(f"🔥 Fire clusters with polygons: {n_clusters}")

# Calculate fires per province
print("\n📊 Calculating fires by province...")
fires_by_province = {}

for fire in fires_data:
    fire_lat = fire['lat']
    fire_lon = fire['lon']
    
    # Determine which province the fire is in
    fire_province = 'Hors province'
    for province in chad_provinces:
        coords = province['coords']
        # Simple point-in-polygon check (bounding box)
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        
        if min(lats) <= fire_lat <= max(lats) and min(lons) <= fire_lon <= max(lons):
            fire_province = province['name']
            break
    
    if fire_province not in fires_by_province:
        fires_by_province[fire_province] = {
            'count': 0,
            'high_confidence': 0,
            'avg_brightness': []
        }
    
    fires_by_province[fire_province]['count'] += 1
    if fire['confidence'] > 80:
        fires_by_province[fire_province]['high_confidence'] += 1
    fires_by_province[fire_province]['avg_brightness'].append(fire['brightness'])

# Calculate averages and sort
for province_name in fires_by_province:
    brightness_vals = fires_by_province[province_name]['avg_brightness']
    if brightness_vals:
        fires_by_province[province_name]['avg_brightness'] = sum(brightness_vals) / len(brightness_vals)
    else:
        fires_by_province[province_name]['avg_brightness'] = 0

# Sort by fire count
sorted_provinces = sorted(fires_by_province.items(), key=lambda x: x[1]['count'], reverse=True)

print("\n🏆 Top 10 Provinces par nombre de feux:")
print("=" * 70)
for i, (province_name, stats) in enumerate(sorted_provinces[:10], 1):
    print(f"{i:2d}. {province_name:20s} | Feux: {stats['count']:3d} | Haute conf: {stats['high_confidence']:3d} | Lum. moy: {stats['avg_brightness']:.1f}K")

print(f"\n✅ Map saved to {output_file}")
print(f"📍 Total fires displayed: {len(fires_data)}")
print(f"🔥 Fire clusters with polygons: {n_clusters}")
print("\n🌐 Now open dashboard.html to see the complete dashboard with all data!")
