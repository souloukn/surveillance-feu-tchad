"""
Enhanced Cyberpunk Popup Template for Fire Detection Dashboard
Provides advanced popup styling with animations, gradients, and data visualization
"""

def create_cyberpunk_popup(
    date, time, latitude, longitude, brightness, confidence, satellite,
    brightness_raw=None, frp=None, scan=None, track=None
):
    """
    Create an enhanced cyberpunk-style popup with advanced styling and animations
    
    Args:
        date: Detection date (string)
        time: Detection time (string)
        latitude: Latitude coordinate (float or string)
        longitude: Longitude coordinate (float or string)
        brightness: Brightness value with unit (string)
        confidence: Confidence level (string)
        satellite: Satellite name (string)
        brightness_raw: Raw brightness value for color coding (optional)
        frp: Fire Radiative Power (optional)
        scan: Scan value (optional)
        track: Track value (optional)
    
    Returns:
        HTML string for the popup
    """
    
    # Determine confidence color and icon
    confidence_colors = {
        'Haute': {'bg': 'rgba(255, 0, 64, 0.15)', 'border': '#ff0040', 'glow': 'rgba(255, 0, 64, 0.5)', 'icon': '🔴'},
        'Nominale': {'bg': 'rgba(255, 140, 0, 0.15)', 'border': '#ff8c00', 'glow': 'rgba(255, 140, 0, 0.5)', 'icon': '🟠'},
        'Basse': {'bg': 'rgba(0, 255, 136, 0.15)', 'border': '#00ff88', 'glow': 'rgba(0, 255, 136, 0.5)', 'icon': '🟢'},
    }
    
    conf_style = confidence_colors.get('Nominale', confidence_colors['Nominale'])
    for key in confidence_colors:
        if key in confidence:
            conf_style = confidence_colors[key]
            break
    
    # Determine brightness level and icon
    brightness_icon = '🔥'
    brightness_color = '#ff8c00'
    if brightness_raw:
        try:
            b_val = float(brightness_raw)
            if b_val >= 400:
                brightness_icon = '🔥🔥🔥'
                brightness_color = '#ff0040'
            elif b_val >= 360:
                brightness_icon = '🔥🔥'
                brightness_color = '#ff6b6b'
            elif b_val >= 330:
                brightness_icon = '🔥'
                brightness_color = '#ff8c00'
        except:
            pass
    
    # Satellite icon
    satellite_icon = '🛰️'
    satellite_color = '#00d9ff'
    
    # Build additional info section if available
    additional_info = ""
    if frp or scan or track:
        additional_info = '<div class="popup-section">'
        if frp:
            additional_info += f'<div class="popup-data-row"><span class="popup-label">⚡ FRP:</span><span class="popup-value highlight-cyan">{frp} MW</span></div>'
        if scan:
            additional_info += f'<div class="popup-data-row"><span class="popup-label">📡 Scan:</span><span class="popup-value">{scan}</span></div>'
        if track:
            additional_info += f'<div class="popup-data-row"><span class="popup-label">📍 Track:</span><span class="popup-value">{track}</span></div>'
        additional_info += '</div>'
    
    popup_html = f"""
    <div class="cyber-popup">
        <style>
            .cyber-popup {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, rgba(5, 8, 16, 0.98) 0%, rgba(10, 14, 26, 0.98) 100%);
                backdrop-filter: blur(20px);
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 12px;
                padding: 0;
                margin: 0;
                color: #e0f3ff;
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.3), inset 0 0 20px rgba(0, 255, 255, 0.05);
                min-width: 280px;
                overflow: hidden;
                position: relative;
            }}
            
            .cyber-popup::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, transparent, #00ffff, #ff00ff, transparent);
                animation: scanline 3s linear infinite;
            }}
            
            @keyframes scanline {{
                0%, 100% {{ opacity: 0.3; }}
                50% {{ opacity: 0.8; }}
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 0.6; transform: scale(1); }}
                50% {{ opacity: 1; transform: scale(1.05); }}
            }}
            
            @keyframes glow {{
                0%, 100% {{ text-shadow: 0 0 10px currentColor; }}
                50% {{ text-shadow: 0 0 20px currentColor, 0 0 30px currentColor; }}
            }}
            
            .popup-header {{
                background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(157, 0, 255, 0.1));
                padding: 12px 16px;
                border-bottom: 1px solid rgba(0, 255, 255, 0.2);
                position: relative;
            }}
            
            .popup-title {{
                font-family: 'Orbitron', monospace;
                font-size: 14px;
                font-weight: 700;
                background: linear-gradient(90deg, #00ffff, #00d9ff, #ff00ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: 1.5px;
                margin: 0 0 8px 0;
                animation: glow 2s ease-in-out infinite;
            }}
            
            .popup-datetime {{
                font-size: 11px;
                color: rgba(0, 255, 255, 0.8);
                font-weight: 500;
                letter-spacing: 0.5px;
            }}
            
            .popup-body {{
                padding: 14px 16px;
            }}
            
            .popup-section {{
                margin-bottom: 12px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(0, 255, 255, 0.1);
            }}
            
            .popup-section:last-child {{
                margin-bottom: 0;
                padding-bottom: 0;
                border-bottom: none;
            }}
            
            .popup-data-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 6px 0;
                transition: all 0.3s ease;
            }}
            
            .popup-data-row:hover {{
                transform: translateX(3px);
                background: rgba(0, 255, 255, 0.05);
                margin: 0 -8px;
                padding: 6px 8px;
                border-radius: 4px;
            }}
            
            .popup-label {{
                font-size: 11px;
                color: rgba(0, 255, 255, 0.7);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .popup-value {{
                font-family: 'Orbitron', monospace;
                font-size: 12px;
                font-weight: 600;
                color: #ffffff;
                text-align: right;
            }}
            
            .highlight-cyan {{
                color: #00ffff;
                text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
            }}
            
            .highlight-fire {{
                color: {brightness_color};
                text-shadow: 0 0 10px {brightness_color};
                animation: pulse 2s ease-in-out infinite;
            }}
            
            .confidence-badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 10px;
                background: {conf_style['bg']};
                border: 1px solid {conf_style['border']};
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                color: {conf_style['border']};
                text-shadow: 0 0 8px {conf_style['glow']};
                box-shadow: 0 0 15px {conf_style['glow']};
            }}
            
            .satellite-badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 10px;
                background: rgba(0, 217, 255, 0.15);
                border: 1px solid {satellite_color};
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                color: {satellite_color};
                text-shadow: 0 0 8px rgba(0, 217, 255, 0.5);
            }}
            
            .popup-coordinates {{
                background: linear-gradient(135deg, rgba(0, 255, 255, 0.05), rgba(157, 0, 255, 0.05));
                border: 1px solid rgba(0, 255, 255, 0.15);
                border-radius: 6px;
                padding: 10px;
                margin-top: 10px;
            }}
            
            .coord-row {{
                display: grid;
                grid-template-columns: 40px 1fr;
                gap: 8px;
                align-items: center;
                padding: 4px 0;
            }}
            
            .coord-icon {{
                font-size: 16px;
            }}
            
            .coord-value {{
                font-family: 'Orbitron', monospace;
                font-size: 11px;
                color: #00ffff;
                text-shadow: 0 0 8px rgba(0, 255, 255, 0.4);
            }}
            
            .popup-footer {{
                background: linear-gradient(135deg, rgba(0, 255, 255, 0.05), rgba(157, 0, 255, 0.05));
                padding: 10px 16px;
                border-top: 1px solid rgba(0, 255, 255, 0.2);
                font-size: 9px;
                color: rgba(0, 255, 255, 0.6);
                text-align: center;
                letter-spacing: 0.5px;
            }}
        </style>
        
        <div class="popup-header">
            <div class="popup-title">🔥 DÉTECTION FEU</div>
            <div class="popup-datetime">📅 {date} • 🕐 {time}</div>
        </div>
        
        <div class="popup-body">
            <div class="popup-section">
                <div class="popup-data-row">
                    <span class="popup-label">🌡️ Luminosité:</span>
                    <span class="popup-value highlight-fire">{brightness_icon} {brightness}</span>
                </div>
                <div class="popup-data-row">
                    <span class="popup-label">📊 Confiance:</span>
                    <span class="confidence-badge">{conf_style['icon']} {confidence}</span>
                </div>
                <div class="popup-data-row">
                    <span class="popup-label">🛰️ Satellite:</span>
                    <span class="satellite-badge">{satellite_icon} {satellite}</span>
                </div>
            </div>
            
            {additional_info}
            
            <div class="popup-coordinates">
                <div class="coord-row">
                    <span class="coord-icon">📍</span>
                    <span class="coord-value">LAT: {latitude}°N</span>
                </div>
                <div class="coord-row">
                    <span class="coord-icon">🧭</span>
                    <span class="coord-value">LON: {longitude}°E</span>
                </div>
            </div>
        </div>
        
        <div class="popup-footer">
            SURVEILLANCE TEMPS RÉEL • NASA FIRMS
        </div>
    </div>
    """
    
    return popup_html


def create_simple_popup(date, time, latitude, longitude, brightness, confidence, satellite):
    """
    Create a simpler version of the cyberpunk popup (for performance on maps with many markers)
    
    Args:
        Same as create_cyberpunk_popup but without optional parameters
    
    Returns:
        HTML string for the popup
    """
    
    popup_html = f"""
    <div style="
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #050810 0%, #0a0e1a 100%);
        border: 2px solid rgba(0, 255, 255, 0.3);
        border-radius: 8px;
        padding: 12px;
        color: #e0f3ff;
        min-width: 220px;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    ">
        <div style="
            font-family: 'Orbitron', monospace;
            font-size: 12px;
            font-weight: 700;
            color: #00ffff;
            margin-bottom: 8px;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        ">🔥 DÉTECTION FEU</div>
        
        <div style="font-size: 10px; color: rgba(0, 255, 255, 0.8); margin-bottom: 10px;">
            📅 {date} • 🕐 {time}
        </div>
        
        <div style="
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 11px;
        ">
            <span style="color: rgba(0, 255, 255, 0.7);">🌡️ Luminosité:</span>
            <span style="font-weight: 600; color: #ff8c00;">{brightness}</span>
        </div>
        
        <div style="
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 11px;
        ">
            <span style="color: rgba(0, 255, 255, 0.7);">📊 Confiance:</span>
            <span style="font-weight: 600;">{confidence}</span>
        </div>
        
        <div style="
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 11px;
        ">
            <span style="color: rgba(0, 255, 255, 0.7);">🛰️ Satellite:</span>
            <span style="font-weight: 600; color: #00d9ff;">{satellite}</span>
        </div>
        
        <div style="
            margin-top: 10px;
            padding: 8px;
            background: rgba(0, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 255, 0.15);
            border-radius: 4px;
            font-size: 10px;
        ">
            <div>📍 LAT: <span style="color: #00ffff;">{latitude}°N</span></div>
            <div style="margin-top: 3px;">🧭 LON: <span style="color: #00ffff;">{longitude}°E</span></div>
        </div>
    </div>
    """
    
    return popup_html
