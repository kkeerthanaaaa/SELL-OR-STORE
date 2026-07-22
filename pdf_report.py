"""
pdf_report.py
-------------
Generates a downloadable PDF recommendation report summarising the
crop, decision, confidence score, reasoning, storage economics, and the
explainable-AI factor breakdown, so a farmer can save or print it.

Uses fpdf2 (pure-Python, no system dependencies).
"""

from datetime import datetime
from fpdf import FPDF

from explainability import rank_ml_feature_importance, rank_decision_factors


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 90, 50)
        self.cell(0, 10, "Sell-or-Store: Crop Sale Timing Report", ln=True, align="C")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, f"Generated on {datetime.now().strftime('%d %b %Y, %I:%M %p')}", ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, "Decision Support Tool - Final selling decisions remain with the farmer.", align="C")

    def section_title(self, text):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(20, 90, 50)
        self.ln(2)
        self.cell(0, 8, text, ln=True)
        self.set_draw_color(20, 90, 50)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)

    def key_value(self, key, value):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 40, 40)
        self.cell(70, 7, str(key))
        self.set_font("Helvetica", "", 10)
        self.cell(0, 7, str(value), ln=True)

    def paragraph(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(1)


def build_report(
    farmer_name: str,
    crop_name: str,
    harvest_age_label: str,
    quantity_kg: float,
    result: dict,
    weather: dict,
    nearby_mandis: list,
    lang: str = "en",
    output_path: str = "recommendation_report.pdf",
) -> str:
    """Builds the PDF and writes it to `output_path`. Returns the path."""
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.section_title("Farmer & Crop Details")
    pdf.key_value("Farmer:", farmer_name or "Guest")
    pdf.key_value("Crop:", crop_name)
    pdf.key_value("Harvested:", harvest_age_label)
    pdf.key_value("Quantity:", f"{quantity_kg:.1f} kg")

    pdf.section_title("Market Snapshot")
    pdf.key_value("Current Price:", f"Rs {result['current_price']}/kg")
    pdf.key_value("Predicted Next-Month Price:", f"Rs {result['predicted_price']}/kg")
    pdf.key_value("Market Trend:", result["trend"])
    pdf.key_value("Model Used:", result["model_used"])

    pdf.section_title("Recommendation")
    pdf.key_value("Decision:", result["decision"])
    pdf.key_value("Confidence Score:", f"{result['confidence']}%")
    pdf.key_value("Risk Level:", result["risk_level"])
    pdf.key_value("Safe Storage Days Remaining:", result["days_remaining"])
    pdf.key_value("Suggested Selling Price:", f"Rs {result['suggested_price']}/kg")
    pdf.paragraph(f"Reason: {result['reason']}")

    pdf.section_title("Weather Snapshot")
    pdf.key_value("City / Region:", weather.get("city", "N/A"))
    pdf.key_value("Temperature:", f"{weather.get('temperature_c', 'N/A')} C")
    pdf.key_value("Humidity:", f"{weather.get('humidity_pct', 'N/A')}%")
    pdf.key_value("Condition:", weather.get("condition", "N/A"))
    pdf.key_value("Data Source:", "Live OpenWeather feed" if weather.get("source") == "live" else "Simulated (no API key configured)")

    pa = result["profit_analysis"]
    pdf.section_title("Storage Cost & Profit Estimation")
    pdf.key_value("Revenue if Sold Now:", f"Rs {pa['revenue_if_sold_now']}")
    pdf.key_value("Estimated Storage Cost:", f"Rs {pa['storage_cost']}")
    pdf.key_value("Estimated Spoilage Loss:", f"{pa['spoilage_kg']} kg")
    pdf.key_value("Net Revenue if Stored:", f"Rs {pa['net_revenue_if_stored']}")
    pdf.key_value("Net Gain from Storing:", f"Rs {pa['net_gain_from_storing']}")
    pdf.paragraph(
        "Storing appears more profitable in this scenario." if pa["storing_is_better"]
        else "Selling now appears more profitable in this scenario."
    )

    if nearby_mandis:
        pdf.section_title("Nearby Mandi Recommendations")
        for m in nearby_mandis:
            pdf.paragraph(
                f"- {m.get('market', 'Unknown market')} ({m.get('district', 'N/A')}), "
                f"~{m.get('distance_km', '?')} km, modal price Rs {m.get('modal_price', '?')}/quintal"
            )

    pdf.section_title("Explainable AI - Why this recommendation?")
    pdf.paragraph("Top factors influencing the price prediction model:")
    for f in rank_ml_feature_importance(result["feature_importance"]):
        pdf.paragraph(f"  - {f['label']}: {f['importance_pct']}% influence")

    pdf.paragraph("Top factors influencing the SELL/STORE decision:")
    for f in rank_decision_factors(result["decision_factors"]):
        pdf.paragraph(f"  - {f['label']}: {f['influence_pct']}% influence ({f['direction']})")

    pdf.section_title("Responsible AI Notice")
    pdf.paragraph(
        "This recommendation is generated using historical mandi price data, live/simulated weather "
        "data, and crop-specific knowledge. It is intended purely as a decision-support aid. "
        "The final selling decision always remains with the farmer."
    )

    pdf.output(output_path)
    return output_path
