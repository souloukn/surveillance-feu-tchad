# Script to generate realistic demo fire data for Chad
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

print("Generating realistic demo fire data for Chad...")

# Set random seed for reproducibility
np.random.seed(42)

# Define realistic regions in Chad where fires occur
regions = [
    {'name': 'Salamat', 'lat': 11.5, 'lon': 22.4, 'fires': 25},
    {'name': 'Moyen-Chari', 'lat': 10.3, 'lon': 20.8, 'fires': 35},
    {'name': 'Mandoul', 'lat': 12.8, 'lon': 19.1, 'fires': 20},
    {'name': 'Logone Oriental', 'lat': 9.2, 'lon': 16.5, 'fires': 18},
    {'name': 'Chari-Baguirmi', 'lat': 11.0, 'lon': 15.3, 'fires': 15},
]

all_fires = []

# Generate fires for each region
for region in regions:
    num_fires = region['fires']
    
    # Generate random positions around region center
    lats = np.random.normal(region['lat'], 0.3, num_fires)
    lons = np.random.normal(region['lon'], 0.3, num_fires)
    
    # Generate realistic brightness values (in Kelvin)
    brightness = np.random.uniform(310, 420, num_fires)
    
    # Generate confidence values
    confidence = np.random.uniform(30, 100, num_fires)
    
    # Generate dates (last 7 days)
    base_date = datetime.now()
    dates = [base_date - timedelta(days=np.random.randint(0, 7)) for _ in range(num_fires)]
    
    # Generate times (HHMM format)
    times = [f"{np.random.randint(0, 24):02d}{np.random.randint(0, 60):02d}" for _ in range(num_fires)]
    
    # Random satellites
    satellites = np.random.choice(['Terra', 'Aqua'], num_fires)
    
    for i in range(num_fires):
        all_fires.append({
            'latitude': lats[i],
            'longitude': lons[i],
            'brightness': brightness[i],
            'confidence': confidence[i],
            'acq_date': dates[i].strftime('%Y-%m-%d'),
            'acq_time': times[i],
            'satellite': satellites[i],
            'region': region['name']
        })

# Create DataFrame
df = pd.DataFrame(all_fires)
df = df.sort_values(by='acq_date', ascending=False).reset_index(drop=True)

print(f"Generated {len(df)} fire detections across {len(regions)} regions")

# Calculate statistics
dashboard_stats = {
    'total_detections': len(df),
    'confidence_counts': {
        'Détections Haute Confiance': int((df['confidence'] > 79).sum()),
        'Détections Nominale Confiance': int(((df['confidence'] >= 30) & (df['confidence'] <= 79)).sum()),
        'Détections Basse Confiance': int((df['confidence'] < 30).sum()),
        'Détections Confiance Inconnue': 0
    },
    'satellite_counts': df['satellite'].value_counts().to_dict(),
    'recent_date_range': f"{df['acq_date'].max()} - {df['acq_date'].min()}"
}

# Format detail list
detail_list = []
for _, row in df.head(50).iterrows():  # Top 50 recent
    detail_list.append({
        'date': row['acq_date'],
        'time': row['acq_time'],
        'location': f"{row['latitude']:.2f}, {row['longitude']:.2f}",
        'confidence': str(int(row['confidence']))
    })

# Format fire records for table
fire_records = []
for _, row in df.iterrows():
    fire_records.append([
        row['acq_date'],
        row['acq_time'],
        f"{row['latitude']:.4f}",
        f"{row['longitude']:.4f}",
        f"{row['brightness']:.1f} K <span class='fire-emoji' data-brightness='{row['brightness']:.2f}'>🔥</span>",
        str(int(row['confidence'])),
        row['satellite']
    ])

# Create dashboard data structure
dashboard_data = {
    'stats': dashboard_stats,
    'detailList': detail_list,
    'fireRecords': fire_records
}

# Save to JSON
output_file = 'fire_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=4, ensure_ascii=False)

print(f"✅ Demo data saved to {output_file}")
print(f"\n📊 Statistics:")
print(f"   - Total fires: {dashboard_stats['total_detections']}")
print(f"   - High confidence: {dashboard_stats['confidence_counts']['Détections Haute Confiance']}")
print(f"   - Nominal confidence: {dashboard_stats['confidence_counts']['Détections Nominale Confiance']}")
print(f"   - Low confidence: {dashboard_stats['confidence_counts']['Détections Basse Confiance']}")
print(f"   - Date range: {dashboard_stats['recent_date_range']}")
print(f"\n🗺️ Now run: python generate_firms_dashboard.py")
print("   Or simply open dashboard.html to see the demo data!")
