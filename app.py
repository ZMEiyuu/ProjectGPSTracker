import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from system import get_recent_points
from datetime import datetime, timedelta

# --- Fungsi Konversi UTC → WIB (GMT+7) ---
def convert_to_wib(date_str, time_str):
    """
    date_str : '2025-11-26'
    time_str : '09:15:22'
    """
    try:
        # Gabungkan tanggal + waktu
        dt_utc = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        dt_wib = dt_utc + timedelta(hours=7)
        return dt_wib.strftime("%Y-%m-%d"), dt_wib.strftime("%H:%M:%S")
    except:
        return date_str, time_str  # Antisipasi jika format salah


# --- Auto-refresh halaman ---
st_autorefresh(interval=5000, key="gps_refresh")

# --- Header UI ---
st.set_page_config(page_title="GPS Tracker", layout="wide")
st.markdown("<h1 style='text-align:center;color:#4285F4'>GPS Tracker</h1>", unsafe_allow_html=True)

# --- Ambil data GPS ---
points_data = get_recent_points(limit=20)
if not points_data:
    st.warning("Belum ada data GPS tersedia.")
    st.stop()

# --- KONVERSI SEMUA WAKTU KE WIB ---
for p in points_data:
    tanggal_wib, waktu_wib = convert_to_wib(p['tanggal'], p['waktu'])
    p['tanggal_wib'] = tanggal_wib
    p['waktu_wib'] = waktu_wib

# --- Peta ---
last_point = points_data[-1]
m = folium.Map(location=[last_point['lat'], last_point['lon']], zoom_start=18)

for p in points_data:
    popup_html = f"""
    <b>Waktu (WIB):</b> {p['waktu_wib']}<br>
    <b>Tanggal:</b> {p['tanggal_wib']}<br>
    """
    folium.Marker(
        location=[p['lat'], p['lon']],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Garis jalur GPS
polyline_points = [[p['lat'], p['lon']] for p in points_data]
if len(polyline_points) > 1:
    folium.PolyLine(polyline_points, color="#4285F4", weight=4, opacity=0.8).add_to(m)

st_folium(m, width="100%", height=500)

# --- History UI ---
st.markdown("<h3 style='color:#4285F4'>Histori (WIB)</h3>", unsafe_allow_html=True)
for i, p in enumerate(points_data):
    maps_link = f"https://www.google.com/maps/dir/?api=1&destination={p['lat']},{p['lon']}"
    st.markdown(
        f"{i+1}. Waktu: **{p['waktu_wib']}**, "
        f"Tanggal: **{p['tanggal_wib']}** — [Navigasi]({maps_link})"
    )
