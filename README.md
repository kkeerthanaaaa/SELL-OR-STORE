# 🌾 Sell-or-Store: AI-Based Crop Sale Timing Assistant for Farmers

A Decision Support System (not an automated decision maker) that helps farmers decide
whether to **sell** their harvested crop now or **store** it a while longer, using
live weather, mandi price data, and machine learning.

## ✨ Features

| Feature | Details |
|---|---|
| 🌦️ Real-time weather | OpenWeather API integration (falls back to simulated data if no key) |
| 🏪 Real mandi prices | data.gov.in / Agmarknet integration (falls back to simulated data if no key) |
| 🤖 Better ML model | Random Forest (default) or XGBoost price prediction with engineered time-series features |
| 📄 PDF report | One-click downloadable recommendation report (fpdf2) |
| 🌍 Multi-language | English, Hindi (हिंदी), Kannada (ಕನ್ನಡ) |
| 🔐 Farmer authentication | Simple username/password login & registration (local JSON store) |
| 📍 Nearby mandi recommendation | Ranks nearby mandis by a blend of price and distance |
| 💰 Storage cost estimation | Rs/kg/day storage cost modelling per crop |
| 📈 Profit-if-stored estimation | Compares net revenue of selling now vs. storing, incl. spoilage loss |
| 📊 Interactive dashboard | Plotly charts (line, bar) replacing static Matplotlib |
| 🧠 Explainable AI | Shows top factors behind both the price prediction and the SELL/STORE decision |
| 📱 Mobile-friendly | Responsive CSS breakpoints and Streamlit wide layout |

## 🗂️ Project Structure

```
Sell_or_Store/
├── app.py                  # Main Streamlit dashboard
├── auth.py                 # Farmer authentication (register/login)
├── crop_data.py             # Crop knowledge base
├── weather_api.py          # OpenWeather integration
├── mandi_data.py            # data.gov.in / Agmarknet integration + nearby mandi ranking
├── ml_model.py              # Random Forest / XGBoost price prediction
├── decision_engine.py       # Combines everything into a SELL/STORE/CAUTION decision
├── storage_economics.py     # Storage cost & profit-if-stored calculations
├── explainability.py        # Human-readable ranked explanations (XAI)
├── pdf_report.py            # PDF report generation (fpdf2)
├── translations.py          # English / Hindi / Kannada text
├── utils.py                 # Formatting & CSS helpers
├── images/                  # Crop images (rice, wheat, onion, tomato, potato, maize)
├── data/users.json          # Local auth store (auto-created on first run)
├── .streamlit/config.toml   # Theme
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

```bash
cd Sell_or_Store
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## 🔑 Configuring Live Data (optional)

The app works out of the box with clearly-labelled **simulated** weather and mandi
data. To use live data:

1. **Weather** — get a free key at https://openweathermap.org/api, then either:
   - `export OPENWEATHER_API_KEY="your_key"` before launching, or
   - paste it into the sidebar "OpenWeather API key" field inside the running app.
2. **Mandi prices** — get a free key at https://data.gov.in (My Account → API keys), then either:
   - `export DATA_GOV_IN_API_KEY="your_key"` before launching, or
   - paste it into the sidebar "data.gov.in API key" field inside the running app.

If a key is missing or a request fails (no internet, rate limit, etc.), the app
automatically falls back to simulated data and tells you so on-screen — it never
crashes because of a missing key.

## 🔐 Authentication Notes

`auth.py` implements a lightweight, salted-SHA-256 username/password system backed
by `data/users.json`. It's suitable for demos and single-instance deployments, but
is **not** a production-grade identity system (no password reset, email
verification, or brute-force protection). For production, swap in a real
identity provider (Auth0, Firebase Auth, Streamlit's native auth, etc.).

## 🧠 Machine Learning Details

`ml_model.py` engineers features from the 12-month price history (lagged prices,
rolling average, trend slope, plus the live weather risk score) and trains a
`RandomForestRegressor` (default) or `XGBRegressor` (if selected and installed) to
predict next month's price. Feature importances feed directly into the
Explainable AI panel. If XGBoost isn't installed, the app automatically falls
back to Random Forest.

## ⚖️ Responsible AI

This app is a **Decision Support Tool**. It surfaces data, predictions, and
reasoning — the final selling decision always remains with the farmer.

## 📝 License / Attribution

Crop images are simple generated placeholders — replace `images/*.jpg` with real
photos for a production deployment. Mandi price schema is modelled on the
data.gov.in "Current Daily Price of Various Commodities" resource (Agmarknet mirror).
