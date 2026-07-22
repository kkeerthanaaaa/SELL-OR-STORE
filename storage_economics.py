"""
storage_economics.py
---------------------
Estimates the cost of storing a crop for additional days and the resulting
net profit or loss compared to selling immediately, factoring in spoilage.
"""


def estimate_storage_cost(quantity_kg: float, storage_cost_per_kg_per_day: float, extra_days: int) -> float:
    """Total Rs cost of storing `quantity_kg` for `extra_days` more days."""
    if extra_days <= 0:
        return 0.0
    return round(quantity_kg * storage_cost_per_kg_per_day * extra_days, 2)


def estimate_spoilage_loss_kg(quantity_kg: float, avg_spoilage_pct_per_day: float, extra_days: int) -> float:
    """Approximate kg of produce lost to spoilage over the extra storage period."""
    if extra_days <= 0:
        return 0.0
    spoilage_fraction = min((avg_spoilage_pct_per_day / 100) * extra_days, 0.9)  # cap at 90% loss
    return round(quantity_kg * spoilage_fraction, 2)


def estimate_profit_if_stored(
    quantity_kg: float,
    current_price_per_kg: float,
    predicted_price_per_kg: float,
    storage_cost_per_kg_per_day: float,
    avg_spoilage_pct_per_day: float,
    extra_days: int,
) -> dict:
    """
    Compares:
      Option A - Sell now:      revenue_now = quantity_kg * current_price_per_kg
      Option B - Store & sell:  revenue_later = (quantity_kg - spoilage_kg) * predicted_price_per_kg - storage_cost

    Returns a breakdown dict including net_gain (positive => storing is more profitable).
    """
    revenue_now = round(quantity_kg * current_price_per_kg, 2)

    spoilage_kg = estimate_spoilage_loss_kg(quantity_kg, avg_spoilage_pct_per_day, extra_days)
    sellable_kg = max(quantity_kg - spoilage_kg, 0)
    storage_cost = estimate_storage_cost(quantity_kg, storage_cost_per_kg_per_day, extra_days)

    gross_revenue_later = round(sellable_kg * predicted_price_per_kg, 2)
    revenue_later_net = round(gross_revenue_later - storage_cost, 2)

    net_gain = round(revenue_later_net - revenue_now, 2)

    return {
        "revenue_if_sold_now": revenue_now,
        "spoilage_kg": spoilage_kg,
        "sellable_kg_after_storage": sellable_kg,
        "storage_cost": storage_cost,
        "gross_revenue_if_stored": gross_revenue_later,
        "net_revenue_if_stored": revenue_later_net,
        "net_gain_from_storing": net_gain,
        "storing_is_better": net_gain > 0,
    }
