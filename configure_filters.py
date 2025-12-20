"""
Configuration Interactive des Filtres API FIRMS
"""
import json
import os

print("=" * 70)
print("⚙️  CONFIGURATION FILTRES API FIRMS")
print("=" * 70)

config = {}

# API KEY
print("\n🔑 CLÉ API NASA FIRMS")
print("Obtenez votre clé gratuite: https://nrt4.modaps.eosdis.nasa.gov/api")
current_key = "bf5e35a4b23a40fdf6b1ce6ec90b8312"
print(f"Clé actuelle: {current_key}")
new_key = input("Nouvelle clé (Entrée pour garder actuelle): ").strip()
config['api_key'] = new_key if new_key else current_key

# FILTRE TEMPOREL
print("\n⏰ FILTRE TEMPOREL")
print("Nombre de jours à récupérer (1-10 pour données temps réel)")
days = input("Jours [7]: ").strip()
config['days'] = int(days) if days.isdigit() and 1 <= int(days) <= 10 else 7

# FILTRE GÉOGRAPHIQUE
print("\n🌍 FILTRE GÉOGRAPHIQUE")
print("1. Tchad complet")
print("2. Régions spécifiques")
geo_choice = input("Choix [1]: ").strip()

if geo_choice == "2":
    config['use_regions'] = True
    print("\nRégions disponibles:")
    regions = {
        '1': 'Lac',
        '2': 'Kanem',
        '3': 'Batha',
        '4': 'Salamat',
        '5': 'Mayo-Kebbi',
        '6': 'Logone Oriental'
    }
    for key, region in regions.items():
        print(f"  {key}. {region}")
    
    selected = input("Régions (ex: 1,2,4) [1]: ").strip()
    if selected:
        config['regions'] = [regions[r.strip()] for r in selected.split(',') if r.strip() in regions]
    else:
        config['regions'] = ['Lac']
else:
    config['use_regions'] = False
    config['regions'] = []

# FILTRE CONFIANCE
print("\n📊 FILTRE CONFIANCE")
print("Confiance minimum (0-100)")
print("  0-30: Basse | 30-79: Nominale | 80+: Haute")
conf = input("Confiance minimum [30]: ").strip()
config['min_confidence'] = int(conf) if conf.isdigit() and 0 <= int(conf) <= 100 else 30

# FILTRE BRILLANCE
print("\n🔥 FILTRE BRILLANCE")
print("Brillance minimum en Kelvin (280-400)")
bright = input("Brillance minimum [300]: ").strip()
config['min_brightness'] = int(bright) if bright.isdigit() else 300

# SOURCES
print("\n📡 SOURCES DE DONNÉES")
print("1. MODIS uniquement (rapide)")
print("2. MODIS + VIIRS (complet, recommandé)")
source_choice = input("Choix [2]: ").strip()
config['multi_source'] = source_choice != "1"

# Sauvegarder config
with open('filters_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n✅ Configuration sauvegardée dans filters_config.json")
print("\n📋 RÉSUMÉ:")
print(f"   • API Key: {config['api_key'][:20]}...")
print(f"   • Période: {config['days']} jours")
print(f"   • Zone: {'Régions ' + str(config['regions']) if config['use_regions'] else 'Tchad complet'}")
print(f"   • Confiance min: {config['min_confidence']}%")
print(f"   • Brillance min: {config['min_brightness']}K")
print(f"   • Sources: {'MODIS + VIIRS' if config['multi_source'] else 'MODIS seulement'}")

print("\n🚀 Lancez maintenant:")
if config['multi_source']:
    print("   python update_multi_source.py")
else:
    print("   python update_api_no_demo.py")

print("\n💡 Pour modifier, relancez: python configure_filters.py")
