from flask import Blueprint, request, jsonify
from api.models2 import db
from api.utils.jwt_handler import token_required
from api.models2 import Driver  # o User si aún no has separado Driver como clase hija

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
