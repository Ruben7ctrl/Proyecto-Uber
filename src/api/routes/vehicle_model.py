from flask import Blueprint, request, jsonify
from ..models import db, VehicleModel
from ..schemas import VehicleModelSchema

vehicle_model_bp = Blueprint(
    'vehicle_model_bp', __name__, url_prefix='/api/vehicle-models')

vehicle_model_schema = VehicleModelSchema()
vehicle_models_schema = VehicleModelSchema(many=True)


@vehicle_model_bp.route('/', methods=['GET'])
def get_vehicle_models():
    models = VehicleModel.query.all()
    return vehicle_models_schema.jsonify(models)


@vehicle_model_bp.route('/<int:id>', methods=['GET'])
def get_vehicle_model(id):
    model = VehicleModel.query.get_or_404(id)
    return vehicle_model_schema.jsonify(model)


@vehicle_model_bp.route('/', methods=['POST'])
def create_vehicle_model():
    data = request.get_json()
    errors = vehicle_model_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    model = vehicle_model_schema.load(data, session=db.session)
    db.session.add(model)
    db.session.commit()
    return vehicle_model_schema.jsonify(model), 201


@vehicle_model_bp.route('/<int:id>', methods=['PUT'])
def update_vehicle_model(id):
    model = VehicleModel.query.get_or_404(id)
    data = request.get_json()
    errors = vehicle_model_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    model = vehicle_model_schema.load(data, instance=model, session=db.session)
    db.session.commit()
    return vehicle_model_schema.jsonify(model)


@vehicle_model_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehicle_model(id):
    model = VehicleModel.query.get_or_404(id)
    db.session.delete(model)
    db.session.commit()
    return '', 204
