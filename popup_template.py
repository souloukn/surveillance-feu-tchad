# Ultra-modern popup template with weather and charts - Qoder style

def create_modern_popup(fire, province, department, weather, risk_level, risk_color, risk_score, base_color, mid_color, intensity_label, i):
    """Create ultra-modern popup with weather data and inline charts"""
    
    # Weather section HTML
    weather_html = ""
    if weather:
        weather_html = f"""
        <!-- Weather Data Section -->
        <div style="background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #4CAF50; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="font-weight: 600; color: #2E7D32; font-size: 13px; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                ☁️ DONNÉES MÉTÉO EN TEMPS RÉEL
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
                <div style="background: rgba(255,255,255,0.7); padding: 8px; border-radius: 6px;">
                    <div style="color: #666; font-size: 10px; margin-bottom: 3px;">🌡️ TEMPÉRATURE</div>
                    <div style="font-weight: 700; font-size: 18px; color: #FF6F00;">{weather['temp']:.1f}°C</div>
                    <div style="font-size: 10px; color: #888;">{weather['description']}</div>
                </div>
                <div style="background: rgba(255,255,255,0.7); padding: 8px; border-radius: 6px;">
                    <div style="color: #666; font-size: 10px; margin-bottom: 3px;">💧 HUMIDITÉ</div>
                    <div style="font-weight: 700; font-size: 18px; color: #2196F3;">{weather['humidity']}%</div>
                    <div style="height: 4px; background: #E0E0E0; border-radius: 2px; margin-top: 3px; overflow: hidden;">
                        <div style="height: 100%; width: {weather['humidity']}%; background: linear-gradient(90deg, #2196F3, #64B5F6); border-radius: 2px;"></div>
                    </div>
                </div>
                <div style="background: rgba(255,255,255,0.7); padding: 8px; border-radius: 6px;">
                    <div style="color: #666; font-size: 10px; margin-bottom: 3px;">🌬️ VENT</div>
                    <div style="font-weight: 700; font-size: 18px; color: #00BCD4;">{weather['wind_speed']:.1f} m/s</div>
                    <div style="font-size: 10px; color: #888;">Direction: {weather['wind_deg']}°</div>
                </div>
                <div style="background: rgba(255,255,255,0.7); padding: 8px; border-radius: 6px;">
                    <div style="color: #666; font-size: 10px; margin-bottom: 3px;">🌡️ PRESSION</div>
                    <div style="font-weight: 700; font-size: 18px; color: #673AB7;">{weather['pressure']} hPa</div>
                </div>
            </div>
        </div>
        """
    else:
        # Fallback when weather data is not available
        weather_html = f"""
        <!-- Weather Data Not Available -->
        <div style="background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #FF9800; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="font-weight: 600; color: #E65100; font-size: 13px; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                ⚠️ DONNÉES MÉTÉO
            </div>
            <div style="font-size: 11px; color: #666;">
                Données météorologiques non disponibles pour cette localisation. Position: {fire['lat']:.2f}°N, {fire['lon']:.2f}°E
            </div>
        </div>
        """
    
    # Mini SVG flame for header
    svg_flame_mini = f"""
    <svg width="28" height="28" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <path d="M 50 10 Q 30 30 35 50 Q 30 70 50 95 Q 70 70 65 50 Q 70 30 50 10 Z" 
              fill="url(#flameGrad{i})" opacity="0.95"/>
        <ellipse cx="50" cy="55" rx="8" ry="15" fill="#FFF" opacity="0.7"/>
        <defs>
            <radialGradient id="flameGrad{i}" cx="50%" cy="70%" r="60%">
                <stop offset="0%" style="stop-color:#FFAA00;stop-opacity:1" />
                <stop offset="100%" style="stop-color:{base_color};stop-opacity:0.8" />
            </radialGradient>
        </defs>
    </svg>
    """
    
    # Fire intensity chart (inline SVG)
    brightness_percent = min(100, (fire['brightness'] - 300) / 1.5)
    confidence_percent = fire['confidence']
    
    popup_html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif; 
                min-width: 380px; max-width: 420px; background: #FAFAFA; border-radius: 12px; overflow: hidden; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);">
        
        <!-- Modern Header with Glassmorphism Effect -->
        <div style="background: linear-gradient(135deg, {base_color} 0%, {mid_color} 100%); 
                    padding: 18px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                        background: url('data:image/svg+xml,%3Csvg width=\"40\" height=\"40\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cg fill=\"%23fff\" opacity=\"0.05\"%3E%3Ccircle cx=\"5\" cy=\"5\" r=\"3\"/%3E%3Ccircle cx=\"25\" cy=\"15\" r=\"2\"/%3E%3Ccircle cx=\"35\" cy=\"25\" r=\"3\"/%3E%3Ccircle cx=\"15\" cy=\"35\" r=\"2\"/%3E%3C/g%3E%3C/svg%3E'); 
                        opacity: 0.3;"></div>
            <div style="display: flex; align-items: center; justify-content: space-between; position: relative; z-index: 1;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(255,255,255,0.25); padding: 8px; border-radius: 12px; backdrop-filter: blur(10px);">
                        {svg_flame_mini}
                    </div>
                    <div>
                        <h3 style="margin: 0; color: white; font-size: 19px; font-weight: 700; letter-spacing: -0.5px; text-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                            Alerte Feu Actif
                        </h3>
                        <div style="background: rgba(255,255,255,0.3); padding: 4px 12px; border-radius: 20px; 
                                    font-size: 11px; font-weight: 700; color: white; margin-top: 6px; display: inline-block;
                                    backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.3);">
                            ⚡ {intensity_label}
                        </div>
                    </div>
                </div>
                <div style="background: {risk_color}; color: white; padding: 8px 14px; border-radius: 20px; 
                            font-size: 12px; font-weight: 700; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                            border: 2px solid rgba(255,255,255,0.3);">
                    🎯 {risk_score}%
                </div>
            </div>
        </div>
        
        <div style="padding: 16px; background: white;">
            
            <!-- Risk Assessment Banner -->
            <div style="background: linear-gradient(135deg, {risk_color}15 0%, {risk_color}25 100%); 
                        padding: 14px; border-radius: 10px; margin-bottom: 16px; 
                        border-left: 4px solid {risk_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-weight: 700; color: {risk_color}; font-size: 14px; margin-bottom: 4px;">
                            🔥 NIVEAU DE RISQUE: {risk_level}
                        </div>
                        <div style="font-size: 11px; color: #666; line-height: 1.4;">
                            {'⚠️ Conditions météo extrêmes détectées' if risk_score >= 80 else '⚠️ Surveillance renforcée requise' if risk_score >= 60 else '✓ Conditions sous surveillance'}
                        </div>
                    </div>
                    <div style="font-size: 32px;">{chr(128293) if risk_score >= 80 else chr(9888) if risk_score >= 60 else chr(128994)}</div>
                </div>
            </div>
            
            {weather_html}
            
            <!-- Administrative Location -->
            <div style="background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); padding: 12px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #2196F3; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-weight: 600; color: #1565C0; font-size: 13px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                    📍 LOCALISATION
                </div>
                <div style="display: grid; grid-template-columns: auto 1fr; gap: 8px; font-size: 12px;">
                    <div style="color: #555; font-weight: 500;">🗺️ Province:</div>
                    <div style="font-weight: 700; color: #1976D2; text-align: right;">{province}</div>
                    <div style="color: #555; font-weight: 500;">🏘️ Département:</div>
                    <div style="font-weight: 700; color: #1976D2; text-align: right;">{department}</div>
                    <div style="color: #555; font-weight: 500;">📍 GPS:</div>
                    <div style="font-weight: 600; color: #1976D2; font-size: 10px; text-align: right;">{fire['lat']:.4f}°N, {fire['lon']:.4f}°E</div>
                </div>
            </div>
            
            <!-- Fire Metrics with Inline Charts -->
            <div style="background: #F5F5F5; padding: 14px; border-radius: 8px; margin-bottom: 16px;">
                <div style="font-weight: 600; color: #424242; font-size: 13px; margin-bottom: 12px;">
                    📊 MÉTRIQUES DU FEU
                </div>
                
                <!-- Brightness Chart -->
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 12px; color: #666; font-weight: 500;">🌡️ Luminosité</span>
                        <span style="font-size: 14px; font-weight: 700; color: {'#D32F2F' if fire['brightness'] > 380 else '#F57C00' if fire['brightness'] > 340 else '#388E3C'};">
                            {fire['brightness']:.1f} K
                        </span>
                    </div>
                    <div style="height: 8px; background: #E0E0E0; border-radius: 10px; overflow: hidden; position: relative;">
                        <div style="height: 100%; width: {brightness_percent}%; 
                                    background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 50%, #FFAA00 100%); 
                                    border-radius: 10px; transition: width 0.6s ease;
                                    box-shadow: 0 0 10px rgba(255, 107, 107, 0.5);"></div>
                    </div>
                </div>
                
                <!-- Confidence Chart -->
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 12px; color: #666; font-weight: 500;">🎯 Niveau de confiance</span>
                        <span style="font-size: 14px; font-weight: 700; color: {'#4CAF50' if fire['confidence'] > 80 else '#FF9800' if fire['confidence'] > 60 else '#F44336'};">
                            {fire['confidence']}%
                        </span>
                    </div>
                    <div style="height: 8px; background: #E0E0E0; border-radius: 10px; overflow: hidden;">
                        <div style="height: 100%; width: {confidence_percent}%; 
                                    background: linear-gradient(90deg, {'#4CAF50' if fire['confidence'] > 80 else '#FF9800' if fire['confidence'] > 60 else '#F44336'}, {'#66BB6A' if fire['confidence'] > 80 else '#FFA726' if fire['confidence'] > 60 else '#EF5350'}); 
                                    border-radius: 10px; transition: width 0.6s ease;"></div>
                    </div>
                </div>
                
                <!-- Risk Score Radial Chart -->
                <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid #E0E0E0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 11px; color: #666; margin-bottom: 2px;">Score de risque global</div>
                            <div style="font-size: 18px; font-weight: 700; color: {risk_color};">{risk_score}/100</div>
                        </div>
                        <svg width="50" height="50" viewBox="0 0 50 50">
                            <circle cx="25" cy="25" r="20" fill="none" stroke="#E0E0E0" stroke-width="4"/>
                            <circle cx="25" cy="25" r="20" fill="none" stroke="{risk_color}" stroke-width="4"
                                    stroke-dasharray="{risk_score * 1.257} 125.7" 
                                    stroke-linecap="round" transform="rotate(-90 25 25)"
                                    style="transition: stroke-dasharray 0.6s ease;"/>
                            <text x="25" y="30" text-anchor="middle" font-size="12" font-weight="700" fill="{risk_color}">{risk_score}</text>
                        </svg>
                    </div>
                </div>
            </div>
            
            <!-- Timestamp and Satellite Info -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                <div style="background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); padding: 10px; border-radius: 6px; border-left: 3px solid #FF9800;">
                    <div style="font-size: 10px; color: #666; margin-bottom: 3px;">📅 DATE</div>
                    <div style="font-size: 13px; font-weight: 700; color: #E65100;">{fire['date']}</div>
                </div>
                <div style="background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%); padding: 10px; border-radius: 6px; border-left: 3px solid #9C27B0;">
                    <div style="font-size: 10px; color: #666; margin-bottom: 3px;">⏰ HEURE</div>
                    <div style="font-size: 13px; font-weight: 700; color: #6A1B9A;">{fire['time']}</div>
                </div>
            </div>
            
            <div style="background: linear-gradient(135deg, #E8EAF6 0%, #C5CAE9 100%); padding: 10px; border-radius: 6px; text-align: center; border-left: 3px solid #3F51B5;">
                <div style="font-size: 10px; color: #666; margin-bottom: 3px;">🛰️ SATELLITE</div>
                <div style="font-size: 13px; font-weight: 700; color: #1A237E;">{fire['satellite']}</div>
            </div>
            
        </div>
        
        <!-- Footer with action button style -->
        <div style="background: linear-gradient(135deg, #ECEFF1 0%, #CFD8DC 100%); padding: 12px; text-align: center; border-top: 1px solid #B0BEC5;">
            <div style="font-size: 10px; color: #546E7A; font-weight: 500;">
                ⚡ Données en temps réel • Dernière mise à jour: {fire['date']} {fire['time']}
            </div>
        </div>
    </div>
    """
    
    return popup_html
