import math
import os
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models import City, User, VehicleCategory, RideExtra, Setting, db
from api.schemas import VehicleCategorySchema  # Ajusta según tu estructura
from api.utils.google_maps import (
    get_lat_lng_from_place_id,
    check_if_airport
)

maps_bp = Blueprint("maps_bp", __name__, url_prefix="/maps")

GOOGLE_MAPS_API_KEY = os.getenv(
    "GOOGLE_MAPS_API_KEY", "YOUR_GOOGLE_MAPS_API_KEY")


@maps_bp.route("/geocode", methods=["POST"])
def geocode():
    data = request.get_json() or {}
    address = data.get("address")
    if not address:
        return jsonify({"error": "Address is required"}), 400

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY}
    res = requests.get(url, params=params).json()

    if res.get("status") != "OK":
        return jsonify({"message": "Geocoding failed", "error": res.get("status")}), 400

    location = res["results"][0]["geometry"]["location"]
    return jsonify({"lat": location["lat"], "lng": location["lng"]})


@maps_bp.route("/directions", methods=["POST"])
def directions():
    data = request.get_json() or {}
    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return jsonify({"error": "Origin and destination are required"}), 400

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {"origin": origin, "destination": destination,
              "key": GOOGLE_MAPS_API_KEY}
    res = requests.get(url, params=params).json()

    if res.get("status") != "OK":
        return jsonify({"message": "Directions failed", "error": res.get("status")}), 400

    leg = res["routes"][0]["legs"][0]
    return jsonify({
        "distance": leg["distance"]["text"],
        "duration": leg["duration"]["text"],
        "start_address": leg["start_address"],
        "end_address": leg["end_address"]
    })


@maps_bp.route("/directions/with-waypoints", methods=["POST"])
def directions_with_waypoints():
    data = request.get_json() or {}
    origin = data.get("origin")
    destination = data.get("destination")
    waypoints = data.get("waypoints", [])

    if not origin or not destination:
        return jsonify({"error": "Origin and destination are required"}), 400

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "waypoints": "|".join(waypoints) if waypoints else None,
        "key": GOOGLE_MAPS_API_KEY
    }
    # Remove None params
    params = {k: v for k, v in params.items() if v is not None}

    res = requests.get(url, params=params).json()

    if res.get("status") != "OK":
        return jsonify({"message": "Directions failed", "error": res.get("status")}), 400

    legs = res["routes"][0]["legs"]
    return jsonify({
        "legs": [{
            "start_address": l["start_address"],
            "end_address": l["end_address"],
            "distance": l["distance"]["text"],
            "duration": l["duration"]["text"]
        } for l in legs]
    })


@maps_bp.route("/calculate-ride", methods=["POST"])
@jwt_required()
def calculate_ride():
    data = request.get_json() or {}

    legs = data.get("legs")
    user_input = data.get("userInput")
    user_id = data.get("user_id")

    if not legs or not user_input or not user_id:
        return jsonify({"error": "Missing legs, userInput or user_id"}), 400

    pickup = user_input.get("pickup")
    destination = user_input.get("destination")
    parada = user_input.get("parada")

    if not pickup or not destination:
        return jsonify({"error": "Pickup and destination required"}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    city = City.query.filter_by(name="Madrid").first()
    if not city:
        return jsonify({"error": "City not found"}), 404

    total_distance = sum(leg["distance"]["value"] for leg in legs) / 1000  # km
    total_duration = sum(leg["duration"]["value"] for leg in legs)  # seconds

    min_distance = float(Setting.query.get("ride_min").value)
    parada_fee_per_minute = float(Setting.query.get("parada_fee").value)

    through_airport = check_if_airport(pickup, destination, parada, city)

    extra_parada_fee = None
    extra_parada_duration = None
    extra_parada_distance = None

    if parada:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": pickup["description"],
            "destination": destination["description"],
            "mode": "driving",
            "key": GOOGLE_MAPS_API_KEY
        }
        res = requests.get(url, params=params)
        if not res.ok:
            return jsonify({"error": "Error getting direct route"}), 400

        res_json = res.json()
        legs_direct = res_json["routes"][0]["legs"]
        direct_distance = sum(f["distance"]["value"] for f in legs_direct)
        direct_duration = sum(f["duration"]["value"] for f in legs_direct)

        extra_parada_duration = total_duration - direct_duration
        extra_parada_distance = (
            total_distance * 1000 - direct_distance) / 1000

    categories = VehicleCategory.query.all()
    results = []
    for category in categories:
        if total_distance < min_distance:
            price = category.airport_min_rate if through_airport else category.min_rate
        else:
            price = total_distance * category.rate
            if through_airport:
                price += category.airport_min_rate

        if extra_parada_duration:
            extra_fee = (extra_parada_duration / 60) * parada_fee_per_minute
            price += extra_fee
        else:
            extra_fee = None

        category_data = VehicleCategorySchema().dump(category)
        category_data["ride_price"] = round(price, 2)
        category_data["img"] = os.getenv("APP_URL", "") + category.img
        results.append(category_data)

    user.new_ride = {
        "userInput": user_input,
        "computed": {
            "distance": total_distance,
            "duration": total_duration,
            "extra_parada_fee": extra_fee,
            "extra_parada_duration": extra_parada_duration,
            "extra_parada_distance": extra_parada_distance,
            "categories": results
        }
    }
    db.session.commit()

    return jsonify({
        "success": True,
        "total_distance": {
            "text": f"{total_distance:.2f} km",
            "value": total_distance
        },
        "total_duration": {
            "text": f"{total_duration / 60:.2f} min",
            "value": total_duration
        },
        "extras": [e.serialize() for e in RideExtra.query.all()],
        "extra_parada_fee": extra_fee,
        "extra_parada_duration": extra_parada_duration,
        "extra_parada_distance": extra_parada_distance,
        "categories": results
    })


@maps_bp.route('/autocomplete/<string:address>', methods=['GET'])
def autocomplete(address):
    """
    Devuelve sugerencias de autocomplete para una dirección dada,
    limitando a España y un radio alrededor de Madrid.
    """
    city = City.get_madrid()
    params = {
        'input': address,
        'key': os.getenv('GOOGLE_MAPS_API_KEY'),
        'language': 'es',
        'components': 'country:es',
        'location': city.center_latlng,
        'radius': 30000,
        'strictbounds': 'true'
    }
    response = requests.get(
        f"{os.getenv('GOOGLE_MAPS_API_URL')}place/autocomplete/json", params=params)
    return response.text, response.status_code


@maps_bp.route('/reverse_geocode/<string:coords>', methods=['GET'])
def reverse_geocode(coords):
    """
    Devuelve la dirección (geocodificación inversa) a partir de coordenadas lat,lng.
    """
    params = {
        'latlng': coords,
        'key': os.getenv('GOOGLE_MAPS_API_KEY'),
    }
    response = requests.get(
        f"{os.getenv('GOOGLE_MAPS_API_URL')}geocode/json", params=params)
    return response.text, response.status_code


@maps_bp.route('/place-details/<string:place_id>', methods=['GET'])
def get_coordinates_from_address(place_id):
    """
    Devuelve las coordenadas lat,lng para un place_id dado usando utils.
    """
    result = get_coords_from_place_id(place_id)
    if not result:
        return jsonify({'error': 'Could not get coordinates'}), 400
    return jsonify(result)


@maps_bp.route('/calculate-ride', methods=['POST'])
def calculate_ride():
    """
    Calcula el costo, distancia y duración total de un viaje con posibles paradas intermedias,
    incluyendo tarifas según categorías y condiciones especiales (como aeropuerto).
    """
    data = request.get_json()
    legs = data.get('legs')
    user_input = data.get('userInput')
    user_id = data.get('user_id')

    if not legs or not user_input or not user_id:
        return jsonify({'error': 'Missing required fields'}), 400

    pickup = user_input['pickup']
    destination = user_input['destination']
    parada = user_input.get('parada')
    city = City.get_madrid()
    user = User.query.get_or_404(user_id)
    min_distance = float(Setting.get_value('ride_min'))
    parada_fee_per_minute = float(Setting.get_value('parada_fee'))

    total_distance = sum(leg['distance']['value']
                         for leg in legs) / 1000  # en km
    total_duration = sum(leg['duration']['value']
                         for leg in legs)  # en segundos

    through_airport = check_if_airport(pickup, destination, parada, city)

    # Cálculo extra por parada
    extra_distance = extra_duration = extra_fee = 0
    if parada:
        url = os.getenv('GOOGLE_MAPS_API_URL') + 'directions/json'
        params = {
            'origin': pickup['description'],
            'destination': destination['description'],
            'mode': 'driving',
            'key': os.getenv('GOOGLE_MAPS_API_KEY'),
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return jsonify({'error': 'Error getting direct route'}), 401
        direct_legs = response.json()['routes'][0]['legs']
        no_waypoint_distance = sum(leg['distance']['value']
                                   for leg in direct_legs) / 1000
        no_waypoint_duration = sum(leg['duration']['value']
                                   for leg in direct_legs)

        extra_distance = total_distance - no_waypoint_distance
        extra_duration = total_duration - no_waypoint_duration
        extra_fee = (extra_duration / 60) * parada_fee_per_minute

    categories = []
    for category in VehicleCategory.query.all():
        if total_distance < min_distance:
            price = category.airport_min_rate if through_airport else category.min_rate
        else:
            price = total_distance * category.rate
            if through_airport:
                price += category.airport_min_rate
        if extra_fee:
            price += extra_fee

        categories.append({
            'id': category.id,
            'name': category.name,
            'ride_price': round(price, 2),
            'img': os.getenv('APP_URL') + category.img,
        })

    new_ride = {
        'userInput': {
            'pickup': pickup,
            'destination': destination,
            'parada': parada
        },
        'computed': {
            'distance': total_distance,
            'duration': total_duration,
            'extra_parada_fee': extra_fee,
            'extra_parada_duration': extra_duration,
            'extra_parada_distance': extra_distance,
            'categories': categories
        }
    }

    user.new_ride = new_ride
    db.session.commit()

    return jsonify({
        'success': True,
        'total_distance': {'text': f"{round(total_distance, 2)} km.", 'value': total_distance},
        'total_duration': {'text': f"{round(total_duration / 60, 2)} min.", 'value': total_duration},
        'extras': [extra.to_dict() for extra in RideExtra.query.all()],
        'extra_parada_fee': extra_fee,
        'extra_parada_duration': extra_duration,
        'extra_parada_distance': extra_distance,
        'categories': categories
    })


def check_if_airport(pickup, destination, parada, city):
    """
    Verifica si el viaje pasa por un aeropuerto según la distancia a las coordenadas
    del aeropuerto almacenadas en la ciudad.

    Args:
        pickup (dict): Lugar de recogida.
        destination (dict): Lugar de destino.
        parada (dict|None): Parada intermedia (opcional).
        city (City): Instancia de la ciudad con datos del aeropuerto.

    Returns:
        bool: True si pasa por aeropuerto, False si no.
    """
    airport_lat, airport_lng = map(float, city.airport_latlng.split(','))
    airport_min_distance = float(Setting.get_value('airport_min_distance'))


def distance_to_airport(location_id):
    coords = get_coords_from_place_id(location_id)
    if not coords:
        return float('inf')
    return calculate_distance(coords['lat'], coords['lng'], airport_lat, airport_lng)

    pickup_distance = distance_to_airport(pickup['id'])
    destination_distance = distance_to_airport(destination['id'])

    if pickup_distance < airport_min_distance or destination_distance < airport_min_distance:
        return True

    if parada:
        parada_distance = distance_to_airport(parada['id'])
        return parada_distance < airport_min_distance

    return False


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia en kilómetros entre dos puntos geográficos usando la fórmula del
    gran círculo (haversine aproximado).

    Args:
        lat1, lon1, lat2, lon2 (float): Coordenadas en grados decimales.

    Returns:
        float: Distancia en kilómetros.
    """
    if lat1 == lat2 and lon1 == lon2:
        return 0
    theta = lon1 - lon2
    dist = math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.cos(math.radians(theta))
    dist = math.acos(min(max(dist, -1.0), 1.0))
    dist = math.degrees(dist)
    miles = dist * 60 * 1.1515
    km = miles * 1.609344
    return km
