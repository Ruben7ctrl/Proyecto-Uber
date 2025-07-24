import os
import requests
from flask import Blueprint, request, jsonify

notifications_bp = Blueprint(
    "notifications_bp", __name__, url_prefix="/notifications")

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")


@notifications_bp.route("/send", methods=["POST"])
def send_notification():
    data = request.get_json() or {}
    to = data.get("to")  # Token o topic
    title = data.get("title")
    body = data.get("body")
    extra = data.get("data", {})

    if not FCM_SERVER_KEY:
        return jsonify({"error": "FCM server key not set"}), 500

    if not to or not title or not body:
        return jsonify({"error": "Missing required fields (to, title, body)"}), 400

    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": to,
        "notification": {"title": title, "body": body},
        "data": extra
    }

    response = requests.post(
        "https://fcm.googleapis.com/fcm/send", json=payload, headers=headers)

    if response.status_code == 200:
        return jsonify({"message": "Notification sent"}), 200
    else:
        return jsonify({
            "error": "Failed to send notification",
            "details": response.text
        }), 500
