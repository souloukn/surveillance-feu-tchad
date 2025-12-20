"""
Multi-source API FIRMS (MODIS + VIIRS) with comprehensive filters
NO DEMO DATA - Only real API data
"""
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import io
import json
from popup_template import create_cyberpunk_popup
from datetime import datetime, timedelta
import sys
import os

print("=" * 70)
print("🔥 SURVEILLANCE FEU TCHAD - MULTI-SOURCE API")
print("=" * 70)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# ==================== CONFIGURATION ====================
# Essayer de charger filters_config.json si existe
if os.path.exists('filters_config.json'):
    print("\n📁 Configuration chargée depuis filters_config.json")
    with open('filters_config.json', 'r') as f:
        config = json.load(f)
    FIRMS_API_KEY = config.get('api_key', 'bf5e35a4b23a40fdf6b1ce6ec90b8312')
    DAYS_TO_FETCH = config.get('days', 10)
    FILTER_BY_SPECIFIC_REGION = config.get('use_regions', False)
    SELECTED_REGIONS = config.get('regions', ['Lac', 'Mayo-Kebbi'])
    MIN_CONFIDENCE = config.get('min_confidence', 30)
    MIN_BRIGHTNESS = config.get('min_brightness', 300)
else:
    FIRMS_API_KEY = "bf5e35a4b23a40fdf6b1ce6ec90b8312"
    DAYS_TO_FETCH = 10
    FILTER_BY_SPECIFIC_REGION = False
    SELECTED_REGIONS = ['Lac', 'Mayo-Kebbi']
    MIN_CONFIDENCE = 30
    MIN_BRIGHTNESS = 300
# FILTRES GÉOGRAPHIQUES
# Zone complète du Tchad
CHAD_BOUNDS = {
    'min_lat': 7.0,
    'max_lat': 23.5,
    'min_lon': 13.5,
    'max_lon': 24.0
}

# Sous-régions du Tchad (pour analyse régionale)
CHAD_REGIONS = {
    'Lac': {'min_lat': 12.5, 'max_lat': 14.5, 'min_lon': 13.5, 'max_lon': 15.5},
    'Kanem': {'min_lat': 13.0, 'max_lat': 16.0, 'min_lon': 14.0, 'max_lon': 16.5},
    'Batha': {'min_lat': 12.0, 'max_lat': 14.5, 'min_lon': 17.0, 'max_lon': 20.0},
    'Salamat': {'min_lat': 9.5, 'max_lat': 12.0, 'min_lon': 19.5, 'max_lon': 22.0},
    'Mayo-Kebbi': {'min_lat': 8.0, 'max_lat': 10.5, 'min_lon': 14.5, 'max_lon': 16.0},
    'Logone Oriental': {'min_lat': 7.5, 'max_lat': 9.5, 'min_lon': 15.5, 'max_lon': 17.0},
}

# FILTRES PAR RÉGION (Changez à True pour activer)
FILTER_BY_SPECIFIC_REGION = False
SELECTED_REGIONS = ['Lac', 'Mayo-Kebbi']  # Régions à surveiller

# FILTRES DE QUALITÉ
MIN_CONFIDENCE = 30  # Confiance minimum (0-100)
MIN_BRIGHTNESS = 300  # Température de brillance minimum (Kelvin)

print(f"\n⏰ FILTRE TEMPOREL:")
print(f"   Période: {DAYS_TO_FETCH} derniers jours (Maximum NRT)")
print(f"   Du: {(datetime.now() - timedelta(days=DAYS_TO_FETCH)).strftime('%Y-%m-%d')}")
print(f"   Au: {datetime.now().strftime('%Y-%m-%d')}")

print(f"\n🌍 FILTRES GÉOGRAPHIQUES:")
if FILTER_BY_SPECIFIC_REGION:
    print(f"   ✓ Régions spécifiques: {', '.join(SELECTED_REGIONS)}")
    for region in SELECTED_REGIONS:
        if region in CHAD_REGIONS:
            r = CHAD_REGIONS[region]
            print(f"     - {region}: Lat {r['min_lat']}-{r['max_lat']}, Lon {r['min_lon']}-{r['max_lon']}")
else:
    print(f"   ✓ Tchad complet:")
    print(f"     Lat: {CHAD_BOUNDS['min_lat']}° à {CHAD_BOUNDS['max_lat']}°")
    print(f"     Lon: {CHAD_BOUNDS['min_lon']}° à {CHAD_BOUNDS['max_lon']}°")

print(f"\n📊 FILTRES DE QUALITÉ:")
print(f"   • Confiance minimale: {MIN_CONFIDENCE}%")
print(f"   • Brillance minimale: {MIN_BRIGHTNESS}K")

# ==================== RÉCUPÉRATION MULTI-SOURCE ====================
sources = [
    {'name': 'MODIS (Terra+Aqua)', 'code': 'MODIS_NRT'},
    {'name': 'VIIRS (SNPP)', 'code': 'VIIRS_SNPP_NRT'},
    {'name': 'VIIRS (NOAA-20)', 'code': 'VIIRS_NOAA20_NRT'},
]

all_data = []

for source in sources:
    url = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{FIRMS_API_KEY}/{source['code']}/TCD/{DAYS_TO_FETCH}"
    
    print(f"\n📡 Source: {source['name']}")
    print(f"   URL: .../{source['code']}/TCD/{DAYS_TO_FETCH}")
    
    for attempt in range(2):
        try:
            print(f"   🔄 Tentative {attempt + 1}/2...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if response.text.strip():
                df_temp = pd.read_csv(io.StringIO(response.text))
                if not df_temp.empty:
                    df_temp['source'] = source['name']
                    all_data.append(df_temp)
                    print(f"   ✅ {len(df_temp)} détections reçues")
                    break
                else:
                    print(f"   ⚠️  Données vides")
            else:
                print(f"   ⚠️  Réponse vide")
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)[:80]}")
        
        if attempt == 0:
            import time
            time.sleep(2)

# Combiner toutes les sources
if not all_data:
    print("\n" + "=" * 70)
    print("❌ AUCUNE DONNÉE DISPONIBLE")
    print("=" * 70)
    print("\n💡 Raisons possibles:")
    print("   1. Pas de feux actifs au Tchad actuellement")
    print("   2. Problème de connexion API")
    print("   3. Clé API invalide")
    print("\n🔑 Obtenez une clé API gratuite:")
    print("   https://nrt4.modaps.eosdis.nasa.gov/api/v2/content/get-apps")
    print("\n🚫 PAS DE DONNÉES DE DÉMO UTILISÉES")
    sys.exit(1)

df = pd.concat(all_data, ignore_index=True)
print(f"\n✅ Total brut: {len(df)} détections de toutes sources")

# ==================== NETTOYAGE ET FILTRAGE ====================
print(f"\n🔧 Application des filtres...")

# Conversion
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['brightness'] = pd.to_numeric(df.get('brightness', 300), errors='coerce')
df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
df['acq_date'] = pd.to_datetime(df['acq_date'], errors='coerce')
df['acq_time'] = df.get('acq_time', '0000').astype(str).str.zfill(4)

initial = len(df)

# FILTRE 1: Coordonnées valides
df = df.dropna(subset=['latitude', 'longitude']).copy()
print(f"   ✓ Coordonnées valides: {len(df)}/{initial}")

# FILTRE 2: Zone géographique
if FILTER_BY_SPECIFIC_REGION:
    # Filtrer par régions spécifiques
    region_mask = pd.Series([False] * len(df))
    for region in SELECTED_REGIONS:
        if region in CHAD_REGIONS:
            r = CHAD_REGIONS[region]
            mask = (
                (df['latitude'] >= r['min_lat']) &
                (df['latitude'] <= r['max_lat']) &
                (df['longitude'] >= r['min_lon']) &
                (df['longitude'] <= r['max_lon'])
            )
            region_mask = region_mask | mask
    df = df[region_mask].copy()
    print(f"   ✓ Dans régions {SELECTED_REGIONS}: {len(df)}/{initial}")
else:
    # Tchad complet
    df = df[
        (df['latitude'] >= CHAD_BOUNDS['min_lat']) &
        (df['latitude'] <= CHAD_BOUNDS['max_lat']) &
        (df['longitude'] >= CHAD_BOUNDS['min_lon']) &
        (df['longitude'] <= CHAD_BOUNDS['max_lon'])
    ].copy()
    print(f"   ✓ Zone Tchad: {len(df)}/{initial}")

# FILTRE 3: Confiance
df = df[df['confidence'] >= MIN_CONFIDENCE].copy()
print(f"   ✓ Confiance ≥ {MIN_CONFIDENCE}%: {len(df)}/{initial}")

# FILTRE 4: Brillance
df = df[df['brightness'] >= MIN_BRIGHTNESS].copy()
print(f"   ✓ Brillance ≥ {MIN_BRIGHTNESS}K: {len(df)}/{initial}")

# Supprimer doublons (même position + même jour)
df['unique_key'] = df['latitude'].round(3).astype(str) + '_' + df['longitude'].round(3).astype(str) + '_' + df['acq_date'].astype(str)
before_dedup = len(df)
df = df.drop_duplicates(subset=['unique_key'], keep='first').copy()
print(f"   ✓ Doublons supprimés: {len(df)}/{before_dedup}")

if df.empty:
    print("\n" + "=" * 70)
    print("⚠️  AUCUNE DÉTECTION APRÈS FILTRAGE")
    print("=" * 70)
    print("\n💡 Essayez d'ajuster les filtres:")
    print(f"   • Réduire MIN_CONFIDENCE (actuel: {MIN_CONFIDENCE}%)")
    print(f"   • Réduire MIN_BRIGHTNESS (actuel: {MIN_BRIGHTNESS}K)")
    print(f"   • Élargir la zone géographique")
    sys.exit(1)

print(f"\n✅ {len(df)} détections valides après filtrage")

# Analyse par région
if not FILTER_BY_SPECIFIC_REGION:
    print(f"\n📍 Répartition par région:")
    for region, bounds in CHAD_REGIONS.items():
        count = len(df[
            (df['latitude'] >= bounds['min_lat']) &
            (df['latitude'] <= bounds['max_lat']) &
            (df['longitude'] >= bounds['min_lon']) &
            (df['longitude'] <= bounds['max_lon'])
        ])
        if count > 0:
            print(f"   • {region}: {count} détections")

# ==================== STATISTIQUES ====================
stats = {
    'total_detections': int(len(df)),
    'confidence_counts': {
        'Détections Haute Confiance': int((df['confidence'] > 79).sum()),
        'Détections Nominale Confiance': int(((df['confidence'] >= 30) & (df['confidence'] <= 79)).sum()),
        'Détections Basse Confiance': int((df['confidence'] < 30).sum()),
        'Détections Confiance Inconnue': 0
    },
    'satellite_counts': df['source'].value_counts().to_dict(),
    'recent_date_range': f"{df['acq_date'].max().strftime('%Y-%m-%d')} - {df['acq_date'].min().strftime('%Y-%m-%d')}"
}

# Liste détails
detail_list = []
for _, row in df.head(100).iterrows():
    detail_list.append({
        'date': row['acq_date'].strftime('%Y-%m-%d'),
        'time': row['acq_time'],
        'location': f"{row['latitude']:.2f}, {row['longitude']:.2f}",
        'confidence': str(int(row['confidence']))
    })

# Sauvegarder JSON
fire_data = {
    'stats': stats,
    'detailList': detail_list,
    'fireRecords': [],
    'filters': {
        'days': DAYS_TO_FETCH,
        'geographic_bounds': CHAD_BOUNDS if not FILTER_BY_SPECIFIC_REGION else SELECTED_REGIONS,
        'min_confidence': MIN_CONFIDENCE,
        'min_brightness': MIN_BRIGHTNESS,
        'sources': [s['name'] for s in sources],
        'last_update': datetime.now().isoformat()
    }
}

with open('fire_data.json', 'w', encoding='utf-8') as f:
    json.dump(fire_data, f, indent=2, ensure_ascii=False)
print(f"\n💾 fire_data.json sauvegardé")

# ==================== CARTE ====================
print(f"\n🗺️  Génération carte interactive...")

center_lat = df['latitude'].mean()
center_lon = df['longitude'].mean()

fire_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles='OpenStreetMap'
)

# Fonds de carte
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='🛰️ Satellite'
).add_to(fire_map)

folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB',
    name='🌙 Sombre'
).add_to(fire_map)

# Cluster
marker_cluster = MarkerCluster(name='🔥 Feux').add_to(fire_map)

# Heatmap
heat_data = [[row['latitude'], row['longitude'], row['confidence']/100] for _, row in df.iterrows()]
HeatMap(heat_data, name='🔥 Carte de chaleur', radius=15, blur=20, max_zoom=10).add_to(fire_map)

# Marqueurs
def get_color(conf):
    return '#ff0040' if conf > 79 else '#ff8c00' if conf >= 30 else '#00ff88'

for idx, row in df.iterrows():
    try:
        popup_html = create_cyberpunk_popup(
            date=row['acq_date'].strftime('%Y-%m-%d'),
            time=row['acq_time'],
            latitude=f"{row['latitude']:.4f}",
            longitude=f"{row['longitude']:.4f}",
            brightness=f"{row['brightness']:.1f} K",
            confidence=str(int(row['confidence'])),
            satellite=row['source'],
            brightness_raw=row['brightness']
        )
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=7,
            color=get_color(row['confidence']),
            fill=True,
            fillColor=get_color(row['confidence']),
            fillOpacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"🔥 {row['acq_date'].strftime('%m-%d')} | {int(row['confidence'])}% | {row['source']}"
        ).add_to(marker_cluster)
    except:
        continue

folium.LayerControl(position='topright', collapsed=False).add_to(fire_map)
fire_map.save('firms_tcd_map.html')
print("✅ firms_tcd_map.html généré")

# ==================== RÉSUMÉ ====================
print("\n" + "=" * 70)
print("✅ MISE À JOUR COMPLÈTE - DONNÉES API RÉELLES")
print("=" * 70)
print(f"\n📊 RÉSULTATS:")
print(f"   • Détections: {stats['total_detections']}")
print(f"   • Haute confiance: {stats['confidence_counts']['Détections Haute Confiance']}")
print(f"   • Nominale: {stats['confidence_counts']['Détections Nominale Confiance']}")
print(f"   • Sources: {', '.join(stats['satellite_counts'].keys())}")
print(f"   • Période: {stats['recent_date_range']}")
print(f"\n🌐 100% DONNÉES API - PAS DE DÉMO")
print("=" * 70)
