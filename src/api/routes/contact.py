from flask import Blueprint, request, jsonify
from flask_mail import Message
# asumimos que tienes un objeto Mail creado en extensions.py
from api.extensions import mail
from api.utils.jwt_handler import token_required
import os

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/send-message', methods=['POST'])
@token_required
def send_message(current_user):
    data = request.get_json()
    message_content = data.get("message")

    if not message_content:
        return jsonify({"message": "El mensaje es obligatorio"}), 400

    recipient = os.getenv('APP_EMAIL_ADDRESS')
    if not recipient:
        return jsonify({"message": "Dirección de correo no configurada"}), 500

    msg = Message(
        subject="Nuevo mensaje de contacto",
        sender=current_user.email,
        recipients=[recipient],
        body=f"Usuario: {current_user.name} ({current_user.email})\n\nMensaje:\n{message_content}"
    )

    try:
        mail.send(msg)
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": "Error al enviar el correo", "error": str(e)}), 500
