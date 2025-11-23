import requests
import folium

# ----------- 1. Fonction pour obtenir les coordonnées -----------
def get_coordinates(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "json", "limit": 1}
    response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'})
    data = response.json()
    if not data:
        raise ValueError(f"Lieu introuvable : {place_name}")
    return float(data[0]["lat"]), float(data[0]["lon"])

# ----------- 2. Départ et arrivée -----------
start_name = "Université de Kinshasa, Kinshasa, RDC"
end_name   = "Université Révérend Kim, N'Djili, Kinshasa, RDC"

start_lat, start_lon = get_coordinates(start_name)
end_lat, end_lon     = get_coordinates(end_name)

# ----------- 3. Appel API OSRM avec alternatives -----------
osrm_url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&alternatives=true"
response = requests.get(osrm_url).json()

routes = response["routes"]

# Tri des routes par distance
routes_sorted = sorted(routes, key=lambda r: r["distance"])
shortest = routes_sorted[0]
longest = routes_sorted[-1]

print(f"Route la plus courte : {shortest['distance']/1000:.2f} km")
print(f"Route la plus longue : {longest['distance']/1000:.2f} km")

# ----------- 4. Carte interactive -----------
carte = folium.Map(location=[start_lat, start_lon], zoom_start=12)

# Marqueurs départ et arrivée
folium.Marker([start_lat, start_lon], popup="UPN", icon=folium.Icon(color="green")).add_to(carte)
folium.Marker([end_lat, end_lon], popup="URKIM", icon=folium.Icon(color="red")).add_to(carte)

# Tracer la route la plus courte (rouge)
coords_short = [[lat, lon] for lon, lat in shortest["geometry"]["coordinates"]]
folium.PolyLine(coords_short, color="red", weight=5, tooltip="Route la plus courte").add_to(carte)

# Tracer la route la plus longue (bleue)
coords_long = [[lat, lon] for lon, lat in longest["geometry"]["coordinates"]]
folium.PolyLine(coords_long, color="blue", weight=5, tooltip="Route la plus longue").add_to(carte)

# Ajouter points intermédiaires (optionnel)
for lon, lat in shortest["geometry"]["coordinates"][::20]:
    folium.CircleMarker([lat, lon], radius=3, color="red", fill=True).add_to(carte)
for lon, lat in longest["geometry"]["coordinates"][::20]:
    folium.CircleMarker([lat, lon], radius=3, color="blue", fill=True).add_to(carte)

# Sauvegarde de la carte
carte.save("itineraire_courte_longue.html")
print("Carte générée : itineraire_courte_longue.html")
