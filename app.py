import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from system import get_recent_points

from dateutil import parser
from datetime import datetime
import pytz


# --- Auto-refresh ---
st_autorefresh(interval=5000, key="gps_refresh")

# --- Header ---
st.set_page_config(page_title="GPS Tracker", layout="wide")
st.markdown("<h1 style='text-align:center;color:#4285F4'>GPS Tracker</h1>", unsafe_allow_html=True)

# --- Ambil data ---
points_data = get_recent_points(limit=20)
if not points_data:
    st.warning("Belum ada data GPS tersedia.")
    st.stop()

# === KONVERSI WAKTU KE WIB ===
utc = pytz.utc
wib = pytz.timezone("Asia/Jakarta")

for p in points_data:
    raw_time = str(p.get('waktu', '')).strip()

    # default: tampilkan apa adanya
    p['waktu_wib'] = raw_time
    p['tanggal_wib'] = p.get('tanggal', '')

    if not raw_time:
        continue

    try:
        dt = parser.parse(raw_time)

        if dt.tzinfo is not None:
            # waktu sudah punya timezone → langsung ke WIB
            wib_time = dt.astimezone(wib)
        else:
            # waktu tidak punya timezone → asumsikan UTC dulu
            dt_utc = utc.localize(dt)
            wib_time = dt_utc.astimezone(wib)

            # cek apakah masuk akal
            now_wib = datetime.now(wib)
            diff = abs((wib_time - now_wib).total_seconds())
            if diff > 12 * 3600:
                # kemungkinan sudah WIB, jangan digeser dua kali
                wib_time = wib.localize(dt)

        p['waktu_wib'] = wib_time.strftime("%H:%M:%S")
        p['tanggal_wib'] = wib_time.strftime("%d/%m/%Y")

    except:
        pass


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

# Garis jalur
polyline_points = [[p['lat'], p['lon']] for p in points_data]
if len(polyline_points) > 1:
    folium.PolyLine(polyline_points, color="#4285F4", weight=4, opacity=0.8).add_to(m)

st_folium(m, width="100%", height=500)

# --- History ---
st.markdown("<h3 style='color:#4285F4'>Histori</h3>", unsafe_allow_html=True)

for i, p in enumerate(points_data):
    # deep link → langsung buka aplikasi Google Maps
    maps_link = f"google.navigation:q={p['lat']},{p['lon']}&mode=d"

    st.markdown(
        f"{i+1}. Waktu (WIB): {p['waktu_wib']}, "
        f"Tanggal: {p['tanggal_wib']} — "
        f"[Navigasi]({maps_link})"
    )
