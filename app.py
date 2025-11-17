import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from system import get_recent_points

# --- Auto-refresh halaman ---
st_autorefresh(interval=5000, key="gps_refresh")  # Halaman otomatis refresh tiap 5 detik

# --- Header UI ---
st.set_page_config(page_title="GPS Tracker", layout="wide")
st.markdown("<h1 style='text-align:center;color:#4285F4'>GPS Tracker</h1>", unsafe_allow_html=True)

# --- Ambil data GPS ---
points_data = get_recent_points(limit=20)
if not points_data:
    st.warning("Belum ada data GPS tersedia.")
    st.stop()

# --- Peta ---
last_point = points_data[-1]
m = folium.Map(location=[last_point['lat'], last_point['lon']], zoom_start=18)

for p in points_data:
    # Hanya tampilkan info waktu & tanggal di popup
    popup_html = f"""
    <b>Waktu:</b> {p['waktu']}<br>
    <b>Tanggal:</b> {p['tanggal']}<br>
    """
    folium.Marker(
        location=[p['lat'], p['lon']],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Garis jalur antar titik GPS
polyline_points = [[p['lat'], p['lon']] for p in points_data]
if len(polyline_points) > 1:
    folium.PolyLine(polyline_points, color="#4285F4", weight=4, opacity=0.8).add_to(m)

st_folium(m, width="100%", height=500)

# --- History UI ---
st.markdown("<h3 style='color:#4285F4'>Histori</h3>", unsafe_allow_html=True)
for i, p in enumerate(points_data):
    # Link navigasi untuk membuka Google Maps app
    maps_link = f"https://www.google.com/maps/dir/?api=1&destination={p['lat']},{p['lon']}"
    st.markdown(f"{i+1}. Waktu: {p['waktu']}, Tanggal: {p['tanggal']} — [Navigasi]({maps_link})")
