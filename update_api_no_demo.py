"""
API FIRMS with Time and Geographic Filters - NO DEMO DATA
Only uses real-time data from NASA FIRMS API
"""
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import io
import json
from popup_template import create_cyberpunk_popup
from datetime import datetime, timedelta
import sys

print("=" * 60)
print("🔥 SURVEILLANCE FEU TCHAD - API TEMPS RÉEL SEULEMENT")
print("=" * 60)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ==================== CONFIGURATION ====================

# NASA FIRMS API KEY
FIRMS_API_KEY = "bf5e35a4b23a40fdf6b1ce6ec90b8312"

# ==================== FILTRES TEMPORELS ====================
# Nombre de jours à récupérer (1-10 pour données temps réel)
DAYS_TO_FETCH = 7
print(f"\n⏰ FILTRE TEMPOREL: {DAYS_TO_FETCH} derniers jours")

# Date de début et fin pour affichage
end_date = datetime.now()
start_date = end_date - timedelta(days=DAYS_TO_FETCH)
print(f"   Du: {start_date.strftime('%Y-%m-%d')}")
print(f"   Au: {end_date.strftime('%Y-%m-%d')}")

# ==================== FILTRES GÉOGRAPHIQUES ====================
# Délimitation géographique du Tchad
CHAD_BOUNDS = {
    'min_lat': 7.0,    # Sud du Tchad
    'max_lat': 23.5,   # Nord du Tchad (Tibesti)
    'min_lon': 13.5,   # Ouest du Tchad
    'max_lon': 24.0    # Est du Tchad
}

print(f"\n🌍 FILTRE GÉOGRAPHIQUE:")
print(f"   Latitude:  {CHAD_BOUNDS['min_lat']}° à {CHAD_BOUNDS['max_lat']}°")
print(f"   Longitude: {CHAD_BOUNDS['min_lon']}° à {CHAD_BOUNDS['max_lon']}°")

# Régions spécifiques d'intérêt (optionnel)
# Décommentez pour filtrer par région
FILTER_BY_REGION = False  # Mettre True pour activer
REGIONS_OF_INTEREST = {
    "N'Djamena": {'lat': 12.1348, 'lon': 15.0557, 'radius_km': 100},
    "Lac": {'lat': 13.5, 'lon': 14.5, 'radius_km': 150},
    "Salamat": {'lat': 11.0, 'lon': 20.5, 'radius_km': 150},
    "Mayo-Kebbi": {'lat': 9.5, 'lon': 15.5, 'radius_km': 120},
}

if FILTER_BY_REGION:
    print(f"\n📍 RÉGIONS D'INTÉRÊT ACTIVÉES:")
    for region, coords in REGIONS_OF_INTEREST.items():
        print(f"   - {region}: Rayon {coords['radius_km']} km")

# Niveau de confiance minimum (0-100)
MIN_CONFIDENCE = 30  # Ignore les détections < 30% confiance
print(f"\n📊 FILTRE CONFIANCE: Minimum {MIN_CONFIDENCE}%")

# ==================== RÉCUPÉRATION API ====================
FIRMS_CSV_URL = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{FIRMS_API_KEY}/MODIS_NRT/TCD/{DAYS_TO_FETCH}"

print(f"\n📡 Connexion à NASA FIRMS API...")
print(f"   URL: {FIRMS_CSV_URL}")

df = pd.DataFrame()
api_success = False

for attempt in range(3):
    try:
        print(f"\n🔄 Tentative {attempt + 1}/3...")
        response = requests.get(FIRMS_CSV_URL, timeout=30)
        response.raise_for_status()
        
        if response.text.strip():
            df = pd.read_csv(io.StringIO(response.text))
            print(f"✅ SUCCÈS! {len(df)} détections brutes reçues de l'API")
            api_success = True
            break
        else:
            print("⚠️  API a retourné des données vides")
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout (30s dépassé)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {str(e)[:100]}")
    
    if attempt < 2:
        print("   ⏳ Nouvelle tentative dans 3 secondes...")
        import time
        time.sleep(3)

# Si l'API échoue, ARRÊTER (pas de fallback démo)
if not api_success or df.empty:
    print("\n" + "=" * 60)
    print("❌ ÉCHEC: Impossible de récupérer les données de l'API")
    print("=" * 60)
    print("\n💡 Solutions possibles:")
    print("   1. Vérifiez votre connexion Internet")
    print("   2. Vérifiez que la clé API est valide:")
    print("      https://nrt4.modaps.eosdis.nasa.gov/api")
    print("   3. L'API FIRMS peut être temporairement indisponible")
    print("   4. Il n'y a peut-être aucun feu au Tchad actuellement")
    print("\n🚫 AUCUNE DONNÉE DE DÉMO UTILISÉE")
    sys.exit(1)

# ==================== NETTOYAGE ET FILTRAGE ====================
print(f"\n🔧 Application des filtres...")

# Conversion des types
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['brightness'] = pd.to_numeric(df['brightness'], errors='coerce')
df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
df['acq_date'] = pd.to_datetime(df['acq_date'], errors='coerce')

initial_count = len(df)

# FILTRE 1: Coordonnées valides
df = df.dropna(subset=['latitude', 'longitude']).copy()
print(f"   ✓ Coordonnées valides: {len(df)}/{initial_count}")

# FILTRE 2: Délimitation géographique
df = df[
    (df['latitude'] >= CHAD_BOUNDS['min_lat']) &
    (df['latitude'] <= CHAD_BOUNDS['max_lat']) &
    (df['longitude'] >= CHAD_BOUNDS['min_lon']) &
    (df['longitude'] <= CHAD_BOUNDS['max_lon'])
].copy()
print(f"   ✓ Dans délimitation Tchad: {len(df)}/{initial_count}")

# FILTRE 3: Confiance minimum
if 'confidence' in df.columns:
    df = df[df['confidence'] >= MIN_CONFIDENCE].copy()
    print(f"   ✓ Confiance ≥ {MIN_CONFIDENCE}%: {len(df)}/{initial_count}")

# FILTRE 4: Régions spécifiques (si activé)
if FILTER_BY_REGION and len(df) > 0:
    def is_in_region(lat, lon):
        from math import radians, cos, sin, sqrt, atan2
        for region, coords in REGIONS_OF_INTEREST.items():
            R = 6371  # Rayon Terre en km
            lat1, lon1 = radians(coords['lat']), radians(coords['lon'])
            lat2, lon2 = radians(lat), radians(lon)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            if distance <= coords['radius_km']:
                return True
        return False
    
    df = df[df.apply(lambda row: is_in_region(row['latitude'], row['longitude']), axis=1)].copy()
    print(f"   ✓ Dans régions d'intérêt: {len(df)}/{initial_count}")

# Vérifier s'il reste des données après filtrage
if df.empty:
    print("\n" + "=" * 60)
    print("⚠️  AUCUNE DÉTECTION après application des filtres")
    print("=" * 60)
    print("\n📊 Filtres appliqués:")
    print(f"   - Période: {DAYS_TO_FETCH} jours")
    print(f"   - Zone géographique: {CHAD_BOUNDS}")
    print(f"   - Confiance minimum: {MIN_CONFIDENCE}%")
    if FILTER_BY_REGION:
        print(f"   - Régions spécifiques: {list(REGIONS_OF_INTEREST.keys())}")
    print("\n💡 Suggestions:")
    print("   - Augmentez DAYS_TO_FETCH (max 10)")
    print("   - Réduisez MIN_CONFIDENCE")
    print("   - Désactivez le filtre par région")
    print("   - Élargissez CHAD_BOUNDS")
    sys.exit(1)

print(f"\n✅ {len(df)} détections valides après filtrage")

# ==================== STATISTIQUES ====================
print(f"\n📊 Calcul des statistiques...")

stats = {
    'total_detections': int(len(df)),
    'confidence_counts': {
        'Détections Haute Confiance': int((df['confidence'] > 79).sum()),
        'Détections Nominale Confiance': int(((df['confidence'] >= 30) & (df['confidence'] <= 79)).sum()),
        'Détections Basse Confiance': int((df['confidence'] < 30).sum()),
        'Détections Confiance Inconnue': 0
    },
    'satellite_counts': df['satellite'].value_counts().to_dict() if 'satellite' in df.columns else {},
    'recent_date_range': f"{df['acq_date'].max().strftime('%Y-%m-%d')} - {df['acq_date'].min().strftime('%Y-%m-%d')}"
}

# Détails pour le dashboard
detail_list = []
for _, row in df.head(100).iterrows():
    detail_list.append({
        'date': row['acq_date'].strftime('%Y-%m-%d'),
        'time': str(row.get('acq_time', '0000')).zfill(4),
        'location': f"{row['latitude']:.2f}, {row['longitude']:.2f}",
        'confidence': str(int(row['confidence']))
    })

# Sauvegarder fire_data.json
print(f"\n💾 Sauvegarde fire_data.json...")
fire_data = {
    'stats': stats,
    'detailList': detail_list,
    'fireRecords': [],
    'filters': {
        'days': DAYS_TO_FETCH,
        'geographic_bounds': CHAD_BOUNDS,
        'min_confidence': MIN_CONFIDENCE,
        'regions_filter_active': FILTER_BY_REGION,
        'last_update': datetime.now().isoformat()
    }
}

with open('fire_data.json', 'w', encoding='utf-8') as f:
    json.dump(fire_data, f, indent=2, ensure_ascii=False)
print("✅ fire_data.json mis à jour")

# ==================== GÉNÉRATION CARTE ====================
print(f"\n🗺️  Création de la carte interactive...")

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
    name='🛰️ Satellite',
    overlay=False
).add_to(fire_map)

folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB',
    name='🌙 Mode Sombre',
    overlay=False
).add_to(fire_map)

# Cluster de marqueurs
marker_cluster = MarkerCluster(name='🔥 Détections Feux').add_to(fire_map)

# Fonction couleur
def get_color(conf):
    return '#ff0040' if conf > 79 else '#ff8c00' if conf >= 30 else '#00ff88'

# Ajouter les marqueurs
print(f"📍 Ajout de {len(df)} marqueurs...")
for idx, row in df.iterrows():
    try:
        popup_html = create_cyberpunk_popup(
            date=row['acq_date'].strftime('%Y-%m-%d'),
            time=str(row.get('acq_time', '0000')).zfill(4),
            latitude=f"{row['latitude']:.4f}",
            longitude=f"{row['longitude']:.4f}",
            brightness=f"{row.get('brightness', 0):.1f} K",
            confidence=str(int(row['confidence'])),
            satellite=row.get('satellite', 'MODIS'),
            brightness_raw=row.get('brightness', 0)
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
            tooltip=f"🔥 {row['acq_date'].strftime('%Y-%m-%d')} | Conf: {int(row['confidence'])}%"
        ).add_to(marker_cluster)
    except Exception as e:
        continue

# Ajouter rectangle de délimitation
if not FILTER_BY_REGION:
    folium.Rectangle(
        bounds=[
            [CHAD_BOUNDS['min_lat'], CHAD_BOUNDS['min_lon']],
            [CHAD_BOUNDS['max_lat'], CHAD_BOUNDS['max_lon']]
        ],
        color='#00ffff',
        fill=False,
        weight=2,
        opacity=0.5,
        popup='Zone de surveillance Tchad'
    ).add_to(fire_map)

# Contrôle des couches
folium.LayerControl(position='topright', collapsed=False).add_to(fire_map)

# Sauvegarder
fire_map.save('firms_tcd_map.html')
print("✅ firms_tcd_map.html généré")

# ==================== RÉSUMÉ ====================
print("\n" + "=" * 60)
print("✅ MISE À JOUR TERMINÉE - DONNÉES API RÉELLES UNIQUEMENT")
print("=" * 60)
print(f"\n📊 STATISTIQUES:")
print(f"   • Total détections: {stats['total_detections']}")
print(f"   • Haute confiance: {stats['confidence_counts']['Détections Haute Confiance']}")
print(f"   • Confiance nominale: {stats['confidence_counts']['Détections Nominale Confiance']}")
print(f"   • Basse confiance: {stats['confidence_counts']['Détections Basse Confiance']}")
print(f"   • Satellites: {', '.join(stats['satellite_counts'].keys())}")
print(f"   • Période: {stats['recent_date_range']}")

print(f"\n🔧 FILTRES APPLIQUÉS:")
print(f"   • Temporel: {DAYS_TO_FETCH} jours")
print(f"   • Géographique: Lat {CHAD_BOUNDS['min_lat']}-{CHAD_BOUNDS['max_lat']}, Lon {CHAD_BOUNDS['min_lon']}-{CHAD_BOUNDS['max_lon']}")
print(f"   • Confiance: ≥ {MIN_CONFIDENCE}%")
print(f"   • Régions spécifiques: {'Activé' if FILTER_BY_REGION else 'Désactivé'}")

print(f"\n🌐 SOURCE: NASA FIRMS API (temps réel)")
print(f"🚫 AUCUNE DONNÉE DE DÉMO UTILISÉE")
print(f"\n🗺️  Ouvrez dashboard.html pour voir la carte")
print("=" * 60)
