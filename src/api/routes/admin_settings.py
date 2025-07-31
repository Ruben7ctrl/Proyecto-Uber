from flask import Blueprint, request, jsonify
from api.models import db, Setting
from api.schemas.setting import SettingCreateSchema, SettingUpdateSchema
from flask_jwt_extended import jwt_required
from api.utils.decorators import admin_required

admin_settings_bp = Blueprint(
    "admin_settings", __name__, url_prefix="/admin/settings")


@admin_settings_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required
def list_settings():
    settings = Setting.query.all()
    return jsonify([s.serialize() for s in settings])


@admin_settings_bp.route("/<key>", methods=["GET"])
@jwt_required()
@admin_required
def get_setting(key):
    setting = Setting.query.filter_by(key=key).first_or_404()
    return jsonify(setting.serialize())


@admin_settings_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required
def create_setting():
    data = request.get_json() or {}
    errors = SettingCreateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    existing = Setting.query.filter_by(key=data["key"]).first()
    if existing:
        return jsonify({"error": "Setting with this key already exists"}), 400

    setting = Setting(**data)
    db.session.add(setting)
    db.session.commit()
    return jsonify(setting.serialize()), 201


@admin_settings_bp.route("/<key>", methods=["PUT"])
@jwt_required()
@admin_required
def update_setting(key):
    setting = Setting.query.filter_by(key=key).first_or_404()
    data = request.get_json() or {}
    errors = SettingUpdateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    if "display_name" in data:
        setting.display_name = data["display_name"]
    if "value" in data:
        setting.value = data["value"]

    db.session.commit()
    return jsonify(setting.serialize())


@admin_settings_bp.route("/<key>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_setting(key):
    setting = Setting.query.filter_by(key=key).first_or_404()
    db.session.delete(setting)
    db.session.commit()
    return jsonify({"message": "Setting deleted."})
