from flask import Blueprint, request, jsonify
from api.models2 import db, VehicleCategory
from api.schemas import VehicleCategorySchema

vehicle_category_bp = Blueprint(
    'vehicle_category_bp', __name__, url_prefix='/api/vehicle-categories')

vehicle_category_schema = VehicleCategorySchema()
vehicle_categories_schema = VehicleCategorySchema(many=True)


@vehicle_category_bp.route('/', methods=['GET'])
def get_vehicle_categories():
    categories = VehicleCategory.query.all()
    return vehicle_categories_schema.jsonify(categories)


@vehicle_category_bp.route('/<int:id>', methods=['GET'])
def get_vehicle_category(id):
    category = VehicleCategory.query.get_or_404(id)
    return vehicle_category_schema.jsonify(category)


@vehicle_category_bp.route('/', methods=['POST'])
def create_vehicle_category():
    data = request.get_json()
    errors = vehicle_category_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    category = vehicle_category_schema.load(data, session=db.session)
    db.session.add(category)
    db.session.commit()
    return vehicle_category_schema.jsonify(category), 201


@vehicle_category_bp.route('/<int:id>', methods=['PUT'])
def update_vehicle_category(id):
    category = VehicleCategory.query.get_or_404(id)
    data = request.get_json()
    errors = vehicle_category_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    category = vehicle_category_schema.load(
        data, instance=category, session=db.session)
    db.session.commit()
    return vehicle_category_schema.jsonify(category)


@vehicle_category_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehicle_category(id):
    category = VehicleCategory.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return '', 204
