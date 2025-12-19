# Convert SHP files to GeoJSON
import geopandas as gpd
import json
import os

print("Converting Chad administrative boundaries from SHP to GeoJSON...")

# Files to convert
shp_files = {
    'TCD_adm0.shp': 'chad_country.geojson',      # Country boundary
    'TCD_adm1.shp': 'chad_provinces.geojson',    # Provinces (23)
    'TCD_adm2.shp': 'chad_departments.geojson',  # Départements
    'TCD_adm3.shp': 'chad_communes.geojson'      # Communes
}

for shp_file, geojson_file in shp_files.items():
    if os.path.exists(shp_file):
        print(f"\n  Converting {shp_file} → {geojson_file}...")
        try:
            # Read shapefile
            gdf = gpd.read_file(shp_file)
            
            # Convert to WGS84 (EPSG:4326) if needed
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                print(f"    Reprojecting from {gdf.crs} to EPSG:4326...")
                gdf = gdf.to_crs(epsg=4326)
            
            # Save as GeoJSON
            gdf.to_file(geojson_file, driver='GeoJSON')
            
            print(f"    ✅ Created {geojson_file}")
            print(f"    📊 Features: {len(gdf)}")
            if 'NAME_1' in gdf.columns:
                print(f"    🏛️ Provinces: {', '.join(gdf['NAME_1'].head(5).tolist())}...")
            elif 'NAME_2' in gdf.columns:
                print(f"    🏘️ Départements: {len(gdf)} total")
            elif 'NAME_3' in gdf.columns:
                print(f"    🏡 Communes: {len(gdf)} total")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    else:
        print(f"  ⚠️ File not found: {shp_file}")

print("\n✅ Conversion complete!")
print("\nGeoJSON files created:")
for geojson_file in shp_files.values():
    if os.path.exists(geojson_file):
        size = os.path.getsize(geojson_file) / 1024
        print(f"  - {geojson_file} ({size:.1f} KB)")
