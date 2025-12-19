# generate_firms_dashboard.py
import requests
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import io
import sys
import json
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime

# --- Configuration ---
# IMPORTANT: Replace with your actual FIRMS API Key or load from config/environment
# **SECURITY WARNING**: Storing API keys directly in code is NOT recommended for production.
# Consider using environment variables (e.g., os.environ.get('FIRMS_API_KEY'))
# or a dedicated configuration file.
FIRMS_API_KEY = "bf5e35a4b23a40fdf6b1ce6ec90b8312" # <-- REMPLACEZ PAR VOTRE CLÉ API VALIDE

if FIRMS_API_KEY == "bf5e35a4b23a40fdf6b1ce6ec90b8312":
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!! WARNING: You are using the placeholder API key.")
    print("!! Please replace 'bf5e35a4b23a40fdf6b1ce6ec90b8312' with your actual")
    print("!! NASA FIRMS API key from https://nrt4.modaps.eosdis.nasa.gov/api")
    print("!! before deploying or sharing this code.")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

# Using 7 days for potentially more data
# MODIS: Good balance of spatial resolution and coverage.
FIRMS_CSV_URL_MODIS = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{FIRMS_API_KEY}/MODIS_NRT/TCD/7"
# VIIRS: Higher spatial resolution, better for smaller fires, but narrower swath.
# FIRMS_CSV_URL_VIIRS = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{FIRMS_API_KEY}/VIIRS_SNPP_NRT/TCD/7"
# Using MODIS by default, uncomment the line below to use VIIRS instead
# FIRMS_CSV_URL = FIRMS_CSV_URL_VIIRS
FIRMS_CSV_URL = FIRMS_CSV_URL_MODIS # Defaulting to MODIS as in the original code

OUTPUT_MAP_FILE = "firms_tcd_map.html"
OUTPUT_CHART_DIR = "charts"
OUTPUT_DATA_JSON_FILE = "fire_data.json" # New output file for JSON data

# Define crucial columns and their expected dtypes for initial validation/handling
CRUCIAL_COLS_DTYPES = {
    'latitude': float,
    'longitude': float,
    'acq_date': object, # Read as object initially, convert to datetime later
    'acq_time': object, # Read as object initially, convert to string later
    'brightness': float,
    'confidence': object, # Can be mixed types, read as object, convert numeric/string later
    'satellite': object
}
REQUIRED_FOR_ROW = ['latitude', 'longitude', 'acq_date'] # Columns essential for a valid record


# --- Ensure output directories exist ---
print(f"Ensuring directory '{OUTPUT_CHART_DIR}' exists.")
try:
    os.makedirs(OUTPUT_CHART_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating directory '{OUTPUT_CHART_DIR}': {e}")
    # For charts, maybe just warn, but map and JSON are critical.
    pass # Continue execution


# --- Fetch Data ---
print(f"Fetching data from: {FIRMS_CSV_URL}")
response = None
try:
    response = requests.get(FIRMS_CSV_URL, timeout=15) # Added timeout
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    print(f"Data fetched successfully (Status: {response.status_code}).")

    if not response.text.strip():
         print("Fetched data is empty.")
         response = None # Treat as failed fetch if content is empty

except requests.exceptions.Timeout:
    print(f"Error fetching data: Request timed out after 15 seconds.")
    print("Please check your internet connection, FIRMS API key, and URL.")
    response = None
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    print("Please check your internet connection, FIRMS API key, and URL.")
    response = None # Ensure response is None on error

# --- Load Data into Pandas DataFrame ---
df = pd.DataFrame() # Initialize df as empty by default

if response and response.status_code == 200:
    try:
        data = io.StringIO(response.text)
        df = pd.read_csv(data)
        print(f"Successfully read CSV. Initial DataFrame shape: {df.shape}")

        # --- Initial Data Validation & Cleaning: Ensure Crucial Columns ---
        for col, dtype in CRUCIAL_COLS_DTYPES.items():
             if col not in df.columns:
                 print(f"Warning: Crucial column '{col}' not found in data. Adding with default values.")
                 if dtype == float:
                     df[col] = np.nan
                 elif col == 'acq_date':
                      df[col] = pd.NaT
                 else:
                     df[col] = ''

        # --- Data Cleaning/Preparation (Apply if df is not empty) ---
        if not df.empty:
             print("Starting data cleaning and preparation...")
             # Convert essential columns to appropriate types, coercing errors
             df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
             df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
             df['acq_date'] = pd.to_datetime(df['acq_date'], errors='coerce')
             df['brightness'] = pd.to_numeric(df['brightness'], errors='coerce')

             def format_acq_time_robust(time_val):
                 if pd.isna(time_val) or str(time_val).strip() == '': return ''
                 try: return str(int(float(time_val))).zfill(4)
                 except (ValueError, TypeError):
                     print(f"Warning: Could not parse acquisition time '{time_val}' as numeric. Treating as missing.")
                     return ''
             df['acq_time'] = df['acq_time'].apply(format_acq_time_robust).fillna('').astype(str)

             if 'confidence' in df.columns:
                 df['confidence_str'] = df['confidence'].astype(str).str.strip().replace('nan', 'unknown').replace('', 'unknown')
                 df['confidence_numeric'] = pd.to_numeric(df['confidence'], errors='coerce')
             else:
                 df['confidence_str'] = 'unknown'
                 df['confidence_numeric'] = np.nan

             if 'satellite' in df.columns:
                  df['satellite'] = df['satellite'].astype(str).str.strip().replace('nan', 'unknown_sat').replace('', 'unknown_sat').fillna('unknown_sat')
             else:
                  df['satellite'] = 'unknown_sat'

             initial_row_count = len(df)
             required_cols_present = [col for col in REQUIRED_FOR_ROW if col in df.columns]
             if required_cols_present:
                df = df.dropna(subset=required_cols_present).copy()
                if len(df) < initial_row_count:
                     print(f"Dropped {initial_row_count - len(df)} rows missing essential data ({', '.join(required_cols_present)}).")
             else:
                 print("Warning: Essential columns for rows are missing. Dropping all rows as invalid.")
                 df = pd.DataFrame()

        if df.empty:
            print("DataFrame is empty after reading and cleaning (no valid fire detections with lat/lon/date).")
        else:
            print(f"{len(df)} valid fire records loaded and cleaned.")

    except pd.errors.EmptyDataError:
        print("CSV data is empty (no fire detections reported).")
        df = pd.DataFrame()
    except Exception as e:
        print(f"Error processing CSV data after fetch: {e}")
        print("Check if the CSV format is as expected or if the API returned an unexpected response.")
        df = pd.DataFrame()
else:
    print("Skipping CSV processing due to failed data fetch or empty response.")


# --- Calculate Statistics for Stats Panel ---
print("Calculating statistics for dashboard...")
dashboard_stats = {
    'total_detections': 0,
    'confidence_counts': {
        'Détections Haute Confiance': 0,
        'Détections Nominale Confiance': 0,
        'Détections Basse Confiance': 0,
        'Détections Confiance Inconnue': 0
        },
    'satellite_counts': {},
    'recent_date_range': 'N/A'
}

if not df.empty:
    dashboard_stats['total_detections'] = int(len(df))

    if 'confidence_numeric' in df.columns and not df['confidence_numeric'].dropna().empty:
         df_confidence_numeric = df['confidence_numeric'].dropna()
         dashboard_stats['confidence_counts']['Détections Haute Confiance'] = int((df_confidence_numeric > 79).sum())
         dashboard_stats['confidence_counts']['Détections Nominale Confiance'] = int(((df_confidence_numeric >= 30) & (df_confidence_numeric <= 79)).sum())
         dashboard_stats['confidence_counts']['Détections Basse Confiance'] = int((df_confidence_numeric < 30).sum())

    if 'confidence_str' in df.columns:
         dashboard_stats['confidence_counts']['Détections Confiance Inconnue'] = int(df['confidence_str'].value_counts().get('unknown', 0))

    if 'satellite' in df.columns and not df['satellite'].dropna().empty:
         satellite_counts_raw = df['satellite'].value_counts()
         dashboard_stats['satellite_counts'] = {k: int(v) for k, v in satellite_counts_raw.items()}

    if 'acq_date' in df.columns and not df['acq_date'].dropna().empty:
        min_date = df['acq_date'].dropna().min()
        max_date = df['acq_date'].dropna().max()
        if pd.notna(min_date) and pd.notna(max_date):
            dashboard_stats['recent_date_range'] = f"{max_date.strftime('%Y-%m-%d')} - {min_date.strftime('%Y-%m-%d')}"

print("Statistics calculation complete.")


# --- Format Data for Detail List Panel (Optional) ---
print("Formatting data for detail list (optional structure)...")
detail_list_data = []
if not df.empty and all(col in df.columns for col in ['acq_date', 'acq_time', 'latitude', 'longitude', 'confidence_str']):
    detail_cols_to_select = ['acq_date', 'acq_time', 'latitude', 'longitude', 'confidence_str']
    df_list = df[detail_cols_to_select].dropna(subset=['acq_date', 'latitude', 'longitude']).copy()

    if not df_list.empty:
        df_list['acq_date_str'] = df_list['acq_date'].dt.strftime('%Y-%m-%d').fillna('N/A')
        df_list['acq_time_str'] = df_list['acq_time'].astype(str).replace('nan', '').replace('', '0000').str.zfill(4)
        df_list['sort_time'] = pd.to_datetime(df_list['acq_date_str'] + df_list['acq_time_str'], format='%Y-%m-%d%H%M', errors='coerce')
        df_list = df_list.dropna(subset=['sort_time']).sort_values(by='sort_time', ascending=False).copy()

        for _, row in df_list.iterrows():
            date_str = row['acq_date'].strftime('%Y-%m-%d') if pd.notna(row['acq_date']) else 'N/A'
            time_str = str(row['acq_time']).strip() if pd.notna(row['acq_time']) and str(row['acq_time']).strip() != '' else 'N/A'
            lat_lon_str = f"{row['latitude']:.2f}, {row['longitude']:.2f}" if pd.notna(row['latitude']) and pd.notna(row['longitude']) else 'N/A'
            confidence_str = row.get('confidence_str', 'N/A')

            detail_list_data.append({
                'date': date_str, 'time': time_str, 'location': lat_lon_str, 'confidence': confidence_str
            })
else:
    print("DataFrame is empty or missing essential columns for detail list. Detail list data will be empty.")


# --- Calculate Map Center ---
print("Calculating map center...")
center_lat, center_lon = 15.45, 19.17 # Default for Chad
if not df.empty and 'latitude' in df.columns and 'longitude' in df.columns:
    valid_lat, valid_lon = df['latitude'].dropna(), df['longitude'].dropna()
    if not valid_lat.empty and not valid_lon.empty:
        center_lat, center_lon = valid_lat.median(), valid_lon.median()
        print(f"Calculated map center from data: Lat={center_lat:.2f}, Lon={center_lon:.2f}")
    else:
        print(f"No valid latitude/longitude data found for centering. Using default center: Lat={center_lat}, Lon={center_lon}")
else:
    print(f"DataFrame is empty or missing latitude/longitude columns. Using default center: Lat={center_lat}, Lon={center_lon}")


# --- Map Generation (Folium) ---
print("Generating map...")
folium_map = folium.Map(
    location=[center_lat, center_lon], zoom_start=6,
    tiles='Esri World Imagery', attr='Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    control_scale=True
)
folium.TileLayer('OpenStreetMap', name='OpenStreetMap', attr='© OpenStreetMap contributors').add_to(folium_map)
folium.TileLayer('CartoDB darkmatter', name='Carte Fond Sombre', show=False, attr='© CartoDB').add_to(folium_map)
STAMEN_ATTRIBUTION = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
folium.TileLayer('Stamen Toner', name='Stamen Toner', show=False, attr=STAMEN_ATTRIBUTION).add_to(folium_map)

# Create separate feature groups for different visualizations
marker_cluster = MarkerCluster(name='Points de Détection')
marker_cluster.add_to(folium_map)

# Feature group for fire polygons
fire_polygons_group = folium.FeatureGroup(name='Zones de Feu (Polygones)', show=True)
fire_polygons_group.add_to(folium_map)

essential_marker_cols = ['latitude', 'longitude', 'acq_date', 'brightness', 'confidence_numeric', 'confidence_str', 'satellite']
# Corrected Syntax Error: Removed the extra closing parenthesis
if not df.empty and all(col in df.columns for col in essential_marker_cols):
    df_markers = df.dropna(subset=essential_marker_cols).copy()
    if not df_markers.empty:
        print(f"Adding {len(df_markers)} markers to map cluster...")
        def get_marker_style(confidence_numeric_value, brightness_value):
            color = 'gray'
            if pd.notna(confidence_numeric_value):
                if confidence_numeric_value > 79: color = 'red'
                elif confidence_numeric_value >= 30: color = 'orange'
                else: color = 'cyan'
            radius = 3
            if pd.notna(brightness_value):
                if brightness_value > 400: radius = 8
                elif brightness_value > 380: radius = 6
                elif brightness_value > 350: radius = 4
            return {'color': color, 'fillColor': color, 'fillOpacity': 0.7, 'radius': radius, 'weight': 1}

        cols_for_tuples = ['latitude', 'longitude', 'confidence_numeric', 'brightness', 'acq_date', 'acq_time', 'confidence_str', 'satellite']
        cols_for_tuples_present = [col for col in cols_for_tuples if col in df_markers.columns]

        for row in df_markers[cols_for_tuples_present].itertuples(index=False):
            row_dict = row._asdict()
            latitude, longitude = row_dict.get('latitude'), row_dict.get('longitude')
            confidence_numeric_value, brightness_value = row_dict.get('confidence_numeric'), row_dict.get('brightness')

            if pd.isna(latitude) or pd.isna(longitude): continue

            style = get_marker_style(confidence_numeric_value, brightness_value)

            date_str_popup = row_dict.get('acq_date', pd.NaT).strftime('%Y-%m-%d') if pd.notna(row_dict.get('acq_date', pd.NaT)) else 'N/A'
            time_str_popup = str(row_dict.get('acq_time', '')).strip() if pd.notna(row_dict.get('acq_time', '')) and str(row_dict.get('acq_time', '')).strip() != '' else 'N/A'
            lat_popup = f"{latitude:.2f} °N" if pd.notna(latitude) else 'N/A'
            lon_popup = f"{longitude:.2f} °E" if pd.notna(longitude) else 'N/A'
            brightness_popup = f"{brightness_value:.1f} K" if pd.notna(brightness_value) else 'N/A'
            confidence_str_popup = row_dict.get('confidence_str', 'N/A')
            satellite_popup = row_dict.get('satellite', 'N/A')

            popup_html = f"""
            <b>Date:</b> {date_str_popup}<br><b>Heure:</b> {time_str_popup}<br>
            <b>Latitude:</b> {lat_popup}<br><b>Longitude:</b> {lon_popup}<br>
            <b>Luminosité:</b> {brightness_popup}<br><b>Confiance:</b> {confidence_str_popup}<br>
            <b>Satellite:</b> {satellite_popup}
            """
            folium.CircleMarker(
                location=[latitude, longitude],
                radius=style['radius'], color=style['color'], fill=True, fill_color=style['fillColor'],
                fill_opacity=style['fillOpacity'], weight=style['weight'],
                popup=folium.Popup(popup_html, max_width=300), tooltip=f"Feu: {date_str_popup} {time_str_popup}"
            ).add_to(marker_cluster)
    else: print("No valid data rows for map markers after cleaning.")
else: print("DataFrame is empty or missing essential columns for markers. Skipping adding markers to the map.")

# --- Generate Fire Polygons (Heat Zones) ---
print("Generating fire polygons...")
if not df.empty and all(col in df.columns for col in ['latitude', 'longitude', 'brightness', 'confidence_numeric']):
    df_polygons = df.dropna(subset=['latitude', 'longitude', 'brightness']).copy()
    
    if not df_polygons.empty:
        print(f"Creating polygons for {len(df_polygons)} fire detections...")
        
        # Group nearby fires into clusters for polygon creation
        from sklearn.cluster import DBSCAN
        import numpy as np
        
        # Prepare coordinates for clustering
        coords = df_polygons[['latitude', 'longitude']].values
        
        # DBSCAN clustering (eps in degrees, ~5km = 0.05 degrees)
        clustering = DBSCAN(eps=0.05, min_samples=2).fit(coords)
        df_polygons['cluster'] = clustering.labels_
        
        # Create polygons for each cluster
        for cluster_id in df_polygons['cluster'].unique():
            if cluster_id == -1:  # Skip noise points
                continue
            
            cluster_fires = df_polygons[df_polygons['cluster'] == cluster_id]
            
            if len(cluster_fires) < 3:  # Need at least 3 points for a polygon
                continue
            
            # Get cluster statistics
            avg_brightness = cluster_fires['brightness'].mean()
            max_brightness = cluster_fires['brightness'].max()
            fire_count = len(cluster_fires)
            avg_confidence = cluster_fires['confidence_numeric'].mean()
            
            # Create convex hull around fire points
            from scipy.spatial import ConvexHull
            points = cluster_fires[['latitude', 'longitude']].values
            
            try:
                hull = ConvexHull(points)
                hull_points = points[hull.vertices]
                
                # Add buffer to polygon (expand slightly)
                center_lat = hull_points[:, 0].mean()
                center_lon = hull_points[:, 1].mean()
                buffer_factor = 1.2  # 20% expansion
                
                buffered_points = []
                for point in hull_points:
                    lat_diff = (point[0] - center_lat) * buffer_factor
                    lon_diff = (point[1] - center_lon) * buffer_factor
                    buffered_points.append([center_lat + lat_diff, center_lon + lon_diff])
                
                # Determine polygon color and opacity based on fire intensity
                if avg_brightness > 400 or avg_confidence > 90:
                    color = '#FF0000'  # Red for very high intensity
                    fill_opacity = 0.4
                elif avg_brightness > 350 or avg_confidence > 70:
                    color = '#FF6600'  # Orange for high intensity
                    fill_opacity = 0.35
                else:
                    color = '#FFAA00'  # Yellow for moderate intensity
                    fill_opacity = 0.3
                
                # Create popup information
                popup_html = f"""
                <div style="font-family: Arial; min-width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #ff6600;">Zone de Feu - Cluster #{cluster_id + 1}</h4>
                    <b>🔥 Nombre de feux:</b> {fire_count}<br>
                    <b>🌡️ Luminosité moyenne:</b> {avg_brightness:.1f} K<br>
                    <b>🔥 Luminosité max:</b> {max_brightness:.1f} K<br>
                    <b>🎯 Confiance moyenne:</b> {avg_confidence:.0f}%<br>
                    <b>📍 Zone:</b> ~{len(hull_points)} points
                </div>
                """
                
                # Add polygon to map
                folium.Polygon(
                    locations=buffered_points,
                    color=color,
                    weight=2,
                    fill=True,
                    fill_color=color,
                    fill_opacity=fill_opacity,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"Zone de feu: {fire_count} détections"
                ).add_to(fire_polygons_group)
                
                # Add a center marker for the cluster
                folium.CircleMarker(
                    location=[center_lat, center_lon],
                    radius=8,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    weight=2,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"Centre: {fire_count} feux"
                ).add_to(fire_polygons_group)
                
            except Exception as e:
                print(f"Warning: Could not create polygon for cluster {cluster_id}: {e}")
                continue
        
        print(f"Created polygons for fire clusters.")
    else:
        print("No valid fire data for polygon creation.")
else:
    print("Insufficient data for polygon generation.")

folium.LayerControl(position='topright').add_to(folium_map)

try: folium_map.save(OUTPUT_MAP_FILE); print(f"Map saved to {OUTPUT_MAP_FILE}")
except Exception as e: print(f"Error saving map file {OUTPUT_MAP_FILE}: {e}")

# --- Chart Generation (Matplotlib) ---
print("Generating charts...")
plt.style.use('dark_background')
chart_colors = {
    'primary': '#ff0000', 'confidence_high': '#ff0000', 'confidence_nominal': '#ffcc00',
    'confidence_low': '#00ffff', 'confidence_unknown': '#555555', 'satellite_accent': '#00bcd4',
    'neutral': '#444444', 'text': 'white'
}
plt.rcParams.update({
    'text.color': chart_colors['text'], 'axes.labelcolor': chart_colors['text'],
    'xtick.color': chart_colors['text'], 'ytick.color': chart_colors['text'],
    'axes.edgecolor': chart_colors['text'], 'figure.facecolor': '#282828',
    'axes.facecolor': '#282828', 'figure.autolayout': True
})

output_chart1_path = os.path.join(OUTPUT_CHART_DIR, 'fires_per_day.png')
print(f"Generating chart: {output_chart1_path}")
plt.figure(figsize=(10, 6))
if not df.empty and 'acq_date' in df.columns and not df['acq_date'].dropna().empty:
    fires_per_day = df['acq_date'].dropna().dt.date.value_counts().sort_index()
    if not fires_per_day.empty:
        fires_per_day.plot(kind='bar', color=chart_colors['primary'], ax=plt.gca())
        plt.title('Nombre de Détections par Jour')
        plt.xlabel('Date')
        plt.ylabel('Nombre de Détections')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7, color=chart_colors['neutral'])
        dates = fires_per_day.index
        if len(dates) > 0: plt.gca().set_xticks(range(len(dates))); plt.gca().set_xticklabels([date.strftime('%Y-%m-%d') for date in dates])
    else: plt.text(0.5, 0.5, "Pas de données de date disponibles", horizontalalignment='center', verticalalignment='center', fontsize=14, color=chart_colors['text'], transform=plt.gca().transAxes); plt.title('Nombre de Détections par Jour'); plt.axis('off')
else: plt.text(0.5, 0.5, "Pas de données disponibles", horizontalalignment='center', verticalalignment='center', fontsize=14, color=chart_colors['text'], transform=plt.gca().transAxes); plt.title('Nombre de Détections par Jour'); plt.axis('off')
try: plt.savefig(output_chart1_path, bbox_inches='tight', transparent=True); print(f"Saved chart: {output_chart1_path}")
except Exception as e: print(f"Error saving chart {output_chart1_path}: {e}")
plt.close()

output_chart2_path = os.path.join(OUTPUT_CHART_DIR, 'confidence_distribution.png')
print(f"Generating chart: {output_chart2_path}")
plt.figure(figsize=(8, 8))
confidence_counts = dashboard_stats['confidence_counts']
filtered_counts = {label: count for label, count in confidence_counts.items() if count > 0}
if filtered_counts:
    labels, sizes = filtered_counts.keys(), filtered_counts.values()
    pie_colors_map = {
        'Détections Haute Confiance': chart_colors['confidence_high'], 'Détections Nominale Confiance': chart_colors['confidence_nominal'],
        'Détections Basse Confiance': chart_colors['confidence_low'], 'Détections Confiance Inconnue': chart_colors['confidence_unknown']
    }
    pie_colors = [pie_colors_map.get(label, chart_colors['neutral']) for label in labels]
    if sizes:
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=pie_colors, textprops={'color': chart_colors['text'], 'fontsize': 10}, wedgeprops={'edgecolor': '#282828'})
        plt.ylabel(''); plt.title('Distribution de la Confiance des Détections'); plt.axis('equal')
    else: plt.text(0.5, 0.5, "Aucune détection avec confiance > 0", horizontalalignment='center', verticalalignment='center', fontsize=14, color=chart_colors['text'], transform=plt.gca().transAxes); plt.title('Distribution de la Confiance des Détections'); plt.axis('off')
else: plt.text(0.5, 0.5, "Pas de données disponibles", horizontalalignment='center', verticalalignment='center', fontsize=14, color=chart_colors['text'], transform=plt.gca().transAxes); plt.title('Distribution de la Confiance des Détections'); plt.axis('off')
try: plt.savefig(output_chart2_path, bbox_inches='tight', transparent=True); print(f"Saved chart: {output_chart2_path}")
except Exception as e: print(f"Error saving chart {output_chart2_path}: {e}")
plt.close()

output_chart3_path = os.path.join(OUTPUT_CHART_DIR, 'fires_per_satellite.png')
print(f"Generating chart: {output_chart3_path}")
plt.figure(figsize=(10, 6))
if not df.empty and 'satellite' in df.columns and not df['satellite'].dropna().empty:
    satellite_counts = df['satellite'].value_counts().sort_index()
    if not satellite_counts.empty:
        satellite_counts.plot(kind='bar', color=chart_colors['satellite_accent'], ax=plt.gca())
        plt.title('Nombre de Détections par Satellite')
        plt.xlabel('Satellite'); plt.ylabel('Nombre de Détections'); plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.7, color=chart_colors['neutral']); plt.ylim(0, satellite_counts.max() * 1.1)
    else: plt.text(0.5, 0.5, "Aucune détection avec satellite identifié", horizontalalignment='center', verticalalignment='center', fontsize=14, color=chart_colors['text'], transform=plt.gca().transAxes); plt.title('Nombre de Détections par Satellite'); plt.axis('off')
else: plt.text(0.5, 0.5, "Pas de données disponibles", horizontalalignment='center', verticalalignment='center', fontsize=14, color=chart_colors['text'], transform=plt.gca().transAxes); plt.title('Nombre de Détections par Satellite'); plt.axis('off')
try: plt.savefig(output_chart3_path, bbox_inches='tight', transparent=True); print(f"Saved chart: {output_chart3_path}")
except Exception as e: print(f"Error saving chart {output_chart3_path}: {e}")
plt.close()

plt.style.use('default')

# --- Prepare Data for JSON file ---
print(f"Preparing data for JSON file: {OUTPUT_DATA_JSON_FILE}")

JS_TABLE_COLUMNS = [
    {'name': 'acq_date', 'label': 'Date', 'type': 'date'},
    {'name': 'acq_time', 'label': 'Heure', 'type': 'string'},
    {'name': 'latitude', 'label': 'Latitude', 'type': 'string'},
    {'name': 'longitude', 'label': 'Longitude', 'type': 'string'},
    {'name': 'brightness', 'label': 'Luminosité', 'type': 'html'}, # This will contain HTML for the emoji
    {'name': 'confidence_str', 'label': 'Confiance', 'type': 'string'}, # Use string version
    {'name': 'satellite', 'label': 'Satellite', 'type': 'string'},
]

js_records = []
if not df.empty:
    print(f"Processing {len(df)} rows for JSON data...")
    cols_to_process_for_js = [col_info['name'] for col_info in JS_TABLE_COLUMNS]
    # Ensure these columns exist before subsetting
    df_for_js = df[[col for col in cols_to_process_for_js if col in df.columns]].copy()

    if not df_for_js.empty:
        for row in df_for_js.itertuples(index=False):
            row_dict = row._asdict()
            formatted_row = []
            for col_info in JS_TABLE_COLUMNS:
                col_name = col_info['name']
                cell_value = row_dict.get(col_name, None)
                formatted_cell = '-' # Default placeholder

                if col_name == 'acq_date':
                     if pd.notna(cell_value):
                         try: formatted_cell = cell_value.strftime('%Y-%m-%d')
                         except Exception: formatted_cell = '-'
                elif col_name == 'acq_time':
                     if pd.notna(cell_value) and str(cell_value).strip() != '': formatted_cell = str(cell_value).strip()
                     else: formatted_cell = '-'
                elif col_name == 'latitude':
                     if pd.notna(cell_value): formatted_cell = f"{cell_value:.4f}"
                     else: formatted_cell = '-'
                elif col_name == 'longitude':
                     if pd.notna(cell_value): formatted_cell = f"{cell_value:.4f}"
                     else: formatted_cell = '-'
                elif col_name == 'brightness':
                     brightness_value = cell_value if pd.notna(cell_value) else np.nan
                     brightness_display_str = f"{brightness_value:.1f} K" if pd.notna(brightness_value) else '-'
                     # Add HTML span with data-brightness for JS styling
                     if pd.notna(brightness_value): formatted_cell = f"{brightness_display_str} <span class='fire-emoji' data-brightness='{brightness_value}'>🔥</span>"
                     else: formatted_cell = '-' # Just '-' if brightness is NaN
                elif col_name == 'confidence_str':
                     if pd.notna(cell_value) and str(cell_value).strip() != '': formatted_cell = str(cell_value).strip()
                     else: formatted_cell = '-'
                elif col_name == 'satellite':
                     if pd.notna(cell_value) and str(cell_value).strip() != '': formatted_cell = str(cell_value).strip()
                     else: formatted_cell = '-'

                formatted_row.append(formatted_cell)
            js_records.append(formatted_row)
        print(f"Formatted {len(js_records)} records for the JSON data.")
        if js_records: print("Sample of first record for JSON:", js_records[0])
    else: print("DataFrame is not empty, but no rows remain after selecting and processing required columns for JSON data.")
else: print("DataFrame is empty. JSON records will be empty.")


# Combine ALL data into a single structure for the JSON file
dashboard_data_json = {
    'stats': dashboard_stats,
    'detailList': detail_list_data, # Optional: Kept but not used by default frontend
    'fireRecords': js_records # Data for simple-datatables
}

# --- Write JSON File ---
print(f"Writing JSON data file: {OUTPUT_DATA_JSON_FILE}")
try:
    with open(OUTPUT_DATA_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(dashboard_data_json, f, indent=4, allow_nan=False)
    print(f"JSON data file saved to {OUTPUT_DATA_JSON_FILE}")
except TypeError as e:
    print(f"Error serializing data to JSON: {e}")
    print("Please check the data in dashboard_data_json for types that cannot be serialized to JSON (e.g., sets, complex objects) or unhandled NaN/Infinity values in numeric columns.")
except Exception as e:
    print(f"Error writing JSON data file {OUTPUT_DATA_JSON_FILE}: {e}")

# --- Script Execution Instructions ---
# To run this script, save it as a .py file (e.g., generate_firms_dashboard.py)
# Make sure you have the required libraries installed:
# pip install pandas requests folium matplotlib numpy
# Then run from your terminal:
# python generate_firms_dashboard.py
# This will generate: firms_tcd_map.html, charts/*.png, and fire_data.json
#
# You will also need an index.html file that includes:
# 1. The Simple-DataTables library (JS and CSS)
# 2. A structure with divs/sections matching the CSS/JS selectors (#left-sidebar, #interactive-map-section, #stats-section, #filter-section, #data-table-section, #fire-table, buttons, date inputs, .auto-refresh-indicator, #refresh-countdown, .header-subtitle, etc.)
# 3. A static JavaScript file (e.g., dashboard.js) that FETCHES fire_data.json
# 4. Include the Simple-DataTables JS and your static dashboard.js file in index.html