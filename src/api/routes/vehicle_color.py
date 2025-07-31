from flask import Blueprint, request, jsonify
from ..models import db, VehicleColor
from ..schemas import VehicleColorSchema

vehicle_color_bp = Blueprint(
    'vehicle_color_bp', __name__, url_prefix='/api/vehicle-colors')

vehicle_color_schema = VehicleColorSchema()
vehicle_colors_schema = VehicleColorSchema(many=True)


@vehicle_color_bp.route('/', methods=['GET'])
def get_vehicle_colors():
    colors = VehicleColor.query.all()
    return vehicle_colors_schema.jsonify(colors)


@vehicle_color_bp.route('/<int:id>', methods=['GET'])
def get_vehicle_color(id):
    color = VehicleColor.query.get_or_404(id)
    return vehicle_color_schema.jsonify(color)


@vehicle_color_bp.route('/', methods=['POST'])
def create_vehicle_color():
    data = request.get_json()
    errors = vehicle_color_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    color = vehicle_color_schema.load(data, session=db.session)
    db.session.add(color)
    db.session.commit()
    return vehicle_color_schema.jsonify(color), 201


@vehicle_color_bp.route('/<int:id>', methods=['PUT'])
def update_vehicle_color(id):
    color = VehicleColor.query.get_or_404(id)
    data = request.get_json()
    errors = vehicle_color_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    color = vehicle_color_schema.load(data, instance=color, session=db.session)
    db.session.commit()
    return vehicle_color_schema.jsonify(color)


@vehicle_color_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehicle_color(id):
    color = VehicleColor.query.get_or_404(id)
    db.session.delete(color)
    db.session.commit()
    return '', 204
