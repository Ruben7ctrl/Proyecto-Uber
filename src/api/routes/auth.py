from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from api.models import db, User
from api.utils.jwt_handler import create_token, decode_token
from functools import wraps
from jwt import ExpiredSignatureError, InvalidTokenError
from marshmallow import ValidationError
from api.schemas.auth_schemas import LoginSchema, RegisterSchema, GoogleLoginSchema, PasswordResetSchema
from api.utils.token_utils import verify_reset_token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_mail import Message
from api import mail  # asumiendo que inicializaste Flask-Mail como `mail`
# función para enviar mails si usas
from api.utils.email import send_reset_password_email

auth_bp = Blueprint("auth", __name__)

login_schema = LoginSchema()
register_schema = RegisterSchema()
google_login_schema = GoogleLoginSchema()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', None)
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = decode_token(token)
            current_user = User.query.filter_by(email=data['email']).first()
            if not current_user:
                return jsonify({"message": "User not found"}), 401
        except ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        except Exception:
            return jsonify({"message": "Token error"}), 401
        return f(current_user, *args, **kwargs)
    return decorated


@auth_bp.route("/login", methods=["POST"])
def login():
    json_data = request.get_json()
    try:
        data = login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"message": "Validation failed", "errors": err.messages}), 422

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
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
    json_data = request.get_json()
    try:
        data = register_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"message": "Validation failed", "errors": err.messages}), 422

    email = data["email"].lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(
        name=data["name"],
        email=email,
        password=hashed_password,
        marketing_allowed=data["marketing_allowed"]
    )
    db.session.add(new_user)
    db.session.commit()

    # Asignar rol 'cliente' (depende de tu implementación de roles)
    new_user.assign_role('cliente')  # implementa este método en tu modelo User

    # Enviar email de verificación
    send_verification_email(new_user)

    token = create_token(new_user.email)
    return jsonify({
        "token": token,
        "user": {
            "name": new_user.name,
            "email": new_user.email
        },
        "message": "User registered successfully"
    }), 201


def send_verification_email(user):
    msg = Message(
        "Verify your email",
        recipients=[user.email]
    )
    msg.body = f"Hola {user.name}, por favor verifica tu email para activar tu cuenta."
    mail.send(msg)


@auth_bp.route("/login_google", methods=["POST"])
def login_google():
    json_data = request.get_json()
    try:
        data = google_login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"message": "Validation failed", "errors": err.messages}), 422

    try:
        idinfo = id_token.verify_oauth2_token(
            data["credential"], google_requests.Request(), YOUR_GOOGLE_CLIENT_ID
        )
        email = idinfo.get("email")
        name = idinfo.get("given_name")

        user = User.query.filter_by(email=email).first()
        if not user:
            from werkzeug.security import generate_password_hash
            user = User(
                name=name,
                email=email,
                password=generate_password_hash("random-password"),
                marketing_allowed=data["marketing_allowed"]
            )
            db.session.add(user)
            db.session.commit()

        # Asignar rol "cliente"
        user.assign_role('cliente')  # implementa este método en User

        token = create_token(user.email)
        return jsonify({
            "token": token,
            "user": {"name": user.name, "email": user.email},
            "message": "Success"
        }), 200

    except ValueError:
        return jsonify({"message": "Invalid token"}), 401


@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile(current_user):
    return jsonify({
        "name": current_user.name,
        "email": current_user.email
    })


@auth_bp.route("/check_token", methods=["GET"])
def check_token():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"message": "Token no válido", "status": "er"}), 401

    try:
        data = decode_token(token)
        user = User.query.filter_by(email=data["email"]).first()
        if user:
            return jsonify({
                "message": "Token válido",
                "user": {"id": user.id, "role": user.get_primary_role()},
                "status": "ok"
            }), 200
    except Exception:
        pass

    return jsonify({"message": "Token no válido", "status": "er"}), 401


@auth_bp.route('/password/reset/<token>', methods=['GET'])
def show_reset_form(token):
    # Solo invitados pueden acceder
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = verify_reset_token(token)
    if not user:
        flash('El token de reseteo no es válido o ha expirado.', 'danger')
        return redirect(url_for('auth.request_password_reset'))

    # Renderizas formulario reset, pasas token y email del usuario
    return render_template('auth/password_reset_form.html', token=token, email=user.email)


@auth_bp.route('/password/reset', methods=['POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Validamos datos con Marshmallow
    schema = PasswordResetSchema()
    errors = schema.validate(request.form)
    if errors:
        return jsonify(errors), 400

    token = request.form.get('token')
    password = request.form.get('password')

    user = verify_reset_token(token)
    if not user:
        return jsonify({"error": "Token inválido o expirado"}), 400

    # Cambiar la contraseña y guardar
    user.password = generate_password_hash(password)
    db.session.commit()

    # Logout en otros dispositivos si implementas sesiones múltiples (opcional)
    # Aquí podrías invalidar tokens de sesión si tienes esa lógica

    # Redirección según rol (ejemplo simple)
    if not user.has_role(['editor', 'admin']):
        return redirect('/password/reset/complete')

    # Redirigir a dashboard o similar para admins/editors
    return redirect(url_for('admin.dashboard'))
