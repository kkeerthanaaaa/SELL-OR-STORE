"""
weather_api.py
--------------
Real-time weather integration using the OpenWeather "Current Weather" API.

Get a free API key at https://openweathermap.org/api and either:
  1. Set it as an environment variable:  export OPENWEATHER_API_KEY="xxxx"
  2. Or paste it into the sidebar field inside the running app.

If no key is configured, or the network call fails (no internet, invalid key,
rate limit, etc.), the module falls back to a clearly-labelled simulated
weather reading so the rest of the app keeps working end-to-end.
"""

import os
import random
import requests

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_TIMEOUT = 6  # seconds


def get_api_key(user_supplied_key: str = "") -> str:
    """Preference order: key typed in the UI > environment variable."""
    if user_supplied_key:
        return user_supplied_key.strip()
    return os.environ.get("OPENWEATHER_API_KEY", "").strip()


def fetch_weather(city: str, api_key: str = "") -> dict:
    """
    Returns a dict:
        {
            "source": "live" | "simulated",
            "city": str,
            "temperature_c": float,
            "humidity_pct": float,
            "condition": str,
            "rain_expected": bool,
        }
    """
    key = get_api_key(api_key)

    if key:
        try:
            resp = requests.get(
                OPENWEATHER_BASE_URL,
                params={"q": city, "appid": key, "units": "metric"},
                timeout=DEFAULT_TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                condition = data["weather"][0]["main"]
                return {
                    "source": "live",
                    "city": city,
                    "temperature_c": data["main"]["temp"],
                    "humidity_pct": data["main"]["humidity"],
                    "condition": condition,
                    "rain_expected": condition.lower() in ("rain", "thunderstorm", "drizzle"),
                }
        except (requests.RequestException, KeyError, IndexError):
            pass  # fall through to simulation

    return _simulate_weather(city)


def _simulate_weather(city: str) -> dict:
    """Deterministic-ish fallback so the UI never breaks without an API key."""
    rnd = random.Random(hash(city) % (2 ** 32))
    conditions = ["Clear", "Clouds", "Rain", "Haze", "Drizzle"]
    condition = rnd.choice(conditions)
    return {
        "source": "simulated",
        "city": city,
        "temperature_c": round(rnd.uniform(20, 38), 1),
        "humidity_pct": round(rnd.uniform(40, 90), 1),
        "condition": condition,
        "rain_expected": condition.lower() in ("rain", "drizzle"),
    }


def weather_risk_score(weather: dict, crop_weather_sensitivity: str) -> float:
    """
    Convert a weather reading + crop sensitivity into a 0-1 spoilage risk multiplier
    used by the decision engine. Higher humidity / rain + high sensitivity => higher risk.
    """
    sensitivity_weight = {"Low": 0.3, "Medium": 0.6, "High": 1.0}.get(crop_weather_sensitivity, 0.6)

    humidity_component = min(weather.get("humidity_pct", 50) / 100, 1.0)
    rain_component = 1.0 if weather.get("rain_expected") else 0.0

    risk = (0.6 * humidity_component + 0.4 * rain_component) * sensitivity_weight
    return round(min(risk, 1.0), 3)
