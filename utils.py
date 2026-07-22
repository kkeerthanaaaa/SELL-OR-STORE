"""
utils.py
--------
Small shared helper functions used across the app (formatting, CSS injection,
month labelling, etc.) to keep app.py focused on layout/flow.
"""

import os
from datetime import datetime, timedelta


def month_labels_for_history(n_months: int = 12) -> list:
    """Returns short month labels ending at the current month, e.g. ['Aug', 'Sep', ..., 'Jul']."""
    today = datetime.now()
    labels = []
    for i in range(n_months - 1, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=1)
        for _ in range(i):
            month_date = month_date.replace(day=1) - timedelta(days=1)
        labels.append(month_date.strftime("%b"))
    return labels[-n_months:]


def format_currency(value) -> str:
    try:
        return f"Rs {float(value):,.2f}"
    except (TypeError, ValueError):
        return "Rs N/A"


def load_custom_css() -> str:
    """Responsive, mobile-friendly custom CSS for the Streamlit dashboard."""
    return """
    <style>
    /* Overall page padding tightened for small screens */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Card styling */
    .sos-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #eef1ee;
        margin-bottom: 1rem;
    }

    .sos-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }

    .sos-badge-sell { background-color: #d9534f; }
    .sos-badge-store { background-color: #2e8b57; }
    .sos-badge-caution { background-color: #e0a800; }

    /* Responsive tweaks for phones */
    @media (max-width: 640px) {
        .block-container { padding-left: 0.6rem; padding-right: 0.6rem; }
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.15rem !important; }
        .sos-card { padding: 0.8rem 0.9rem; }
    }
    </style>
    """


def safe_image_path(path: str, fallback_emoji_label: str = "🌾") -> str:
    """Returns the image path if it exists on disk, else None (caller should show a placeholder)."""
    return path if os.path.exists(path) else None
