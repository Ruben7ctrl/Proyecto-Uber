import requests
from flask import Blueprint, request, jsonify
import os

places_bp = Blueprint("places_bp", __name__, url_prefix="/places")

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_GOOGLE_MAPS_API_KEY")


@places_bp.route("/autocomplete", methods=["GET"])
def autocomplete():
    input_text = request.args.get("input")
    if not input_text:
        return jsonify({"error": "Missing input parameter"}), 400

    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": input_text,
        "key": GOOGLE_API_KEY
    }

    res = requests.get(url, params=params).json()
    if res.get("status") != "OK":
        return jsonify({"error": res.get("status")}), 400

    return jsonify(res.get("predictions", []))


@places_bp.route("/details", methods=["GET"])
def place_details():
    place_id = request.args.get("place_id")
    if not place_id:
        return jsonify({"error": "Missing place_id parameter"}), 400

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_API_KEY
    }

    res = requests.get(url, params=params).json()
    if res.get("status") != "OK":
        return jsonify({"error": res.get("status")}), 400

    return jsonify(res.get("result", {}))
