from flask import Blueprint, request, jsonify
from api.models import db, SystemConfig

config_bp = Blueprint("config_bp", __name__, url_prefix='/config')


@config_bp.route("/", methods=["GET"])
def list_config():
    configs = SystemConfig.query.all()
    return jsonify([
        {"key": c.key, "value": c.value, "description": c.description} for c in configs
    ])


@config_bp.route("/<key>", methods=["GET"])
def get_config(key):
    config = SystemConfig.query.filter_by(key=key).first_or_404()
    return jsonify({"key": config.key, "value": config.value})


@config_bp.route("/", methods=["POST"])
def create_config():
    data = request.get_json() or {}
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
def update_config(key):
    data = request.get_json() or {}
    config = SystemConfig.query.filter_by(key=key).first_or_404()
    config.value = data.get("value", config.value)
    db.session.commit()
    return jsonify({"message": "Configuration updated."})
