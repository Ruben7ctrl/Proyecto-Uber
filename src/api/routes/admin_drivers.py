from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models import Driver
from api.schemas.driver import DriverCreateSchema, DriverUpdateSchema
from api.services.driver_service import create_driver, update_driver, delete_driver
from api.utils.decorators import admin_required

admin_drivers_bp = Blueprint(
    "admin_drivers", __name__, url_prefix="/admin/drivers")


@admin_drivers_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required
def list_drivers():
    drivers = Driver.query.all()
    return jsonify([d.serialize() for d in drivers])


@admin_drivers_bp.route("/<int:driver_id>", methods=["GET"])
@jwt_required()
@admin_required
def show_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    return jsonify(driver.serialize())


@admin_drivers_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required
def create_driver_route():
    data = request.json
    errors = DriverCreateSchema().validate(data)
    if errors:
        return jsonify(errors), 400
    driver, err = create_driver(data)
    if err:
        return jsonify(err), 400
    return jsonify(driver.serialize()), 201


@admin_drivers_bp.route("/<int:driver_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_driver_route(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    data = request.json
    errors = DriverUpdateSchema().validate(data)
    if errors:
        return jsonify(errors), 400
    err = update_driver(driver, data)
    if err:
        return jsonify(err), 400
    return jsonify(driver.serialize())


@admin_drivers_bp.route("/<int:driver_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_driver_route(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    delete_driver(driver)
    return jsonify({"msg": "Driver deleted"}), 200
