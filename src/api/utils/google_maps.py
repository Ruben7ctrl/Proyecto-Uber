import os
import requests


GOOGLE_MAPS_API_KEY = os.getenv(
    "GOOGLE_MAPS_API_KEY", "YOUR_GOOGLE_MAPS_API_KEY")


def get_lat_lng_from_place_id(place_id):
    """
    Dado un place_id de Google Places, devuelve latitud y longitud.
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "geometry",
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params)
    if response.ok:
        location = response.json()['result']['geometry']['location']
        return location
    return None


def check_if_airport(pickup, destination, parada, city):
    """
    Verifica si alguna de las ubicaciones está dentro del aeropuerto de la ciudad.
    Devuelve True si pasa por aeropuerto, False si no.
    """
    airport_names = [city.airport_name,
                     city.airport_name_2, city.airport_name_3]
    airport_names = [a.lower() for a in airport_names if a]

    def location_contains_airport_name(loc):
        desc = loc.get("description", "").lower()
        return any(airport in desc for airport in airport_names)

    if location_contains_airport_name(pickup):
        return True
    if location_contains_airport_name(destination):
        return True
    if parada and location_contains_airport_name(parada):
        return True
    return False


def get_place_autocomplete(input_text, location=None, radius=30000):
    """
    Consulta el endpoint Place Autocomplete de Google Maps para obtener sugerencias
    de lugares según un texto parcial.

    Args:
        input_text (str): Texto parcial para autocompletar.
        location (str, optional): Coordenadas "lat,lng" para limitar la búsqueda cerca de este punto.
        radius (int, optional): Radio en metros para restringir resultados alrededor de location.

    Returns:
        dict|None: JSON con las sugerencias o None si falla la petición.
    """
    params = {
        "input": input_text,
        "key": GOOGLE_MAPS_API_KEY,
        "language": "es",
        "components": "country:es",
    }
    if location:
        params["location"] = location
        params["radius"] = radius
        params["strictbounds"] = "true"

    response = requests.get(
        f"{GOOGLE_MAPS_API_URL}place/autocomplete/json", params=params)
    if response.ok:
        return response.json()
    return None


def get_address_from_coords(latlng):
    """
    Consulta el endpoint de Geocoding para obtener la dirección a partir de coordenadas.

    Args:
        latlng (str): Coordenadas en formato "lat,lng".

    Returns:
        dict|None: JSON con la dirección o None si falla la petición.
    """
    params = {
        "latlng": latlng,
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(
        f"{GOOGLE_MAPS_API_URL}geocode/json", params=params)
    if response.ok:
        return response.json()
    return None


def get_coords_from_place_id(place_id):
    """
    Consulta el endpoint Place Details para obtener las coordenadas de un lugar
    a partir de su place_id.

    Args:
        place_id (str): Identificador único del lugar.

    Returns:
        dict|None: Diccionario con "lat" y "lng" o None si no se encontró.
    """
    params = {
        "place_id": place_id,
        "fields": "geometry",
        "key": GOOGLE_MAPS_API_KEY
    }
    response = requests.get(
        f"{GOOGLE_MAPS_API_URL}place/details/json", params=params)
    if response.ok:
        json_data = response.json()
        if 'result' in json_data and 'geometry' in json_data['result']:
            return json_data['result']['geometry']['location']
    return None


def get_directions(origin, destination, waypoints=None):
    """
    Consulta el endpoint Directions para obtener la ruta desde un origen a un destino,
    opcionalmente con paradas intermedias (waypoints).

    Args:
        origin (str): Dirección o coordenadas del punto de origen.
        destination (str): Dirección o coordenadas del punto destino.
        waypoints (list[str], optional): Lista de direcciones o coordenadas para paradas intermedias.

    Returns:
        dict|None: JSON con la ruta o None si falla la petición.
    """
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "key": GOOGLE_MAPS_API_KEY
    }
    if waypoints:
        params["waypoints"] = "|".join(waypoints)

    response = requests.get(
        f"{GOOGLE_MAPS_API_URL}directions/json", params=params)
    if response.ok:
        return response.json()
    return None
