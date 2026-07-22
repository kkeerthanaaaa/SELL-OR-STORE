"""
crop_data.py
------------
Structured crop knowledge base used by the ML model and the decision engine.

Each crop entry contains:
- image: path to a representative image
- safe_storage_days: number of days the crop can be safely stored post-harvest
- storage_sensitivity: qualitative sensitivity to storage / spoilage (Low/Medium/High)
- weather_sensitivity: qualitative sensitivity to weather/humidity risk (Low/Medium/High)
- growing_conditions: short description
- market_behaviour: short description of typical price behaviour
- historical_prices: 12 monthly average mandi prices (Rs/kg), oldest -> newest
- base_mandi_price: latest known reference price (Rs/kg), used when live data is unavailable
- storage_cost_per_kg_per_day: approximate cold/dry storage cost (Rs/kg/day)
- avg_spoilage_pct_per_day: approximate spoilage loss (% of quantity) per day beyond safe storage
"""

import random

CROPS = {
    "Rice": {
        "image": "images/rice.jpg",
        "safe_storage_days": 180,
        "storage_sensitivity": "Low",
        "weather_sensitivity": "Low",
        "growing_conditions": "Warm, humid climate with standing water; thrives in clayey loam soils.",
        "market_behaviour": "Prices are relatively stable through the year with mild upward drift post-monsoon.",
        "historical_prices": [21, 21.2, 21.5, 21.4, 21.8, 22.0, 22.3, 22.1, 22.5, 22.8, 23.0, 23.2],
        "base_mandi_price": 23.2,
        "storage_cost_per_kg_per_day": 0.03,
        "avg_spoilage_pct_per_day": 0.05,
    },
    "Wheat": {
        "image": "images/wheat.jpg",
        "safe_storage_days": 150,
        "storage_sensitivity": "Low",
        "weather_sensitivity": "Low",
        "growing_conditions": "Cool growing season, well-drained loamy soil, moderate irrigation.",
        "market_behaviour": "Stable prices with seasonal peak before the next sowing cycle.",
        "historical_prices": [24, 24.1, 24.3, 24.5, 24.6, 24.8, 25.0, 25.1, 25.3, 25.5, 25.6, 25.8],
        "base_mandi_price": 25.8,
        "storage_cost_per_kg_per_day": 0.025,
        "avg_spoilage_pct_per_day": 0.04,
    },
    "Onion": {
        "image": "images/onion.jpg",
        "safe_storage_days": 30,
        "storage_sensitivity": "Medium",
        "weather_sensitivity": "Medium",
        "growing_conditions": "Sensitive to excess moisture; needs well-drained sandy loam soil.",
        "market_behaviour": "Highly volatile prices driven by supply gluts and export policy changes.",
        "historical_prices": [18, 16, 15, 14, 17, 22, 26, 24, 20, 19, 21, 25],
        "base_mandi_price": 25,
        "storage_cost_per_kg_per_day": 0.05,
        "avg_spoilage_pct_per_day": 0.8,
    },
    "Tomato": {
        "image": "images/tomato.jpg",
        "safe_storage_days": 7,
        "storage_sensitivity": "High",
        "weather_sensitivity": "High",
        "growing_conditions": "Requires warm days, cool nights, and consistent watering; highly perishable.",
        "market_behaviour": "Extremely volatile; prices can swing 2-3x within weeks due to perishability.",
        "historical_prices": [12, 15, 20, 10, 8, 14, 22, 18, 12, 9, 16, 24],
        "base_mandi_price": 24,
        "storage_cost_per_kg_per_day": 0.08,
        "avg_spoilage_pct_per_day": 3.0,
    },
    "Potato": {
        "image": "images/potato.jpg",
        "safe_storage_days": 90,
        "storage_sensitivity": "Medium",
        "weather_sensitivity": "Medium",
        "growing_conditions": "Cool climate crop; sensitive to waterlogging and high humidity in storage.",
        "market_behaviour": "Moderate seasonal swings, generally rising toward off-season months.",
        "historical_prices": [14, 14.5, 15, 15.2, 15.5, 16, 16.5, 16.8, 17, 17.3, 17.6, 18],
        "base_mandi_price": 18,
        "storage_cost_per_kg_per_day": 0.035,
        "avg_spoilage_pct_per_day": 0.3,
    },
    "Maize": {
        "image": "images/maize.jpg",
        "safe_storage_days": 120,
        "storage_sensitivity": "Low",
        "weather_sensitivity": "Medium",
        "growing_conditions": "Warm season crop; needs well-drained soil and moderate rainfall.",
        "market_behaviour": "Fairly stable with mild upward trend tied to poultry-feed demand.",
        "historical_prices": [19, 19.2, 19.3, 19.5, 19.6, 19.8, 20.0, 20.1, 20.3, 20.5, 20.6, 20.8],
        "base_mandi_price": 20.8,
        "storage_cost_per_kg_per_day": 0.02,
        "avg_spoilage_pct_per_day": 0.1,
    },
}

HARVEST_AGE_OPTIONS = {
    "Today": 0,
    "1 day ago": 1,
    "2 days ago": 2,
    "3 days ago": 3,
    "5 days ago": 5,
    "1 week ago": 7,
    "2 weeks ago": 14,
}


def get_crop_names():
    return list(CROPS.keys())


def get_crop_info(crop_name: str) -> dict:
    return CROPS.get(crop_name, {})


def simulate_daily_price(crop_name: str, seed_offset: int = 0) -> float:
    """
    Small deterministic-ish daily fluctuation layered on top of the latest monthly
    price, used only when a live mandi price feed is not reachable/configured.
    """
    info = get_crop_info(crop_name)
    base = info.get("base_mandi_price", 20)
    rnd = random.Random(hash(crop_name) + seed_offset)
    fluctuation = rnd.uniform(-0.04, 0.04)  # +/- 4%
    return round(base * (1 + fluctuation), 2)
