from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models2 import Role, Permission, db
from api.schemas.role import RoleCreateSchema, RoleUpdateSchema
from api.utils.decorators import admin_required

admin_roles_bp = Blueprint("admin_roles", __name__, url_prefix="/admin/roles")

# List all roles


@admin_roles_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required
def list_roles():
    roles = Role.query.all()
    return jsonify([r.serialize() for r in roles]), 200

# Get specific role


@admin_roles_bp.route("/<int:role_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_role(role_id):
    role = Role.query.get_or_404(role_id)
    return jsonify(role.serialize()), 200

# Create role


@admin_roles_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required
def create_role():
    data = request.json
    errors = RoleCreateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    if Role.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Role with this name already exists"}), 409

    role = Role(name=data["name"], display_name=data["display_name"])
    db.session.add(role)
    db.session.commit()
    return jsonify(role.serialize()), 201

# Update role


@admin_roles_bp.route("/<int:role_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_role(role_id):
    role = Role.query.get_or_404(role_id)
    data = request.json
    errors = RoleUpdateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    role.name = data.get("name", role.name)
    role.display_name = data.get("display_name", role.display_name)
    db.session.commit()
    return jsonify(role.serialize()), 200

# Delete role


@admin_roles_bp.route("/<int:role_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    return jsonify({"msg": "Role deleted"}), 200

# Assign permissions to role


@admin_roles_bp.route("/<int:role_id>/permissions", methods=["POST"])
@jwt_required()
@admin_required
def assign_permissions(role_id):
    role = Role.query.get_or_404(role_id)
    data = request.json
    permission_ids = data.get("permission_ids", [])

    if not isinstance(permission_ids, list):
        return jsonify({"error": "permission_ids must be a list"}), 400

    role.permissions = Permission.query.filter(
        Permission.id.in_(permission_ids)).all()
    db.session.commit()
    return jsonify({"msg": "Permissions updated", "permissions": [p.serialize() for p in role.permissions]}), 200
