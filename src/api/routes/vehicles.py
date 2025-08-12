from flask import Blueprint, request, jsonify, abort
from api.models2 import db, Vehicle
from api.schemas.vehicle_schemas import VehicleSchema

vehicles_bp = Blueprint('vehicles_bp', __name__, url_prefix='/api/vehicles')

vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)

# GET all vehicles


@vehicles_bp.route('/', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify(vehicles_schema.dump(vehicles)), 200

# GET one vehicle by id


@vehicles_bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify(vehicle_schema.dump(vehicle)), 200

# POST create a new vehicle


@vehicles_bp.route('/', methods=['POST'])
def create_vehicle():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400

    # Validate and deserialize input
    try:
        vehicle = vehicle_schema.load(json_data, session=db.session)
    except Exception as err:
        return jsonify({'message': 'Validation failed', 'errors': err.messages}), 422

    db.session.add(vehicle)
    db.session.commit()

    return jsonify(vehicle_schema.dump(vehicle)), 201

# PUT update an existing vehicle


@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400

    # Validate and deserialize input, partial=True allows partial updates
    try:
        vehicle = vehicle_schema.load(
            json_data, instance=vehicle, session=db.session, partial=True)
    except Exception as err:
        return jsonify({'message': 'Validation failed', 'errors': err.messages}), 422

    db.session.commit()

    return jsonify(vehicle_schema.dump(vehicle)), 200

# DELETE a vehicle


@vehicles_bp.route('/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': f'Vehicle {vehicle_id} deleted'}), 200
