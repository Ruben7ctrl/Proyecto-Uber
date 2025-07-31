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
    data = schema(request.get_json())
    schema = RideExtraSchema()
    name = data.get("name")
    price = data.get("price")
    if not name or price is None:
        return jsonify({"error": "Missing name or price"}), 400

    extra = Extra(name=name, price=price)
    db.session.add(extra)
    db.session.commit()
    return jsonify({"message": "Extra created", "id": extra.id}), 201


@extras_bp.route("/<int:extra_id>", methods=["GET"])
def get_extra(extra_id):
    extra = Extra.query.get_or_404(extra_id)
    return jsonify({
        "id": extra.id,
        "name": extra.name,
        "price": extra.price
    })


@extras_bp.route("/<int:extra_id>", methods=["PUT"])
def update_extra(extra_id):
    extra = Extra.query.get_or_404(extra_id)
    data = schema(request.get_json())
    schema = RideExtraSchema()

    name = data.get("name")
    price = data.get("price")

    if not name or price is None:
        return jsonify({"error": "Missing name or price"}), 400

    extra.name = name
    extra.price = price
    db.session.commit()

    return jsonify({"message": "Extra updated"})


@extras_bp.route("/<int:extra_id>", methods=["DELETE"])
def delete_extra(extra_id):
    extra = Extra.query.get_or_404(extra_id)
    db.session.delete(extra)
    db.session.commit()
    return jsonify({"message": "Extra deleted"})
