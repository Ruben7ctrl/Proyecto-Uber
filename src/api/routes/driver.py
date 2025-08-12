from flask import Blueprint, request, jsonify

from sqlalchemy import func
from api.models2 import db, Driver, Ride, Transaction
from api.utils.jwt_handler import token_required

driver_bp = Blueprint("driver", __name__)


@driver_bp.route("/change-status", methods=["POST"])
@token_required
def change_status(current_user):
    data = request.get_json()
    new_status = data.get("driver_status")

    # Validación del valor recibido
    if new_status not in [0, 1]:
        return jsonify({"error": "Invalid status"}), 400

    # Validar que es conductor
    if not hasattr(current_user, "driver_status"):
        return jsonify({"error": "Only drivers can perform this action"}), 403

    current_user.driver_status = new_status
    db.session.commit()

    return jsonify({
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "driver_status": current_user.driver_status
        },
        "message": "Success"
    }), 200


@driver_bp.route("/stats", methods=["GET"])
@token_required
def driver_stats(current_user):
    """Return basic statistics for the authenticated driver."""
    if current_user.role != "driver":
        return jsonify({"error": "Only drivers can view stats"}), 403

    rides = Ride.query.filter_by(driver_id=current_user.id).all()
    total_rides = len(rides)

    total_revenue = (
        db.session.query(func.sum(Transaction.amount))
        .join(Ride, Transaction.ride_id == Ride.id)
        .filter(Ride.driver_id == current_user.id, Transaction.type == "payment")
        .scalar()
        or 0.0
    )

    estimated_hours = total_rides * 1.5

    return jsonify(
        {
            "total_rides": total_rides,
            "estimated_hours": estimated_hours,
            "total_revenue": total_revenue,
        }
    ), 200
