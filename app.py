import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from system import get_recent_points

# --- Auto-refresh halaman ---
st_autorefresh(interval=5000, key="gps_refresh")  # Halaman akan otomatis refresh tiap 5 detik

# --- Header UI ---
st.set_page_config(page_title="GPS Tracker", layout="wide")  # Konfigurasi halaman Streamlit
st.markdown("<h1 style='text-align:center;color:#4285F4'>GPS Tracker</h1>", unsafe_allow_html=True)  # Judul halaman

# --- Ambil data GPS ---
points_data = get_recent_points(limit=20)  # Memanggil backend untuk mengambil 20 titik GPS terbaru
if not points_data:
    st.warning("Belum ada data GPS tersedia.")  # Menampilkan peringatan jika data kosong
    st.stop()

# --- Peta ---
last_point = points_data[-1]  # Titik terakhir dijadikan pusat peta
m = folium.Map(location=[last_point['lat'], last_point['lon']], zoom_start=18)  # Inisialisasi peta
for p in points_data:  # Menambahkan marker dan popup untuk tiap titik GPS
    maps_link = f"https://www.google.com/maps/dir/?api=1&destination={p['lat']},{p['lon']}"
    popup_html = f"<b>Waktu:</b> {p['waktu']}<br><b>Tanggal:</b> {p['tanggal']}<br><a href='{maps_link}' target='_blank'>Navigasi</a>"
    folium.Marker(location=[p['lat'], p['lon']], popup=popup_html, icon=folium.Icon(color="blue")).add_to(m)

# Menambahkan garis jalur antar titik GPS
polyline_points = [[p['lat'], p['lon']] for p in points_data]
if len(polyline_points) > 1:
    folium.PolyLine(polyline_points, color="#4285F4", weight=4, opacity=0.8).add_to(m)

st_folium(m, width="100%", height=500)  # Menampilkan peta di Streamlit

# --- History UI ---
st.markdown("<h3 style='color:#4285F4'>Histori</h3>", unsafe_allow_html=True)  # Judul history
for i, p in enumerate(points_data):  # Menampilkan daftar histori titik GPS
    maps_link = f"https://www.google.com/maps/dir/?api=1&destination={p['lat']},{p['lon']}"
    st.markdown(f"{i+1}. Waktu: {p['waktu']}, Tanggal: {p['tanggal']} — [Navigasi]({maps_link})")
