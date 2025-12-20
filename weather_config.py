"""
Configuration file for Weather API integration
"""

# OpenWeatherMap API Configuration
# Get your free API key from: https://openweathermap.org/api
OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

# Weather display configuration
WEATHER_ENABLED = False  # Set to True when you have a valid API key
WEATHER_UPDATE_INTERVAL = 3600  # Update every hour (in seconds)

# Temperature units: 'metric' (Celsius), 'imperial' (Fahrenheit), or 'standard' (Kelvin)
WEATHER_UNITS = 'metric'

# Language for weather descriptions
WEATHER_LANG = 'fr'  # French

# Cities to monitor in Chad
CHAD_CITIES = [
    {"name": "N'Djamena", "lat": 12.1348, "lon": 15.0557},
    {"name": "Moundou", "lat": 8.5667, "lon": 16.0833},
    {"name": "Abéché", "lat": 13.8292, "lon": 20.8324},
    {"name": "Sarh", "lat": 9.1500, "lon": 18.3833},
    {"name": "Faya-Largeau", "lat": 17.9167, "lon": 19.1167},
]

# Weather display options
WEATHER_SHOW_TEMPERATURE = True
WEATHER_SHOW_HUMIDITY = True
WEATHER_SHOW_WIND = True
WEATHER_SHOW_PRECIPITATION = True
WEATHER_SHOW_ICON = True

# Alert thresholds
WEATHER_HIGH_TEMP_THRESHOLD = 40  # Celsius
WEATHER_LOW_HUMIDITY_THRESHOLD = 20  # Percentage
WEATHER_HIGH_WIND_THRESHOLD = 50  # km/h

# Display format
WEATHER_CARD_STYLE = 'cyberpunk'  # Options: 'cyberpunk', 'minimal', 'detailed'
