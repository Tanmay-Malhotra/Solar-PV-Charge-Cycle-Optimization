import requests
from datetime import datetime, timedelta
import math

def get_coordinates(city, state, country, api_key):
    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": f"{city},{state},{country}",
        "limit": 1,
        "appid": api_key
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    if data:
        return data[0]["lat"], data[0]["lon"]
    else:
        raise ValueError("Location not found.")

def get_weather_forecast(lat, lon, api_key):
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"   # <-- Fetch temperature in Celsius
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

def bell_curve_efficiency(temp_c):
    """
    Bell curve model centered at 25°C.
    Efficiency reduces as temperature deviates from 25°C.
    """
    optimal_temp = 25
    sigma = 10   # spread of the curve
    efficiency = math.exp(-((temp_c - optimal_temp) ** 2) / (2 * sigma ** 2))
    return efficiency  # between 0 and 1

def fetch_weather(api_key, city="Vellore", state="TN", country="IN"):
    try:
        lat, lon = get_coordinates(city, state, country, api_key)
        forecast_data = get_weather_forecast(lat, lon, api_key)
        
        tomorrow = (datetime.utcnow() + timedelta(days=1)).date()

        # Filter forecasts for tomorrow
        tomorrow_forecasts = [
            entry for entry in forecast_data["list"]
            if datetime.fromtimestamp(entry["dt"]).date() == tomorrow
        ]

        if not tomorrow_forecasts:
            raise ValueError("No forecast data available for tomorrow.")
        
        # Pick forecast near midday (most solar intensity)
        midday_forecast = None
        for entry in tomorrow_forecasts:
            if "12:00:00" in entry["dt_txt"]:
                midday_forecast = entry
                break
        if midday_forecast is None:
            midday_forecast = tomorrow_forecasts[0]

        # Extract parameters
        weather = midday_forecast["weather"][0]["main"]
        temperature = midday_forecast["main"]["temp"]
        efficiency = bell_curve_efficiency(temperature)

        return weather, temperature, efficiency

    except Exception as e:
        raise RuntimeError(f"Error fetching weather: {e}")

# Uncomment to test
if __name__ == "__main__":
    api_key = ""
    weather, temp, eff = fetch_weather(api_key)
    print(f"Weather: {weather}, Temp: {temp}°C, Efficiency Factor: {eff:.2f}")