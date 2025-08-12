from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import re
from flask_jwt_extended import jwt_required
from .models2.user import db, Customer, User
# asumo que tienes este decorador para control de roles
from .utils.decorators import admin_required

admin_customers_bp = Blueprint(
    "admin_customers_bp", __name__, url_prefix="/admin/customers")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if not value:
        return False
    return str(value).lower() in ("true", "1", "yes", "on")


@admin_customers_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required
def list_customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = Customer.query.paginate(page=page, per_page=per_page)
    customers = pagination.items
    return jsonify({
        "items": [c.serialize() for c in customers],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    })


@admin_customers_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required
def create_customer():
    data = request.form
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    marketing_allowed = parse_bool(data.get("marketing_allowed"))

    # Validaciones básicas
    if not name or not email or not password:
        return jsonify({"error": "Campos requeridos faltantes"}), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Email no válido"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email ya está en uso"}), 400

    customer = Customer(
        name=name,
        email=email,
        marketing_allowed=marketing_allowed
    )
    customer.set_password(password)

    # Manejo imagen perfil
    if "profile_photo" in request.files:
        photo = request.files["profile_photo"]
        if photo.filename != "":
            if not allowed_file(photo.filename):
                return jsonify({"error": "Archivo no permitido"}), 400
            filename = secure_filename(photo.filename)
            upload_folder = current_app.config.get(
                "UPLOAD_FOLDER", "uploads/profile_pictures")
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            try:
                photo.save(filepath)
                customer.profile_photo_path = filename
            except Exception as e:
                return jsonify({"error": f"Error guardando la imagen: {str(e)}"}), 500

    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.serialize()), 201


@admin_customers_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
@admin_required
def show_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify(customer.serialize())


@admin_customers_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.form

    customer.name = data.get("name", customer.name)
    email = data.get("email", customer.email)
    if email != customer.email:
        # Validar email y duplicados si cambió
        if not re.match(EMAIL_REGEX, email):
            return jsonify({"error": "Email no válido"}), 400
        if User.query.filter(User.email == email, User.id != customer.id).first():
            return jsonify({"error": "Email ya está en uso"}), 400
        customer.email = email

    customer.marketing_allowed = parse_bool(
        data.get("marketing_allowed", customer.marketing_allowed))

    if data.get("password"):
        customer.set_password(data["password"])

    if "profile_photo" in request.files:
        photo = request.files["profile_photo"]
        if photo.filename != "":
            if not allowed_file(photo.filename):
                return jsonify({"error": "Archivo no permitido"}), 400
            filename = secure_filename(photo.filename)
            upload_folder = current_app.config.get(
                "UPLOAD_FOLDER", "uploads/profile_pictures")
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            try:
                photo.save(filepath)
                customer.profile_photo_path = filename
            except Exception as e:
                return jsonify({"error": f"Error guardando la imagen: {str(e)}"}), 500

    db.session.commit()
    return jsonify(customer.serialize()), 200


@admin_customers_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Cliente {id} eliminado"}), 200
