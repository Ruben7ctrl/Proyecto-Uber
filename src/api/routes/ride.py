from flask import Blueprint, request, jsonify
from datetime import datetime
from .. import db
from api.models2 import Ride, User  # Asegúrate de tener estos modelos
from api.auth import token_required

ride_bp = Blueprint("ride_bp", __name__, url_prefix="/rides")


@ride_bp.route("/request", methods=["POST"])
@token_required
def request_ride(current_user):
    if current_user.role != "customer":
        return jsonify({"message": "Only customers can request rides"}), 403

    data = request.get_json()
    user_id = data.get("user_id")
    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return jsonify({"message": "Origin and destination required"}), 400

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
@token_required
def assign_driver(current_user, ride_id):
    if current_user.role != "driver":
        return jsonify({"message": "Only drivers can assign themselves"}), 403

    ride = Ride.query.get_or_404(ride_id)
    driver_id = data.get("driver_id")

    if ride.driver_id is not None:
        return jsonify({"message": "Ride already assigned"}), 400

    ride.driver_id = current_user.id
    ride.status = Ride.STATUS_ACTIVE
    db.session.commit()
    return jsonify({"message": "Driver assigned", "ride_id": ride.id})


@ride_bp.route("/<int:ride_id>/start", methods=["POST"])
@token_required
def start_ride(current_user, ride_id):
    ride = Ride.query.get_or_404(ride_id)
    if ride.driver_id != current_user.id:
        return jsonify({"message": "Unauthorized to start this ride"}), 403

    ride.status = Ride.STATUS_ACTIVE
    db.session.commit()
    return jsonify({"message": "Ride started", "ride_id": ride.id})


@ride_bp.route("/<int:ride_id>/finish", methods=["POST"])
@token_required
def finish_ride(current_user, ride_id):
    ride = Ride.query.get_or_404(ride_id)
    if ride.driver_id != current_user.id:
        return jsonify({"message": "Unauthorized to finish this ride"}), 403

    ride.status = Ride.STATUS_DONE
    db.session.commit()
    return jsonify({"message": "Ride completed", "ride_id": ride.id})


@ride_bp.route("/user/<int:user_id>", methods=["GET"])
@token_required
def get_user_rides(current_user):
    if current_user.role != "customer":
        return jsonify({"message": "Only customers can view their rides"}), 403

    rides = Ride.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": r.id,
        "origin": r.origin,
        "destination": r.destination,
        "status": r.status,
        "driver_id": r.driver_id
    } for r in rides])


@ride_bp.route("/driver/<int:driver_id>", methods=["GET"])
@token_required
def get_driver_rides(current_user):
    if current_user.role != "driver":
        return jsonify({"message": "Only drivers can view their rides"}), 403

    rides = Ride.query.filter_by(driver_id=current_user.id).all()
    return jsonify([{
        "id": r.id,
        "origin": r.origin,
        "destination": r.destination,
        "status": r.status,
        "user_id": r.user_id
    } for r in rides])


@ride_bp.route("/history", methods=["GET"])
@token_required
def ride_history(current_user):
    # Podrías agregar control de acceso, por ejemplo admins pueden ver todo,
    # clientes solo sus rides, drivers solo los suyos, etc.
    user_id = request.args.get("user_id", type=int)
    driver_id = request.args.get("driver_id", type=int)
    status = request.args.get("status")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = Ride.query

    # Aquí podrías validar acceso para que user_id o driver_id solo sean válidos si corresponden al current_user
    if current_user.role == "customer":
        query = query.filter_by(user_id=current_user.id)
    elif current_user.role == "driver":
        query = query.filter_by(driver_id=current_user.id)
    else:
        # Admin o roles que pueden filtrar todo
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


@ride_bp.route("", methods=["POST"])
@token_required
def create_ride(current_user):
    if current_user.role != "customer":
        return jsonify({"message": "Only customers can create rides"}), 403

    data = request.get_json()

    # Validar campos mínimos
    required_fields = ['pickup', 'destination', 'city_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field {field}"}), 400

    ride = Ride(
        pickup=data['pickup'],
        destination=data['destination'],
        parada=data.get('parada'),
        status_value=Ride.STATUS_CREATED,
        city_id=data['city_id'],
        customer_id=current_user.id
    )

    extras_ids = data.get('extras', [])
    if extras_ids:
        extras = RideExtra.query.filter(RideExtra.id.in_(extras_ids)).all()
        ride.extras = extras

    db.session.add(ride)
    db.session.commit()

    return jsonify(ride.serialize()), 201


@ride_bp.route("/<int:ride_id>", methods=["GET"])
@token_required
def get_ride(current_user, ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Validar que el usuario pueda ver el ride
    if current_user.role == "customer" and ride.customer_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403
    if current_user.role == "driver" and ride.driver_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403

    return jsonify(ride.serialize())


@ride_bp.route("/<int:ride_id>", methods=["PUT", "PATCH"])
@token_required
def update_ride(current_user, ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Validar permiso de edición
    if current_user.role == "customer" and ride.customer_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403
    if current_user.role == "driver":
        return jsonify({"message": "Drivers cannot update rides"}), 403

    data = request.get_json()
    if 'pickup' in data:
        ride.pickup = data['pickup']
    if 'destination' in data:
        ride.destination = data['destination']
    if 'parada' in data:
        ride.parada = data['parada']
    if 'status_value' in data and data['status_value'] in [Ride.STATUS_ACTIVE, Ride.STATUS_DONE, Ride.STATUS_CANCELED, Ride.STATUS_CREATED]:
        ride.status_value = data['status_value']
    if 'driver_id' in data:
        ride.driver_id = data['driver_id']
    if 'extras' in data:
        extras_ids = data['extras']
        extras = RideExtra.query.filter(RideExtra.id.in_(extras_ids)).all()
        ride.extras = extras

    db.session.commit()
    return jsonify(ride.serialize())


@ride_bp.route("/<int:ride_id>", methods=["DELETE"])
@token_required
def delete_ride(current_user, ride_id):
    ride = Ride.query.get_or_404(ride_id)

    # Validar permiso
    if current_user.role != "admin":
        return jsonify({"message": "Only admins can delete rides"}), 403

    db.session.delete(ride)
    db.session.commit()
    return jsonify({"message": "Ride deleted"}), 200


@ride_bp.route("", methods=["GET"])
@token_required
def list_rides(current_user):
    # Solo admins pueden listar o filtrar rides
    if current_user.role != "admin":
        return jsonify({"message": "Only admins can list rides"}), 403

    # Parámetros de filtro opcionales
    user_id = request.args.get("user_id", type=int)
    driver_id = request.args.get("driver_id", type=int)
    status = request.args.get("status")
    city_id = request.args.get("city_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = Ride.query

    if user_id:
        query = query.filter_by(customer_id=user_id)
    if driver_id:
        query = query.filter_by(driver_id=driver_id)
    if status:
        query = query.filter_by(status_value=status)
    if city_id:
        query = query.filter_by(city_id=city_id)

    # Filtro fechas con validación del formato
    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Ride.created_at >= start)
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Ride.created_at <= end)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    rides = query.all()

    return jsonify([r.serialize() for r in rides])


@ride_bp.route("/<int:ride_id>/status", methods=["POST"])
def update_ride_status(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    data = request.get_json()
    new_status = data.get("status")

    valid_statuses = [Ride.STATUS_ACTIVE, Ride.STATUS_DONE,
                      Ride.STATUS_CANCELED, Ride.STATUS_CREATED]
    if new_status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400

    ride.status_value = new_status
    db.session.commit()
    return jsonify({"message": f"Ride status updated to {new_status}", "ride": ride.serialize()})


@ride_bp.route("/extras", methods=["GET"])
@token_required
def get_all_extras(current_user):
    # Opcional: validar roles si quieres limitar acceso
    extras = RideExtra.query.all()
    return jsonify([e.serialize() for e in extras])
