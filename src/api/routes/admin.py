# /api/routes/admin.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, User, Ride

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    current_user = User.query.get(get_jwt_identity())

    if not current_user or current_user.role != "admin":
        return jsonify({"msg": "Unauthorized"}), 403

    total_users = User.query.count()
    total_clients = User.query.filter_by(role="client").count()
    total_drivers = User.query.filter_by(role="driver").count()
    total_rides = Ride.query.count()
    completed_rides = Ride.query.filter_by(status="completed").count()
    assigned_rides = Ride.query.filter_by(status="assigned").count()

    return jsonify({
        "total_users": total_users,
        "clients": total_clients,
        "drivers": total_drivers,
        "total_rides": total_rides,
        "completed_rides": completed_rides,
        "assigned_rides": assigned_rides
    }), 200
