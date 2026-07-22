"""
explainability.py
------------------
Turns raw ML feature importances and decision-engine factor weights into a
human-readable, ranked explanation of what drove a SELL / STORE / CAUTION
recommendation - the "Explainable AI" section of the dashboard.
"""

FEATURE_LABELS = {
    "month_index": "Seasonality / time progression",
    "lag_1_price": "Most recent month's price",
    "lag_2_price": "Price two months ago",
    "rolling_3_avg": "3-month rolling average price",
    "trend_slope": "Recent price trend (momentum)",
    "weather_risk": "Weather / spoilage risk",
}

DECISION_FACTOR_LABELS = {
    "storage_utilisation": "How much of the safe storage window is already used",
    "predicted_trend": "Predicted market price trend",
    "weather_risk": "Weather-driven spoilage risk",
    "storage_sensitivity": "Crop's inherent storage sensitivity",
    "prediction_certainty": "Confidence in the price prediction",
}


def rank_ml_feature_importance(feature_importance: dict, top_n: int = 4) -> list:
    """Returns a sorted list of (label, importance_pct) for the price-prediction model."""
    total = sum(feature_importance.values()) or 1
    ranked = sorted(feature_importance.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    return [
        {"label": FEATURE_LABELS.get(name, name), "importance_pct": round((val / total) * 100, 1)}
        for name, val in ranked
        if val > 0
    ] or [{"label": FEATURE_LABELS.get(name, name), "importance_pct": 0.0} for name, val in ranked]


def rank_decision_factors(decision_factors: dict, top_n: int = 5) -> list:
    """
    decision_factors: dict of factor_name -> normalized weight (0-1) contributed
    to the final SELL/STORE score, produced by decision_engine.py.
    """
    total = sum(abs(v) for v in decision_factors.values()) or 1
    ranked = sorted(decision_factors.items(), key=lambda kv: abs(kv[1]), reverse=True)[:top_n]
    return [
        {
            "label": DECISION_FACTOR_LABELS.get(name, name),
            "influence_pct": round((abs(val) / total) * 100, 1),
            "direction": "towards SELL" if val > 0 else "towards STORE",
        }
        for name, val in ranked
    ]
