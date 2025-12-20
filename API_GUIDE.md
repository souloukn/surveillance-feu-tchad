# 🔥 Guide API FIRMS - Données Temps Réel

## ⚠️ SITUATION ACTUELLE

**Les 3 sources API (MODIS + VIIRS) retournent actuellement 0 détections.**

Cela signifie qu'il **n'y a AUCUN feu actif au Tchad** dans les 10 derniers jours.

---

## 🔑 Obtenir une VRAIE Clé API FIRMS

La clé actuelle (`bf5e35a4b23a40fdf6b1ce6ec90b8312`) est un placeholder.

### Étapes pour obtenir votre clé GRATUITE:

1. **Visitez:** https://nrt4.modaps.eosdis.nasa.gov/api/v2/content/get-apps

2. **Remplissez le formulaire:**
   - Nom
   - Email
   - Organisation
   - Raison d'utilisation: "Fire monitoring in Chad"

3. **Recevez votre clé par email** (instantané)

4. **Remplacez dans les scripts:**
   ```python
   FIRMS_API_KEY = "VOTRE_VRAIE_CLE_ICI"
   ```

---

## 📊 Scripts avec Filtres

### 1️⃣ `update_multi_source.py` - **RECOMMANDÉ**

**Caractéristiques:**
- ✅ 3 sources API (MODIS + VIIRS SNPP + VIIRS NOAA-20)
- ✅ Filtres temporels (jusqu'à 10 jours)
- ✅ Filtres géographiques (zones personnalisables)
- ✅ Filtres de qualité (confiance, brillance)
- ✅ Analyse par région
- ✅ Carte de chaleur (heatmap)
- ✅ Suppression doublons
- ❌ PAS de données démo

**Usage:**
```bash
python update_multi_source.py
```

### 2️⃣ `update_api_no_demo.py` - Simple

**Caractéristiques:**
- ✅ 1 source (MODIS seulement)
- ✅ Filtres temporels
- ✅ Filtres géographiques
- ✅ Rectangle de délimitation sur carte
- ❌ PAS de données démo

**Usage:**
```bash
python update_api_no_demo.py
```

---

## 🔧 Configuration des Filtres

### Dans `update_multi_source.py`:

```python
# FILTRE TEMPOREL (ligne 15)
DAYS_TO_FETCH = 10  # Maximum pour NRT: 10 jours

# FILTRE GÉOGRAPHIQUE COMPLET (ligne 18)
CHAD_BOUNDS = {
    'min_lat': 7.0,    # Sud
    'max_lat': 23.5,   # Nord
    'min_lon': 13.5,   # Ouest
    'max_lon': 24.0    # Est
}

# FILTRE PAR RÉGIONS SPÉCIFIQUES (ligne 33)
FILTER_BY_SPECIFIC_REGION = True  # Activez pour filtrer
SELECTED_REGIONS = ['Lac', 'Mayo-Kebbi']  # Régions à surveiller

# FILTRES DE QUALITÉ (ligne 37)
MIN_CONFIDENCE = 30     # Confiance minimum (0-100)
MIN_BRIGHTNESS = 300    # Brillance minimum (Kelvin)
```

### Régions Disponibles:

| Région | Latitude | Longitude |
|--------|----------|-----------|
| Lac | 12.5-14.5 | 13.5-15.5 |
| Kanem | 13.0-16.0 | 14.0-16.5 |
| Batha | 12.0-14.5 | 17.0-20.0 |
| Salamat | 9.5-12.0 | 19.5-22.0 |
| Mayo-Kebbi | 8.0-10.5 | 14.5-16.0 |
| Logone Oriental | 7.5-9.5 | 15.5-17.0 |

---

## 📡 Sources de Données API

### MODIS (Terra + Aqua)
- **Résolution:** 1km
- **Couverture:** 2 passages/jour
- **Meilleur pour:** Détection générale

### VIIRS SNPP
- **Résolution:** 375m
- **Couverture:** 1-2 passages/jour
- **Meilleur pour:** Petits feux

### VIIRS NOAA-20
- **Résolution:** 375m
- **Couverture:** 1-2 passages/jour
- **Meilleur pour:** Couverture complémentaire

---

## 🗺️ Sorties Générées

### `fire_data.json`
Statistiques et détails pour le dashboard:
```json
{
  "stats": {
    "total_detections": 0,
    "confidence_counts": {...},
    "satellite_counts": {...}
  },
  "filters": {
    "days": 10,
    "min_confidence": 30,
    "sources": ["MODIS", "VIIRS"]
  }
}
```

### `firms_tcd_map.html`
Carte interactive avec:
- 🔴 Marqueurs colorés par confiance
- 🗺️ Fonds de carte multiples
- 🔥 Heatmap (carte de chaleur)
- 📍 Clustering automatique
- 💬 Popups cyberpunk

---

## ⚙️ Exemples de Configuration

### Surveiller uniquement la région du Lac:
```python
FILTER_BY_SPECIFIC_REGION = True
SELECTED_REGIONS = ['Lac']
MIN_CONFIDENCE = 50  # Plus strict
```

### Détecter tous les feux (sensible):
```python
MIN_CONFIDENCE = 0
MIN_BRIGHTNESS = 280
DAYS_TO_FETCH = 10
```

### Focus haute confiance seulement:
```python
MIN_CONFIDENCE = 80
MIN_BRIGHTNESS = 350
```

---

## 🔄 Automatisation

### Mise à jour automatique toutes les heures (Windows):

**Créer `update_fires.bat`:**
```batch
@echo off
cd "C:\Users\UltraBook 3.1\Downloads\Feu_de_brousses"
python update_multi_source.py
git add fire_data.json firms_tcd_map.html
git commit -m "Auto-update: %date% %time%"
git push origin main
```

**Planifier avec Task Scheduler:**
1. Ouvrir "Planificateur de tâches"
2. Créer une tâche
3. Déclencheur: Toutes les heures
4. Action: `update_fires.bat`

### Linux/Mac (Cron):
```bash
0 * * * * cd /path/to/Feu_de_brousses && python update_multi_source.py && git add -A && git commit -m "Auto-update" && git push
```

---

## 🐛 Dépannage

### Problème: "AUCUNE DONNÉE DISPONIBLE"

**Solutions:**
1. ✅ Vérifiez votre clé API
2. ✅ Testez manuellement l'URL API dans le navigateur
3. ✅ Réduisez MIN_CONFIDENCE à 0
4. ✅ Attendez la saison des feux (nov-mai)

### Problème: "Timeout"

**Solutions:**
1. ✅ Augmentez le timeout (ligne avec `timeout=30`)
2. ✅ Vérifiez votre connexion internet
3. ✅ Utilisez un VPN si l'API est bloquée

### Problème: Trop de détections

**Solutions:**
1. ✅ Augmentez MIN_CONFIDENCE
2. ✅ Augmentez MIN_BRIGHTNESS
3. ✅ Réduisez DAYS_TO_FETCH
4. ✅ Activez FILTER_BY_SPECIFIC_REGION

---

## 📈 Interprétation des Résultats

### Confiance (Confidence):
- **> 80%:** 🔴 Haute - Feu quasi certain
- **30-79%:** 🟠 Nominale - Feu probable
- **< 30%:** 🟢 Basse - Feu possible

### Brillance (Brightness):
- **> 350K:** Feu intense
- **320-350K:** Feu modéré
- **300-320K:** Feu faible

### FRP (Fire Radiative Power):
- **> 100 MW:** Très intense
- **50-100 MW:** Intense
- **< 50 MW:** Faible

---

## 📞 Support

**Documentation FIRMS:**
https://firms.modaps.eosdis.nasa.gov/usfs/api/

**GitHub Issues:**
https://github.com/souloukn/surveillance-feu-tchad/issues

**Email Support NASA FIRMS:**
support@earthdata.nasa.gov

---

## ✅ Checklist Déploiement

- [ ] Obtenir clé API FIRMS
- [ ] Remplacer `FIRMS_API_KEY` dans les scripts
- [ ] Configurer les filtres selon vos besoins
- [ ] Tester `python update_multi_source.py`
- [ ] Vérifier `fire_data.json` et `firms_tcd_map.html`
- [ ] Git add/commit/push
- [ ] Attendre 2-5 min pour GitHub Pages
- [ ] Vérifier dashboard live
- [ ] (Optionnel) Configurer automatisation

---

**Dernière mise à jour:** 2025-12-20
