from flask import Blueprint, request, jsonify
from api import db
from api.models import Extra

extras_bp = Blueprint("extras_bp", __name__, url_prefix='/extras')


@extras_bp.route("/", methods=["GET"])
def list_extras():
    extras = Extra.query.all()
    return jsonify([
        {"id": e.id, "name": e.name, "price": e.price}
        for e in extras
    ])


@extras_bp.route("/", methods=["POST"])
def create_extra():
    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    if not name or price is None:
        return jsonify({"error": "Missing name or price"}), 400

    extra = Extra(name=name, price=price)
    db.session.add(extra)
    db.session.commit()
    return jsonify({"message": "Extra created", "id": extra.id}), 201
