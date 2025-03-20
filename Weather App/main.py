import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

# Cache weather data to reduce API calls
@st.cache_data(show_spinner=False, ttl=3600)
def get_weather(city):
    """Fetch weather data with error handling and caching"""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            st.error(f"City '{city}' not found. Please check the spelling.")
        else:
            st.error(f"HTTP error occurred: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def get_local_time(data):
    """Get local time using coordinates from weather data"""
    try:
        area = data['nearest_area'][0]
        latitude = float(area['latitude'])
        longitude = float(area['longitude'])
        
        tf = TimezoneFinder()
        timezone = tf.timezone_at(lng=longitude, lat=latitude)
        
        if timezone:
            tz = pytz.timezone(timezone)
            city_time = datetime.now(tz)  # Dynamically fetch current time
            return city_time.strftime("%I:%M %p, %A %d %B %Y (%Z)")
        
        return None
    except Exception as e:
        st.error(f"Could not get local time: {str(e)}")
        return None

def get_weather_icon(weather_code):
    """Map weather code to appropriate emoji"""
    icon_map = {
        '113': '☀️',  # Sunny
        '116': '⛅',  # Partly Cloudy
        '119': '☁️',  # Cloudy
        '122': '☁️',  # Overcast
        '143': '🌫️',  # Mist
        '176': '🌦️',  # Patchy rain
        '179': '🌨️',  # Patchy snow
        '182': '🌨️',  # Patchy sleet
        '185': '🌧️',  # Freezing drizzle
        '200': '⛈️',  # Thunder
        '227': '🌨️',  # Blowing snow
        '230': '❄️',  # Blizzard
        '248': '🌫️',  # Fog
        '260': '🌫️',  # Freezing fog
        '263': '🌦️',  # Light drizzle
        '266': '🌦️',  # Drizzle
        '281': '🌧️',  # Freezing drizzle
        '284': '🌧️',  # Heavy freezing drizzle
        '293': '🌦️',  # Light rain
        '296': '🌧️',  # Rain
        '299': '🌧️',  # Moderate rain
        '302': '🌧️',  # Heavy rain
        '311': '🌧️',  # Light freezing rain
        '314': '🌧️',  # Heavy freezing rain
        '317': '🌨️',  # Light sleet
        '320': '🌨️',  # Heavy sleet
        '323': '🌨️',  # Light snow
        '326': '🌨️',  # Snow
        '329': '❄️',  # Moderate snow
        '332': '❄️',  # Heavy snow
        '338': '❄️',  # Heavy snow
        '350': '🌨️',  # Ice pellets
        '353': '🌦️',  # Light shower
        '356': '🌧️',  # Heavy shower
        '359': '🌧️',  # Torrential rain
        '362': '🌨️',  # Light sleet shower
        '365': '🌨️',  # Heavy sleet shower
        '368': '🌨️',  # Light snow shower
        '371': '❄️',  # Heavy snow shower
        '386': '⛈️',  # Thunder shower
        '389': '🌩️',  # Heavy thunder
        '392': '⛈️',  # Snow thunder
        '395': '❄️⛈️', # Heavy snow thunder
    }
    return icon_map.get(weather_code, '🌈')

def display_current_weather(data, unit):
    """Display current weather conditions in columns"""
    current = data['current_condition'][0]
    weather_code = current['weatherCode']
    icon = get_weather_icon(weather_code)
    weather_desc = current['weatherDesc'][0]['value']
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperature", 
                 f"{current['temp_'+unit]}°{unit}",
                 f"Feels like {current['FeelsLike'+unit]}°{unit}")
    with col2:
        wind_key = 'windspeedKmph' if unit == 'C' else 'windspeedMiles'
        st.metric("Wind", 
                 f"{current[wind_key]} {'km/h' if unit == 'C' else 'mph'}",
                 current['winddir16Point'])
    with col3:
        st.metric("Humidity", f"{current['humidity']}%")

    st.subheader(f"{icon} {weather_desc}")
    st.caption(f"Observation time: {current['localObsDateTime']}")

    # Additional metrics
    try:
        astronomy = data['weather'][0]['astronomy'][0]
        col4, col5 = st.columns(2)
        with col4:
            st.metric("🌅 Sunrise", astronomy['sunrise'])
        with col5:
            st.metric("🌇 Sunset", astronomy['sunset'])
    except KeyError:
        pass

    # Hourly forecast chart
    try:
        hourly_data = data['weather'][0]['hourly']
        times = []
        temps = []
        for hour in hourly_data:
            time_in_min = int(hour['time'])
            hours = time_in_min // 60
            minutes = time_in_min % 60
            time_str = f"{hours:02d}:{minutes:02d}"
            times.append(time_str)
            temps.append(float(hour[f'temp{unit}']))
        
        chart_data = pd.DataFrame({'Temperature': temps}, index=times)
        st.subheader("24-Hour Temperature Forecast")
        st.line_chart(chart_data)
    except Exception as e:
        st.error(f"Could not display hourly forecast: {e}")

def display_forecast(data, unit):
    """Display 3-day weather forecast with corrected keys"""
    st.subheader("3-Day Forecast")
    cols = st.columns(3)
    for i in range(3):
        day = data['weather'][i]
        with cols[i]:
            date = datetime.strptime(day['date'], "%Y-%m-%d").strftime("%a, %d %b")
            weather_code = day['hourly'][0]['weatherCode']
            icon = get_weather_icon(weather_code)
            st.subheader(f"{icon} {date}")
            
            # Calculate averages
            hourly_humidity = [int(hour['humidity']) for hour in day['hourly']]
            avg_humidity = sum(hourly_humidity) // len(hourly_humidity)
            
            precip_key = 'precipMM' if unit == 'C' else 'precipInches'
            total_precip = sum(float(hour[precip_key]) for hour in day['hourly'])
            precip_unit = 'mm' if unit == 'C' else 'in'

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"🌡 Max: {day[f'maxtemp{unit}']}°{unit}")
                st.write(f"💧 Humidity: {avg_humidity}%")
            with col2:
                st.write(f"🌡 Min: {day[f'mintemp{unit}']}°{unit}")
                st.write(f"🌧️ Rain: {total_precip:.1f}{precip_unit}")

# Streamlit UI Configuration
st.set_page_config(
    page_title="WeatherWise",
    page_icon="🌤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f2f6;
    }
    .st-bq {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Main App
st.title("🌍 WeatherWise - Advanced Weather Dashboard")
st.markdown("### Your Comprehensive Weather Companion")

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    city = st.text_input("🏙️ Enter City Name", "").strip()
    unit = st.selectbox("🌡️ Select Units", ('C', 'F'), index=0)
    
    if st.button("📍 Use My Location"):
        try:
            response = requests.get('https://ipinfo.io/json', timeout=5)
            city = response.json().get('city', 'London')
            st.experimental_rerun()
        except:
            st.error("Could not detect location")

# Main Content
if not city:
    st.info("""
    🌟 Welcome to WeatherWise!
    
    To get started, please:
    1. Enter a city name in the sidebar, or
    2. Click the "Use My Location" button to automatically detect your location
    
    The weather information will appear here once you provide a location.
    """)
else:
    with st.spinner(f"Fetching weather for {city}..."):
        data = get_weather(city)
        local_time = get_local_time(data) if data else None
        
    if data and local_time:
        st.success(f"Local Time: {local_time}")
        display_current_weather(data, unit)
        display_forecast(data, unit)
        
        # Additional Weather Details
        with st.expander("Advanced Weather Details"):
            current = data['current_condition'][0]
            cols = st.columns(4)
            cols[0].metric("Visibility", f"{current['visibility']} km")
            cols[1].metric("Cloud Cover", f"{current['cloudcover']}%")
            cols[2].metric("UV Index", current['uvIndex'])
            cols[3].metric("Pressure", f"{current['pressure']} hPa")
            
        # Weather Map
        st.subheader("Satellite Map")
        st.image(f"https://wttr.in/{city}_0pq_transparent=100.png")
    else:
        st.error("Could not retrieve weather data. Please try again later.")