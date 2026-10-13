
import json
import re
import html
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime

import streamlit as st

# ============================================================
# FARM SATHI — RESPONSIVE FARMING DASHBOARD
# Keep knowledge_base.json in the same folder as this file.
# ============================================================

BASE_DIR = Path(__file__).parent
KB_PATH = BASE_DIR / "knowledge_base.json"

FALLBACK = {
    "en": (
        "I couldn't find reliable information for this question in "
        "FarmSathi's knowledge base. Please contact your local agriculture "
        "officer, Raitha Samparka Kendra, or Krishi Vigyan Kendra (KVK). "
        "Do not spray unknown chemicals."
    ),
    "kn": (
        "ಫಾರ್ಮ್‌ಸಾಥಿ ಜ್ಞಾನ ಭಂಡಾರದಲ್ಲಿ ಈ ಪ್ರಶ್ನೆಗೆ ನಂಬಲರ್ಹ ಮಾಹಿತಿ ಸಿಗಲಿಲ್ಲ. "
        "ಸ್ಥಳೀಯ ಕೃಷಿ ಅಧಿಕಾರಿ, ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ ಅಥವಾ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು "
        "ಸಂಪರ್ಕಿಸಿ. ಗೊತ್ತಿಲ್ಲದ ರಾಸಾಯನಿಕಗಳನ್ನು ಸಿಂಪಡಿಸಬೇಡಿ."
    ),
}

TEXT = {
    "en": {
        "welcome": "Growing a better tomorrow",
        "tagline": "Smart farming starts with the right information.",
        "dashboard": "Your farming dashboard",
        "weather": "Weather",
        "ask": "Ask FarmSathi",
        "doctor": "Crop Doctor",
        "guide": "Crop Guide",
        "weather_desc": "Check local conditions and a 3-day forecast.",
        "ask_desc": "Get guidance from our farming knowledge base.",
        "doctor_desc": "Describe a crop problem and optionally add a photo.",
        "guide_desc": "Explore common crop symptoms and general guidance.",
        "question": "What would you like to know?",
        "placeholder": "e.g. How should I water tomato plants?",
        "get_advice": "Get advice",
        "popular": "Popular questions",
        "location": "Town or village",
        "check_weather": "Check weather",
        "crop": "Select crop",
        "symptom": "Select symptom",
        "get_guidance": "Get guidance",
        "problem": "Describe your crop problem",
        "photo": "Upload a crop photo (optional)",
        "topics": "Available knowledge topics",
        "home": "Home",
        "disclaimer": (
            "FarmSathi is a prototype. Advice comes from a curated knowledge "
            "base and simple weather rules, not a live agricultural expert "
            "or image-diagnosis model. Confirm important decisions locally."
        ),
    },
    "kn": {
        "welcome": "ಉತ್ತಮ ನಾಳೆಗಾಗಿ ಕೃಷಿ",
        "tagline": "ಸರಿಯಾದ ಮಾಹಿತಿಯಿಂದ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಆರಂಭವಾಗುತ್ತದೆ.",
        "dashboard": "ನಿಮ್ಮ ಕೃಷಿ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "weather": "ಹವಾಮಾನ",
        "ask": "ಫಾರ್ಮ್‌ಸಾಥಿಯನ್ನು ಕೇಳಿ",
        "doctor": "ಬೆಳೆ ಸಮಸ್ಯೆ",
        "guide": "ಬೆಳೆ ಮಾರ್ಗದರ್ಶಿ",
        "weather_desc": "ಸ್ಥಳೀಯ ಹವಾಮಾನ ಮತ್ತು 3 ದಿನಗಳ ಮುನ್ಸೂಚನೆ ನೋಡಿ.",
        "ask_desc": "ಕೃಷಿ ಜ್ಞಾನ ಭಂಡಾರದಿಂದ ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ.",
        "doctor_desc": "ಬೆಳೆ ಸಮಸ್ಯೆಯನ್ನು ವಿವರಿಸಿ, ಫೋಟೋ ಕೂಡ ಸೇರಿಸಬಹುದು.",
        "guide_desc": "ಸಾಮಾನ್ಯ ಬೆಳೆ ಲಕ್ಷಣಗಳು ಮತ್ತು ಮಾರ್ಗದರ್ಶನ ನೋಡಿ.",
        "question": "ನಿಮಗೆ ಏನು ತಿಳಿಯಬೇಕು?",
        "placeholder": "ಉದಾ: ಟೊಮೆಟೊ ಗಿಡಗಳಿಗೆ ಹೇಗೆ ನೀರು ಹಾಕಬೇಕು?",
        "get_advice": "ಸಲಹೆ ಪಡೆಯಿರಿ",
        "popular": "ಜನಪ್ರಿಯ ಪ್ರಶ್ನೆಗಳು",
        "location": "ಪಟ್ಟಣ ಅಥವಾ ಗ್ರಾಮದ ಹೆಸರು",
        "check_weather": "ಹವಾಮಾನ ಪರಿಶೀಲಿಸಿ",
        "crop": "ಬೆಳೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "symptom": "ಲಕ್ಷಣವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "get_guidance": "ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ",
        "problem": "ಬೆಳೆ ಸಮಸ್ಯೆಯನ್ನು ವಿವರಿಸಿ",
        "photo": "ಬೆಳೆ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ (ಐಚ್ಛಿಕ)",
        "topics": "ಲಭ್ಯವಿರುವ ವಿಷಯಗಳು",
        "home": "ಮುಖಪುಟ",
        "disclaimer": (
            "ಫಾರ್ಮ್‌ಸಾಥಿ ಒಂದು ಮಾದರಿ ಅಪ್ಲಿಕೇಶನ್. ಸಲಹೆಗಳು ಜ್ಞಾನ ಭಂಡಾರ ಮತ್ತು "
            "ಸರಳ ಹವಾಮಾನ ನಿಯಮಗಳನ್ನು ಆಧರಿಸಿವೆ. ಇದು ನೇರ ಕೃಷಿ ತಜ್ಞರ ಸೇವೆಯಲ್ಲ. "
            "ಮುಖ್ಯ ನಿರ್ಧಾರಗಳನ್ನು ಸ್ಥಳೀಯ ತಜ್ಞರೊಂದಿಗೆ ದೃಢಪಡಿಸಿ."
        ),
    },
}

CROPS = {
    "Tomato": "ಟೊಮೇಟೊ",
    "Ragi": "ರಾಗಿ",
    "Paddy": "ಭತ್ತ",
    "Maize": "ಮೆಕ್ಕೆಜೋಳ",
    "Other": "ಇತರೆ",
}

SYMPTOMS = {
    "Yellow leaves": "ಹಳದಿ ಎಲೆಗಳು",
    "Leaf spots": "ಎಲೆಗಳ ಮೇಲೆ ಚುಕ್ಕೆಗಳು",
    "Wilting": "ಗಿಡ ಬಾಡುತ್ತಿದೆ",
    "Holes in leaves": "ಎಲೆಗಳಲ್ಲಿ ರಂಧ್ರಗಳು",
    "Insects": "ಕೀಟಗಳು",
}

# -------------------------- THEME ----------------------------

def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --forest: #173f2a;
            --green: #2d7147;
            --lime: #a4c96c;
            --cream: #f7f7ef;
            --ink: #20362a;
            --muted: #657568;
            --gold: #edc76c;
        }

        .stApp {
            background:
                radial-gradient(ellipse at top right,
                #e7efd9 0%, transparent 38%),
                #f7f7ef;
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: rgba(247,247,239,.88);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg,#e6eedb,#f8f7ee);
            border-right: 1px solid #d9e4d2;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: var(--forest) !important;
        }

        .block-container {
            max-width: 1250px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4 {
            color: var(--forest) !important;
            letter-spacing: -.35px;
        }

        p, label, li, [data-testid="stCaptionContainer"] {
            color: var(--ink);
        }

        .brand {
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: 1.2px;
            color: var(--forest);
            margin-bottom: .7rem;
        }

        .hero {
            position: relative;
            overflow: hidden;
            padding: 2.1rem;
            min-height: 235px;
            border-radius: 25px;
            background:
                linear-gradient(100deg,
                rgba(17,55,34,.96),
                rgba(35,104,60,.83)),
                url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1500&q=85");
            background-position: center;
            background-size: cover;
            box-shadow: 0 12px 32px rgba(30,75,43,.13);
            margin-bottom: 1.2rem;
        }

        .hero h1 {
            color: #ffffff !important;
            font-size: clamp(2rem,4vw,3rem);
            line-height: 1.12;
            max-width: 650px;
            margin: .4rem 0;
        }

        .hero p {
            color: #edf6e8 !important;
            font-size: 1.04rem;
            max-width: 540px;
            line-height: 1.65;
        }

        .hero-tag {
            color: #f2d991;
            font-weight: 800;
            text-transform: uppercase;
            font-size: .76rem;
            letter-spacing: 2px;
        }

        .section-kicker {
            color: #6a805e;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: .25rem;
        }

        .feature-card {
            background: rgba(255,255,255,.91);
            border: 1px solid #e5e9dc;
            border-radius: 19px;
            padding: 1.15rem;
            min-height: 150px;
            box-shadow: 0 5px 18px rgba(40,70,42,.045);
        }

        .feature-icon {
            width: 43px;
            height: 43px;
            border-radius: 13px;
            background: #e9f1df;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            margin-bottom: .7rem;
        }

        .feature-title {
            font-size: 1.04rem;
            font-weight: 800;
            color: var(--forest);
            margin-bottom: .3rem;
        }

        .feature-desc {
            color: var(--muted);
            font-size: .88rem;
            line-height: 1.5;
        }

        .panel {
            background: #fff;
            border: 1px solid #e5e9dc;
            border-radius: 18px;
            padding: 1.15rem;
            margin: .5rem 0 1rem 0;
        }

        .answer-card {
            background: white;
            border: 1px solid #dce8d7;
            border-left: 6px solid #3e8550;
            padding: 1.2rem;
            border-radius: 15px;
            line-height: 1.75;
            margin: .7rem 0;
        }

        .fallback-card {
            background: #fff5df;
            border-left: 6px solid #d6a344;
            padding: 1.2rem;
            border-radius: 15px;
            line-height: 1.7;
            margin: .7rem 0;
        }

        [data-testid="stMetric"] {
            background: #fff;
            border: 1px solid #e4e9dd;
            border-radius: 15px;
            padding: 1rem;
        }

        [data-testid="stMetricLabel"] {
            color: #637567 !important;
        }

        [data-testid="stMetricValue"] {
            color: var(--forest) !important;
        }

        .stButton button, .stFormSubmitButton button {
            border-radius: 11px;
            min-height: 43px;
            font-weight: 650;
            border: 1px solid #d5e3d0;
            transition: all .15s ease;
        }

        .stButton button[kind="primary"],
        .stFormSubmitButton button[kind="primary"] {
            background: var(--green);
            color: white;
            border: none;
        }

        .stButton button:hover,
        .stFormSubmitButton button:hover {
            border-color: #80a777;
            transform: translateY(-1px);
        }

        .stTextInput input, .stTextArea textarea,
        [data-baseweb="select"] > div {
            border-radius: 10px !important;
            background: #fff !important;
        }

        div[data-testid="stExpander"] {
            border: 1px solid #e1e8da;
            border-radius: 13px;
            background: white;
        }

        hr {
            border-color: #e1e7db;
        }

        @media (max-width: 640px) {
            .block-container {
                padding: 1rem .85rem 2rem .85rem;
            }
            .hero {
                padding: 1.3rem;
                min-height: 210px;
                border-radius: 19px;
            }
            .feature-card {
                padding: .9rem;
                min-height: 155px;
            }
        }
        
/* --- FarmSathi visual upgrade --- */

.brand {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.05rem;
    font-weight: 900;
    letter-spacing: 1.8px;
    color: #173f2a;
    margin: 0 0 14px 2px;
}

.hero {
    min-height: 280px;
    padding: clamp(24px, 4vw, 48px);
    display: flex;
    flex-direction: column;
    justify-content: center;
    background:
        linear-gradient(
            90deg,
            rgba(16, 52, 32, .94) 0%,
            rgba(24, 76, 43, .76) 58%,
            rgba(24, 76, 43, .15) 100%
        ),
        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1600&q=85");
    background-size: cover;
    background-position: center;
    border-radius: 26px;
    box-shadow: 0 16px 35px rgba(24, 68, 37, .16);
    margin-bottom: 30px;
}

.hero h1 {
    max-width: 650px;
    font-size: clamp(2rem, 4vw, 3.25rem);
    line-height: 1.12;
    font-weight: 850;
}

.hero p {
    max-width: 520px;
    line-height: 1.75;
}

.hero-tag {
    display: inline-block;
    color: #f5d88a;
    font-size: .75rem;
    font-weight: 850;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.feature-card {
    overflow: hidden;
    padding: 0;
    min-height: 275px;
    height: 100%;
    background: #fff;
    border: 1px solid #e3e9dd;
    border-radius: 21px;
    box-shadow: 0 7px 23px rgba(30, 68, 39, .07);
    transition: transform .2s ease, box-shadow .2s ease;
}

.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 13px 30px rgba(30, 68, 39, .12);
}

.feature-image {
    width: 100%;
    height: 145px;
    object-fit: cover;
    display: block;
}

.feature-content {
    padding: 16px 18px 20px;
}

.feature-icon {
    width: 43px;
    height: 43px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: #edf4e5;
    font-size: 1.45rem;
    margin-bottom: 10px;
}

.feature-title {
    font-size: 1.05rem;
    font-weight: 850;
    color: #173f2a;
    margin-bottom: 6px;
}

.feature-desc {
    color: #667568;
    font-size: .88rem;
    line-height: 1.65;
}

.section-kicker {
    color: #718365;
    font-size: .76rem;
    font-weight: 850;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.panel {
    background: linear-gradient(120deg, #edf4e4, #fffdf6);
    border: 1px solid #dfe9d7;
    border-radius: 20px;
    padding: 22px;
    margin: 12px 0 20px;
}

.stButton button {
    transition: all .18s ease;
}

.stButton button[kind="primary"] {
    background: #2d7147;
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 750;
}

.stButton button[kind="primary"]:hover {
    background: #205c38;
    border: none;
}

@media (max-width: 640px) {
    .hero {
        min-height: 235px;
        padding: 22px;
        border-radius: 20px;
        background-position: 60% center;
    }

    .feature-card {
        min-height: 250px;
        border-radius: 17px;
    }

    .feature-image {
        height: 115px;
    }

    .feature-content {
        padding: 13px;
    }
}

        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------- KNOWLEDGE BASE -----------------------

@st.cache_data
def load_knowledge_base():
    if not KB_PATH.exists():
        return []
    with KB_PATH.open(encoding="utf-8") as file:
        data = json.load(file)
    return data.get("entries", [])


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\u0C80-\u0CFF]", " ", text)
    return re.sub(r"\s+", " ", text)


def score_entry(question, entry):
    q = normalize(question)
    if not q:
        return 0

    score = 0
    keywords = entry.get("keywords_en", []) + entry.get("keywords_kn", [])

    for keyword in keywords:
        key = normalize(keyword)
        if key and key in q:
            score += 3 if " " in key else 2

    for word in q.split():
        if len(word) < 3:
            continue
        for keyword in keywords:
            key = normalize(keyword)
            if word == key or (len(word) >= 4 and word in key):
                score += 1

    return score


def find_best_entry(question, entries):
    ranked = [
        (score_entry(question, entry), entry)
        for entry in entries
    ]
    if not ranked:
        return None, 0

    ranked.sort(key=lambda item: item[0], reverse=True)
    score, entry = ranked[0]
    return (entry, score) if score >= 2 else (None, score)


def get_answer_text(entry, lang):
    title_key = "title_kn" if lang == "kn" else "title_en"
    answer_key = "answer_kn" if lang == "kn" else "answer_en"
    return (
        entry.get(title_key, "FarmSathi"),
        entry.get(answer_key, FALLBACK[lang]),
        entry.get("source", "FarmSathi knowledge base"),
    )


def show_answer(title, answer, source=None):
    # Escape text before placing it into HTML.
    title = html.escape(str(title))
    answer = html.escape(str(answer)).replace("\n", "<br>")
    source_html = ""
    if source:
        source_html = (
            '<p style="color:#55725a;font-size:.85rem;margin-bottom:0">'
            "<b>Source:</b> " + html.escape(str(source)) + "</p>"
        )
    st.markdown(
        f'<div class="answer-card"><b>{title}</b>'
        f'<p>{answer}</p>{source_html}</div>',
        unsafe_allow_html=True,
    )


# ------------------------- WEATHER ----------------------------

def get_json_from_url(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "FarmSathi/1.0"}
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def find_location(place):
    aliases = {
        "ಮೈಸೂರು": "Mysuru, Karnataka, India",
        "ಬೆಂಗಳೂರು": "Bengaluru, Karnataka, India",
        "ಹಾಸನ": "Hassan, Karnataka, India",
        "ಚನ್ನರಾಯಪಟ್ಟಣ": "Channarayapatna, Karnataka, India",
    }
    place = aliases.get(place.strip(), place.strip())
    if not place:
        return None

    params = urllib.parse.urlencode({
        "name": place,
        "count": 10,
        "language": "en",
        "format": "json",
    })
    data = get_json_from_url(
        "https://geocoding-api.open-meteo.com/v1/search?" + params
    )
    results = data.get("results", [])

    for result in results:
        if (
            result.get("country_code") == "IN"
            and result.get("admin1", "").lower() == "karnataka"
        ):
            return result

    return results[0] if results else None


def get_weather(latitude, longitude):
    params = urllib.parse.urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,weather_code,wind_speed_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,precipitation_sum"
        ),
        "forecast_days": 3,
        "timezone": "auto",
    })
    return get_json_from_url(
        "https://api.open-meteo.com/v1/forecast?" + params
    )


def weather_description(code):
    descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
        3: "Overcast", 45: "Fog", 48: "Fog",
        51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 80: "Rain showers", 81: "Rain showers",
        82: "Heavy rain showers", 95: "Thunderstorm",
        96: "Thunderstorm with hail", 99: "Thunderstorm with hail",
    }
    return descriptions.get(code, "Conditions unavailable")


def show_weather(lang):
    t = TEXT[lang]
    st.markdown(f"## 🌦️ {t['weather']}")
    st.write(t["weather_desc"])

    with st.form("weather_search_form"):
        place = st.text_input(
            t["location"],
            placeholder="Mysuru" if lang == "en" else "ಮೈಸೂರು",
        )
        submitted = st.form_submit_button(
            t["check_weather"], type="primary", use_container_width=True
        )

    if not submitted:
        st.info(
            "Enter a town or village above to load its forecast."
            if lang == "en"
            else "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆಗಾಗಿ ಮೇಲಿನ ಸ್ಥಳದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ."
        )
        return

    if not place.strip():
        st.warning("Please enter a location." if lang == "en" else "ಸ್ಥಳದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ.")
        return

    try:
        with st.spinner("Loading weather..."):
            location = find_location(place)
            if not location:
                st.warning("Location not found. Try adding the district or state.")
                return
            weather = get_weather(location["latitude"], location["longitude"])

        current = weather.get("current", {})
        daily = weather.get("daily", {})

        st.markdown(
            f"### 📍 {location.get('name', place)}, "
            f"{location.get('admin1', '')}"
        )
        st.caption(
            weather_description(current.get("weather_code"))
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature", f"{current.get('temperature_2m', '—')} °C")
        c2.metric("Humidity", f"{current.get('relative_humidity_2m', '—')}%")
        c3.metric("Wind", f"{current.get('wind_speed_10m', '—')} km/h")

        st.markdown("### 📅 Three-day forecast")
        rows = []
        for i, date in enumerate(daily.get("time", [])):
            rows.append({
                "Date": date,
                "Conditions": weather_description(
                    daily.get("weather_code", [None] * 3)[i]
                ),
                "Min °C": daily.get("temperature_2m_min", [None] * 3)[i],
                "Max °C": daily.get("temperature_2m_max", [None] * 3)[i],
                "Rain chance %": daily.get(
                    "precipitation_probability_max", [None] * 3
                )[i],
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

        st.markdown("### 🌱 Weather-based farming tips")
        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        rain = daily.get("precipitation_probability_max", [])
        amounts = daily.get("precipitation_sum", [])

        if any(x is not None and x >= 50 for x in rain):
            st.info(
                "Rain may occur. Check field drainage and soil moisture "
                "before deciding whether irrigation is needed."
            )
        else:
            st.info(
                "Check soil moisture and crop needs before irrigation. "
                "Do not rely on weather data alone."
            )

        if temp is not None and temp >= 35:
            st.warning("High temperature: monitor crops for heat stress.")

        if humidity is not None and humidity >= 80:
            st.info("Humidity is high. Inspect crops for disease symptoms.")

        if any(x is not None and x >= 70 for x in rain) or any(
            x is not None and x >= 20 for x in amounts
        ):
            st.warning(
                "Heavy-rain risk may be present. Check the latest forecast "
                "and drainage conditions."
            )

        crop = st.selectbox(
            "Crop-specific tips",
            ["Tomato", "Ragi", "Paddy", "Maize", "Other"],
            format_func=lambda x: CROPS[x] if lang == "kn" else x,
            key="weather_crop",
        )
        tips = {
            "Tomato": "Check soil moisture and avoid waterlogging.",
            "Ragi": "Monitor soil moisture and field drainage after rain.",
            "Paddy": "Manage field water according to crop stage.",
            "Maize": "Monitor soil moisture and avoid waterlogging.",
            "Other": "Check crop-specific guidance with a local expert.",
        }
        st.success(tips[crop])
        st.caption(
            "Weather data: Open-Meteo. Forecasts can change."
        )

    except Exception:
        st.error(
            "Weather data could not be loaded. Check your internet connection "
            "and try again."
        )


# ---------------------- CROP PROBLEM GUIDE --------------------

def crop_guidance(crop, symptom, lang):
    en = {
        "Yellow leaves": (
            "Possible causes include nutrient deficiency, water stress, "
            "or natural leaf ageing. Check soil moisture and whether old "
            "or new leaves are affected."
        ),
        "Leaf spots": (
            "Leaf spots can have several causes, including disease and "
            "environmental stress. Check whether spots are spreading."
        ),
        "Wilting": (
            "Wilting may be caused by too little water, waterlogged soil, "
            "root damage, or disease. Check moisture and drainage before "
            "watering more."
        ),
        "Holes in leaves": (
            "Inspect both sides of leaves for insects, eggs, or droppings. "
            "Confirm the pest before choosing a treatment."
        ),
        "Insects": (
            "Inspect the undersides of leaves and new shoots. Note the "
            "insect's appearance and whether damage is spreading."
        ),
    }
    kn = {
        "Yellow leaves": (
            "ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ, ನೀರಿನ ಒತ್ತಡ ಅಥವಾ ಎಲೆಗಳ ಸಹಜ ವಯಸ್ಸಾಗುವಿಕೆ "
            "ಕಾರಣವಾಗಿರಬಹುದು. ಮಣ್ಣಿನ ತೇವಾಂಶ ಪರಿಶೀಲಿಸಿ."
        ),
        "Leaf spots": (
            "ಎಲೆಗಳ ಚುಕ್ಕೆಗಳಿಗೆ ರೋಗ ಅಥವಾ ಪರಿಸರದ ಒತ್ತಡ ಕಾರಣವಾಗಿರಬಹುದು. "
            "ಚುಕ್ಕೆಗಳು ಹರಡುತ್ತಿವೆಯೇ ಪರಿಶೀಲಿಸಿ."
        ),
        "Wilting": (
            "ನೀರಿನ ಕೊರತೆ, ಮಣ್ಣಿನಲ್ಲಿ ನೀರು ನಿಲ್ಲುವುದು ಅಥವಾ ಬೇರುಗಳ ಹಾನಿಯಿಂದ "
            "ಗಿಡ ಬಾಡಬಹುದು. ಹೆಚ್ಚು ನೀರು ಹಾಕುವ ಮೊದಲು ತೇವಾಂಶ ಪರಿಶೀಲಿಸಿ."
        ),
        "Holes in leaves": (
            "ಎಲೆಗಳ ಎರಡೂ ಬದಿಗಳಲ್ಲಿ ಕೀಟಗಳು, ಮೊಟ್ಟೆಗಳು ಅಥವಾ ಕೀಟಗಳ ಮಲವಿದೆಯೇ "
            "ಪರಿಶೀಲಿಸಿ. ಚಿಕಿತ್ಸೆಗೂ ಮೊದಲು ಕೀಟವನ್ನು ಗುರುತಿಸಿಕೊಳ್ಳಿ."
        ),
        "Insects": (
            "ಎಲೆಗಳ ಕೆಳಭಾಗ ಮತ್ತು ಹೊಸ ಚಿಗುರುಗಳನ್ನು ಪರಿಶೀಲಿಸಿ. ಕೀಟದ ರೂಪ ಮತ್ತು "
            "ಹಾನಿ ಹರಡುತ್ತಿದೆಯೇ ಗಮನಿಸಿ."
        ),
    }
    crop_name = CROPS.get(crop, crop) if lang == "kn" else crop
    explanation = (kn if lang == "kn" else en)[symptom]
    note = (
        "ಇದು ಸಾಮಾನ್ಯ ಮಾರ್ಗದರ್ಶನ ಮಾತ್ರ; ಖಚಿತ ರೋಗನಿರ್ಣಯವಲ್ಲ."
        if lang == "kn"
        else "This is general guidance, not a confirmed diagnosis."
    )
    return f"Selected crop: {crop_name}\n\n{explanation}\n\n{note}"


def show_crop_doctor(lang, entries):
    t = TEXT[lang]
    st.markdown(f"## 🩺 {t['doctor']}")
    st.write(t["doctor_desc"])

    with st.form("crop_problem_form"):
        crop = st.selectbox(
            t["crop"],
            list(CROPS),
            format_func=lambda x: CROPS[x] if lang == "kn" else x,
        )
        problem = st.text_area(
            t["problem"],
            placeholder=(
                "Example: Leaves are turning yellow"
                if lang == "en" else "ಉದಾ: ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ"
            ),
            max_chars=500,
        )
        photo = st.file_uploader(
            t["photo"], type=["jpg", "jpeg", "png"]
        )
        submitted = st.form_submit_button(
            t["get_guidance"], type="primary", use_container_width=True
        )

    if photo is not None:
        st.image(
            photo,
            caption="Uploaded crop photo",
            use_container_width=True,
        )
        st.caption(
            "The photo is shown for reference; this prototype does not "
            "automatically diagnose images."
        )

    if submitted:
        if not problem.strip():
            st.warning(
                "Please describe the problem first."
                if lang == "en" else "ಮೊದಲು ಸಮಸ್ಯೆಯನ್ನು ವಿವರಿಸಿ."
            )
        else:
            query = problem if crop == "Other" else crop + " " + problem
            match, _ = find_best_entry(query, entries)
            if match:
                title, answer, source = get_answer_text(match, lang)
                show_answer(title, answer, source)
            else:
                st.markdown(
                    f'<div class="fallback-card">{html.escape(FALLBACK[lang])}</div>',
                    unsafe_allow_html=True,
                )
            st.caption(
                "For serious or spreading crop problems, consult a local "
                "agricultural expert before choosing a treatment."
            )


def show_symptom_guide(lang):
    t = TEXT[lang]
    st.markdown(f"## 🌿 {t['guide']}")
    st.write(t["guide_desc"])

    crop = st.selectbox(
        t["crop"],
        list(CROPS),
        format_func=lambda x: CROPS[x] if lang == "kn" else x,
        key="guide_crop",
    )
    symptom = st.selectbox(
        t["symptom"],
        list(SYMPTOMS),
        format_func=lambda x: SYMPTOMS[x] if lang == "kn" else x,
        key="guide_symptom",
    )
    if st.button(t["get_guidance"], type="primary", key="guide_button"):
        st.info(crop_guidance(crop, symptom, lang))
        st.caption(
            "Confirm the cause locally. Do not apply unknown pesticides."
        )


# ------------------------ ASK FARM SATHI ----------------------

def show_ask_page(lang, entries):
    t = TEXT[lang]
    st.markdown(f"## 💬 {t['ask']}")
    st.write(t["ask_desc"])

    questions = (
        {
            "🌱 Soil health": "How can I improve soil health?",
            "🍅 Tomato watering": "How should I water tomato plants?",
            "💧 Drip irrigation": "What is drip irrigation?",
            "🐛 Crop pests": "How can I manage aphids?",
        }
        if lang == "en"
        else {
            "🌱 ಮಣ್ಣಿನ ಆರೋಗ್ಯ": "ಮಣ್ಣಿನ ಆರೋಗ್ಯವನ್ನು ಹೇಗೆ ಸುಧಾರಿಸಬಹುದು?",
            "🍅 ಟೊಮೆಟೊ ನೀರಾವರಿ": "ಟೊಮೆಟೊ ಗಿಡಗಳಿಗೆ ಹೇಗೆ ನೀರು ಹಾಕಬೇಕು?",
            "💧 ಹನಿ ನೀರಾವರಿ": "ಹನಿ ನೀರಾವರಿ ಎಂದರೇನು?",
            "🐛 ಗಿಡಹೇನು": "ಗಿಡಹೇನು ಬಂದರೆ ಏನು ಮಾಡಬೇಕು?",
        }
    )

    st.markdown(f"### {t['popular']}")
    cols = st.columns(2)
    for i, (label, question) in enumerate(questions.items()):
        with cols[i % 2]:
            if st.button(label, key=f"popular_{lang}_{i}",
                         use_container_width=True):
                st.session_state["farm_question"] = question

    if "farm_question" not in st.session_state:
        st.session_state["farm_question"] = ""

    question = st.text_area(
        t["question"],
        placeholder=t["placeholder"],
        key="farm_question",
        height=105,
    )

    if st.button(t["get_advice"], type="primary",
                  use_container_width=True, key="ask_submit"):
        if not question.strip():
            st.warning(
                "Please type a question first."
                if lang == "en" else "ದಯವಿಟ್ಟು ಮೊದಲು ಪ್ರಶ್ನೆ ಬರೆಯಿರಿ."
            )
        else:
            match, _ = find_best_entry(question, entries)
            if match:
                title, answer, source = get_answer_text(match, lang)
                show_answer(title, answer, source)
            else:
                st.markdown(
                    f'<div class="fallback-card">'
                    f'<b>FarmSathi</b><p>{html.escape(FALLBACK[lang])}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# --------------------------- HOME -----------------------------


def feature_card(icon, title, description, image_url):
    safe_title = html.escape(str(title))
    safe_description = html.escape(str(description))
    safe_icon = html.escape(str(icon))
    safe_url = html.escape(str(image_url), quote=True)

    st.markdown(
        f"""
        <div class="feature-card">
            <img
                class="feature-image"
                src="{safe_url}"
                alt="Farming and agriculture"
                loading="lazy"
            />
            <div class="feature-content">
                <div class="feature-icon">{safe_icon}</div>
                <div class="feature-title">{safe_title}</div>
                <div class="feature-desc">{safe_description}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def show_home(lang):
    t = TEXT[lang]

    st.markdown(
        f"""
        <div class="brand">🌾 FARMSATHI</div>

        <div class="hero">
            <div class="hero-tag">
                SMART FARMING · BETTER TOMORROW
            </div>
            <h1>{html.escape(t['welcome'])}</h1>
            <p>{html.escape(t['tagline'])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="section-kicker">YOUR FARMING TOOLS</div>'
        f'<h2>{html.escape(t["dashboard"])}</h2>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Everything you need to start your farming journey."
        if lang == "en"
        else "ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಯಾಣಕ್ಕೆ ಬೇಕಾದ ಉಪಯುಕ್ತ ಸಾಧನಗಳು."
    )

    # Use separate images for the four feature cards.
    cards = [
        (
            "🌦️",
            t["weather"],
            t["weather_desc"],
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=900&q=80",
        ),
        
(
    "💬",
    t["ask"],
    t["ask_desc"],
    "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=900&q=80",
),

        (
            "🩺",
            t["doctor"],
            t["doctor_desc"],
            "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=900&q=80",
        ),
        (
            "🌿",
            t["guide"],
            t["guide_desc"],
            "https://images.unsplash.com/photo-1492496913980-501348b61469?auto=format&fit=crop&w=900&q=80",
        ),
    ]

    left, right = st.columns(2, gap="large")

    for index, (icon, title, description, image_url) in enumerate(cards):
        with (left if index % 2 == 0 else right):
            feature_card(icon, title, description, image_url)
            st.write("")

    st.markdown(
        """
        <div class="panel">
            <div class="section-kicker">GROW WITH CONFIDENCE</div>
            <h3>🌱 Make informed farming decisions</h3>
            <p style="color:#657568;line-height:1.8">
                Explore farming knowledge, check local weather forecasts,
                and learn about common crop symptoms. When an answer is
                uncertain, consult a local agricultural expert.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------- APP -----------------------------

def main():
    st.set_page_config(
        page_title="FarmSathi | Smart Farming Assistant",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()

    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"

    if "page" not in st.session_state:
        st.session_state["page"] = "Home"

    lang = st.sidebar.radio(
        "Language / ಭಾಷೆ",
        ["en", "kn"],
        format_func=lambda x: "English" if x == "en" else "ಕನ್ನಡ",
        horizontal=True,
        key="language_choice",
    )
    st.session_state["lang"] = lang
    t = TEXT[lang]

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🌾 FarmSathi")
    st.sidebar.caption(
        "Your farming companion"
        if lang == "en" else "ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ"
    )

    page_options = {
        t["home"]: "Home",
        t["weather"]: "Weather",
        t["ask"]: "Ask FarmSathi",
        t["doctor"]: "Crop Doctor",
        t["guide"]: "Crop Guide",
    }
    selected_label = st.sidebar.radio(
        "Navigate",
        list(page_options.keys()),
        index=list(page_options.values()).index(
            st.session_state["page"]
        ) if st.session_state["page"] in page_options.values() else 0,
    )
    page = page_options[selected_label]
    st.session_state["page"] = page

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Built to support small farmers 🌱"
        if lang == "en" else "ಸಣ್ಣ ರೈತರಿಗಾಗಿ ನಿರ್ಮಿಸಲಾಗಿದೆ 🌱"
    )

    entries = load_knowledge_base()
    if not entries:
        st.warning(
            "knowledge_base.json was not found or contains no entries. "
            "Put your existing knowledge_base.json next to app.py."
        )

    if page == "Home":
        show_home(lang)
    elif page == "Weather":
        show_weather(lang)
    elif page == "Ask FarmSathi":
        show_ask_page(lang, entries)
    elif page == "Crop Doctor":
        show_crop_doctor(lang, entries)
    elif page == "Crop Guide":
        show_symptom_guide(lang)

    st.markdown("---")
    st.caption(t["disclaimer"])


if __name__ == "__main__":
    main()
