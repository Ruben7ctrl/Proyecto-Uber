from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from api.models import db, User
from api.utils.jwt_handler import create_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Unauthorized"}), 401

    token = create_token(user.email)
    return jsonify({
        "token": token,
        "user": {
            "name": user.name,
            "email": user.email
        },
        "message": "Login successful"
    }), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    token = create_token(new_user.email)
    return jsonify({
        "token": token,
        "user": {
            "name": new_user.name,
            "email": new_user.email
        },
        "message": "User registered successfully"
    }), 201
