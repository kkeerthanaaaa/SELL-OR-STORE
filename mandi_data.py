"""
mandi_data.py
-------------
Real mandi (agricultural market) price data integration using the
data.gov.in "Current Daily Price of Various Commodities" API, which mirrors
Agmarknet data.

Dataset resource used (Government Open Data Platform India):
  https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi

To enable live data:
  1. Get a free API key at https://data.gov.in/ (create account -> My Account -> API keys)
  2. Set it as an environment variable: export DATA_GOV_IN_API_KEY="xxxx"
     or paste it into the sidebar field inside the running app.

If no key is configured or the request fails, the module falls back to a
clearly-labelled simulated mandi price list so the rest of the app (nearby
mandi comparison, price prediction, etc.) keeps working end-to-end.
"""

import os
import random
import requests

DATA_GOV_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # Agmarknet mirror resource
DATA_GOV_BASE_URL = f"https://api.data.gov.in/resource/{DATA_GOV_RESOURCE_ID}"
DEFAULT_TIMEOUT = 6

# A small, illustrative set of mandis per state used for the "nearby mandi" feature
# when live location-tagged data isn't available. Distance is approximate (km) from
# a representative district centroid and is only meant to rank options, not navigate.
SAMPLE_MANDIS = {
    "Karnataka": [
        {"name": "Bengaluru (Yeshwanthpur) Mandi", "district": "Bengaluru Urban", "distance_km": 8},
        {"name": "Kolar APMC", "district": "Kolar", "distance_km": 66},
        {"name": "Mysuru APMC", "district": "Mysuru", "distance_km": 145},
        {"name": "Hubballi APMC", "district": "Dharwad", "distance_km": 410},
    ],
    "Maharashtra": [
        {"name": "Pune Market Yard", "district": "Pune", "distance_km": 10},
        {"name": "Nashik APMC (Lasalgaon)", "district": "Nashik", "distance_km": 180},
        {"name": "Mumbai Vashi APMC", "district": "Mumbai", "distance_km": 150},
    ],
    "Default": [
        {"name": "District Main Mandi", "district": "Local", "distance_km": 12},
        {"name": "Regional Wholesale Market", "district": "Regional", "distance_km": 55},
        {"name": "State APMC Hub", "district": "State Capital", "distance_km": 210},
    ],
}


def get_api_key(user_supplied_key: str = "") -> str:
    if user_supplied_key:
        return user_supplied_key.strip()
    return os.environ.get("DATA_GOV_IN_API_KEY", "").strip()


def fetch_live_mandi_prices(commodity: str, state: str = "", api_key: str = "", limit: int = 10) -> dict:
    """
    Attempts to fetch live per-mandi prices for a commodity from data.gov.in.
    Returns:
        {
            "source": "live" | "simulated",
            "records": [ {market, state, district, min_price, max_price, modal_price, date}, ... ]
        }
    Prices from data.gov.in are typically in Rs/quintal; callers should divide by
    100 to convert to Rs/kg for consistency with the rest of this app.
    """
    key = get_api_key(api_key)

    if key:
        try:
            params = {
                "api-key": key,
                "format": "json",
                "limit": limit,
                "filters[commodity]": commodity,
            }
            if state:
                params["filters[state]"] = state

            resp = requests.get(DATA_GOV_BASE_URL, params=params, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 200:
                payload = resp.json()
                records = payload.get("records", [])
                if records:
                    return {"source": "live", "records": records}
        except (requests.RequestException, ValueError):
            pass  # fall through to simulation

    return _simulate_mandi_prices(commodity, state)


def _simulate_mandi_prices(commodity: str, state: str = "") -> dict:
    mandis = SAMPLE_MANDIS.get(state, SAMPLE_MANDIS["Default"])
    rnd = random.Random(hash(commodity) % (2 ** 32))
    base_quintal_price = rnd.uniform(1200, 2600)
    records = []
    for m in mandis:
        variation = rnd.uniform(-0.08, 0.08)
        modal = round(base_quintal_price * (1 + variation), 2)
        records.append(
            {
                "market": m["name"],
                "district": m["district"],
                "state": state or "Default",
                "distance_km": m["distance_km"],
                "min_price": round(modal * 0.95, 2),
                "max_price": round(modal * 1.05, 2),
                "modal_price": modal,
                "commodity": commodity,
            }
        )
    return {"source": "simulated", "records": records}


def rank_nearby_mandis(mandi_result: dict, top_n: int = 3) -> list:
    """
    Rank mandis by a blend of higher modal price and shorter distance, so the
    farmer sees genuinely useful nearby options rather than just the closest
    or just the highest-paying one in isolation.
    """
    records = mandi_result.get("records", [])
    if not records:
        return []

    max_price = max(r.get("modal_price", 0) for r in records) or 1
    max_dist = max(r.get("distance_km", 1) for r in records) or 1

    scored = []
    for r in records:
        price_score = r.get("modal_price", 0) / max_price
        distance_score = 1 - (r.get("distance_km", max_dist) / max_dist)
        combined = 0.65 * price_score + 0.35 * distance_score
        scored.append({**r, "score": round(combined, 3)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
