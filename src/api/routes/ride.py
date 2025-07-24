from flask import Blueprint, request, jsonify
from datetime import datetime
from .. import db
from ..models import Ride, User  # Asegúrate de tener estos modelos

ride_bp = Blueprint("ride_bp", __name__, url_prefix="/rides")


@ride_bp.route("/request", methods=["POST"])
def request_ride():
    data = request.get_json()
    user_id = data.get("user_id")
    origin = data.get("origin")
    destination = data.get("destination")

    new_ride = Ride(
        user_id=user_id,
        origin=origin,
        destination=destination,
        status="pending"
    )
    db.session.add(new_ride)
    db.session.commit()

    return jsonify({
        "ride_id": new_ride.id,
        "status": new_ride.status,
        "origin": new_ride.origin,
        "destination": new_ride.destination,
        "message": "Ride requested successfully"
    }), 201


@ride_bp.route("/<int:ride_id>/assign", methods=["POST"])
def assign_driver(ride_id):
    data = request.get_json()
    driver_id = data.get("driver_id")
    ride = Ride.query.get_or_404(ride_id)
    ride.driver_id = driver_id
    ride.status = "assigned"
    db.session.commit()
    return jsonify({"message": "Driver assigned", "ride_id": ride.id})


@ride_bp.route("/<int:ride_id>/start", methods=["POST"])
def start_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    ride.status = "in_progress"
    db.session.commit()
    return jsonify({"message": "Ride started", "ride_id": ride.id})


@ride_bp.route("/<int:ride_id>/finish", methods=["POST"])
def finish_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    ride.status = "completed"
    db.session.commit()
    return jsonify({"message": "Ride completed", "ride_id": ride.id})


@ride_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_rides(user_id):
    rides = Ride.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": r.id,
        "origin": r.origin,
        "destination": r.destination,
        "status": r.status,
        "driver_id": r.driver_id
    } for r in rides])


@ride_bp.route("/driver/<int:driver_id>", methods=["GET"])
def get_driver_rides(driver_id):
    rides = Ride.query.filter_by(driver_id=driver_id).all()
    return jsonify([{
        "id": r.id,
        "origin": r.origin,
        "destination": r.destination,
        "status": r.status,
        "user_id": r.user_id
    } for r in rides])


@ride_bp.route("/history", methods=["GET"])
def ride_history():
    user_id = request.args.get("user_id", type=int)
    driver_id = request.args.get("driver_id", type=int)
    status = request.args.get("status")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = Ride.query

    if user_id:
        query = query.filter_by(user_id=user_id)
    if driver_id:
        query = query.filter_by(driver_id=driver_id)
    if status:
        query = query.filter_by(status=status)
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Ride.created_at >= start)
        except:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Ride.created_at <= end)
        except:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    rides = query.all()
    return jsonify([
        {
            "id": r.id,
            "origin": r.origin,
            "destination": r.destination,
            "status": r.status,
            "user_id": r.user_id,
            "driver_id": r.driver_id
        } for r in rides
    ])
