import os
import requests
from flask import Blueprint, request, jsonify

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
