import datetime

import requests

try:
    # Το local_settings.py δεν ανεβαίνει ποτέ στο GitHub (είναι στο
    # .gitignore) - εκεί μένει το πραγματικό, προσωπικό σου API key.
    from local_settings import WEATHER_API_KEY as API_KEY
except ImportError:
    API_KEY = "ΒΑΛΕ_ΕΔΩ_ΤΟ_API_KEY_ΣΟΥ"

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

WEATHER_EMOJI = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}


def get_weather_emoji(main):
    return WEATHER_EMOJI.get(main, "🌤️")


def _fetch(url, city):
    """Ζητά δεδομένα από το OpenWeatherMap. Επιστρέφει None αν κάτι πάει στραβά (κλειδί, πόλη, δίκτυο)."""
    if not city or API_KEY == "ΒΑΛΕ_ΕΔΩ_ΤΟ_API_KEY_ΣΟΥ":
        return None

    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "el"}
    try:
        response = requests.get(url, params=params, timeout=5)
    except requests.RequestException:
        return None
    return response.json() if response.status_code == 200 else None


def get_current_weather(city):
    data = _fetch(BASE_URL, city)
    if data is None:
        return None
    return {
        "main": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
    }


def get_forecast(city, days=4):
    data = _fetch(FORECAST_URL, city)
    if data is None:
        return None

    # Η πρόγνωση έρχεται ανά 3 ώρες - την ομαδοποιούμε ανά ημέρα
    by_date = {}
    for entry in data["list"]:
        date_str = entry["dt_txt"].split(" ")[0]
        by_date.setdefault(date_str, []).append(entry)

    today_str = datetime.date.today().isoformat()
    result = []
    for date_str in sorted(by_date):
        if date_str == today_str:
            continue
        entries = by_date[date_str]
        temps = [e["main"]["temp"] for e in entries]
        midday_entry = min(entries, key=lambda e: abs(int(e["dt_txt"][11:13]) - 12))
        result.append({
            "date": date_str,
            "main": midday_entry["weather"][0]["main"],
            "description": midday_entry["weather"][0]["description"],
            "temp_min": min(temps),
            "temp_max": max(temps),
        })
    return result[:days]
