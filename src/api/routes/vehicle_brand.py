from flask import Blueprint, request, jsonify
from ..models import db, VehicleBrand
from ..schemas import VehicleBrandSchema

vehicle_brand_bp = Blueprint(
    'vehicle_brand_bp', __name__, url_prefix='/api/vehicle-brands')

vehicle_brand_schema = VehicleBrandSchema()
vehicle_brands_schema = VehicleBrandSchema(many=True)


@vehicle_brand_bp.route('/', methods=['GET'])
def get_vehicle_brands():
    brands = VehicleBrand.query.all()
    return vehicle_brands_schema.jsonify(brands)


@vehicle_brand_bp.route('/<int:id>', methods=['GET'])
def get_vehicle_brand(id):
    brand = VehicleBrand.query.get_or_404(id)
    return vehicle_brand_schema.jsonify(brand)


@vehicle_brand_bp.route('/', methods=['POST'])
def create_vehicle_brand():
    data = request.get_json()
    errors = vehicle_brand_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    brand = vehicle_brand_schema.load(data, session=db.session)
    db.session.add(brand)
    db.session.commit()
    return vehicle_brand_schema.jsonify(brand), 201


@vehicle_brand_bp.route('/<int:id>', methods=['PUT'])
def update_vehicle_brand(id):
    brand = VehicleBrand.query.get_or_404(id)
    data = request.get_json()
    errors = vehicle_brand_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    brand = vehicle_brand_schema.load(data, instance=brand, session=db.session)
    db.session.commit()
    return vehicle_brand_schema.jsonify(brand)


@vehicle_brand_bp.route('/<int:id>', methods=['DELETE'])
def delete_vehicle_brand(id):
    brand = VehicleBrand.query.get_or_404(id)
    db.session.delete(brand)
    db.session.commit()
    return '', 204
