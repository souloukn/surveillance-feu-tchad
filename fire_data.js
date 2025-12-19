// ========== ADVANCED FEATURES ==========
// 1. Real-time Alert System
const alertSystem = {
    highConfidenceThreshold: 80,
    soundEnabled: true,
    lastAlertTime: null,
    alertCooldown: 60000, // 1 minute between alerts
    newFiresDetected: [],
    
    playAlertSound() {
        if (!this.soundEnabled) return;
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    },
    
    showAlert(fireCount, highConfCount) {
        const now = Date.now();
        if (this.lastAlertTime && (now - this.lastAlertTime) < this.alertCooldown) return;
        
        this.playAlertSound();
        this.lastAlertTime = now;
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'fire-alert';
        alertDiv.innerHTML = `
            <div class="alert-content">
                <span class="alert-icon">🔥</span>
                <div class="alert-text">
                    <strong>ALERTE : Nouveaux feux détectés !</strong>
                    <p>${fireCount} nouveaux feu(x) dont ${highConfCount} haute confiance</p>
                </div>
                <button class="alert-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        document.body.appendChild(alertDiv);
        
        setTimeout(() => alertDiv.classList.add('show'), 10);
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
    },
    
    checkForNewFires(fireRecords) {
        const highConfFires = fireRecords.filter(record => {
            const confidence = parseInt(record[5]);
            return !isNaN(confidence) && confidence >= this.highConfidenceThreshold;
        });
        
        if (highConfFires.length > 0) {
            this.showAlert(fireRecords.length, highConfFires.length);
        }
    }
};

// 2. Weather Data Integration (OpenWeatherMap)
const weatherSystem = {
    apiKey: '93001eb223da7a2e6159542cf220c81c', // OpenWeatherMap API Key
    weatherData: {},
    
    async fetchWeather(lat, lon) {
        if (this.apiKey === 'YOUR_OPENWEATHERMAP_API_KEY') {
            console.warn('Please configure OpenWeatherMap API key');
            return null;
        }
        
        try {
            const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${this.apiKey}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Weather API error');
            return await response.json();
        } catch (error) {
            console.error('Error fetching weather:', error);
            return null;
        }
    },
    
    async updateWeatherPanel(centerLat, centerLon) {
        const weather = await this.fetchWeather(centerLat, centerLon);
        if (!weather) return;
        
        this.weatherData = {
            temp: weather.main.temp,
            humidity: weather.main.humidity,
            windSpeed: weather.wind.speed,
            description: weather.weather[0].description
        };
        
        this.displayWeather();
    },
    
    displayWeather() {
        const weatherSection = document.getElementById('weather-section');
        if (!weatherSection) return;
        
        const riskLevel = this.calculateFireRisk();
        weatherSection.querySelector('.section-content').innerHTML = `
            <div class="weather-grid">
                <div class="weather-item">
                    <span class="weather-label">Température:</span>
                    <span class="weather-value">${this.weatherData.temp.toFixed(1)}°C</span>
                </div>
                <div class="weather-item">
                    <span class="weather-label">Humidité:</span>
                    <span class="weather-value">${this.weatherData.humidity}%</span>
                </div>
                <div class="weather-item">
                    <span class="weather-label">Vent:</span>
                    <span class="weather-value">${this.weatherData.windSpeed.toFixed(1)} m/s</span>
                </div>
                <div class="weather-item">
                    <span class="weather-label">Conditions:</span>
                    <span class="weather-value">${this.weatherData.description}</span>
                </div>
                <div class="fire-risk-indicator risk-${riskLevel.level}">
                    <strong>Risque d'incendie:</strong> ${riskLevel.text}
                </div>
            </div>
        `;
    },
    
    calculateFireRisk() {
        const { temp, humidity, windSpeed } = this.weatherData;
        let score = 0;
        
        if (temp > 35) score += 3;
        else if (temp > 30) score += 2;
        else if (temp > 25) score += 1;
        
        if (humidity < 20) score += 3;
        else if (humidity < 40) score += 2;
        else if (humidity < 60) score += 1;
        
        if (windSpeed > 10) score += 3;
        else if (windSpeed > 5) score += 2;
        else if (windSpeed > 2) score += 1;
        
        if (score >= 7) return { level: 'high', text: 'ÉLEVÉ' };
        if (score >= 4) return { level: 'medium', text: 'MOYEN' };
        return { level: 'low', text: 'FAIBLE' };
    }
};

// 3. Predictive Analysis Module
const predictiveAnalysis = {
    historicalData: [],
    predictions: [],
    
    analyzePatterns(fireRecords) {
        const dateGroups = {};
        
        fireRecords.forEach(record => {
            const date = record[0];
            if (!dateGroups[date]) dateGroups[date] = [];
            dateGroups[date].push({
                lat: parseFloat(record[2]),
                lon: parseFloat(record[3]),
                brightness: parseFloat(record[4].match(/[\d.]+/)[0]),
                confidence: parseInt(record[5])
            });
        });
        
        this.historicalData = dateGroups;
        this.generatePredictions();
    },
    
    generatePredictions() {
        const hotspots = this.identifyHotspots();
        this.predictions = hotspots.map(spot => ({
            lat: spot.lat,
            lon: spot.lon,
            riskScore: spot.score,
            fireCount: spot.count
        }));
        
        this.displayPredictions();
    },
    
    identifyHotspots() {
        const clusters = [];
        const allFires = [];
        
        Object.values(this.historicalData).forEach(dayFires => {
            allFires.push(...dayFires);
        });
        
        const gridSize = 0.5; // degrees
        const grid = {};
        
        allFires.forEach(fire => {
            const gridKey = `${Math.floor(fire.lat / gridSize)}_${Math.floor(fire.lon / gridSize)}`;
            if (!grid[gridKey]) {
                grid[gridKey] = { fires: [], totalBrightness: 0, count: 0 };
            }
            grid[gridKey].fires.push(fire);
            grid[gridKey].totalBrightness += fire.brightness;
            grid[gridKey].count++;
        });
        
        Object.entries(grid).forEach(([key, data]) => {
            if (data.count >= 3) {
                const avgLat = data.fires.reduce((sum, f) => sum + f.lat, 0) / data.count;
                const avgLon = data.fires.reduce((sum, f) => sum + f.lon, 0) / data.count;
                const score = (data.count * data.totalBrightness) / 1000;
                
                clusters.push({ lat: avgLat, lon: avgLon, count: data.count, score });
            }
        });
        
        return clusters.sort((a, b) => b.score - a.score).slice(0, 10);
    },
    
    displayPredictions() {
        const predSection = document.getElementById('prediction-section');
        if (!predSection) return;
        
        let html = '<div class="prediction-list">';
        this.predictions.forEach((pred, index) => {
            const riskClass = pred.riskScore > 50 ? 'high' : pred.riskScore > 20 ? 'medium' : 'low';
            html += `
                <div class="prediction-item risk-${riskClass}">
                    <span class="pred-rank">#${index + 1}</span>
                    <span class="pred-location">${pred.lat.toFixed(2)}°N, ${pred.lon.toFixed(2)}°E</span>
                    <span class="pred-fires">${pred.fireCount} feux</span>
                    <span class="pred-risk">Risque: ${pred.riskScore.toFixed(0)}</span>
                </div>
            `;
        });
        html += '</div>';
        
        predSection.querySelector('.section-content').innerHTML = html;
    }
};

// 4. Historical Dashboard Module
const historicalDashboard = {
    storedData: [],
    comparisonPeriod: 7, // days
    
    initialize() {
        this.loadStoredData();
        this.setupEventListeners();
    },
    
    loadStoredData() {
        const stored = localStorage.getItem('fireHistory');
        if (stored) {
            try {
                this.storedData = JSON.parse(stored);
            } catch (e) {
                console.error('Error loading historical data:', e);
                this.storedData = [];
            }
        }
    },
    
    saveCurrentData(stats, fireRecords) {
        const entry = {
            timestamp: new Date().toISOString(),
            date: new Date().toLocaleDateString(),
            stats: stats,
            fireCount: fireRecords.length
        };
        
        this.storedData.push(entry);
        
        // Keep only last 30 days
        const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
        this.storedData = this.storedData.filter(entry => 
            new Date(entry.timestamp).getTime() > thirtyDaysAgo
        );
        
        localStorage.setItem('fireHistory', JSON.stringify(this.storedData));
    },
    
    generateComparison() {
        if (this.storedData.length < 2) return null;
        
        const recent = this.storedData.slice(-7);
        const previous = this.storedData.slice(-14, -7);
        
        const recentAvg = recent.reduce((sum, d) => sum + d.fireCount, 0) / recent.length;
        const prevAvg = previous.length > 0 ? 
            previous.reduce((sum, d) => sum + d.fireCount, 0) / previous.length : recentAvg;
        
        const change = ((recentAvg - prevAvg) / prevAvg) * 100;
        
        return {
            recentAvg: recentAvg.toFixed(1),
            previousAvg: prevAvg.toFixed(1),
            changePercent: change.toFixed(1),
            trend: change > 0 ? 'up' : 'down'
        };
    },
    
    displayComparison() {
        const histSection = document.getElementById('historical-section');
        if (!histSection) return;
        
        const comparison = this.generateComparison();
        if (!comparison) {
            histSection.querySelector('.section-content').innerHTML = 
                '<p>Données insuffisantes pour comparaison (minimum 2 jours requis)</p>';
            return;
        }
        
        const trendIcon = comparison.trend === 'up' ? '📈' : '📉';
        const trendClass = comparison.trend === 'up' ? 'trend-up' : 'trend-down';
        
        histSection.querySelector('.section-content').innerHTML = `
            <div class="historical-comparison">
                <div class="comparison-item">
                    <span class="comp-label">7 derniers jours:</span>
                    <span class="comp-value">${comparison.recentAvg} feux/jour</span>
                </div>
                <div class="comparison-item">
                    <span class="comp-label">7 jours précédents:</span>
                    <span class="comp-value">${comparison.previousAvg} feux/jour</span>
                </div>
                <div class="comparison-trend ${trendClass}">
                    ${trendIcon} <strong>${Math.abs(comparison.changePercent)}%</strong> 
                    ${comparison.trend === 'up' ? 'augmentation' : 'diminution'}
                </div>
                <div class="data-count">
                    ${this.storedData.length} jours de données stockées
                </div>
            </div>
        `;
    },
    
    setupEventListeners() {
        const clearBtn = document.getElementById('clear-history-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (confirm('Effacer tout l\'historique ?')) {
                    this.storedData = [];
                    localStorage.removeItem('fireHistory');
                    this.displayComparison();
                }
            });
        }
    }
};

// 5. Custom Zones of Interest
const zonesOfInterest = {
    zones: [],
    drawingMode: false,
    currentZone: null,
    
    initialize() {
        this.loadZones();
        this.setupControls();
    },
    
    loadZones() {
        const stored = localStorage.getItem('customZones');
        if (stored) {
            try {
                this.zones = JSON.parse(stored);
            } catch (e) {
                console.error('Error loading zones:', e);
                this.zones = [];
            }
        }
    },
    
    saveZones() {
        localStorage.setItem('customZones', JSON.stringify(this.zones));
    },
    
    addZone(name, coordinates) {
        const zone = {
            id: Date.now().toString(),
            name: name,
            coordinates: coordinates,
            created: new Date().toISOString()
        };
        
        this.zones.push(zone);
        this.saveZones();
        this.displayZones();
        return zone;
    },
    
    removeZone(zoneId) {
        this.zones = this.zones.filter(z => z.id !== zoneId);
        this.saveZones();
        this.displayZones();
    },
    
    getFiresInZone(zoneId, fireRecords) {
        const zone = this.zones.find(z => z.id === zoneId);
        if (!zone) return [];
        
        return fireRecords.filter(record => {
            const lat = parseFloat(record[2]);
            const lon = parseFloat(record[3]);
            return this.pointInPolygon(lat, lon, zone.coordinates);
        });
    },
    
    pointInPolygon(lat, lon, polygon) {
        let inside = false;
        for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
            const xi = polygon[i][0], yi = polygon[i][1];
            const xj = polygon[j][0], yj = polygon[j][1];
            
            const intersect = ((yi > lon) !== (yj > lon)) &&
                (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi);
            if (intersect) inside = !inside;
        }
        return inside;
    },
    
    displayZones() {
        const zonesSection = document.getElementById('zones-section');
        if (!zonesSection) return;
        
        let html = '<div class="zones-list">';
        
        if (this.zones.length === 0) {
            html += '<p class="no-zones">Aucune zone définie. Utilisez la carte pour créer des zones.</p>';
        } else {
            this.zones.forEach(zone => {
                html += `
                    <div class="zone-item" data-zone-id="${zone.id}">
                        <span class="zone-name">📍 ${zone.name}</span>
                        <button class="zone-delete" onclick="zonesOfInterest.removeZone('${zone.id}')">🗑️</button>
                    </div>
                `;
            });
        }
        
        html += '</div>';
        html += `
            <div class="zone-controls">
                <button id="draw-zone-btn" class="zone-btn">✏️ Dessiner une zone</button>
                <button id="export-zones-btn" class="zone-btn">💾 Exporter zones</button>
            </div>
        `;
        
        zonesSection.querySelector('.section-content').innerHTML = html;
        this.setupControls();
    },
    
    setupControls() {
        const drawBtn = document.getElementById('draw-zone-btn');
        const exportBtn = document.getElementById('export-zones-btn');
        
        if (drawBtn) {
            drawBtn.addEventListener('click', () => {
                alert('Fonctionnalité de dessin: Interagissez avec la carte pour tracer un polygone.\nCette fonctionnalité nécessite une intégration avec la carte Folium.');
            });
        }
        
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                const dataStr = JSON.stringify(this.zones, null, 2);
                const blob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'zones_interet.json';
                a.click();
            });
        }
    }
};

const dashboardData = {
    "stats": {
        "total_detections": 77,
        "confidence_counts": {
            "D\u00e9tections Haute Confiance": 31,
            "D\u00e9tections Nominale Confiance": 44,
            "D\u00e9tections Basse Confiance": 2,
            "D\u00e9tections Confiance Inconnue": 0
        },
        "satellite_counts": {
            "Terra": 48,
            "Aqua": 29
        },
        "recent_date_range": "2025-05-08 - 2025-05-02"
    },
    "detailList": [
        {
            "date": "2025-05-08",
            "time": "0048",
            "location": "11.51, 22.41",
            "confidence": "70"
        },
        {
            "date": "2025-05-08",
            "time": "0048",
            "location": "11.50, 22.40",
            "confidence": "97"
        },
        {
            "date": "2025-05-08",
            "time": "0048",
            "location": "11.50, 22.41",
            "confidence": "81"
        },
        {
            "date": "2025-05-07",
            "time": "1923",
            "location": "11.51, 22.40",
            "confidence": "97"
        },
        {
            "date": "2025-05-07",
            "time": "1923",
            "location": "11.50, 22.40",
            "confidence": "100"
        },
        {
            "date": "2025-05-07",
            "time": "1234",
            "location": "12.29, 22.29",
            "confidence": "62"
        },
        {
            "date": "2025-05-07",
            "time": "0837",
            "location": "9.92, 20.40",
            "confidence": "91"
        },
        {
            "date": "2025-05-07",
            "time": "0837",
            "location": "9.82, 15.51",
            "confidence": "72"
        },
        {
            "date": "2025-05-07",
            "time": "0837",
            "location": "9.91, 20.42",
            "confidence": "95"
        },
        {
            "date": "2025-05-07",
            "time": "0837",
            "location": "9.91, 20.42",
            "confidence": "100"
        },
        {
            "date": "2025-05-07",
            "time": "0837",
            "location": "9.91, 20.40",
            "confidence": "98"
        },
        {
            "date": "2025-05-07",
            "time": "0837",
            "location": "9.92, 20.43",
            "confidence": "45"
        },
        {
            "date": "2025-05-07",
            "time": "0837",
            "location": "9.93, 20.40",
            "confidence": "51"
        },
        {
            "date": "2025-05-07",
            "time": "0837",
            "location": "10.97, 16.61",
            "confidence": "64"
        },
        {
            "date": "2025-05-07",
            "time": "0835",
            "location": "12.03, 18.67",
            "confidence": "60"
        },
        {
            "date": "2025-05-07",
            "time": "0835",
            "location": "12.02, 17.79",
            "confidence": "68"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "10.43, 19.96",
            "confidence": "83"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "8.63, 17.43",
            "confidence": "57"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "8.83, 16.61",
            "confidence": "54"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "8.94, 15.32",
            "confidence": "42"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "9.64, 20.16",
            "confidence": "75"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "9.65, 20.17",
            "confidence": "88"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "10.41, 18.05",
            "confidence": "49"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "10.42, 19.98",
            "confidence": "81"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "11.50, 16.38",
            "confidence": "83"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "10.43, 19.98",
            "confidence": "100"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "10.97, 15.27",
            "confidence": "41"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "10.97, 15.28",
            "confidence": "89"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "10.98, 15.28",
            "confidence": "87"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "10.98, 15.29",
            "confidence": "76"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "11.64, 21.73",
            "confidence": "65"
        },
        {
            "date": "2025-05-06",
            "time": "1333",
            "location": "13.15, 14.28",
            "confidence": "65"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "10.80, 15.14",
            "confidence": "84"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "11.46, 21.60",
            "confidence": "74"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "11.46, 21.61",
            "confidence": "74"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "11.12, 20.72",
            "confidence": "63"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "11.02, 22.24",
            "confidence": "59"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "10.80, 15.13",
            "confidence": "68"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "10.80, 15.16",
            "confidence": "87"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "10.80, 15.17",
            "confidence": "86"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "10.79, 15.13",
            "confidence": "66"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "10.79, 15.16",
            "confidence": "81"
        },
        {
            "date": "2025-05-06",
            "time": "0756",
            "location": "10.33, 19.62",
            "confidence": "66"
        },
        {
            "date": "2025-05-06",
            "time": "0109",
            "location": "10.98, 15.31",
            "confidence": "58"
        },
        {
            "date": "2025-05-06",
            "time": "0109",
            "location": "10.98, 15.32",
            "confidence": "60"
        },
        {
            "date": "2025-05-05",
            "time": "1942",
            "location": "9.69, 20.31",
            "confidence": "55"
        },
        {
            "date": "2025-05-05",
            "time": "1255",
            "location": "11.47, 21.61",
            "confidence": "66"
        },
        {
            "date": "2025-05-05",
            "time": "1253",
            "location": "10.31, 21.00",
            "confidence": "76"
        },
        {
            "date": "2025-05-05",
            "time": "1253",
            "location": "10.31, 20.99",
            "confidence": "83"
        },
        {
            "date": "2025-05-04",
            "time": "0818",
            "location": "9.67, 16.23",
            "confidence": "71"
        },
        {
            "date": "2025-05-04",
            "time": "0818",
            "location": "9.18, 20.01",
            "confidence": "70"
        },
        {
            "date": "2025-05-04",
            "time": "0818",
            "location": "9.18, 20.02",
            "confidence": "73"
        },
        {
            "date": "2025-05-04",
            "time": "0816",
            "location": "12.00, 18.84",
            "confidence": "16"
        },
        {
            "date": "2025-05-04",
            "time": "0816",
            "location": "10.87, 21.84",
            "confidence": "93"
        },
        {
            "date": "2025-05-04",
            "time": "0816",
            "location": "10.87, 21.86",
            "confidence": "97"
        },
        {
            "date": "2025-05-04",
            "time": "0816",
            "location": "10.86, 21.85",
            "confidence": "84"
        },
        {
            "date": "2025-05-03",
            "time": "2002",
            "location": "10.39, 20.78",
            "confidence": "100"
        },
        {
            "date": "2025-05-03",
            "time": "2002",
            "location": "9.95, 15.70",
            "confidence": "32"
        },
        {
            "date": "2025-05-03",
            "time": "2002",
            "location": "10.39, 20.77",
            "confidence": "100"
        },
        {
            "date": "2025-05-03",
            "time": "2002",
            "location": "10.98, 18.07",
            "confidence": "14"
        },
        {
            "date": "2025-05-03",
            "time": "2002",
            "location": "10.39, 20.78",
            "confidence": "100"
        },
        {
            "date": "2025-05-03",
            "time": "2002",
            "location": "13.15, 20.67",
            "confidence": "39"
        },
        {
            "date": "2025-05-03",
            "time": "1314",
            "location": "12.81, 19.06",
            "confidence": "54"
        },
        {
            "date": "2025-05-03",
            "time": "1314",
            "location": "11.39, 19.37",
            "confidence": "73"
        },
        {
            "date": "2025-05-03",
            "time": "1314",
            "location": "10.40, 20.76",
            "confidence": "82"
        },
        {
            "date": "2025-05-03",
            "time": "1314",
            "location": "10.39, 20.76",
            "confidence": "92"
        },
        {
            "date": "2025-05-03",
            "time": "0737",
            "location": "10.23, 21.65",
            "confidence": "44"
        },
        {
            "date": "2025-05-02",
            "time": "1923",
            "location": "13.15, 20.64",
            "confidence": "100"
        },
        {
            "date": "2025-05-02",
            "time": "1923",
            "location": "13.15, 20.65",
            "confidence": "100"
        },
        {
            "date": "2025-05-02",
            "time": "1923",
            "location": "13.14, 20.62",
            "confidence": "70"
        },
        {
            "date": "2025-05-02",
            "time": "0835",
            "location": "11.57, 19.23",
            "confidence": "75"
        },
        {
            "date": "2025-05-02",
            "time": "0835",
            "location": "10.11, 20.64",
            "confidence": "75"
        },
        {
            "date": "2025-05-02",
            "time": "0835",
            "location": "10.12, 20.64",
            "confidence": "65"
        },
        {
            "date": "2025-05-02",
            "time": "0835",
            "location": "9.21, 15.60",
            "confidence": "76"
        },
        {
            "date": "2025-05-02",
            "time": "0835",
            "location": "11.57, 19.21",
            "confidence": "92"
        },
        {
            "date": "2025-05-02",
            "time": "0835",
            "location": "13.36, 15.25",
            "confidence": "46"
        },
        {
            "date": "2025-05-02",
            "time": "0835",
            "location": "9.20, 20.03",
            "confidence": "78"
        }
    ],
    "fireRecords": [
        [
            "2025-05-02",
            "0835",
            "9.1980",
            "20.0327",
            "327.5 K <span class='fire-emoji' data-brightness='327.46'>\ud83d\udd25</span>",
            "78",
            "Terra"
        ],
        [
            "2025-05-02",
            "0835",
            "9.2087",
            "15.6004",
            "328.8 K <span class='fire-emoji' data-brightness='328.84'>\ud83d\udd25</span>",
            "76",
            "Terra"
        ],
        [
            "2025-05-02",
            "0835",
            "10.1118",
            "20.6420",
            "328.5 K <span class='fire-emoji' data-brightness='328.48'>\ud83d\udd25</span>",
            "75",
            "Terra"
        ],
        [
            "2025-05-02",
            "0835",
            "10.1248",
            "20.6441",
            "323.1 K <span class='fire-emoji' data-brightness='323.05'>\ud83d\udd25</span>",
            "65",
            "Terra"
        ],
        [
            "2025-05-02",
            "0835",
            "11.5670",
            "19.2270",
            "333.1 K <span class='fire-emoji' data-brightness='333.09'>\ud83d\udd25</span>",
            "75",
            "Terra"
        ],
        [
            "2025-05-02",
            "0835",
            "11.5694",
            "19.2118",
            "349.0 K <span class='fire-emoji' data-brightness='348.99'>\ud83d\udd25</span>",
            "92",
            "Terra"
        ],
        [
            "2025-05-02",
            "0835",
            "13.3614",
            "15.2506",
            "326.2 K <span class='fire-emoji' data-brightness='326.21'>\ud83d\udd25</span>",
            "46",
            "Terra"
        ],
        [
            "2025-05-02",
            "1923",
            "13.1407",
            "20.6224",
            "309.5 K <span class='fire-emoji' data-brightness='309.51'>\ud83d\udd25</span>",
            "70",
            "Terra"
        ],
        [
            "2025-05-02",
            "1923",
            "13.1452",
            "20.6492",
            "335.6 K <span class='fire-emoji' data-brightness='335.58'>\ud83d\udd25</span>",
            "100",
            "Terra"
        ],
        [
            "2025-05-02",
            "1923",
            "13.1480",
            "20.6440",
            "336.7 K <span class='fire-emoji' data-brightness='336.69'>\ud83d\udd25</span>",
            "100",
            "Terra"
        ],
        [
            "2025-05-03",
            "0737",
            "10.2330",
            "21.6500",
            "312.9 K <span class='fire-emoji' data-brightness='312.93'>\ud83d\udd25</span>",
            "44",
            "Terra"
        ],
        [
            "2025-05-03",
            "1314",
            "10.3947",
            "20.7638",
            "346.2 K <span class='fire-emoji' data-brightness='346.22'>\ud83d\udd25</span>",
            "92",
            "Aqua"
        ],
        [
            "2025-05-03",
            "1314",
            "10.4037",
            "20.7625",
            "334.4 K <span class='fire-emoji' data-brightness='334.35'>\ud83d\udd25</span>",
            "82",
            "Aqua"
        ],
        [
            "2025-05-03",
            "1314",
            "11.3937",
            "19.3662",
            "320.8 K <span class='fire-emoji' data-brightness='320.76'>\ud83d\udd25</span>",
            "73",
            "Aqua"
        ],
        [
            "2025-05-03",
            "1314",
            "12.8094",
            "19.0616",
            "319.9 K <span class='fire-emoji' data-brightness='319.94'>\ud83d\udd25</span>",
            "54",
            "Aqua"
        ],
        [
            "2025-05-03",
            "2002",
            "9.9519",
            "15.7003",
            "302.2 K <span class='fire-emoji' data-brightness='302.16'>\ud83d\udd25</span>",
            "32",
            "Terra"
        ],
        [
            "2025-05-03",
            "2002",
            "10.3897",
            "20.7660",
            "321.0 K <span class='fire-emoji' data-brightness='321.0'>\ud83d\udd25</span>",
            "100",
            "Terra"
        ],
        [
            "2025-05-03",
            "2002",
            "10.3910",
            "20.7754",
            "323.5 K <span class='fire-emoji' data-brightness='323.5'>\ud83d\udd25</span>",
            "100",
            "Terra"
        ],
        [
            "2025-05-03",
            "2002",
            "10.3922",
            "20.7848",
            "322.8 K <span class='fire-emoji' data-brightness='322.78'>\ud83d\udd25</span>",
            "100",
            "Terra"
        ],
        [
            "2025-05-03",
            "2002",
            "10.9754",
            "18.0697",
            "300.2 K <span class='fire-emoji' data-brightness='300.2'>\ud83d\udd25</span>",
            "14",
            "Terra"
        ],
        [
            "2025-05-03",
            "2002",
            "13.1477",
            "20.6663",
            "303.4 K <span class='fire-emoji' data-brightness='303.37'>\ud83d\udd25</span>",
            "39",
            "Terra"
        ],
        [
            "2025-05-04",
            "0816",
            "10.8606",
            "21.8536",
            "334.6 K <span class='fire-emoji' data-brightness='334.6'>\ud83d\udd25</span>",
            "84",
            "Terra"
        ],
        [
            "2025-05-04",
            "0816",
            "10.8703",
            "21.8552",
            "355.3 K <span class='fire-emoji' data-brightness='355.34'>\ud83d\udd25</span>",
            "97",
            "Terra"
        ],
        [
            "2025-05-04",
            "0816",
            "10.8721",
            "21.8440",
            "347.4 K <span class='fire-emoji' data-brightness='347.38'>\ud83d\udd25</span>",
            "93",
            "Terra"
        ],
        [
            "2025-05-04",
            "0816",
            "12.0034",
            "18.8390",
            "325.1 K <span class='fire-emoji' data-brightness='325.13'>\ud83d\udd25</span>",
            "16",
            "Terra"
        ],
        [
            "2025-05-04",
            "0818",
            "9.1814",
            "20.0202",
            "325.5 K <span class='fire-emoji' data-brightness='325.51'>\ud83d\udd25</span>",
            "73",
            "Terra"
        ],
        [
            "2025-05-04",
            "0818",
            "9.1828",
            "20.0108",
            "323.4 K <span class='fire-emoji' data-brightness='323.38'>\ud83d\udd25</span>",
            "70",
            "Terra"
        ],
        [
            "2025-05-04",
            "0818",
            "9.6662",
            "16.2316",
            "329.0 K <span class='fire-emoji' data-brightness='328.96'>\ud83d\udd25</span>",
            "71",
            "Terra"
        ],
        [
            "2025-05-05",
            "1253",
            "10.3076",
            "20.9931",
            "340.0 K <span class='fire-emoji' data-brightness='340.03'>\ud83d\udd25</span>",
            "83",
            "Aqua"
        ],
        [
            "2025-05-05",
            "1253",
            "10.3095",
            "21.0050",
            "335.0 K <span class='fire-emoji' data-brightness='335.03'>\ud83d\udd25</span>",
            "76",
            "Aqua"
        ],
        [
            "2025-05-05",
            "1255",
            "11.4716",
            "21.6095",
            "333.8 K <span class='fire-emoji' data-brightness='333.84'>\ud83d\udd25</span>",
            "66",
            "Aqua"
        ],
        [
            "2025-05-05",
            "1942",
            "9.6884",
            "20.3071",
            "306.7 K <span class='fire-emoji' data-brightness='306.7'>\ud83d\udd25</span>",
            "55",
            "Terra"
        ],
        [
            "2025-05-06",
            "0109",
            "10.9775",
            "15.3181",
            "304.4 K <span class='fire-emoji' data-brightness='304.37'>\ud83d\udd25</span>",
            "60",
            "Aqua"
        ],
        [
            "2025-05-06",
            "0109",
            "10.9806",
            "15.3137",
            "304.1 K <span class='fire-emoji' data-brightness='304.08'>\ud83d\udd25</span>",
            "58",
            "Aqua"
        ],
        [
            "2025-05-06",
            "0756",
            "10.3316",
            "19.6234",
            "326.9 K <span class='fire-emoji' data-brightness='326.9'>\ud83d\udd25</span>",
            "66",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "10.7856",
            "15.1598",
            "333.4 K <span class='fire-emoji' data-brightness='333.39'>\ud83d\udd25</span>",
            "81",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "10.7889",
            "15.1308",
            "326.0 K <span class='fire-emoji' data-brightness='326.04'>\ud83d\udd25</span>",
            "66",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "10.7994",
            "15.1674",
            "338.4 K <span class='fire-emoji' data-brightness='338.37'>\ud83d\udd25</span>",
            "86",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "10.8006",
            "15.1615",
            "339.9 K <span class='fire-emoji' data-brightness='339.91'>\ud83d\udd25</span>",
            "87",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "10.8026",
            "15.1383",
            "336.9 K <span class='fire-emoji' data-brightness='336.88'>\ud83d\udd25</span>",
            "84",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "10.8041",
            "15.1325",
            "325.3 K <span class='fire-emoji' data-brightness='325.3'>\ud83d\udd25</span>",
            "68",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "11.0155",
            "22.2372",
            "326.2 K <span class='fire-emoji' data-brightness='326.23'>\ud83d\udd25</span>",
            "59",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "11.1236",
            "20.7249",
            "327.3 K <span class='fire-emoji' data-brightness='327.33'>\ud83d\udd25</span>",
            "63",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "11.4624",
            "21.6105",
            "331.9 K <span class='fire-emoji' data-brightness='331.95'>\ud83d\udd25</span>",
            "74",
            "Terra"
        ],
        [
            "2025-05-06",
            "0756",
            "11.4638",
            "21.6004",
            "331.7 K <span class='fire-emoji' data-brightness='331.69'>\ud83d\udd25</span>",
            "74",
            "Terra"
        ],
        [
            "2025-05-06",
            "1333",
            "8.6261",
            "17.4258",
            "328.2 K <span class='fire-emoji' data-brightness='328.22'>\ud83d\udd25</span>",
            "57",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "8.8342",
            "16.6133",
            "331.1 K <span class='fire-emoji' data-brightness='331.1'>\ud83d\udd25</span>",
            "54",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "8.9365",
            "15.3207",
            "332.9 K <span class='fire-emoji' data-brightness='332.9'>\ud83d\udd25</span>",
            "42",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "9.6435",
            "20.1560",
            "331.5 K <span class='fire-emoji' data-brightness='331.5'>\ud83d\udd25</span>",
            "75",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "9.6457",
            "20.1721",
            "342.1 K <span class='fire-emoji' data-brightness='342.14'>\ud83d\udd25</span>",
            "88",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "10.4127",
            "18.0511",
            "329.0 K <span class='fire-emoji' data-brightness='329.0'>\ud83d\udd25</span>",
            "49",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "10.4215",
            "19.9794",
            "338.1 K <span class='fire-emoji' data-brightness='338.09'>\ud83d\udd25</span>",
            "81",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "10.4310",
            "19.9618",
            "339.5 K <span class='fire-emoji' data-brightness='339.51'>\ud83d\udd25</span>",
            "83",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "10.4331",
            "19.9778",
            "373.5 K <span class='fire-emoji' data-brightness='373.48'>\ud83d\udd25</span>",
            "100",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "10.9699",
            "15.2728",
            "332.9 K <span class='fire-emoji' data-brightness='332.86'>\ud83d\udd25</span>",
            "41",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "10.9712",
            "15.2818",
            "346.8 K <span class='fire-emoji' data-brightness='346.75'>\ud83d\udd25</span>",
            "89",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "10.9800",
            "15.2805",
            "346.8 K <span class='fire-emoji' data-brightness='346.79'>\ud83d\udd25</span>",
            "87",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "10.9813",
            "15.2895",
            "343.8 K <span class='fire-emoji' data-brightness='343.78'>\ud83d\udd25</span>",
            "76",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "11.5040",
            "16.3783",
            "344.3 K <span class='fire-emoji' data-brightness='344.28'>\ud83d\udd25</span>",
            "83",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "11.6383",
            "21.7295",
            "331.2 K <span class='fire-emoji' data-brightness='331.25'>\ud83d\udd25</span>",
            "65",
            "Aqua"
        ],
        [
            "2025-05-06",
            "1333",
            "13.1520",
            "14.2760",
            "332.9 K <span class='fire-emoji' data-brightness='332.95'>\ud83d\udd25</span>",
            "65",
            "Aqua"
        ],
        [
            "2025-05-07",
            "0835",
            "12.0242",
            "17.7941",
            "331.5 K <span class='fire-emoji' data-brightness='331.46'>\ud83d\udd25</span>",
            "68",
            "Terra"
        ],
        [
            "2025-05-07",
            "0835",
            "12.0330",
            "18.6738",
            "328.6 K <span class='fire-emoji' data-brightness='328.57'>\ud83d\udd25</span>",
            "60",
            "Terra"
        ],
        [
            "2025-05-07",
            "0837",
            "9.8177",
            "15.5054",
            "330.2 K <span class='fire-emoji' data-brightness='330.23'>\ud83d\udd25</span>",
            "72",
            "Terra"
        ],
        [
            "2025-05-07",
            "0837",
            "9.9110",
            "20.4239",
            "351.7 K <span class='fire-emoji' data-brightness='351.71'>\ud83d\udd25</span>",
            "95",
            "Terra"
        ],
        [
            "2025-05-07",
            "0837",
            "9.9146",
            "20.4025",
            "357.5 K <span class='fire-emoji' data-brightness='357.46'>\ud83d\udd25</span>",
            "98",
            "Terra"
        ],
        [
            "2025-05-07",
            "0837",
            "9.9149",
            "20.4181",
            "360.1 K <span class='fire-emoji' data-brightness='360.06'>\ud83d\udd25</span>",
            "100",
            "Terra"
        ],
        [
            "2025-05-07",
            "0837",
            "9.9183",
            "20.3965",
            "345.6 K <span class='fire-emoji' data-brightness='345.59'>\ud83d\udd25</span>",
            "91",
            "Terra"
        ],
        [
            "2025-05-07",
            "0837",
            "9.9242",
            "20.4261",
            "324.2 K <span class='fire-emoji' data-brightness='324.25'>\ud83d\udd25</span>",
            "45",
            "Terra"
        ],
        [
            "2025-05-07",
            "0837",
            "9.9278",
            "20.4046",
            "325.6 K <span class='fire-emoji' data-brightness='325.56'>\ud83d\udd25</span>",
            "51",
            "Terra"
        ],
        [
            "2025-05-07",
            "0837",
            "10.9676",
            "16.6110",
            "326.0 K <span class='fire-emoji' data-brightness='325.98'>\ud83d\udd25</span>",
            "64",
            "Terra"
        ],
        [
            "2025-05-07",
            "1234",
            "12.2858",
            "22.2856",
            "334.3 K <span class='fire-emoji' data-brightness='334.3'>\ud83d\udd25</span>",
            "62",
            "Aqua"
        ],
        [
            "2025-05-07",
            "1923",
            "11.4990",
            "22.3993",
            "322.2 K <span class='fire-emoji' data-brightness='322.17'>\ud83d\udd25</span>",
            "100",
            "Terra"
        ],
        [
            "2025-05-07",
            "1923",
            "11.5114",
            "22.3968",
            "318.6 K <span class='fire-emoji' data-brightness='318.63'>\ud83d\udd25</span>",
            "97",
            "Terra"
        ],
        [
            "2025-05-08",
            "0048",
            "11.4974",
            "22.4061",
            "310.6 K <span class='fire-emoji' data-brightness='310.63'>\ud83d\udd25</span>",
            "81",
            "Aqua"
        ],
        [
            "2025-05-08",
            "0048",
            "11.5038",
            "22.3997",
            "318.5 K <span class='fire-emoji' data-brightness='318.48'>\ud83d\udd25</span>",
            "97",
            "Aqua"
        ],
        [
            "2025-05-08",
            "0048",
            "11.5109",
            "22.4076",
            "307.0 K <span class='fire-emoji' data-brightness='306.96'>\ud83d\udd25</span>",
            "70",
            "Aqua"
        ]
    ]
};
// --- Début du code JavaScript front-end amélioré ---
// Wait for the DOM to be fully loaded before trying to access elements
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded. Starting dashboard population.");

    // Access data loaded from the JSON structure defined before this script block
    // const dashboardData is defined in the Python output.
    // Add a check to ensure dashboardData is available
    if (typeof dashboardData === 'undefined') {
        console.error("Error: dashboardData is not defined. Python script may have failed to generate the data file or it's empty.");
        // Optionally display an error message in key areas if data failed to load
        const mainContent = document.querySelector("main"); // Assuming main contains dashboard elements
        if(mainContent) mainContent.innerHTML = "<h1>Erreur de chargement des données</h1><p>Impossible de charger les données du tableau de bord. Veuillez vérifier le script Python et l'accès à l'API FIRMS.</p>";
        return; // Stop script execution if data is missing
    }
    console.log("Dashboard data loaded successfully."); // Simpler initial log

    // --- IMPORTANT DEBUG LOGS ---
    console.log("Dashboard data structure received in JS:", dashboardData);
    console.log("Stats data:", dashboardData.stats);
    console.log("Number of fireRecords received:", dashboardData.fireRecords ? dashboardData.fireRecords.length : 0);
    if (dashboardData.fireRecords && dashboardData.fireRecords.length > 0) {
         console.log("First fireRecord sample:", dashboardData.fireRecords[0]);
    } else {
         console.log("dashboardData.fireRecords is empty or null.");
    }
    // --- END DEBUG LOGS ---


    // Store original unfiltered records
    // fireRecords column order is defined by JS_TABLE_COLUMNS in Python:
    // Date, Time, Latitude, Longitude, Brightness (HTML), Confidence (string), Satellite
    const originalFireRecords = dashboardData.fireRecords || []; // Use || [] to ensure it's an array even if missing/null
    let currentDataTableInstance = null; // Variable to hold the Simple-DataTables instance
    let refreshIntervalId = null; // Variable to hold the interval ID for auto-refresh

    // Read refresh interval from a data attribute in HTML if available, fallback to default
    const refreshIndicator = document.querySelector(".auto-refresh-indicator");
    // Use a default of 300 seconds (5 minutes) if attribute is missing or invalid
    const refreshIntervalSeconds = refreshIndicator ? parseInt(refreshIndicator.dataset.interval || '300', 10) : 300;
    let countdownSpan = refreshIndicator ? refreshIndicator.querySelector("#refresh-countdown") : null; // Span for countdown inside the indicator


    // --- Function to populate the data table and initialize/re-initialize Simple-DataTables ---
    // This function is called with the array of records to display (either all or filtered)
    function initializeDataTable(recordsToShow) {
        console.log("DataTable: initializeDataTable called.");
        const tableElement = document.querySelector("#fire-table");
        const tableBody = tableElement ? tableElement.querySelector("tbody") : null; // Check if tableElement exists first

        if (!tableElement || !tableBody) {
             console.error("DataTable Error: Table element (#fire-table) or tbody not found. Cannot initialize.");
             // Potentially display an error message inside the table container if the elements are missing
             const tableSectionContent = document.querySelector("#data-table-section .section-content");
             if(tableSectionContent) {
                  tableSectionContent.innerHTML = "<p>Erreur : Éléments du tableau (table, tbody) introuvables dans le HTML.</p>";
             }
             return;
        }

        console.log(`DataTable: Attempting to initialize table with ${recordsToShow ? recordsToShow.length : 0} records provided.`);

        // Destroy existing instance if it exists
        if (currentDataTableInstance) {
            console.log("DataTable: Destroying existing Simple-DataTables instance.");
            try {
               currentDataTableInstance.destroy();
               // Simple-DataTables destroy typically cleans up its wrapper.
               // The manual cleanup below is kept only as a fallback for severe issues.
            } catch(e) {
               console.warn("DataTable Warning: Error destroying Simple-DataTables instance, attempting manual cleanup:", e);
               // Manual cleanup attempt if destroy fails - target the wrapper element
                const wrapper = tableElement.parentElement;
               if(wrapper && wrapper.classList.contains('dataTable-wrapper')) {
                   console.warn("DataTable Manual Cleanup: Attempting manual DataTable wrapper cleanup...");
                   // Re-insert the original table element back into its parent before removing the wrapper
                   wrapper.parentElement.insertBefore(tableElement, wrapper);
                   wrapper.remove(); // Remove the wrapper
                    console.log("DataTable Manual Cleanup: Completed.");
               }
            }
            currentDataTableInstance = null; // Ensure instance is null after destruction/cleanup
            // Restore any inline styles SimpleDataTable might have added (like height)
             tableElement.style.removeProperty('height');
             tableElement.style.removeProperty('width'); // less likely, but defensive
             tableElement.style.removeProperty('max-width'); // simple-datatables adds this
        }

        // Clear existing rows (including the potential initial loading message from HTML)
        tableBody.innerHTML = '';
        console.log("DataTable: tbody cleared.");


        // Define the expected number of columns based on your table header or Python's JS_TABLE_COLUMNS
        // This is used for colspan and padding rows if needed.
        const expectedColCount = 7; // Date, Time, Lat, Lon, Brightness(HTML), Confidence, Satellite

        // Decide whether to populate with data and initialize DataTable, or show "No data" message
        if (recordsToShow && recordsToShow.length > 0) {
            console.log(`DataTable: Populating tbody with ${recordsToShow.length} records.`);
            recordsToShow.forEach((row, rowIndex) => {
                const tr = document.createElement("tr");
                 if (Array.isArray(row)) {
                    // Log sample row content for debugging
                     if (rowIndex < 5) { // Log first 5 rows as sample
                         console.log(`DataTable: Processing row ${rowIndex}:`, row);
                     }

                    // Ensure row has enough data cells as expected, pad if necessary
                    // Iterate up to the expected number of columns defined by HTML structure/Python prep
                    for(let i = 0; i < expectedColCount; i++) {
                         const td = document.createElement("td");
                         // Get cell data at index i, default to '-' if missing, null, or undefined
                         const cellData = (i < row.length && row[i] !== null && row[i] !== undefined) ? row[i] : '-';

                         // For the brightness column (index 4), insert HTML
                         if (i === 4) { // Assuming Brightness is the 5th column (index 4)
                              td.innerHTML = String(cellData); // Use innerHTML for the brightness column (includes emoji HTML)
                         } else {
                              // For other columns, use textContent for security
                              td.textContent = String(cellData); // Ensure it's a string
                         }

                         // Add data attribute for the date column (index 0) for potential external filtering
                         if (i === 0) { // Date column
                             const recordDate = String(cellData); // Get the date string
                             // Basic validation for YYYY-MM-DD format before adding data-attribute
                             if (typeof recordDate === 'string' && recordDate.match(/^\d{4}-\d{2}-\d{2}$/)) {
                                 tr.dataset.date = recordDate;
                             } else {
                                 tr.dataset.date = 'invalid-date'; // Tag rows with invalid dates
                                 // console.warn(`Record ${rowIndex} has invalid date format for filtering:`, recordDate, row); // Can be chatty
                             }
                         }
                         tr.appendChild(td);
                    }
                    // If row had more columns than expected, they are ignored by the loop

                    tableBody.appendChild(tr);
                 } else {
                     console.warn("DataTable Warning: Skipping invalid row format in recordsToShow:", row);
                 }
            });
            console.log("DataTable: tbody populated.");

            // *** Initialize Simple-DataTables NOW if there are valid data rows in tbody ***
             // Check if the tbody actually contains data rows to display, not just invalid/placeholder ones
             // A simple check for number of rows is sufficient after populating it from recordsToShow
             const populatedRowCount = tableBody.querySelectorAll("tr").length;
             console.log(`DataTable: Found ${populatedRowCount} rows in tbody after population.`);

             if (populatedRowCount > 0) {
                 try {
                    console.log("DataTable: Initializing simple-datatables...");
                    // Pass the table element directly
                    currentDataTableInstance = new simpleDatatables.DataTable(tableElement, {
                       searchable: true, // Enable search input
                       fixedHeight: true, // Use fixed height for scrollable table body (CSS must define height for .dataTable-container)
                       perPage: 10, // Default number of rows per page
                       perPageSelect: [5, 10, 20, 50, 100, -1], // -1 means All rows
                       labels: { // Customize labels (French)
                            placeholder: "Rechercher...",
                            perPage: "{select} entrées par page",
                            noRows: "Aucune entrée correspondante", // Message when search/filters return nothing
                            info: "Affichage de {start} à {end} sur {rows} entrées",
                            sort: "Trier ", // Added space for icon
                            emptyRows: "Aucune donnée à afficher." // Message when the *initial* data is empty (should be caught by outer checks)
                       },
                       layout: { // Define layout order for top/bottom controls
                           top: "{search}{select}",
                           bottom: "{info}{pager}"
                       },
                       columns: [ // Define column properties (0-indexed)
                            { select: 0, type: "date", format: "YYYY-MM-DD" }, // Date column (index 0) is date type
                            { select: 4, type: "html" }, // Brightness column (index 4) contains HTML
                            // Other columns default to 'string' type, which is fine for sorting text/numbers as strings
                            // { select: [1, 2, 3, 5, 6], type: "string" } // Can explicitly set if needed
                       ],
                    });
                    console.log("DataTable: simple-datatables initialized successfully.");

                    // Trigger layout update if needed (sometimes necessary after DOM manipulation or hidden elements)
                    // A small delay might be required if the table was initially hidden due to collapsible
                    if (currentDataTableInstance && typeof currentDataTableInstance.update === 'function') {
                         console.log("DataTable: Triggering initial update.");
                         setTimeout(() => currentDataTableInstance.update(), 50); // Add a slight delay
                    }


                 } catch (error) {
                    console.error("DataTable Error: Error initializing simple-datatables:", error);
                    // Display a fallback message if DataTable initialization fails despite having data rows in tbody
                    // Ensure the error message takes up the full width
                    if (tableBody.querySelectorAll("tr").length > 0) {
                         const errorRow = document.createElement("tr");
                         const errorCell = document.createElement("td");
                         errorCell.setAttribute("colspan", expectedColCount); // Use dynamic colspan
                         errorCell.style.textAlign = "center";
                         errorCell.textContent = "Erreur lors de l'affichage du tableau de données.";
                         tableBody.innerHTML = ''; // Clear any potentially corrupted data rows
                         tableBody.appendChild(errorRow);
                    } else {
                         // If tbody somehow became empty or had no valid data rows, show a generic no data message
                         const noDataRow = document.createElement("tr");
                         const noDataCell = document.createElement("td");
                         noDataCell.setAttribute("colspan", expectedColCount);
                         noDataCell.style.textAlign = "center";
                         noDataCell.textContent = "Impossible d'afficher le tableau. Aucune donnée valide.";
                         tableBody.innerHTML = ''; // Ensure it's clear
                         tableBody.appendChild(noDataRow);
                    }
                    // Ensure instance is null if initialization failed
                    currentDataTableInstance = null;
                }
             } else {
                  // This case means recordsToShow had data, but tbody population resulted in 0 valid rows
                  console.warn("DataTable Warning: recordsToShow had data, but tbody population resulted in 0 valid data rows. Simple-datatables not initialized.");
                  const noDataRow = document.createElement("tr");
                  const noDataCell = document.createElement("td");
                  noDataCell.setAttribute("colspan", expectedColCount);
                  noDataCell.style.textAlign = "center";
                  noDataCell.textContent = "Aucune donnée valide à afficher dans le tableau.";
                  tableBody.innerHTML = ''; // Clear any previous content
                  tableBody.appendChild(noDataRow);
             }


        } else {
            // Case where recordsToShow is empty or null - display a "No data" message
            console.log("DataTable: recordsToShow is empty or null.");
            const expectedColCount = 7; // Need this for colspan
            const noDataRow = document.createElement("tr");
            const noDataCell = document.createElement("td");
            noDataCell.setAttribute("colspan", expectedColCount);
            noDataCell.style.textAlign = "center";
            noDataCell.textContent = "Aucune donnée de détection disponible pour le tableau.";
            tableBody.innerHTML = ''; // Clear initial loading message
            tableBody.appendChild(noDataRow);
             console.warn("DataTable Warning: No fire records data provided to initializeDataTable function or data is empty. DataTable not initialized.");
             // Destroy if there was a previous instance showing data from a prior filter state
             if (currentDataTableInstance) {
                 currentDataTableInstance.destroy();
                 currentDataTableInstance = null;
             }
        }

         // After initialization (or not), apply the brightness emoji styling
         // This styles emojis added manually or by simple-datatables
         // Add a timeout just in case rendering takes a moment
         setTimeout(applyBrightnessEmojiStyle, 100);


         // Re-adjust DataTable layout after potential styling or if in a collapsed container
         // This is sometimes needed for column widths/heights
         // The update call after initialization above might be sufficient, but adding another one here
         // after emoji styling might help if styling affects layout.
         // if (currentDataTableInstance && typeof currentDataTableInstance.update === 'function') {
         //      console.log("DataTable: Triggering update after emoji styling.");
         //       setTimeout(() => currentDataTableInstance.update(), 150); // Small delay after emoji styling
         // }

    }

    // --- Function to dynamically style brightness emojis based on data-brightness attribute ---
    function applyBrightnessEmojiStyle() {
        console.log("EmojiStyle: Applying brightness emoji styles...");
        // Select emojis *within the table body* that have the data-brightness attribute
        const emojis = document.querySelectorAll("#fire-table tbody .fire-emoji[data-brightness]");

        if (emojis.length === 0) {
            console.log("EmojiStyle: No brightness emojis found in table to style.");
        } else {
             console.log(`EmojiStyle: Found ${emojis.length} brightness emojis to style.`);
        }


        emojis.forEach(emojiSpan => {
            const brightness = parseFloat(emojiSpan.dataset.brightness);
            // Remove any previous size classes
            emojiSpan.classList.remove('fire-size-medium', 'fire-size-high', 'fire-size-veryhigh');

            if (!isNaN(brightness)) {
                // Add class based on brightness range (matches CSS classes)
                if (brightness > 400) {
                    emojiSpan.classList.add('fire-size-veryhigh');
                } else if (brightness > 380) {
                    emojiSpan.classList.add('fire-size-high');
                } else if (brightness > 350) {
                    emojiSpan.classList.add('fire-size-medium');
                }
                // Base size is applied by the default CSS rule
            }

            // Ensure inline-block and vertical alignment for proper display
            emojiSpan.style.display = 'inline-block'; // Ensure transform/font-size works
            emojiSpan.style.marginLeft = '5px'; // Add slight space from number
            emojiSpan.style.verticalAlign = 'middle'; // Vertically align emoji
            emojiSpan.style.lineHeight = '1'; // Adjust line height for better alignment
            emojiSpan.style.transformOrigin = 'center center'; // Scale from the center

             // Optional: Add a tooltip showing the exact brightness value
             emojiSpan.title = `Luminosité: ${isNaN(brightness) ? 'N/A' : brightness.toFixed(1) + ' K'}`;
        });
         console.log(`EmojiStyle: Styled ${emojis.length} brightness emojis.`);
    }


    // --- Function to apply date filters ---
    function applyDateFilters() {
        console.log("Filter: Applying date filters...");
        const filterSection = document.querySelector("#filter-section"); // Select the filter section first
        // Select inputs and buttons *within* the filter section
        const singleDateInput = filterSection ? filterSection.querySelector("#filter-single-date") : null;
        const startDateInput = filterSection ? filterSection.querySelector("#filter-start-date") : null;
        const endDateInput = filterSection ? filterSection.querySelector("#filter-end-date") : null;

        // Ensure at least the filter section exists before trying to get values
        const singleDateVal = singleDateInput ? singleDateInput.value : '';
        const startDateVal = startDateInput ? startDateInput.value : '';
        const endDateVal = endDateInput ? endDateInput.value : '';

        console.log(`Filter: Inputs - Single: "${singleDateVal}", Start: "${startDateVal}", End: "${endDateVal}"`);


        let filteredRecords = originalFireRecords; // Start with all records

        // Filtering logic using YYYY-MM-DD string comparison
        if (singleDateVal) {
            console.log(`Filter: Filtering for single date: ${singleDateVal}`);
            filteredRecords = originalFireRecords.filter(row => {
                // Assuming date is the first column (index 0) and is 'YYYY-MM-DD' string from Python
                const recordDate = (row.length > 0 && row[0] !== null && row[0] !== undefined) ? String(row[0]) : '';
                // Check if recordDate is a valid string format before comparison
                const isMatch = typeof recordDate === 'string' && recordDate.match(/^\d{4}-\d{2}-\d{2}$/) && recordDate === singleDateVal;
                // if (!isMatch && rowIndex < 10) console.log(`Filter: Row ${rowIndex} date "${recordDate}" does not match single date "${singleDateVal}"`); // Debug non-matches
                return isMatch;
            });
             console.log(`Filter: Found ${filteredRecords.length} records matching single date filter.`);


        } else if (startDateVal || endDateVal) {
             console.log(`Filter: Filtering for date range: ${startDateVal || 'Any'} to ${endDateVal || 'Any'}`);
             filteredRecords = originalFireRecords.filter((row, rowIndex) => {
                // Assuming date is the first column (index 0) and is 'YYYY-MM-DD' string from Python
                const recordDate = (row.length > 0 && row[0] !== null && row[0] !== undefined) ? String(row[0]) : '';

                // Records must have a valid date string (YYYY-MM-DD) to be considered for range filtering
                if (!recordDate || typeof recordDate !== 'string' || !recordDate.match(/^\d{4}-\d{2}-\d{2}$/)) {
                     // if (rowIndex < 10) console.log("Filter: Skipping record with invalid date format for filtering:", recordDate, row); // Too chatty
                     return false; // Exclude records with invalid or missing dates from range filter
                }

                // Check start date (recordDate must be >= startDateVal if startDateVal is set)
                const passStartDateFilter = !startDateVal || recordDate >= startDateVal;

                // Check end date (recordDate must be <= endDateVal if EndDateVal is set)
                const passEndDateFilter = !endDateVal || recordDate <= endDateVal;

                // Record passes filter only if both start and end date conditions are met
                const isMatch = passStartDateFilter && passEndDateFilter;
                // if (!isMatch && rowIndex < 10) console.log(`Filter: Row ${rowIndex} date "${recordDate}" does not match range "${startDateVal}"-"${endDateVal}"`); // Debug non-matches
                return isMatch;
            });
            console.log(`Filter: Found ${filteredRecords.length} records matching date range filter.`);

        }
        // If no filters are set (both single and range are empty), filteredRecords remains originalFireRecords
        if (!singleDateVal && !startDateVal && !endDateVal) {
             console.log("Filter: No date filters applied. Displaying all records.");
        }


        // Re-initialize the table with the filtered data
        initializeDataTable(filteredRecords);
        console.log(`Filter: Filter applied. initializeDataTable called with ${filteredRecords.length} records.`);

         // Note: Map markers are NOT updated here as the map is in an iframe
         // generated statically by Python. Dynamic map filtering requires
         // using a JS map library in index.html instead of an iframe.
         // The LayerControl within the iframe is also static until reload.
    }

    // --- Function to clear date filters ---
    function clearDateFilters() {
        console.log("Filter: Clearing date filters...");
         const filterSection = document.querySelector("#filter-section"); // Select the filter section first
        const singleDateInput = filterSection ? filterSection.querySelector("#filter-single-date") : null;
        const startDateInput = filterSection ? filterSection.querySelector("#filter-start-date") : null;
        const endDateInput = filterSection ? filterSection.querySelector("#filter-end-date") : null;

        // Clear values if elements exist
        if(singleDateInput) singleDateInput.value = '';
        if(startDateInput) startDateInput.value = '';
        if(endDateInput) endDateInput.value = '';

        // Ensure range inputs are re-enabled if elements exist
         if(startDateInput) startDateInput.disabled = false;
         if(endDateInput) endDateInput.disabled = false;
         if(singleDateInput) singleDateInput.disabled = false; // Also re-enable single date

         // Trigger the filter application which will now use all records (as inputs are empty)
        applyDateFilters(); // Re-apply filters (which are now all clear)
         console.log("Filter: Filters cleared. Displaying all records.");
    }


    // --- Function to start the auto-refresh timer ---
    function startAutoRefresh() {
        console.log("Refresh: startAutoRefresh called.");
        // Ensure the countdown span and the indicator container exist before starting
        if (!countdownSpan || !refreshIndicator) {
             console.warn("Refresh: Refresh countdown span (#refresh-countdown) or indicator container (.auto-refresh-indicator) not found. Auto-refresh will not start.");
             // Optionally hide the whole refresh indicator if either part is missing
             if(refreshIndicator) refreshIndicator.style.display = 'none'; // Hide the container
             return; // Exit if elements not found
        }

        console.log(`Refresh: Starting auto-refresh timer for ${refreshIntervalSeconds} seconds.`);
        let secondsRemaining = refreshIntervalSeconds;

        // Clear any existing timer before starting a new one (important if startAutoRefresh is called multiple times)
        if (refreshIntervalId) {
            clearInterval(refreshIntervalId);
            console.log("Refresh: Cleared existing refresh interval.");
        }

        function updateCountdown() {
             const minutes = Math.floor(secondsRemaining / 60);
             const seconds = secondsRemaining % 60;
             // Ensure two digits for seconds
             const display = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
             countdownSpan.textContent = display; // Update the span text

             if (secondsRemaining <= 0) {
                 console.log("Refresh: Auto-refresh triggered. Reloading page...");
                 clearInterval(refreshIntervalId); // Stop timer before reloading
                 window.location.reload(); // Reload the entire page
             } else {
                 secondsRemaining--;
             }
        }

        // Update countdown immediately and then every second
        updateCountdown(); // Initial display
        refreshIntervalId = setInterval(updateCountdown, 1000); // Update every second
        console.log("Refresh: Auto-refresh interval started.");
    }

    // --- Initialize Collapsible Sections ---
     function initializeCollapsibles() {
        console.log("Collapsible: Initializing collapsible sections...");
        const sidebarSections = document.querySelectorAll("#left-sidebar section");

        if (sidebarSections.length === 0) {
             console.warn("Collapsible: No sidebar sections found (#left-sidebar section). Initialization skipped.");
        }

        sidebarSections.forEach(section => {
            // Find the first H2 that is a *direct* child of the section using :scope
            const header = section.querySelector(':scope > h2');

            if (header) {
                 console.log(`Collapsible: Found header for section: ${section.id || 'N/A'} (${header.textContent.trim()})`);
                 // Check if a content wrapper (.section-content) already exists as a direct child
                 let content = section.querySelector(':scope > .section-content');

                 if (!content) {
                    // If not, create one and move all siblings of h2 into it
                    console.log(`Collapsible: Wrapping content for section: ${section.id || 'N/A'}`);
                    content = document.createElement('div');
                    content.classList.add('section-content');
                    // Move all siblings of h2 *after* h2 into the new wrapper
                    let sibling = header.nextElementSibling;
                    while(sibling) {
                        const nextSibling = sibling.nextElementSibling; // Get next before moving
                         // Only move elements that are *direct* children of the section
                         if (sibling.parentElement === section) {
                            content.appendChild(sibling);
                         }
                        sibling = nextSibling;
                    }
                     section.appendChild(content); // Add the new wrapper back to the section
                     console.log(`Collapsible: Content wrapping complete for section: ${section.id || 'N/A'}.`);
                 } else {
                     console.log(`Collapsible: Content wrapper (.section-content) found for section: ${section.id || 'N/A'}. No wrapping needed.`);
                 }

                // Add classes and attributes to the header
                header.classList.add('collapsible-header'); // Add class for styling/identification
                header.setAttribute('tabindex', '0'); // Make it focusable (allows keyboard navigation)
                header.setAttribute('role', 'button'); // Indicate it's a button for assistive technologies
                header.setAttribute('aria-controls', content ? content.id || section.id + '-content' : ''); // Associate header with content (generate an ID if needed)
                if (content && !content.id) {
                     content.id = section.id + '-content'; // Give content an ID if it doesn't have one
                }


                // Determine initial state (expanded by default, collapse charts/table/detail list)
                // Check section IDs to decide initial state
                const isInitiallyCollapsed = section.id === 'charts-section' || section.id === 'data-table-section' || section.id === 'detail-list-panel'; // Add detail-list-panel if you re-add it

                if (isInitiallyCollapsed) {
                    section.classList.add('collapsed'); // Add collapsed class
                     header.setAttribute('aria-expanded', 'false'); // ARIA attribute for accessibility
                     console.log(`Collapsible: Section ${section.id} initially collapsed.`);
                     // CSS handles hiding .section-content when .collapsed is present
                } else {
                     section.classList.add('expanded'); // Add expanded class (optional, but good practice)
                     header.setAttribute('aria-expanded', 'true');
                     console.log(`Collapsible: Section ${section.id} initially expanded.`);
                     // CSS handles visibility of .section-content when .expanded is present or no class
                }

                // Add click listener to the header to toggle the state
                header.addEventListener('click', () => {
                    console.log(`Collapsible: Header clicked for section: ${section.id || 'N/A'}.`);
                    // Toggle the collapsed/expanded state on the section element
                    const isCollapsed = section.classList.toggle('collapsed');
                    section.classList.toggle('expanded', !isCollapsed); // Keep expanded/collapsed in sync
                     header.setAttribute('aria-expanded', !isCollapsed); // Update ARIA state

                    console.log(`Collapsible: Section ${section.id} toggled. Expanded: ${!isCollapsed}.`);

                     // Special handling for the DataTable section if it's being expanded
                     // This can sometimes help Simple-DataTables render correctly if initialized while hidden
                     if (!isCollapsed && section.id === 'data-table-section') {
                         // Delay the DataTable update slightly to allow the section to become visible
                         if (currentDataTableInstance && typeof currentDataTableInstance.update === 'function') {
                             console.log("Collapsible: Triggering DataTable update after expanding section.");
                             // A small delay (e.g., 50ms) gives the browser time to render the container
                             setTimeout(() => currentDataTableInstance.update(), 50);
                         } else {
                             console.warn("Collapsible: DataTable instance not found or update method missing after expanding table section.");
                         }
                     }
                });

                 // Add keypress listener for accessibility (Enter or Space key)
                 header.addEventListener('keypress', (event) => {
                      if (event.key === 'Enter' || event.key === ' ') { // Space key also common for buttons
                           console.log(`Collapsible: Header keypress (${event.key}) for section: ${section.id || 'N/A'}. Triggering click.`);
                           event.preventDefault(); // Prevent default browser actions (like scrolling with space)
                           header.click(); // Trigger the click event listener
                       }
                 });


            } else {
                 console.warn(`Collapsible Warning: Section with id '${section.id || 'N/A'}' found without a direct H2 header. Collapsible not initialized for this section.`, section);
                 // If no H2, ensure content is at least visible if not wrapped/controlled
                 const content = section.querySelector(':scope > .section-content');
                 if(content) {
                     content.style.display = 'block'; // Ensure visibility if not collapsible
                     console.log(`Collapsible: Ensured visibility for content of section: ${section.id || 'N/A'}.`);
                 }
            }
        });
        console.log("Collapsible initialization complete.");
     }


    // --- Initial Population and Event Listeners ---
    // Initialize collapsibles first, so the .section-content wrappers are ready and initial state is set.
    initializeCollapsibles();

    // 1. Populate Statistics Panel
    console.log("Population: Starting Stats Panel population.");
    // Select the stats section by its ID (#stats-section)
    const statsSection = document.querySelector("#stats-section");
    // Select the content wrapper *within* the stats section
    const statsContent = statsSection ? statsSection.querySelector('.section-content') : null;

    // Check if the section, its content wrapper, and the stats data exist
    if (statsSection && statsContent && dashboardData.stats) {
        console.log("Stats: Attempting to populate statistics panel...");
         // Select metric elements *inside* the content wrapper
         const metricElements = statsContent.querySelectorAll(".metric");
         console.log(`Stats: Found ${metricElements.length} metric elements in stats panel.`);
         let statsPopulatedCount = 0;

         if (metricElements.length === 0) {
              console.warn("Stats Warning: No metric elements found within the stats section content. Skipping population.");
              // Display a message if the HTML structure within .section-content is missing .metric divs
              statsContent.innerHTML = "<p>Structure métrique non configurée dans l'HTML.</p>";
         } else {
             metricElements.forEach(metricEl => {
                 const labelEl = metricEl.querySelector('.label');
                 const numberEl = metricEl.querySelector('.number');
                 if (labelEl && numberEl) {
                     const labelText = labelEl.textContent.trim(); // Get the text from the label
                     //console.log(`Processing metric label: "${labelText}"`); // Too chatty unless debugging
                     let valueToDisplay = '?'; // Default placeholder
                     let foundData = false; // Flag to check if we found corresponding data


                     // --- Map label text (French) to data keys from dashboardData.stats ---
                     // These keys must match the French labels defined in Python's dashboard_stats

                     if (labelText === 'Total Détections') {
                          if (dashboardData.stats.total_detections !== undefined) {
                             valueToDisplay = dashboardData.stats.total_detections;
                             foundData = true;
                          }
                          console.log(`Stats Check: Total Détections (Label: "${labelText}") -> Value: ${valueToDisplay}, Found: ${foundData}`);
                     } else if (dashboardData.stats.confidence_counts && dashboardData.stats.confidence_counts.hasOwnProperty(labelText)) {
                           // Check if labelText exists as a key directly in confidence_counts
                           valueToDisplay = dashboardData.stats.confidence_counts[labelText];
                           foundData = true;
                           console.log(`Stats Check: Confidence Count (Label: "${labelText}") -> Value: ${valueToDisplay}, Found: ${foundData}`);

                     }
                     // Add more mappings here for satellite counts if needed in separate metrics
                     // Example:
                     // else if (dashboardData.stats.satellite_counts && dashboardData.stats.satellite_counts.hasOwnProperty(labelText)) {
                     //     valueToDisplay = dashboardData.stats.satellite_counts[labelText];
                     //     foundData = true;
                     //     console.log(`Stats Check: Satellite Count (Label: "${labelText}") -> Value: ${valueToDisplay}, Found: ${foundData}`);
                     // }
                     // Add a fallback if the label is not mapped above
                     else {
                         console.warn(`Stats Warning: Label "${labelText}" found in HTML but not mapped in JS data lookup.`);
                     }


                     // Only update the textContent if we found valid data (number >= 0)
                      if (foundData && typeof valueToDisplay === 'number' && valueToDisplay >= 0) {
                          numberEl.textContent = valueToDisplay;
                           statsPopulatedCount++;
                          //console.log(`Updated "${labelText}" with value: ${valueToDisplay}`); // Too chatty unless debugging
                      } else {
                          numberEl.textContent = '?'; // Keep placeholder
                          if (!foundData) {
                              console.warn(`Stats Warning: Data for label "${labelText}" not found or is undefined in dashboardData.stats.`);
                          } else if (typeof valueToDisplay !== 'number' || valueToDisplay < 0) {
                               console.warn(`Stats Warning: Data found for label "${labelText}" is not a valid number (>=0). Value:`, valueToDisplay);
                          }
                      }
                 } // Close if (labelEl && numberEl)
                 });
                  console.log(`Stats: Statistics panel population attempt finished. ${statsPopulatedCount} metrics updated.`);
             }


             // Update header subtitle text with date range if available
             const headerSubtitleP = document.querySelector('header p.header-subtitle');
             if(headerSubtitleP && dashboardData.stats.recent_date_range && dashboardData.stats.recent_date_range !== 'N/A') {
                  // Replace the default text with the date range from stats
                  // Ensure the original text "Données MODIS" and "– NASA FIRMS" are kept if desired
                  headerSubtitleP.textContent = `Données MODIS (${dashboardData.stats.recent_date_range}) – NASA FIRMS`;
                  console.log("Stats: Updated header subtitle with date range.");
             } else if (headerSubtitleP) {
                 // If date range is not available, maybe update the text slightly or keep default
                 headerSubtitleP.textContent = `Données récentes – NASA FIRMS`; // Keep the default if no date range
                 console.log("Stats: Date range not available, kept default header subtitle.");
             } else {
                  console.warn("Stats Warning: Header subtitle element not found.");
             }


        } else {
             // Display fallback message if the stats object is missing entirely or panels/content are missing
             const targetEl = statsContent || statsSection; // Target content div if it exists, otherwise the section
             if(targetEl) {
                 targetEl.innerHTML = "<p>Données statistiques non disponibles ou structure HTML/JSON incorrecte.</p>";
                 // Ensure the header still says "Statistiques Clés" if the content is replaced
                 const headerEl = statsSection ? statsSection.querySelector(':scope > h2') : null; // Target direct H2
                 if (headerEl) headerEl.textContent = "Statistiques Clés"; // Reset header text
                 console.warn("Stats Error: Displayed fallback message in stats panel.");
             }
             console.error("Stats Error: Stats section (#stats-section), its .section-content, or dashboardData.stats is missing/null.");
        }


        // 2. Populate Detail List Panel (if container exists and data is available)
         // This is an optional panel, often hidden or showing limited data.
         // It targets the .section-content wrapper created by initializeCollapsibles
        const detailListSection = document.querySelector("#detail-list-panel"); // Assuming #detail-list-panel is the section ID
        const detailListContainer = detailListSection ? detailListSection.querySelector(".section-content") : null; // Target content wrapper
        const detailListData = dashboardData.detailList || []; // Ensure it's an array, default to empty

        if (detailListContainer) {
             console.log("Detail List: Attempting to populate detail list panel...");
             detailListContainer.innerHTML = ''; // Clear loading message/placeholders

             if (detailListData.length > 0) {
                 console.log(`Detail List: data available: ${detailListData.length} items.`);
                 // Optional: Limit items shown in the list for performance/UI if necessary
                 // const limitedDetailList = detailListData.slice(0, 100); // Example: show only first 100

                 detailListData.forEach((item, index) => {
                     // Log sample item for debugging
                     if (index < 5) {
                          console.log(`Detail List: Processing item ${index}:`, item);
                     }

                     const div = document.createElement("div");
                     div.classList.add("list-item");
                     // Check item properties before displaying - use the keys from Python detail_list_data
                     const date = item.date || '-';
                     const time = item.time || '-';
                     const location = item.location || '-';
                     const confidence = item.confidence || '-';

                     // Construct the display string
                     div.textContent = `${date} ${time} | ${location} | Confiance: ${confidence}`;
                     detailListContainer.appendChild(div);
                 });
                 console.log("Detail List: populated.");
             } else {
                 detailListContainer.textContent = "Aucune donnée de détection récente pour la liste.";
                 console.log("Detail List: No data available or data is empty in dashboardData.detailList.");
             }
        } else {
            console.log("Detail List Warning: Detail list container (#detail-list-panel .section-content) not found. Skipping population.");
        }


    // 3. Initial Table Population and DataTable Initialization
    // Start by showing all original records initially
    console.log("Initialization: Initializing data table with all original records...");
    initializeDataTable(originalFireRecords); // Call the function with all data


    // 4. Add Event Listeners for Date Filters
    console.log("Event Listeners: Adding filter event listeners.");
    // Select filter inputs and buttons
    const filterSection = document.querySelector("#filter-section"); // Select the filter section first
    const applyFiltersBtn = filterSection ? filterSection.querySelector("#apply-filters-btn") : null;
    const clearFiltersBtn = filterSection ? filterSection.querySelector("#clear-filters-btn") : null;
    const singleDateInput = filterSection ? filterSection.querySelector("#filter-single-date") : null;
    const startDateInput = filterSection ? filterSection.querySelector("#filter-start-date") : null;
    const endDateInput = filterSection ? filterSection.querySelector("#filter-end-date") : null;

    // Add event listeners if elements are found
    if(applyFiltersBtn) {
         applyFiltersBtn.addEventListener('click', applyDateFilters);
         console.log("Event Listeners: Added listener for #apply-filters-btn.");
    } else {
         console.warn("Event Listeners Warning: #apply-filters-btn not found.");
    }

     if(clearFiltersBtn) {
         clearFiltersBtn.addEventListener('click', clearDateFilters);
          console.log("Event Listeners: Added listener for #clear-filters-btn.");
     } else {
          console.warn("Event Listeners Warning: #clear-filters-btn not found.");
     }

     // Add listeners to manage single date vs range date inputs (basic logic)
     if(singleDateInput && startDateInput && endDateInput) {
         console.log("Event Listeners: Date input elements found, adding state management listeners.");
         // Function to manage input states: disables range if single is set, and vice versa
         const manageDateInputStates = () => {
              // console.log("Managing date input states..."); // Too chatty
              if (singleDateInput.value) {
                  // If single date is set, disable range inputs and clear their values
                  // Add checks to avoid unnecessary DOM manipulation if already disabled
                  if(!startDateInput.disabled) {
                       startDateInput.disabled = true;
                       startDateInput.value = ''; // Clear value when disabling
                       // console.log("Single date set, disabling start date input.");
                  }
                   if(!endDateInput.disabled) {
                       endDateInput.disabled = true;
                       endDateInput.value = ''; // Clear value when disabling
                       // console.log("Single date set, disabling end date input.");
                   }
              } else if (startDateInput.value || endDateInput.value) {
                  // If range dates are set, disable single date input and clear its value
                  if(!singleDateInput.disabled) {
                       singleDateInput.disabled = true;
                       singleDateInput.value = ''; // Clear value when disabling
                       // console.log("Range date set, disabling single date input.");
                  }
                  // Ensure range inputs are enabled
                  if(startDateInput.disabled) startDateInput.disabled = false;
                  if(endDateInput.disabled) endDateInput.disabled = false;

              } else {
                  // If nothing is set, ensure all are enabled
                  if(singleDateInput.disabled) {
                       singleDateInput.disabled = false;
                       // console.log("No date set, enabling single date input.");
                  }
                   if(startDateInput.disabled) {
                        startDateInput.disabled = false;
                        // console.log("No date set, enabling start date input.");
                   }
                   if(endDateInput.disabled) {
                        endDateInput.disabled = false;
                         // console.log("No date set, enabling end date input.");
                   }
              }
              // console.log(`Input states: Single: "${singleDateInput.value}" (disabled: ${singleDateInput.disabled}), Range: "${startDateInput.value}" - "${endDateInput.value}" (disabled: ${startDateInput.disabled})`); // Too chatty for production
         };

         // Use 'input' event for immediate feedback as user types/clears
         // Use 'change' event for date pickers (value is committed when picker is closed)
         singleDateInput.addEventListener('input', manageDateInputStates);
         singleDateInput.addEventListener('change', manageDateInputStates);

         startDateInput.addEventListener('input', manageDateInputStates);
         startDateInput.addEventListener('change', manageDateInputStates);

         endDateInput.addEventListener('input', manageDateInputStates);
         endDateInput.addEventListener('change', manageDateInputStates);


         // Initial check in case date inputs are pre-filled by the browser (e.g., from history)
         manageDateInputStates();

     } else {
          console.warn("Event Listeners Warning: Date input elements not all found (#filter-single-date, #filter-start-date, #filter-end-date). Single date vs range input state logic not applied.");
     }


    // 5. Start Auto-Refresh Timer
    console.log("Refresh: Checking for auto-refresh elements.");
    // Ensure the countdown span and the indicator container exist before starting the timer
    if (countdownSpan && refreshIndicator) {
       startAutoRefresh();
    } else {
       console.warn("Refresh: Refresh countdown span (#refresh-countdown) or indicator container (.auto-refresh-indicator) not found. Auto-refresh will not start.");
       // Optionally hide the whole refresh indicator if either part is missing
       if(refreshIndicator) refreshIndicator.style.display = 'none'; // Hide the container
    }


    console.log("Initial dashboard setup complete.");

    // ========== INITIALIZE ADVANCED FEATURES ==========
    console.log("Initializing advanced features...");
    
    // 1. Setup Alert System
    const alertSoundToggle = document.getElementById('alert-sound-toggle');
    const alertThresholdInput = document.getElementById('alert-threshold-input');
    
    if (alertSoundToggle) {
        alertSoundToggle.addEventListener('change', (e) => {
            alertSystem.soundEnabled = e.target.checked;
            console.log(`Alert sound ${alertSystem.soundEnabled ? 'enabled' : 'disabled'}`);
        });
    }
    
    if (alertThresholdInput) {
        alertThresholdInput.addEventListener('change', (e) => {
            const value = parseInt(e.target.value);
            if (value >= 0 && value <= 100) {
                alertSystem.highConfidenceThreshold = value;
                console.log(`Alert threshold set to ${value}%`);
            }
        });
    }
    
    // Check for new fires on initial load
    alertSystem.checkForNewFires(originalFireRecords);
    
    // 2. Initialize Weather System
    if (originalFireRecords.length > 0) {
        // Calculate center coordinates from data
        const lats = originalFireRecords.map(r => parseFloat(r[2])).filter(n => !isNaN(n));
        const lons = originalFireRecords.map(r => parseFloat(r[3])).filter(n => !isNaN(n));
        
        if (lats.length > 0 && lons.length > 0) {
            const centerLat = lats.reduce((a, b) => a + b) / lats.length;
            const centerLon = lons.reduce((a, b) => a + b) / lons.length;
            weatherSystem.updateWeatherPanel(centerLat, centerLon);
        }
    }
    
    // 3. Initialize Predictive Analysis
    predictiveAnalysis.analyzePatterns(originalFireRecords);
    
    // 4. Initialize Historical Dashboard
    historicalDashboard.initialize();
    historicalDashboard.saveCurrentData(dashboardData.stats, originalFireRecords);
    historicalDashboard.displayComparison();
    
    // 5. Initialize Zones of Interest
    zonesOfInterest.initialize();
    zonesOfInterest.displayZones();
    
    console.log("Advanced features initialized successfully.");

}); // End DOMContentLoaded
// --- Fin du code JavaScript front-end amélioré ---
