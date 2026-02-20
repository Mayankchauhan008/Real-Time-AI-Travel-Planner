import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from fpdf import FPDF

# Import our services
from services.geocoding_service import GeocodingService
from services.places_service import PlacesService
from services.weather_service import WeatherService
from services.ai_service import AIService

# Load environment variables
load_dotenv()

# Initialize services
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

# Clear cache button for development/testing
if st.sidebar.button("🔄 Reset App State"):
    st.cache_resource.clear()
    st.session_state.clear()
    st.rerun()

# Page config
st.set_page_config(
    page_title="Real-Time AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .hotel-card {
        padding: 1rem;
        border-radius: 10px;
        background: #f0f2f6;
        margin: 0.5rem 0;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-size: 1.1rem;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">✈️ Real-Time AI Travel Planner</h1>', unsafe_allow_html=True)
st.markdown("### Powered by Real APIs: Google Places, OpenAI, Live Weather")

# Sidebar
with st.sidebar:
    st.header("📝 Trip Details")
    
    destination = st.text_input("🌍 Destination City", placeholder="e.g., Paris, Tokyo, Mumbai")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Start Date", datetime.now())
    with col2:
        end_date = st.date_input("📅 End Date", datetime.now() + timedelta(days=3))
    
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
    
    generate_button = st.button("🚀 Generate Real-Time Itinerary", use_container_width=True)

# Main logic
if generate_button:
    if not destination or num_days <= 0:
        st.error("Please enter valid destination and dates!")
    else:
        with st.spinner(f"🔍 Finding real places in {destination}..."):
            
            # Step 1: Get coordinates
            location_details = services['geocoding'].get_place_details(destination)
            
            if not location_details:
                st.error("Could not find location. Please try another destination.")
                st.stop()
            
            lat = location_details['lat']
            lon = location_details['lon']
            
            st.success(f"📍 Found: {location_details['name']}")
            
            # Step 2: Search real hotels
            with st.spinner("🏨 Searching real hotels..."):
                hotels = services['places'].search_hotels(
                    destination, lat, lon, budget, radius=5000
                )
            
            # Step 3: Search real restaurants
            with st.spinner("🍽️ Finding real restaurants..."):
                restaurants = services['places'].search_restaurants(lat, lon, radius=3000)
            
            # Step 4: Search real attractions
            with st.spinner("🎭 Discovering real attractions..."):
                all_attractions = []
                for interest in interests[:2]:  # Limit to avoid API quota
                    attrs = services['places'].search_attractions(lat, lon, interest, radius=5000)
                    all_attractions.extend(attrs)
                
                # Remove duplicates
                seen = set()
                unique_attractions = []
                for attr in all_attractions:
                    if attr['place_id'] not in seen:
                        seen.add(attr['place_id'])
                        unique_attractions.append(attr)
            
            # Step 5: Get weather
            with st.spinner("🌤️ Getting live weather forecast..."):
                weather_forecast = services['weather'].get_forecast(lat, lon, num_days)
                current_weather = services['weather'].get_current_weather(lat, lon)
            
            # Step 6: Generate AI itinerary with real places
            with st.spinner("🤖 AI creating personalized itinerary..."):
                daily_plans = []
                for day in range(1, num_days + 1):
                    plan = services['ai'].generate_daily_plan(
                        day, destination, interests, 
                        hotels, restaurants, unique_attractions
                    )
                    daily_plans.append(plan)
            
            # Store in session state
            st.session_state.update({
                'location_details': location_details,
                'hotels': hotels,
                'restaurants': restaurants,
                'attractions': unique_attractions,
                'weather_forecast': weather_forecast,
                'current_weather': current_weather,
                'daily_plans': daily_plans,
                'start_date': start_date,
                'num_days': num_days
            })
            
            st.success("✅ Real-time itinerary generated!")

# Display Results
if 'hotels' in st.session_state:
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📅 Itinerary", "🏨 Hotels", "🍽️ Restaurants", "🎭 Attractions", "🌤️ Weather", "🗺️ Map"]
    )
    
    # TAB 1: ITINERARY
    with tab1:
        st.header("Day-by-Day Itinerary")
        
        for day_idx, day_plan in enumerate(st.session_state['daily_plans'], 1):
            day_date = st.session_state['start_date'] + timedelta(days=day_idx-1)
            
            with st.expander(f"**Day {day_idx} - {day_date.strftime('%A, %B %d')}**", expanded=True):
                
                # Activities
                st.subheader("🎯 Activities")
                for activity in day_plan.get('activities', []):
                    # Find matching attraction for details
                    attr_details = next(
                        (a for a in st.session_state['attractions'] 
                         if a['name'].lower() in activity['activity'].lower()), 
                        None
                    )
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{activity['time']}** - {activity['activity']}")
                        if attr_details:
                            st.caption(f"📍 {attr_details['address']} | ⭐ {attr_details['rating']}")
                    with col2:
                        st.info(f"⏱️ {activity.get('duration', 'N/A')}")
                
                st.divider()
                
                # Meals
                st.subheader("🍽️ Dining")
                for meal in day_plan.get('meals', []):
                    # Find matching restaurant
                    rest_details = next(
                        (r for r in st.session_state['restaurants'] 
                         if r['name'].lower() in meal['restaurant'].lower()), 
                        None
                    )
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**{meal['type']}** ({meal['time']})")
                    with col2:
                        st.markdown(f"📍 {meal['restaurant']}")
                        if rest_details:
                            st.caption(f"⭐ {rest_details['rating']} | {rest_details['estimated_cost']}")
                    with col3:
                        if rest_details:
                            st.metric("Cost", rest_details['estimated_cost'])
    
    # TAB 2: HOTELS
    with tab2:
        st.header("🏨 Recommended Hotels (Real Data)")
        
        if st.session_state['hotels']:
            for hotel in st.session_state['hotels'][:5]:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.subheader(hotel['name'])
                        st.caption(f"📍 {hotel['address']}")
                        
                        # Rating display
                        stars = "⭐" * int(hotel['rating'])
                        st.markdown(f"{stars} {hotel['rating']} ({hotel['total_ratings']} reviews)")
                    
                    with col2:
                        st.metric("Price/Night", hotel['estimated_price'])
                        price_symbols = "$" * (hotel['price_level'] + 1)
                        st.caption(f"Price Level: {price_symbols}")
                    
                    with col3:
                        if hotel['phone'] != 'N/A':
                            st.caption(f"📞 {hotel['phone']}")
                        if hotel['website'] != 'N/A':
                            st.markdown(f"[🌐 Website]({hotel['website']})")
                    
                    # Show photo if available
                    if hotel['photo_reference']:
                        photo_url = services['places'].get_photo_url(hotel['photo_reference'])
                        st.image(photo_url, width=300)
                    
                    st.divider()
        else:
            st.info("No hotels found. Try different search criteria.")
    
    # TAB 3: RESTAURANTS
    with tab3:
        st.header("🍽️ Top-Rated Restaurants")
        
        cols = st.columns(2)
        for idx, restaurant in enumerate(st.session_state['restaurants'][:10]):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"### {restaurant['name']}")
                    st.caption(f"📍 {restaurant['address']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Rating", f"⭐ {restaurant['rating']}")
                    with col2:
                        st.metric("Avg Cost", restaurant['estimated_cost'])
                    
                    cuisine = ", ".join([t.replace('_', ' ').title() 
                                       for t in restaurant['types'][:3]])
                    st.caption(f"🍴 {cuisine}")
                    st.divider()
    
    # TAB 4: ATTRACTIONS
    with tab4:
        st.header("🎭 Must-Visit Attractions")
        
        cols = st.columns(2)
        for idx, attraction in enumerate(st.session_state['attractions'][:10]):
            with cols[idx % 2]:
                st.markdown(f"### {attraction['name']}")
                st.caption(f"📍 {attraction['address']}")
                st.metric("Rating", f"⭐ {attraction['rating']}")
                
                # Calculate distance from city center
                distance_info = services['places'].calculate_distance(
                    st.session_state['location_details']['lat'],
                    st.session_state['location_details']['lon'],
                    attraction['lat'],
                    attraction['lon']
                )
                st.caption(f"🚶 {distance_info['distance']} ({distance_info['duration']})")
                st.divider()
    
    # TAB 5: WEATHER
    with tab5:
        st.header("🌤️ Live Weather Forecast")
        
        # Current weather
        if st.session_state['current_weather']:
            curr = st.session_state['current_weather']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Temperature", f"{curr['temp']}°C")
            with col2:
                st.metric("Feels Like", f"{curr['feels_like']}°C")
            with col3:
                st.metric("Humidity", f"{curr['humidity']}%")
            with col4:
                st.metric("Wind", f"{curr['wind_speed']} m/s")
            
            st.info(f"☁️ {curr['description'].title()}")
        
        st.divider()
        
        # Forecast
        if st.session_state['weather_forecast']:
            st.subheader("5-Day Forecast")
            cols = st.columns(len(st.session_state['weather_forecast']))
            
            for idx, forecast in enumerate(st.session_state['weather_forecast']):
                with cols[idx]:
                    st.markdown(f"**{forecast['day_name']}**")
                    st.markdown(f"{forecast['date']}")
                    st.metric(
                        "Temp",
                        f"{forecast['temp_avg']:.1f}°C",
                        delta=f"{forecast['temp_max']:.1f}° / {forecast['temp_min']:.1f}°"
                    )
                    st.caption(forecast['description'].title())
    
    # TAB 6: MAP
    with tab6:
        st.header("🗺️ Interactive Map")
        
        # Create map centered on destination
        m = folium.Map(
            location=[st.session_state['location_details']['lat'], 
                     st.session_state['location_details']['lon']], 
            zoom_start=13
        )
        
        # Add hotels
        for hotel in st.session_state['hotels'][:5]:
            folium.Marker(
                [hotel['lat'], hotel['lon']],
                popup=f"<b>{hotel['name']}</b><br>⭐{hotel['rating']}<br>{hotel['estimated_price']}/night",
                tooltip=hotel['name'],
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
        
        # Add attractions
        for attr in st.session_state['attractions'][:10]:
            folium.Marker(
                [attr['lat'], attr['lon']],
                popup=f"<b>{attr['name']}</b><br>⭐{attr['rating']}",
                tooltip=attr['name'],
                icon=folium.Icon(color='blue', icon='star')
            ).add_to(m)
        
        # Add restaurants
        for rest in st.session_state['restaurants'][:10]:
            folium.Marker(
                [rest['lat'], rest['lon']],
                popup=f"<b>{rest['name']}</b><br>⭐{rest['rating']}",
                tooltip=rest['name'],
                icon=folium.Icon(color='green', icon='cutlery')
            ).add_to(m)
        
        st_folium(m, width=900, height=600)
