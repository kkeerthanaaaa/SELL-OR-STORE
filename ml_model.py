"""
ml_model.py
-----------
Price prediction model. Upgraded from a single-feature Linear Regression to a
Random Forest Regressor (with an optional XGBoost backend if the package is
installed) that learns from engineered time-series features, and exposes
feature importances for the Explainable AI section.

Public API:
    train_and_predict(historical_prices, weather_risk, model_type="random_forest")
        -> dict with predicted_price, trend, model_used, feature_importance
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

FEATURE_NAMES = [
    "month_index",
    "lag_1_price",
    "lag_2_price",
    "rolling_3_avg",
    "trend_slope",
    "weather_risk",
]


def _build_features(historical_prices: list, weather_risk: float):
    """
    Builds a small supervised-learning dataset from a 12-point monthly price
    series so a tree ensemble has more than one raw number to learn from.
    Each row t (starting at t=2) predicts price[t] from features derived
    from prices up to t-1, plus the current weather risk score.
    """
    prices = np.array(historical_prices, dtype=float)
    n = len(prices)
    X, y = [], []

    for t in range(2, n):
        lag_1 = prices[t - 1]
        lag_2 = prices[t - 2]
        rolling_3 = prices[max(0, t - 3):t].mean()
        # simple slope over the last up-to-3 points
        window = prices[max(0, t - 3):t]
        slope = np.polyfit(range(len(window)), window, 1)[0] if len(window) > 1 else 0.0
        X.append([t, lag_1, lag_2, rolling_3, slope, weather_risk])
        y.append(prices[t])

    return np.array(X), np.array(y)


def _next_step_features(historical_prices: list, weather_risk: float):
    prices = np.array(historical_prices, dtype=float)
    n = len(prices)
    lag_1 = prices[-1]
    lag_2 = prices[-2] if n > 1 else prices[-1]
    rolling_3 = prices[-3:].mean()
    window = prices[-3:]
    slope = np.polyfit(range(len(window)), window, 1)[0] if len(window) > 1 else 0.0
    return np.array([[n, lag_1, lag_2, rolling_3, slope, weather_risk]])


def train_and_predict(historical_prices: list, weather_risk: float = 0.3, model_type: str = "random_forest") -> dict:
    """
    Trains a model on engineered features from the historical monthly price
    series and predicts next month's price.

    model_type: "random_forest" (default) or "xgboost" (falls back to
    random_forest automatically if xgboost isn't installed).
    """
    X, y = _build_features(historical_prices, weather_risk)

    # Guard against too little data for a tree ensemble; fall back to linear trend.
    if len(X) < 4:
        model = LinearRegression()
        idx = np.arange(len(historical_prices)).reshape(-1, 1)
        model.fit(idx, historical_prices)
        next_idx = np.array([[len(historical_prices)]])
        predicted = float(model.predict(next_idx)[0])
        importances = {name: 0.0 for name in FEATURE_NAMES}
        used_model = "linear_regression (fallback: insufficient data)"
    else:
        use_xgb = model_type == "xgboost" and XGBOOST_AVAILABLE
        if use_xgb:
            model = XGBRegressor(
                n_estimators=200, max_depth=3, learning_rate=0.08,
                subsample=0.9, random_state=42, verbosity=0,
            )
            used_model = "xgboost"
        else:
            model = RandomForestRegressor(
                n_estimators=300, max_depth=5, random_state=42, min_samples_leaf=1
            )
            used_model = "random_forest" if model_type != "xgboost" else "random_forest (xgboost not installed)"

        model.fit(X, y)
        next_X = _next_step_features(historical_prices, weather_risk)
        predicted = float(model.predict(next_X)[0])

        raw_importances = getattr(model, "feature_importances_", np.zeros(len(FEATURE_NAMES)))
        importances = {name: round(float(val), 4) for name, val in zip(FEATURE_NAMES, raw_importances)}

    current_price = historical_prices[-1]
    trend = "Increasing" if predicted > current_price * 1.01 else (
        "Decreasing" if predicted < current_price * 0.99 else "Stable"
    )

    return {
        "predicted_price": round(predicted, 2),
        "current_price": round(current_price, 2),
        "trend": trend,
        "model_used": used_model,
        "feature_importance": importances,
        "prediction_certainty": _estimate_certainty(historical_prices),
    }


def _estimate_certainty(historical_prices: list) -> float:
    """
    A simple volatility-based proxy for how certain we can be about the
    prediction: lower coefficient of variation => higher certainty (0-1).
    """
    prices = np.array(historical_prices, dtype=float)
    if prices.mean() == 0:
        return 0.5
    cv = prices.std() / prices.mean()
    certainty = max(0.2, min(1.0, 1 - cv))
    return round(certainty, 3)
