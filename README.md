# 🔥 Surveillance Feu Tchad - Dashboard Cyberpunk

Tableau de bord en temps réel pour la surveillance des feux de brousse au Tchad avec interface cyberpunk.

## 🚀 Déploiement Live

**Dashboard:** [https://souloukn.github.io/surveillance-feu-tchad/dashboard.html](https://souloukn.github.io/surveillance-feu-tchad/dashboard.html)

## ✨ Fonctionnalités

- 🎨 **Interface Cyberpunk** - Design neon cyan/pink/purple avec effets glassmorphism
- 🔢 **Compteurs Animés** - Animation progressive avec son synchronisé (Web Audio API)
- 📊 **Graphiques** - Distribution de confiance (doughnut) et détections par satellite (barres)
- 🔮 **Prédictions** - Tendance 24h et niveau de risque de propagation
- 🗺️ **Carte Interactive** - Marqueurs de feu avec popups cyberpunk améliorés
- 📱 **Responsive** - Design adaptatif mobile avec sidebar toggle
- 🇫🇷 **Interface Française** - 100% en français

## 🗺️ Problème Résolu: Carte avec Feux

### Si la carte n'affiche pas les feux:

1. **Régénérer la carte avec les données de démo:**
   ```bash
   python generate_demo_data.py
   python generate_map_from_demo.py
   ```

2. **Recharger la page** - La carte `firms_tcd_map.html` sera mise à jour

### Structure de la Carte:
- **Marqueurs colorés** par niveau de confiance:
  - 🔴 Rouge: Haute confiance (>79)
  - 🟠 Orange: Confiance nominale (30-79)
  - 🟢 Vert: Basse confiance (<30)
- **Clustering** automatique pour performance
- **Popups cyberpunk** avec glassmorphism et animations
- **Fonds de carte multiples**: Satellite, OpenStreetMap, Dark Mode

## ☁️ Options Météo (Optionnel)

### Activation de la Météo:

1. **Obtenir une clé API gratuite:**
   - Visitez [OpenWeatherMap](https://openweathermap.org/api)
   - Créez un compte gratuit
   - Copiez votre clé API

2. **Configurer:**
   ```python
   # Dans weather_config.py
   OPENWEATHER_API_KEY = "VOTRE_CLE_API_ICI"
   WEATHER_ENABLED = True
   ```

3. **Régénérer les données:**
   ```bash
   python generate_demo_data.py
   ```

### Fonctionnalités Météo:
- 🌡️ Température en temps réel
- 💧 Humidité
- 💨 Vitesse du vent
- 🌧️ Précipitations
- ⚠️ Alertes conditions dangereuses (temp élevée, humidité basse)

## 🎵 Son du Compteur

### Deux Options:

**Option 1: Web Audio API (Par Défaut)**
- Beep synthétique (800Hz, 50ms)
- Fonctionne sans fichier
- Activé automatiquement

**Option 2: Fichier Audio Personnalisé**
```bash
# Ajoutez un fichier audio dans le dossier:
son.mp3  # ou son.wav, son.ogg
```

## 📦 Installation Locale

```bash
# Cloner le repository
git clone https://github.com/souloukn/surveillance-feu-tchad.git
cd surveillance-feu-tchad

# Installer les dépendances
pip install -r requirements.txt

# Générer les données de démo
python generate_demo_data.py

# Générer la carte
python generate_map_from_demo.py

# Ouvrir le dashboard
# Double-cliquez sur dashboard.html
```

## 🔄 Mise à Jour des Données

### Avec Données de Démo:
```bash
python generate_demo_data.py
python generate_map_from_demo.py
```

### Avec API FIRMS (Données Réelles):
```bash
# Éditer generate_firms_dashboard.py
FIRMS_API_KEY = "VOTRE_CLE_FIRMS"

# Générer
python generate_firms_dashboard.py
```

## 🛠️ Structure du Projet

```
surveillance-feu-tchad/
├── dashboard.html          # Dashboard principal avec compteurs animés
├── style.css              # Styles cyberpunk
├── fire_data.js           # Données et scripts du dashboard
├── fire_data.json         # Données JSON
├── firms_tcd_map.html     # Carte Folium interactive
├── popup_template.py      # Templates popups cyberpunk
├── generate_demo_data.py  # Générateur données de démo
├── generate_map_from_demo.py  # Générateur carte depuis démo
├── generate_firms_dashboard.py  # Générateur avec API FIRMS
├── weather_config.py      # Configuration météo (optionnel)
└── requirements.txt       # Dépendances Python
```

## 🎨 Personnalisation

### Couleurs:
```css
/* Dans style.css */
:root {
    --neon-cyan: #00ffff;
    --neon-pink: #ff00ff;
    --neon-purple: #9d00ff;
}
```

### Animation du Compteur:
```javascript
// Dans dashboard.html
animateCounter(element, targetValue, 2500, true);
//                                    ↑     ↑
//                              durée(ms)  son activé
```

## 📊 Données

**Source:** NASA FIRMS (Fire Information for Resource Management System)
- **Satellites:** MODIS (Terra & Aqua)
- **Fréquence:** Temps quasi-réel
- **Couverture:** Tchad (TCD)

## 🐛 Dépannage

### La carte est vide:
```bash
python generate_map_from_demo.py
```

### Le son ne fonctionne pas:
- Normal: Les navigateurs bloquent l'autoplay audio
- Cliquez n'importe où sur la page pour activer
- Web Audio API génère automatiquement un beep

### Les graphiques ne s'affichent pas:
- Vérifiez la console: F12 → Console
- Rechargez la page (Ctrl+F5)
- Vérifiez que Chart.js est chargé

## 📝 Licence

MIT License - Libre d'utilisation

## 🤝 Contribution

Les contributions sont les bienvenues!

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m '✨ Nouvelle fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## 📧 Contact

Pour questions ou support: [GitHub Issues](https://github.com/souloukn/surveillance-feu-tchad/issues)

---

**Développé avec ❤️ pour la surveillance des feux de brousse au Tchad**