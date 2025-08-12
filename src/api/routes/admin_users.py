from flask import Blueprint, request, jsonify
from api import db
from api.models2 import User, Role

admin_users_bp = Blueprint("admin_users_bp", __name__,
                           url_prefix="/admin/users")


@admin_users_bp.route("/", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users])


@admin_users_bp.route("/<int:user_id>/roles", methods=["PUT"])
def assign_roles(user_id):
    data = request.get_json()
    role_ids = data.get("roles", [])
    user = User.query.get_or_404(user_id)
    user.roles = Role.query.filter(Role.id.in_(role_ids)).all()
    db.session.commit()
    return jsonify({"message": "Roles updated"})
