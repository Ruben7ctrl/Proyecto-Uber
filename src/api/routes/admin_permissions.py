from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models2 import Permission, db
from api.schemas.permission import PermissionCreateSchema, PermissionUpdateSchema
from api.utils.decorators import admin_required

admin_permissions_bp = Blueprint(
    "admin_permissions", __name__, url_prefix="/admin/permissions")


@admin_permissions_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required
def list_permissions():
    permissions = Permission.query.all()
    return jsonify([p.serialize() for p in permissions])


@admin_permissions_bp.route("/<int:permission_id>", methods=["GET"])
@jwt_required()
@admin_required
def show_permission(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    return jsonify(permission.serialize())


@admin_permissions_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required
def create_permission():
    data = request.json
    errors = PermissionCreateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    # Controlar duplicado
    if Permission.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Permission with this name already exists"}), 409

    permission = Permission(**data)
    db.session.add(permission)
    db.session.commit()
    return jsonify(permission.serialize()), 201


@admin_permissions_bp.route("/<int:permission_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_permission(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    data = request.json
    errors = PermissionUpdateSchema().validate(data)
    if errors:
        return jsonify(errors), 400
    for key, value in data.items():
        setattr(permission, key, value)
    db.session.commit()
    return jsonify(permission.serialize())


@admin_permissions_bp.route("/<int:permission_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_permission(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    db.session.delete(permission)
    db.session.commit()
    return jsonify({"msg": "Permission deleted"}), 200
