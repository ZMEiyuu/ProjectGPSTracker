import requests
import folium
from streamlit_folium import st_folium
import streamlit as st
from streamlit_autorefresh import st_autorefresh

CHANNEL_ID = "3167055"
WRITE_API_KEY = "L5379U9H379NGATS"
READ_API_KEY = "8NQY0UZ2O9AAI5YV"

st.set_page_config(page_title="GPS Tracker", layout="wide")
st.markdown("""
<style>
body {
    background-color: #f0f0f0;
    color: #000000;
    font-family: Arial, sans-serif;
}
.sidebar .sidebar-content {
    background-color: #ffffff;
    color: #000000;
}
.stButton>button {
    background: linear-gradient(145deg, #4285F4, #1a73e8);
    color: #ffffff;
    font-weight: bold;
    border-radius: 12px;
    padding: 12px;
    margin-top: 10px;
    width: 100%;
    box-shadow: 0 6px 0 #1a73e8, 0 6px 12px rgba(0,0,0,0.2);
    transition: all 0.2s ease;
}
.stButton>button:active {
    transform: translateY(4px);
    box-shadow: 0 2px 0 #1a73e8, 0 2px 6px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:#4285F4'>GPS Tracker</h1>", unsafe_allow_html=True)

if "points" not in st.session_state:
    st.session_state.points = []

def get_latest_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results=1&api_key={READ_API_KEY}"
    try:
        response = requests.get(url, timeout=5).json()
        feed = response['feeds'][0]
        lat = float(feed['field1']) if feed['field1'] else None
        lon = float(feed['field2']) if feed['field2'] else None
        waktu = feed['field3'] if feed['field3'] else "N/A"
        tanggal = feed['field4'] if feed['field4'] else "N/A"
        status_alat = int(feed['field5']) if feed['field5'] else 0
        return lat, lon, waktu, tanggal, status_alat
    except:
        return None, None, "N/A", "N/A", 0

def set_device(status):
    try:
        url = f"https://api.thingspeak.com/update?api_key={WRITE_API_KEY}&field5={status}"
        requests.get(url, timeout=5)
    except:
        pass

st.sidebar.markdown("<h3 style='color:#4285F4'>Kontrol Alat</h3>", unsafe_allow_html=True)
if st.sidebar.button("Hidupkan Alat"):
    set_device(1)
if st.sidebar.button("Matikan Alat"):
    set_device(0)

# Auto-refresh tiap 15 detik
st_autorefresh(interval=15000, key="gps_refresh")

lat, lon, waktu, tanggal, status_alat = get_latest_data()
if lat is not None and lon is not None:
    st.session_state.points.append([lat, lon])
else:
    lat, lon = 0, 0

m = folium.Map(location=[lat, lon], zoom_start=18, tiles='OpenStreetMap')

marker_color = "green" if status_alat == 1 else "red"
status_text = "ON" if status_alat == 1 else "OFF"
maps_link = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"

popup_html = f"""
<b>Waktu:</b> {waktu}<br>
<b>Tanggal:</b> {tanggal}<br>
<b>Status Alat:</b> {status_text}<br>
<a href='{maps_link}' target='_blank' style='color:#4285F4;font-weight:bold'>Navigasi ke sini</a>
"""

folium.Marker(
    location=[lat, lon],
    popup=popup_html,
    tooltip=f"GPS Tracker - {status_text}",
    icon=folium.Icon(color=marker_color, icon='map-marker', prefix='fa')
).add_to(m)

if len(st.session_state.points) > 1:
    folium.PolyLine(st.session_state.points, color="#4285F4", weight=4, opacity=0.8).add_to(m)

st.markdown("""
<div style="border: 4px solid #4285F4; border-radius: 5px; padding: 5px; width: 100%; box-sizing: border-box;">
""", unsafe_allow_html=True)

st_folium(m, width="100%", height=500)
st.markdown("</div>", unsafe_allow_html=True)
