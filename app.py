"""
app.py
------
Main Streamlit entry point for "Sell-or-Store: AI-Based Crop Sale Timing
Assistant for Farmers". Wires together auth, translations, live weather,
live mandi data, the ML price model, the decision engine, storage economics,
explainability, and the downloadable PDF report into one responsive
dashboard.

Run with:  streamlit run app.py
"""

import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from crop_data import get_crop_names, get_crop_info, HARVEST_AGE_OPTIONS
from translations import t, LANGUAGES
from weather_api import fetch_weather
from mandi_data import fetch_live_mandi_prices, rank_nearby_mandis
from decision_engine import generate_recommendation
from explainability import rank_ml_feature_importance, rank_decision_factors
from storage_economics import estimate_storage_cost
from pdf_report import build_report
from utils import load_custom_css, month_labels_for_history, format_currency, safe_image_path
import auth

# --------------------------------------------------------------------------
# Page config & global styling
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Sell-or-Store | AI Crop Sale Timing Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(load_custom_css(), unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Session state defaults
# --------------------------------------------------------------------------
defaults = {
    "lang": "en",
    "authenticated": False,
    "user": None,
    "result": None,
    "weather": None,
    "mandi_result": None,
    "nearby_mandis": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# --------------------------------------------------------------------------
# Sidebar: language, API keys, auth
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌍 " + t("language", st.session_state.lang))
    lang_choice = st.selectbox(
        t("language", st.session_state.lang),
        options=list(LANGUAGES.keys()),
        format_func=lambda code: LANGUAGES[code],
        index=list(LANGUAGES.keys()).index(st.session_state.lang),
        label_visibility="collapsed",
    )
    st.session_state.lang = lang_choice
    lang = st.session_state.lang

    st.divider()
    st.markdown("### 🔑 API Keys (optional)")
    st.caption("Leave blank to use simulated data for weather / mandi prices.")
    owm_key = st.text_input("OpenWeather API key", type="password", key="owm_key")
    dgi_key = st.text_input("data.gov.in API key", type="password", key="dgi_key")

    st.divider()
    st.markdown("### 👤 " + t("login", lang))

    if not st.session_state.authenticated:
        auth_tab_login, auth_tab_register = st.tabs([t("login", lang), t("register", lang)])

        with auth_tab_login:
            login_user = st.text_input(t("username", lang), key="login_user")
            login_pass = st.text_input(t("password", lang), type="password", key="login_pass")
            if st.button(t("login", lang), use_container_width=True):
                ok, record = auth.authenticate(login_user, login_pass)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.user = record
                    st.rerun()
                else:
                    st.error(t("login_failed", lang))

        with auth_tab_register:
            reg_user = st.text_input(t("username", lang), key="reg_user")
            reg_pass = st.text_input(t("password", lang), type="password", key="reg_pass")
            reg_name = st.text_input(t("full_name", lang), key="reg_name")
            reg_district = st.text_input(t("district", lang), key="reg_district")
            if st.button(t("register", lang), use_container_width=True):
                ok, msg_key = auth.register_user(reg_user, reg_pass, reg_name, reg_district)
                if ok:
                    st.success(t(msg_key, lang))
                else:
                    st.error(t(msg_key, lang))
    else:
        user = st.session_state.user
        st.success(f"{t('welcome', lang)}, {user.get('full_name') or user['username']} 👋")
        if st.button(t("logout", lang), use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
        <h1 style="margin-bottom:0.2rem;">🌾 {t('app_title', lang)}</h1>
        <p style="color:#5a6b5a; font-size:1.0rem;">{t('app_subtitle', lang)}</p>
        <span class="sos-badge" style="background:#1c7c54;">SDG 2 · Zero Hunger</span>
        <span class="sos-badge" style="background:#2d6a4f;">SDG 12 · Responsible Consumption</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
col_left, col_right = st.columns([1, 1.3], gap="large")

crop_names = get_crop_names()

with col_left:
    st.markdown(f"#### 🌱 {t('select_crop', lang)}")
    crop_name = st.selectbox(t("select_crop", lang), crop_names, label_visibility="collapsed")
    info = get_crop_info(crop_name)

    img_path = safe_image_path(os.path.join(os.path.dirname(__file__), info["image"]))
    if img_path:
        st.image(img_path, use_container_width=True)

    st.markdown(
        f"""
        <div class="sos-card">
            <b>🌦️ {t('growing_conditions', lang)}:</b> {info['growing_conditions']}<br><br>
            <b>📦 {t('storage_sensitivity', lang)}:</b> {info['storage_sensitivity']}<br>
            <b>⏳ {t('safe_storage_days', lang)}:</b> {info['safe_storage_days']} days
        </div>
        """,
        unsafe_allow_html=True,
    )

    city = st.text_input("City / District (for weather)", value=st.session_state.user.get("district", "Bengaluru") if st.session_state.user else "Bengaluru")
    state = st.selectbox("State (for mandi lookup)", ["Karnataka", "Maharashtra", "Default"])
    quantity_kg = st.number_input("Quantity Harvested (kg)", min_value=1.0, value=100.0, step=10.0)
    model_choice = st.radio("Prediction Model", ["Random Forest", "XGBoost"], horizontal=True)

with col_right:
    st.markdown(f"#### 📈 {t('current_price', lang)} / {t('market_trend', lang)}")

    view_choice = st.radio(
        "History view", [t("past_month", lang), t("past_year", lang)],
        horizontal=True, label_visibility="collapsed",
    )

    prices = info["historical_prices"]
    labels = month_labels_for_history(12)
    if view_choice == t("past_month", lang):
        plot_prices, plot_labels = prices[-1:], labels[-1:]
        # show a small daily-style zoom using the last value repeated with light noise for illustration
        plot_prices = [round(p, 2) for p in prices[-2:]]
        plot_labels = labels[-2:]
    else:
        plot_prices, plot_labels = prices, labels

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=plot_labels, y=plot_prices, mode="lines+markers",
            line=dict(color="#2d6a4f", width=3), marker=dict(size=7),
            fill="tozeroy", fillcolor="rgba(45,106,79,0.08)",
        )
    )
    fig.update_layout(
        height=320, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, title="Month"),
        yaxis=dict(showgrid=False, title="Price (Rs/kg)"),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"#### 🌦️ {t('weather_today', lang)}")
    weather = fetch_weather(city, api_key=owm_key)
    st.session_state.weather = weather
    w_col1, w_col2, w_col3 = st.columns(3)
    w_col1.metric("Temp (°C)", weather["temperature_c"])
    w_col2.metric("Humidity (%)", weather["humidity_pct"])
    w_col3.metric("Condition", weather["condition"])
    if weather["source"] == "simulated":
        st.caption("⚠️ Showing simulated weather — add an OpenWeather API key in the sidebar for live data.")
    else:
        st.caption("✅ Live weather data from OpenWeather.")

st.divider()

# --------------------------------------------------------------------------
# Harvest age + Generate button
# --------------------------------------------------------------------------
st.markdown(f"#### 📅 {t('harvest_age', lang)}")
harvest_label = st.select_slider(
    t("harvest_age", lang), options=list(HARVEST_AGE_OPTIONS.keys()),
    label_visibility="collapsed",
)
harvest_days = HARVEST_AGE_OPTIONS[harvest_label]

generate = st.button(f"🚀 {t('generate_btn', lang)}", type="primary", use_container_width=True)

if generate:
    model_type = "xgboost" if model_choice == "XGBoost" else "random_forest"
    result = generate_recommendation(
        crop_name=crop_name,
        harvest_age_days=harvest_days,
        weather=weather,
        quantity_kg=quantity_kg,
        model_type=model_type,
    )
    st.session_state.result = result

    mandi_result = fetch_live_mandi_prices(crop_name, state=state, api_key=dgi_key)
    st.session_state.mandi_result = mandi_result
    st.session_state.nearby_mandis = rank_nearby_mandis(mandi_result, top_n=3)

# --------------------------------------------------------------------------
# Recommendation card
# --------------------------------------------------------------------------
if st.session_state.result:
    result = st.session_state.result
    decision = result["decision"]

    badge_class = (
        "sos-badge-sell" if decision.startswith("SELL")
        else "sos-badge-store" if decision.startswith("STORE")
        else "sos-badge-caution"
    )

    st.markdown("### 📋 " + t("recommendation", lang))
    st.markdown(
        f"""
        <div class="sos-card">
            <span class="sos-badge {badge_class}" style="font-size:1rem; padding:0.5rem 1rem;">{decision}</span>
            <p style="margin-top:0.8rem;">{result['reason']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t("current_price", lang), format_currency(result["current_price"]))
    m2.metric(t("predicted_price", lang), format_currency(result["predicted_price"]), result["trend"])
    m3.metric(t("risk_level", lang), result["risk_level"])
    m4.metric(t("storage_days_remaining", lang), result["days_remaining"])

    st.markdown(f"**{t('confidence_score', lang)}:** {result['confidence']}%")
    st.progress(int(result["confidence"]))

    st.caption(f"Model used: {result['model_used']}")

    # ---- Storage cost & profit estimation ----
    st.markdown("#### 💰 " + t("storage_cost", lang) + " & " + t("profit_if_stored", lang))
    pa = result["profit_analysis"]
    p1, p2, p3, p4 = st.columns(4)
    p1.metric(t("storage_cost", lang), format_currency(pa["storage_cost"]))
    p2.metric("Spoilage Loss (kg)", pa["spoilage_kg"])
    p3.metric("Net Revenue if Stored", format_currency(pa["net_revenue_if_stored"]))
    p4.metric(t("profit_if_stored", lang), format_currency(pa["net_gain_from_storing"]))

    if pa["storing_is_better"]:
        st.success("📈 Storing appears more profitable in this scenario, after accounting for spoilage and storage cost.")
    else:
        st.warning("📉 Selling now appears more profitable once spoilage and storage cost are factored in.")

    # ---- Nearby mandi recommendations ----
    st.markdown("#### 🏪 " + t("nearby_mandis", lang))
    nearby = st.session_state.nearby_mandis
    mandi_result = st.session_state.mandi_result
    if mandi_result["source"] == "simulated":
        st.caption("⚠️ Showing simulated mandi data — add a data.gov.in API key in the sidebar for live Agmarknet prices.")
    else:
        st.caption("✅ Live mandi data from data.gov.in (Agmarknet).")

    if nearby:
        mandi_df_rows = [
            {
                "Mandi": m.get("market"),
                "District": m.get("district"),
                "Distance (km)": m.get("distance_km", "N/A"),
                "Modal Price (Rs/quintal)": m.get("modal_price"),
            }
            for m in nearby
        ]
        st.dataframe(mandi_df_rows, use_container_width=True, hide_index=True)

        bar_fig = px.bar(
            mandi_df_rows, x="Mandi", y="Modal Price (Rs/quintal)",
            color="Modal Price (Rs/quintal)", color_continuous_scale="Greens",
        )
        bar_fig.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10), coloraxis_showscale=False)
        st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})

    # ---- Explainable AI ----
    with st.expander(f"🧠 {t('explainability', lang)}", expanded=True):
        st.markdown("**Price prediction model — top influencing features:**")
        ml_factors = rank_ml_feature_importance(result["feature_importance"])
        ml_fig = px.bar(
            ml_factors, x="importance_pct", y="label", orientation="h",
            labels={"importance_pct": "Influence (%)", "label": ""},
            color="importance_pct", color_continuous_scale="Teal",
        )
        ml_fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False)
        st.plotly_chart(ml_fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("**SELL vs STORE decision — top influencing factors:**")
        decision_factors = rank_decision_factors(result["decision_factors"])
        for f in decision_factors:
            st.write(f"- **{f['label']}** — {f['influence_pct']}% influence, pushing **{f['direction']}**")

    # ---- PDF report ----
    st.markdown("#### 📄 " + t("download_report", lang))
    farmer_name = st.session_state.user.get("full_name") if st.session_state.user else "Guest Farmer"
    report_path = os.path.join(os.path.dirname(__file__), "recommendation_report.pdf")
    build_report(
        farmer_name=farmer_name,
        crop_name=crop_name,
        harvest_age_label=harvest_label,
        quantity_kg=quantity_kg,
        result=result,
        weather=weather,
        nearby_mandis=nearby,
        lang=lang,
        output_path=report_path,
    )
    with open(report_path, "rb") as f:
        st.download_button(
            f"⬇️ {t('download_report', lang)}", data=f, file_name="sell_or_store_report.pdf",
            mime="application/pdf", use_container_width=True,
        )

st.divider()

# --------------------------------------------------------------------------
# Footer
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="text-align:center; color:#6b7a6b; font-size:0.85rem; padding-bottom:1rem;">
        <b>Decision Support Tool</b> — {t('responsible_ai', lang)}
    </div>
    """,
    unsafe_allow_html=True,
)
