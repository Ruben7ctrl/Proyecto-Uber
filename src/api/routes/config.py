from flask import Blueprint, request, jsonify
from api.models import db, SystemConfig
from flask_jwt_extended import jwt_required
from api.utils.decorators import admin_required

config_bp = Blueprint("config_bp", __name__, url_prefix='/config')


@config_bp.route("/", methods=["GET"])
def list_config():
    configs = SystemConfig.query.all()
    return jsonify([
        {"key": c.key, "value": c.value, "description": getattr(c, "description", None)} for c in configs
    ])


@config_bp.route("/<key>", methods=["GET"])
def get_config(key):
    config = SystemConfig.query.filter_by(key=key).first_or_404()
    return jsonify({"key": config.key, "value": config.value})


@config_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required
def create_config():
    data = request.get_json() or {}
    errors = SystemConfigSchema().validate(data)
    if errors:
        return jsonify(errors), 400
    if not data.get("key") or not data.get("value"):
        return jsonify({"error": "Key and value are required"}), 400

    existing = SystemConfig.query.filter_by(key=data["key"]).first()
    if existing:
        return jsonify({"error": "Configuration with this key already exists"}), 400

    config = SystemConfig(**data)
    db.session.add(config)
    db.session.commit()
    return jsonify({"message": "Configuration saved."}), 201


@config_bp.route("/<key>", methods=["PUT"])
@jwt_required()
@admin_required
def update_config(key):
    data = request.get_json() or {}
    config = SystemConfig.query.filter_by(key=key).first_or_404()

    if "value" not in data:
        return jsonify({"error": "Value is required"}), 400

    config.value = data["value"]
    db.session.commit()
    return jsonify({"message": "Configuration updated."})


@config_bp.route("/<key>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_config(key):
    config = SystemConfig.query.filter_by(key=key).first_or_404()
    db.session.delete(config)
    db.session.commit()
    return jsonify({"message": "Configuration deleted."})
