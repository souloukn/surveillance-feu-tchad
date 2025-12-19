# 🔥 Système de Surveillance des Feux de Brousse - Tchad

Application avancée de détection et surveillance des feux de brousse au Tchad utilisant les données NASA FIRMS en temps réel.

## 🌟 Fonctionnalités

### 📊 Dashboard Interactif
- **Carte interactive** avec marqueurs animés en forme de flamme
- **Visualisation en temps réel** des feux actifs
- **Interface ultra-moderne** style Qoder avec glassmorphism

### ☁️ Intégration Météo
- **Données météo en temps réel** (OpenWeatherMap API)
- **4 métriques clés** : Température, Humidité, Vent, Pression
- **Calcul du risque d'incendie** basé sur les conditions météo

### 🗺️ Limites Administratives
- **Provinces du Tchad** (23 régions)
- **Départements** (55 divisions)
- **Communes** (348 localités)
- **Données GeoJSON** officielles

### 📈 Graphiques et Analyses
- **Graphiques animés** : Luminosité, Confiance, Risque
- **Barres de progression** avec gradients dynamiques
- **Graphique circulaire SVG** pour le score de risque global

### 🎯 Système d'Alerte
- **5 niveaux de risque** : Critique, Très Élevé, Élevé, Modéré, Faible
- **Score intelligent** combinant météo et données satellitaires
- **Popups détaillés** avec scroll pour chaque feu

## 🚀 Installation

### Prérequis
- Python 3.9+
- pip

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/souloukn/surveillance-feu-tchad.git
cd surveillance-feu-tchad
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer l'API OpenWeatherMap**
- Obtenir une clé API gratuite sur [OpenWeatherMap](https://openweathermap.org/api)
- La clé est déjà configurée dans `generate_map_animated.py` (ligne 156)

## 💻 Utilisation

### Générer des données de démonstration
```bash
python generate_demo_data.py
```

### Générer la carte interactive
```bash
python generate_map_animated.py
```

### Ouvrir le dashboard
```bash
start firms_tcd_map.html
# ou
start dashboard.html
```

## 📁 Structure du Projet

```
surveillance-feu-tchad/
├── generate_map_animated.py      # Script principal de génération de carte
├── generate_demo_data.py         # Générateur de données de test
├── popup_template.py             # Template des popups modernes
├── convert_shp_to_geojson.py    # Conversion SHP → GeoJSON
├── dashboard.html                # Dashboard HTML principal
├── fire_data.js                  # Logique JavaScript
├── style.css                     # Styles CSS modernes
├── fire_data.json               # Données des feux (généré)
├── firms_tcd_map.html           # Carte interactive (généré)
├── chad_provinces.geojson       # Limites des provinces
├── chad_departments.geojson     # Limites des départements
├── chad_communes.geojson        # Limites des communes
└── charts/                      # Graphiques matplotlib
```

## 🎨 Captures d'écran

### Carte Interactive
- Marqueurs animés en forme de flamme 🔥
- Design moderne avec effets glassmorphism
- Navigation fluide et responsive

### Popup Détaillé
- Header avec niveau d'intensité
- Score de risque global
- Données météo en temps réel
- Graphiques animés
- Localisation administrative précise

## 🔧 Technologies Utilisées

- **Python** : Backend et traitement de données
- **Folium** : Cartographie interactive
- **OpenWeatherMap API** : Données météo
- **NASA FIRMS** : Données satellitaires sur les feux
- **GeoPandas** : Traitement des données géospatiales
- **Shapely** : Opérations géométriques
- **Scikit-learn** : Clustering DBSCAN (optionnel)
- **HTML/CSS/JavaScript** : Interface utilisateur

## 📊 Sources de Données

- **NASA FIRMS** : Fire Information for Resource Management System
- **OpenWeatherMap** : Données météorologiques
- **OpenStreetMap** : Limites administratives

## 🎯 Algorithme de Calcul du Risque

Le score de risque (0-100) est calculé selon :

```python
Score = Température + Humidité + Vent + Luminosité + Confiance

Facteurs :
- Température >40°C    → +35 points
- Humidité <20%        → +30 points
- Vent >15 m/s         → +25 points
- Luminosité >400K     → +10 points
- Confiance >90%       → +5 points
```

**Niveaux** :
- 🔴 **CRITIQUE** (≥80)
- 🟠 **TRÈS ÉLEVÉ** (≥60)
- 🟡 **ÉLEVÉ** (≥40)
- 🟢 **MODÉRÉ** (≥20)
- ✅ **FAIBLE** (<20)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `license.txt` pour plus de détails.

## 👤 Auteur

**souloukn**
- GitHub: [@souloukn](https://github.com/souloukn)

## 🙏 Remerciements

- NASA FIRMS pour les données satellitaires
- OpenWeatherMap pour les données météo
- OpenStreetMap pour les données géographiques
- La communauté open-source Python

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

**Développé avec ❤️ pour la surveillance environnementale au Tchad**
