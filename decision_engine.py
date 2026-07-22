"""
decision_engine.py
-------------------
Combines crop knowledge, live weather risk, ML price prediction, and storage
economics into a single SELL / STORE / CAUTION recommendation with a
confidence score and a factor-level breakdown for explainability.

This module is a Decision Support tool: it produces a recommendation and
reasoning for a human (the farmer) to consider - it does not execute any
transaction automatically.
"""

from crop_data import get_crop_info
from ml_model import train_and_predict
from weather_api import weather_risk_score
from storage_economics import estimate_profit_if_stored

SENSITIVITY_WEIGHT = {"Low": 0.3, "Medium": 0.6, "High": 1.0}


def generate_recommendation(
    crop_name: str,
    harvest_age_days: int,
    weather: dict,
    quantity_kg: float = 100.0,
    model_type: str = "random_forest",
) -> dict:
    info = get_crop_info(crop_name)
    if not info:
        raise ValueError(f"Unknown crop: {crop_name}")

    safe_storage_days = info["safe_storage_days"]
    storage_sensitivity = info["storage_sensitivity"]
    weather_sensitivity = info["weather_sensitivity"]
    historical_prices = info["historical_prices"]

    w_risk = weather_risk_score(weather, weather_sensitivity)

    ml_result = train_and_predict(historical_prices, weather_risk=w_risk, model_type=model_type)
    predicted_price = ml_result["predicted_price"]
    current_price = ml_result["current_price"]
    trend = ml_result["trend"]
    certainty = ml_result["prediction_certainty"]

    days_remaining = safe_storage_days - harvest_age_days
    storage_utilisation = min(max(harvest_age_days / safe_storage_days, 0), 1.5)  # can exceed 1 if overdue

    price_growth_pct = ((predicted_price - current_price) / current_price) * 100 if current_price else 0

    # ---- Scoring: positive score leans SELL, negative leans STORE ----
    factors = {}

    # 1. Storage utilisation: the more of the safe window already used, the more it pushes to SELL
    factors["storage_utilisation"] = round((storage_utilisation - 0.5) * 1.4, 3)

    # 2. Predicted trend: rising prices push to STORE (negative), falling prices push to SELL (positive)
    factors["predicted_trend"] = round(-price_growth_pct / 8, 3)

    # 3. Weather risk: higher spoilage risk pushes to SELL
    factors["weather_risk"] = round(w_risk * 1.1, 3)

    # 4. Storage sensitivity of the crop itself: high sensitivity pushes to SELL
    factors["storage_sensitivity"] = round(SENSITIVITY_WEIGHT.get(storage_sensitivity, 0.6) * 0.7, 3)

    # 5. Prediction certainty dampens or amplifies the trend factor's influence
    factors["prediction_certainty"] = round((1 - certainty) * 0.4, 3)  # low certainty nudges towards caution/SELL

    score = sum(factors.values())

    # ---- Decision thresholds ----
    if days_remaining < 0:
        decision = "SELL NOW"
        reason = (
            f"{crop_name} has exceeded its safe storage duration by {abs(days_remaining)} day(s). "
            "Continued storage risks significant spoilage that predicted price gains are unlikely to offset."
        )
    elif score > 0.55:
        decision = "SELL NOW"
        reason = (
            f"{crop_name} is approaching or has used up a large share of its safe storage window, "
            f"and/or predicted prices ({trend.lower()}) and current weather risk don't justify holding further."
        )
    elif score < -0.15:
        suggested_hold_days = min(max(days_remaining, 1), 14)
        decision = f"STORE FOR {suggested_hold_days} MORE DAYS"
        reason = (
            f"{crop_name} is still well within its safe storage period. Predicted prices show a "
            f"{trend.lower()} trend and current weather risk is manageable, so holding briefly may improve returns."
        )
    else:
        decision = "CAUTION"
        reason = (
            f"Conditions for {crop_name} are mixed — storage window, price trend, and weather risk roughly "
            "balance out. Monitor mandi prices closely over the next 1-2 days before deciding."
        )

    # ---- Confidence score (0-100) ----
    trend_strength = min(abs(price_growth_pct) / 15, 1.0)  # normalise, cap at 1
    spoilage_component = 1 - w_risk
    storage_tolerance_component = 1 - min(storage_utilisation, 1.0)
    confidence = (
        0.30 * trend_strength
        + 0.25 * spoilage_component
        + 0.20 * storage_tolerance_component
        + 0.25 * certainty
    ) * 100
    confidence = round(min(max(confidence, 5), 98), 1)

    # ---- Risk level ----
    if w_risk > 0.66 or storage_utilisation > 1.0:
        risk_level = "High"
    elif w_risk > 0.35 or storage_utilisation > 0.7:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # ---- Suggested selling price: modest premium if holding is advised, else current price ----
    if decision.startswith("STORE"):
        suggested_price = round(max(current_price, predicted_price * 0.97), 2)
    else:
        suggested_price = current_price

    # ---- Storage cost / profit-if-stored economics ----
    extra_days_for_profit_calc = max(days_remaining, 0) if days_remaining > 0 else 0
    profit_analysis = estimate_profit_if_stored(
        quantity_kg=quantity_kg,
        current_price_per_kg=current_price,
        predicted_price_per_kg=predicted_price,
        storage_cost_per_kg_per_day=info["storage_cost_per_kg_per_day"],
        avg_spoilage_pct_per_day=info["avg_spoilage_pct_per_day"],
        extra_days=extra_days_for_profit_calc or 3,  # illustrate a short 3-day hold if already at/over limit
    )

    return {
        "decision": decision,
        "reason": reason,
        "confidence": confidence,
        "risk_level": risk_level,
        "current_price": current_price,
        "predicted_price": predicted_price,
        "trend": trend,
        "suggested_price": suggested_price,
        "days_remaining": days_remaining,
        "safe_storage_days": safe_storage_days,
        "weather_risk_score": w_risk,
        "model_used": ml_result["model_used"],
        "feature_importance": ml_result["feature_importance"],
        "decision_factors": factors,
        "profit_analysis": profit_analysis,
        "historical_prices": historical_prices,
    }
