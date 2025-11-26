import requests

CHANNEL_ID = "3167055"
READ_API_KEY = "8NQY0UZ2O9AAI5YV"

# --- Fungsi untuk ambil titik GPS terbaru ---
def get_recent_points(limit=20):
    """
    Mengambil data GPS terbaru dari ThingSpeak.
    
    Args:
        limit (int): jumlah titik terakhir yang ingin diambil (default 20)
        
    Returns:
        List[dict]: list berisi dictionary tiap titik dengan key 'lat', 'lon', 'waktu', 'tanggal'
    """
    # Membuat URL request ke ThingSpeak
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results={limit}&api_key={READ_API_KEY}"
    response = requests.get(url).json()  # Request data JSON dari ThingSpeak
    feeds = response['feeds']  # Ambil array feeds (data tiap titik)

    points = []
    for feed in feeds:  # Loop tiap feed untuk diproses
        if feed['field1'] is not None and feed['field2'] is not None:  # Pastikan ada koordinat
            points.append({
                'lat': float(feed['field1']),  # Latitude
                'lon': float(feed['field2']),  # Longitude
                'waktu': feed['field3'] if feed['field3'] else "N/A",  # Waktu jika tersedia
                'tanggal': feed['field4'] if feed['field4'] else "N/A"  # Tanggal jika tersedia
            })
    return points  # Kembalikan list titik GPS
