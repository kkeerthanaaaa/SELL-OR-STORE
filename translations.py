"""
translations.py
----------------
Central store for multi-language text used across the app.
Supported languages: English (en), Hindi (hi), Kannada (kn)

Usage:
    from translations import t
    st.title(t("app_title", lang))
"""

LANGUAGES = {
    "en": "English",
    "hi": "हिंदी (Hindi)",
    "kn": "ಕನ್ನಡ (Kannada)",
}

TEXT = {
    "app_title": {
        "en": "Sell-or-Store: AI Crop Sale Timing Assistant",
        "hi": "सेल-या-स्टोर: फसल बिक्री समय सहायक",
        "kn": "ಮಾರಾಟ-ಅಥವಾ-ಸಂಗ್ರಹ: ಬೆಳೆ ಮಾರಾಟ ಸಮಯ ಸಹಾಯಕ",
    },
    "app_subtitle": {
        "en": "A Decision Support System for Farmers — Not an Automated Decision Maker",
        "hi": "किसानों के लिए निर्णय सहायता प्रणाली — स्वचालित निर्णयकर्ता नहीं",
        "kn": "ರೈತರಿಗಾಗಿ ನಿರ್ಧಾರ ಬೆಂಬಲ ವ್ಯವಸ್ಥೆ — ಸ್ವಯಂಚಾಲಿತ ನಿರ್ಧಾರಕಾರಿಯಲ್ಲ",
    },
    "login": {"en": "Login", "hi": "लॉगिन", "kn": "ಲಾಗಿನ್"},
    "register": {"en": "Register", "hi": "रजिस्टर करें", "kn": "ನೋಂದಣಿ"},
    "username": {"en": "Username", "hi": "उपयोगकर्ता नाम", "kn": "ಬಳಕೆದಾರ ಹೆಸರು"},
    "password": {"en": "Password", "hi": "पासवर्ड", "kn": "ಪಾಸ್‌ವರ್ಡ್"},
    "full_name": {"en": "Full Name", "hi": "पूरा नाम", "kn": "ಪೂರ್ಣ ಹೆಸರು"},
    "district": {"en": "District", "hi": "जिला", "kn": "ಜಿಲ್ಲೆ"},
    "logout": {"en": "Logout", "hi": "लॉगआउट", "kn": "ಲಾಗ್ಔಟ್"},
    "welcome": {"en": "Welcome", "hi": "स्वागत है", "kn": "ಸ್ವಾಗತ"},
    "select_crop": {"en": "Select Crop", "hi": "फसल चुनें", "kn": "ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ"},
    "harvest_age": {"en": "When was it harvested?", "hi": "फसल कब काटी गई?", "kn": "ಬೆಳೆ ಯಾವಾಗ ಕೊಯ್ಲು ಮಾಡಲಾಯಿತು?"},
    "generate_btn": {"en": "Generate Recommendation", "hi": "सिफारिश जनरेट करें", "kn": "ಶಿಫಾರಸು ರಚಿಸಿ"},
    "current_price": {"en": "Current Market Price", "hi": "वर्तमान बाजार मूल्य", "kn": "ಪ್ರಸ್ತುತ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ"},
    "predicted_price": {"en": "Predicted Price (Next Month)", "hi": "अनुमानित मूल्य (अगले महीने)", "kn": "ಮುಂದಿನ ತಿಂಗಳ ಅಂದಾಜು ಬೆಲೆ"},
    "market_trend": {"en": "Market Trend", "hi": "बाजार का रुझान", "kn": "ಮಾರುಕಟ್ಟೆ ಪ್ರವೃತ್ತಿ"},
    "recommendation": {"en": "Recommendation", "hi": "सिफारिश", "kn": "ಶಿಫಾರಸು"},
    "confidence_score": {"en": "Confidence Score", "hi": "विश्वास स्कोर", "kn": "ವಿಶ್ವಾಸ ಅಂಕ"},
    "reason": {"en": "Reason", "hi": "कारण", "kn": "ಕಾರಣ"},
    "storage_days_remaining": {"en": "Safe Storage Days Remaining", "hi": "सुरक्षित भंडारण के शेष दिन", "kn": "ಸುರಕ್ಷಿತ ಸಂಗ್ರಹಣೆಯ ಉಳಿದ ದಿನಗಳು"},
    "suggested_price": {"en": "Suggested Selling Price", "hi": "सुझाया गया विक्रय मूल्य", "kn": "ಸೂಚಿಸಿದ ಮಾರಾಟ ಬೆಲೆ"},
    "risk_level": {"en": "Risk Level", "hi": "जोखिम स्तर", "kn": "ಅಪಾಯದ ಮಟ್ಟ"},
    "weather_today": {"en": "Today's Weather", "hi": "आज का मौसम", "kn": "ಇಂದಿನ ಹವಾಮಾನ"},
    "storage_cost": {"en": "Estimated Storage Cost", "hi": "अनुमानित भंडारण लागत", "kn": "ಅಂದಾಜು ಸಂಗ್ರಹಣಾ ವೆಚ್ಚ"},
    "profit_if_stored": {"en": "Net Profit/Loss if Stored", "hi": "भंडारण करने पर शुद्ध लाभ/हानि", "kn": "ಸಂಗ್ರಹಿಸಿದರೆ ನಿವ್ವಳ ಲಾಭ/ನಷ್ಟ"},
    "nearby_mandis": {"en": "Nearby Mandi Recommendations", "hi": "नज़दीकी मंडी सिफारिशें", "kn": "ಹತ್ತಿರದ ಮಂಡಿ ಶಿಫಾರಸುಗಳು"},
    "download_report": {"en": "Download PDF Report", "hi": "पीडीएफ रिपोर्ट डाउनलोड करें", "kn": "PDF ವರದಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ"},
    "explainability": {"en": "Why this recommendation? (Explainable AI)", "hi": "यह सिफारिश क्यों? (व्याख्येय एआई)", "kn": "ಈ ಶಿಫಾರಸು ಏಕೆ? (ವಿವರಿಸಬಹುದಾದ AI)"},
    "responsible_ai": {
        "en": "This recommendation is generated using historical data, live weather, and crop-specific knowledge. Final selling decisions remain with the farmer.",
        "hi": "यह सिफारिश ऐतिहासिक डेटा, वास्तविक मौसम और फसल-विशिष्ट ज्ञान का उपयोग करके तैयार की गई है। अंतिम बिक्री निर्णय किसान के पास रहता है।",
        "kn": "ಈ ಶಿಫಾರಸು ಐತಿಹಾಸಿಕ ದತ್ತಾಂಶ, ನೇರ ಹವಾಮಾನ ಮತ್ತು ಬೆಳೆ-ನಿರ್ದಿಷ್ಟ ಜ್ಞಾನವನ್ನು ಬಳಸಿ ರಚಿಸಲಾಗಿದೆ. ಅಂತಿಮ ಮಾರಾಟ ನಿರ್ಧಾರ ರೈತರದ್ದೇ ಆಗಿರುತ್ತದೆ.",
    },
    "sell_now": {"en": "SELL NOW", "hi": "अभी बेचें", "kn": "ಈಗ ಮಾರಾಟ ಮಾಡಿ"},
    "store": {"en": "STORE", "hi": "स्टोर करें", "kn": "ಸಂಗ್ರಹಿಸಿ"},
    "caution": {"en": "CAUTION", "hi": "सावधानी", "kn": "ಎಚ್ಚರಿಕೆ"},
    "past_month": {"en": "Past 1 Month", "hi": "पिछला 1 महीना", "kn": "ಕಳೆದ 1 ತಿಂಗಳು"},
    "past_year": {"en": "Past 1 Year", "hi": "पिछला 1 वर्ष", "kn": "ಕಳೆದ 1 ವರ್ಷ"},
    "growing_conditions": {"en": "Growing Conditions", "hi": "उगाने की स्थितियाँ", "kn": "ಬೆಳೆಯುವ ಪರಿಸ್ಥಿತಿಗಳು"},
    "storage_sensitivity": {"en": "Storage Sensitivity", "hi": "भंडारण संवेदनशीलता", "kn": "ಸಂಗ್ರಹಣಾ ಸಂವೇದನಶೀಲತೆ"},
    "safe_storage_days": {"en": "Safe Storage Days", "hi": "सुरक्षित भंडारण दिन", "kn": "ಸುರಕ್ಷಿತ ಸಂಗ್ರಹಣಾ ದಿನಗಳು"},
    "language": {"en": "Language", "hi": "भाषा", "kn": "ಭಾಷೆ"},
    "login_failed": {"en": "Invalid username or password", "hi": "अमान्य उपयोगकर्ता नाम या पासवर्ड", "kn": "ಅಮಾನ್ಯ ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಪಾಸ್‌ವರ್ಡ್"},
    "register_success": {"en": "Registration successful. Please log in.", "hi": "पंजीकरण सफल। कृपया लॉगिन करें।", "kn": "ನೋಂದಣಿ ಯಶಸ್ವಿಯಾಗಿದೆ. ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ."},
    "user_exists": {"en": "Username already exists", "hi": "उपयोगकर्ता नाम पहले से मौजूद है", "kn": "ಬಳಕೆದಾರ ಹೆಸರು ಈಗಾಗಲೇ ಅಸ್ತಿತ್ವದಲ್ಲಿದೆ"},
}


def t(key: str, lang: str = "en") -> str:
    """Return the translated string for `key` in `lang`, falling back to English."""
    entry = TEXT.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get("en", key))
