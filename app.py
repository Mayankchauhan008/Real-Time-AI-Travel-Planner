import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from fpdf import FPDF
import io
import re

# Import our services
from services.geocoding_service import GeocodingService
from services.places_service import PlacesService
from services.weather_service import WeatherService
from services.ai_service import AIService

# Load environment variables
load_dotenv()

# ─────────────────────────────────────────────
# INIT SERVICES
# ─────────────────────────────────────────────
@st.cache_resource
def init_services():
    return {
        'geocoding': GeocodingService(
            os.getenv("GOOGLE_MAPS_API_KEY"),
            os.getenv("GEOAPIFY_API_KEY")
        ),
        'places': PlacesService(os.getenv("GOOGLE_MAPS_API_KEY")),
        'weather': WeatherService(os.getenv("WEATHER_API_KEY")),
        'ai': AIService(os.getenv("OPENAI_API_KEY"))
    }

services = init_services()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL CSS — Premium Dark-Luxury Aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root Variables ── */
:root {
    --gold: #C9A84C;
    --gold-light: #E8C97A;
    --bg-dark: #0D0F14;
    --bg-card: #161920;
    --bg-surface: #1E2229;
    --text-primary: #F0EDE8;
    --text-muted: #8B8B9A;
    --accent-blue: #4A9EFF;
    --accent-green: #3ECF8E;
    --accent-red: #FF6B6B;
    --border: rgba(201,168,76,0.2);
    --radius: 16px;
}

/* ── Global Overrides ── */
html, body, .stApp {
    background-color: var(--bg-dark) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0D0F14 0%, #1a1600 50%, #0D0F14 100%);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -60%;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 300px;
    background: radial-gradient(ellipse, rgba(201,168,76,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 50%, var(--gold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    line-height: 1.1;
}
.hero-subtitle {
    color: var(--text-muted);
    font-size: 1.05rem;
    font-weight: 300;
    letter-spacing: 0.05em;
}
.hero-badges {
    display: flex;
    justify-content: center;
    gap: 0.75rem;
    margin-top: 1.25rem;
    flex-wrap: wrap;
}
.badge {
    background: rgba(201,168,76,0.1);
    border: 1px solid var(--border);
    color: var(--gold-light);
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.03em;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stDateInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stSelectSlider div,
[data-testid="stSidebar"] .stMultiSelect div {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
}
.sidebar-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: var(--gold);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--gold) 0%, #A8883A 100%) !important;
    color: #0D0F14 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(201,168,76,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(201,168,76,0.5) !important;
}

/* ── Cards ── */
.trip-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.3s ease, transform 0.2s ease;
    position: relative;
    overflow: hidden;
}
.trip-card:hover {
    border-color: var(--gold);
    transform: translateY(-2px);
}
.trip-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--gold), var(--gold-light), var(--gold));
    opacity: 0;
    transition: opacity 0.3s ease;
}
.trip-card:hover::before { opacity: 1; }

.hotel-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: all 0.3s ease;
}
.hotel-card:hover {
    border-color: var(--gold);
    box-shadow: 0 0 30px rgba(201,168,76,0.1);
}
.hotel-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: var(--gold-light);
    margin-bottom: 0.25rem;
}
.hotel-address {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 0.75rem;
}
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: var(--bg-surface);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}
.price-tag {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--gold);
}

/* ── Section Headers ── */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: var(--gold);
    margin-bottom: 0.25rem;
}
.section-divider {
    height: 2px;
    background: linear-gradient(90deg, var(--gold), transparent);
    margin-bottom: 1.5rem;
    border: none;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-testid="stTab"] {
    background: var(--bg-card) !important;
    color: var(--text-muted) !important;
    border: 1px solid transparent !important;
    border-radius: 10px 10px 0 0 !important;
    font-weight: 500 !important;
}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    background: var(--bg-surface) !important;
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
}

/* ── Weather Cards ── */
.weather-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem;
    text-align: center;
}
.weather-temp {
    font-size: 2rem;
    font-weight: 700;
    color: var(--gold-light);
    font-family: 'Playfair Display', serif;
}
.weather-label {
    color: var(--text-muted);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Activity Timeline ── */
.timeline-item {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.2rem;
    padding-left: 0.5rem;
    border-left: 2px solid var(--border);
    padding-left: 1.2rem;
    position: relative;
}
.timeline-item::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 6px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--gold);
}
.timeline-time {
    color: var(--gold);
    font-weight: 600;
    font-size: 0.85rem;
    white-space: nowrap;
    min-width: 70px;
}
.timeline-content {
    color: var(--text-primary);
    font-size: 0.95rem;
}
.timeline-meta {
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-top: 0.2rem;
}

/* ── Payment Form ── */
.payment-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2rem;
    max-width: 640px;
    margin: 0 auto;
}
.payment-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    color: var(--gold);
    margin-bottom: 0.25rem;
}
.payment-subtitle {
    color: var(--text-muted);
    font-size: 0.875rem;
    margin-bottom: 1.5rem;
}
.payment-method-btn {
    background: var(--bg-surface);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    color: var(--text-primary);
}
.payment-method-btn.active {
    border-color: var(--gold);
    background: rgba(201,168,76,0.08);
    color: var(--gold);
}
.payment-summary-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.9rem;
    color: var(--text-muted);
}
.payment-total-row {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 0;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--gold);
}
.input-label {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-bottom: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.form-input {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 0.75rem 1rem !important;
    width: 100% !important;
    font-family: 'DM Sans', sans-serif !important;
}
.success-box {
    background: rgba(62,207,142,0.1);
    border: 1px solid var(--accent-green);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    color: var(--accent-green);
}
.error-box {
    background: rgba(255,107,107,0.1);
    border: 1px solid var(--accent-red);
    border-radius: 14px;
    padding: 1rem;
    color: var(--accent-red);
    font-size: 0.9rem;
}

/* ── PDF Download Button ── */
.pdf-btn-wrap a {
    display: inline-block;
    background: linear-gradient(135deg, var(--gold) 0%, #A8883A 100%);
    color: #0D0F14 !important;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 0.7rem 2rem;
    border-radius: 12px;
    text-decoration: none;
    letter-spacing: 0.05em;
    box-shadow: 0 4px 20px rgba(201,168,76,0.3);
    transition: all 0.3s;
}
.pdf-btn-wrap a:hover {
    box-shadow: 0 8px 30px rgba(201,168,76,0.5);
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.75rem 1rem;
}
[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--gold-light) !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── Info / Success boxes ── */
.stAlert {
    border-radius: 12px !important;
    border-left: 4px solid var(--gold) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPER: CLEAN TEXT FOR PDF
# ─────────────────────────────────────────────
def clean_text(text):
    """Remove characters not supported by latin-1 for FPDF."""
    if not text:
        return ""
    text = str(text)
    replacements = {
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u2022': '-',
        '\u00e9': 'e', '\u00e8': 'e', '\u00ea': 'e', '\u00eb': 'e',
        '\u00e0': 'a', '\u00e2': 'a', '\u00e4': 'a', '\u00ee': 'i',
        '\u00f4': 'o', '\u00f6': 'o', '\u00fc': 'u', '\u00e7': 'c',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', errors='replace').decode('latin-1')

# ─────────────────────────────────────────────
# TASK 2: PDF GENERATOR
# ─────────────────────────────────────────────
def generate_trip_pdf(destination, start_date, num_days, num_travelers, budget,
                      daily_plans, hotels, restaurants, attractions,
                      current_weather, weather_forecast):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ─── COVER PAGE ───────────────────────────
    pdf.add_page()
    pdf.set_fill_color(13, 15, 20)
    pdf.rect(0, 0, 210, 297, 'F')

    # Gold accent bar
    pdf.set_fill_color(201, 168, 76)
    pdf.rect(0, 0, 210, 8, 'F')

    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(201, 168, 76)
    pdf.ln(35)
    pdf.cell(0, 14, "AI TRAVEL PLANNER", ln=True, align='C')

    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(232, 201, 122)
    pdf.cell(0, 10, clean_text(f"Your Journey to {destination}"), ln=True, align='C')

    pdf.ln(10)
    pdf.set_draw_color(201, 168, 76)
    pdf.set_line_width(0.5)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(10)

    # Trip summary box
    pdf.set_fill_color(30, 34, 41)
    pdf.set_text_color(240, 237, 232)
    pdf.set_font("Helvetica", "", 13)

    details = [
        ("Destination", f"{destination}"),
        ("Travel Dates", f"{start_date.strftime('%d %b %Y')} - {(start_date + timedelta(days=num_days)).strftime('%d %b %Y')}"),
        ("Duration", f"{num_days} days"),
        ("Travelers", f"{num_travelers} person(s)"),
        ("Budget", f"{budget}"),
    ]
    for label, value in details:
        pdf.set_x(40)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(201, 168, 76)
        pdf.cell(55, 9, f"{label}:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(240, 237, 232)
        pdf.cell(0, 9, clean_text(value), ln=True)

    pdf.ln(8)
    pdf.set_line_width(0.5)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(139, 139, 154)
    pdf.cell(0, 6, f"Generated on {datetime.now().strftime('%d %b %Y at %H:%M')} | Powered by Real APIs", ln=True, align='C')

    # Gold bar bottom
    pdf.set_fill_color(201, 168, 76)
    pdf.rect(0, 289, 210, 8, 'F')

    # ─── PAGE HELPER ──────────────────────────
    def add_section_header(title, emoji=""):
        pdf.add_page()
        pdf.set_fill_color(201, 168, 76)
        pdf.rect(0, 0, 210, 6, 'F')
        pdf.ln(12)
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(201, 168, 76)
        pdf.cell(0, 10, clean_text(f"{emoji}  {title}"), ln=True, align='C')
        pdf.set_draw_color(201, 168, 76)
        pdf.set_line_width(0.4)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(6)
        pdf.set_text_color(240, 237, 232)

    # ─── WEATHER PAGE ─────────────────────────
    add_section_header("Live Weather", "🌤")

    if current_weather:
        cw = current_weather
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(232, 201, 122)
        pdf.cell(0, 8, "Current Conditions", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(240, 237, 232)
        weather_info = [
            f"Temperature: {cw['temp']}°C  (Feels like {cw['feels_like']}°C)",
            f"Condition: {cw['description'].title()}",
            f"Humidity: {cw['humidity']}%    Wind Speed: {cw['wind_speed']} m/s",
        ]
        for line in weather_info:
            pdf.cell(0, 7, clean_text(line), ln=True)
        pdf.ln(4)

    if weather_forecast:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(232, 201, 122)
        pdf.cell(0, 8, "5-Day Forecast", ln=True)
        pdf.ln(2)
        for fc in weather_forecast:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(201, 168, 76)
            pdf.cell(55, 7, clean_text(f"{fc['day_name']} {fc['date']}"), ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(240, 237, 232)
            pdf.cell(0, 7, clean_text(
                f"Avg: {fc['temp_avg']:.1f}°C  |  Max: {fc['temp_max']:.1f}°  Min: {fc['temp_min']:.1f}°  |  {fc['description'].title()}"
            ), ln=True)
        pdf.ln(3)

    # ─── DAY PLANS ────────────────────────────
    for day_idx, day_plan in enumerate(daily_plans, 1):
        day_date = start_date + timedelta(days=day_idx - 1)
        add_section_header(f"Day {day_idx} — {day_date.strftime('%A, %B %d')}", "📅")

        # Activities
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(232, 201, 122)
        pdf.cell(0, 8, "Activities", ln=True)
        pdf.ln(1)
        for act in day_plan.get('activities', []):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(201, 168, 76)
            pdf.cell(28, 7, clean_text(act['time']), ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(240, 237, 232)
            pdf.cell(0, 7, clean_text(act['activity']), ln=True)
            if act.get('duration'):
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(139, 139, 154)
                pdf.cell(28, 5, "", ln=False)
                pdf.cell(0, 5, clean_text(f"Duration: {act['duration']}"), ln=True)
        pdf.ln(4)

        # Meals
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(232, 201, 122)
        pdf.cell(0, 8, "Dining", ln=True)
        pdf.ln(1)
        for meal in day_plan.get('meals', []):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(201, 168, 76)
            pdf.cell(50, 7, clean_text(f"{meal['type']} ({meal['time']})"), ln=False)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(240, 237, 232)
            pdf.cell(0, 7, clean_text(meal['restaurant']), ln=True)

    # ─── HOTELS PAGE ──────────────────────────
    add_section_header("Recommended Hotels", "🏨")
    for i, hotel in enumerate(hotels[:5], 1):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(232, 201, 122)
        pdf.cell(0, 8, clean_text(f"{i}. {hotel['name']}"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(240, 237, 232)
        pdf.cell(0, 6, clean_text(f"Address: {hotel['address']}"), ln=True)
        stars_count = int(hotel['rating'])
        pdf.cell(0, 6, clean_text(f"Rating: {'★' * stars_count} {hotel['rating']} ({hotel['total_ratings']} reviews)"), ln=True)
        pdf.cell(0, 6, clean_text(f"Price: {hotel['estimated_price']} per night"), ln=True)
        if hotel.get('phone') and hotel['phone'] != 'N/A':
            pdf.cell(0, 6, clean_text(f"Phone: {hotel['phone']}"), ln=True)
        if hotel.get('website') and hotel['website'] != 'N/A':
            pdf.cell(0, 6, clean_text(f"Website: {hotel['website']}"), ln=True)
        pdf.ln(4)

    # ─── RESTAURANTS PAGE ─────────────────────
    add_section_header("Top Restaurants", "🍽")
    for i, rest in enumerate(restaurants[:10], 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(232, 201, 122)
        pdf.cell(0, 7, clean_text(f"{i}. {rest['name']}"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(240, 237, 232)
        pdf.cell(0, 5, clean_text(f"{rest['address']}  |  ⭐ {rest['rating']}  |  {rest['estimated_cost']}"), ln=True)
        pdf.ln(2)

    # ─── ATTRACTIONS PAGE ─────────────────────
    add_section_header("Must-Visit Attractions", "🎭")
    for i, attr in enumerate(attractions[:10], 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(232, 201, 122)
        pdf.cell(0, 7, clean_text(f"{i}. {attr['name']}"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(240, 237, 232)
        pdf.cell(0, 5, clean_text(f"{attr['address']}  |  Rating: {attr['rating']}"), ln=True)
        pdf.ln(2)

    # ─── BACK COVER ───────────────────────────
    pdf.add_page()
    pdf.set_fill_color(13, 15, 20)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_fill_color(201, 168, 76)
    pdf.rect(0, 289, 210, 8, 'F')
    pdf.ln(110)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(201, 168, 76)
    pdf.cell(0, 12, "Bon Voyage!", ln=True, align='C')
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(139, 139, 154)
    pdf.cell(0, 8, clean_text(f"Your {num_days}-day adventure awaits in {destination}."), ln=True, align='C')
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Generated by AI Travel Planner | Powered by Google Places & OpenAI", ln=True, align='C')

    return bytes(pdf.output())

# ─────────────────────────────────────────────
# TASK 3: PAYMENT VALIDATION
# ─────────────────────────────────────────────
def validate_card_number(number):
    number = re.sub(r'\D', '', number)
    if len(number) < 13 or len(number) > 19:
        return False
    # Luhn Algorithm
    total = 0
    reverse_digits = number[::-1]
    for i, d in enumerate(reverse_digits):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def get_card_type(number):
    number = re.sub(r'\D', '', number)
    if number.startswith('4'):
        return "💳 Visa"
    elif number[:2] in ['51','52','53','54','55'] or (2221 <= int(number[:4] or 0) <= 2720):
        return "💳 Mastercard"
    elif number[:2] in ['34','37']:
        return "💳 Amex"
    elif number[:4] in ['6011'] or number[:2] == '65':
        return "💳 Discover"
    return "💳 Card"

def validate_expiry(expiry):
    expiry = expiry.strip()
    if not re.match(r'^\d{2}/\d{2}$', expiry):
        return False
    month, year = expiry.split('/')
    month, year = int(month), int(year) + 2000
    now = datetime.now()
    if month < 1 or month > 12:
        return False
    return datetime(year, month, 1) >= datetime(now.year, now.month, 1)

def validate_cvv(cvv, card_type=""):
    cvv = re.sub(r'\D', '', cvv)
    if "Amex" in card_type:
        return len(cvv) == 4
    return len(cvv) == 3

def calculate_total(hotels, num_days, num_travelers, budget):
    """Estimate total trip cost."""
    if not hotels:
        price_map = {
            "Budget ($50-100/day)": 75,
            "Moderate ($100-300/day)": 200,
            "Luxury ($300-500/day)": 400,
            "Ultra Luxury ($500+/day)": 700,
        }
        daily = price_map.get(budget, 200)
    else:
        try:
            price_str = hotels[0]['estimated_price']
            price_clean = re.sub(r'[^\d.]', '', price_str.split('-')[0])
            daily = float(price_clean) if price_clean else 200
        except:
            daily = 200
    hotel_total = daily * num_days
    food_total = 60 * num_days * num_travelers
    activities_total = 40 * num_days * num_travelers
    return hotel_total, food_total, activities_total, hotel_total + food_total + activities_total

# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">✈️ AI Travel Planner</div>
    <div class="hero-subtitle">Real-time intelligence for extraordinary journeys</div>
    <div class="hero-badges">
        <span class="badge">🌍 Google Places API</span>
        <span class="badge">🤖 OpenAI GPT</span>
        <span class="badge">🌤️ Live Weather</span>
        <span class="badge">📄 PDF Export</span>
        <span class="badge">💳 Secure Payments</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-header">📝 Trip Configuration</div>', unsafe_allow_html=True)

    if st.button("🔄 Reset App"):
        st.cache_resource.clear()
        st.session_state.clear()
        st.rerun()

    destination = st.text_input("🌍 Destination City", placeholder="e.g., Paris, Tokyo, Mumbai")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Start", datetime.now())
    with col2:
        end_date = st.date_input("📅 End", datetime.now() + timedelta(days=3))

    num_days = (end_date - start_date).days

    budget = st.select_slider(
        "💰 Budget (per person/day)",
        options=["Budget ($50-100/day)", "Moderate ($100-300/day)",
                 "Luxury ($300-500/day)", "Ultra Luxury ($500+/day)"],
        value="Moderate ($100-300/day)"
    )

    num_travelers = st.number_input("👥 Travelers", min_value=1, max_value=10, value=2)

    interests = st.multiselect(
        "🎯 Interests",
        ["Culture & History", "Food & Dining", "Adventure", "Nature",
         "Shopping", "Nightlife", "Relaxation"],
        default=["Culture & History", "Food & Dining"]
    )

    st.markdown("---")
    generate_button = st.button("🚀 Generate Real-Time Itinerary", use_container_width=True)

# ─────────────────────────────────────────────
# TASK 1: GENERATE REAL DATA
# ─────────────────────────────────────────────
if generate_button:
    if not destination or num_days <= 0:
        st.error("⚠️ Please enter a valid destination and travel dates.")
    else:
        progress_bar = st.progress(0)
        status = st.empty()

        with st.spinner(f"🔍 Locating {destination} on the map..."):
            location_details = services['geocoding'].get_place_details(destination)
            progress_bar.progress(10)

        if not location_details:
            st.error("❌ Could not locate destination. Please try another city name.")
            st.stop()

        lat = location_details['lat']
        lon = location_details['lon']
        st.success(f"📍 Located: **{location_details['name']}**")
        progress_bar.progress(20)

        status.info("🏨 Fetching real hotel listings from Google Places...")
        hotels = services['places'].search_hotels(destination, lat, lon, budget, radius=5000)
        progress_bar.progress(35)

        status.info("🍽️ Discovering top-rated restaurants nearby...")
        restaurants = services['places'].search_restaurants(lat, lon, radius=3000)
        progress_bar.progress(50)

        status.info("🎭 Searching attractions and experiences...")
        all_attractions = []
        for interest in interests[:2]:
            attrs = services['places'].search_attractions(lat, lon, interest, radius=5000)
            all_attractions.extend(attrs)
        seen = set()
        unique_attractions = []
        for attr in all_attractions:
            if attr['place_id'] not in seen:
                seen.add(attr['place_id'])
                unique_attractions.append(attr)
        progress_bar.progress(65)

        status.info("🌤️ Pulling live weather forecast...")
        weather_forecast = services['weather'].get_forecast(lat, lon, num_days)
        current_weather = services['weather'].get_current_weather(lat, lon)
        progress_bar.progress(78)

        status.info("🤖 AI crafting your personalized day-by-day plan...")
        daily_plans = []
        for day in range(1, num_days + 1):
            plan = services['ai'].generate_daily_plan(
                day, destination, interests,
                hotels, restaurants, unique_attractions
            )
            daily_plans.append(plan)
        progress_bar.progress(95)

        st.session_state.update({
            'location_details': location_details,
            'hotels': hotels,
            'restaurants': restaurants,
            'attractions': unique_attractions,
            'weather_forecast': weather_forecast,
            'current_weather': current_weather,
            'daily_plans': daily_plans,
            'start_date': start_date,
            'num_days': num_days,
            'destination': destination,
            'num_travelers': num_travelers,
            'budget': budget,
        })

        progress_bar.progress(100)
        status.empty()
        st.success("✅ Real-time itinerary ready! Explore the tabs below.")

# ─────────────────────────────────────────────
# DISPLAY RESULTS
# ─────────────────────────────────────────────
if 'hotels' in st.session_state:

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📅 Itinerary",
        "🏨 Hotels",
        "🍽️ Restaurants",
        "🎭 Attractions",
        "🌤️ Weather",
        "🗺️ Map",
        "📄 PDF Report",     # TASK 2
        "💳 Book & Pay",     # TASK 3
    ])

    # ──────────────────────────────────────────
    # TAB 1 — ITINERARY (Real AI Plans)
    # ──────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">📅 Day-by-Day Itinerary</div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        for day_idx, day_plan in enumerate(st.session_state['daily_plans'], 1):
            day_date = st.session_state['start_date'] + timedelta(days=day_idx - 1)

            with st.expander(f"✈️  Day {day_idx} — {day_date.strftime('%A, %B %d, %Y')}", expanded=(day_idx == 1)):
                col_act, col_meal = st.columns([3, 2])

                with col_act:
                    st.markdown("**🎯 Activities**")
                    for activity in day_plan.get('activities', []):
                        attr_details = next(
                            (a for a in st.session_state['attractions']
                             if a['name'].lower() in activity['activity'].lower()),
                            None
                        )
                        st.markdown(f"""
                        <div class="timeline-item">
                            <div>
                                <div class="timeline-time">{activity['time']}</div>
                                <div class="timeline-content">{activity['activity']}</div>
                                {"<div class='timeline-meta'>📍 " + attr_details['address'] + "  ⭐ " + str(attr_details['rating']) + "</div>" if attr_details else ""}
                                <div class="timeline-meta">⏱️ {activity.get('duration', 'N/A')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                with col_meal:
                    st.markdown("**🍽️ Dining Plan**")
                    for meal in day_plan.get('meals', []):
                        rest_details = next(
                            (r for r in st.session_state['restaurants']
                             if r['name'].lower() in meal['restaurant'].lower()),
                            None
                        )
                        with st.container():
                            st.markdown(f"""
                            <div class="trip-card" style="padding:0.8rem;">
                                <div style="color:var(--gold);font-weight:700;font-size:0.85rem;">{meal['type']} · {meal['time']}</div>
                                <div style="color:var(--text-primary);margin-top:0.2rem;">{meal['restaurant']}</div>
                                {"<div style='color:var(--text-muted);font-size:0.8rem;margin-top:0.2rem;'>⭐ " + str(rest_details['rating']) + " · " + rest_details['estimated_cost'] + "</div>" if rest_details else ""}
                            </div>
                            """, unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # TAB 2 — HOTELS (Real Google Data)
    # ──────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">🏨 Real Hotels — Google Places</div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        if st.session_state['hotels']:
            for hotel in st.session_state['hotels'][:5]:
                col1, col2, col3 = st.columns([3, 2, 2])

                with col1:
                    st.markdown(f'<div class="hotel-name">{hotel["name"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="hotel-address">📍 {hotel["address"]}</div>', unsafe_allow_html=True)
                    stars = "⭐" * int(hotel['rating'])
                    st.markdown(f'<span class="stat-pill">{stars} {hotel["rating"]}</span>'
                                f'<span class="stat-pill">👥 {hotel["total_ratings"]} reviews</span>',
                                unsafe_allow_html=True)

                with col2:
                    st.markdown(f'<div class="price-tag">{hotel["estimated_price"]}</div><div style="color:var(--text-muted);font-size:0.8rem;">per night</div>', unsafe_allow_html=True)
                    price_symbols = "$" * (hotel['price_level'] + 1)
                    st.caption(f"Level: {price_symbols}")

                with col3:
                    if hotel['phone'] != 'N/A':
                        st.caption(f"📞 {hotel['phone']}")
                    if hotel['website'] != 'N/A':
                        st.markdown(f"[🌐 Visit Website]({hotel['website']})")

                if hotel['photo_reference']:
                    photo_url = services['places'].get_photo_url(hotel['photo_reference'])
                    st.image(photo_url, width=320, use_column_width=False)

                st.markdown('<hr style="border-color:var(--border);margin:1rem 0;">', unsafe_allow_html=True)
        else:
            st.info("No hotels found. Try a different destination or budget.")

    # ──────────────────────────────────────────
    # TAB 3 — RESTAURANTS (Real Data)
    # ──────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">🍽️ Top-Rated Restaurants</div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        cols = st.columns(2)
        for idx, restaurant in enumerate(st.session_state['restaurants'][:10]):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="trip-card">
                    <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:var(--gold-light);margin-bottom:0.3rem;">{restaurant['name']}</div>
                    <div style="color:var(--text-muted);font-size:0.82rem;margin-bottom:0.6rem;">📍 {restaurant['address']}</div>
                    <span class="stat-pill">⭐ {restaurant['rating']}</span>
                    <span class="stat-pill">💰 {restaurant['estimated_cost']}</span>
                    <div style="color:var(--text-muted);font-size:0.78rem;margin-top:0.5rem;">
                        {", ".join([t.replace('_',' ').title() for t in restaurant['types'][:3]])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # TAB 4 — ATTRACTIONS (Real Data)
    # ──────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">🎭 Must-Visit Attractions</div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        cols = st.columns(2)
        for idx, attraction in enumerate(st.session_state['attractions'][:10]):
            with cols[idx % 2]:
                distance_info = services['places'].calculate_distance(
                    st.session_state['location_details']['lat'],
                    st.session_state['location_details']['lon'],
                    attraction['lat'],
                    attraction['lon']
                )
                st.markdown(f"""
                <div class="trip-card">
                    <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:var(--gold-light);margin-bottom:0.3rem;">{attraction['name']}</div>
                    <div style="color:var(--text-muted);font-size:0.82rem;margin-bottom:0.6rem;">📍 {attraction['address']}</div>
                    <span class="stat-pill">⭐ {attraction['rating']}</span>
                    <span class="stat-pill">🚶 {distance_info['distance']}</span>
                    <span class="stat-pill">⏱️ {distance_info['duration']}</span>
                </div>
                """, unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # TAB 5 — WEATHER (Live)
    # ──────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">🌤️ Live Weather Forecast</div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        if st.session_state['current_weather']:
            curr = st.session_state['current_weather']
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("🌡️ Temperature", f"{curr['temp']}°C")
            with c2: st.metric("🤔 Feels Like", f"{curr['feels_like']}°C")
            with c3: st.metric("💧 Humidity", f"{curr['humidity']}%")
            with c4: st.metric("💨 Wind", f"{curr['wind_speed']} m/s")
            st.info(f"☁️ Current: {curr['description'].title()}")

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        if st.session_state['weather_forecast']:
            st.markdown("**📅 5-Day Forecast**")
            cols = st.columns(len(st.session_state['weather_forecast']))
            for idx, forecast in enumerate(st.session_state['weather_forecast']):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="weather-card">
                        <div class="weather-label">{forecast['day_name']}</div>
                        <div style="color:var(--text-muted);font-size:0.75rem;">{forecast['date']}</div>
                        <div class="weather-temp">{forecast['temp_avg']:.0f}°</div>
                        <div style="color:var(--text-muted);font-size:0.78rem;">{forecast['description'].title()}</div>
                        <div style="color:var(--accent-blue);font-size:0.75rem;margin-top:0.3rem;">
                            ↑{forecast['temp_max']:.0f}° ↓{forecast['temp_min']:.0f}°
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # TAB 6 — MAP
    # ──────────────────────────────────────────
    with tab6:
        st.markdown('<div class="section-title">🗺️ Interactive Map</div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        col_legend, col_note = st.columns([2, 3])
        with col_legend:
            st.markdown("""
            <div class="trip-card" style="padding:0.8rem;">
                <div style="color:var(--gold);font-weight:700;margin-bottom:0.5rem;">Map Legend</div>
                <div style="font-size:0.85rem;color:var(--text-muted);">🔴 Hotels &nbsp; 🔵 Attractions &nbsp; 🟢 Restaurants</div>
            </div>
            """, unsafe_allow_html=True)

        m = folium.Map(
            location=[st.session_state['location_details']['lat'],
                      st.session_state['location_details']['lon']],
            zoom_start=13,
            tiles='CartoDB dark_matter'
        )

        for hotel in st.session_state['hotels'][:5]:
            folium.Marker(
                [hotel['lat'], hotel['lon']],
                popup=folium.Popup(f"<b>{hotel['name']}</b><br>⭐{hotel['rating']}<br>{hotel['estimated_price']}/night", max_width=200),
                tooltip=hotel['name'],
                icon=folium.Icon(color='red', icon='home', prefix='fa')
            ).add_to(m)

        for attr in st.session_state['attractions'][:10]:
            folium.Marker(
                [attr['lat'], attr['lon']],
                popup=folium.Popup(f"<b>{attr['name']}</b><br>⭐{attr['rating']}", max_width=200),
                tooltip=attr['name'],
                icon=folium.Icon(color='blue', icon='star', prefix='fa')
            ).add_to(m)

        for rest in st.session_state['restaurants'][:10]:
            folium.Marker(
                [rest['lat'], rest['lon']],
                popup=folium.Popup(f"<b>{rest['name']}</b><br>⭐{rest['rating']}", max_width=200),
                tooltip=rest['name'],
                icon=folium.Icon(color='green', icon='cutlery', prefix='fa')
            ).add_to(m)

        st_folium(m, width="100%", height=580)

    # ──────────────────────────────────────────
    # TAB 7 — PDF REPORT (TASK 2)
    # ──────────────────────────────────────────
    with tab7:
        st.markdown('<div class="section-title">📄 Download Trip Report</div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        st.markdown("""
        <div class="trip-card" style="text-align:center;padding:2rem;">
            <div style="font-size:3rem;margin-bottom:1rem;">📋</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.4rem;color:var(--gold);margin-bottom:0.5rem;">
                Professional Trip Report
            </div>
            <div style="color:var(--text-muted);font-size:0.9rem;margin-bottom:1.5rem;">
                Your complete itinerary with hotels, restaurants, attractions, and weather forecast — beautifully formatted as a PDF.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_info, col_btn = st.columns([2, 1])
        with col_info:
            ss = st.session_state
            dest_name = ss.get('destination', 'Your Destination')
            report_includes = [
                f"✅ Cover page for {dest_name}",
                f"✅ {ss['num_days']}-day detailed itinerary",
                f"✅ {len(ss['hotels'])} recommended hotels with prices",
                f"✅ {len(ss['restaurants'])} top restaurants",
                f"✅ {len(ss['attractions'])} must-visit attractions",
                f"✅ Live weather forecast",
            ]
            for item in report_includes:
                st.markdown(f'<div style="color:var(--text-primary);margin-bottom:0.3rem;font-size:0.9rem;">{item}</div>', unsafe_allow_html=True)

        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📥 Generate PDF Report", use_container_width=True):
                with st.spinner("🖨️ Crafting your premium PDF report..."):
                    try:
                        pdf_bytes = generate_trip_pdf(
                            destination=ss.get('destination', 'Destination'),
                            start_date=ss['start_date'],
                            num_days=ss['num_days'],
                            num_travelers=ss.get('num_travelers', 2),
                            budget=ss.get('budget', 'Moderate'),
                            daily_plans=ss['daily_plans'],
                            hotels=ss['hotels'],
                            restaurants=ss['restaurants'],
                            attractions=ss['attractions'],
                            current_weather=ss.get('current_weather'),
                            weather_forecast=ss.get('weather_forecast', [])
                        )
                        dest_safe = re.sub(r'[^a-zA-Z0-9]', '_', ss.get('destination', 'Trip'))
                        filename = f"TripReport_{dest_safe}_{ss['start_date'].strftime('%Y%m%d')}.pdf"
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("✅ PDF ready! Click Download PDF above.")
                    except Exception as e:
                        st.error(f"PDF generation error: {str(e)}")

    # ──────────────────────────────────────────
    # TAB 8 — PAYMENT (TASK 3)
    # ──────────────────────────────────────────
    with tab8:
        st.markdown('<div class="section-title">💳 Book & Pay Securely</div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        ss = st.session_state
        hotel_cost, food_cost, activities_cost, total_cost = calculate_total(
            ss['hotels'], ss['num_days'], ss.get('num_travelers', 2), ss.get('budget', 'Moderate')
        )

        left_col, right_col = st.columns([3, 2])

        # ── LEFT: PAYMENT FORM ─────────────────
        with left_col:
            st.markdown('<div class="payment-title">💳 Secure Payment</div>', unsafe_allow_html=True)
            st.markdown('<div class="payment-subtitle">All transactions encrypted with 256-bit SSL</div>', unsafe_allow_html=True)

            # Payment Method Selection
            st.markdown("**Select Payment Method**")
            pm_col1, pm_col2, pm_col3 = st.columns(3)
            with pm_col1:
                pm_credit = st.button("💳 Credit / Debit Card", use_container_width=True)
            with pm_col2:
                pm_upi = st.button("📱 UPI / QR Code", use_container_width=True)
            with pm_col3:
                pm_wallet = st.button("👝 Net Banking", use_container_width=True)

            # Persist method
            if pm_credit:
                ss['payment_method'] = 'card'
            elif pm_upi:
                ss['payment_method'] = 'upi'
            elif pm_wallet:
                ss['payment_method'] = 'netbanking'
            if 'payment_method' not in ss:
                ss['payment_method'] = 'card'

            st.markdown(f"**Selected:** `{ss['payment_method'].upper()}`")
            st.markdown("---")

            # ── CARD FORM ───────────────────────
            if ss['payment_method'] == 'card':
                st.markdown("**Cardholder Name**")
                cardholder = st.text_input("Full Name on Card", placeholder="John Doe", key="cardholder", label_visibility="collapsed")

                st.markdown("**Card Number**")
                card_number_input = st.text_input("Card Number", placeholder="4111 1111 1111 1111", max_chars=19, key="card_num", label_visibility="collapsed")

                # Detect card type live
                if card_number_input:
                    detected = get_card_type(card_number_input)
                    st.markdown(f'<span class="stat-pill">{detected} detected</span>', unsafe_allow_html=True)

                exp_col, cvv_col = st.columns(2)
                with exp_col:
                    st.markdown("**Expiry (MM/YY)**")
                    expiry = st.text_input("Expiry", placeholder="08/27", max_chars=5, key="expiry", label_visibility="collapsed")
                with cvv_col:
                    st.markdown("**CVV**")
                    cvv = st.text_input("CVV", placeholder="•••", max_chars=4, type="password", key="cvv", label_visibility="collapsed")

                st.markdown("**Billing Email**")
                email = st.text_input("Email", placeholder="you@email.com", key="billing_email", label_visibility="collapsed")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"🔒 Pay ${total_cost:,.0f} Securely", use_container_width=True):
                    errors = []
                    if not cardholder or len(cardholder.strip()) < 3:
                        errors.append("Enter cardholder full name.")
                    if not validate_card_number(card_number_input):
                        errors.append("Invalid card number (Luhn check failed).")
                    if not validate_expiry(expiry):
                        errors.append("Invalid or expired expiry date (MM/YY).")
                    card_type_detected = get_card_type(card_number_input)
                    if not validate_cvv(cvv, card_type_detected):
                        errors.append("Invalid CVV (3 digits; 4 for Amex).")
                    if not email or "@" not in email:
                        errors.append("Enter a valid email address.")

                    if errors:
                        for err in errors:
                            st.markdown(f'<div class="error-box">❌ {err}</div>', unsafe_allow_html=True)
                    else:
                        dest_name = ss.get('destination', 'your destination')
                        st.markdown(f"""
                        <div class="success-box">
                            <div style="font-size:2rem;margin-bottom:0.75rem;">✅</div>
                            <div style="font-size:1.2rem;font-weight:700;margin-bottom:0.4rem;">Payment Confirmed!</div>
                            <div style="font-size:0.9rem;opacity:0.85;">
                                ${total_cost:,.0f} charged to {card_type_detected} ending in {re.sub(r'\D','',card_number_input)[-4:]}<br>
                                Confirmation sent to <b>{email}</b><br><br>
                                🎉 Your trip to <b>{dest_name}</b> is officially booked!
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # ── UPI FORM ─────────────────────────
            elif ss['payment_method'] == 'upi':
                st.markdown("**UPI ID**")
                upi_id = st.text_input("UPI ID", placeholder="yourname@upi", key="upi_id", label_visibility="collapsed")

                st.markdown("**Full Name**")
                upi_name = st.text_input("Full Name", placeholder="John Doe", key="upi_name", label_visibility="collapsed")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"📱 Pay ₹{total_cost * 84:,.0f} via UPI", use_container_width=True):
                    upi_errors = []
                    if not upi_id or "@" not in upi_id:
                        upi_errors.append("Enter a valid UPI ID (e.g., name@upi).")
                    if not upi_name or len(upi_name.strip()) < 3:
                        upi_errors.append("Enter your full name.")
                    if upi_errors:
                        for err in upi_errors:
                            st.markdown(f'<div class="error-box">❌ {err}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="success-box">
                            <div style="font-size:2rem;margin-bottom:0.75rem;">✅</div>
                            <div style="font-size:1.2rem;font-weight:700;">UPI Payment Confirmed!</div>
                            <div style="font-size:0.9rem;opacity:0.85;margin-top:0.4rem;">
                                ₹{total_cost * 84:,.0f} debited from <b>{upi_id}</b><br>
                                🎉 Trip to <b>{ss.get('destination','destination')}</b> is booked!
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # ── NET BANKING FORM ──────────────────
            elif ss['payment_method'] == 'netbanking':
                st.markdown("**Select Bank**")
                bank = st.selectbox("Bank", [
                    "State Bank of India", "HDFC Bank", "ICICI Bank",
                    "Axis Bank", "Kotak Mahindra Bank", "Punjab National Bank",
                    "Bank of Baroda", "Yes Bank", "Canara Bank", "Union Bank"
                ], label_visibility="collapsed")

                st.markdown("**Account Holder Name**")
                nb_name = st.text_input("Name", placeholder="Full Name", key="nb_name", label_visibility="collapsed")

                st.markdown("**Account Number**")
                nb_acc = st.text_input("Account Number", placeholder="XXXXXXXXXX", key="nb_acc", label_visibility="collapsed")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"🏦 Pay ₹{total_cost * 84:,.0f} via {bank}", use_container_width=True):
                    nb_errors = []
                    if not nb_name or len(nb_name.strip()) < 3:
                        nb_errors.append("Enter account holder name.")
                    if not nb_acc or len(re.sub(r'\D', '', nb_acc)) < 9:
                        nb_errors.append("Enter a valid account number.")
                    if nb_errors:
                        for err in nb_errors:
                            st.markdown(f'<div class="error-box">❌ {err}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="success-box">
                            <div style="font-size:2rem;margin-bottom:0.75rem;">✅</div>
                            <div style="font-size:1.2rem;font-weight:700;">Net Banking Payment Confirmed!</div>
                            <div style="font-size:0.9rem;opacity:0.85;margin-top:0.4rem;">
                                ₹{total_cost * 84:,.0f} debited from <b>{bank}</b><br>
                                🎉 Trip to <b>{ss.get('destination','destination')}</b> is booked!
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # ── RIGHT: BOOKING SUMMARY ─────────────
        with right_col:
            st.markdown("**📋 Booking Summary**")
            dest_name = ss.get('destination', 'Destination')
            nights = ss['num_days']
            travelers = ss.get('num_travelers', 2)

            hotel_name = ss['hotels'][0]['name'] if ss['hotels'] else "Selected Hotel"
            hotel_price = ss['hotels'][0]['estimated_price'] if ss['hotels'] else "$200"

            st.markdown(f"""
            <div class="trip-card" style="padding:1.5rem;">
                <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:var(--gold-light);margin-bottom:1rem;">
                    ✈️ {dest_name} Trip
                </div>
                <div class="payment-summary-row">
                    <span>🏨 Hotel ({nights} nights)</span>
                    <span>${hotel_cost:,.0f}</span>
                </div>
                <div class="payment-summary-row">
                    <span>🍽️ Food & Dining</span>
                    <span>${food_cost:,.0f}</span>
                </div>
                <div class="payment-summary-row">
                    <span>🎭 Activities</span>
                    <span>${activities_cost:,.0f}</span>
                </div>
                <div class="payment-summary-row">
                    <span>✈️ Service Fee (5%)</span>
                    <span>${total_cost * 0.05:,.0f}</span>
                </div>
                <div class="payment-total-row">
                    <span>Total</span>
                    <span>${total_cost * 1.05:,.0f}</span>
                </div>
                <div style="margin-top:1rem;padding:0.75rem;background:rgba(201,168,76,0.08);border-radius:10px;border:1px solid var(--border);">
                    <div style="color:var(--text-muted);font-size:0.78rem;">👥 {travelers} traveler(s) · {nights} nights</div>
                    <div style="color:var(--text-muted);font-size:0.78rem;margin-top:0.2rem;">📅 {ss['start_date'].strftime('%b %d')} – {(ss['start_date'] + timedelta(days=nights)).strftime('%b %d, %Y')}</div>
                    <div style="color:var(--text-muted);font-size:0.78rem;margin-top:0.2rem;">🏨 {hotel_name}</div>
                </div>
                <div style="margin-top:1rem;text-align:center;">
                    <span style="color:var(--accent-green);font-size:0.8rem;">🔒 Secured by 256-bit SSL Encryption</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Refund policy
            st.markdown("""
            <div style="margin-top:1rem;padding:0.75rem;background:var(--bg-surface);border-radius:10px;border:1px solid var(--border);">
                <div style="color:var(--gold);font-size:0.82rem;font-weight:700;margin-bottom:0.4rem;">📌 Cancellation Policy</div>
                <div style="color:var(--text-muted);font-size:0.78rem;line-height:1.5;">
                    • Free cancellation within 24 hours<br>
                    • 50% refund up to 7 days before travel<br>
                    • No refund within 48 hours of travel date
                </div>
            </div>
            """, unsafe_allow_html=True)